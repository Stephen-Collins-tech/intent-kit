"""
Tests for graph builder module.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from intent_kit.builders.graph import IntentGraphBuilder
from intent_kit.nodes import TreeNode
from intent_kit.graph import IntentGraph


class TestIntentGraphBuilder:
    """Test cases for IntentGraphBuilder."""

    def test_init(self):
        """Test IntentGraphBuilder initialization."""
        builder = IntentGraphBuilder()
        assert builder._root_nodes == []
        assert builder._debug_context_enabled is False
        assert builder._context_trace_enabled is False
        assert builder._json_graph is None
        assert builder._function_registry is None
        assert builder._llm_config is None

    def test_root(self):
        """Test setting root node."""
        builder = IntentGraphBuilder()
        mock_node = MagicMock(spec=TreeNode)

        result = builder.root(mock_node)

        assert result is builder
        assert builder._root_nodes == [mock_node]

    def test_with_json(self):
        """Test setting JSON graph."""
        builder = IntentGraphBuilder()
        json_graph = {"root": "test", "nodes": {}}

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
            with patch("yaml.safe_load", return_value={"root": "test", "nodes": {}}):
                result = builder.with_yaml("test.yaml")

        assert result is builder
        assert builder._json_graph is not None

    def test_with_yaml_dict(self):
        """Test setting YAML from dict."""
        builder = IntentGraphBuilder()
        yaml_dict = {"root": "test", "nodes": {}}

        result = builder.with_yaml(yaml_dict)

        assert result is builder
        assert builder._json_graph == yaml_dict

    def test_with_yaml_import_error(self):
        """Test with_yaml when PyYAML is not available."""
        builder = IntentGraphBuilder()

        with patch("builtins.open", mock_open(read_data="test: data")):
            with patch(
                "intent_kit.services.yaml_service.yaml_service.safe_load",
                side_effect=ImportError("PyYAML is required"),
            ):
                with pytest.raises(ValueError, match="PyYAML is required"):
                    builder.with_yaml("test.yaml")

    def test_with_yaml_file_error(self):
        """Test with_yaml when file loading fails."""
        builder = IntentGraphBuilder()

        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            with pytest.raises(ValueError, match="Failed to load YAML file"):
                builder.with_yaml("nonexistent.yaml")

    def test_with_default_llm_config(self):
        """Test setting default LLM configuration."""
        builder = IntentGraphBuilder()
        llm_config = {"provider": "openai", "api_key": "test_key"}

        result = builder.with_default_llm_config(llm_config)

        assert result is builder
        assert builder._llm_config == llm_config

    def test_process_llm_config_none(self):
        """Test processing None LLM config."""
        builder = IntentGraphBuilder()
        result = builder._process_llm_config(None)
        assert result is None

    def test_process_llm_config_empty(self):
        """Test processing empty LLM config."""
        builder = IntentGraphBuilder()
        result = builder._process_llm_config({})
        assert result == {}

    def test_process_llm_config_with_env_vars(self):
        """Test processing LLM config with environment variables."""
        builder = IntentGraphBuilder()
        llm_config = {"provider": "openai", "api_key": "${OPENAI_API_KEY}"}

        with patch("os.getenv", return_value="env_api_key"):
            result = builder._process_llm_config(llm_config)

        assert result is not None
        assert result["provider"] == "openai"
        assert result["api_key"] == "env_api_key"

    def test_process_llm_config_env_var_not_found(self):
        """Test processing LLM config with missing environment variable."""
        builder = IntentGraphBuilder()
        llm_config = {"provider": "openai", "api_key": "${MISSING_KEY}"}

        with patch("os.getenv", return_value=None):
            result = builder._process_llm_config(llm_config)

        assert result is not None
        assert result["provider"] == "openai"
        assert result["api_key"] == "${MISSING_KEY}"

    def test_process_llm_config_mixed_env_vars(self):
        """Test processing LLM config with mixed environment and regular values."""
        builder = IntentGraphBuilder()
        llm_config = {
            "provider": "openai",
            "api_key": "${OPENAI_API_KEY}",
            "model": "gpt-4",
            "temperature": "${TEMP}",
        }

        with patch("os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key: (
                "env_api_key"
                if key == "OPENAI_API_KEY"
                else "0.7" if key == "TEMP" else None
            )
            result = builder._process_llm_config(llm_config)

        assert result is not None
        assert result["provider"] == "openai"
        assert result["api_key"] == "env_api_key"
        assert result["model"] == "gpt-4"
        assert result["temperature"] == "0.7"

    def test_process_llm_config_validation_openai(self):
        """Test LLM config validation for OpenAI provider."""
        builder = IntentGraphBuilder()
        llm_config = {"provider": "openai"}

        with patch("os.getenv", return_value=None):
            result = builder._process_llm_config(llm_config)

        # Should warn about missing api_key but not fail
        assert result is not None
        assert result["provider"] == "openai"

    def test_process_llm_config_validation_anthropic(self):
        """Test LLM config validation for Anthropic provider."""
        builder = IntentGraphBuilder()
        llm_config = {"provider": "anthropic"}

        with patch("os.getenv", return_value=None):
            result = builder._process_llm_config(llm_config)

        # Should warn about missing api_key but not fail
        assert result is not None
        assert result["provider"] == "anthropic"

    def test_process_llm_config_validation_ollama(self):
        """Test LLM config validation for Ollama provider."""
        builder = IntentGraphBuilder()
        llm_config = {"provider": "ollama"}

        with patch("os.getenv", return_value=None):
            result = builder._process_llm_config(llm_config)

        # Ollama doesn't require api_key, so no warning
        assert result is not None
        assert result["provider"] == "ollama"

    def test_build_with_json_validation_no_graph(self):
        """Test build validation when no JSON graph is set."""
        builder = IntentGraphBuilder()

        with pytest.raises(ValueError, match="No JSON graph set"):
            builder._validate_json_graph()

    def test_build_with_json_validation_missing_root(self):
        """Test build validation with missing root field."""
        builder = IntentGraphBuilder()
        builder._json_graph = {"nodes": {}}

        with pytest.raises(ValueError, match="Missing 'root' field"):
            builder._validate_json_graph()

    def test_build_with_json_validation_missing_intents(self):
        """Test build validation with missing nodes field."""
        builder = IntentGraphBuilder()
        builder._json_graph = {"root": "test"}

        with pytest.raises(ValueError, match="Missing 'nodes' field"):
            builder._validate_json_graph()

    def test_build_with_json_validation_root_not_found(self):
        builder = IntentGraphBuilder()
        # Setup a graph missing the root node
        builder._json_graph = {
            "nodes": {"test": {"type": "action"}},
            "root": "nonexistent",
        }
        with pytest.raises(
            ValueError,
            match="Root node 'nonexistent' not found in nodes",
        ):
            builder._validate_json_graph()

    def test_build_with_json_validation_missing_type(self):
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "nodes": {"test": {"name": "test"}}, "root": "test"}
        with pytest.raises(
            ValueError,
            match="Node 'test' missing 'type' field",
        ):
            builder._validate_json_graph()

    def test_build_with_json_validation_action_missing_function(self):
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "nodes": {"test": {"type": "action", "name": "test"}},
            "root": "test",
        }
        with pytest.raises(
            ValueError,
            match="Action node 'test' missing 'function' field",
        ):
            builder._validate_json_graph()

    def test_build_with_json_validation_llm_classifier_missing_config(self):
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "nodes": {
                "test": {"type": "classifier", "classifier_type": "llm", "name": "test"}
            },
            "root": "test",
        }
        with pytest.raises(
            ValueError,
            match="LLM classifier node 'test' missing 'llm_config' field",
        ):
            builder._validate_json_graph()

    def test_build_with_json_validation_classifier_missing_function(self):
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "nodes": {
                "test": {
                    "type": "classifier",
                    "classifier_type": "rule",
                    "name": "test",
                }
            },
            "root": "test",
        }
        with pytest.raises(
            ValueError,
            match="Rule classifier node 'test' missing 'classifier_function' field",
        ):
            builder._validate_json_graph()

    def test_build_with_json_validation_valid(self):
        """Test build validation with valid JSON graph."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "nodes": {
                "test": {
                    "type": "action",
                    "function": "test_func",
                    "name": "test",
                    "description": "Test description",
                }
            },
        }

        # Should not raise any exception
        builder._validate_json_graph()

    def test_validate_json_graph_public_api(self):
        """Test the public validate_json_graph method."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "nodes": {
                "test": {
                    "type": "action",
                    "function": "test_func",
                    "name": "test",
                    "description": "Test description",
                }
            },
        }

        result = builder.validate_json_graph()

        assert result["valid"] is True
        assert result["node_count"] == 1
        assert result["edge_count"] == 0
        assert len(result["errors"]) == 0

    def test_validate_json_graph_public_api_with_errors(self):
        """Test the public validate_json_graph method with validation errors."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "nodes": {
                "test": {
                    "type": "action",
                    # Missing function field
                    "name": "test",
                    "description": "Test description",
                }
            },
        }

        result = builder.validate_json_graph()

        assert result["valid"] is False
        assert result["node_count"] == 1
        assert len(result["errors"]) > 0
        assert "missing 'function' field" in result["errors"][0].lower()

    def test_validate_json_graph_public_api_no_graph(self):
        """Test the public validate_json_graph method when no graph is set."""
        builder = IntentGraphBuilder()

        with pytest.raises(ValueError, match="No JSON graph set"):
            builder.validate_json_graph()

    def test_validate_json_graph_with_cycles(self):
        """Test validation with cycles in the graph."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "A",
            "nodes": {
                "A": {
                    "type": "action",
                    "function": "func_a",
                    "name": "A",
                    "children": ["B"],
                },
                "B": {
                    "type": "action",
                    "function": "func_b",
                    "name": "B",
                    "children": ["C"],
                },
                "C": {
                    "type": "action",
                    "function": "func_c",
                    "name": "C",
                    "children": ["A"],
                },
            },
        }

        result = builder.validate_json_graph()
        assert result["valid"] is False
        assert result["cycles_detected"] is True
        assert len(result["errors"]) > 0
        assert "cycles detected" in result["errors"][0].lower()

    def test_validate_json_graph_with_unreachable_nodes(self):
        """Test validation with unreachable nodes."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "A",
            "nodes": {
                "A": {
                    "type": "action",
                    "function": "func_a",
                    "name": "A",
                    "children": ["B"],
                },
                "B": {"type": "action", "function": "func_b", "name": "B"},
                # Unreachable
                "C": {"type": "action", "function": "func_c", "name": "C"},
            },
        }

        result = builder.validate_json_graph()
        # Unreachable nodes are warnings, not errors
        assert result["valid"] is True
        assert "C" in result["unreachable_nodes"]
        assert len(result["warnings"]) > 0
        assert "unreachable" in result["warnings"][0].lower()

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
            "nodes": {
                "test": {
                    "type": "action",
                    "function": "test_func",
                    "name": "test",
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
            "nodes": {
                "test": {
                    "type": "action",
                    "function": "test_func",
                    "name": "test",
                    "description": "Test description",
                }
            },
        }

        with pytest.raises(
            ValueError, match="Function 'test_func' not found in function registry"
        ):
            builder.build()

    def test_build_with_json_validation_integration(self):
        """Test that build method calls validation internally."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "nodes": {
                "test": {
                    "type": "action",
                    "function": "test_func",
                    "name": "test",
                    "description": "Test description",
                }
            },
        }
        builder._function_registry = {"test_func": MagicMock()}

        # Should not raise validation errors since graph is valid
        result = builder.build()
        assert isinstance(result, IntentGraph)

    def test_build_with_json_validation_failure(self):
        """Test that build method fails when validation fails."""
        builder = IntentGraphBuilder()
        builder._json_graph = {
            "root": "test",
            "nodes": {
                "test": {
                    "type": "action",
                    # Missing function field
                    "name": "test",
                    "description": "Test description",
                }
            },
        }

        with pytest.raises(
            ValueError, match="Action node 'test' missing 'function' field"
        ):
            builder.build()

    def test_build_with_llm_config_injection(self):
        """Test building graph with LLM config injection."""
        builder = IntentGraphBuilder()
        mock_node = MagicMock(spec=TreeNode)
        # Set up the classifier attribute properly
        mock_classifier = MagicMock()
        mock_classifier.__name__ = "llm_classifier"
        mock_node.classifier = mock_classifier
        mock_node.llm_config = None
        mock_node.children = []

        builder.root(mock_node)
        builder.with_default_llm_config(
            {"provider": "openai", "api_key": "test"})

        result = builder.build()

        assert isinstance(result, IntentGraph)
        # Should have injected LLM config into the node
        assert mock_node.llm_config == {
            "provider": "openai", "api_key": "test"}

    def test_build_with_llm_config_validation_failure(self):
        """Test building graph with LLM config validation failure."""
        builder = IntentGraphBuilder()
        mock_node = MagicMock(spec=TreeNode)
        # Set up the classifier attribute properly
        mock_classifier = MagicMock()
        mock_classifier.__name__ = "llm_classifier"
        mock_node.classifier = mock_classifier
        mock_node.llm_config = None
        mock_node.children = []
        mock_node.name = "test_node"

        builder.root(mock_node)
        # No default LLM config set

        with pytest.raises(ValueError, match="requires an LLM config"):
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
        nodes = {
            "A": {"type": "action", "children": ["B"]},
            "B": {"type": "action", "children": ["C"]},
            "C": {"type": "action", "children": ["A"]},
        }

        cycles = builder._detect_cycles(nodes)

        assert len(cycles) > 0
        assert any(
            "A" in cycle and "B" in cycle and "C" in cycle for cycle in cycles)

    def test_detect_cycles_no_cycles(self):
        """Test cycle detection in graph without cycles."""
        builder = IntentGraphBuilder()
        nodes = {
            "A": {"type": "action", "children": ["B"]},
            "B": {"type": "action", "children": ["C"]},
            "C": {"type": "action"},
        }

        cycles = builder._detect_cycles(nodes)

        assert len(cycles) == 0

    def test_detect_cycles_self_loop(self):
        """Test cycle detection with self-loop."""
        builder = IntentGraphBuilder()
        nodes = {
            "A": {"type": "action", "children": ["A"]},
        }

        cycles = builder._detect_cycles(nodes)

        assert len(cycles) > 0
        assert any("A" in cycle for cycle in cycles)

    def test_find_unreachable_nodes(self):
        """Test finding unreachable nodes."""
        builder = IntentGraphBuilder()
        nodes = {
            "A": {"type": "action", "children": ["B"]},
            "B": {"type": "action"},
            "C": {"type": "action"},  # Unreachable
        }

        unreachable = builder._find_unreachable_nodes(nodes, "A")

        assert "C" in unreachable
        assert "A" not in unreachable
        assert "B" not in unreachable

    def test_find_unreachable_nodes_all_reachable(self):
        """Test finding unreachable nodes when all are reachable."""
        builder = IntentGraphBuilder()
        nodes = {
            "A": {"type": "action", "children": ["B"]},
            "B": {"type": "action"},
        }

        unreachable = builder._find_unreachable_nodes(nodes, "A")

        assert len(unreachable) == 0

    def test_find_unreachable_nodes_disconnected(self):
        """Test finding unreachable nodes in disconnected graph."""
        builder = IntentGraphBuilder()
        nodes = {
            "A": {"type": "action"},
            "B": {"type": "action"},
            "C": {"type": "action"},
        }

        unreachable = builder._find_unreachable_nodes(nodes, "A")

        assert "B" in unreachable
        assert "C" in unreachable
        assert "A" not in unreachable

    def test_create_node_from_spec_action(self):
        """Test creating action node from specification."""
        builder = IntentGraphBuilder()
        node_spec = {
            "type": "action",
            "name": "test_action",
            "description": "Test action",
            "function": "test_func",
            "param_schema": {"param1": "str"},
            "llm_config": {"provider": "openai"},
            "context_inputs": ["input1"],
            "context_outputs": ["output1"],
            "remediation_strategies": ["retry"],
        }
        function_registry = {"test_func": lambda x: x}

        node = builder._create_node_from_spec(
            "test_id", node_spec, function_registry)
        assert node.name == "test_action"
        assert node.description == "Test action"

    def test_create_node_from_spec_classifier(self):
        """Test creating classifier node from specification."""
        builder = IntentGraphBuilder()
        node_spec = {
            "type": "classifier",
            "name": "test_classifier",
            "description": "Test classifier",
            "classifier_function": "test_classifier_func",
            "llm_config": {"provider": "openai"},
            "remediation_strategies": ["retry"],
        }
        function_registry = {"test_classifier_func": lambda x: x}

        node = builder._create_node_from_spec(
            "test_id", node_spec, function_registry)
        assert node.name == "test_classifier"
        assert node.description == "Test classifier"

    def test_create_node_from_spec_llm_classifier(self):
        """Test creating LLM classifier node from specification."""
        builder = IntentGraphBuilder()
        node_spec = {
            "type": "classifier",
            "name": "test_llm_classifier",
            "description": "Test LLM classifier",
            "classifier_type": "llm",
            "llm_config": {"provider": "openai", "api_key": "test"},
            "classification_prompt": "Test prompt",
            "remediation_strategies": ["retry"],
        }
        function_registry = {}

        node = builder._create_node_from_spec(
            "test_id", node_spec, function_registry)
        assert node.name == "test_llm_classifier"
        assert node.description == "Test LLM classifier"

    def test_create_node_from_spec_missing_type(self):
        """Test creating node with missing type."""
        builder = IntentGraphBuilder()
        node_spec = {"name": "test_node", "description": "Test node"}
        function_registry = {}

        with pytest.raises(ValueError, match="must have a 'type' field"):
            builder._create_node_from_spec(
                "test_id", node_spec, function_registry)

    def test_create_node_from_spec_unknown_type(self):
        """Test creating node with unknown type."""
        builder = IntentGraphBuilder()
        node_spec = {
            "type": "unknown_type",
            "name": "test_node",
            "description": "Test node",
        }
        function_registry = {}

        with pytest.raises(ValueError, match="Unknown node type"):
            builder._create_node_from_spec(
                "test_id", node_spec, function_registry)

    def test_create_action_node_missing_function(self):
        """Test creating action node with missing function."""
        builder = IntentGraphBuilder()
        node_spec = {
            "type": "action",
            "name": "test_action",
            "description": "Test action",
        }
        function_registry = {}

        with pytest.raises(ValueError, match="must have a 'function' field"):
            builder._create_action_node(
                "test_id", "test_action", "Test action", node_spec, function_registry
            )

    def test_create_action_node_function_not_found(self):
        """Test creating action node with function not in registry."""
        builder = IntentGraphBuilder()
        node_spec = {
            "type": "action",
            "name": "test_action",
            "description": "Test action",
            "function": "missing_func",
        }
        function_registry = {}

        with pytest.raises(ValueError, match="not found in function registry"):
            builder._create_action_node(
                "test_id", "test_action", "Test action", node_spec, function_registry
            )

    def test_create_llm_classifier_node_missing_config(self):
        """Test creating LLM classifier node with missing config."""
        builder = IntentGraphBuilder()
        node_spec = {
            "type": "classifier",
            "name": "test_llm_classifier",
            "description": "Test LLM classifier",
            "classifier_type": "llm",
        }
        function_registry = {}

        with pytest.raises(ValueError, match="must have an 'llm_config' field"):
            builder._create_llm_classifier_node(
                "test_id",
                "test_llm_classifier",
                "Test LLM classifier",
                node_spec,
                function_registry,
            )

    def test_create_classifier_node_missing_function(self):
        """Test creating classifier node with missing function."""
        builder = IntentGraphBuilder()
        node_spec = {
            "type": "classifier",
            "name": "test_classifier",
            "description": "Test classifier",
        }
        function_registry = {}

        with pytest.raises(ValueError, match="must have a 'classifier_function' field"):
            builder._create_classifier_node(
                "test_id",
                "test_classifier",
                "Test classifier",
                node_spec,
                function_registry,
            )

    def test_create_classifier_node_function_not_found(self):
        """Test creating classifier node with function not in registry."""
        builder = IntentGraphBuilder()
        node_spec = {
            "type": "classifier",
            "name": "test_classifier",
            "description": "Test classifier",
            "classifier_function": "missing_func",
        }
        function_registry = {}

        with pytest.raises(ValueError, match="not found in function registry"):
            builder._create_classifier_node(
                "test_id",
                "test_classifier",
                "Test classifier",
                node_spec,
                function_registry,
            )

    def test_build_from_json_complex_graph(self):
        """Test building complex graph from JSON."""
        builder = IntentGraphBuilder()
        graph_spec = {
            "root": "start",
            "nodes": {
                "start": {
                    "type": "classifier",
                    "name": "start",
                    "description": "Start classifier",
                    "classifier_function": "start_classifier",
                    "children": ["action1", "action2"],
                },
                "action1": {
                    "type": "action",
                    "name": "action1",
                    "description": "First action",
                    "function": "action1_func",
                    "children": ["end"],
                },
                "action2": {
                    "type": "action",
                    "name": "action2",
                    "description": "Second action",
                    "function": "action2_func",
                    "children": ["end"],
                },
                "end": {
                    "type": "action",
                    "name": "end",
                    "description": "End action",
                    "function": "end_func",
                },
            },
        }
        function_registry = {
            "start_classifier": lambda x: x,
            "action1_func": lambda x: x,
            "action2_func": lambda x: x,
            "end_func": lambda x: x,
        }

        graph = builder._build_from_json(graph_spec, function_registry)
        assert isinstance(graph, IntentGraph)
        assert len(graph.root_nodes) == 1
        assert graph.root_nodes[0].name == "start"

    def test_build_from_json_missing_root(self):
        """Test building from JSON with missing root."""
        builder = IntentGraphBuilder()
        graph_spec = {
            "nodes": {
                "test": {"type": "action", "name": "test", "function": "test_func"}
            }
        }
        function_registry = {"test_func": lambda x: x}

        with pytest.raises(ValueError, match="must contain a 'root' field"):
            builder._build_from_json(graph_spec, function_registry)

    def test_build_from_json_missing_nodes(self):
        """Test building from JSON with missing nodes."""
        builder = IntentGraphBuilder()
        graph_spec = {"root": "test"}
        function_registry = {}

        with pytest.raises(ValueError, match="must contain an 'nodes' field"):
            builder._build_from_json(graph_spec, function_registry)

    def test_build_from_json_root_not_found(self):
        """Test building from JSON with root not in nodes."""
        builder = IntentGraphBuilder()
        graph_spec = {
            "root": "missing",
            "nodes": {
                "test": {"type": "action", "name": "test", "function": "test_func"}
            },
        }
        function_registry = {"test_func": lambda x: x}

        with pytest.raises(ValueError, match="not found in nodes"):
            builder._build_from_json(graph_spec, function_registry)

    def test_build_from_json_child_not_found(self):
        """Test building from JSON with child not in nodes."""
        builder = IntentGraphBuilder()
        graph_spec = {
            "root": "start",
            "nodes": {
                "start": {
                    "type": "action",
                    "name": "start",
                    "function": "start_func",
                    "children": ["missing"],
                }
            },
        }
        function_registry = {"start_func": lambda x: x}

        with pytest.raises(ValueError, match="not found in nodes"):
            builder._build_from_json(graph_spec, function_registry)

    def test_build_from_json_node_missing_id_or_name(self):
        """Test building from JSON with node missing id and name."""
        builder = IntentGraphBuilder()
        graph_spec = {
            "root": "test",
            "nodes": {"test": {"type": "action", "function": "test_func"}},
        }
        function_registry = {"test_func": lambda x: x}

        with pytest.raises(ValueError, match="missing required 'id' or 'name' field"):
            builder._build_from_json(graph_spec, function_registry)

    def test_build_from_json_with_llm_config(self):
        """Test building from JSON with LLM config."""
        builder = IntentGraphBuilder()
        builder.with_default_llm_config(
            {"provider": "openai", "api_key": "test"})

        graph_spec = {
            "root": "test",
            "nodes": {
                "test": {"type": "action", "name": "test", "function": "test_func"}
            },
        }
        function_registry = {"test_func": lambda x: x}

        graph = builder._build_from_json(graph_spec, function_registry)
        assert isinstance(graph, IntentGraph)
        assert graph.llm_config == {"provider": "openai", "api_key": "test"}

    def test_build_from_json_with_debug_context(self):
        """Test building from JSON with debug context enabled."""
        builder = IntentGraphBuilder()
        builder._debug_context_enabled = True
        builder._context_trace_enabled = True

        graph_spec = {
            "root": "test",
            "nodes": {
                "test": {"type": "action", "name": "test", "function": "test_func"}
            },
        }
        function_registry = {"test_func": lambda x: x}

        graph = builder._build_from_json(graph_spec, function_registry)
        assert isinstance(graph, IntentGraph)
        assert graph.debug_context is True
        assert graph.context_trace is True

    def test_build_with_no_root_and_no_json(self):
        """Test building with no root nodes and no JSON graph."""
        builder = IntentGraphBuilder()

        with pytest.raises(ValueError, match="No root nodes set"):
            builder.build()

    def test_build_with_json_and_root_nodes(self):
        """Test building with both JSON and root nodes (JSON should take precedence)."""
        builder = IntentGraphBuilder()
        mock_node = MagicMock(spec=TreeNode)
        builder.root(mock_node)

        builder._json_graph = {
            "root": "test",
            "nodes": {
                "test": {"type": "action", "name": "test", "function": "test_func"}
            },
        }
        builder._function_registry = {"test_func": MagicMock()}

        result = builder.build()
        assert isinstance(result, IntentGraph)
        # Should use JSON graph, not the root node
        assert result.root_nodes[0].name == "test"
