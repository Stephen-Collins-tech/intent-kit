from typing import Optional
import re
from intent_kit.node.base import TreeNode
from intent_kit.node.enums import NodeType
from intent_kit.node.types import ExecutionResult
from intent_kit.context import IntentContext


class NluParserNode(TreeNode):
    """Very naive rule-based NLU parser returning an intent label."""

    def __init__(self, name: Optional[str] = "nlu_parser_node", description: str = "Parses intent from input"):
        super().__init__(name=name, description=description, children=[])

    @property
    def node_type(self) -> NodeType:
        return NodeType.HANDLER

    def execute(self, user_input: str, context: Optional[IntentContext] = None) -> ExecutionResult:
        text = user_input.lower()
        if re.search(r"book .*flight", text):
            intent = "book_flight"
        elif "cancel" in text:
            intent = "cancel_reservation"
        elif "weather" in text:
            intent = "get_weather"
        else:
            intent = "unknown"
        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=self.get_path(),
            node_type=self.node_type,
            input=user_input,
            output=intent,
            error=None,
            params=None,
            children_results=[],
        )