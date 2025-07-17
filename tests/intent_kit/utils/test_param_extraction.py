"""
Tests for parameter extraction utilities.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Type

from intent_kit.utils.param_extraction import (
    parse_param_schema,
    create_rule_based_extractor,
    create_arg_extractor,
    _extract_name_parameter,
    _extract_location_parameter,
    _extract_calculation_parameters,
)


class TestParseParamSchema:
    """Test parameter schema parsing."""

    def test_parse_basic_types(self):
        """Test parsing of basic parameter types."""
        schema_data = {
            "name": "str",
            "age": "int",
            "height": "float",
            "is_active": "bool",
            "tags": "list",
            "metadata": "dict",
        }

        result = parse_param_schema(schema_data)

        assert result["name"] == str
        assert result["age"] == int
        assert result["height"] == float
        assert result["is_active"] == bool
        assert result["tags"] == list
        assert result["metadata"] == dict

    def test_parse_unknown_type(self):
        """Test that unknown types raise ValueError."""
        schema_data = {"invalid": "unknown_type"}

        with pytest.raises(ValueError, match="Unknown parameter type: unknown_type"):
            parse_param_schema(schema_data)

    def test_parse_empty_schema(self):
        """Test parsing empty schema."""
        result = parse_param_schema({})
        assert result == {}


class TestExtractNameParameter:
    """Test name parameter extraction."""

    def test_extract_single_name(self):
        """Test extracting single name."""
        input_text = "hello john"
        result = _extract_name_parameter(input_text)
        assert result == {"name": "John"}

    def test_extract_full_name(self):
        """Test extracting full name."""
        input_text = "hi john doe"
        result = _extract_name_parameter(input_text)
        assert result == {"name": "John Doe"}

    def test_extract_greet_command(self):
        """Test extracting name from greet command."""
        input_text = "greet alice"
        result = _extract_name_parameter(input_text)
        assert result == {"name": "Alice"}

    def test_no_name_found(self):
        """Test when no name is found."""
        input_text = "hello there"
        result = _extract_name_parameter(input_text)
        assert result == {"name": "User"}

    def test_case_insensitive(self):
        """Test case insensitive matching."""
        input_text = "HELLO BOB"
        result = _extract_name_parameter(input_text)
        assert result == {"name": "Bob"}


class TestExtractLocationParameter:
    """Test location parameter extraction."""

    def test_extract_weather_location(self):
        """Test extracting location from weather query."""
        input_text = "weather in new york"
        result = _extract_location_parameter(input_text)
        assert result == {"location": "New York"}

    def test_extract_location_with_in(self):
        """Test extracting location with 'in' keyword."""
        input_text = "what's the weather in london"
        result = _extract_location_parameter(input_text)
        assert result == {"location": "London"}

    def test_no_location_found(self):
        """Test when no location is found."""
        input_text = "what's the weather like"
        result = _extract_location_parameter(input_text)
        assert result == {"location": "Unknown"}

    def test_case_insensitive(self):
        """Test case insensitive matching."""
        input_text = "WEATHER IN PARIS"
        result = _extract_location_parameter(input_text)
        assert result == {"location": "Paris"}


class TestExtractCalculationParameters:
    """Test calculation parameter extraction."""

    def test_extract_addition(self):
        """Test extracting addition parameters."""
        input_text = "what's 5 plus 3"
        result = _extract_calculation_parameters(input_text)
        assert result == {"a": 5.0, "operation": "plus", "b": 3.0}

    def test_extract_subtraction(self):
        """Test extracting subtraction parameters."""
        input_text = "10 minus 4"
        result = _extract_calculation_parameters(input_text)
        assert result == {"a": 10.0, "operation": "minus", "b": 4.0}

    def test_extract_multiplication(self):
        """Test extracting multiplication parameters."""
        input_text = "6 times 7"
        result = _extract_calculation_parameters(input_text)
        assert result == {"a": 6.0, "operation": "times", "b": 7.0}

    def test_extract_division(self):
        """Test extracting division parameters."""
        input_text = "15 divided by 3"
        result = _extract_calculation_parameters(input_text)
        assert result == {"a": 15.0, "operation": "divided", "b": 3.0}

    def test_extract_decimal_numbers(self):
        """Test extracting decimal numbers."""
        input_text = "3.5 plus 2.1"
        result = _extract_calculation_parameters(input_text)
        assert result == {"a": 3.5, "operation": "plus", "b": 2.1}

    def test_no_calculation_found(self):
        """Test when no calculation is found."""
        input_text = "hello world"
        result = _extract_calculation_parameters(input_text)
        assert result == {}


class TestCreateRuleBasedExtractor:
    """Test rule-based extractor creation."""

    def test_create_extractor_with_name_param(self):
        """Test creating extractor with name parameter."""
        param_schema = {"name": str}
        extractor = create_rule_based_extractor(param_schema)

        result = extractor("hello john", {})
        assert result == {"name": "John"}

    def test_create_extractor_with_location_param(self):
        """Test creating extractor with location parameter."""
        param_schema = {"location": str}
        extractor = create_rule_based_extractor(param_schema)

        result = extractor("weather in tokyo", {})
        assert result == {"location": "Tokyo"}

    def test_create_extractor_with_calculation_params(self):
        """Test creating extractor with calculation parameters."""
        param_schema = {"a": float, "operation": str, "b": float}
        extractor = create_rule_based_extractor(param_schema)

        result = extractor("10 plus 5", {})
        assert result == {"a": 10.0, "operation": "plus", "b": 5.0}

    def test_create_extractor_with_multiple_params(self):
        """Test creating extractor with multiple parameters."""
        param_schema = {"name": str, "location": str}
        extractor = create_rule_based_extractor(param_schema)

        result = extractor("hello john, weather in paris", {})
        assert result == {"name": "John", "location": "Paris"}

    def test_create_extractor_with_context(self):
        """Test creating extractor with context parameter."""
        param_schema = {"name": str}
        extractor = create_rule_based_extractor(param_schema)

        context = {"user_id": "123"}
        result = extractor("hello alice", context)
        assert result == {"name": "Alice"}

    def test_create_extractor_no_matching_params(self):
        """Test creating extractor with no matching parameters."""
        param_schema = {"unknown": str}
        extractor = create_rule_based_extractor(param_schema)

        result = extractor("hello world", {})
        assert result == {}


class TestCreateArgExtractor:
    """Test argument extractor creation."""

    def test_create_rule_based_extractor(self):
        """Test creating rule-based extractor when no LLM config provided."""
        param_schema = {"name": str}
        extractor = create_arg_extractor(param_schema)

        result = extractor("hello john", {})
        assert result == {"name": "John"}

    @patch("intent_kit.utils.param_extraction.create_llm_arg_extractor")
    @patch("intent_kit.utils.param_extraction.get_default_extraction_prompt")
    def test_create_llm_extractor(self, mock_get_prompt, mock_create_llm_extractor):
        """Test creating LLM-based extractor."""
        param_schema = {"name": str}
        llm_config = {"model": "gpt-3.5-turbo"}
        mock_extractor = Mock()
        mock_create_llm_extractor.return_value = mock_extractor
        mock_get_prompt.return_value = "Extract parameters"

        extractor = create_arg_extractor(param_schema, llm_config)

        mock_create_llm_extractor.assert_called_once_with(
            llm_config, "Extract parameters", param_schema
        )
        assert extractor == mock_extractor

    @patch("intent_kit.utils.param_extraction.create_llm_arg_extractor")
    def test_create_llm_extractor_with_custom_prompt(self, mock_create_llm_extractor):
        """Test creating LLM-based extractor with custom prompt."""
        param_schema = {"name": str}
        llm_config = {"model": "gpt-3.5-turbo"}
        custom_prompt = "Custom extraction prompt"
        mock_extractor = Mock()
        mock_create_llm_extractor.return_value = mock_extractor

        extractor = create_arg_extractor(
            param_schema, llm_config, extraction_prompt=custom_prompt
        )

        mock_create_llm_extractor.assert_called_once_with(
            llm_config, custom_prompt, param_schema
        )
        assert extractor == mock_extractor

    def test_create_extractor_with_node_name(self):
        """Test creating extractor with node name for logging."""
        param_schema = {"name": str}
        extractor = create_arg_extractor(param_schema, node_name="test_node")

        result = extractor("hello john", {})
        assert result == {"name": "John"}

    def test_create_extractor_empty_schema(self):
        """Test creating extractor with empty schema."""
        param_schema = {}
        extractor = create_arg_extractor(param_schema)

        result = extractor("hello world", {})
        assert result == {}