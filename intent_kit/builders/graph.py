"""
Graph builder for creating IntentGraph instances with fluent interface.

This module provides a builder class for creating IntentGraph instances
with a more readable and type-safe approach.
"""

from typing import List, Dict, Any, Optional, Callable, Union
from intent_kit.nodes import TreeNode
from intent_kit.nodes.enums import NodeType, ClassifierType
from intent_kit.graph import IntentGraph
from .base import Builder
from intent_kit.services.yaml_service import yaml_service
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.utils.logger import Logger

from intent_kit.nodes.classifiers import ClassifierNode
from intent_kit.nodes.classifiers import (
    create_llm_classifier,
    get_default_classification_prompt,
)
import os


class IntentGraphBuilder(Builder):
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
                raise ValueError(
                    f"Failed to load YAML file '{yaml_input}': {e}")
        else:
            # Treat as dict
            json_graph = yaml_input

        self._json_graph = json_graph
        return self

    def with_default_llm_config(
        self, llm_config: Dict[str, Any]
    ) -> "IntentGraphBuilder":
        """Set the default LLM configuration for the entire graph.

        Args:
            llm_config: Dictionary containing LLM configuration parameters.

        Returns:
            Self for method chaining
        """
        self._llm_config = self._process_llm_config(llm_config)
        return self

    def _process_llm_config(
        self, llm_config: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Process LLM config with environment variable substitution.

        Args:
            llm_config: Raw LLM configuration dictionary

        Returns:
            Processed LLM configuration with environment variables resolved
        """
        if not llm_config:
            return llm_config

        processed_config = {}
        supported_providers = {"openai", "anthropic",
                               "google", "openrouter", "ollama"}

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
                    self._logger.debug(
                        f"Resolved environment variable {env_var} for key {key}"
                    )
                else:
                    self._logger.warning(
                        f"Environment variable {env_var} not found for key {key}"
                    )
                    processed_config[key] = value  # Keep original value
            else:
                processed_config[key] = value

        # Validate that we have required fields for supported providers
        provider = processed_config.get("provider", "").lower()
        if provider in supported_providers:
            if provider != "ollama" and not processed_config.get("api_key"):
                self._logger.warning(
                    f"Provider {provider} requires api_key but none found in config"
                )

        return processed_config

    def _validate_json_graph(self) -> None:
        """Validate the JSON graph specification internally.

        Raises:
            ValueError: If validation fails
        """
        if self._json_graph is None:
            raise ValueError(
                "No JSON graph set. Call .with_json() or .with_yaml() first"
            )

        errors = []

        # Basic structure validation
        if "root" not in self._json_graph:
            errors.append("Missing 'root' field")

        if "nodes" not in self._json_graph:
            errors.append("Missing 'nodes' field")

        if errors:
            raise ValueError(f"Graph validation failed: {'; '.join(errors)}")

        nodes = self._json_graph["nodes"]
        root_id = self._json_graph["root"]

        # Validate root node exists
        if root_id not in nodes:
            errors.append(f"Root node '{root_id}' not found in nodes")

        # Validate each node
        for node_spec in nodes.values():
            # Check required fields
            if "id" not in node_spec and "name" not in node_spec:
                errors.append(
                    f"Node missing required 'id' or 'name' field: {node_spec}"
                )
                continue

            node_id = node_spec.get("id", node_spec.get("name"))

            if "type" not in node_spec:
                errors.append(f"Node '{node_id}' missing 'type' field")
                continue

            node_type = node_spec["type"]

            # Type-specific validation
            match node_type:
                case NodeType.ACTION.value:
                    if "function" not in node_spec:
                        errors.append(
                            f"Action node '{node_id}' missing 'function' field"
                        )

                case NodeType.CLASSIFIER.value:
                    classifier_type = node_spec.get(
                        "classifier_type", ClassifierType.RULE.value
                    )
                    if classifier_type == ClassifierType.LLM.value:
                        if "llm_config" not in node_spec:
                            errors.append(
                                f"LLM classifier node '{node_id}' missing 'llm_config' field"
                            )
                    elif classifier_type == ClassifierType.RULE.value:
                        if "classifier_function" not in node_spec:
                            errors.append(
                                f"Rule classifier node '{node_id}' missing 'classifier_function' field"
                            )

                case _:
                    errors.append(
                        f"Unknown node type '{node_type}' for node '{node_id}'"
                    )

            # Validate children references
            if "children" in node_spec:
                for child_id in node_spec["children"]:
                    if child_id not in nodes:
                        errors.append(
                            f"Child node '{child_id}' not found for node '{node_id}'"
                        )

        # Check for cycles (simple cycle detection)
        cycles = self._detect_cycles(nodes)
        if cycles:
            errors.append(f"Cycles detected in graph: {cycles}")

        if errors:
            raise ValueError(f"Graph validation failed: {'; '.join(errors)}")

    def validate_json_graph(self) -> Dict[str, Any]:
        """Validate the JSON graph specification and return detailed results.

        This method provides detailed validation information without raising exceptions
        for validation failures. Use this for debugging and validation reporting.

        Returns:
            Dictionary containing validation results and statistics

        Raises:
            ValueError: If no JSON graph is set
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

        nodes = self._json_graph["nodes"]
        root_id = self._json_graph["root"]

        # Basic structure validation
        if "root" not in self._json_graph:
            validation_results["errors"].append("Missing 'root' field")
            validation_results["valid"] = False

        if "nodes" not in self._json_graph:
            validation_results["errors"].append("Missing 'nodes' field")
            validation_results["valid"] = False

        if not validation_results["valid"]:
            return validation_results

        # Validate root node exists
        if root_id not in nodes:
            validation_results["errors"].append(
                f"Root node '{root_id}' not found in nodes"
            )
            validation_results["valid"] = False

        # Validate each node
        for node_spec in nodes.values():
            validation_results["node_count"] += 1

            # Check required fields
            if "id" not in node_spec and "name" not in node_spec:
                validation_results["errors"].append(
                    f"Node missing required 'id' or 'name' field: {node_spec}"
                )
                validation_results["valid"] = False
                continue

            node_id = node_spec.get("id", node_spec.get("name"))

            if "type" not in node_spec:
                validation_results["errors"].append(
                    f"Node '{node_id}' missing 'type' field"
                )
                validation_results["valid"] = False
                continue

            node_type = node_spec["type"]

            # Type-specific validation
            match node_type:
                case NodeType.ACTION.value:
                    if "function" not in node_spec:
                        validation_results["errors"].append(
                            f"Action node '{node_id}' missing 'function' field"
                        )
                        validation_results["valid"] = False

                case NodeType.CLASSIFIER.value:
                    classifier_type = node_spec.get(
                        "classifier_type", ClassifierType.RULE.value
                    )
                    if classifier_type == ClassifierType.LLM.value:
                        if "llm_config" not in node_spec:
                            validation_results["errors"].append(
                                f"LLM classifier node '{node_id}' missing 'llm_config' field"
                            )
                            validation_results["valid"] = False
                    elif classifier_type == ClassifierType.RULE.value:
                        if "classifier_function" not in node_spec:
                            validation_results["errors"].append(
                                f"Rule classifier node '{node_id}' missing 'classifier_function' field"
                            )
                            validation_results["valid"] = False

                case _:
                    validation_results["errors"].append(
                        f"Unknown node type '{node_type}' for node '{node_id}'"
                    )
                    validation_results["valid"] = False

            # Validate children references
            if "children" in node_spec:
                for child_id in node_spec["children"]:
                    validation_results["edge_count"] += 1
                    if child_id not in nodes:
                        validation_results["errors"].append(
                            f"Child node '{child_id}' not found for node '{node_id}'"
                        )
                        validation_results["valid"] = False

        # Check for cycles (simple cycle detection)
        cycles = self._detect_cycles(nodes)
        if cycles:
            validation_results["cycles_detected"] = True
            validation_results["errors"].append(
                f"Cycles detected in graph: {cycles}")
            validation_results["valid"] = False

        # Check for unreachable nodes
        unreachable = self._find_unreachable_nodes(nodes, root_id)
        if unreachable:
            validation_results["unreachable_nodes"] = unreachable
            validation_results["warnings"].append(
                f"Unreachable nodes found: {unreachable}"
            )

        return validation_results

    def _detect_cycles(self, nodes: Dict[str, Any]) -> List[List[str]]:
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

            if node_id in nodes and "children" in nodes[node_id]:
                for child_id in nodes[node_id]["children"]:
                    dfs(child_id, path.copy())

            rec_stack.remove(node_id)

        for node_id in nodes:
            if node_id not in visited:
                dfs(node_id, [])

        return cycles

    def _find_unreachable_nodes(self, nodes: Dict[str, Any], root_id: str) -> List[str]:
        """Find nodes that are not reachable from the root."""
        reachable = set()

        def mark_reachable(node_id: str) -> None:
            if node_id in reachable:
                return
            reachable.add(node_id)

            if node_id in nodes and "children" in nodes[node_id]:
                for child_id in nodes[node_id]["children"]:
                    mark_reachable(child_id)

        mark_reachable(root_id)

        unreachable = [
            node_id for node_id in nodes if node_id not in reachable]
        return unreachable

    def build(self) -> IntentGraph:
        """Build and return the IntentGraph instance.

        Returns:
            Configured IntentGraph instance

        Raises:
            ValueError: If no root nodes have been set and no JSON graph provided
        """
        if self._json_graph is not None:
            # Validate JSON graph before building
            self._validate_json_graph()
            graph = self._build_from_json(
                self._json_graph, self._function_registry or {}
            )
        else:
            if not self._root_nodes:
                raise ValueError(
                    "No root nodes set. Call .root() before .build() or use .with_json()"
                )

            graph = IntentGraph(
                root_nodes=self._root_nodes,
                llm_config=self._llm_config,
                debug_context=self._debug_context_enabled,
                context_trace=self._context_trace_enabled,
            )

            # --- LLM config validation ---
            def check_llm_config(node):
                # Check for LLM classifier nodes (by class name or attribute)
                if hasattr(node, "classifier") and getattr(
                    node.classifier, "__name__", ""
                ).startswith("llm_classifier"):
                    if not (getattr(node, "llm_config", None) or self._llm_config):
                        raise ValueError(
                            f"Node '{getattr(node, 'name', repr(node))}' requires an LLM config, but none was provided at node or graph level."
                        )
                for child in getattr(node, "children", []):
                    check_llm_config(child)

            for root in self._root_nodes:
                check_llm_config(root)
            # --- end validation ---

            # Inject graph-level llm_config into classifier nodes that need it
            def inject_llm_config(node):
                if hasattr(node, "classifier") and getattr(
                    node.classifier, "__name__", ""
                ).startswith("llm_classifier"):
                    self._logger.debug(
                        f"DEBUG: Injecting graph-level llm_config into node BEFORE ATTRIBUTE CHECK '{getattr(node, 'name', repr(node))}'"
                    )
                    if not getattr(node, "llm_config", None):
                        self._logger.debug(
                            f"DEBUG: Injecting graph-level llm_config into node '{getattr(node, 'name', repr(node))}'"
                        )
                        node.llm_config = self._llm_config
                        if hasattr(node, "classifier"):
                            setattr(node.classifier, "llm_config",
                                    self._llm_config)
                    else:
                        self._logger.debug(
                            f"DEBUG: Node '{getattr(node, 'name', repr(node))}' already has llm_config"
                        )
                for child in getattr(node, "children", []):
                    inject_llm_config(child)

            for root in self._root_nodes:
                inject_llm_config(root)

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
            raise ValueError(
                "JSON graph specification must contain a 'root' field")

        if "nodes" not in graph_spec:
            raise ValueError(
                "JSON graph specification must contain an 'nodes' field")

        # Create all nodes first, mapping IDs to nodes
        node_map: Dict[str, TreeNode] = {}

        for node_spec in graph_spec["nodes"].values():
            # Default id to name if not provided
            if "id" not in node_spec:
                if "name" not in node_spec:
                    raise ValueError(
                        f"Node missing required 'id' or 'name' field: {node_spec}"
                    )
                node_spec["id"] = node_spec["name"]

            node_id = node_spec["id"]
            node = self._create_node_from_spec(
                node_id, node_spec, function_registry)
            node_map[node_id] = node

        # Set up parent-child relationships
        for node_spec in graph_spec["nodes"].values():
            node_id = node_spec.get("id", node_spec.get("name"))
            if "children" in node_spec:
                children = []
                for child_id in node_spec["children"]:
                    if child_id not in node_map:
                        raise ValueError(
                            f"Child node '{child_id}' not found in nodes for node '{node_id}'"
                        )
                    children.append(node_map[child_id])
                node_map[node_id].children = children
                # Set parent relationships
                for child in children:
                    child.parent = node_map[node_id]

        # Get root node
        root_id = graph_spec["root"]
        if root_id not in node_map:
            raise ValueError(f"Root node '{root_id}' not found in nodes")

        # Create IntentGraph
        graph = IntentGraph(
            root_nodes=[node_map[root_id]],
            llm_config=self._llm_config,  # Already processed by _process_llm_config
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
        node_type = node_spec.get("type", NodeType.UNKNOWN)
        classifier_type = node_spec.get("classifier_type", ClassifierType.RULE)
        self._logger.debug(
            f"DEBUG: Creating node '{name}' of type '{node_type}'")
        self._logger.debug(
            f"DEBUG: Creating node '{name}' of classifier_type '{classifier_type}'"
        )

        # Dispatch table for node type to creation method
        dispatch = {
            NodeType.ACTION.value: self._create_action_node,
            NodeType.CLASSIFIER.value: lambda *args, **kwargs: (
                self._create_llm_classifier_node(*args, **kwargs)
                if node_spec.get("classifier_type", ClassifierType.RULE.value)
                == ClassifierType.LLM.value
                else self._create_classifier_node(*args, **kwargs)
            ),
        }

        if node_type not in dispatch:
            raise ValueError(
                f"Unknown node type '{node_type}' for node '{node_id}'")

        self._logger.debug(
            f"DEBUG: Creating node '{name}' of type '{node_type}'")
        node_creator = dispatch[node_type]
        if not callable(node_creator):
            raise TypeError(
                f"Node creator for type '{node_type}' is not callable")
        return node_creator(node_id, name, description, node_spec, function_registry)

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
            raise ValueError(
                f"Action node '{node_id}' must have a 'function' field")

        function_name = node_spec["function"]
        if function_name not in function_registry:
            raise ValueError(
                f"Function '{function_name}' not found in function registry for node '{node_id}'"
            )

        action_func = function_registry[function_name]
        param_schema_raw = node_spec.get("param_schema", {})

        # Parse parameter schema from string types to Python types
        from intent_kit.utils.param_extraction import parse_param_schema

        self._logger.debug(
            f"Creating action node '{node_id}' with raw param_schema: {param_schema_raw}"
        )
        param_schema = parse_param_schema(param_schema_raw)
        self._logger.debug(f"Parsed param_schema: {param_schema}")

        raw_llm_config = node_spec.get("llm_config", self._llm_config)
        llm_config = (
            self._process_llm_config(
                raw_llm_config) if raw_llm_config else None
        )
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

        raw_llm_config = node_spec.get("llm_config", self._llm_config)
        llm_config = (
            self._process_llm_config(
                raw_llm_config) if raw_llm_config else None
        )
        if not llm_config:
            raise ValueError(
                f"LLM classifier node '{node_id}' must have an 'llm_config' field or a default must be set on the graph."
            )

        classification_prompt = node_spec.get("classification_prompt")
        remediation_strategies = node_spec.get("remediation_strategies", [])

        # Create a temporary node for now - children will be set later
        # We'll need to create a placeholder and update it after all nodes are created

        if not classification_prompt:
            classification_prompt = get_default_classification_prompt()

        # Create a placeholder classifier function
        classifier_func = create_llm_classifier(
            llm_config, classification_prompt, [])

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
        raw_llm_config = node_spec.get("llm_config", self._llm_config)
        llm_config = (
            self._process_llm_config(
                raw_llm_config) if raw_llm_config else None
        )
        llm_client = None
        if llm_config:
            try:
                llm_client = LLMFactory.create_client(llm_config)
            except Exception as e:
                self._logger.debug(
                    f"Failed to create LLM client for classifier node '{node_id}': {e}"
                )
                pass
        node = ClassifierNode(
            name=name,
            description=description,
            classifier=classifier_func,
            children=[],  # Will be set later
            remediation_strategies=remediation_strategies,
        )
        if llm_client and hasattr(node, "llm_client"):
            node.llm_client = llm_client
        return node

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
