"""
Tests for intent_kit.graph.intent_graph module.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Optional

from intent_kit.graph.intent_graph import IntentGraph
from intent_kit.nodes import TreeNode
from intent_kit.nodes.enums import NodeType
from intent_kit.context import IntentContext
from intent_kit.nodes import ExecutionResult
from intent_kit.graph.validation import GraphValidationError


class MockTreeNode(TreeNode):
    """Mock TreeNode for testing."""

    def __init__(
        self, name: str, description: str = "", node_type: NodeType = NodeType.ACTION
    ):
        super().__init__(name=name, description=description)
        self._node_type = node_type
        self.executed = False
        self.execution_result: Optional[ExecutionResult] = None

    @property
    def node_type(self) -> NodeType:
        return self._node_type

    def execute(self, user_input: str, context=None) -> ExecutionResult:
        """Mock execution."""
        self.executed = True
        self.execution_result = ExecutionResult(
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
        return self.execution_result


class MockClassifierNode(MockTreeNode):
    """Mock ClassifierNode for testing."""

    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description, NodeType.CLASSIFIER)

    def classify(
        self, user_input: str, children: List[TreeNode], context=None
    ) -> Optional[TreeNode]:
        """Mock classification."""
        if children:
            return children[0]  # Always return first child
        return None

    def execute(self, user_input: str, context=None):
        # Classifier nodes should not execute in this test
        return None


class TestIntentGraphInitialization:
    """Test IntentGraph initialization."""

    def test_init_with_no_args(self):
        """Test initialization with no arguments."""
        graph = IntentGraph()

        assert graph.root_nodes == []
        assert graph.llm_config is None

    def test_init_with_root_nodes(self):
        """Test initialization with root nodes."""
        root_node = MockClassifierNode("root", "Root node")
        graph = IntentGraph(root_nodes=[root_node])

        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0] == root_node

    def test_init_with_all_options(self):
        """Test initialization with all options."""
        root_node = MockClassifierNode("root", "Root node")

        graph = IntentGraph(
            root_nodes=[root_node],
            llm_config={"provider": "openai"},
        )

        assert len(graph.root_nodes) == 1
        assert graph.llm_config == {"provider": "openai"}


class TestIntentGraphNodeManagement:
    """Test IntentGraph node management methods."""

    def test_add_root_node_success(self):
        """Test successfully adding a root node."""
        graph = IntentGraph()
        root_node = MockClassifierNode("root", "Root node")

        graph.add_root_node(root_node)

        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0] == root_node

    def test_add_root_node_invalid_type(self):
        """Test adding a non-TreeNode as root node."""
        graph = IntentGraph()

        with pytest.raises(ValueError, match="Root node must be a TreeNode"):
            graph.add_root_node("not a node")  # type: ignore[arg-type]

    def test_add_root_node_with_validation_failure(self):
        """Test adding root node when validation fails."""
        graph = IntentGraph()
        root_node = MockClassifierNode("root", "Root node")

        # Mock validation to fail
        with patch(
            "intent_kit.graph.intent_graph.validate_graph_structure"
        ) as mock_validate:
            mock_validate.side_effect = GraphValidationError(
                "Validation failed")

            with pytest.raises(GraphValidationError):
                graph.add_root_node(root_node)

            # Node should be removed after validation failure
            assert len(graph.root_nodes) == 0

    def test_remove_root_node_success(self):
        """Test successfully removing a root node."""
        graph = IntentGraph()
        root_node = MockClassifierNode("root", "Root node")
        graph.add_root_node(root_node)

        graph.remove_root_node(root_node)

        assert len(graph.root_nodes) == 0

    def test_remove_root_node_not_found(self):
        """Test removing a root node that doesn't exist."""
        graph = IntentGraph()
        root_node = MockClassifierNode("root", "Root node")

        # Should not raise an exception, just log a warning
        graph.remove_root_node(root_node)

        assert len(graph.root_nodes) == 0

    def test_list_root_nodes(self):
        """Test listing root node names."""
        graph = IntentGraph()
        root_node1 = MockClassifierNode("root1", "Root node 1")
        root_node2 = MockClassifierNode("root2", "Root node 2")

        graph.add_root_node(root_node1)
        graph.add_root_node(root_node2)

        node_names = graph.list_root_nodes()

        assert node_names == ["root1", "root2"]


class TestIntentGraphValidation:
    """Test IntentGraph validation methods."""

    def test_validate_graph_success(self):
        """Test successful graph validation."""
        graph = IntentGraph()
        root_node = MockClassifierNode("root", "Root node")
        graph.add_root_node(root_node)

        # Mock validation functions to succeed
        with (
            patch(
                "intent_kit.graph.intent_graph.validate_node_types"
            ) as mock_validate_types,
            patch(
                "intent_kit.graph.intent_graph.validate_graph_structure"
            ) as mock_validate_structure,
        ):

            mock_validate_structure.return_value = {
                "total_nodes": 1,
                "routing_valid": True,
            }

            result = graph.validate_graph()

            mock_validate_types.assert_called_once()
            mock_validate_structure.assert_called_once()
            assert result["total_nodes"] == 1
            assert result["routing_valid"] is True

    def test_validate_graph_with_validation_failure(self):
        """Test graph validation when validation fails."""
        graph = IntentGraph()
        root_node = MockClassifierNode("root", "Root node")
        graph.add_root_node(root_node)

        # Mock validation to fail
        with patch(
            "intent_kit.graph.intent_graph.validate_node_types"
        ) as mock_validate_types:
            mock_validate_types.side_effect = GraphValidationError(
                "Node type validation failed"
            )

            with pytest.raises(GraphValidationError):
                graph.validate_graph()


class TestIntentGraphRouting:
    """Test IntentGraph routing functionality."""

    def test_route_chunk_to_root_node_success(self):
        """Test successfully routing a chunk to a root node."""
        graph = IntentGraph()
        root_node = MockClassifierNode("root", "Root node")
        graph.add_root_node(root_node)

        result = graph._route_chunk_to_root_node("test input")

        assert result == root_node

    def test_route_chunk_to_root_node_no_match(self):
        """Test routing a chunk when no root node matches."""
        graph = IntentGraph()
        root_node = MockClassifierNode("root", "Root node")
        graph.add_root_node(root_node)

        # Mock the classification to return None
        with patch(
            "intent_kit.graph.intent_graph.classify_intent_chunk"
        ) as mock_classify:
            mock_classify.return_value = {
                "classification": "Invalid",
                "action": "reject",
                "metadata": {"confidence": 0.0, "reason": "No match"},
            }

            result = graph._route_chunk_to_root_node("test input")

            assert result is None

    def test_route_chunk_to_root_node_with_llm_config(self):
        """Test routing with LLM configuration."""
        graph = IntentGraph(llm_config={"provider": "openai"})
        root_node = MockClassifierNode("root", "Root node")
        graph.add_root_node(root_node)

        with patch(
            "intent_kit.graph.intent_graph.classify_intent_chunk"
        ) as mock_classify:
            mock_classify.return_value = {
                "classification": "Atomic",
                "action": "handle",
                "metadata": {"confidence": 0.9, "reason": "Match found"},
            }

            graph._route_chunk_to_root_node("test input")

            mock_classify.assert_called_once()
            call_args = mock_classify.call_args[0]
            assert call_args[1] == {"provider": "openai"}  # llm_config


class TestIntentGraphExecution:
    """Test IntentGraph execution functionality."""

    def test_route_simple_execution(self):
        """Test simple routing and execution."""
        graph = IntentGraph()
        root_node = MockClassifierNode("root", "Root node")
        graph.add_root_node(root_node)

        result = graph.route("test input")

        assert result.success is True
        assert result.output is not None
        assert "Mock result for test input" in str(result.output)
        assert result.node_name == "root"

    def test_route_with_context(self):
        """Test routing with context."""
        graph = IntentGraph()
        root_node = MockClassifierNode("root", "Root node")
        graph.add_root_node(root_node)
        context = IntentContext()
        context.set("key", "value")

        result = graph.route("test input", context=context)

        assert result.success is True

    def test_route_with_debug_options(self):
        """Test routing with debug options."""
        graph = IntentGraph(debug_context=True, context_trace=True)
        root_node = MockClassifierNode("root", "Root node")
        graph.add_root_node(root_node)

        result = graph.route("test input", debug=True)

        assert result.success is True

    def test_route_with_no_root_nodes(self):
        """Test routing when no root nodes are available."""
        graph = IntentGraph()

        result = graph.route("test input")

        assert result.success is False
        assert result.error is not None
        assert "No root nodes available" in result.error.message

    def test_route_with_execution_error(self):
        """Test routing when node execution fails."""
        graph = IntentGraph()

        # Create a mock classifier node that raises an exception
        error_node = MockClassifierNode("error", "Error node")
        error_node.execute = Mock(side_effect=Exception("Execution failed"))

        graph.add_root_node(error_node)

        result = graph.route("test input")

        assert result.success is False
        assert result.error is not None
        assert "Execution failed" in result.error.message


class TestIntentGraphContextTracking:
    """Test IntentGraph context tracking functionality."""

    def test_capture_context_state(self):
        """Test capturing context state."""
        graph = IntentGraph()
        context = IntentContext()
        context.set("key1", "value1")
        context.set("key2", "value2")

        state = graph._capture_context_state(context, "test_label")

        assert state["key1"] == "value1"
        assert state["key2"] == "value2"
        assert "timestamp" in state

    def test_log_context_changes(self):
        """Test logging context changes."""
        graph = IntentGraph(debug_context=True)

        state_before = {"key1": "old_value", "key2": "unchanged"}
        state_after = {"key1": "new_value", "key2": "unchanged"}

        # Should not raise an exception
        graph._log_context_changes(
            state_before, state_after, "test_node", debug=True, context_trace=False
        )

    def test_log_detailed_context_trace(self):
        """Test detailed context tracing."""
        graph = IntentGraph()

        state_before = {"key1": "old_value"}
        state_after = {"key1": "new_value", "key2": "added"}

        # Should not raise an exception
        graph._log_detailed_context_trace(
            state_before, state_after, "test_node")


class TestIntentGraphIntegration:
    """Integration tests for IntentGraph."""

    def test_complete_workflow(self):
        """Test a complete workflow with multiple components."""
        # Create handler nodes
        handler1 = MockClassifierNode("handler1", "Handler 1")
        handler2 = MockClassifierNode("handler2", "Handler 2")

        # Create graph with multiple root nodes
        graph = IntentGraph()
        graph.add_root_node(handler1)
        graph.add_root_node(handler2)

        # Route input that should match handler1
        result = graph.route("handle handler1 task")

        assert result.success is True
        assert handler1.executed is True  # First handler should be executed

    def test_graph_with_multiple_root_nodes(self):
        """Test graph with multiple root nodes."""
        graph = IntentGraph()

        root1 = MockClassifierNode("root1", "Root 1")
        root2 = MockClassifierNode("root2", "Root 2")

        graph.add_root_node(root1)
        graph.add_root_node(root2)

        assert len(graph.root_nodes) == 2
        assert graph.list_root_nodes() == ["root1", "root2"]

    def test_graph_validation_integration(self):
        """Test graph validation integration."""
        graph = IntentGraph()

        # Add a valid node
        root_node = MockClassifierNode("root", "Root node")
        graph.add_root_node(root_node)

        # Validation should pass
        stats = graph.validate_graph()

        assert "total_nodes" in stats
        assert stats["total_nodes"] >= 1
