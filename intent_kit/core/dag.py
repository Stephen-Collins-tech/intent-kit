"""Core DAG builder for intent-kit."""

from typing import Dict, Set, Optional, Any
from intent_kit.core.types import GraphNode
from intent_kit.core.types import IntentDAG, EdgeLabel
from intent_kit.core.validation import validate_dag_structure


class DAGBuilder:
    """Builder for creating and modifying IntentDAG instances."""

    def __init__(self, dag: Optional[IntentDAG] = None):
        """Initialize the builder with an optional existing DAG."""
        self.dag = dag or IntentDAG()
        self._frozen = False

    @classmethod
    def from_json(cls, config: Dict[str, Any]) -> "DAGBuilder":
        """Create a DAGBuilder from a JSON configuration dictionary.

        Args:
            config: Dictionary containing DAG configuration with keys:
                - nodes: Dict mapping node_id to node configuration
                - edges: List of edge dictionaries with 'from', 'to', 'label' keys
                - entrypoints: List of entrypoint node IDs

        Returns:
            Configured DAGBuilder instance

        Raises:
            ValueError: If configuration is invalid or missing required keys
        """
        if not isinstance(config, dict):
            raise ValueError("Config must be a dictionary")

        required_keys = ["nodes", "edges", "entrypoints"]
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValueError(f"Missing required keys in config: {missing_keys}")

        builder = cls()

        # Add nodes
        for node_id, node_config in config["nodes"].items():
            if not isinstance(node_config, dict):
                raise ValueError(f"Node config for {node_id} must be a dictionary")

            if "type" not in node_config:
                raise ValueError(f"Node {node_id} missing required 'type' field")

            node_type = node_config.pop("type")
            builder.add_node(node_id, node_type, **node_config)

        # Add edges
        for edge in config["edges"]:
            if not isinstance(edge, dict):
                raise ValueError("Edge must be a dictionary")

            required_edge_keys = ["from", "to"]
            missing_edge_keys = [key for key in required_edge_keys if key not in edge]
            if missing_edge_keys:
                raise ValueError(f"Edge missing required keys: {missing_edge_keys}")

            label = edge.get("label")
            builder.add_edge(edge["from"], edge["to"], label)

        # Set entrypoints
        entrypoints = config["entrypoints"]
        if not isinstance(entrypoints, list):
            raise ValueError("Entrypoints must be a list")

        builder.set_entrypoints(entrypoints)

        return builder

    def add_node(self, node_id: str, node_type: str, **config) -> "DAGBuilder":
        """Add a node to the DAG.

        Args:
            node_id: Unique identifier for the node
            node_type: Type of the node (e.g., 'classifier', 'action')
            **config: Additional configuration for the node

        Returns:
            Self for method chaining

        Raises:
            ValueError: If node_id already exists or is invalid
        """
        if self._frozen:
            raise RuntimeError("Cannot modify frozen DAG")

        if node_id in self.dag.nodes:
            raise ValueError(f"Node {node_id} already exists")

        # Validate node type is supported
        self._validate_node_type(node_type)

        node = GraphNode(id=node_id, type=node_type, config=config)
        self.dag.nodes[node_id] = node
        self.dag.adj[node_id] = {}
        self.dag.rev[node_id] = set()

        return self

    def add_edge(self, src: str, dst: str, label: EdgeLabel = None) -> "DAGBuilder":
        """Add an edge from src to dst with optional label.

        Args:
            src: Source node ID
            dst: Destination node ID
            label: Optional edge label (None means default/fall-through)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If src or dst nodes don't exist
            RuntimeError: If DAG is frozen
        """
        if self._frozen:
            raise RuntimeError("Cannot modify frozen DAG")

        if src not in self.dag.nodes:
            raise ValueError(f"Source node {src} does not exist")
        if dst not in self.dag.nodes:
            raise ValueError(f"Destination node {dst} does not exist")

        # Add to adjacency list
        if label not in self.dag.adj[src]:
            self.dag.adj[src][label] = set()
        self.dag.adj[src][label].add(dst)

        # Add to reverse adjacency list
        self.dag.rev[dst].add(src)

        return self

    def set_entrypoints(self, entrypoints: list[str]) -> "DAGBuilder":
        """Set the entrypoints for the DAG.

        Args:
            entrypoints: List of node IDs that are entry points

        Returns:
            Self for method chaining
        """
        self.dag.entrypoints = entrypoints
        return self

    def with_default_llm_config(self, llm_config: Dict[str, Any]) -> "DAGBuilder":
        """Set default LLM configuration for the graph.

        This configuration will be used by nodes that don't have their own llm_config.

        Args:
            llm_config: Default LLM configuration dictionary

        Returns:
            Self for method chaining
        """
        if self._frozen:
            raise RuntimeError("Cannot modify frozen DAG")

        # Store the default config in the DAG metadata
        if not hasattr(self.dag, "metadata"):
            self.dag.metadata = {}
        self.dag.metadata["default_llm_config"] = llm_config
        return self

    def freeze(self) -> "DAGBuilder":
        """Make the DAG immutable to catch mutation bugs."""
        self._frozen = True

        # Make sets immutable
        frozen_adj: Dict[str, Dict[EdgeLabel, frozenset[str]]] = {}
        for node_id, labels in self.dag.adj.items():
            frozen_adj[node_id] = {}
            for label, dsts in labels.items():
                frozen_adj[node_id][label] = frozenset(dsts)
        self.dag.adj = frozen_adj  # type: ignore[assignment]

        frozen_rev = {}
        for node_id, srcs in self.dag.rev.items():
            frozen_rev[node_id] = frozenset(srcs)
        self.dag.rev = frozen_rev  # type: ignore[assignment]

        self.dag.entrypoints = tuple(self.dag.entrypoints)

        return self

    def build(
        self,
        validate_structure: bool = True,
        producer_labels: Optional[Dict[str, Set[str]]] = None,
    ) -> IntentDAG:
        """Build and return the final IntentDAG.

        Args:
            validate_structure: Whether to validate the DAG structure before returning
            producer_labels: Optional dictionary mapping node_id to set of labels it can produce

        Returns:
            The built IntentDAG

        Raises:
            ValueError: If validation fails and validate_structure is True
            CycleError: If a cycle is detected and validate_structure is True
        """
        if validate_structure:
            issues = validate_dag_structure(self.dag, producer_labels)
            if issues:
                raise ValueError(f"DAG validation failed: {'; '.join(issues)}")

        return self.dag

    def _validate_node_type(self, node_type: str) -> None:
        """Validate that a node type is supported.

        Args:
            node_type: The node type to validate

        Raises:
            ValueError: If the node type is not supported
        """
        supported_types = {"classifier", "action", "extractor", "clarification"}

        if node_type not in supported_types:
            raise ValueError(
                f"Unsupported node type '{node_type}'. "
                f"Supported types: {sorted(supported_types)}"
            )

    def get_outgoing_edges(self, node_id: str) -> Dict[EdgeLabel, Set[str]]:
        """Get outgoing edges from a node.

        Args:
            node_id: The node ID

        Returns:
            Dictionary mapping edge labels to sets of destination node IDs
        """
        return self.dag.adj.get(node_id, {})

    def get_incoming_edges(self, node_id: str) -> Set[str]:
        """Get incoming edges to a node.

        Args:
            node_id: The node ID

        Returns:
            Set of source node IDs
        """
        return self.dag.rev.get(node_id, set())

    def has_edge(self, src: str, dst: str, label: EdgeLabel = None) -> bool:
        """Check if an edge exists.

        Args:
            src: Source node ID
            dst: Destination node ID
            label: Optional edge label

        Returns:
            True if the edge exists, False otherwise
        """
        if src not in self.dag.adj:
            return False
        if label not in self.dag.adj[src]:
            return False
        return dst in self.dag.adj[src][label]

    def remove_node(self, node_id: str) -> "DAGBuilder":
        """Remove a node and all its edges.

        Args:
            node_id: The node ID to remove

        Returns:
            Self for method chaining

        Raises:
            RuntimeError: If DAG is frozen
            ValueError: If node doesn't exist
        """
        if self._frozen:
            raise RuntimeError("Cannot modify frozen DAG")

        if node_id not in self.dag.nodes:
            raise ValueError(f"Node {node_id} does not exist")

        # Remove from entrypoints
        if node_id in self.dag.entrypoints:
            if isinstance(self.dag.entrypoints, list):
                self.dag.entrypoints.remove(node_id)
            else:
                # Convert tuple to list, remove, then convert back
                entrypoints_list = list(self.dag.entrypoints)
                entrypoints_list.remove(node_id)
                self.dag.entrypoints = tuple(entrypoints_list)

        # Remove all incoming edges
        for src in self.dag.rev[node_id]:
            for label, dsts in self.dag.adj[src].items():
                if node_id in dsts:
                    dsts.remove(node_id)
                    if not dsts:  # Remove empty label entry
                        del self.dag.adj[src][label]

        # Remove all outgoing edges
        for dst in self.dag.adj[node_id].values():
            for target in dst:
                self.dag.rev[target].discard(node_id)

        # Remove node
        del self.dag.nodes[node_id]
        del self.dag.adj[node_id]
        del self.dag.rev[node_id]

        return self
