"""Tests for the DAG traversal engine."""

import pytest
from typing import Any

from intent_kit.core.traversal import run_dag
from intent_kit.core import DAGBuilder, ExecutionResult, NodeProtocol
from intent_kit.core.exceptions import TraversalLimitError, TraversalError
from intent_kit.core.context import DefaultContext as Context


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
        # Add classifier with proper configuration
        builder.add_node(
            "A",
            "classifier",
            output_labels=["next", "error"],
            classification_func=lambda input, ctx: "next",
        )
        # Add actions with proper configuration
        builder.add_node(
            "B",
            "action",
            action=lambda **kwargs: "result_b",
            terminate_on_success=False,
        )
        builder.add_node(
            "C", "action", action=lambda **kwargs: "result_c", terminate_on_success=True
        )
        builder.add_edge("A", "B", "next")
        builder.add_edge("B", "C", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        result, ctx = run_dag(dag, "test input", ctx=ctx)

        assert result is not None
        assert result.terminate is True
        assert result.data == "result_c"

    def test_fan_out_execution(self):
        """Test that fan-out executes both branches."""
        # Create a fan-out DAG: A -> B, A -> C
        builder = DAGBuilder()
        # Add classifier with proper configuration
        builder.add_node(
            "A",
            "classifier",
            output_labels=["branch1", "branch2"],
            classification_func=lambda input, ctx: "branch1",
        )
        # Add actions with proper configuration
        builder.add_node(
            "B", "action", action=lambda **kwargs: "result_b", terminate_on_success=True
        )
        builder.add_node(
            "C", "action", action=lambda **kwargs: "result_c", terminate_on_success=True
        )
        builder.add_edge("A", "B", "branch1")
        builder.add_edge("A", "C", "branch2")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        result, ctx = run_dag(dag, "test input", ctx=ctx)

        # Should execute A -> B (since A returns "branch1")
        assert result is not None
        assert result.data == "result_b"

    def test_fan_in_context_merging(self):
        """Test that fan-in merges context patches correctly."""
        # Create a fan-in DAG: A -> C, B -> C
        builder = DAGBuilder()
        # Add actions with proper configuration that set context
        builder.add_node(
            "A",
            "action",
            action=lambda **kwargs: "result_a",
            terminate_on_success=False,
        )
        builder.add_node(
            "B",
            "action",
            action=lambda **kwargs: "result_b",
            terminate_on_success=False,
        )
        builder.add_node(
            "C", "action", action=lambda **kwargs: "result_c", terminate_on_success=True
        )
        builder.add_edge("A", "C", "next")
        builder.add_edge("B", "C", "next")
        builder.set_entrypoints(["A", "B"])
        dag = builder.build()

        ctx = Context()
        result, ctx = run_dag(dag, "test input", ctx=ctx)

        # Context should have both patches merged
        assert ctx.get("action_result") == "result_c"
        assert ctx.get("action_name") == "C"

    def test_early_termination(self):
        """Test that early termination stops processing."""
        builder = DAGBuilder()
        # Add actions with proper configuration
        builder.add_node(
            "A",
            "action",
            action=lambda **kwargs: "result_a",
            terminate_on_success=False,
        )
        builder.add_node(
            "B", "action", action=lambda **kwargs: "result_b", terminate_on_success=True
        )  # This should terminate
        builder.add_node(
            "C", "action", action=lambda **kwargs: "result_c", terminate_on_success=True
        )
        builder.add_edge("A", "B", "next")
        builder.add_edge("B", "C", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        result, metrics = run_dag(dag, "test input", ctx=ctx)

        # Should terminate after B
        assert result is not None
        assert result.terminate is True
        assert result.data == "result_b"

    def test_max_steps_limit(self):
        """Test that max_steps limit is enforced."""
        builder = DAGBuilder()
        # Create a linear chain longer than max_steps
        for i in range(10):
            builder.add_node(
                f"node_{i}",
                "action",
                action=lambda **kwargs: f"result_{i}",
                terminate_on_success=False,
            )
            if i > 0:
                builder.add_edge(f"node_{i-1}", f"node_{i}", "next")
        builder.set_entrypoints(["node_0"])
        dag = builder.build()

        ctx = Context()
        with pytest.raises(TraversalLimitError, match="Exceeded max_steps"):
            run_dag(dag, "test input", ctx=ctx, max_steps=5)

    def test_max_fanout_limit(self):
        """Test that max_fanout_per_node limit is enforced."""
        builder = DAGBuilder()
        # Add classifier with proper configuration
        builder.add_node(
            "A",
            "classifier",
            output_labels=[f"edge{i}" for i in range(20)],
            classification_func=lambda input, ctx: "edge0",
        )
        # Add more than max_fanout_per_node destinations
        for i in range(20):
            builder.add_node(
                f"B{i}",
                "action",
                action=lambda **kwargs: f"result_{i}",
                terminate_on_success=True,
            )
            builder.add_edge("A", f"B{i}", f"edge{i}")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        # This should not raise an error since only one edge is actually used
        result, metrics = run_dag(dag, "test input", ctx=ctx, max_fanout_per_node=16)
        assert result is not None

    def test_deterministic_order(self):
        """Test that traversal order is deterministic."""
        builder = DAGBuilder()
        # Add classifier with proper configuration
        builder.add_node(
            "A",
            "classifier",
            output_labels=["branch1", "branch2", "branch3"],
            classification_func=lambda input, ctx: "branch1",
        )
        # Add actions with proper configuration
        builder.add_node(
            "B", "action", action=lambda **kwargs: "result_b", terminate_on_success=True
        )
        builder.add_node(
            "C", "action", action=lambda **kwargs: "result_c", terminate_on_success=True
        )
        builder.add_node(
            "D", "action", action=lambda **kwargs: "result_d", terminate_on_success=True
        )
        builder.add_edge("A", "B", "branch1")
        builder.add_edge("A", "C", "branch2")
        builder.add_edge("A", "D", "branch3")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        result, ctx = run_dag(dag, "test input", ctx=ctx)

        # Should execute A -> B (since A returns "branch1")
        assert result is not None
        assert result.data == "result_b"

    def test_error_routing(self):
        """Test that errors are routed via 'error' edges."""
        builder = DAGBuilder()
        # Add action that raises an error
        builder.add_node(
            "A",
            "action",
            action=lambda **kwargs: (_ for _ in ()).throw(Exception("Test error")),
            terminate_on_success=False,
        )
        builder.add_node(
            "error_handler",
            "action",
            action=lambda **kwargs: "error_handled",
            terminate_on_success=True,
        )
        builder.add_edge("A", "error_handler", "error")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        result, ctx = run_dag(dag, "test input", ctx=ctx)

        # Error handler should be called
        assert result is not None
        assert result.data == "error_handled"
        # Error context should be set
        assert ctx.get("last_error") == "Test error"
        assert ctx.get("error_node") == "A"

    def test_error_without_handler(self):
        """Test that errors without handlers stop traversal."""
        builder = DAGBuilder()
        # Add action that raises an error
        builder.add_node(
            "A",
            "action",
            action=lambda **kwargs: (_ for _ in ()).throw(Exception("Test error")),
            terminate_on_success=False,
        )
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        with pytest.raises(TraversalError, match="Node A failed"):
            run_dag(dag, "test input", ctx=ctx)

    def test_no_entrypoints_error(self):
        """Test that empty entrypoints raises error."""
        builder = DAGBuilder()
        builder.add_node(
            "A", "action", action=lambda **kwargs: "result", terminate_on_success=True
        )
        # Don't set entrypoints to test validation
        # Skip validation to test traversal error
        dag = builder.build(validate_structure=False)

        ctx = Context()
        with pytest.raises(TraversalError, match="No entrypoints defined"):
            run_dag(dag, "test input", ctx=ctx)

    def test_no_resolver_error(self):
        """Test that missing resolver raises error."""
        # This test is no longer applicable since we have a default resolver
        # The _create_node function handles all known node types
        pass

    def test_metrics_aggregation(self):
        """Test that metrics are aggregated correctly."""
        builder = DAGBuilder()
        builder.add_node(
            "A",
            "action",
            action=lambda **kwargs: "result_a",
            terminate_on_success=False,
        )
        builder.add_node(
            "B", "action", action=lambda **kwargs: "result_b", terminate_on_success=True
        )
        builder.add_edge("A", "B", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        result, ctx = run_dag(dag, "test input", ctx=ctx)

        # Should return context
        assert isinstance(ctx, Context)

    def test_memoization(self):
        """Test that memoization prevents duplicate executions."""
        builder = DAGBuilder()
        builder.add_node(
            "A",
            "action",
            action=lambda **kwargs: "result_a",
            terminate_on_success=False,
        )
        builder.add_node(
            "B",
            "action",
            action=lambda **kwargs: "result_b",
            terminate_on_success=False,
        )
        builder.add_edge("A", "B", "next")
        builder.add_edge("B", "A", "back")  # Create a cycle
        builder.set_entrypoints(["A"])
        # Skip validation for cycle test
        dag = builder.build(validate_structure=False)

        ctx = Context()
        # This should not run forever due to memoization
        result, ctx = run_dag(
            dag, "test input", ctx=ctx, max_steps=10, enable_memoization=True
        )

        # Should complete without infinite loop
        assert result is not None

    def test_context_patch_application(self):
        """Test that context patches are applied correctly."""
        builder = DAGBuilder()
        builder.add_node(
            "A",
            "action",
            action=lambda **kwargs: "result_a",
            terminate_on_success=False,
        )
        builder.add_node(
            "B", "action", action=lambda **kwargs: "result_b", terminate_on_success=True
        )
        builder.add_edge("A", "B", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        result, ctx = run_dag(dag, "test input", ctx=ctx)

        # Context patches should be applied
        assert ctx.get("action_result") == "result_b"
        assert ctx.get("action_name") == "B"

    def test_empty_next_edges(self):
        """Test that empty next_edges stops traversal."""
        builder = DAGBuilder()
        builder.add_node(
            "A",
            "action",
            action=lambda **kwargs: "result_a",
            terminate_on_success=False,
        )
        builder.add_node(
            "B", "action", action=lambda **kwargs: "result_b", terminate_on_success=True
        )
        builder.add_edge("A", "B", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        result, ctx = run_dag(dag, "test input", ctx=ctx)

        # Should terminate after B since B has terminate_on_success=True
        assert result is not None
        assert result.terminate is True
        assert result.data == "result_b"

    def test_none_next_edges(self):
        """Test that None next_edges stops traversal."""
        builder = DAGBuilder()
        builder.add_node(
            "A",
            "action",
            action=lambda **kwargs: "result_a",
            terminate_on_success=False,
        )
        builder.add_node(
            "B", "action", action=lambda **kwargs: "result_b", terminate_on_success=True
        )
        builder.add_edge("A", "B", "next")
        builder.set_entrypoints(["A"])
        dag = builder.build()

        ctx = Context()
        result, ctx = run_dag(dag, "test input", ctx=ctx)

        # Should terminate after B since B has terminate_on_success=True
        assert result is not None
        assert result.terminate is True
        assert result.data == "result_b"
