"""
Tests for context debug module.
"""

import pytest
from unittest.mock import patch, MagicMock
from intent_kit.context.debug import (
    get_context_dependencies,
    validate_context_flow,
    trace_context_execution,
    _collect_all_nodes,
    _analyze_node_dependencies,
    _validate_node_dependencies,
    _capture_full_context_state,
    _format_context_history,
    _format_console_trace,
)
from intent_kit.context import IntentContext
from intent_kit.context.dependencies import ContextDependencies


class TestContextDebug:
    """Test cases for context debug module."""

    def test_get_context_dependencies(self):
        """Test getting context dependencies for a graph."""
        # Mock graph with nodes
        mock_node1 = MagicMock()
        mock_node1.name = "node1"
        mock_node1.context_inputs = {"input1", "input2"}
        mock_node1.context_outputs = {"output1"}

        mock_node2 = MagicMock()
        mock_node2.name = "node2"
        mock_node2.context_inputs = {"input3"}
        mock_node2.context_outputs = {"output2"}

        mock_graph = MagicMock()
        mock_graph.root_nodes = [mock_node1, mock_node2]

        dependencies = get_context_dependencies(mock_graph)

        assert "node1" in dependencies
        assert "node2" in dependencies
        assert dependencies["node1"].inputs == {"input1", "input2"}
        assert dependencies["node1"].outputs == {"output1"}

    def test_validate_context_flow_success(self):
        """Test successful context flow validation."""
        # Mock dependencies
        mock_deps = ContextDependencies(
            inputs={"input1", "input2"},
            outputs={"output1"},
            description="Test dependencies",
        )

        # Mock graph
        mock_graph = MagicMock()
        mock_graph.root_nodes = []

        # Mock context with required fields
        mock_context = MagicMock()
        mock_context.keys.return_value = {"input1", "input2", "output1"}

        with patch(
            "intent_kit.context.debug.get_context_dependencies"
        ) as mock_get_deps:
            mock_get_deps.return_value = {"test_node": mock_deps}

            result = validate_context_flow(mock_graph, mock_context)

        assert result["valid"] is True
        assert result["total_nodes"] == 1
        assert result["nodes_with_dependencies"] == 1

    def test_validate_context_flow_missing_dependencies(self):
        """Test context flow validation with missing dependencies."""
        # Mock dependencies
        mock_deps = ContextDependencies(
            inputs={"input1", "input2", "missing_input"},
            outputs={"output1"},
            description="Test dependencies",
        )

        # Mock graph
        mock_graph = MagicMock()
        mock_graph.root_nodes = []

        # Mock context with missing fields
        mock_context = MagicMock()
        mock_context.keys.return_value = {"input1", "output1"}

        with patch(
            "intent_kit.context.debug.get_context_dependencies"
        ) as mock_get_deps:
            mock_get_deps.return_value = {"test_node": mock_deps}

            result = validate_context_flow(mock_graph, mock_context)

        assert result["valid"] is False
        assert "test_node" in result["missing_dependencies"]
        assert "missing_input" in result["missing_dependencies"]["test_node"]

    def test_trace_context_execution_json(self):
        """Test context execution tracing in JSON format."""
        # Mock graph
        mock_graph = MagicMock()
        mock_graph.root_nodes = []

        # Mock context
        mock_context = MagicMock()
        mock_context.session_id = "test_session"
        mock_context.keys.return_value = {"field1", "field2"}
        mock_context.error_count.return_value = 0
        mock_context.get_history.return_value = []

        result = trace_context_execution(
            mock_graph, "test input", mock_context, output_format="json"
        )

        assert isinstance(result, str)
        assert "test input" in result
        assert "test_session" in result

    def test_trace_context_execution_console(self):
        """Test context execution tracing in console format."""
        # Mock graph
        mock_graph = MagicMock()
        mock_graph.root_nodes = []

        # Mock context
        mock_context = MagicMock()
        mock_context.session_id = "test_session"
        mock_context.keys.return_value = {"field1", "field2"}
        mock_context.error_count.return_value = 0
        mock_context.get_history.return_value = []

        result = trace_context_execution(
            mock_graph, "test input", mock_context, output_format="console"
        )

        assert isinstance(result, str)
        assert "test input" in result
        assert "test_session" in result

    def test_collect_all_nodes(self):
        """Test collecting all nodes from a graph."""
        # Create mock nodes with children
        mock_child1 = MagicMock()
        mock_child1.node_id = "child1"
        mock_child1.children = []

        mock_child2 = MagicMock()
        mock_child2.node_id = "child2"
        mock_child2.children = []

        mock_root = MagicMock()
        mock_root.node_id = "root"
        mock_root.children = [mock_child1, mock_child2]

        nodes = _collect_all_nodes([mock_root])

        assert len(nodes) == 3
        node_ids = [node.node_id for node in nodes]
        assert "root" in node_ids
        assert "child1" in node_ids
        assert "child2" in node_ids

    def test_collect_all_nodes_with_cycles(self):
        """Test collecting nodes with cycles (should handle gracefully)."""
        # Create mock nodes with cycle
        mock_node1 = MagicMock()
        mock_node1.node_id = "node1"
        mock_node1.children = []

        mock_node2 = MagicMock()
        mock_node2.node_id = "node2"
        mock_node2.children = [mock_node1]  # Creates cycle

        mock_node1.children = [mock_node2]  # Completes cycle

        nodes = _collect_all_nodes([mock_node1])

        # Should handle cycle gracefully
        assert len(nodes) == 2
        node_ids = [node.node_id for node in nodes]
        assert "node1" in node_ids
        assert "node2" in node_ids

    def test_analyze_node_dependencies_with_explicit_deps(self):
        """Test analyzing node dependencies with explicit dependencies."""
        mock_node = MagicMock()
        mock_node.context_inputs = {"input1", "input2"}
        mock_node.context_outputs = {"output1"}
        mock_node.name = "test_node"

        deps = _analyze_node_dependencies(mock_node)

        assert deps is not None
        assert deps.inputs == {"input1", "input2"}
        assert deps.outputs == {"output1"}
        assert "test_node" in deps.description

    def test_analyze_node_dependencies_with_handler(self):
        """Test analyzing node dependencies with handler function."""
        mock_handler = MagicMock()
        mock_node = MagicMock()
        mock_node.handler = mock_handler
        mock_node.name = "test_node"

        with patch(
            "intent_kit.context.debug.analyze_action_dependencies"
        ) as mock_analyze:
            mock_analyze.return_value = ContextDependencies(
                inputs={"input1"}, outputs={"output1"}, description="Handler deps"
            )

            deps = _analyze_node_dependencies(mock_node)

        assert deps is not None
        mock_analyze.assert_called_once_with(mock_handler)

    def test_analyze_node_dependencies_with_classifier(self):
        """Test analyzing node dependencies with classifier function."""
        mock_classifier = MagicMock()
        mock_node = MagicMock()
        mock_node.classifier = mock_classifier
        mock_node.name = "test_classifier"

        deps = _analyze_node_dependencies(mock_node)

        assert deps is not None
        assert deps.inputs == set()
        assert deps.outputs == set()
        assert "test_classifier" in deps.description

    def test_analyze_node_dependencies_no_deps(self):
        """Test analyzing node dependencies with no dependencies."""
        mock_node = MagicMock()
        mock_node.name = "test_node"

        deps = _analyze_node_dependencies(mock_node)

        assert deps is None

    def test_validate_node_dependencies_success(self):
        """Test validating node dependencies successfully."""
        deps = ContextDependencies(
            inputs={"input1", "input2"},
            outputs={"output1"},
            description="Test dependencies",
        )

        mock_context = MagicMock()
        mock_context.keys.return_value = {"input1", "input2", "output1"}

        result = _validate_node_dependencies(deps, mock_context)

        assert result["valid"] is True
        assert len(result["missing_inputs"]) == 0

    def test_validate_node_dependencies_missing(self):
        """Test validating node dependencies with missing inputs."""
        deps = ContextDependencies(
            inputs={"input1", "input2", "missing_input"},
            outputs={"output1"},
            description="Test dependencies",
        )

        mock_context = MagicMock()
        mock_context.keys.return_value = {"input1", "output1"}

        result = _validate_node_dependencies(deps, mock_context)

        assert result["valid"] is False
        assert "missing_input" in result["missing_inputs"]

    def test_capture_full_context_state(self):
        """Test capturing full context state."""
        mock_context = MagicMock()
        mock_context.keys.return_value = {"field1", "field2"}
        mock_context.get.return_value = "test_value"
        mock_context.session_id = "test_session"
        mock_context.error_count.return_value = 0
        mock_context.get_history.return_value = []

        state = _capture_full_context_state(mock_context)

        assert "current_fields" in state
        assert "session_id" in state
        assert "error_count" in state
        assert "history_summary" in state

    def test_format_context_history(self):
        """Test formatting context history."""
        # Mock history entries
        mock_entry1 = MagicMock()
        mock_entry1.timestamp = "2024-01-01T12:00:00"
        mock_entry1.action = "set"
        mock_entry1.key = "test_key"
        mock_entry1.value = "test_value"
        mock_entry1.modified_by = "test_user"

        mock_entry2 = MagicMock()
        mock_entry2.timestamp = "2024-01-01T12:01:00"
        mock_entry2.action = "get"
        mock_entry2.key = "test_key"
        mock_entry2.value = "test_value"
        mock_entry2.modified_by = None

        history = [mock_entry1, mock_entry2]
        formatted = _format_context_history(history)

        assert len(formatted) == 2
        assert formatted[0]["action"] == "set"
        assert formatted[1]["action"] == "get"

    def test_format_console_trace(self):
        """Test formatting console trace."""
        trace_data = {
            "timestamp": "2024-01-01T12:00:00",
            "user_input": "test input",
            "session_id": "test_session",
            "execution_summary": {
                "total_fields": 2,
                "history_entries": 1,
                "error_count": 0,
            },
            "context_state": {
                "current_fields": {"field1", "field2"},
                "session_id": "test_session",
                "error_count": 0,
            },
            "history": [],
        }

        result = _format_console_trace(trace_data)

        assert isinstance(result, str)
        assert "test input" in result
        assert "test_session" in result
        assert "2 fields" in result
