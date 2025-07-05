from typing import Optional, Dict
import re
from intent_kit.node.base import TreeNode
from intent_kit.node.enums import NodeType
from intent_kit.node.types import ExecutionResult
from intent_kit.context import IntentContext


class SlotFillerNode(TreeNode):
    """Extracts origin and destination cities from flight queries."""

    CITY_PATTERN = re.compile(r"from (?P<origin>[A-Za-z ]+) to (?P<destination>[A-Za-z ]+)", re.IGNORECASE)

    def __init__(self, name: Optional[str] = "slot_filler_node", description: str = "Extracts origin/destination"):
        super().__init__(name=name, description=description, children=[])

    @property
    def node_type(self) -> NodeType:
        return NodeType.HANDLER

    def execute(self, user_input: str, context: Optional[IntentContext] = None) -> ExecutionResult:
        match = self.CITY_PATTERN.search(user_input)
        slots: Dict[str, str]
        if match:
            slots = {
                "origin": match.group("origin").strip(),
                "destination": match.group("destination").strip(),
            }
            success = True
        else:
            slots = {}
            success = False
        return ExecutionResult(
            success=success,
            node_name=self.name,
            node_path=self.get_path(),
            node_type=self.node_type,
            input=user_input,
            output=slots,
            error=None if success else None,
            params=None,
            children_results=[],
        )