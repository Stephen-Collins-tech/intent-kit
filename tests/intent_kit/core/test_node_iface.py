"""Tests for node execution interface."""

from intent_kit.core import ExecutionResult


class MockContext:
    """Mock context for testing."""

    pass


class MockNode:
    """Mock node implementing NodeProtocol protocol."""

    def __init__(self, result: ExecutionResult):
        self.result = result

    def execute(self, user_input: str, ctx) -> ExecutionResult:
        return self.result


class TestExecutionResult:
    """Test ExecutionResult functionality."""

    def test_default_values(self):
        """Test ExecutionResult with default values."""
        result = ExecutionResult()

        assert result.data is None
        assert result.next_edges is None
        assert result.terminate is False
        assert result.metrics == {}
        assert result.context_patch == {}

    def test_with_all_values(self):
        """Test ExecutionResult with all values specified."""
        result = ExecutionResult(
            data="test",
            next_edges=["a", "b"],
            terminate=True,
            metrics={"tokens": 100},
            context_patch={"key": "value"},
        )

        assert result.data == "test"
        assert result.next_edges == ["a", "b"]
        assert result.terminate is True
        assert result.metrics == {"tokens": 100}
        assert result.context_patch == {"key": "value"}

    def test_merge_metrics_numeric(self):
        """Test merging numeric metrics."""
        result = ExecutionResult(metrics={"tokens": 50, "cost": 0.01})
        result.merge_metrics({"tokens": 25, "cost": 0.005})

        assert result.metrics["tokens"] == 75
        assert result.metrics["cost"] == 0.015

    def test_merge_metrics_non_numeric(self):
        """Test merging non-numeric metrics."""
        result = ExecutionResult(metrics={"status": "ok", "count": 5})
        result.merge_metrics({"status": "error", "count": 3})

        # Non-numeric should be replaced
        assert result.metrics["status"] == "error"
        # Numeric should be added
        assert result.metrics["count"] == 8

    def test_merge_metrics_new_keys(self):
        """Test merging metrics with new keys."""
        result = ExecutionResult(metrics={"existing": 10})
        result.merge_metrics({"new_key": "value", "new_number": 5})

        assert result.metrics["existing"] == 10
        assert result.metrics["new_key"] == "value"
        assert result.metrics["new_number"] == 5


class TestINode:
    """Test NodeProtocol protocol implementation."""

    def test_mock_node_implements_protocol(self):
        """Test that MockNode correctly implements NodeProtocol protocol."""
        result = ExecutionResult(data="test")
        node = MockNode(result)

        # This should work without type errors
        ctx = MockContext()
        output = node.execute("input", ctx)

        assert output == result
        assert output.data == "test"

    def test_node_with_terminate(self):
        """Test node that terminates execution."""
        result = ExecutionResult(terminate=True, data="final")
        node = MockNode(result)

        ctx = MockContext()
        output = node.execute("input", ctx)

        assert output.terminate is True
        assert output.data == "final"

    def test_node_with_next_edges(self):
        """Test node that specifies next edges."""
        result = ExecutionResult(next_edges=["success", "fallback"])
        node = MockNode(result)

        ctx = MockContext()
        output = node.execute("input", ctx)

        assert output.next_edges == ["success", "fallback"]
