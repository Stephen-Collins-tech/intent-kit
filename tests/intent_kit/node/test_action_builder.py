"""
Tests for ActionBuilder class.
"""

import pytest
from typing import Dict, Any
from intent_kit.nodes.actions.builder import ActionBuilder
from intent_kit.services.ai.base_client import BaseLLMClient


class TestActionBuilder:
    """Test the ActionBuilder class."""

    def test_with_llm_config_dict(self):
        """Test with_llm_config method with dictionary config."""
        builder = ActionBuilder("test_action")

        llm_config = {"provider": "openai", "api_key": "test_key"}
        result = builder.with_llm_config(llm_config)

        assert result is builder
        assert builder.llm_config == llm_config

    def test_with_llm_config_none(self):
        """Test with_llm_config method with None."""
        builder = ActionBuilder("test_action")

        result = builder.with_llm_config(None)

        assert result is builder
        assert builder.llm_config is None

    def test_with_llm_config_client(self):
        """Test with_llm_config method with BaseLLMClient instance."""
        builder = ActionBuilder("test_action")

        # Mock LLM client
        class MockLLMClient(BaseLLMClient):
            def _initialize_client(self, **kwargs):
                pass

            def get_client(self):
                return None

            def _ensure_imported(self):
                pass

            def generate(self, prompt: str, model=None):
                from intent_kit.types import LLMResponse

                return LLMResponse(
                    output="Mock response",
                    model="mock-model",
                    input_tokens=10,
                    output_tokens=5,
                    cost=0.0,
                    provider="mock",
                    duration=0.1,
                )

        mock_client = MockLLMClient()
        result = builder.with_llm_config(mock_client)

        assert result is builder
        assert builder.llm_config == mock_client

    def test_with_extraction_prompt(self):
        """Test with_extraction_prompt method."""
        builder = ActionBuilder("test_action")

        prompt = "Extract the following parameters from the user input: {parameters}"
        result = builder.with_extraction_prompt(prompt)

        assert result is builder
        assert builder.extraction_prompt == prompt

    def test_with_context_inputs_list(self):
        """Test with_context_inputs method with list."""
        builder = ActionBuilder("test_action")

        inputs = ["user_id", "session_id", "preferences"]
        result = builder.with_context_inputs(inputs)

        assert result is builder
        assert builder.context_inputs == {"user_id", "session_id", "preferences"}

    def test_with_context_inputs_set(self):
        """Test with_context_inputs method with set."""
        builder = ActionBuilder("test_action")

        inputs = {"user_id", "session_id"}
        result = builder.with_context_inputs(inputs)

        assert result is builder
        assert builder.context_inputs == {"user_id", "session_id"}

    def test_with_context_inputs_tuple(self):
        """Test with_context_inputs method with tuple."""
        builder = ActionBuilder("test_action")

        inputs = ("user_id", "session_id")
        result = builder.with_context_inputs(inputs)

        assert result is builder
        assert builder.context_inputs == {"user_id", "session_id"}

    def test_with_context_outputs_list(self):
        """Test with_context_outputs method with list."""
        builder = ActionBuilder("test_action")

        outputs = ["result", "status", "message"]
        result = builder.with_context_outputs(outputs)

        assert result is builder
        assert builder.context_outputs == {"result", "status", "message"}

    def test_with_context_outputs_set(self):
        """Test with_context_outputs method with set."""
        builder = ActionBuilder("test_action")

        outputs = {"result", "status"}
        result = builder.with_context_outputs(outputs)

        assert result is builder
        assert builder.context_outputs == {"result", "status"}

    def test_with_context_outputs_tuple(self):
        """Test with_context_outputs method with tuple."""
        builder = ActionBuilder("test_action")

        outputs = ("result", "status")
        result = builder.with_context_outputs(outputs)

        assert result is builder
        assert builder.context_outputs == {"result", "status"}

    def test_with_input_validator(self):
        """Test with_input_validator method."""
        builder = ActionBuilder("test_action")

        def input_validator(params: Dict[str, Any]) -> bool:
            return "name" in params and "age" in params and params["age"] >= 18

        result = builder.with_input_validator(input_validator)

        assert result is builder
        assert builder.input_validator == input_validator

    def test_with_output_validator(self):
        """Test with_output_validator method."""
        builder = ActionBuilder("test_action")

        def output_validator(result: Any) -> bool:
            return isinstance(result, str) and len(result) > 0

        result = builder.with_output_validator(output_validator)

        assert result is builder
        assert builder.output_validator == output_validator

    def test_with_remediation_strategies_list(self):
        """Test with_remediation_strategies method with list."""
        builder = ActionBuilder("test_action")

        strategies = ["retry", "fallback", "ask_user"]
        result = builder.with_remediation_strategies(strategies)

        assert result is builder
        assert builder.remediation_strategies == ["retry", "fallback", "ask_user"]

    def test_with_remediation_strategies_tuple(self):
        """Test with_remediation_strategies method with tuple."""
        builder = ActionBuilder("test_action")

        strategies = ("retry", "fallback")
        result = builder.with_remediation_strategies(strategies)

        assert result is builder
        assert builder.remediation_strategies == ["retry", "fallback"]

    def test_with_remediation_strategies_set(self):
        """Test with_remediation_strategies method with set."""
        builder = ActionBuilder("test_action")

        strategies = {"retry", "fallback"}
        result = builder.with_remediation_strategies(strategies)

        assert result is builder
        # Set order is not guaranteed, so check length and content
        assert builder.remediation_strategies is not None
        assert len(builder.remediation_strategies) == 2
        assert "retry" in builder.remediation_strategies
        assert "fallback" in builder.remediation_strategies

    def test_builder_fluent_interface(self):
        """Test that all builder methods support fluent interface."""
        builder = ActionBuilder("test_action")

        def mock_action(name: str) -> str:
            return f"Hello {name}"

        def mock_validator(params: Dict[str, Any]) -> bool:
            return "name" in params

        result = (
            builder.with_action(mock_action)
            .with_param_schema({"name": str})
            .with_llm_config({"provider": "openai"})
            .with_extraction_prompt("Extract name")
            .with_context_inputs(["user_id"])
            .with_context_outputs(["result"])
            .with_input_validator(mock_validator)
            .with_output_validator(lambda x: isinstance(x, str))
            .with_remediation_strategies(["retry"])
        )

        assert result is builder
        assert builder.action_func == mock_action
        assert builder.param_schema == {"name": str}
        assert builder.llm_config == {"provider": "openai"}
        assert builder.extraction_prompt == "Extract name"
        assert builder.context_inputs == {"user_id"}
        assert builder.context_outputs == {"result"}
        assert builder.input_validator == mock_validator
        assert builder.output_validator is not None
        assert builder.remediation_strategies == ["retry"]

    def test_build_with_all_configurations(self):
        """Test building ActionNode with all configurations set."""
        builder = ActionBuilder("test_action")

        def mock_action(name: str, age: int) -> str:
            return f"Hello {name}, you are {age} years old"

        def mock_arg_extractor(user_input: str, context=None) -> Dict[str, Any]:
            return {"name": "Alice", "age": 30}

        def input_validator(params: Dict[str, Any]) -> bool:
            return "name" in params and "age" in params

        def output_validator(result: str) -> bool:
            return "Hello" in result

        action_node = (
            builder.with_action(mock_action)
            .with_param_schema({"name": str, "age": int})
            .with_llm_config({"provider": "openai"})
            .with_extraction_prompt("Extract name and age")
            .with_context_inputs(["user_id"])
            .with_context_outputs(["result"])
            .with_input_validator(input_validator)
            .with_output_validator(output_validator)
            .with_remediation_strategies(["retry", "fallback"])
            .build()
        )

        assert action_node.name == "test_action"
        assert action_node.action == mock_action
        assert action_node.param_schema == {"name": str, "age": int}
        assert action_node.context_inputs == {"user_id"}
        assert action_node.context_outputs == {"result"}
        assert action_node.input_validator == input_validator
        assert action_node.output_validator == output_validator
        assert action_node.remediation_strategies == ["retry", "fallback"]

    def test_from_json_with_llm_config(self):
        """Test from_json method with LLM config."""
        node_spec = {
            "id": "test_action",
            "name": "test_action",
            "description": "Test action",
            "function": "test_func",
            "param_schema": {"name": "str"},
            "llm_config": {"provider": "openai", "api_key": "test"},
            "context_inputs": ["user_id"],
            "context_outputs": ["result"],
            "remediation_strategies": ["retry"],
        }

        function_registry = {"test_func": lambda x: x}

        builder = ActionBuilder.from_json(node_spec, function_registry)

        assert builder.name == "test_action"
        assert builder.description == "Test action"
        assert builder.action_func == function_registry["test_func"]
        assert builder.llm_config == {"provider": "openai", "api_key": "test"}
        assert builder.context_inputs == {"user_id"}
        assert builder.context_outputs == {"result"}
        assert builder.remediation_strategies == ["retry"]

    def test_from_json_with_default_llm_config(self):
        """Test from_json method with default LLM config."""
        node_spec = {
            "id": "test_action",
            "name": "test_action",
            "description": "Test action",
            "function": "test_func",
            "param_schema": {"name": "str"},
        }

        function_registry = {"test_func": lambda x: x}
        default_llm_config = {"provider": "anthropic", "api_key": "default"}

        builder = ActionBuilder.from_json(
            node_spec, function_registry, default_llm_config
        )

        assert builder.llm_config == default_llm_config

    def test_from_json_with_callable_action(self):
        """Test from_json method with callable action."""

        def test_action(name: str) -> str:
            return f"Hello {name}"

        node_spec = {
            "id": "test_action",
            "name": "test_action",
            "description": "Test action",
            "function": test_action,
            "param_schema": {"name": "str"},
        }

        function_registry = {}

        builder = ActionBuilder.from_json(node_spec, function_registry)

        assert builder.action_func == test_action

    def test_from_json_missing_id_and_name(self):
        """Test from_json method with missing id and name."""
        node_spec = {
            "description": "Test action",
            "function": "test_func",
        }

        function_registry = {"test_func": lambda x: x}

        with pytest.raises(ValueError, match="must have 'id' or 'name'"):
            ActionBuilder.from_json(node_spec, function_registry)

    def test_from_json_function_not_found(self):
        """Test from_json method with function not in registry."""
        node_spec = {
            "id": "test_action",
            "name": "test_action",
            "description": "Test action",
            "function": "missing_func",
        }

        function_registry = {}

        with pytest.raises(ValueError, match="not found for node"):
            ActionBuilder.from_json(node_spec, function_registry)

    def test_from_json_invalid_function_type(self):
        """Test from_json method with invalid function type."""
        node_spec = {
            "id": "test_action",
            "name": "test_action",
            "description": "Test action",
            "function": 123,  # Not callable
        }

        function_registry = {}

        with pytest.raises(
            ValueError, match="must be a function name or callable object"
        ):
            ActionBuilder.from_json(node_spec, function_registry)
