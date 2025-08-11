"""
Tests for classifier output functionality.
"""

from intent_kit.types import (
    TypedOutputData,
    TypedOutputType,
    IntentClassification,
    IntentAction,
)


class TestClassifierOutput:
    """Test classifier output functionality."""

    def test_cast_to_classifier_from_json(self):
        """Test casting JSON to ClassifierOutput."""
        json_str = """{
            "chunk_text": "Hello, how are you?",
            "classification": "Atomic",
            "intent_type": "greeting",
            "action": "handle",
            "metadata": {"confidence": 0.95}
        }"""

        typed_output = TypedOutputData(
            content=json_str, type=TypedOutputType.CLASSIFIER
        )
        result = typed_output.get_typed_content()

        assert result["chunk_text"] == "Hello, how are you?"
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["intent_type"] == "greeting"
        assert result["action"] == IntentAction.HANDLE
        assert result["metadata"]["confidence"] == 0.95

    def test_cast_to_classifier_from_dict(self):
        """Test casting dict to ClassifierOutput."""
        data = {
            "chunk_text": "What's the weather like?",
            "classification": "Composite",
            "intent_type": "weather_query",
            "action": "split",
            "metadata": {"location": "unknown"},
        }

        typed_output = TypedOutputData(content=data, type=TypedOutputType.CLASSIFIER)
        result = typed_output.get_typed_content()

        assert result["chunk_text"] == "What's the weather like?"
        assert result["classification"] == IntentClassification.COMPOSITE
        assert result["intent_type"] == "weather_query"
        assert result["action"] == IntentAction.SPLIT
        assert result["metadata"]["location"] == "unknown"

    def test_cast_to_classifier_with_invalid_classification(self):
        """Test casting with invalid classification value."""
        json_str = """{
            "chunk_text": "Invalid input",
            "classification": "InvalidClassification",
            "action": "handle"
        }"""

        typed_output = TypedOutputData(
            content=json_str, type=TypedOutputType.CLASSIFIER
        )
        result = typed_output.get_typed_content()

        # Should default to ATOMIC
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["action"] == IntentAction.HANDLE

    def test_cast_to_classifier_with_invalid_action(self):
        """Test casting with invalid action value."""
        json_str = """{
            "chunk_text": "Invalid action",
            "classification": "Atomic",
            "action": "invalid_action"
        }"""

        typed_output = TypedOutputData(
            content=json_str, type=TypedOutputType.CLASSIFIER
        )
        result = typed_output.get_typed_content()

        # Should default to HANDLE
        assert result["action"] == IntentAction.HANDLE

    def test_cast_to_classifier_from_plain_string(self):
        """Test casting plain string to ClassifierOutput."""
        typed_output = TypedOutputData(
            content="Hello world", type=TypedOutputType.CLASSIFIER
        )
        result = typed_output.get_typed_content()

        assert result["chunk_text"] == "Hello world"
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["intent_type"] is None
        assert result["action"] == IntentAction.HANDLE
        assert "raw_content" in result["metadata"]

    def test_cast_to_classifier_with_missing_fields(self):
        """Test casting with missing optional fields."""
        json_str = """{
            "chunk_text": "Minimal input",
            "classification": "Ambiguous"
        }"""

        typed_output = TypedOutputData(
            content=json_str, type=TypedOutputType.CLASSIFIER
        )
        result = typed_output.get_typed_content()

        assert result["chunk_text"] == "Minimal input"
        assert result["classification"] == IntentClassification.AMBIGUOUS
        assert result["intent_type"] is None
        assert result["action"] == IntentAction.HANDLE  # Default
        assert result["metadata"] == {}

    def test_cast_to_classifier_with_all_enum_values(self):
        """Test all classification and action enum values."""
        test_cases = [
            ("Atomic", IntentClassification.ATOMIC),
            ("Composite", IntentClassification.COMPOSITE),
            ("Ambiguous", IntentClassification.AMBIGUOUS),
            ("Invalid", IntentClassification.INVALID),
        ]

        for classification_str, expected_enum in test_cases:
            json_str = f"""{{
                "chunk_text": "Test {classification_str}",
                "classification": "{classification_str}",
                "action": "handle"
            }}"""

            typed_output = TypedOutputData(
                content=json_str, type=TypedOutputType.CLASSIFIER
            )
            result = typed_output.get_typed_content()

            assert result["classification"] == expected_enum

        action_test_cases = [
            ("handle", IntentAction.HANDLE),
            ("split", IntentAction.SPLIT),
            ("clarify", IntentAction.CLARIFY),
            ("reject", IntentAction.REJECT),
        ]

        for action_str, expected_enum in action_test_cases:
            json_str = f"""{{
                "chunk_text": "Test {action_str}",
                "classification": "Atomic",
                "action": "{action_str}"
            }}"""

            typed_output = TypedOutputData(
                content=json_str, type=TypedOutputType.CLASSIFIER
            )
            result = typed_output.get_typed_content()

            assert result["action"] == expected_enum

    def test_cast_to_classifier_with_complex_metadata(self):
        """Test casting with complex metadata."""
        json_str = """{
            "chunk_text": "Complex query",
            "classification": "Composite",
            "intent_type": "multi_step_task",
            "action": "split",
            "metadata": {
                "confidence": 0.87,
                "sub_tasks": ["task1", "task2"],
                "priority": "high",
                "nested": {
                    "key": "value"
                }
            }
        }"""

        typed_output = TypedOutputData(
            content=json_str, type=TypedOutputType.CLASSIFIER
        )
        result = typed_output.get_typed_content()

        assert result["metadata"]["confidence"] == 0.87
        assert result["metadata"]["sub_tasks"] == ["task1", "task2"]
        assert result["metadata"]["priority"] == "high"
        assert result["metadata"]["nested"]["key"] == "value"
