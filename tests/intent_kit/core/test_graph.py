"""Tests for core DAG graph types."""

import pytest
from intent_kit.core import GraphNode, IntentDAG, ExecutionResult, DAGBuilder


class TestGraphNode:
    """Test GraphNode functionality."""

    def test_create_node(self):
        """Test creating a basic node."""
        node = GraphNode(id="test", type="classifier", config={"key": "value"})
        assert node.id == "test"
        assert node.type == "classifier"
        assert node.config == {"key": "value"}

    def test_node_validation(self):
        """Test node validation."""
        with pytest.raises(ValueError, match="Node ID cannot be empty"):
            GraphNode(id="", type="classifier")

        with pytest.raises(ValueError, match="Node type cannot be empty"):
            GraphNode(id="test", type="")


class TestIntentDAG:
    """Test IntentDAG functionality."""

    def test_create_empty_dag(self):
        """Test creating an empty DAG."""
        dag = IntentDAG()
        assert len(dag.nodes) == 0
        assert len(dag.adj) == 0
        assert len(dag.rev) == 0
        assert len(dag.entrypoints) == 0

    def test_add_node(self):
        """Test adding nodes to DAG."""
        builder = DAGBuilder()
        builder.add_node("test", "dag_classifier", key="value")
        builder.set_entrypoints(["test"])
        dag = builder.build()

        assert dag.nodes["test"].id == "test"
        assert dag.nodes["test"].type == "dag_classifier"
        assert dag.nodes["test"].config == {"key": "value"}
        assert "test" in dag.nodes
        assert "test" in dag.adj
        assert "test" in dag.rev

    def test_add_duplicate_node(self):
        """Test adding duplicate node raises error."""
        builder = DAGBuilder()
        builder.add_node("test", "dag_classifier")

        with pytest.raises(ValueError, match="Node test already exists"):
            builder.add_node("test", "dag_action")

    def test_add_edge(self):
        """Test adding edges between nodes."""
        builder = DAGBuilder()
        builder.add_node("src", "dag_classifier")
        builder.add_node("dst", "dag_action")

        builder.add_edge("src", "dst", "success")

        assert builder.has_edge("src", "dst", "success")
        assert "dst" in builder.get_outgoing_edges("src")["success"]
        assert "src" in builder.get_incoming_edges("dst")

    def test_add_edge_nonexistent_nodes(self):
        """Test adding edge with nonexistent nodes raises error."""
        builder = DAGBuilder()

        with pytest.raises(ValueError, match="Source node src does not exist"):
            builder.add_edge("src", "dst", "label")

        builder.add_node("src", "dag_classifier")
        with pytest.raises(ValueError, match="Destination node dst does not exist"):
            builder.add_edge("src", "dst", "label")

    def test_freeze_dag(self):
        """Test freezing DAG makes it immutable."""
        builder = DAGBuilder()
        builder.add_node("test", "dag_classifier")
        builder.freeze()

        with pytest.raises(RuntimeError, match="Cannot modify frozen DAG"):
            builder.add_node("another", "dag_action")

        with pytest.raises(RuntimeError, match="Cannot modify frozen DAG"):
            builder.add_edge("test", "another", "label")


class TestExecutionResult:
    """Test ExecutionResult functionality."""

    def test_create_result(self):
        """Test creating execution result."""
        result = ExecutionResult(
            data="test_data",
            next_edges=["success", "fallback"],
            terminate=False,
            metrics={"tokens": 100},
            context_patch={"user_id": "123"}
        )

        assert result.data == "test_data"
        assert result.next_edges == ["success", "fallback"]
        assert result.terminate is False
        assert result.metrics == {"tokens": 100}
        assert result.context_patch == {"user_id": "123"}

    def test_merge_metrics(self):
        """Test merging metrics."""
        result = ExecutionResult(metrics={"tokens": 100, "cost": 0.01})
        result.merge_metrics({"tokens": 50, "errors": 1})

        assert result.metrics["tokens"] == 150  # Should add numeric values
        assert result.metrics["cost"] == 0.01   # Should preserve existing
        assert result.metrics["errors"] == 1    # Should add new
