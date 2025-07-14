"""
Splitter builder for creating splitter nodes with fluent interface.

This module provides a builder class for creating SplitterNode instances
with a more readable and type-safe approach.
"""

from typing import Any, Callable, List, Optional
from intent_kit.node import TreeNode
from intent_kit.node.splitters import SplitterNode
from intent_kit.utils.node_factory import create_splitter_node
from .base import Builder


class SplitterBuilder(Builder):
    """Builder for creating splitter nodes with fluent interface."""

    def __init__(self, name: str):
        """Initialize the splitter builder.

        Args:
            name: Name of the splitter node
        """
        super().__init__(name)
        self.splitter_func: Optional[Callable] = None
        self.children: List[TreeNode] = []
        self.llm_client: Optional[Any] = None

    def with_splitter(self, splitter_func: Callable) -> "SplitterBuilder":
        """Set the splitter function.

        Args:
            splitter_func: Function to split intents

        Returns:
            Self for method chaining
        """
        self.splitter_func = splitter_func
        return self

    def with_children(self, children: List[TreeNode]) -> "SplitterBuilder":
        """Set the child nodes.

        Args:
            children: List of child nodes to route to

        Returns:
            Self for method chaining
        """
        self.children = children
        return self

    def add_child(self, child: TreeNode) -> "SplitterBuilder":
        """Add a child node.

        Args:
            child: Child node to add

        Returns:
            Self for method chaining
        """
        self.children.append(child)
        return self

    def with_llm_client(self, llm_client: Any) -> "SplitterBuilder":
        """Set the LLM client for LLM-based splitting.

        Args:
            llm_client: LLM client instance

        Returns:
            Self for method chaining
        """
        self.llm_client = llm_client
        return self

    def build(self) -> SplitterNode:
        """Build and return the SplitterNode instance.

        Returns:
            Configured SplitterNode instance

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields using base class method
        self._validate_required_fields(
            [
                ("children", self.children, "with_children"),
                ("splitter function", self.splitter_func, "with_splitter"),
            ]
        )

        # Type assertion since validation ensures these are not None
        assert self.splitter_func is not None
        assert self.children is not None
        splitter_func = self.splitter_func
        children = self.children

        return create_splitter_node(
            name=self.name,
            description=self.description,
            splitter_func=splitter_func,
            children=children,
            llm_client=self.llm_client,
        )
