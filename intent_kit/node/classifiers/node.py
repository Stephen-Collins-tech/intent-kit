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


class ClassifierNode(TreeNode):
    """Intermediate node that uses a classifier to select child nodes."""

    def __init__(
        self,
        name: Optional[str],
        classifier: Callable[
            [str, List["TreeNode"], Optional[Dict[str, Any]]], Optional["TreeNode"]
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
        chosen = self.classifier(user_input, self.children, context_dict)
        if not chosen:
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
            )
        self.logger.debug(
            f"Classifier at '{self.name}' routed input to '{chosen.name}'."
        )
        child_result = chosen.execute(user_input, context)
        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=self.get_path(),
            node_type=NodeType.CLASSIFIER,
            input=user_input,
            output=child_result.output,  # Return the child's actual output
            error=None,
            params={
                "chosen_child": chosen.name,
                "available_children": [child.name for child in self.children],
            },
            children_results=[child_result],
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
