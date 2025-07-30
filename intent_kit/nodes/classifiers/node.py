"""
Classifier node implementation.

This module provides the ClassifierNode class which routes user input
to child nodes based on classification logic.
"""

from typing import Any, Callable, List, Optional, Union, Dict
from ..actions.remediation import (
    RemediationStrategy,
    get_remediation_strategy,
)
from ..base import TreeNode
from ..enums import NodeType
from ..types import ExecutionResult, ExecutionError
from intent_kit.context import IntentContext
import inspect


class ClassifierNode(TreeNode):
    """Intermediate node that uses a classifier to select child nodes."""

    def __init__(
        self,
        name: Optional[str],
        classifier: Callable[..., ExecutionResult],
        children: List["TreeNode"],
        description: str = "",
        parent: Optional["TreeNode"] = None,
        remediation_strategies: Optional[List[Union[str,
                                                    RemediationStrategy]]] = None,
        llm_client=None,
    ):
        super().__init__(
            name=name, description=description, children=children, parent=parent
        )
        self.classifier = classifier
        self.remediation_strategies = remediation_strategies or []
        self.llm_client = llm_client  # For framework injection

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node."""
        return NodeType.CLASSIFIER

    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        context_dict: Dict[str, Any] = {}
        # Use only self.llm_client (should be injected by builder/graph)
        classifier_params = inspect.signature(self.classifier).parameters
        self.logger.debug(
            f"classifier_params: {classifier_params}"
        )
        if "llm_client" in classifier_params or any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in classifier_params.values()
        ):
            classifier_result = self.classifier(
                user_input, self.children, context_dict, llm_client=self.llm_client
            )
        else:
            classifier_result = self.classifier(
                user_input, self.children, context_dict)

        # Handle the case where classifier returns None (legacy behavior)
        if classifier_result is None:
            self.logger.error(
                f"Classifier at '{self.name}' (Path: {'.'.join(self.get_path())}) could not route input."
            )

            # Try remediation strategies
            error = ExecutionError(
                error_type="ClassifierRoutingError",
                message=f"Classifier at '{self.name}' could not route input.",
                node_name=self.name,
                node_path=self.get_path(),
            )

            remediation_result = self._execute_remediation_strategies(
                user_input=user_input, context=context, original_error=error
            )

            if remediation_result:
                return remediation_result

            # If no remediation succeeded, return the original error
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.CLASSIFIER,
                input=user_input,
                output=None,
                error=error,
                params=None,
                children_results=[],
                # No token information available for None result
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                duration=0.0,
            )

        # Handle ExecutionResult from classifier
        if not classifier_result.success:
            self.logger.error(
                f"Classifier at '{self.name}' (Path: {'.'.join(self.get_path())}) failed: {classifier_result.error}"
            )

            # Try remediation strategies
            remediation_result = self._execute_remediation_strategies(
                user_input=user_input,
                context=context,
                original_error=classifier_result.error,
            )

            if remediation_result:
                return remediation_result

            # If no remediation succeeded, return the classifier error
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.CLASSIFIER,
                input=user_input,
                output=None,
                error=classifier_result.error,
                params=classifier_result.params,
                children_results=[],
                # Preserve token information from the failed classifier result
                input_tokens=getattr(classifier_result, "input_tokens", None),
                output_tokens=getattr(
                    classifier_result, "output_tokens", None),
                cost=getattr(classifier_result, "cost", None),
                provider=getattr(classifier_result, "provider", None),
                model=getattr(classifier_result, "model", None),
                duration=getattr(classifier_result, "duration", None),
            )

        # Classifier succeeded - return the result with our node info
        chosen_child = (
            classifier_result.params.get("chosen_child", "unknown")
            if classifier_result.params
            else "unknown"
        )
        self.logger.debug(
            f"Classifier at '{self.name}' completed successfully with chosen child: {chosen_child}"
        )

        self.logger.debug(
            f"Classifier at '{self.name}' completed successfully with chosen child: {chosen_child} and params: {classifier_result.params}"
        )
        self.logger.debug(f"classifier_result: {classifier_result}")

        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=self.get_path(),
            node_type=NodeType.CLASSIFIER,
            input=user_input,
            output=classifier_result.output,
            error=None,
            params=classifier_result.params,
            children_results=[],  # Children will be handled by traverse method
            # Preserve token information from the classifier result
            input_tokens=getattr(classifier_result, "input_tokens", None),
            output_tokens=getattr(classifier_result, "output_tokens", None),
            cost=getattr(classifier_result, "cost", None),
            provider=getattr(classifier_result, "provider", None),
            model=getattr(classifier_result, "model", None),
            duration=getattr(classifier_result, "duration", None),
        )

    def _execute_remediation_strategies(
        self,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
    ) -> Optional[ExecutionResult]:
        """Execute remediation strategies for classifier failures."""
        if not self.remediation_strategies:
            return None

        for strategy_item in self.remediation_strategies:
            strategy: Optional[RemediationStrategy] = None

            if isinstance(strategy_item, str):
                # String ID - get from registry
                strategy = get_remediation_strategy(strategy_item)
                if not strategy:
                    self.logger.warning(
                        f"Remediation strategy '{strategy_item}' not found in registry"
                    )
                    continue
            elif isinstance(strategy_item, RemediationStrategy):
                # Direct strategy object
                strategy = strategy_item
            else:
                self.logger.warning(
                    f"Invalid remediation strategy type: {type(strategy_item)}"
                )
                continue

            try:
                result = strategy.execute(
                    node_name=self.name or "unknown",
                    user_input=user_input,
                    context=context,
                    original_error=original_error,
                    classifier_func=self.classifier,
                    available_children=self.children,
                )
                if result and result.success:
                    self.logger.info(
                        f"Remediation strategy '{strategy.name}' succeeded for {self.name}"
                    )
                    return result
                else:
                    self.logger.warning(
                        f"Remediation strategy '{strategy.name}' failed for {self.name}"
                    )
            except Exception as e:
                self.logger.error(
                    f"Remediation strategy '{strategy.name}' error for {self.name}: {type(e).__name__}: {str(e)}"
                )

        self.logger.error(f"All remediation strategies failed for {self.name}")
        return None
