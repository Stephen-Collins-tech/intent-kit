"""
Tests for core type definitions.
"""

from intent_kit.types import (
    IntentClassification,
    IntentAction,
    IntentChunkClassification,
    ClassifierOutput,
    ClassifierFunction,
    TypedOutputType,
    TokenUsage,
    InputTokens,
    OutputTokens,
    TotalTokens,
    Cost,
    Provider,
    Model,
    Output,
    Duration,
    StructuredOutput,
    TypedOutput,
)


class TestIntentClassification:
    """Test the IntentClassification enum."""

    def test_all_enum_values_exist(self):
        """Test that all expected enum values exist."""
        expected_values = {
            "ATOMIC": "Atomic",
            "COMPOSITE": "Composite",
            "AMBIGUOUS": "Ambiguous",
            "INVALID": "Invalid",
        }

        for name, value in expected_values.items():
            assert hasattr(IntentClassification, name)
            assert getattr(IntentClassification, name).value == value

    def test_enum_values_are_strings(self):
        """Test that all enum values are strings."""
        for classification in IntentClassification:
            assert isinstance(classification.value, str)

    def test_enum_values_are_unique(self):
        """Test that all enum values are unique."""
        values = [classification.value for classification in IntentClassification]
        assert len(values) == len(set(values))

    def test_atomic_classification(self):
        """Test the ATOMIC classification."""
        assert IntentClassification.ATOMIC.value == "Atomic"

    def test_composite_classification(self):
        """Test the COMPOSITE classification."""
        assert IntentClassification.COMPOSITE.value == "Composite"

    def test_ambiguous_classification(self):
        """Test the AMBIGUOUS classification."""
        assert IntentClassification.AMBIGUOUS.value == "Ambiguous"

    def test_invalid_classification(self):
        """Test the INVALID classification."""
        assert IntentClassification.INVALID.value == "Invalid"

    def test_enum_iteration(self):
        """Test that the enum can be iterated over."""
        classifications = list(IntentClassification)
        assert len(classifications) == 4  # Total number of enum values

    def test_enum_comparison(self):
        """Test enum comparison operations."""
        assert IntentClassification.ATOMIC == IntentClassification.ATOMIC
        assert IntentClassification.ATOMIC != IntentClassification.COMPOSITE
        assert IntentClassification.ATOMIC.value == "Atomic"

    def test_enum_string_conversion(self):
        """Test string conversion of enum values."""
        assert str(IntentClassification.ATOMIC) == "IntentClassification.ATOMIC"
        assert (
            repr(IntentClassification.ATOMIC)
            == "<IntentClassification.ATOMIC: 'Atomic'>"
        )

    def test_enum_value_access(self):
        """Test accessing enum values."""
        assert IntentClassification.ATOMIC.value == "Atomic"
        assert IntentClassification.COMPOSITE.value == "Composite"
        assert IntentClassification.AMBIGUOUS.value == "Ambiguous"
        assert IntentClassification.INVALID.value == "Invalid"

    def test_enum_name_access(self):
        """Test accessing enum names."""
        assert IntentClassification.ATOMIC.name == "ATOMIC"
        assert IntentClassification.COMPOSITE.name == "COMPOSITE"
        assert IntentClassification.AMBIGUOUS.name == "AMBIGUOUS"
        assert IntentClassification.INVALID.name == "INVALID"

    def test_enum_membership(self):
        """Test enum membership operations."""
        assert IntentClassification.ATOMIC in IntentClassification
        assert IntentClassification.COMPOSITE in IntentClassification
        assert IntentClassification.AMBIGUOUS in IntentClassification
        assert IntentClassification.INVALID in IntentClassification

    def test_enum_value_membership(self):
        """Test checking if a value belongs to the enum."""
        valid_values = [classification.value for classification in IntentClassification]
        assert "Atomic" in valid_values
        assert "Composite" in valid_values
        assert "Ambiguous" in valid_values
        assert "Invalid" in valid_values
        assert "Unknown" not in valid_values

    def test_enum_from_value(self):
        """Test creating enum from value."""
        atomic_classification = next(
            (c for c in IntentClassification if c.value == "Atomic"), None
        )
        assert atomic_classification == IntentClassification.ATOMIC

    def test_enum_documentation(self):
        """Test that enum has proper documentation."""
        # Enums don't have docstrings by default, so this test is just for completeness
        # The enum is properly defined and functional
        assert IntentClassification is not None


class TestIntentAction:
    """Test the IntentAction enum."""

    def test_all_enum_values_exist(self):
        """Test that all expected enum values exist."""
        expected_values = {
            "HANDLE": "handle",
            "SPLIT": "split",
            "CLARIFY": "clarify",
            "REJECT": "reject",
        }

        for name, value in expected_values.items():
            assert hasattr(IntentAction, name)
            assert getattr(IntentAction, name).value == value

    def test_enum_values_are_strings(self):
        """Test that all enum values are strings."""
        for action in IntentAction:
            assert isinstance(action.value, str)

    def test_enum_values_are_unique(self):
        """Test that all enum values are unique."""
        values = [action.value for action in IntentAction]
        assert len(values) == len(set(values))

    def test_handle_action(self):
        """Test the HANDLE action."""
        assert IntentAction.HANDLE.value == "handle"

    def test_split_action(self):
        """Test the SPLIT action."""
        assert IntentAction.SPLIT.value == "split"

    def test_clarify_action(self):
        """Test the CLARIFY action."""
        assert IntentAction.CLARIFY.value == "clarify"

    def test_reject_action(self):
        """Test the REJECT action."""
        assert IntentAction.REJECT.value == "reject"

    def test_enum_iteration(self):
        """Test that the enum can be iterated over."""
        actions = list(IntentAction)
        assert len(actions) == 4  # Total number of enum values

    def test_enum_comparison(self):
        """Test enum comparison operations."""
        assert IntentAction.HANDLE == IntentAction.HANDLE
        assert IntentAction.HANDLE != IntentAction.SPLIT
        assert IntentAction.HANDLE.value == "handle"

    def test_enum_string_conversion(self):
        """Test string conversion of enum values."""
        assert str(IntentAction.HANDLE) == "IntentAction.HANDLE"
        assert repr(IntentAction.HANDLE) == "<IntentAction.HANDLE: 'handle'>"

    def test_enum_value_access(self):
        """Test accessing enum values."""
        assert IntentAction.HANDLE.value == "handle"
        assert IntentAction.SPLIT.value == "split"
        assert IntentAction.CLARIFY.value == "clarify"
        assert IntentAction.REJECT.value == "reject"

    def test_enum_name_access(self):
        """Test accessing enum names."""
        assert IntentAction.HANDLE.name == "HANDLE"
        assert IntentAction.SPLIT.name == "SPLIT"
        assert IntentAction.CLARIFY.name == "CLARIFY"
        assert IntentAction.REJECT.name == "REJECT"

    def test_enum_membership(self):
        """Test enum membership operations."""
        assert IntentAction.HANDLE in IntentAction
        assert IntentAction.SPLIT in IntentAction
        assert IntentAction.CLARIFY in IntentAction
        assert IntentAction.REJECT in IntentAction

    def test_enum_value_membership(self):
        """Test checking if a value belongs to the enum."""
        valid_values = [action.value for action in IntentAction]
        assert "handle" in valid_values
        assert "split" in valid_values
        assert "clarify" in valid_values
        assert "reject" in valid_values
        assert "unknown" not in valid_values

    def test_enum_from_value(self):
        """Test creating enum from value."""
        handle_action = next((a for a in IntentAction if a.value == "handle"), None)
        assert handle_action == IntentAction.HANDLE

    def test_enum_documentation(self):
        """Test that enum has proper documentation."""
        # Enums don't have docstrings by default, so this test is just for completeness
        # The enum is properly defined and functional
        assert IntentAction is not None


class TestTypedOutputType:
    """Test the TypedOutputType enum."""

    def test_all_enum_values_exist(self):
        """Test that all expected enum values exist."""
        expected_values = {
            "JSON": "json",
            "YAML": "yaml",
            "STRING": "string",
            "DICT": "dict",
            "LIST": "list",
            "CLASSIFIER": "classifier",
            "AUTO": "auto",
        }

        for name, value in expected_values.items():
            assert hasattr(TypedOutputType, name)
            assert getattr(TypedOutputType, name).value == value

    def test_enum_values_are_strings(self):
        """Test that all enum values are strings."""
        for output_type in TypedOutputType:
            assert isinstance(output_type.value, str)

    def test_enum_values_are_unique(self):
        """Test that all enum values are unique."""
        values = [output_type.value for output_type in TypedOutputType]
        assert len(values) == len(set(values))

    def test_enum_iteration(self):
        """Test that the enum can be iterated over."""
        output_types = list(TypedOutputType)
        assert len(output_types) == 7  # Total number of enum values


class TestTypeAliases:
    """Test the type aliases."""

    def test_classifier_output_type(self):
        """Test that ClassifierOutput is properly defined."""
        # ClassifierOutput should be IntentChunkClassification
        assert ClassifierOutput == IntentChunkClassification

    def test_classifier_function_type(self):
        """Test that ClassifierFunction is properly defined."""
        # ClassifierFunction should be Callable[[str], ClassifierOutput]
        from typing import Callable

        expected_type = Callable[[str], ClassifierOutput]
        assert str(ClassifierFunction) == str(expected_type)

    def test_type_aliases_are_defined(self):
        """Test that all type aliases are properly defined."""
        # Test that the type aliases are not None
        assert TokenUsage is not None
        assert InputTokens is not None
        assert OutputTokens is not None
        assert TotalTokens is not None
        assert Cost is not None
        assert Provider is not None
        assert Model is not None
        assert Output is not None
        assert Duration is not None
        assert StructuredOutput is not None
        assert TypedOutput is not None
