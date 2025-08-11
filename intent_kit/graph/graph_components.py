"""
Composition classes for building intent graphs.

This module contains specialized classes that work together to construct
intent graphs from various specifications (JSON, YAML, etc.).
"""

from typing import List, Dict, Any, Optional, Callable, Union
from intent_kit.nodes import TreeNode
from intent_kit.nodes.enums import NodeType
from intent_kit.graph import IntentGraph
from intent_kit.services.yaml_service import yaml_service
from intent_kit.utils.logger import Logger
from intent_kit.nodes.actions import ActionNode
from intent_kit.nodes.classifiers import ClassifierNode
import os


class JsonParser:
    """Handles JSON and YAML parsing for graph specifications."""

    def __init__(self):
        self.logger = Logger("json_parser")

    def parse_yaml(self, yaml_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Parse YAML input (file path or dict) into JSON dict."""
        if isinstance(yaml_input, str):
            # Treat as file path
            try:
                with open(yaml_input, "r") as f:
                    return yaml_service.safe_load(f)
            except Exception as e:
                raise ValueError(f"Failed to load YAML file '{yaml_input}': {e}")
        else:
            # Treat as dict
            return yaml_input


class LLMConfigProcessor:
    """Processes and validates LLM configurations."""

    def __init__(self):
        self.logger = Logger("llm_config_processor")
        self.supported_providers = {
            "openai",
            "anthropic",
            "google",
            "openrouter",
            "ollama",
        }

    def process_config(
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
                    self.logger.debug(
                        f"Resolved environment variable {env_var} for key {key}"
                    )
                else:
                    self.logger.warning(
                        f"Environment variable {env_var} not found for key {key}"
                    )
                    processed_config[key] = value  # Keep original value
            else:
                processed_config[key] = value

        # Validate that we have required fields for supported providers
        provider = processed_config.get("provider", "").lower()
        if provider in self.supported_providers:
            if provider != "ollama" and not processed_config.get("api_key"):
                self.logger.warning(
                    f"Provider {provider} requires api_key but none found in config"
                )

        return processed_config


class GraphValidator:
    """Validates graph specifications and node relationships."""

    def __init__(self):
        self.logger = Logger("graph_validator")

    def validate_graph_spec(self, graph_spec: Dict[str, Any]) -> None:
        """Validate basic graph structure."""
        if "root" not in graph_spec or "nodes" not in graph_spec:
            raise ValueError("Graph spec must have 'root' and 'nodes' fields")

    def validate_node_spec(self, node_id: str, node_spec: Dict[str, Any]) -> None:
        """Validate individual node specification."""
        if "id" not in node_spec and "name" not in node_spec:
            raise ValueError(f"Node missing required 'id' or 'name' field: {node_spec}")

        if "type" not in node_spec:
            raise ValueError(f"Node '{node_id}' must have a 'type' field")

    def validate_node_references(self, graph_spec: Dict[str, Any]) -> None:
        """Validate that all node references exist."""
        nodes = graph_spec["nodes"]
        root_id = graph_spec["root"]

        if root_id not in nodes:
            raise ValueError(f"Root node '{root_id}' not found in nodes")

        for node_id, node_spec in nodes.items():
            if "children" in node_spec:
                for child_id in node_spec["children"]:
                    if child_id not in nodes:
                        raise ValueError(
                            f"Child node '{child_id}' not found for node '{node_id}'"
                        )

    def detect_cycles(self, nodes: Dict[str, Any]) -> List[List[str]]:
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

    def find_unreachable_nodes(self, nodes: Dict[str, Any], root_id: str) -> List[str]:
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

        unreachable = [node_id for node_id in nodes if node_id not in reachable]
        return unreachable


class NodeFactory:
    """Creates node builders from specifications."""

    def __init__(
        self,
        function_registry: Dict[str, Callable],
        default_llm_config: Optional[Dict[str, Any]] = None,
    ):
        self.function_registry = function_registry
        self.default_llm_config = default_llm_config
        self.llm_processor = LLMConfigProcessor()

    def create_node_builder(self, node_id: str, node_spec: Dict[str, Any]):
        """Create a node builder using the appropriate builder."""
        node_type = node_spec.get("type")

        # Use node-specific LLM config if available, otherwise use default
        raw_node_llm_config = node_spec.get("llm_config", self.default_llm_config)

        # Process the LLM config to handle environment variable substitution
        node_llm_config = self.llm_processor.process_config(raw_node_llm_config)

        if node_type == NodeType.ACTION.value:
            return ActionNode.from_json(
                node_spec, self.function_registry, node_llm_config
            )
        elif node_type == NodeType.CLASSIFIER.value:
            if "children" not in node_spec:
                raise ValueError(
                    f"Classifier node '{node_id}' must have 'children' field"
                )
            return ClassifierNode.from_json(
                node_spec, self.function_registry, node_llm_config
            )
        else:
            raise ValueError(f"Unknown node type '{node_type}' for node '{node_id}'")


class RelationshipBuilder:
    """Builds parent-child relationships between nodes."""

    @staticmethod
    def build_relationships(
        graph_spec: Dict[str, Any], node_map: Dict[str, TreeNode]
    ) -> None:
        """Set up parent-child relationships for all nodes."""
        for node_id, node_spec in graph_spec["nodes"].items():
            if "children" in node_spec:
                children = []
                for child_id in node_spec["children"]:
                    if child_id not in node_map:
                        raise ValueError(
                            f"Child node '{child_id}' not found for node '{node_id}'"
                        )
                    children.append(node_map[child_id])
                node_map[node_id].children = children
                # Set parent relationships
                for child in children:
                    child.parent = node_map[node_id]


class GraphConstructor:
    """Constructs graphs from JSON specifications."""

    def __init__(
        self,
        validator: GraphValidator,
        node_factory: NodeFactory,
        relationship_builder: RelationshipBuilder,
    ):
        self.validator = validator
        self.node_factory = node_factory
        self.relationship_builder = relationship_builder

    def construct_from_json(
        self,
        graph_spec: Dict[str, Any],
        default_llm_config: Optional[Dict[str, Any]] = None,
    ) -> IntentGraph:
        """Construct an IntentGraph from JSON specification."""
        # Validate graph specification
        self.validator.validate_graph_spec(graph_spec)
        self.validator.validate_node_references(graph_spec)

        # Create all nodes first, mapping IDs to nodes
        node_map: Dict[str, TreeNode] = {}

        for node_id, node_spec in graph_spec["nodes"].items():
            # Validate individual node
            self.validator.validate_node_spec(node_id, node_spec)

            # Default id to name if not provided
            if "id" not in node_spec:
                node_spec["id"] = node_spec["name"]

            # Create node using factory
            result = self.node_factory.create_node_builder(node_id, node_spec)
            # Both ActionNode.from_json and ClassifierNode.from_json return nodes directly
            node = result
            node_map[node_id] = node

        # Set parent-child relationships on built nodes
        for node_id, node_spec in graph_spec["nodes"].items():
            if "children" in node_spec:
                children = []
                for child_id in node_spec["children"]:
                    if child_id not in node_map:
                        raise ValueError(
                            f"Child node '{child_id}' not found for node '{node_id}'"
                        )
                    children.append(node_map[child_id])
                node_map[node_id].children = children
                # Set parent relationships
                for child in children:
                    child.parent = node_map[node_id]

        # Get root node
        root_id = graph_spec["root"]
        root_node = node_map[root_id]

        # Create IntentGraph
        return IntentGraph(
            root_nodes=[root_node],
            llm_config=default_llm_config,
            debug_context=False,
            context_trace=False,
        )
