"""
Tests for LLM response classes.
"""

from intent_kit.services.ai.llm_response import (
    LLMResponse,
    RawLLMResponse,
    StructuredLLMResponse,
)


class TestLLMResponse:
    """Test the LLMResponse dataclass."""

    def test_llm_response_creation(self):
        """Test creating an LLMResponse instance."""
        response = LLMResponse(
            output="Hello, world!",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        assert response.output == "Hello, world!"
        assert response.model == "gpt-4"
        assert response.input_tokens == 100
        assert response.output_tokens == 50
        assert response.cost == 0.01
        assert response.provider == "openai"
        assert response.duration == 1.5

    def test_llm_response_total_tokens(self):
        """Test the total_tokens property."""
        response = LLMResponse(
            output="Hello, world!",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        assert response.total_tokens == 150

    def test_llm_response_get_structured_output_string(self):
        """Test get_structured_output with string output."""
        response = LLMResponse(
            output="Hello, world!",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        structured = response.get_structured_output()
        assert isinstance(structured, dict)
        assert structured["raw_content"] == "Hello, world!"

    def test_llm_response_get_structured_output_json(self):
        """Test get_structured_output with JSON string."""
        json_str = '{"message": "Hello", "status": "success"}'
        response = LLMResponse(
            output=json_str,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        structured = response.get_structured_output()
        assert isinstance(structured, dict)
        assert structured["message"] == "Hello"
        assert structured["status"] == "success"

    def test_llm_response_get_structured_output_dict(self):
        """Test get_structured_output with dict output."""
        data = {"message": "Hello", "status": "success"}
        response = LLMResponse(
            output=data,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        structured = response.get_structured_output()
        assert structured == data

    def test_llm_response_get_structured_output_list(self):
        """Test get_structured_output with list output."""
        data = ["item1", "item2", "item3"]
        response = LLMResponse(
            output=data,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        structured = response.get_structured_output()
        assert structured == data

    def test_llm_response_get_structured_output_yaml(self):
        """Test get_structured_output with YAML string."""
        yaml_str = """
        message: Hello
        status: success
        items:
          - item1
          - item2
        """
        response = LLMResponse(
            output=yaml_str,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        structured = response.get_structured_output()
        assert isinstance(structured, dict)
        assert structured["message"] == "Hello"
        assert structured["status"] == "success"
        assert structured["items"] == ["item1", "item2"]

    def test_llm_response_get_structured_output_yaml_scalar(self):
        """Test get_structured_output with YAML scalar (non-dict/list)."""
        yaml_str = "Hello, world!"
        response = LLMResponse(
            output=yaml_str,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        structured = response.get_structured_output()
        assert isinstance(structured, dict)
        assert structured["raw_content"] == "Hello, world!"

    def test_llm_response_get_structured_output_non_string_non_dict(self):
        """Test get_structured_output with non-string, non-dict output."""
        response = LLMResponse(
            output=123,  # Integer
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        structured = response.get_structured_output()
        assert isinstance(structured, dict)
        assert structured["raw_content"] == "123"

    def test_llm_response_get_string_output_string(self):
        """Test get_string_output with string output."""
        response = LLMResponse(
            output="Hello, world!",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        string_output = response.get_string_output()
        assert string_output == "Hello, world!"

    def test_llm_response_get_string_output_dict(self):
        """Test get_string_output with dict output."""
        data = {"message": "Hello", "status": "success"}
        response = LLMResponse(
            output=data,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        string_output = response.get_string_output()
        assert "message" in string_output
        assert "Hello" in string_output

    def test_llm_response_get_string_output_list(self):
        """Test get_string_output with list output."""
        data = ["item1", "item2", "item3"]
        response = LLMResponse(
            output=data,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        string_output = response.get_string_output()
        assert "item1" in string_output
        assert "item2" in string_output
        assert "item3" in string_output


class TestRawLLMResponse:
    """Test the RawLLMResponse dataclass."""

    def test_raw_llm_response_creation(self):
        """Test creating a RawLLMResponse instance."""
        response = RawLLMResponse(
            content="Hello, world!",
            model="gpt-4",
            provider="openai",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            duration=1.5,
            metadata={"key": "value"},
        )

        assert response.content == "Hello, world!"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.input_tokens == 100
        assert response.output_tokens == 50
        assert response.cost == 0.01
        assert response.duration == 1.5
        assert response.metadata == {"key": "value"}

    def test_raw_llm_response_defaults(self):
        """Test RawLLMResponse with default values."""
        response = RawLLMResponse(
            content="Hello, world!",
            model="gpt-4",
            provider="openai",
        )

        assert response.content == "Hello, world!"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.input_tokens is None
        assert response.output_tokens is None
        assert response.cost is None
        assert response.duration is None
        assert response.metadata == {}

    def test_raw_llm_response_total_tokens_with_values(self):
        """Test total_tokens property when both input and output tokens are set."""
        response = RawLLMResponse(
            content="Hello, world!",
            model="gpt-4",
            provider="openai",
            input_tokens=100,
            output_tokens=50,
        )

        assert response.total_tokens == 150

    def test_raw_llm_response_total_tokens_missing(self):
        """Test total_tokens property when tokens are missing."""
        response = RawLLMResponse(
            content="Hello, world!",
            model="gpt-4",
            provider="openai",
        )

        assert response.total_tokens is None

    def test_raw_llm_response_to_structured_response(self):
        """Test converting to StructuredLLMResponse."""
        response = RawLLMResponse(
            content='{"message": "Hello", "status": "success"}',
            model="gpt-4",
            provider="openai",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            duration=1.5,
        )

        structured = response.to_structured_response(dict)
        assert isinstance(structured, StructuredLLMResponse)
        assert structured.model == "gpt-4"
        assert structured.provider == "openai"
        assert structured.input_tokens == 100
        assert structured.output_tokens == 50
        assert structured.cost == 0.01
        assert structured.duration == 1.5


class TestStructuredLLMResponse:
    """Test the StructuredLLMResponse class."""

    def test_structured_llm_response_creation_with_string(self):
        """Test creating StructuredLLMResponse with string input."""
        response = StructuredLLMResponse(
            output='{"message": "Hello", "status": "success"}',
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        assert isinstance(response.output, dict)
        assert response.output["message"] == "Hello"
        assert response.output["status"] == "success"

    def test_structured_llm_response_creation_with_dict(self):
        """Test creating StructuredLLMResponse with dict input."""
        data = {"message": "Hello", "status": "success"}
        response = StructuredLLMResponse(
            output=data,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        assert response.output == data

    def test_structured_llm_response_with_type_validation(self):
        """Test StructuredLLMResponse with type validation."""
        response = StructuredLLMResponse(
            output='{"message": "Hello", "status": "success"}',
            expected_type=dict,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        validated = response.get_validated_output()
        assert isinstance(validated, dict)
        assert validated["message"] == "Hello"

    def test_structured_llm_response_from_llm_response(self):
        """Test creating StructuredLLMResponse from LLMResponse."""
        llm_response = LLMResponse(
            output='{"message": "Hello", "status": "success"}',
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        structured = StructuredLLMResponse.from_llm_response(llm_response, dict)
        assert isinstance(structured, StructuredLLMResponse)
        assert structured.model == "gpt-4"
        assert structured.provider == "openai"

    def test_structured_llm_response_with_string_expected_type(self):
        """Test StructuredLLMResponse with string expected type."""
        response = StructuredLLMResponse(
            output="Hello, world!",
            expected_type=str,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        assert response.output == "Hello, world!"

    def test_structured_llm_response_with_list_input(self):
        """Test StructuredLLMResponse with list input."""
        data = ["item1", "item2", "item3"]
        response = StructuredLLMResponse(
            output=data,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        assert response.output == data

    def test_structured_llm_response_get_validated_output_no_type(self):
        """Test get_validated_output when no expected_type is set."""
        response = StructuredLLMResponse(
            output={"message": "Hello", "status": "success"},
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        validated = response.get_validated_output()
        assert validated == {"message": "Hello", "status": "success"}
