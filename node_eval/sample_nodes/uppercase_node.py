from typing import Optional
from intent_kit.node.base import TreeNode
from intent_kit.node.enums import NodeType
from intent_kit.node.types import ExecutionResult
from intent_kit.context import IntentContext


class UppercaseNode(TreeNode):
    """Simple node that uppercases the user input."""

    def __init__(self, name: Optional[str] = "uppercase_node", description: str = "Uppercases input"):
        super().__init__(name=name, description=description, children=[])

    @property
    def node_type(self) -> NodeType:
        return NodeType.HANDLER  # treat as handler-type leaf

    def execute(self, user_input: str, context: Optional[IntentContext] = None) -> ExecutionResult:
        output_text = user_input.upper()
        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=self.get_path(),
            node_type=self.node_type,
            input=user_input,
            output=output_text,
            error=None,
            params=None,
            children_results=[],
        )