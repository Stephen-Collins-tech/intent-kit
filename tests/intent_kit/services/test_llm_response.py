"""
Tests for LLM response classes.
"""

from intent_kit.services.ai.llm_response import (
    LLMResponse,
    RawLLMResponse,
    StructuredLLMResponse,
)
import pytest
from unittest.mock import patch


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

    def test_llm_response_get_structured_output_invalid_json(self):
        """Test get_structured_output with invalid JSON."""
        invalid_json = '{"message": "Hello", "status":}'  # Missing value
        response = LLMResponse(
            output=invalid_json,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        structured = response.get_structured_output()
        assert isinstance(structured, dict)
        # The implementation is robust and can parse partial JSON
        assert structured["message"] == "Hello"
        assert structured["status"] is None

    @patch("intent_kit.services.ai.llm_response.yaml")
    def test_llm_response_get_structured_output_yaml(self, mock_yaml):
        """Test get_structured_output with YAML parsing."""
        yaml_str = "message: Hello\nstatus: success"
        mock_yaml.safe_load.return_value = {"message": "Hello", "status": "success"}

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

    def test_llm_response_get_structured_output_yaml_error(self):
        """Test get_structured_output with YAML parsing error."""
        # Use a string that looks like YAML but has a syntax error
        yaml_str = "message: Hello\nstatus: success\n  invalid: indentation"

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
        # When YAML parsing fails, it should fall back to raw_content
        assert structured["raw_content"] == yaml_str

    @patch("intent_kit.services.ai.llm_response.yaml", None)
    def test_llm_response_get_structured_output_no_yaml(self):
        """Test get_structured_output when YAML is not available."""
        yaml_str = "message: Hello\nstatus: success"
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
        assert structured["raw_content"] == yaml_str

    def test_llm_response_get_structured_output_non_dict_yaml(self):
        """Test get_structured_output with YAML that doesn't parse to dict/list."""
        response = LLMResponse(
            output="simple string",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        structured = response.get_structured_output()
        assert isinstance(structured, dict)
        assert structured["raw_content"] == "simple string"

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
        assert '"message": "Hello"' in string_output
        assert '"status": "success"' in string_output

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
        assert '"item1"' in string_output
        assert '"item2"' in string_output
        assert '"item3"' in string_output

    def test_llm_response_get_string_output_non_jsonable(self):
        """Test get_string_output with non-JSON-serializable object."""

        class NonJsonable:
            def __str__(self):
                return "custom string representation"

        non_jsonable = NonJsonable()
        response = LLMResponse(
            output=non_jsonable,
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            cost=0.01,
            provider="openai",
            duration=1.5,
        )

        # The implementation tries json.dumps which will fail for non-JSON-serializable objects
        with pytest.raises(
            TypeError, match="Object of type NonJsonable is not JSON serializable"
        ):
            response.get_string_output()


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
        )

        assert response.content == "Hello, world!"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.input_tokens == 100
        assert response.output_tokens == 50
        assert response.cost == 0.01
        assert response.duration == 1.5
        assert response.metadata == {}

    def test_raw_llm_response_creation_with_metadata(self):
        """Test creating a RawLLMResponse instance with metadata."""
        metadata = {"key": "value", "nested": {"data": "test"}}
        response = RawLLMResponse(
            content="Hello, world!",
            model="gpt-4",
            provider="openai",
            metadata=metadata,
        )

        assert response.metadata == metadata

    def test_raw_llm_response_total_tokens_with_values(self):
        """Test total_tokens property when both input and output tokens are available."""
        response = RawLLMResponse(
            content="Hello, world!",
            model="gpt-4",
            provider="openai",
            input_tokens=100,
            output_tokens=50,
        )

        assert response.total_tokens == 150

    def test_raw_llm_response_total_tokens_missing_input(self):
        """Test total_tokens property when input_tokens is missing."""
        response = RawLLMResponse(
            content="Hello, world!",
            model="gpt-4",
            provider="openai",
            output_tokens=50,
        )

        assert response.total_tokens is None

    def test_raw_llm_response_total_tokens_missing_output(self):
        """Test total_tokens property when output_tokens is missing."""
        response = RawLLMResponse(
            content="Hello, world!",
            model="gpt-4",
            provider="openai",
            input_tokens=100,
        )

        assert response.total_tokens is None

    def test_raw_llm_response_total_tokens_missing_both(self):
        """Test total_tokens property when both tokens are missing."""
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

        validated = structured.get_validated_output()
        assert isinstance(validated, dict)
        assert validated["message"] == "Hello"
        assert validated["status"] == "success"

    def test_raw_llm_response_to_structured_response_with_defaults(self):
        """Test converting to StructuredLLMResponse with default values."""
        response = RawLLMResponse(
            content="Hello, world!",
            model="gpt-4",
            provider="openai",
        )

        structured = response.to_structured_response(str)
        assert isinstance(structured, StructuredLLMResponse)
        assert structured.model == "gpt-4"
        assert structured.provider == "openai"
        assert structured.input_tokens == 0
        assert structured.output_tokens == 0
        assert structured.cost == 0.0
        assert structured.duration == 0.0

        validated = structured.get_validated_output()
        assert validated == "Hello, world!"


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

    def test_structured_llm_response_parse_string_to_structured_json(self):
        """Test _parse_string_to_structured with JSON."""
        response = StructuredLLMResponse(
            output='{"message": "Hello"}',
            model="gpt-4",
            provider="openai",
        )

        result = response._parse_string_to_structured('{"message": "Hello"}')
        assert isinstance(result, dict)
        assert result["message"] == "Hello"

    def test_structured_llm_response_parse_string_to_structured_json_block(self):
        """Test _parse_string_to_structured with JSON in code block."""
        response = StructuredLLMResponse(
            output='```json\n{"message": "Hello"}\n```',
            model="gpt-4",
            provider="openai",
        )

        result = response._parse_string_to_structured(
            '```json\n{"message": "Hello"}\n```'
        )
        assert isinstance(result, dict)
        assert result["message"] == "Hello"

    def test_structured_llm_response_parse_string_to_structured_generic_block(self):
        """Test _parse_string_to_structured with generic code block."""
        response = StructuredLLMResponse(
            output='```\n{"message": "Hello"}\n```',
            model="gpt-4",
            provider="openai",
        )

        result = response._parse_string_to_structured('```\n{"message": "Hello"}\n```')
        assert isinstance(result, dict)
        assert result["message"] == "Hello"

    def test_structured_llm_response_parse_string_to_structured_invalid_json(self):
        """Test _parse_string_to_structured with invalid JSON."""
        response = StructuredLLMResponse(
            output='{"message": "Hello", "status":}',  # Invalid JSON
            model="gpt-4",
            provider="openai",
        )

        result = response._parse_string_to_structured('{"message": "Hello", "status":}')
        assert isinstance(result, dict)
        # The implementation is robust and can parse partial JSON
        assert result["message"] == "Hello"
        assert result["status"] is None

    @patch("intent_kit.services.ai.llm_response.yaml")
    def test_structured_llm_response_parse_string_to_structured_yaml(self, mock_yaml):
        """Test _parse_string_to_structured with YAML."""
        mock_yaml.safe_load.return_value = {"message": "Hello", "status": "success"}

        response = StructuredLLMResponse(
            output="message: Hello\nstatus: success",
            model="gpt-4",
            provider="openai",
        )

        result = response._parse_string_to_structured("message: Hello\nstatus: success")
        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"

    def test_structured_llm_response_parse_string_to_structured_yaml_error(self):
        """Test _parse_string_to_structured with YAML parsing error."""
        # Use a string that looks like YAML but has a syntax error
        yaml_str = "message: Hello\nstatus: success\n  invalid: indentation"

        response = StructuredLLMResponse(
            output=yaml_str,
            model="gpt-4",
            provider="openai",
        )

        result = response._parse_string_to_structured(yaml_str)
        assert isinstance(result, dict)
        # When YAML parsing fails, it should fall back to raw_content
        assert result["raw_content"] == yaml_str

    def test_structured_llm_response_convert_to_expected_type_dict(self):
        """Test _convert_to_expected_type with dict expected type."""
        response = StructuredLLMResponse(
            output="Hello, world!",
            model="gpt-4",
            provider="openai",
        )

        result = response._convert_to_expected_type("Hello, world!", dict)
        assert isinstance(result, dict)
        assert result["raw_content"] == "Hello, world!"

    def test_structured_llm_response_convert_to_expected_type_list(self):
        """Test _convert_to_expected_type with list expected type."""
        response = StructuredLLMResponse(
            output={"key1": "value1", "key2": "value2"},
            model="gpt-4",
            provider="openai",
        )

        result = response._convert_to_expected_type(
            {"key1": "value1", "key2": "value2"}, list
        )
        assert isinstance(result, list)
        assert "value1" in result
        assert "value2" in result

    def test_structured_llm_response_convert_to_expected_type_str(self):
        """Test _convert_to_expected_type with str expected type."""
        response = StructuredLLMResponse(
            output={"message": "Hello"},
            model="gpt-4",
            provider="openai",
        )

        result = response._convert_to_expected_type({"message": "Hello"}, str)
        assert isinstance(result, str)
        assert '"message": "Hello"' in result

    def test_structured_llm_response_convert_to_expected_type_int(self):
        """Test _convert_to_expected_type with int expected type."""
        response = StructuredLLMResponse(
            output="The number is 42",
            model="gpt-4",
            provider="openai",
        )

        result = response._convert_to_expected_type("The number is 42", int)
        assert isinstance(result, int)
        assert result == 42

    def test_structured_llm_response_convert_to_expected_type_float(self):
        """Test _convert_to_expected_type with float expected type."""
        response = StructuredLLMResponse(
            output="The price is 19.99",
            model="gpt-4",
            provider="openai",
        )

        result = response._convert_to_expected_type("The price is 19.99", float)
        assert isinstance(result, float)
        assert result == 19.99

    def test_structured_llm_response_convert_to_expected_type_already_correct(self):
        """Test _convert_to_expected_type when data is already correct type."""
        response = StructuredLLMResponse(
            output={"message": "Hello"},
            model="gpt-4",
            provider="openai",
        )

        result = response._convert_to_expected_type({"message": "Hello"}, dict)
        assert isinstance(result, dict)
        assert result["message"] == "Hello"

    def test_structured_llm_response_validation_error_handling(self):
        """Test handling of validation errors in StructuredLLMResponse."""
        # Use a truly invalid JSON that can't be parsed at all
        response = StructuredLLMResponse(
            output='{"message": "Hello", "status":}',  # Invalid JSON
            expected_type=str,  # Force it to be treated as string
            model="gpt-4",
            provider="openai",
        )

        # The output should be the raw string since expected_type is str
        assert isinstance(response.output, str)
        assert response.output == '{"message": "Hello", "status":}'

    def test_structured_llm_response_get_validated_output_with_validation_error(self):
        """Test get_validated_output when validation failed."""
        # Create a response with a validation error by using a complex type
        response = StructuredLLMResponse(
            output='{"message": "Hello", "status": "success"}',
            expected_type=list,  # This will cause a validation error
            model="gpt-4",
            provider="openai",
        )

        # Should raise an exception when trying to get validated output
        with pytest.raises(Exception):
            response.get_validated_output()

    def test_structured_llm_response_with_complex_nested_data(self):
        """Test StructuredLLMResponse with complex nested data."""
        complex_data = {
            "user": {
                "name": "John Doe",
                "preferences": {"theme": "dark", "notifications": True},
            },
            "items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
        }

        response = StructuredLLMResponse(
            output=complex_data,
            expected_type=dict,
            model="gpt-4",
            provider="openai",
        )

        validated = response.get_validated_output()
        assert validated == complex_data
        assert validated["user"]["name"] == "John Doe"  # type: ignore
        assert len(validated["items"]) == 2  # type: ignore

    def test_structured_llm_response_with_empty_data(self):
        """Test StructuredLLMResponse with empty data."""
        response = StructuredLLMResponse(
            output="",
            expected_type=str,
            model="gpt-4",
            provider="openai",
        )

        validated = response.get_validated_output()
        assert validated == ""

    def test_structured_llm_response_with_none_data(self):
        """Test StructuredLLMResponse with None data."""
        response = StructuredLLMResponse(
            output=None,
            model="gpt-4",
            provider="openai",
        )

        # Should handle None gracefully
        assert response.output is None or isinstance(response.output, dict)

    def test_structured_llm_response_edge_cases(self):
        """Test StructuredLLMResponse with various edge cases."""
        # Test with very long string
        long_string = "x" * 10000
        response = StructuredLLMResponse(
            output=long_string,
            expected_type=str,
            model="gpt-4",
            provider="openai",
        )
        assert response.get_validated_output() == long_string

        # Test with special characters
        special_chars = '{"message": "Hello World\\tTab\\rReturn"}'
        response = StructuredLLMResponse(
            output=special_chars,
            expected_type=dict,
            model="gpt-4",
            provider="openai",
        )
        validated = response.get_validated_output()
        assert isinstance(validated, dict)
        assert "Hello World\tTab\rReturn" in validated["message"]
