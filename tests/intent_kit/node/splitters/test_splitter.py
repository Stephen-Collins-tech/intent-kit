"""
Tests for splitter node module.
"""

from unittest.mock import MagicMock, patch
from typing import Optional

from intent_kit.node.splitters.splitter import SplitterNode
from intent_kit.node.base import TreeNode
from intent_kit.node.enums import NodeType
from intent_kit.node.types import ExecutionResult, ExecutionError
from intent_kit.context import IntentContext


class MockChildNode(TreeNode):
    """Mock child node for testing."""

    def __init__(
        self, name: str, should_succeed: bool = True, description: str = "Mock child"
    ):
        super().__init__(name=name, description=description, children=[])
        self.should_succeed = should_succeed

    @property
    def node_type(self) -> NodeType:
        return NodeType.ACTION

    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        if self.should_succeed:
            return ExecutionResult(
                success=True,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=self.node_type,
                input=user_input,
                output=f"Processed: {user_input}",
                error=None,
                params={},
                children_results=[],
            )
        else:
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=self.node_type,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="MockError",
                    message="Mock child failed",
                    node_name=self.name,
                    node_path=self.get_path(),
                ),
                params={},
                children_results=[],
            )


class TestSplitterNode:
    """Test cases for SplitterNode."""

    def test_init_basic(self):
        """Test basic SplitterNode initialization."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1", "chunk2"]

        child = MockChildNode("child1")
        node = SplitterNode(
            name="test_splitter",
            splitter_function=mock_splitter,
            children=[child],
            description="Test splitter",
        )

        assert node.name == "test_splitter"
        assert node.splitter_function == mock_splitter
        assert node.children == [child]
        assert node.description == "Test splitter"
        assert node.llm_client is None
        assert node.llm_config is None

    def test_init_with_llm_client(self):
        """Test SplitterNode initialization with LLM client."""

        def mock_splitter(user_input, debug=False, llm_client=None):
            return ["chunk1", "chunk2"]

        mock_llm_client = MagicMock()
        child = MockChildNode("child1")

        node = SplitterNode(
            name="test_splitter",
            splitter_function=mock_splitter,
            children=[child],
            llm_client=mock_llm_client,
        )

        assert node.llm_client == mock_llm_client

    def test_init_with_parent(self):
        """Test SplitterNode initialization with parent."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1"]

        parent = MockChildNode("parent")
        child = MockChildNode("child1")

        node = SplitterNode(
            name="test_splitter",
            splitter_function=mock_splitter,
            children=[child],
            parent=parent,
        )

        assert node.parent == parent

    def test_node_type(self):
        """Test node_type property."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1"]

        child = MockChildNode("child1")
        node = SplitterNode(
            name="test_splitter", splitter_function=mock_splitter, children=[child]
        )

        assert node.node_type == NodeType.SPLITTER

    def test_execute_successful_splitting_and_handling(self):
        """Test successful execution with multiple chunks handled by children."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1", "chunk2", "chunk3"]

        child1 = MockChildNode("child1", should_succeed=True)
        child2 = MockChildNode("child2", should_succeed=True)

        node = SplitterNode(
            name="test_splitter",
            splitter_function=mock_splitter,
            children=[child1, child2],
        )

        context = IntentContext()
        result = node.execute("test input", context)

        assert result.success is True
        assert result.node_name == "test_splitter"
        assert result.node_type == NodeType.SPLITTER
        assert result.input == "test input"
        assert result.output is not None
        assert len(result.output) == 3  # All chunks processed
        assert result.error is None
        assert result.params is not None
        assert result.params["intent_chunks"] == ["chunk1", "chunk2", "chunk3"]
        assert result.params["chunks_processed"] == 3
        assert result.params["chunks_handled"] == 3
        assert len(result.children_results) == 3

    def test_execute_with_dict_chunks(self):
        """Test execution with dictionary chunks containing chunk_text."""

        def mock_splitter(user_input, debug=False):
            return [
                {"chunk_text": "chunk1", "metadata": "meta1"},
                {"chunk_text": "chunk2", "metadata": "meta2"},
            ]

        child = MockChildNode("child1", should_succeed=True)

        node = SplitterNode(
            name="test_splitter", splitter_function=mock_splitter, children=[child]
        )

        result = node.execute("test input")

        assert result.success is True
        assert len(result.children_results) == 2
        assert result.children_results[0].input == "chunk1"
        assert result.children_results[1].input == "chunk2"

    def test_execute_no_intent_chunks_found(self):
        """Test execution when splitter returns no chunks."""

        def mock_splitter(user_input, debug=False):
            return []

        child = MockChildNode("child1")

        node = SplitterNode(
            name="test_splitter", splitter_function=mock_splitter, children=[child]
        )

        with patch.object(node, "logger") as mock_logger:
            result = node.execute("test input")

            assert result.success is False
            assert result.output is None
            assert result.error is not None
            assert getattr(result.error, "error_type", None) == "NoIntentChunksFound"
            assert "No intent chunks found after splitting" in getattr(
                result.error, "message", ""
            )
            assert result.params is not None
            assert result.params["intent_chunks"] == []
            assert len(result.children_results) == 0
            mock_logger.warning.assert_called_once()

    def test_execute_no_intent_chunks_found_none_returned(self):
        """Test execution when splitter returns None."""

        def mock_splitter(user_input, debug=False):
            return None

        child = MockChildNode("child1")

        node = SplitterNode(
            name="test_splitter", splitter_function=mock_splitter, children=[child]
        )

        with patch.object(node, "logger"):
            result = node.execute("test input")

            assert result.success is False
            assert result.error is not None
            assert getattr(result.error, "error_type", None) == "NoIntentChunksFound"

    def test_execute_partial_chunk_handling(self):
        """Test execution where some chunks are handled and others are not."""

        def mock_splitter(user_input, debug=False):
            return ["handled_chunk", "unhandled_chunk"]

        # Child that only handles chunks starting with "handled"
        child = MockChildNode("child1", should_succeed=True)

        # Mock the child to fail on unhandled_chunk
        original_execute = child.execute

        def selective_execute(user_input, context=None):
            if user_input.startswith("handled"):
                return original_execute(user_input, context)
            else:
                raise Exception("Cannot handle this chunk")

        child.execute = selective_execute

        node = SplitterNode(
            name="test_splitter", splitter_function=mock_splitter, children=[child]
        )

        with patch.object(node, "logger"):
            result = node.execute("test input")

            assert result.success is True  # At least one chunk was handled
            assert len(result.children_results) == 2
            assert result.children_results[0].success is True  # handled_chunk
            # unhandled_chunk
            assert result.children_results[1].success is False
            assert result.children_results[1].error is not None
            assert (
                getattr(result.children_results[1].error, "error_type", None)
                == "UnhandledChunk"
            )
            assert result.params is not None
            assert result.params["chunks_handled"] == 1
            assert result.params["chunks_processed"] == 2

    def test_execute_all_chunks_unhandled(self):
        """Test execution where no chunks can be handled by any child."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1", "chunk2"]

        # Child that always fails
        child = MockChildNode("child1", should_succeed=False)

        # Mock the child to raise exceptions
        def failing_execute(user_input, context=None):
            raise Exception("Cannot handle any chunk")

        child.execute = failing_execute

        node = SplitterNode(
            name="test_splitter", splitter_function=mock_splitter, children=[child]
        )

        with patch.object(node, "logger"):
            result = node.execute("test input")

            assert result.success is False  # No chunks were handled
            assert len(result.children_results) == 2
            assert all(
                not child_result.success for child_result in result.children_results
            )
            assert result.params is not None
            assert result.params["chunks_handled"] == 0
            assert result.params["chunks_processed"] == 2

    def test_execute_with_llm_client_parameter(self):
        """Test execution with splitter function that accepts llm_client parameter."""

        def mock_splitter_with_llm(user_input, debug=False, llm_client=None):
            assert llm_client is not None
            return ["chunk1"]

        mock_llm_client = MagicMock()
        child = MockChildNode("child1")

        node = SplitterNode(
            name="test_splitter",
            splitter_function=mock_splitter_with_llm,
            children=[child],
            llm_client=mock_llm_client,
        )

        result = node.execute("test input")
        assert result.success is True

    def test_execute_without_llm_client_parameter(self):
        """Test execution with splitter function that doesn't accept llm_client parameter."""

        def mock_splitter_no_llm(user_input, debug=False):
            return ["chunk1"]

        mock_llm_client = MagicMock()
        child = MockChildNode("child1")

        node = SplitterNode(
            name="test_splitter",
            splitter_function=mock_splitter_no_llm,
            children=[child],
            llm_client=mock_llm_client,
        )

        result = node.execute("test input")
        assert result.success is True

    def test_execute_multiple_children_first_succeeds(self):
        """Test execution where first child handles chunk successfully."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1"]

        child1 = MockChildNode("child1", should_succeed=True)
        child2 = MockChildNode("child2", should_succeed=True)

        node = SplitterNode(
            name="test_splitter",
            splitter_function=mock_splitter,
            children=[child1, child2],
        )

        result = node.execute("test input")

        assert result.success is True
        assert len(result.children_results) == 1
        assert result.children_results[0].node_name == "child1"

    def test_execute_multiple_children_second_succeeds(self):
        """Test execution where second child handles chunk after first fails."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1"]

        # First child fails, second succeeds
        child1 = MockChildNode("child1", should_succeed=False)
        child2 = MockChildNode("child2", should_succeed=True)

        # Mock first child to raise exception
        def failing_execute(user_input, context=None):
            raise Exception("First child fails")

        child1.execute = failing_execute

        node = SplitterNode(
            name="test_splitter",
            splitter_function=mock_splitter,
            children=[child1, child2],
        )

        with patch.object(node, "logger"):
            result = node.execute("test input")

            assert result.success is True
            assert len(result.children_results) == 1
            assert result.children_results[0].node_name == "child2"

    def test_execute_with_context(self):
        """Test execution with IntentContext."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1"]

        child = MockChildNode("child1")
        context = IntentContext()

        node = SplitterNode(
            name="test_splitter", splitter_function=mock_splitter, children=[child]
        )

        result = node.execute("test input", context)
        assert result.success is True

    def test_execute_without_context(self):
        """Test execution without IntentContext."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1"]

        child = MockChildNode("child1")

        node = SplitterNode(
            name="test_splitter", splitter_function=mock_splitter, children=[child]
        )

        result = node.execute("test input")
        assert result.success is True

    def test_unhandled_chunk_error_details(self):
        """Test that unhandled chunk errors contain proper details."""

        def mock_splitter(user_input, debug=False):
            return ["unhandled_chunk_with_long_text_that_should_be_truncated"]

        child = MockChildNode("child1")

        def failing_execute(user_input, context=None):
            raise Exception("Cannot handle")

        child.execute = failing_execute

        node = SplitterNode(
            name="test_splitter", splitter_function=mock_splitter, children=[child]
        )

        with patch.object(node, "logger"):
            result = node.execute("test input")

            assert result.success is False
            unhandled_result = result.children_results[0]
            assert unhandled_result.node_type == NodeType.UNHANDLED_CHUNK
            assert unhandled_result.node_name == "unhandled_chunk_unhandled_chunk_with"
            assert unhandled_result.error is not None
            assert "No child node could handle chunk" in getattr(
                unhandled_result.error, "message", ""
            )
            assert unhandled_result.params is not None
            assert (
                unhandled_result.params["chunk"]
                == "unhandled_chunk_with_long_text_that_should_be_truncated"
            )

    def test_logger_debug_messages(self):
        """Test that appropriate debug messages are logged."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1", "chunk2"]

        child = MockChildNode("child1")

        node = SplitterNode(
            name="test_splitter", splitter_function=mock_splitter, children=[child]
        )

        with patch.object(node, "logger") as mock_logger:
            node.execute("test input")

            mock_logger.debug.assert_called_with(
                "Splitter 'test_splitter' found 2 chunks: ['chunk1', 'chunk2']"
            )

    def test_splitter_function_signature_inspection(self):
        """Test that function signature inspection works correctly."""
        import inspect

        def splitter_with_llm(user_input, debug=False, llm_client=None):
            return ["chunk1"]

        def splitter_without_llm(user_input, debug=False):
            return ["chunk1"]

        # Test with llm_client parameter
        params_with_llm = inspect.signature(splitter_with_llm).parameters
        assert "llm_client" in params_with_llm

        # Test without llm_client parameter
        params_without_llm = inspect.signature(splitter_without_llm).parameters
        assert "llm_client" not in params_without_llm

    def test_get_path_inheritance(self):
        """Test that SplitterNode properly inherits path functionality."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1"]

        parent = MockChildNode("parent")
        child = MockChildNode("child1")

        node = SplitterNode(
            name="test_splitter",
            splitter_function=mock_splitter,
            children=[child],
            parent=parent,
        )

        assert node.get_path() == ["parent", "test_splitter"]
        assert node.get_path_string() == "parent.test_splitter"

    def test_node_properties_inheritance(self):
        """Test that SplitterNode inherits all expected properties from TreeNode."""

        def mock_splitter(user_input, debug=False):
            return ["chunk1"]

        child = MockChildNode("child1")
        node = SplitterNode(
            name="test_splitter",
            splitter_function=mock_splitter,
            children=[child],
            description="Test description",
        )

        # Test TreeNode properties
        assert hasattr(node, "name")
        assert hasattr(node, "description")
        assert hasattr(node, "children")
        assert hasattr(node, "parent")
        assert hasattr(node, "logger")

        # Test Node properties
        assert hasattr(node, "node_id")
        assert hasattr(node, "has_name")
        assert hasattr(node, "get_path")
        assert hasattr(node, "get_path_string")
        assert hasattr(node, "get_uuid_path")
        assert hasattr(node, "get_uuid_path_string")

        # Test specific SplitterNode properties
        assert hasattr(node, "splitter_function")
        assert hasattr(node, "llm_client")
        assert hasattr(node, "llm_config")
        assert hasattr(node, "node_type")
