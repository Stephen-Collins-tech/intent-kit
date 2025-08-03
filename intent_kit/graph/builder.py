"""
Graph builder for creating IntentGraph instances with fluent interface.

This module provides a builder class for creating IntentGraph instances
with a more readable and type-safe approach.
"""

from typing import List, Dict, Any, Optional, Callable, Union
import os
from intent_kit.nodes import TreeNode
from intent_kit.graph.intent_graph import IntentGraph
from intent_kit.graph.graph_components import (
    LLMConfigProcessor,
    GraphValidator,
    NodeFactory,
    RelationshipBuilder,
    GraphConstructor,
)
from intent_kit.services.yaml_service import yaml_service

from intent_kit.nodes.base_builder import BaseBuilder
from intent_kit.nodes.actions.builder import ActionBuilder
from intent_kit.nodes.classifiers.builder import ClassifierBuilder


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
        constructor = GraphConstructor(validator, node_factory, relationship_builder)

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

    def with_yaml(self, yaml_input: Union[str, Dict[str, Any]]) -> "IntentGraphBuilder":
        """Set the YAML graph specification for construction.

        Args:
            yaml_input: YAML file path or dict specification

        Returns:
            Self for method chaining
        """
        try:
            if isinstance(yaml_input, str):
                # Treat as file path
                with open(yaml_input, "r") as f:
                    self._json_graph = yaml_service.safe_load(f)
            else:
                # Treat as dict
                self._json_graph = yaml_input
        except ImportError as e:
            raise ValueError("PyYAML is required") from e
        except Exception as e:
            raise ValueError(f"Failed to load YAML file: {e}") from e
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

    def with_default_llm_config(
        self, llm_config: Dict[str, Any]
    ) -> "IntentGraphBuilder":
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

    def _debug_context(self, enabled: bool = True) -> "IntentGraphBuilder":
        """Enable or disable debug context (internal method for testing).

        Args:
            enabled: Whether to enable debug context

        Returns:
            Self for method chaining
        """
        self._debug_context_enabled = enabled
        return self

    def _context_trace(self, enabled: bool = True) -> "IntentGraphBuilder":
        """Enable or disable context trace (internal method for testing).

        Args:
            enabled: Whether to enable context trace

        Returns:
            Self for method chaining
        """
        self._context_trace_enabled = enabled
        return self

    def _process_llm_config(
        self, llm_config: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Process LLM config with environment variable substitution."""
        if not llm_config:
            return llm_config

        processed_config = {}
        for key, value in llm_config.items():
            if (
                isinstance(value, str)
                and value.startswith("${")
                and value.endswith("}")
            ):
                env_var = value[2:-1]  # Remove ${ and }
                env_value = os.getenv(env_var)
                if env_value:
                    processed_config[key] = env_value
                else:
                    processed_config[key] = value  # Keep original value
            else:
                processed_config[key] = value

        # Validate that we have required fields for supported providers
        provider = processed_config.get("provider", "").lower()
        supported_providers = {"openai", "anthropic", "google", "openrouter", "ollama"}
        if provider in supported_providers:
            if provider != "ollama" and not processed_config.get("api_key"):
                # Warning: Provider requires api_key but none found in config
                pass

        return processed_config

    def _validate_json_graph(self) -> None:
        """Validate the JSON graph specification."""
        if not self._json_graph:
            raise ValueError("No JSON graph set")

        if "root" not in self._json_graph:
            raise ValueError("Missing 'root' field")

        if "nodes" not in self._json_graph:
            raise ValueError("Missing 'nodes' field")

        root_id = self._json_graph["root"]
        nodes = self._json_graph["nodes"]

        if root_id not in nodes:
            raise ValueError(f"Root node '{root_id}' not found in nodes")

        for node_id, node_spec in nodes.items():
            if "type" not in node_spec:
                raise ValueError(f"Node '{node_id}' missing 'type' field")

            node_type = node_spec["type"]
            if node_type == "action":
                if "function" not in node_spec:
                    raise ValueError(
                        f"Action node '{node_id}' missing 'function' field"
                    )
            elif node_type == "classifier":
                classifier_type = node_spec.get("classifier_type", "rule")
                if classifier_type == "llm":
                    if "llm_config" not in node_spec:
                        raise ValueError(
                            f"LLM classifier node '{node_id}' missing 'llm_config' field"
                        )
                else:
                    if "classifier_function" not in node_spec:
                        raise ValueError(
                            f"Rule classifier node '{node_id}' missing 'classifier_function' field"
                        )

    def validate_json_graph(self) -> Dict[str, Any]:
        """Public API for JSON graph validation."""
        if not self._json_graph:
            raise ValueError("No JSON graph set")

        result: Dict[str, Any] = {
            "valid": True,
            "node_count": len(self._json_graph.get("nodes", {})),
            "edge_count": 0,
            "errors": [],
            "warnings": [],
            "cycles_detected": False,
            "unreachable_nodes": [],
        }

        try:
            self._validate_json_graph()

            # Check for cycles
            cycles = self._detect_cycles(self._json_graph["nodes"])
            if cycles:
                result["cycles_detected"] = True
                result["valid"] = False
                result["errors"].append(f"Cycles detected in graph: {cycles}")

            # Check for unreachable nodes
            unreachable = self._find_unreachable_nodes(
                self._json_graph["nodes"], self._json_graph["root"]
            )
            if unreachable:
                result["unreachable_nodes"] = unreachable
                result["warnings"].append(f"Unreachable nodes detected: {unreachable}")

        except ValueError as e:
            result["valid"] = False
            result["errors"].append(str(e))

        return result

    def _detect_cycles(self, nodes: Dict[str, Any]) -> List[List[str]]:
        """Detect cycles in the graph."""
        cycles: List[List[str]] = []
        visited: set[str] = set()
        path: List[str] = []

        def dfs(node_id: str) -> None:
            if node_id in path:
                cycle_start = path.index(node_id)
                cycles.append(path[cycle_start:] + [node_id])
                return

            if node_id in visited:
                return

            visited.add(node_id)
            path.append(node_id)

            node_spec = nodes.get(node_id, {})
            children = node_spec.get("children", [])

            for child in children:
                if child in nodes:
                    dfs(child)

            path.pop()

        for node_id in nodes:
            if node_id not in visited:
                dfs(node_id)

        return cycles

    def _find_unreachable_nodes(self, nodes: Dict[str, Any], root_id: str) -> List[str]:
        """Find unreachable nodes from the root."""
        reachable = set()

        def mark_reachable(node_id: str) -> None:
            if node_id in reachable or node_id not in nodes:
                return
            reachable.add(node_id)
            node_spec = nodes[node_id]
            children = node_spec.get("children", [])
            for child in children:
                mark_reachable(child)

        mark_reachable(root_id)
        unreachable = [node_id for node_id in nodes if node_id not in reachable]
        return unreachable

    def _create_node_from_spec(
        self,
        node_id: str,
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
    ) -> TreeNode:
        """Create a node from specification."""
        if "type" not in node_spec:
            raise ValueError(f"Node '{node_id}' must have a 'type' field")

        node_type = node_spec["type"]
        if node_type == "action":
            return self._create_action_node(
                node_id,
                node_spec.get("name", node_id),
                node_spec.get("description", ""),
                node_spec,
                function_registry,
            )
        elif node_type == "classifier":
            return self._create_classifier_node(
                node_id,
                node_spec.get("name", node_id),
                node_spec.get("description", ""),
                node_spec,
                function_registry,
            )
        else:
            raise ValueError(f"Unknown node type '{node_type}' for node '{node_id}'")

    def _create_action_node(
        self,
        node_id: str,
        name: str,
        description: str,
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
    ) -> TreeNode:
        """Create an action node from specification."""
        if "function" not in node_spec:
            raise ValueError(f"Action node '{node_id}' must have a 'function' field")

        function_name = node_spec["function"]
        if function_name not in function_registry:
            raise ValueError(
                f"Function '{function_name}' not found in function registry"
            )

        builder = ActionBuilder(name)
        builder.with_action(function_registry[function_name])
        builder.with_description(description)

        # Use provided param_schema or default to empty dict
        param_schema = node_spec.get("param_schema", {})
        builder.with_param_schema(param_schema)

        return builder.build()

    def _create_classifier_node(
        self,
        node_id: str,
        name: str,
        description: str,
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
    ) -> TreeNode:
        """Create a classifier node from specification."""
        return ClassifierBuilder.create_from_spec(
            node_id, name, description, node_spec, function_registry
        )

    def _create_llm_classifier_node(
        self,
        node_id: str,
        name: str,
        description: str,
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
    ) -> TreeNode:
        """Create an LLM classifier node from specification."""
        if "llm_config" not in node_spec:
            raise ValueError(
                f"LLM classifier node '{node_id}' must have an 'llm_config' field"
            )

        return ClassifierBuilder.create_from_spec(
            node_id, name, description, node_spec, function_registry
        )

    def _build_from_json(
        self,
        graph_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> IntentGraph:
        """Build graph from JSON specification."""
        if "root" not in graph_spec:
            raise ValueError("Graph spec must contain a 'root' field")

        if "nodes" not in graph_spec:
            raise ValueError("Graph spec must contain an 'nodes' field")

        root_id = graph_spec["root"]
        nodes = graph_spec["nodes"]

        if root_id not in nodes:
            raise ValueError(f"Root node '{root_id}' not found in nodes")

        # Check for missing children before creating nodes
        for node_id, node_spec in nodes.items():
            children = node_spec.get("children", [])
            for child_id in children:
                if child_id not in nodes:
                    raise ValueError(f"Child node '{child_id}' not found in nodes")

        # Create all nodes
        node_map = {}
        for node_id, node_spec in nodes.items():
            if "id" not in node_spec and "name" not in node_spec:
                raise ValueError(
                    f"Node '{node_id}' missing required 'id' or 'name' field"
                )

            node = self._create_node_from_spec(node_id, node_spec, function_registry)
            node_map[node_id] = node

        # Set up parent-child relationships
        for node_id, node_spec in nodes.items():
            node = node_map[node_id]
            children = node_spec.get("children", [])

            for child_id in children:
                child = node_map[child_id]
                child.parent = node

        root_node = node_map[root_id]

        # Process LLM config if provided
        processed_llm_config = None
        if llm_config:
            processed_llm_config = self._process_llm_config(llm_config)

        return IntentGraph(
            root_nodes=[root_node],
            llm_config=processed_llm_config,
            debug_context=self._debug_context_enabled,
            context_trace=self._context_trace_enabled,
        )

    def build(self) -> IntentGraph:
        """Build and return the IntentGraph instance.

        Returns:
            Configured IntentGraph instance

        Raises:
            ValueError: If required fields are missing
        """
        # If we have JSON spec, validate it first
        if self._json_graph:
            if not self._function_registry:
                # Validate JSON even without function registry to catch validation errors
                self._validate_json_graph()
                raise ValueError(
                    "Function registry required for JSON-based construction"
                )

            return self.from_json(
                self._json_graph, self._function_registry, self._llm_config
            )

        # Otherwise, validate we have root nodes for direct construction
        if not self._root_nodes:
            raise ValueError("No root nodes set")

        # Process LLM config if provided
        processed_llm_config = None
        if self._llm_config:
            processed_llm_config = self._process_llm_config(self._llm_config)

        # Create IntentGraph directly from root nodes
        return IntentGraph(
            root_nodes=self._root_nodes,
            llm_config=processed_llm_config,
            debug_context=self._debug_context_enabled,
            context_trace=self._context_trace_enabled,
        )
