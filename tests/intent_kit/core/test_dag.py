"""Tests for the DAG builder module."""

import pytest
from intent_kit.core.dag import DAGBuilder
from intent_kit.core.types import IntentDAG, GraphNode


class TestDAGBuilder:
    """Test cases for DAGBuilder class."""

    def test_dag_builder_initialization(self):
        """Test DAGBuilder initialization."""
        builder = DAGBuilder()
        assert builder.dag is not None
        assert isinstance(builder.dag, IntentDAG)
        assert not builder._frozen

    def test_dag_builder_with_existing_dag(self):
        """Test DAGBuilder initialization with existing DAG."""
        existing_dag = IntentDAG()
        builder = DAGBuilder(existing_dag)
        assert builder.dag is existing_dag

    def test_add_node_success(self):
        """Test adding a node successfully."""
        builder = DAGBuilder()
        builder.add_node("test_node", "classifier", config_key="value")

        assert "test_node" in builder.dag.nodes
        node = builder.dag.nodes["test_node"]
        assert isinstance(node, GraphNode)
        assert node.id == "test_node"
        assert node.type == "classifier"
        assert node.config["config_key"] == "value"

    def test_add_node_duplicate_id(self):
        """Test adding a node with duplicate ID raises error."""
        builder = DAGBuilder()
        builder.add_node("test_node", "classifier")

        with pytest.raises(ValueError, match="Node test_node already exists"):
            builder.add_node("test_node", "action")

    def test_add_node_invalid_type(self):
        """Test adding a node with invalid type raises error."""
        builder = DAGBuilder()

        with pytest.raises(ValueError, match="Unsupported node type"):
            builder.add_node("test_node", "invalid_type")

    def test_add_node_after_freeze(self):
        """Test adding a node after freezing raises error."""
        builder = DAGBuilder()
        builder.freeze()

        with pytest.raises(RuntimeError, match="Cannot modify frozen DAG"):
            builder.add_node("test_node", "classifier")

    def test_add_edge_success(self):
        """Test adding an edge successfully."""
        builder = DAGBuilder()
        builder.add_node("src", "classifier")
        builder.add_node("dst", "action")

        builder.add_edge("src", "dst", "success")

        assert "success" in builder.dag.adj["src"]
        assert "dst" in builder.dag.adj["src"]["success"]
        assert "src" in builder.dag.rev["dst"]

    def test_add_edge_without_label(self):
        """Test adding an edge without label."""
        builder = DAGBuilder()
        builder.add_node("src", "classifier")
        builder.add_node("dst", "action")

        builder.add_edge("src", "dst")

        assert None in builder.dag.adj["src"]
        assert "dst" in builder.dag.adj["src"][None]

    def test_add_edge_source_not_exists(self):
        """Test adding edge with non-existent source node."""
        builder = DAGBuilder()
        builder.add_node("dst", "action")

        with pytest.raises(ValueError, match="Source node src does not exist"):
            builder.add_edge("src", "dst")

    def test_add_edge_destination_not_exists(self):
        """Test adding edge with non-existent destination node."""
        builder = DAGBuilder()
        builder.add_node("src", "classifier")

        with pytest.raises(ValueError, match="Destination node dst does not exist"):
            builder.add_edge("src", "dst")

    def test_add_edge_after_freeze(self):
        """Test adding edge after freezing raises error."""
        builder = DAGBuilder()
        builder.add_node("src", "classifier")
        builder.add_node("dst", "action")
        builder.freeze()

        with pytest.raises(RuntimeError, match="Cannot modify frozen DAG"):
            builder.add_edge("src", "dst")

    def test_set_entrypoints(self):
        """Test setting entrypoints."""
        builder = DAGBuilder()
        builder.add_node("node1", "classifier")
        builder.add_node("node2", "classifier")

        builder.set_entrypoints(["node1", "node2"])

        assert builder.dag.entrypoints == ["node1", "node2"]

    def test_with_default_llm_config(self):
        """Test setting default LLM configuration."""
        builder = DAGBuilder()
        llm_config = {"provider": "openai", "model": "gpt-4"}

        builder.with_default_llm_config(llm_config)

        assert builder.dag.metadata["default_llm_config"] == llm_config

    def test_with_default_llm_config_after_freeze(self):
        """Test setting LLM config after freezing raises error."""
        builder = DAGBuilder()
        builder.freeze()

        with pytest.raises(RuntimeError, match="Cannot modify frozen DAG"):
            builder.with_default_llm_config({"provider": "openai"})

    def test_freeze(self):
        """Test freezing the DAG."""
        builder = DAGBuilder()
        builder.add_node("node1", "classifier")
        builder.add_node("node2", "action")
        builder.add_edge("node1", "node2")
        builder.set_entrypoints(["node1"])

        builder.freeze()

        assert builder._frozen
        # Check that adjacency lists are frozen
        assert isinstance(builder.dag.adj["node1"][None], frozenset)
        assert isinstance(builder.dag.rev["node2"], frozenset)
        assert isinstance(builder.dag.entrypoints, tuple)

    def test_build_success(self):
        """Test building a valid DAG."""
        builder = DAGBuilder()
        builder.add_node("node1", "classifier")
        builder.add_node("node2", "action")
        builder.add_edge("node1", "node2")
        builder.set_entrypoints(["node1"])

        dag = builder.build()

        assert isinstance(dag, IntentDAG)
        assert "node1" in dag.nodes
        assert "node2" in dag.nodes

    def test_build_with_validation_disabled(self):
        """Test building without validation."""
        builder = DAGBuilder()
        builder.add_node("node1", "classifier")
        builder.add_node("node2", "action")
        builder.add_edge("node1", "node2")
        builder.set_entrypoints(["node1"])

        dag = builder.build(validate_structure=False)

        assert isinstance(dag, IntentDAG)

    def test_get_outgoing_edges(self):
        """Test getting outgoing edges."""
        builder = DAGBuilder()
        builder.add_node("src", "classifier")
        builder.add_node("dst1", "action")
        builder.add_node("dst2", "action")
        builder.add_edge("src", "dst1", "success")
        builder.add_edge("src", "dst2", "failure")

        edges = builder.get_outgoing_edges("src")

        assert "success" in edges
        assert "failure" in edges
        assert "dst1" in edges["success"]
        assert "dst2" in edges["failure"]

    def test_get_outgoing_edges_nonexistent_node(self):
        """Test getting outgoing edges for non-existent node."""
        builder = DAGBuilder()

        edges = builder.get_outgoing_edges("nonexistent")

        assert edges == {}

    def test_get_incoming_edges(self):
        """Test getting incoming edges."""
        builder = DAGBuilder()
        builder.add_node("src1", "classifier")
        builder.add_node("src2", "classifier")
        builder.add_node("dst", "action")
        builder.add_edge("src1", "dst")
        builder.add_edge("src2", "dst")

        edges = builder.get_incoming_edges("dst")

        assert "src1" in edges
        assert "src2" in edges

    def test_get_incoming_edges_nonexistent_node(self):
        """Test getting incoming edges for non-existent node."""
        builder = DAGBuilder()

        edges = builder.get_incoming_edges("nonexistent")

        assert edges == set()

    def test_has_edge_true(self):
        """Test has_edge returns True for existing edge."""
        builder = DAGBuilder()
        builder.add_node("src", "classifier")
        builder.add_node("dst", "action")
        builder.add_edge("src", "dst", "success")

        assert builder.has_edge("src", "dst", "success") is True

    def test_has_edge_false(self):
        """Test has_edge returns False for non-existing edge."""
        builder = DAGBuilder()
        builder.add_node("src", "classifier")
        builder.add_node("dst", "action")
        builder.add_edge("src", "dst", "success")

        assert builder.has_edge("src", "dst", "failure") is False
        assert builder.has_edge("src", "nonexistent") is False
        assert builder.has_edge("nonexistent", "dst") is False

    def test_remove_node_success(self):
        """Test removing a node successfully."""
        builder = DAGBuilder()
        builder.add_node("node1", "classifier")
        builder.add_node("node2", "action")
        builder.add_node("node3", "action")
        builder.add_edge("node1", "node2")
        builder.add_edge("node1", "node3")
        builder.set_entrypoints(["node1"])

        builder.remove_node("node2")

        assert "node2" not in builder.dag.nodes
        assert "node2" not in builder.dag.adj
        assert "node2" not in builder.dag.rev
        assert "node1" in builder.dag.nodes
        assert "node3" in builder.dag.nodes

    def test_remove_node_from_entrypoints(self):
        """Test removing a node that is an entrypoint."""
        builder = DAGBuilder()
        builder.add_node("node1", "classifier")
        builder.add_node("node2", "action")
        builder.set_entrypoints(["node1", "node2"])

        builder.remove_node("node1")

        assert "node1" not in builder.dag.entrypoints
        assert "node2" in builder.dag.entrypoints

    def test_remove_node_nonexistent(self):
        """Test removing a non-existent node raises error."""
        builder = DAGBuilder()

        with pytest.raises(ValueError, match="Node nonexistent does not exist"):
            builder.remove_node("nonexistent")

    def test_remove_node_after_freeze(self):
        """Test removing node after freezing raises error."""
        builder = DAGBuilder()
        builder.add_node("node1", "classifier")
        builder.freeze()

        with pytest.raises(RuntimeError, match="Cannot modify frozen DAG"):
            builder.remove_node("node1")

    def test_validate_node_type_supported(self):
        """Test validation of supported node types."""
        builder = DAGBuilder()

        # These should not raise exceptions
        builder._validate_node_type("classifier")
        builder._validate_node_type("action")
        builder._validate_node_type("extractor")
        builder._validate_node_type("clarification")

    def test_validate_node_type_unsupported(self):
        """Test validation of unsupported node types."""
        builder = DAGBuilder()

        with pytest.raises(ValueError, match="Unsupported node type"):
            builder._validate_node_type("unsupported")


class TestDAGBuilderFromJSON:
    """Test cases for DAGBuilder.from_json method."""

    def test_from_json_success(self):
        """Test creating DAGBuilder from valid JSON config."""
        config = {
            "nodes": {
                "node1": {"type": "classifier", "config_key": "value"},
                "node2": {"type": "action", "another_key": "another_value"},
            },
            "edges": [{"from": "node1", "to": "node2", "label": "success"}],
            "entrypoints": ["node1"],
        }

        builder = DAGBuilder.from_json(config)

        assert "node1" in builder.dag.nodes
        assert "node2" in builder.dag.nodes
        assert builder.dag.nodes["node1"].type == "classifier"
        assert builder.dag.nodes["node2"].type == "action"
        assert builder.dag.entrypoints == ["node1"]

    def test_from_json_invalid_config_type(self):
        """Test from_json with invalid config type."""
        with pytest.raises(ValueError, match="Config must be a dictionary"):
            DAGBuilder.from_json("not a dict")  # type: ignore

    def test_from_json_missing_required_keys(self):
        """Test from_json with missing required keys."""
        config = {"nodes": {}}

        with pytest.raises(ValueError, match="Missing required keys"):
            DAGBuilder.from_json(config)

    def test_from_json_invalid_node_config(self):
        """Test from_json with invalid node configuration."""
        config = {"nodes": {"node1": "not a dict"}, "edges": [], "entrypoints": []}

        with pytest.raises(
            ValueError, match="Node config for node1 must be a dictionary"
        ):
            DAGBuilder.from_json(config)

    def test_from_json_node_missing_type(self):
        """Test from_json with node missing type field."""
        config = {
            "nodes": {"node1": {"config_key": "value"}},
            "edges": [],
            "entrypoints": [],
        }

        with pytest.raises(
            ValueError, match="Node node1 missing required 'type' field"
        ):
            DAGBuilder.from_json(config)

    def test_from_json_invalid_edge(self):
        """Test from_json with invalid edge configuration."""
        config = {
            "nodes": {"node1": {"type": "classifier"}},
            "edges": ["not a dict"],
            "entrypoints": [],
        }

        with pytest.raises(ValueError, match="Edge must be a dictionary"):
            DAGBuilder.from_json(config)

    def test_from_json_edge_missing_required_keys(self):
        """Test from_json with edge missing required keys."""
        config = {
            "nodes": {"node1": {"type": "classifier"}},
            "edges": [{"from": "node1"}],  # Missing "to"
            "entrypoints": [],
        }

        with pytest.raises(ValueError, match="Edge missing required keys"):
            DAGBuilder.from_json(config)

    def test_from_json_invalid_entrypoints(self):
        """Test from_json with invalid entrypoints."""
        config = {
            "nodes": {"node1": {"type": "classifier"}},
            "edges": [],
            "entrypoints": "not a list",
        }

        with pytest.raises(ValueError, match="Entrypoints must be a list"):
            DAGBuilder.from_json(config)
