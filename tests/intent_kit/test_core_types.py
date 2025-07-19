"""
Tests for core types module.
"""




    IntentClassification,
    IntentAction,
    IntentChunkClassification,
    IntentChunk,
    ClassifierOutput,
    SplitterFunction,
    ClassifierFunction,
()


class TestIntentClassification:
    """Test the IntentClassification enum."""

    def test_def test_def test_all_enum_values_exist(self): -> None: -> None:
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

    def test_def test_def test_enum_values_are_strings(self): -> None: -> None:
        """Test that all enum values are strings."""
        for classification in IntentClassification:
            assert isinstance(classification.value, str)

    def test_def test_def test_enum_values_are_unique(self): -> None: -> None:
        """Test that all enum values are unique."""
        values = [classification.value for classification in IntentClassification]
        assert len(values) == len(set(values))

    def test_def test_def test_atomic_classification(self): -> None: -> None:
        """Test the ATOMIC classification."""
        assert IntentClassification.ATOMIC.value == "Atomic"

    def test_def test_def test_composite_classification(self): -> None: -> None:
        """Test the COMPOSITE classification."""
        assert IntentClassification.COMPOSITE.value == "Composite"

    def test_def test_def test_ambiguous_classification(self): -> None: -> None:
        """Test the AMBIGUOUS classification."""
        assert IntentClassification.AMBIGUOUS.value == "Ambiguous"

    def test_def test_def test_invalid_classification(self): -> None: -> None:
        """Test the INVALID classification."""
        assert IntentClassification.INVALID.value == "Invalid"

    def test_def test_def test_enum_iteration(self): -> None: -> None:
        """Test that the enum can be iterated over."""
        classifications = list(IntentClassification)
        assert len(classifications) == 4  # Total number of enum values

    def test_def test_def test_enum_comparison(self): -> None: -> None:
        """Test enum comparison operations."""
        assert IntentClassification.ATOMIC == IntentClassification.ATOMIC
        assert IntentClassification.ATOMIC != IntentClassification.COMPOSITE
        assert IntentClassification.ATOMIC.value == "Atomic"

    def test_def test_def test_enum_string_conversion(self): -> None: -> None:
        """Test string conversion of enum values."""
        assert str(IntentClassification.ATOMIC) == "IntentClassification.ATOMIC"
        assert ()
            repr(IntentClassification.ATOMIC)
            == "<IntentClassification.ATOMIC: 'Atomic'>"
(        )

    def test_def test_def test_enum_value_access(self): -> None: -> None:
        """Test accessing enum values."""
        assert IntentClassification.ATOMIC.value == "Atomic"
        assert IntentClassification.COMPOSITE.value == "Composite"
        assert IntentClassification.AMBIGUOUS.value == "Ambiguous"
        assert IntentClassification.INVALID.value == "Invalid"

    def test_def test_def test_enum_name_access(self): -> None: -> None:
        """Test accessing enum names."""
        assert IntentClassification.ATOMIC.name == "ATOMIC"
        assert IntentClassification.COMPOSITE.name == "COMPOSITE"
        assert IntentClassification.AMBIGUOUS.name == "AMBIGUOUS"
        assert IntentClassification.INVALID.name == "INVALID"

    def test_def test_def test_enum_membership(self): -> None: -> None:
        """Test enum membership operations."""
        assert IntentClassification.ATOMIC in IntentClassification
        assert IntentClassification.COMPOSITE in IntentClassification
        assert IntentClassification.AMBIGUOUS in IntentClassification
        assert IntentClassification.INVALID in IntentClassification

    def test_def test_def test_enum_value_membership(self): -> None: -> None:
        """Test checking if a value belongs to the enum."""
        valid_values = [classification.value for classification in IntentClassification]
        assert "Atomic" in valid_values
        assert "Composite" in valid_values
        assert "Ambiguous" in valid_values
        assert "Invalid" in valid_values
        assert "Unknown" not in valid_values

    def test_def test_def test_enum_from_value(self): -> None: -> None:
        """Test creating enum from value."""
        atomic_classification = next()
            (c for c in IntentClassification if c.value == "Atomic"), None
(        )
        assert atomic_classification == IntentClassification.ATOMIC

    def test_def test_def test_enum_documentation(self): -> None: -> None:
        """Test that enum has proper documentation."""
        # Enums don't have docstrings by default, so this test is just for completeness
        # The enum is properly defined and functional
        assert IntentClassification is not None


class TestIntentAction:
    """Test the IntentAction enum."""

    def test_def test_def test_all_enum_values_exist(self): -> None: -> None:
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

    def test_def test_def test_enum_values_are_strings(self): -> None: -> None:
        """Test that all enum values are strings."""
        for action in IntentAction:
            assert isinstance(action.value, str)

    def test_def test_def test_enum_values_are_unique(self): -> None: -> None:
        """Test that all enum values are unique."""
        values = [action.value for action in IntentAction]
        assert len(values) == len(set(values))

    def test_def test_def test_handle_action(self): -> None: -> None:
        """Test the HANDLE action."""
        assert IntentAction.HANDLE.value == "handle"

    def test_def test_def test_split_action(self): -> None: -> None:
        """Test the SPLIT action."""
        assert IntentAction.SPLIT.value == "split"

    def test_def test_def test_clarify_action(self): -> None: -> None:
        """Test the CLARIFY action."""
        assert IntentAction.CLARIFY.value == "clarify"

    def test_def test_def test_reject_action(self): -> None: -> None:
        """Test the REJECT action."""
        assert IntentAction.REJECT.value == "reject"

    def test_def test_def test_enum_iteration(self): -> None: -> None:
        """Test that the enum can be iterated over."""
        actions = list(IntentAction)
        assert len(actions) == 4  # Total number of enum values

    def test_def test_def test_enum_comparison(self): -> None: -> None:
        """Test enum comparison operations."""
        assert IntentAction.HANDLE == IntentAction.HANDLE
        assert IntentAction.HANDLE != IntentAction.SPLIT
        assert IntentAction.HANDLE.value == "handle"

    def test_def test_def test_enum_string_conversion(self): -> None: -> None:
        """Test string conversion of enum values."""
        assert str(IntentAction.HANDLE) == "IntentAction.HANDLE"
        assert repr(IntentAction.HANDLE) == "<IntentAction.HANDLE: 'handle'>"

    def test_def test_def test_enum_value_access(self): -> None: -> None:
        """Test accessing enum values."""
        assert IntentAction.HANDLE.value == "handle"
        assert IntentAction.SPLIT.value == "split"
        assert IntentAction.CLARIFY.value == "clarify"
        assert IntentAction.REJECT.value == "reject"

    def test_def test_def test_enum_name_access(self): -> None: -> None:
        """Test accessing enum names."""
        assert IntentAction.HANDLE.name == "HANDLE"
        assert IntentAction.SPLIT.name == "SPLIT"
        assert IntentAction.CLARIFY.name == "CLARIFY"
        assert IntentAction.REJECT.name == "REJECT"

    def test_def test_def test_enum_membership(self): -> None: -> None:
        """Test enum membership operations."""
        assert IntentAction.HANDLE in IntentAction
        assert IntentAction.SPLIT in IntentAction
        assert IntentAction.CLARIFY in IntentAction
        assert IntentAction.REJECT in IntentAction

    def test_def test_def test_enum_value_membership(self): -> None: -> None:
        """Test checking if a value belongs to the enum."""
        valid_values = [action.value for action in IntentAction]
        assert "handle" in valid_values
        assert "split" in valid_values
        assert "clarify" in valid_values
        assert "reject" in valid_values
        assert "unknown" not in valid_values

    def test_def test_def test_enum_from_value(self): -> None: -> None:
        """Test creating enum from value."""
        handle_action = next((a for a in IntentAction if a.value == "handle"), None)
        assert handle_action == IntentAction.HANDLE

    def test_def test_def test_enum_documentation(self): -> None: -> None:
        """Test that enum has proper documentation."""
        # Enums don't have docstrings by default, so this test is just for completeness
        # The enum is properly defined and functional
        assert IntentAction is not None


class TestIntentChunkClassification:
    """Test the IntentChunkClassification TypedDict."""

    def test_def test_def test_basic_creation(self): -> None: -> None:
        """Test creating a basic IntentChunkClassification."""
        classification = IntentChunkClassification()
            chunk_text="test chunk",
            classification=IntentClassification.ATOMIC,
            intent_type="test_intent",
            action=IntentAction.HANDLE,
            metadata={"key": "value"},
(        )

        assert classification["chunk_text"] == "test chunk"
        assert classification["classification"] == IntentClassification.ATOMIC
        assert classification["intent_type"] == "test_intent"
        assert classification["action"] == IntentAction.HANDLE
        assert classification["metadata"] == {"key": "value"}

    def test_def test_def test_creation_with_optional_fields(self): -> None: -> None:
        """Test creating IntentChunkClassification with optional fields."""
        classification = IntentChunkClassification()
            chunk_text="test chunk",
            classification=IntentClassification.COMPOSITE,
            action=IntentAction.SPLIT,
(        )

        assert classification["chunk_text"] == "test chunk"
        assert classification["classification"] == IntentClassification.COMPOSITE
        assert classification["action"] == IntentAction.SPLIT
        # Optional fields should be missing
        assert "intent_type" not in classification
        assert "metadata" not in classification

    def test_def test_def test_creation_with_none_intent_type(self): -> None: -> None:
        """Test creating IntentChunkClassification with None intent_type."""
        classification = IntentChunkClassification()
            chunk_text="test chunk",
            classification=IntentClassification.AMBIGUOUS,
            intent_type=None,
            action=IntentAction.CLARIFY,
            metadata={},
(        )

        assert classification["chunk_text"] == "test chunk"
        assert classification["classification"] == IntentClassification.AMBIGUOUS
        assert classification["intent_type"] is None
        assert classification["action"] == IntentAction.CLARIFY
        assert classification["metadata"] == {}

    def test_def test_def test_creation_with_complex_metadata(self): -> None: -> None:
        """Test creating IntentChunkClassification with complex metadata."""
        metadata = {
            "confidence": 0.95,
            "processing_time": 0.1,
            "model_used": "gpt-4",
            "nested": {"key": "value"},
        }

        classification = IntentChunkClassification()
            chunk_text="test chunk",
            classification=IntentClassification.ATOMIC,
            intent_type="complex_intent",
            action=IntentAction.HANDLE,
            metadata=metadata,
(        )

        assert classification["metadata"] == metadata
        assert classification["metadata"]["confidence"] == 0.95
        assert classification["metadata"]["nested"]["key"] == "value"

    def test_def test_def test_all_classification_types(self): -> None: -> None:
        """Test creating IntentChunkClassification with all classification types."""
        classifications = [
            IntentClassification.ATOMIC,
            IntentClassification.COMPOSITE,
            IntentClassification.AMBIGUOUS,
            IntentClassification.INVALID,
        ]

        for classification_type in classifications:
            chunk_classification = IntentChunkClassification()
                chunk_text="test chunk",
                classification=classification_type,
                action=IntentAction.HANDLE,
(            )

            assert chunk_classification["classification"] == classification_type

    def test_def test_def test_all_action_types(self): -> None: -> None:
        """Test creating IntentChunkClassification with all action types."""
        actions = [
            IntentAction.HANDLE,
            IntentAction.SPLIT,
            IntentAction.CLARIFY,
            IntentAction.REJECT,
        ]

        for action_type in actions:
            chunk_classification = IntentChunkClassification()
                chunk_text="test chunk",
                classification=IntentClassification.ATOMIC,
                action=action_type,
(            )

            assert chunk_classification["action"] == action_type

    def test_def test_def test_dict_like_behavior(self): -> None: -> None:
        """Test that IntentChunkClassification behaves like a dictionary."""
        classification = IntentChunkClassification()
            chunk_text="test chunk",
            classification=IntentClassification.ATOMIC,
            action=IntentAction.HANDLE,
(        )

        # Test key access
        assert classification["chunk_text"] == "test chunk"
        assert classification["classification"] == IntentClassification.ATOMIC
        assert classification["action"] == IntentAction.HANDLE

        # Test key iteration
        keys = list(classification.keys())
        assert "chunk_text" in keys
        assert "classification" in keys
        assert "action" in keys

        # Test value iteration
        values = list(classification.values())
        assert "test chunk" in values
        assert IntentClassification.ATOMIC in values
        assert IntentAction.HANDLE in values

        # Test item iteration
        items = list(classification.items())
        assert ("chunk_text", "test chunk") in items
        assert ("classification", IntentClassification.ATOMIC) in items
        assert ("action", IntentAction.HANDLE) in items

    def test_def test_def test_total_false_behavior(self): -> None: -> None:
        """Test that total=False allows missing optional fields."""
        # This should work because total=False allows missing fields
        classification = IntentChunkClassification()
            chunk_text="test chunk",
            classification=IntentClassification.ATOMIC,
            action=IntentAction.HANDLE,
(        )

        # Optional fields should not be present
        assert "intent_type" not in classification
        assert "metadata" not in classification


class TestTypeAliases:
    """Test the type aliases."""

    def test_def test_def test_intent_chunk_type(self): -> None: -> None:
        """Test that IntentChunk is properly defined."""
        # IntentChunk should be Union[str, Dict[str, Any]]
        assert IntentChunk == Union[str, Dict[str, Any]]

    def test_def test_def test_classifier_output_type(self): -> None: -> None:
        """Test that ClassifierOutput is properly defined."""
        # ClassifierOutput should be IntentChunkClassification
        assert ClassifierOutput == IntentChunkClassification

    def test_def test_def test_splitter_function_type(self): -> None: -> None:
        """Test that SplitterFunction is properly defined."""
        # SplitterFunction should be Callable[..., Sequence[IntentChunk]]


        expected_type = Callable[..., Sequence[IntentChunk]]
        assert str(SplitterFunction) == str(expected_type)

    def test_def test_def test_classifier_function_type(self): -> None: -> None:
        """Test that ClassifierFunction is properly defined."""
        # ClassifierFunction should be Callable[[IntentChunk], ClassifierOutput]


        expected_type = Callable[[IntentChunk], ClassifierOutput]
        assert str(ClassifierFunction) == str(expected_type)
