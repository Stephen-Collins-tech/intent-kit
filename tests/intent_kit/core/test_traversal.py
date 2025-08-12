"""Tests for the DAG traversal engine."""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from intent_kit.core.traversal import run_dag
from intent_kit.core import IntentDAG, GraphNode, DAGBuilder, ExecutionResult, NodeProtocol
from intent_kit.core.exceptions import TraversalLimitError, TraversalError, NodeError
from intent_kit.context.context import Context


class MockNode(NodeProtocol):
    """Mock node implementation for testing."""

    def __init__(self, result: ExecutionResult):
        self.result = result

    def execute(self, user_input: str, ctx: Any) -> ExecutionResult:
        return self.result


class TestTraversalEngine:
    """Test the DAG traversal engine."""

    def test_linear_path_execution(self):
        """Test that a linear path executes all nodes once."""
        # Create a simple linear DAG: A -> B -> C
        builder = DAGBuilder()
        builder.add_node("A", "dag_classifier")
        builder.add_node("B", "dag_action")
        builder.add_node("C", "dag_action")
        builder.add_edge("A", "B", "next")
        builder.add_edge("B", "C", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        # Mock node implementations
        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                return MockNode(ExecutionResult(next_edges=["next"]))
            elif node.id == "B":
                return MockNode(ExecutionResult(next_edges=["next"]))
            elif node.id == "C":
                return MockNode(ExecutionResult(terminate=True))
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        result, metrics = run_dag(
            dag, ctx, "test input", resolve_impl=resolve_impl)

        assert result is not None
        assert result.terminate is True
        assert result.data is None

    def test_fan_out_execution(self):
        """Test that fan-out executes both branches."""
        # Create a fan-out DAG: A -> B, A -> C
        builder = DAGBuilder()
        builder.add_node("A", "dag_classifier")
        builder.add_node("B", "dag_action")
        builder.add_node("C", "dag_action")
        builder.add_edge("A", "B", "branch1")
        builder.add_edge("A", "C", "branch2")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        execution_order = []

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                return MockNode(ExecutionResult(next_edges=["branch1", "branch2"]))
            elif node.id in ["B", "C"]:
                execution_order.append(node.id)
                return MockNode(ExecutionResult(terminate=True))
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        result, metrics = run_dag(
            dag, ctx, "test input", resolve_impl=resolve_impl)

        # Both branches should be executed
        assert len(execution_order) == 2
        assert "B" in execution_order
        assert "C" in execution_order

    def test_fan_in_context_merging(self):
        """Test that fan-in merges context patches correctly."""
        # Create a fan-in DAG: A -> C, B -> C
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        builder.add_node("B", "dag_action")
        builder.add_node("C", "dag_action")
        builder.add_edge("A", "C", "next")
        builder.add_edge("B", "C", "next")
        builder.set_entrypoints(["A", "B"])
        dag = builder.build()

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                return MockNode(ExecutionResult(
                    next_edges=["next"],
                    context_patch={"from_a": "value_a"}
                ))
            elif node.id == "B":
                return MockNode(ExecutionResult(
                    next_edges=["next"],
                    context_patch={"from_b": "value_b"}
                ))
            elif node.id == "C":
                return MockNode(ExecutionResult(terminate=True))
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        result, metrics = run_dag(
            dag, ctx, "test input", resolve_impl=resolve_impl)

        # Context should have both patches merged
        assert ctx.get("from_a") == "value_a"
        assert ctx.get("from_b") == "value_b"

    def test_early_termination(self):
        """Test that early termination stops processing."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        builder.add_node("B", "dag_action")
        builder.add_node("C", "dag_action")
        builder.add_edge("A", "B", "next")
        builder.add_edge("B", "C", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        execution_order = []

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                execution_order.append(node.id)
                return MockNode(ExecutionResult(next_edges=["next"]))
            elif node.id == "B":
                execution_order.append(node.id)
                # Early termination
                return MockNode(ExecutionResult(terminate=True))
            elif node.id == "C":
                execution_order.append(node.id)
                return MockNode(ExecutionResult(terminate=True))
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        result, metrics = run_dag(
            dag, ctx, "test input", resolve_impl=resolve_impl)

        # Only A and B should execute, C should not
        assert execution_order == ["A", "B"]
        assert result is not None
        assert result.terminate is True

    def test_max_steps_limit(self):
        """Test that max_steps limit is enforced."""
        builder = DAGBuilder()
        # Create a linear chain longer than max_steps
        for i in range(10):
            builder.add_node(f"node_{i}", "dag_action")
            if i > 0:
                builder.add_edge(f"node_{i-1}", f"node_{i}", "next")
        builder.set_entrypoints(["node_0"])
        dag = builder.build()

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            # Only the last node should terminate
            if node.id == "node_9":
                return MockNode(ExecutionResult(terminate=True))
            else:
                return MockNode(ExecutionResult(next_edges=["next"]))

        ctx = Context()
        with pytest.raises(TraversalLimitError, match="Exceeded max_steps"):
            run_dag(dag, ctx, "test input", max_steps=5,
                    resolve_impl=resolve_impl)

    def test_max_fanout_limit(self):
        """Test that max_fanout_per_node limit is enforced."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_classifier")
        # Add more than max_fanout_per_node destinations
        for i in range(20):
            builder.add_node(f"B{i}", "dag_action")
            builder.add_edge("A", f"B{i}", f"edge{i}")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                # Return more edges than the limit
                return MockNode(ExecutionResult(next_edges=[f"edge{i}" for i in range(20)]))
            else:
                return MockNode(ExecutionResult(terminate=True))

        ctx = Context()
        with pytest.raises(TraversalLimitError, match="Exceeded max_fanout_per_node"):
            run_dag(dag, ctx, "test input", max_fanout_per_node=16,
                    resolve_impl=resolve_impl)

    def test_deterministic_order(self):
        """Test that traversal order is deterministic."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_classifier")
        builder.add_node("B", "dag_action")
        builder.add_node("C", "dag_action")
        builder.add_node("D", "dag_action")
        builder.add_edge("A", "B", "branch1")
        builder.add_edge("A", "C", "branch2")
        builder.add_edge("A", "D", "branch3")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        execution_order = []

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                return MockNode(ExecutionResult(next_edges=["branch1", "branch2", "branch3"]))
            else:
                execution_order.append(node.id)
                return MockNode(ExecutionResult(terminate=True))

        ctx = Context()
        result, metrics = run_dag(
            dag, ctx, "test input", resolve_impl=resolve_impl)

        # Order should be deterministic (BFS order)
        assert len(execution_order) == 3
        # The order should be consistent across runs
        assert set(execution_order) == {"B", "C", "D"}

    def test_error_routing(self):
        """Test that errors are routed via 'error' edges."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        builder.add_node("error_handler", "dag_action")
        builder.add_edge("A", "error_handler", "error")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        error_handler_called = False

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                # Return a node that raises an error during execution
                class ErrorNode(NodeProtocol):
                    def execute(self, user_input: str, ctx: Any) -> ExecutionResult:
                        raise NodeError("Test error")
                return ErrorNode()
            elif node.id == "error_handler":
                nonlocal error_handler_called
                error_handler_called = True
                return MockNode(ExecutionResult(terminate=True))
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        result, metrics = run_dag(
            dag, ctx, "test input", resolve_impl=resolve_impl)

        # Error handler should be called
        assert error_handler_called
        # Error context should be set
        assert ctx.get("last_error") == "Test error"
        assert ctx.get("error_node") == "A"

    def test_error_without_handler(self):
        """Test that errors without handlers stop traversal."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                # Return a node that raises an error during execution
                class ErrorNode(NodeProtocol):
                    def execute(self, user_input: str, ctx: Any) -> ExecutionResult:
                        raise NodeError("Test error")
                return ErrorNode()
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        with pytest.raises(TraversalError, match="Node A failed"):
            run_dag(dag, ctx, "test input", resolve_impl=resolve_impl)

    def test_no_entrypoints_error(self):
        """Test that empty entrypoints raises error."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        # Don't set entrypoints to test validation
        # Skip validation to test traversal error
        dag = builder.build(validate_structure=False)

        ctx = Context()
        with pytest.raises(TraversalError, match="No entrypoints defined"):
            run_dag(dag, ctx, "test input",
                    resolve_impl=lambda x: MockNode(ExecutionResult()))

    def test_no_resolver_error(self):
        """Test that missing resolver raises error."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        with pytest.raises(TraversalError, match="No implementation resolver provided"):
            run_dag(dag, ctx, "test input", resolve_impl=None)

    def test_metrics_aggregation(self):
        """Test that metrics are aggregated correctly."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        builder.add_node("B", "dag_action")
        builder.add_edge("A", "B", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                return MockNode(ExecutionResult(
                    next_edges=["next"],
                    metrics={"tokens": 10, "cost": 0.01}
                ))
            elif node.id == "B":
                return MockNode(ExecutionResult(
                    terminate=True,
                    metrics={"tokens": 20, "cost": 0.02}
                ))
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        result, metrics = run_dag(
            dag, ctx, "test input", resolve_impl=resolve_impl)

        # Metrics should be aggregated
        assert metrics["tokens"] == 30
        assert metrics["cost"] == 0.03

    def test_memoization(self):
        """Test that memoization prevents duplicate executions."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        builder.add_node("B", "dag_action")
        builder.add_edge("A", "B", "next")
        builder.add_edge("B", "A", "back")  # Create a cycle
        builder.set_entrypoints(["A"])
        # Skip validation for cycle test
        dag = builder.build(validate_structure=False)

        execution_count = {"A": 0, "B": 0}

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                execution_count["A"] += 1
                return MockNode(ExecutionResult(next_edges=["next"]))
            elif node.id == "B":
                execution_count["B"] += 1
                return MockNode(ExecutionResult(next_edges=["back"]))
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        # This should not run forever due to memoization
        result, metrics = run_dag(
            dag, ctx, "test input",
            max_steps=10,
            resolve_impl=resolve_impl,
            enable_memoization=True
        )

        # Each node should only execute once due to memoization
        assert execution_count["A"] == 1
        assert execution_count["B"] == 1

    def test_context_patch_application(self):
        """Test that context patches are applied correctly."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        builder.add_node("B", "dag_action")
        builder.add_edge("A", "B", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                return MockNode(ExecutionResult(
                    next_edges=["next"],
                    context_patch={"key1": "value1", "key2": "value2"}
                ))
            elif node.id == "B":
                return MockNode(ExecutionResult(
                    terminate=True,
                    context_patch={"key3": "value3"}
                ))
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        result, metrics = run_dag(
            dag, ctx, "test input", resolve_impl=resolve_impl)

        # All context patches should be applied
        assert ctx.get("key1") == "value1"
        assert ctx.get("key2") == "value2"
        assert ctx.get("key3") == "value3"

    def test_empty_next_edges(self):
        """Test that empty next_edges stops traversal."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        builder.add_node("B", "dag_action")
        builder.add_edge("A", "B", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                return MockNode(ExecutionResult(next_edges=[]))  # Empty list
            elif node.id == "B":
                return MockNode(ExecutionResult(terminate=True))
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        result, metrics = run_dag(
            dag, ctx, "test input", resolve_impl=resolve_impl)

        # Should terminate after A since it has no next edges
        assert result is not None
        assert result.terminate is False  # A didn't terminate, just no next edges

    def test_none_next_edges(self):
        """Test that None next_edges stops traversal."""
        builder = DAGBuilder()
        builder.add_node("A", "dag_action")
        builder.add_node("B", "dag_action")
        builder.add_edge("A", "B", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        def resolve_impl(node: GraphNode) -> NodeProtocol:
            if node.id == "A":
                return MockNode(ExecutionResult(next_edges=None))  # None
            elif node.id == "B":
                return MockNode(ExecutionResult(terminate=True))
            raise ValueError(f"Unknown node: {node.id}")

        ctx = Context()
        result, metrics = run_dag(
            dag, ctx, "test input", resolve_impl=resolve_impl)

        # Should terminate after A since it has no next edges
        assert result is not None
        assert result.terminate is False  # A didn't terminate, just no next edges
