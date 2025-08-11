"""
Tests for TypedOutputData functionality.
"""

from intent_kit.types import TypedOutputData, TypedOutputType


class TestTypedOutputData:
    """Test TypedOutputData functionality."""

    def test_auto_detect_json(self):
        """Test auto-detection of JSON content."""
        json_str = '{"message": "Hello", "status": "success"}'
        typed_output = TypedOutputData(content=json_str, type=TypedOutputType.AUTO)
        result = typed_output.get_typed_content()

        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"

    def test_auto_detect_plain_string(self):
        """Test auto-detection of plain string content."""
        typed_output = TypedOutputData(
            content="Hello, world!", type=TypedOutputType.AUTO
        )
        result = typed_output.get_typed_content()

        assert isinstance(result, dict)
        assert result["raw_content"] == "Hello, world!"

    def test_cast_to_json(self):
        """Test casting to JSON format."""
        json_str = '{"message": "Hello", "status": "success"}'
        typed_output = TypedOutputData(content=json_str, type=TypedOutputType.JSON)
        result = typed_output.get_typed_content()

        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"

    def test_cast_to_json_plain_string(self):
        """Test casting plain string to JSON format."""
        typed_output = TypedOutputData(
            content="Hello, world!", type=TypedOutputType.JSON
        )
        result = typed_output.get_typed_content()

        assert isinstance(result, dict)
        assert result["raw_content"] == "Hello, world!"

    def test_cast_to_string(self):
        """Test casting to string format."""
        data = {"message": "Hello", "status": "success"}
        typed_output = TypedOutputData(content=data, type=TypedOutputType.STRING)
        result = typed_output.get_typed_content()

        assert isinstance(result, str)
        assert "message" in result
        assert "Hello" in result

    def test_cast_to_dict(self):
        """Test casting to dictionary format."""
        json_str = '{"message": "Hello", "status": "success"}'
        typed_output = TypedOutputData(content=json_str, type=TypedOutputType.DICT)
        result = typed_output.get_typed_content()

        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"

    def test_cast_to_list(self):
        """Test casting to list format."""
        json_str = '["item1", "item2", "item3"]'
        typed_output = TypedOutputData(content=json_str, type=TypedOutputType.LIST)
        result = typed_output.get_typed_content()

        assert isinstance(result, list)
        assert result == ["item1", "item2", "item3"]

    def test_cast_to_list_plain_string(self):
        """Test casting plain string to list format."""
        typed_output = TypedOutputData(
            content="Hello, world!", type=TypedOutputType.LIST
        )
        result = typed_output.get_typed_content()

        assert isinstance(result, list)
        assert result == ["Hello, world!"]

    def test_yaml_parsing(self):
        """Test YAML parsing."""
        yaml_str = """
        message: Hello
        status: success
        items:
          - item1
          - item2
        """
        typed_output = TypedOutputData(content=yaml_str, type=TypedOutputType.YAML)
        result = typed_output.get_typed_content()

        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"
        assert result["items"] == ["item1", "item2"]

    def test_already_structured_data(self):
        """Test with already structured data."""
        data = {"message": "Hello", "status": "success"}
        typed_output = TypedOutputData(content=data, type=TypedOutputType.AUTO)
        result = typed_output.get_typed_content()

        assert result == data

    def test_already_list_data(self):
        """Test with already list data."""
        data = ["item1", "item2", "item3"]
        typed_output = TypedOutputData(content=data, type=TypedOutputType.AUTO)
        result = typed_output.get_typed_content()

        assert result == data
