"""
Tests for structured output functionality.
"""

from intent_kit.types import LLMResponse, StructuredLLMResponse


class TestStructuredOutput:
    """Test structured output functionality."""

    def test_llm_response_with_string_output(self):
        """Test LLMResponse with string output."""
        response = LLMResponse(
            output="Hello, world!",
            model="test-model",
            input_tokens=10,
            output_tokens=5,
            cost=0.01,
            provider="test-provider",
            duration=1.0,
        )

        assert response.output == "Hello, world!"
        assert response.get_string_output() == "Hello, world!"
        # Plain strings should be wrapped in a dict
        assert response.get_structured_output() == {"raw_content": "Hello, world!"}

    def test_llm_response_with_json_string(self):
        """Test LLMResponse with JSON string output."""
        json_str = '{"message": "Hello", "status": "success"}'
        response = LLMResponse(
            output=json_str,
            model="test-model",
            input_tokens=10,
            output_tokens=5,
            cost=0.01,
            provider="test-provider",
            duration=1.0,
        )

        assert response.output == json_str
        assert response.get_string_output() == json_str
        assert response.get_structured_output() == {
            "message": "Hello",
            "status": "success",
        }

    def test_llm_response_with_dict_output(self):
        """Test LLMResponse with dictionary output."""
        data = {"message": "Hello", "status": "success"}
        response = LLMResponse(
            output=data,
            model="test-model",
            input_tokens=10,
            output_tokens=5,
            cost=0.01,
            provider="test-provider",
            duration=1.0,
        )

        assert response.output == data
        assert response.get_structured_output() == data
        assert "message" in response.get_string_output()

    def test_structured_llm_response_with_string(self):
        """Test StructuredLLMResponse with string input."""
        response = StructuredLLMResponse(
            output='{"message": "Hello", "status": "success"}',
            model="test-model",
            input_tokens=10,
            output_tokens=5,
            cost=0.01,
            provider="test-provider",
            duration=1.0,
        )

        # Should be parsed as structured data
        assert isinstance(response.output, dict)
        assert response.output["message"] == "Hello"
        assert response.output["status"] == "success"

    def test_structured_llm_response_with_plain_string(self):
        """Test StructuredLLMResponse with plain string input."""
        response = StructuredLLMResponse(
            output="Hello, world!",
            model="test-model",
            input_tokens=10,
            output_tokens=5,
            cost=0.01,
            provider="test-provider",
            duration=1.0,
        )

        # Should be wrapped in a dict
        assert isinstance(response.output, dict)
        assert response.output["raw_content"] == "Hello, world!"

    def test_structured_llm_response_with_dict(self):
        """Test StructuredLLMResponse with dictionary input."""
        data = {"message": "Hello", "status": "success"}
        response = StructuredLLMResponse(
            output=data,
            model="test-model",
            input_tokens=10,
            output_tokens=5,
            cost=0.01,
            provider="test-provider",
            duration=1.0,
        )

        assert response.output == data

    def test_structured_llm_response_with_list(self):
        """Test StructuredLLMResponse with list input."""
        data = ["item1", "item2", "item3"]
        response = StructuredLLMResponse(
            output=data,
            model="test-model",
            input_tokens=10,
            output_tokens=5,
            cost=0.01,
            provider="test-provider",
            duration=1.0,
        )

        assert response.output == data

    def test_yaml_parsing_in_structured_response(self):
        """Test that YAML strings are parsed correctly."""
        yaml_str = """
        message: Hello
        status: success
        items:
          - item1
          - item2
        """

        response = StructuredLLMResponse(
            output=yaml_str,
            model="test-model",
            input_tokens=10,
            output_tokens=5,
            cost=0.01,
            provider="test-provider",
            duration=1.0,
        )

        assert isinstance(response.output, dict)
        assert response.output["message"] == "Hello"
        assert response.output["status"] == "success"
        assert response.output["items"] == ["item1", "item2"]

    def test_type_safety(self):
        """Test that type checking works correctly."""
        # This should work
        response = StructuredLLMResponse(
            output={"key": "value"},
            model="test-model",
            input_tokens=10,
            output_tokens=5,
            cost=0.01,
            provider="test-provider",
            duration=1.0,
        )

        # The output should always be structured
        assert isinstance(response.output, (dict, list))

        # We can access structured data safely
        if isinstance(response.output, dict):
            assert "key" in response.output
