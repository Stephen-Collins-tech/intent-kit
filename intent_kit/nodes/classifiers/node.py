"""
Classifier node implementation.

This module provides the ClassifierNode class which is an intermediate node
that uses a classifier to select child nodes.
"""

from typing import Any, Callable, List, Optional, Dict, Union
from ..base_node import TreeNode
from ..enums import NodeType
from ..types import ExecutionResult, ExecutionError
from intent_kit.context import IntentContext
from intent_kit.types import LLMResponse
from ..actions.remediation import (
    get_remediation_strategy,
    RemediationStrategy,
)


class ClassifierNode(TreeNode):
    """Intermediate node that uses a classifier to select child nodes."""

    def __init__(
        self,
        name: Optional[str],
        classifier: Callable[
            [str, List["TreeNode"], Optional[Dict[str, Any]]],
            tuple[Optional["TreeNode"], Optional[LLMResponse]],
        ],
        children: List["TreeNode"],
        description: str = "",
        parent: Optional["TreeNode"] = None,
        remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = None,
    ):
        super().__init__(
            name=name, description=description, children=children, parent=parent
        )
        self.classifier = classifier
        self.remediation_strategies = remediation_strategies or []

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node."""
        return NodeType.CLASSIFIER

    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        context_dict: Dict[str, Any] = {}
        # If context is needed, populate context_dict here in the future

        # Call classifier function - it now returns a tuple (chosen_child, response_info)
        (chosen_child, response) = self.classifier(
            user_input, self.children, context_dict
        )

        if not chosen_child:
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
            self.logger.debug(
                f"ClassifierNode .execute method call remediation_result: {remediation_result}"
            )

            if remediation_result:
                self.logger.warning(
                    f"ClassifierNode .execute method call remediation_result: {remediation_result}"
                )
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
            )

        # Extract LLM response info from the classifier result
        # Handle both dict and LLMResponse objects
        if isinstance(response, dict):
            # Response is a dict with response info
            cost = response.get("cost", 0.0)
            model = response.get("model", "")
            provider = response.get("provider", "")
            input_tokens = response.get("input_tokens", 0)
            output_tokens = response.get("output_tokens", 0)
        else:
            # Response is an LLMResponse object
            cost = response.cost if response else 0.0
            model = response.model if response else ""
            provider = response.provider if response else ""
            input_tokens = response.input_tokens if response else 0
            output_tokens = response.output_tokens if response else 0

        # Execute the chosen child to get the actual output
        child_result = chosen_child.execute(user_input, context)

        # Calculate total cost (classifier + child)
        total_cost = cost + child_result.cost if child_result.cost else cost
        total_input_tokens = (
            input_tokens + child_result.input_tokens
            if child_result.input_tokens
            else input_tokens
        )
        total_output_tokens = (
            output_tokens + child_result.output_tokens
            if child_result.output_tokens
            else output_tokens
        )

        return ExecutionResult(
            success=True,
            node_name=self.name or "unknown",
            node_path=self.get_path(),
            node_type=NodeType.CLASSIFIER,
            input=user_input,
            output=child_result.output,  # Use the child's output
            error=None,
            params={
                "chosen_child": chosen_child.name or "unknown",
                "available_children": [
                    child.name or "unknown" for child in self.children
                ],
            },
            children_results=[child_result],
            cost=total_cost,
            model=model,
            provider=provider,
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
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
