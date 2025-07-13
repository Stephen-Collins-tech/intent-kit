"""
Tests for graph builder module.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from intent_kit.builders.graph import IntentGraphBuilder
from intent_kit.node import TreeNode
from intent_kit.graph import IntentGraph


class TestIntentGraphBuilder:
    """Test cases for IntentGraphBuilder."""

    def test_init(self):
        """Test IntentGraphBuilder initialization."""
        builder = IntentGraphBuilder()
        assert builder._root_nodes == []
        assert builder._splitter is None
        assert builder._debug_context_enabled is False
        assert builder._context_trace_enabled is False
        assert builder._json_graph is None
        assert builder._function_registry is None

    def test_root(self):
        """Test setting root node."""
        builder = IntentGraphBuilder()
        mock_node = MagicMock(spec=TreeNode)

        result = builder.root(mock_node)

        assert result is builder
        assert builder._root_nodes == [mock_node]

    def test_splitter(self):
        """Test setting splitter function."""
        builder = IntentGraphBuilder()
        mock_splitter = MagicMock()

        result = builder.splitter(mock_splitter)

        assert result is builder
        assert builder._splitter == mock_splitter

    def test_with_json(self):
        """Test setting JSON graph."""
        builder = IntentGraphBuilder()
        json_graph = {"root": "test", "intents": {}}

        result = builder.with_json(json_graph)

        assert result is builder
        assert builder._json_graph == json_graph

    def test_with_functions(self):
        """Test setting function registry."""
        builder = IntentGraphBuilder()
        function_registry = {"test_func": MagicMock()}

        result = builder.with_functions(function_registry)

        assert result is builder
        assert builder._function_registry == function_registry

    def test_with_yaml_string(self):
        """Test setting YAML from string path."""
        builder = IntentGraphBuilder()
        yaml_content = "root: test\nintents:\n  test: {type: action}"

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("yaml.safe_load", return_value={"root": "test", "intents": {}}):
                result = builder.with_yaml("test.yaml")

        assert result is builder
        assert builder._json_graph is not None

    def test_with_yaml_dict(self):
        """Test setting YAML from dict."""
        builder = IntentGraphBuilder()
        yaml_dict = {"root": "test", "intents": {}}

        result = builder.with_yaml(yaml_dict)

        assert result is builder
        assert builder._json_graph == yaml_dict

    def test_with_yaml_import_error(self):
        """Test with_yaml when PyYAML is not available."""
        builder = IntentGraphBuilder()

        with patch("yaml", None):
            with pytest.raises(ImportError, match="PyYAML is required"):
                builder.with_yaml("test.yaml")

    def test_with_yaml_file_error(self):
        """Test with_yaml when file loading fails."""
        builder = IntentGraphBuilder()

        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            with pytest.raises(ValueError, match="Failed to load YAML file"):
                builder.with_yaml("nonexistent.yaml")

    def test_validate_json_graph_no_graph(self):
        """Test validation when no JSON graph is set."""
        builder = IntentGraphBuilder()

        with pytest.raises(ValueError, match="No JSON graph set"):
            builder.validate_json_graph()

    def test_validate_json_graph_missing_root(self):
        """Test validation with missing root field."""
        builder = IntentGraphBuilder()
        builder._json_graph = {"intents": {}}

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert "Missing 'root' field" in result["errors"]

    def test_validate_json_graph_missing_intents(self):
        """Test validation with missing intents field."""
        builder = IntentGraphBuilder()
        builder._json_graph = {"root": "test"}

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert "Missing 'intents' field" in result["errors"]

    def test_validate_json_graph_root_not_found(self):
        """Test validation when root node doesn't exist."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "nonexistent",
            "intents": {"test": {"type": "action"}},
        }

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert "Root node 'nonexistent' not found" in result["errors"]

    def test_validate_json_graph_missing_type(self):
        """Test validation with missing type field."""
        builder = IntentGraphBuilder()
        builder._json_graph = {"root": "test", "intents": {"test": {}}}

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert "Node 'test' missing 'type' field" in result["errors"]

    def test_validate_json_graph_action_missing_function(self):
        """Test validation for action node missing function."""
        builder = IntentGraphBuilder()
        builder._json_graph = {"root": "test", "intents": {"test": {"type": "action"}}}

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert "Action node 'test' missing 'function' field" in result["errors"]

    def test_validate_json_graph_llm_classifier_missing_config(self):
        """Test validation for LLM classifier missing config."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "intents": {"test": {"type": "llm_classifier"}},
        }

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert (
            "LLM classifier node 'test' missing 'llm_config' field" in result["errors"]
        )

    def test_validate_json_graph_classifier_missing_function(self):
        """Test validation for classifier missing function."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "intents": {"test": {"type": "classifier"}},
        }

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert (
            "Classifier node 'test' missing 'classifier_function' field"
            in result["errors"]
        )

    def test_validate_json_graph_splitter_missing_function(self):
        """Test validation for splitter missing function."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "intents": {"test": {"type": "splitter"}},
        }

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert (
            "Splitter node 'test' missing 'splitter_function' field" in result["errors"]
        )

    def test_validate_json_graph_valid(self):
        """Test validation with valid JSON graph."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "intents": {
                "test": {
                    "type": "action",
                    "function": "test_func",
                    "name": "Test Action",
                    "description": "Test description",
                }
            },
        }

        result = builder.validate_json_graph()

        assert result["valid"] is True
        assert result["node_count"] == 1
        assert len(result["errors"]) == 0

    def test_build_with_root_nodes(self):
        """Test building graph with root nodes."""
        builder = IntentGraphBuilder()
        mock_node = MagicMock(spec=TreeNode)
        builder.root(mock_node)

        result = builder.build()

        assert isinstance(result, IntentGraph)
        assert result.root_nodes == [mock_node]

    def test_build_with_json(self):
        """Test building graph from JSON specification."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "intents": {
                "test": {
                    "type": "action",
                    "function": "test_func",
                    "name": "Test Action",
                    "description": "Test description",
                }
            },
        }
        builder._function_registry = {"test_func": MagicMock()}

        result = builder.build()

        assert isinstance(result, IntentGraph)

    def test_build_with_json_no_functions(self):
        """Test building graph from JSON without function registry."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "intents": {
                "test": {
                    "type": "action",
                    "function": "test_func",
                    "name": "Test Action",
                    "description": "Test description",
                }
            },
        }

        with pytest.raises(ValueError, match="Function registry is required"):
            builder.build()

    def test_debug_context(self):
        """Test enabling debug context."""
        builder = IntentGraphBuilder()

        result = builder._debug_context(True)

        assert result is builder
        assert builder._debug_context_enabled is True

    def test_context_trace(self):
        """Test enabling context trace."""
        builder = IntentGraphBuilder()

        result = builder._context_trace(True)

        assert result is builder
        assert builder._context_trace_enabled is True

    def test_detect_cycles(self):
        """Test cycle detection in graph."""
        builder = IntentGraphBuilder()
        intents = {
            "A": {"type": "action", "next": "B"},
            "B": {"type": "action", "next": "C"},
            "C": {"type": "action", "next": "A"},
        }

        cycles = builder._detect_cycles(intents)

        assert len(cycles) > 0
        assert any("A" in cycle and "B" in cycle and "C" in cycle for cycle in cycles)

    def test_find_unreachable_nodes(self):
        """Test finding unreachable nodes."""
        builder = IntentGraphBuilder()
        intents = {
            "A": {"type": "action", "next": "B"},
            "B": {"type": "action"},
            "C": {"type": "action"},  # Unreachable
        }

        unreachable = builder._find_unreachable_nodes(intents, "A")

        assert "C" in unreachable
        assert "A" not in unreachable
        assert "B" not in unreachable
