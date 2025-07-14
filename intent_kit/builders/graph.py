"""
Graph builder for creating IntentGraph instances with fluent interface.

This module provides a builder class for creating IntentGraph instances
with a more readable and type-safe approach.
"""

from typing import List, Dict, Any, Optional, Callable, Union
from intent_kit.node import TreeNode
from intent_kit.graph import IntentGraph
from .base import Builder
from intent_kit.services.yaml_service import yaml_service


class IntentGraphBuilder(Builder):
    """Builder for creating IntentGraph instances with fluent interface."""

    def __init__(self):
        """Initialize the graph builder."""
        super().__init__("intent_graph")
        self._root_nodes: List[TreeNode] = []
        self._splitter = None
        self._debug_context_enabled = False
        self._context_trace_enabled = False
        self._json_graph: Optional[Dict[str, Any]] = None
        self._function_registry: Optional[Dict[str, Callable]] = None

    def root(self, node: TreeNode) -> "IntentGraphBuilder":
        """Set the root node for the intent graph.

        Args:
            node: The root TreeNode to use for the graph

        Returns:
            Self for method chaining
        """
        self._root_nodes = [node]
        return self

    def splitter(self, splitter_func) -> "IntentGraphBuilder":
        """Set a custom splitter function for the intent graph.

        Args:
            splitter_func: Function to use for splitting intents

        Returns:
            Self for method chaining
        """
        self._splitter = splitter_func
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

    def with_yaml(self, yaml_input: Union[str, Dict[str, Any]]) -> "IntentGraphBuilder":
        """Set the YAML graph specification for construction.

        Args:
            yaml_input: Either a file path (str) or YAML dict object

        Returns:
            Self for method chaining

        Raises:
            ImportError: If PyYAML is not installed
            ValueError: If YAML parsing fails
        """
        if isinstance(yaml_input, str):
            # Treat as file path
            try:
                with open(yaml_input, "r") as f:
                    json_graph = yaml_service.safe_load(f)
            except Exception as e:
                raise ValueError(f"Failed to load YAML file '{yaml_input}': {e}")
        else:
            # Treat as dict
            json_graph = yaml_input

        self._json_graph = json_graph
        return self

    def validate_json_graph(self) -> Dict[str, Any]:
        """Validate the JSON graph specification.

        Returns:
            Dictionary containing validation results and statistics

        Raises:
            ValueError: If validation fails
        """
        if self._json_graph is None:
            raise ValueError(
                "No JSON graph set. Call .with_json() or .with_yaml() first"
            )

        validation_results: Dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "node_count": 0,
            "edge_count": 0,
            "cycles_detected": False,
            "unreachable_nodes": [],
        }

        try:
            # Basic structure validation
            if "root" not in self._json_graph:
                validation_results["errors"].append("Missing 'root' field")
                validation_results["valid"] = False

            if "intents" not in self._json_graph:
                validation_results["errors"].append("Missing 'intents' field")
                validation_results["valid"] = False

            if not validation_results["valid"]:
                return validation_results

            intents = self._json_graph["intents"]
            root_id = self._json_graph["root"]

            # Validate root node exists
            if root_id not in intents:
                validation_results["errors"].append(
                    f"Root node '{root_id}' not found in intents"
                )
                validation_results["valid"] = False

            # Validate each node
            for node_id, node_spec in intents.items():
                validation_results["node_count"] += 1

                # Check required fields
                if "type" not in node_spec:
                    validation_results["errors"].append(
                        f"Node '{node_id}' missing 'type' field"
                    )
                    validation_results["valid"] = False
                    continue

                node_type = node_spec["type"]

                # Type-specific validation
                if node_type == "action":
                    if "function" not in node_spec:
                        validation_results["errors"].append(
                            f"Action node '{node_id}' missing 'function' field"
                        )
                        validation_results["valid"] = False

                elif node_type == "llm_classifier":
                    if "llm_config" not in node_spec:
                        validation_results["errors"].append(
                            f"LLM classifier node '{node_id}' missing 'llm_config' field"
                        )
                        validation_results["valid"] = False

                elif node_type == "classifier":
                    if "classifier_function" not in node_spec:
                        validation_results["errors"].append(
                            f"Classifier node '{node_id}' missing 'classifier_function' field"
                        )
                        validation_results["valid"] = False

                elif node_type == "splitter":
                    if "splitter_function" not in node_spec:
                        validation_results["errors"].append(
                            f"Splitter node '{node_id}' missing 'splitter_function' field"
                        )
                        validation_results["valid"] = False

                else:
                    validation_results["errors"].append(
                        f"Unknown node type '{node_type}' for node '{node_id}'"
                    )
                    validation_results["valid"] = False

                # Validate children references
                if "children" in node_spec:
                    for child_id in node_spec["children"]:
                        validation_results["edge_count"] += 1
                        if child_id not in intents:
                            validation_results["errors"].append(
                                f"Child node '{child_id}' not found for node '{node_id}'"
                            )
                            validation_results["valid"] = False

            # Check for cycles (simple cycle detection)
            if validation_results["valid"]:
                cycles = self._detect_cycles(intents)
                if cycles:
                    validation_results["cycles_detected"] = True
                    validation_results["errors"].append(
                        f"Cycles detected in graph: {cycles}"
                    )
                    validation_results["valid"] = False

            # Check for unreachable nodes
            if validation_results["valid"]:
                unreachable = self._find_unreachable_nodes(intents, root_id)
                if unreachable:
                    validation_results["unreachable_nodes"] = unreachable
                    validation_results["warnings"].append(
                        f"Unreachable nodes found: {unreachable}"
                    )

        except Exception as e:
            validation_results["errors"].append(f"Validation error: {e}")
            validation_results["valid"] = False

        if not validation_results["valid"]:
            raise ValueError(
                f"Graph validation failed: {'; '.join(validation_results['errors'])}"
            )

        return validation_results

    def _detect_cycles(self, intents: Dict[str, Any]) -> List[List[str]]:
        """Detect cycles in the graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node_id: str, path: List[str]) -> None:
            if node_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(node_id)
                cycles.append(path[cycle_start:] + [node_id])
                return

            if node_id in visited:
                return

            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            if node_id in intents and "children" in intents[node_id]:
                for child_id in intents[node_id]["children"]:
                    dfs(child_id, path.copy())

            rec_stack.remove(node_id)

        for node_id in intents:
            if node_id not in visited:
                dfs(node_id, [])

        return cycles

    def _find_unreachable_nodes(
        self, intents: Dict[str, Any], root_id: str
    ) -> List[str]:
        """Find nodes that are not reachable from the root."""
        reachable = set()

        def mark_reachable(node_id: str) -> None:
            if node_id in reachable:
                return
            reachable.add(node_id)

            if node_id in intents and "children" in intents[node_id]:
                for child_id in intents[node_id]["children"]:
                    mark_reachable(child_id)

        mark_reachable(root_id)

        unreachable = [node_id for node_id in intents if node_id not in reachable]
        return unreachable

    def build(self) -> IntentGraph:
        """Build and return the IntentGraph instance.

        Returns:
            Configured IntentGraph instance

        Raises:
            ValueError: If no root nodes have been set and no JSON graph provided
        """
        if self._json_graph is not None:
            return self._build_from_json(
                self._json_graph, self._function_registry or {}
            )

        if not self._root_nodes:
            raise ValueError(
                "No root nodes set. Call .root() before .build() or use .with_json()"
            )

        graph = IntentGraph(
            root_nodes=self._root_nodes,
            splitter=self._splitter,
            debug_context=self._debug_context_enabled,
            context_trace=self._context_trace_enabled,
        )

        return graph

    def _build_from_json(
        self, graph_spec: Dict[str, Any], function_registry: Dict[str, Callable]
    ) -> IntentGraph:
        """Build an IntentGraph from a flat JSON specification.

        Args:
            graph_spec: Flat JSON specification for the intent graph
            function_registry: Dictionary mapping function names to callables

        Returns:
            Configured IntentGraph instance

        Raises:
            ValueError: If the JSON specification is invalid or missing required fields
        """
        # Validate required fields
        if "root" not in graph_spec:
            raise ValueError("JSON graph specification must contain a 'root' field")

        if "intents" not in graph_spec:
            raise ValueError("JSON graph specification must contain an 'intents' field")

        # Create all nodes first, mapping IDs to nodes
        node_map: Dict[str, TreeNode] = {}

        for node_id, node_spec in graph_spec["intents"].items():
            node = self._create_node_from_spec(node_id, node_spec, function_registry)
            node_map[node_id] = node

        # Set up parent-child relationships
        for node_id, node_spec in graph_spec["intents"].items():
            if "children" in node_spec:
                children = []
                for child_id in node_spec["children"]:
                    if child_id not in node_map:
                        raise ValueError(
                            f"Child node '{child_id}' not found in intents for node '{node_id}'"
                        )
                    children.append(node_map[child_id])
                node_map[node_id].children = children
                # Set parent relationships
                for child in children:
                    child.parent = node_map[node_id]

        # Get root node
        root_id = graph_spec["root"]
        if root_id not in node_map:
            raise ValueError(f"Root node '{root_id}' not found in intents")

        # Create IntentGraph
        graph = IntentGraph(
            root_nodes=[node_map[root_id]],
            splitter=self._splitter,
            debug_context=self._debug_context_enabled,
            context_trace=self._context_trace_enabled,
        )

        return graph

    def _create_node_from_spec(
        self,
        node_id: str,
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
    ) -> TreeNode:
        """Create a TreeNode from a node specification.

        Args:
            node_id: ID of the node
            node_spec: Node specification from JSON
            function_registry: Dictionary mapping function names to callables

        Returns:
            Configured TreeNode

        Raises:
            ValueError: If the node specification is invalid
        """
        if "type" not in node_spec:
            raise ValueError(f"Node '{node_id}' must have a 'type' field")

        node_type = node_spec["type"]
        name = node_spec.get("name", node_id)
        description = node_spec.get("description", "")

        if node_type == "action":
            return self._create_action_node(
                node_id, name, description, node_spec, function_registry
            )
        elif node_type == "llm_classifier":
            return self._create_llm_classifier_node(
                node_id, name, description, node_spec, function_registry
            )
        elif node_type == "classifier":
            return self._create_classifier_node(
                node_id, name, description, node_spec, function_registry
            )
        elif node_type == "splitter":
            return self._create_splitter_node(
                node_id, name, description, node_spec, function_registry
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
        """Create an ActionNode from specification."""
        from intent_kit.utils.node_factory import action

        if "function" not in node_spec:
            raise ValueError(f"Action node '{node_id}' must have a 'function' field")

        function_name = node_spec["function"]
        if function_name not in function_registry:
            raise ValueError(
                f"Function '{function_name}' not found in function registry for node '{node_id}'"
            )

        action_func = function_registry[function_name]
        param_schema_raw = node_spec.get("param_schema", {})

        # Parse parameter schema from string types to Python types
        from intent_kit.utils.param_extraction import parse_param_schema
        from intent_kit.utils.logger import Logger

        logger = Logger("graph_builder")

        logger.debug(
            f"Creating action node '{node_id}' with raw param_schema: {param_schema_raw}"
        )
        param_schema = parse_param_schema(param_schema_raw)
        logger.debug(f"Parsed param_schema: {param_schema}")

        llm_config = node_spec.get("llm_config")
        context_inputs = set(node_spec.get("context_inputs", []))
        context_outputs = set(node_spec.get("context_outputs", []))
        remediation_strategies = node_spec.get("remediation_strategies", [])

        return action(
            name=name,
            description=description,
            action_func=action_func,
            param_schema=param_schema,
            llm_config=llm_config,
            context_inputs=context_inputs,
            context_outputs=context_outputs,
            remediation_strategies=remediation_strategies,
        )

    def _create_llm_classifier_node(
        self,
        node_id: str,
        name: str,
        description: str,
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
    ) -> TreeNode:
        """Create an LLM ClassifierNode from specification."""

        if "llm_config" not in node_spec:
            raise ValueError(
                f"LLM classifier node '{node_id}' must have an 'llm_config' field"
            )

        llm_config = node_spec["llm_config"]
        classification_prompt = node_spec.get("classification_prompt")
        remediation_strategies = node_spec.get("remediation_strategies", [])

        # Create a temporary node for now - children will be set later
        # We'll need to create a placeholder and update it after all nodes are created
        from intent_kit.node.classifiers import ClassifierNode
        from intent_kit.node.classifiers import (
            create_llm_classifier,
            get_default_classification_prompt,
        )

        if not classification_prompt:
            classification_prompt = get_default_classification_prompt()

        # Create a placeholder classifier function
        classifier_func = create_llm_classifier(llm_config, classification_prompt, [])

        return ClassifierNode(
            name=name,
            description=description,
            classifier=classifier_func,
            children=[],  # Will be set later
            remediation_strategies=remediation_strategies,
        )

    def _create_classifier_node(
        self,
        node_id: str,
        name: str,
        description: str,
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
    ) -> TreeNode:
        """Create a ClassifierNode from specification."""
        from intent_kit.node.classifiers import ClassifierNode

        if "classifier_function" not in node_spec:
            raise ValueError(
                f"Classifier node '{node_id}' must have a 'classifier_function' field"
            )

        classifier_function_name = node_spec["classifier_function"]
        if classifier_function_name not in function_registry:
            raise ValueError(
                f"Classifier function '{classifier_function_name}' not found in function registry for node '{node_id}'"
            )

        classifier_func = function_registry[classifier_function_name]
        remediation_strategies = node_spec.get("remediation_strategies", [])

        return ClassifierNode(
            name=name,
            description=description,
            classifier=classifier_func,
            children=[],  # Will be set later
            remediation_strategies=remediation_strategies,
        )

    def _create_splitter_node(
        self,
        node_id: str,
        name: str,
        description: str,
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
    ) -> TreeNode:
        """Create a SplitterNode from specification."""
        from intent_kit.node.splitters import SplitterNode

        if "splitter_function" not in node_spec:
            raise ValueError(
                f"Splitter node '{node_id}' must have a 'splitter_function' field"
            )

        splitter_function_name = node_spec["splitter_function"]
        if splitter_function_name not in function_registry:
            raise ValueError(
                f"Splitter function '{splitter_function_name}' not found in function registry for node '{node_id}'"
            )

        splitter_func = function_registry[splitter_function_name]
        llm_client = node_spec.get("llm_client")

        return SplitterNode(
            name=name,
            description=description,
            splitter_function=splitter_func,
            children=[],  # Will be set later
            llm_client=llm_client,
        )

    # Internal debug methods (for development use only)
    def _debug_context(self, enabled: bool = True) -> "IntentGraphBuilder":
        """Enable context debugging for the intent graph.

        Args:
            enabled: Whether to enable context debugging

        Returns:
            Self for method chaining
        """
        self._debug_context_enabled = enabled
        return self

    def _context_trace(self, enabled: bool = True) -> "IntentGraphBuilder":
        """Enable detailed context tracing for the intent graph.

        Args:
            enabled: Whether to enable context tracing

        Returns:
            Self for method chaining
        """
        self._context_trace_enabled = enabled
        return self
