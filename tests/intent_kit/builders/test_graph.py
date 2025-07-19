"""
Tests for graph builder module.
"""

import pytest






class TestIntentGraphBuilder:
    """Test cases for IntentGraphBuilder."""

    def test_def test_init(self): -> None:
        """Test IntentGraphBuilder initialization."""
        builder = IntentGraphBuilder()
        assert builder._root_nodes == []
        assert builder._splitter is None
        assert builder._debug_context_enabled is False
        assert builder._context_trace_enabled is False
        assert builder._json_graph is None
        assert builder._function_registry is None

    def test_def test_root(self): -> None:
        """Test setting root node."""
        builder = IntentGraphBuilder()
        mock_node = MagicMock(spec=TreeNode)

        result = builder.root(mock_node)

        assert result is builder
        assert builder._root_nodes == [mock_node]

    def test_def test_splitter(self): -> None:
        """Test setting splitter function."""
        builder = IntentGraphBuilder()
        mock_splitter = MagicMock()

        result = builder.splitter(mock_splitter)

        assert result is builder
        assert builder._splitter == mock_splitter

    def test_def test_with_json(self): -> None:
        """Test setting JSON graph."""
        builder = IntentGraphBuilder()
        json_graph = {"root": "test", "intents": {}}

        result = builder.with_json(json_graph)

        assert result is builder
        assert builder._json_graph == json_graph

    def test_def test_with_functions(self): -> None:
        """Test setting function registry."""
        builder = IntentGraphBuilder()
        function_registry = {"test_func": MagicMock()}

        result = builder.with_functions(function_registry)

        assert result is builder
        assert builder._function_registry == function_registry

    def test_def test_with_yaml_string(self): -> None:
        """Test setting YAML from string path."""
        builder = IntentGraphBuilder()
        yaml_content = "root: test\nintents:\n  test: {type: action}"

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            with patch("yaml.safe_load", return_value={"root": "test", "intents": {}}):
                result = builder.with_yaml("test.yaml")

        assert result is builder
        assert builder._json_graph is not None

    def test_def test_with_yaml_dict(self): -> None:
        """Test setting YAML from dict."""
        builder = IntentGraphBuilder()
        yaml_dict = {"root": "test", "intents": {}}

        result = builder.with_yaml(yaml_dict)

        assert result is builder
        assert builder._json_graph == yaml_dict

    def test_def test_with_yaml_import_error(self): -> None:
        """Test with_yaml when PyYAML is not available."""
        builder = IntentGraphBuilder()

        with patch("builtins.open", mock_open(read_data="test: data")):
            with patch(
                "intent_kit.services.yaml_service.yaml_service.safe_load",
                side_effect=ImportError("PyYAML is required"),
            ):
                with pytest.raises(ValueError, match="PyYAML is required"):
                    builder.with_yaml("test.yaml")

    def test_def test_with_yaml_file_error(self): -> None:
        """Test with_yaml when file loading fails."""
        builder = IntentGraphBuilder()

        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            with pytest.raises(ValueError, match="Failed to load YAML file"):
                builder.with_yaml("nonexistent.yaml")

    def test_def test_validate_json_graph_no_graph(self): -> None:
        """Test validation when no JSON graph is set."""
        builder = IntentGraphBuilder()

        with pytest.raises(ValueError, match="No JSON graph set"):
            builder.validate_json_graph()

    def test_def test_validate_json_graph_missing_root(self): -> None:
        """Test validation with missing root field."""
        builder = IntentGraphBuilder()
        builder._json_graph = {"intents": {}}

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert "Missing 'root' field" in result["errors"]

    def test_def test_validate_json_graph_missing_intents(self): -> None:
        """Test validation with missing intents field."""
        builder = IntentGraphBuilder()
        builder._json_graph = {"root": "test"}

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert "Missing 'intents' field" in result["errors"]

    def test_def test_validate_json_graph_root_not_found(self): -> None:
        builder = IntentGraphBuilder()
        # Setup a graph missing the root node
        builder._json_graph = {
            "intents": {"test": {"type": "action"}},
            "root": "nonexistent",
        }
        with pytest.raises(
            ValueError,
            match="Graph validation failed: Root node 'nonexistent' not found in intents; Action node 'test' missing 'function' field",
        ):
            builder.validate_json_graph()

    def test_def test_validate_json_graph_missing_type(self): -> None:
        builder = IntentGraphBuilder()
        builder._json_graph = {"intents": {"test": {}}, "root": "test"}
        with pytest.raises(
            ValueError,
            match="Graph validation failed: Node 'test' missing 'type' field",
        ):
            builder.validate_json_graph()

    def test_def test_validate_json_graph_action_missing_function(self): -> None:
        builder = IntentGraphBuilder()
        builder._json_graph = {"intents": {"test": {"type": "action"}}, "root": "test"}
        with pytest.raises(
            ValueError,
            match="Graph validation failed: Action node 'test' missing 'function' field",
        ):
            builder.validate_json_graph()

    def test_def test_validate_json_graph_llm_classifier_missing_config(self): -> None:
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "intents": {"test": {"type": "llm_classifier"}},
            "root": "test",
        }
        with pytest.raises(
            ValueError,
            match="Graph validation failed: LLM classifier node 'test' missing 'llm_config' field",
        ):
            builder.validate_json_graph()

    def test_def test_validate_json_graph_classifier_missing_function(self): -> None:
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "intents": {"test": {"type": "classifier"}},
            "root": "test",
        }
        with pytest.raises(
            ValueError,
            match="Graph validation failed: Classifier node 'test' missing 'classifier_function' field",
        ):
            builder.validate_json_graph()

    def test_def test_validate_json_graph_splitter_missing_function(self): -> None:
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "intents": {"test": {"type": "splitter"}},
            "root": "test",
        }
        with pytest.raises(
            ValueError,
            match="Graph validation failed: Splitter node 'test' missing 'splitter_function' field",
        ):
            builder.validate_json_graph()

    def test_def test_validate_json_graph_valid(self): -> None:
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

    def test_def test_build_with_root_nodes(self): -> None:
        """Test building graph with root nodes."""
        builder = IntentGraphBuilder()
        mock_node = MagicMock(spec=TreeNode)
        builder.root(mock_node)

        result = builder.build()

        assert isinstance(result, IntentGraph)
        assert result.root_nodes == [mock_node]

    def test_def test_build_with_json(self): -> None:
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

    def test_def test_build_with_json_no_functions(self): -> None:
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

        with pytest.raises(
            ValueError, match="Function 'test_func' not found in function registry"
        ):
            builder.build()

    def test_def test_debug_context(self): -> None:
        """Test enabling debug context."""
        builder = IntentGraphBuilder()

        result = builder._debug_context(True)

        assert result is builder
        assert builder._debug_context_enabled is True

    def test_def test_context_trace(self): -> None:
        """Test enabling context trace."""
        builder = IntentGraphBuilder()

        result = builder._context_trace(True)

        assert result is builder
        assert builder._context_trace_enabled is True

    def test_def test_detect_cycles(self): -> None:
        """Test cycle detection in graph."""
        builder = IntentGraphBuilder()
        intents = {
            "A": {"type": "action", "children": ["B"]},
            "B": {"type": "action", "children": ["C"]},
            "C": {"type": "action", "children": ["A"]},
        }

        cycles = builder._detect_cycles(intents)

        assert len(cycles) > 0
        assert any("A" in cycle and "B" in cycle and "C" in cycle for cycle in cycles)

    def test_def test_find_unreachable_nodes(self): -> None:
        """Test finding unreachable nodes."""
        builder = IntentGraphBuilder()
        intents = {
            "A": {"type": "action", "children": ["B"]},
            "B": {"type": "action"},
            "C": {"type": "action"},  # Unreachable
        }

        unreachable = builder._find_unreachable_nodes(intents, "A")

        assert "C" in unreachable
        assert "A" not in unreachable
        assert "B" not in unreachable
