"""
Tests for TypedOutputData utility.
"""

from intent_kit.utils.typed_output import TypedOutputData
from intent_kit.types import TypedOutputType, IntentClassification, IntentAction


class TestTypedOutputData:
    """Test the TypedOutputData class."""

    def test_typed_output_data_creation(self):
        """Test creating a TypedOutputData instance."""
        data = TypedOutputData(
            content='{"message": "Hello", "status": "success"}',
            type=TypedOutputType.JSON,
        )

        assert data.content == '{"message": "Hello", "status": "success"}'
        assert data.type == TypedOutputType.JSON

    def test_typed_output_data_default_type(self):
        """Test TypedOutputData with default type."""
        data = TypedOutputData(content="Hello, world!")
        assert data.type == TypedOutputType.AUTO

    def test_typed_output_data_get_typed_content_json(self):
        """Test get_typed_content with JSON type."""
        data = TypedOutputData(
            content='{"message": "Hello", "status": "success"}',
            type=TypedOutputType.JSON,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"

    def test_typed_output_data_get_typed_content_string(self):
        """Test get_typed_content with STRING type."""
        data = TypedOutputData(
            content={"message": "Hello", "status": "success"},
            type=TypedOutputType.STRING,
        )

        result = data.get_typed_content()
        assert isinstance(result, str)
        assert "message" in result
        assert "Hello" in result

    def test_typed_output_data_get_typed_content_dict(self):
        """Test get_typed_content with DICT type."""
        data = TypedOutputData(
            content='{"message": "Hello", "status": "success"}',
            type=TypedOutputType.DICT,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["message"] == "Hello"

    def test_typed_output_data_get_typed_content_list(self):
        """Test get_typed_content with LIST type."""
        data = TypedOutputData(
            content='["item1", "item2", "item3"]',
            type=TypedOutputType.LIST,
        )

        result = data.get_typed_content()
        assert isinstance(result, list)
        assert result == ["item1", "item2", "item3"]

    def test_typed_output_data_get_typed_content_classifier(self):
        """Test get_typed_content with CLASSIFIER type."""
        classifier_data = {
            "chunk_text": "Hello, world!",
            "classification": "Atomic",
            "intent_type": "greeting",
            "action": "handle",
            "metadata": {"key": "value"},
        }
        data = TypedOutputData(
            content=classifier_data,
            type=TypedOutputType.CLASSIFIER,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["chunk_text"] == "Hello, world!"
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["action"] == IntentAction.HANDLE

    def test_typed_output_data_auto_detect_json(self):
        """Test auto-detection of JSON content."""
        data = TypedOutputData(
            content='{"message": "Hello", "status": "success"}',
            type=TypedOutputType.AUTO,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["message"] == "Hello"

    def test_typed_output_data_auto_detect_plain_string(self):
        """Test auto-detection of plain string content."""
        data = TypedOutputData(
            content="Hello, world!",
            type=TypedOutputType.AUTO,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["raw_content"] == "Hello, world!"

    def test_typed_output_data_auto_detect_list(self):
        """Test auto-detection of list content."""
        data = TypedOutputData(
            content=["item1", "item2", "item3"],
            type=TypedOutputType.AUTO,
        )

        result = data.get_typed_content()
        assert result == ["item1", "item2", "item3"]

    def test_typed_output_data_auto_detect_non_string_non_dict(self):
        """Test auto-detection of non-string, non-dict content."""
        data = TypedOutputData(
            content=123,
            type=TypedOutputType.AUTO,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["raw_content"] == "123"

    def test_typed_output_data_yaml_parsing(self):
        """Test YAML parsing in TypedOutputData."""
        yaml_str = """
        message: Hello
        status: success
        items:
          - item1
          - item2
        """
        data = TypedOutputData(
            content=yaml_str,
            type=TypedOutputType.YAML,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"
        assert result["items"] == ["item1", "item2"]

    def test_typed_output_data_yaml_parsing_scalar(self):
        """Test YAML parsing of scalar values."""
        data = TypedOutputData(
            content="Hello, world!",
            type=TypedOutputType.YAML,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["raw_content"] == "Hello, world!"

    def test_typed_output_data_dict_parsing_json_string(self):
        """Test DICT parsing with JSON string."""
        data = TypedOutputData(
            content='{"message": "Hello", "status": "success"}',
            type=TypedOutputType.DICT,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"

    def test_typed_output_data_dict_parsing_yaml_string(self):
        """Test DICT parsing with YAML string."""
        yaml_str = """
        message: Hello
        status: success
        """
        data = TypedOutputData(
            content=yaml_str,
            type=TypedOutputType.DICT,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"

    def test_typed_output_data_list_parsing_json_string(self):
        """Test LIST parsing with JSON string."""
        data = TypedOutputData(
            content='["item1", "item2", "item3"]',
            type=TypedOutputType.LIST,
        )

        result = data.get_typed_content()
        assert isinstance(result, list)
        assert result == ["item1", "item2", "item3"]

    def test_typed_output_data_list_parsing_yaml_string(self):
        """Test LIST parsing with YAML string."""
        yaml_str = """
        - item1
        - item2
        - item3
        """
        data = TypedOutputData(
            content=yaml_str,
            type=TypedOutputType.LIST,
        )

        result = data.get_typed_content()
        assert isinstance(result, list)
        assert result == ["item1", "item2", "item3"]

    def test_typed_output_data_list_parsing_dict_input(self):
        """Test LIST parsing with dict input."""
        data = TypedOutputData(
            content={"key1": "value1", "key2": "value2"},
            type=TypedOutputType.LIST,
        )

        result = data.get_typed_content()
        assert isinstance(result, list)
        # The dict gets converted to string and wrapped in a list
        assert len(result) == 1
        assert isinstance(result[0], str)
        assert "key1" in result[0]
        assert "value1" in result[0]

    def test_typed_output_data_classifier_parsing_dict(self):
        """Test CLASSIFIER parsing with dict input."""
        classifier_data = {
            "chunk_text": "Hello, world!",
            "classification": "Composite",
            "intent_type": "greeting",
            "action": "split",
            "metadata": {"key": "value"},
        }
        data = TypedOutputData(
            content=classifier_data,
            type=TypedOutputType.CLASSIFIER,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["chunk_text"] == "Hello, world!"
        assert result["classification"] == IntentClassification.COMPOSITE
        assert result["action"] == IntentAction.SPLIT

    def test_typed_output_data_classifier_parsing_json_string(self):
        """Test CLASSIFIER parsing with JSON string."""
        json_str = '{"chunk_text": "Hello, world!", "classification": "Ambiguous", "action": "clarify"}'
        data = TypedOutputData(
            content=json_str,
            type=TypedOutputType.CLASSIFIER,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["chunk_text"] == "Hello, world!"
        assert result["classification"] == IntentClassification.AMBIGUOUS
        assert result["action"] == IntentAction.CLARIFY

    def test_typed_output_data_classifier_parsing_plain_string(self):
        """Test CLASSIFIER parsing with plain string."""
        data = TypedOutputData(
            content="Hello, world!",
            type=TypedOutputType.CLASSIFIER,
        )

        result = data.get_typed_content()
        assert isinstance(result, dict)
        assert result["chunk_text"] == "Hello, world!"
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["action"] == IntentAction.HANDLE
