from typing import Any, Callable, List, Optional, Dict
from intent_kit.node.base import TreeNode
from intent_kit.node.enums import NodeType
from intent_kit.utils.logger import Logger
from intent_kit.context import IntentContext
from intent_kit.node.types import ExecutionResult, ExecutionError


class ClassifierNode(TreeNode):
    """Intermediate node that uses a classifier to select child nodes."""

    def __init__(
        self,
        name: Optional[str],
        classifier: Callable[[str, List["TreeNode"], Optional[Dict[str, Any]]], Optional["TreeNode"]],
        children: List["TreeNode"],
        description: str = "",
        parent: Optional["TreeNode"] = None
    ):
        super().__init__(name=name, description=description, children=children, parent=parent)
        self.classifier = classifier

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node."""
        return NodeType.CLASSIFIER

    def execute(self, user_input: str, context: Optional[IntentContext] = None) -> ExecutionResult:
        context_dict = None
        if context:
            context_dict = {key: context.get(key) for key in context.keys()}
        chosen = self.classifier(user_input, self.children, context_dict)
        if not chosen:
            self.logger.error(
                f"Classifier at '{self.name}' (Path: {'.'.join(self.get_path())}) could not route input.")
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.CLASSIFIER,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="ClassifierRoutingError",
                    message=f"Classifier at '{self.name}' could not route input.",
                    node_name=self.name,
                    node_path=self.get_path()
                ),
                params=None,
                children_results=[]
            )
        self.logger.debug(
            f"Classifier at '{self.name}' routed input to '{chosen.name}'.")
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
                "available_children": [child.name for child in self.children]
            },
            children_results=[child_result]
        )
