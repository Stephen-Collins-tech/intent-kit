"""
Tests for text utilities module.
"""

from intent_kit.utils.text_utils import TextUtil
import json


class TestTextUtils:
    """Test cases for text utilities."""

    def test_extract_json_from_text_valid_json(self):
        """Test extracting valid JSON from text."""
        text = 'Here is the response: {"key": "value", "number": 42}'
        result = TextUtil.extract_json_from_text(text)
        assert result == {"key": "value", "number": 42}

    def test_extract_json_from_text_invalid_json(self):
        """Test extracting invalid JSON from text."""
        text = "Here is the response: {key: value, number: 42}"
        result = TextUtil.extract_json_from_text(text)
        assert result == {"key": "value", "number": 42}

    def test_extract_json_from_text_with_code_blocks(self):
        """Test extracting JSON from text with code blocks."""
        text = '```json\n{"key": "value"}\n```'
        result = TextUtil.extract_json_from_text(text)
        assert result == {"key": "value"}

    def test_extract_json_from_text_no_json(self):
        """Test extracting JSON when none exists."""
        text = "This is just plain text"
        result = TextUtil.extract_json_from_text(text)
        assert result is None

    def test_extract_json_array_from_text_valid_array(self):
        """Test extracting valid JSON array from text."""
        text = 'Here are the items: ["item1", "item2", "item3"]'
        result = TextUtil.extract_json_array_from_text(text)
        assert result == ["item1", "item2", "item3"]

    def test_extract_json_array_from_text_manual_extraction(self):
        """Test manual extraction of array-like data."""
        text = "1. First item\n2. Second item\n3. Third item"
        result = TextUtil.extract_json_array_from_text(text)
        assert result == ["First item", "Second item", "Third item"]

    def test_extract_json_array_from_text_dash_items(self):
        """Test extracting dash-separated items."""
        text = "- Item one\n- Item two\n- Item three"
        result = TextUtil.extract_json_array_from_text(text)
        assert result == ["Item one", "Item two", "Item three"]

    def test_extract_key_value_pairs_quoted_keys(self):
        """Test extracting key-value pairs with quoted keys."""
        text = '"name": "John", "age": 30, "active": true'
        result = TextUtil.extract_key_value_pairs(text)
        assert result == {"name": "John", "age": 30, "active": True}

    def test_extract_key_value_pairs_unquoted_keys(self):
        """Test extracting key-value pairs with unquoted keys."""
        text = "name: John, age: 30, active: true"
        result = TextUtil.extract_key_value_pairs(text)
        assert result == {"name": "John", "age": 30, "active": True}

    def test_extract_key_value_pairs_equals_sign(self):
        """Test extracting key-value pairs with equals sign."""
        text = "name = John, age = 30, active = true"
        result = TextUtil.extract_key_value_pairs(text)
        assert result == {"name": "John", "age": 30, "active": True}

    def test_is_deserializable_json_valid(self):
        """Test checking valid JSON."""
        text = '{"key": "value"}'
        result = TextUtil.is_deserializable_json(text)
        assert result is True

    def test_is_deserializable_json_invalid(self):
        """Test checking invalid JSON."""
        text = "{key: value}"
        result = TextUtil.is_deserializable_json(text)
        assert result is False

    def test_is_deserializable_json_empty(self):
        """Test checking empty text."""
        result = TextUtil.is_deserializable_json("")
        assert result is False

    def test_clean_for_deserialization_code_blocks(self):
        """Test cleaning code blocks from text."""
        text = '```json\n{"key": "value"}\n```'
        result = TextUtil.clean_for_deserialization(text)
        assert result == '{"key": "value"}'

    def test_clean_for_deserialization_unquoted_keys(self):
        """Test cleaning unquoted keys."""
        text = '{key: "value", number: 42}'
        result = TextUtil.clean_for_deserialization(text)
        # Compare as JSON objects to ignore whitespace
        assert json.loads(result) == {"key": "value", "number": 42}

    def test_clean_for_deserialization_trailing_commas(self):
        """Test cleaning trailing commas."""
        text = '{"key": "value", "number": 42,}'
        result = TextUtil.clean_for_deserialization(text)
        assert result == '{"key": "value", "number": 42}'

    def test_extract_structured_data_json_object(self):
        """Test extracting structured data as JSON object."""
        text = '{"key": "value", "number": 42}'
        data, method = TextUtil.extract_structured_data(text, "dict")
        assert data == {"key": "value", "number": 42}
        assert method == "json_object"

    def test_extract_structured_data_json_array(self):
        """Test extracting structured data as JSON array."""
        text = '["item1", "item2"]'
        data, method = TextUtil.extract_structured_data(text, "list")
        assert data == ["item1", "item2"]
        assert method == "json_array"

    def test_extract_structured_data_manual_object(self):
        """Test extracting structured data with manual object extraction."""
        text = "key: value, number: 42"
        data, method = TextUtil.extract_structured_data(text, "dict")
        assert data == {"key": "value", "number": 42}
        assert method == "manual_object"

    def test_extract_structured_data_manual_array(self):
        """Test extracting structured data with manual array extraction."""
        text = "1. Item one\n2. Item two"
        data, method = TextUtil.extract_structured_data(text, "list")
        assert data == ["Item one", "Item two"]
        assert method == "manual_array"

    def test_extract_structured_data_string(self):
        """Test extracting structured data as string."""
        text = "This is a simple string"
        data, method = TextUtil.extract_structured_data(text, "string")
        assert data == "This is a simple string"
        assert method == "string"

    def test_extract_structured_data_auto_detection(self):
        """Test automatic type detection."""
        # Test JSON object
        text = '{"key": "value"}'
        data, method = TextUtil.extract_structured_data(text)
        assert data == {"key": "value"}
        assert method == "json_object"

        # Test JSON array
        text = '["item1", "item2"]'
        data, method = TextUtil.extract_structured_data(text)
        assert data == ["item1", "item2"]
        assert method == "json_array"

    def test_validate_json_structure_valid(self):
        """Test validating valid JSON structure."""
        data = {"name": "John", "age": 30}
        result = TextUtil.validate_json_structure(data, ["name", "age"])
        assert result is True

    def test_validate_json_structure_missing_keys(self):
        """Test validating JSON structure with missing keys."""
        data = {"name": "John"}
        result = TextUtil.validate_json_structure(data, ["name", "age"])
        assert result is False

    def test_validate_json_structure_no_required_keys(self):
        """Test validating JSON structure without required keys."""
        data = {"name": "John", "age": 30}
        result = TextUtil.validate_json_structure(data)
        assert result is True

    def test_validate_json_structure_none_data(self):
        """Test validating JSON structure with None data."""
        result = TextUtil.validate_json_structure(None)
        assert result is False

    def test_edge_cases_empty_string(self):
        """Test edge cases with empty strings."""
        result = TextUtil.extract_json_from_text("")
        assert result is None

        result = TextUtil.extract_json_array_from_text("")
        assert result is None

        result = TextUtil.extract_key_value_pairs("")
        assert result == {}

    def test_edge_cases_none_input(self):
        """Test edge cases with None input."""
        result = TextUtil.extract_json_from_text(None)
        assert result is None

        result = TextUtil.extract_json_array_from_text(None)
        assert result is None

        result = TextUtil.extract_key_value_pairs(None)
        assert result == {}

    def test_edge_cases_non_string_input(self):
        """Test edge cases with non-string input."""
        result = TextUtil.extract_json_from_text(str(123))
        assert result is None

        result = TextUtil.extract_json_array_from_text(str(123))
        assert result is None

        result = TextUtil.extract_key_value_pairs(str(123))
        assert result == {}

    def test_extract_json_from_text_json_block(self):
        text = """Here is a block:
        ```json
        {"foo": "bar", "num": 123}
        ```
        """
        result = TextUtil.extract_json_from_text(text)
        assert result == {"foo": "bar", "num": 123}

    def test_extract_json_array_from_text_json_block(self):
        text = """Some output:
        ```json
        ["a", "b", "c"]
        ```
        """
        result = TextUtil.extract_json_array_from_text(text)
        assert result == ["a", "b", "c"]

    def test_extract_json_from_text_json_block_malformed(self):
        text = """```json\n{"foo": "bar", "num": }```"""
        result = TextUtil.extract_json_from_text(text)
        assert result == {"foo": "bar", "num": ""}
