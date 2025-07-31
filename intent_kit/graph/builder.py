"""
Graph builder for creating IntentGraph instances with fluent interface.

This module provides a builder class for creating IntentGraph instances
with a more readable and type-safe approach.
"""

from typing import List, Dict, Any, Optional, Callable, Union
from intent_kit.nodes import TreeNode
from intent_kit.graph.intent_graph import IntentGraph
from intent_kit.utils.logger import Logger
from intent_kit.graph.graph_components import (
    LLMConfigProcessor,
    GraphValidator,
    NodeFactory,
    RelationshipBuilder,
    GraphConstructor,
)


from intent_kit.nodes.base_builder import BaseBuilder


class IntentGraphBuilder(BaseBuilder[IntentGraph]):
    """Builder for creating IntentGraph instances with fluent interface."""

    def __init__(self):
        """Initialize the graph builder."""
        super().__init__("intent_graph")
        self._root_nodes: List[TreeNode] = []
        self._debug_context_enabled = False
        self._context_trace_enabled = False
        self._json_graph: Optional[Dict[str, Any]] = None
        self._function_registry: Optional[Dict[str, Callable]] = None
        self._llm_config: Optional[Dict[str, Any]] = None
        self._logger = Logger("graph_builder")

    @staticmethod
    def from_json(
        graph_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> IntentGraph:
        """
        Create an IntentGraph from JSON spec.
        Supports both direct node creation and function registry resolution.
        """
        # Process LLM config
        llm_processor = LLMConfigProcessor()
        processed_llm_config = llm_processor.process_config(llm_config)

        # Create components
        validator = GraphValidator()
        node_factory = NodeFactory(function_registry, processed_llm_config)
        relationship_builder = RelationshipBuilder()
        constructor = GraphConstructor(
            validator, node_factory, relationship_builder)

        return constructor.construct_from_json(graph_spec, processed_llm_config)

    def root(self, node: TreeNode) -> "IntentGraphBuilder":
        """Set the root node for the intent graph.

        Args:
            node: The root TreeNode to use for the graph

        Returns:
            Self for method chaining
        """
        self._root_nodes = [node]
        return self

    def with_json(self, json_graph: Dict[str, Any]) -> "IntentGraphBuilder":
        """Set the JSON graph specification for construction.

        Args:
            json_graph: Flat JSON/dict specification for the intent graph

        Returns:
            Self for method chaining
        """
        self._json_graph = json_graph
        return self

    def with_functions(
        self, function_registry: Dict[str, Callable]
    ) -> "IntentGraphBuilder":
        """Set the function registry for JSON-based construction.

        Args:
            function_registry: Dictionary mapping function names to callables

        Returns:
            Self for method chaining
        """
        self._function_registry = function_registry
        return self

    def with_default_llm_config(self, llm_config: Dict[str, Any]) -> "IntentGraphBuilder":
        """Set the default LLM configuration for the graph.

        Args:
            llm_config: LLM configuration dictionary

        Returns:
            Self for method chaining
        """
        self._llm_config = llm_config
        return self

    def with_debug_context(self, enabled: bool = True) -> "IntentGraphBuilder":
        """Enable or disable debug context.

        Args:
            enabled: Whether to enable debug context

        Returns:
            Self for method chaining
        """
        self._debug_context_enabled = enabled
        return self

    def with_context_trace(self, enabled: bool = True) -> "IntentGraphBuilder":
        """Enable or disable context tracing.

        Args:
            enabled: Whether to enable context tracing

        Returns:
            Self for method chaining
        """
        self._context_trace_enabled = enabled
        return self

    def build(self) -> IntentGraph:
        """Build and return the IntentGraph instance.

        Returns:
            Configured IntentGraph instance

        Raises:
            ValueError: If required fields are missing
        """
        # If we have JSON spec, use the from_json static method
        if self._json_graph and self._function_registry:
            return self.from_json(self._json_graph, self._function_registry, self._llm_config)

        # Otherwise, validate we have root nodes for direct construction
        if not self._root_nodes:
            raise ValueError(
                "Root nodes must be set. Call .root() before .build()")

        # Process LLM config if provided
        processed_llm_config = None
        if self._llm_config:
            llm_processor = LLMConfigProcessor()
            processed_llm_config = llm_processor.process_config(
                self._llm_config)

        # Create IntentGraph directly from root nodes
        return IntentGraph(
            root_nodes=self._root_nodes,
            llm_config=processed_llm_config,
            debug_context=self._debug_context_enabled,
            context_trace=self._context_trace_enabled,
        )
