import uuid
from typing import List, Optional, Dict, Any
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
        custom_prompts: Optional[Dict[str, str]] = None,
    ):
        super().__init__(name=name, parent=parent)
        self.logger = Logger(name or "unnamed_node")
        self.description = description
        self.children: List["TreeNode"] = list(children) if children else []
        for child in self.children:
            child.parent = self
        
        # Advanced feature: Custom prompt overrides
        # WARNING: This is for advanced users only. Custom prompts can degrade performance
        # and cause unexpected behavior. If you experience issues, revert to default prompts.
        self._custom_prompts = custom_prompts or {}
        
        if custom_prompts:
            self.logger.warning(
                f"Node '{self.name}' is using custom prompts. "
                "This is an advanced feature that may affect performance. "
                "If you experience issues, revert to default prompts before troubleshooting."
            )

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node. Override in subclasses."""
        return NodeType.UNKNOWN

    @property
    def custom_prompts(self) -> Dict[str, str]:
        """Get custom prompts for this node. Returns empty dict if none set."""
        return self._custom_prompts.copy()

    def get_custom_prompt(self, prompt_key: str, default_prompt: str) -> str:
        """
        Get a custom prompt for this node, falling back to the default.
        
        Args:
            prompt_key: Key identifying the prompt type (e.g., 'classification', 'extraction')
            default_prompt: Default prompt to use if no custom prompt is set
            
        Returns:
            Custom prompt if set, otherwise default prompt
        """
        return self._custom_prompts.get(prompt_key, default_prompt)

    def has_custom_prompts(self) -> bool:
        """Check if this node has any custom prompts set."""
        return bool(self._custom_prompts)

    @abstractmethod
    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        """Execute the node with the given user input and optional context."""
        pass
