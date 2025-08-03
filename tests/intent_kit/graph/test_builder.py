"""
Tests for intent_kit.graph.builder module.
"""

from intent_kit.graph.builder import IntentGraphBuilder
from intent_kit.nodes import TreeNode
from intent_kit.nodes.enums import NodeType


class MockTreeNode(TreeNode):
    """Mock TreeNode for testing."""

    def __init__(
        self, name: str, description: str = "", node_type: NodeType = NodeType.ACTION
    ):
        super().__init__(name=name, description=description)
        self._node_type = node_type

    @property
    def node_type(self) -> NodeType:
        return self._node_type

    def execute(self, user_input: str, context=None):
        """Mock execution method."""
        from intent_kit.nodes import ExecutionResult

        return ExecutionResult(
            success=True,
            node_name=self.name,
            node_path=[self.name],
            node_type=self.node_type,
            input=user_input,
            output=f"Mock result for {user_input}",
            error=None,
            params={},
            children_results=[],
        )


class TestIntentGraphBuilder:
    """Test IntentGraphBuilder class."""

    def test_init(self):
        """Test IntentGraphBuilder initialization."""
        builder = IntentGraphBuilder()

        assert builder._root_nodes == []
        assert builder._debug_context_enabled is False
        assert builder._context_trace_enabled is False
        assert builder._json_graph is None
        assert builder._function_registry is None
        assert builder._llm_config is None

    def test_with_debug_context_enabled(self):
        """Test with_debug_context method with enabled=True."""
        builder = IntentGraphBuilder()

        result = builder.with_debug_context(True)

        assert result is builder
        assert builder._debug_context_enabled is True

    def test_with_debug_context_disabled(self):
        """Test with_debug_context method with enabled=False."""
        builder = IntentGraphBuilder()
        builder._debug_context_enabled = True  # Set initial state

        result = builder.with_debug_context(False)

        assert result is builder
        assert builder._debug_context_enabled is False

    def test_with_debug_context_default(self):
        """Test with_debug_context method with default parameter."""
        builder = IntentGraphBuilder()

        result = builder.with_debug_context()

        assert result is builder
        assert builder._debug_context_enabled is True

    def test_with_context_trace_enabled(self):
        """Test with_context_trace method with enabled=True."""
        builder = IntentGraphBuilder()

        result = builder.with_context_trace(True)

        assert result is builder
        assert builder._context_trace_enabled is True

    def test_with_context_trace_disabled(self):
        """Test with_context_trace method with enabled=False."""
        builder = IntentGraphBuilder()
        builder._context_trace_enabled = True  # Set initial state

        result = builder.with_context_trace(False)

        assert result is builder
        assert builder._context_trace_enabled is False

    def test_with_context_trace_default(self):
        """Test with_context_trace method with default parameter."""
        builder = IntentGraphBuilder()

        result = builder.with_context_trace()

        assert result is builder
        assert builder._context_trace_enabled is True

    def test_method_chaining(self):
        """Test that debug context methods support method chaining."""
        builder = IntentGraphBuilder()

        result = builder.with_debug_context(True).with_context_trace(False)

        assert result is builder
        assert builder._debug_context_enabled is True
        assert builder._context_trace_enabled is False

    def test_debug_context_internal_method(self):
        """Test the internal _debug_context method."""
        builder = IntentGraphBuilder()

        result = builder._debug_context(True)

        assert result is builder
        assert builder._debug_context_enabled is True

    def test_context_trace_internal_method(self):
        """Test the internal _context_trace method."""
        builder = IntentGraphBuilder()

        result = builder._context_trace(True)

        assert result is builder
        assert builder._context_trace_enabled is True

    def test_multiple_calls_same_method(self):
        """Test multiple calls to the same debug method."""
        builder = IntentGraphBuilder()

        # First call
        builder.with_debug_context(True)
        assert builder._debug_context_enabled is True

        # Second call
        builder.with_debug_context(False)
        assert builder._debug_context_enabled is False

        # Third call
        builder.with_debug_context(True)
        assert builder._debug_context_enabled is True

    def test_debug_context_with_other_builder_methods(self):
        """Test debug context methods work with other builder methods."""
        builder = IntentGraphBuilder()
        mock_node = MockTreeNode("test_node", "Test node")

        result = (
            builder.root(mock_node).with_debug_context(True).with_context_trace(True)
        )

        assert result is builder
        assert builder._root_nodes == [mock_node]
        assert builder._debug_context_enabled is True
        assert builder._context_trace_enabled is True
