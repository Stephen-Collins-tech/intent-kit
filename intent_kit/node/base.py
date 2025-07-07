import uuid
from typing import List, Optional
from abc import ABC, abstractmethod
from intent_kit.utils.logger import Logger
from intent_kit.context import IntentContext
from intent_kit.node.types import ExecutionResult
from intent_kit.node.enums import NodeType


class Node:
    """Base class for all nodes with UUID identification and optional user-defined names."""

    def __init__(self, name: Optional[str] = None, parent: Optional["Node"] = None):
        self.node_id = str(uuid.uuid4())
        self.name = name or self.node_id
        self.parent = parent

    @property
    def has_name(self) -> bool:
        return self.name is not None

    def get_path(self) -> List[str]:
        path = []
        node: Optional["Node"] = self
        while node:
            path.append(node.name)
            node = node.parent
        return list(reversed(path))

    def get_path_string(self) -> str:
        return ".".join(self.get_path())

    def get_uuid_path(self) -> List[str]:
        path = []
        node: Optional["Node"] = self
        while node:
            path.append(node.node_id)
            node = node.parent
        return list(reversed(path))

    def get_uuid_path_string(self) -> str:
        return ".".join(self.get_uuid_path())


class TreeNode(Node, ABC):
    """Base class for all nodes in the intent tree."""

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: str,
        children: Optional[List["TreeNode"]] = None,
        parent: Optional["TreeNode"] = None,
    ):
        super().__init__(name=name, parent=parent)
        self.logger = Logger(name or "unnamed_node")
        self.description = description
        self.children: List["TreeNode"] = list(children) if children else []
        for child in self.children:
            child.parent = self

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node. Override in subclasses."""
        return NodeType.UNKNOWN

    @abstractmethod
    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        """Execute the node with the given user input and optional context."""
        pass
