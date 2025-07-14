"""
Tests for intent_kit.node.classifiers.chunk_classifier module.
"""

from unittest.mock import patch

from intent_kit.node.classifiers.chunk_classifier import (
    classify_intent_chunk,
    _create_classification_prompt,
    _parse_classification_response,
    _manual_parse_classification,
    _fallback_classify,
)
from intent_kit.types import IntentClassification, IntentAction


class TestClassifyIntentChunk:
    """Test the main classify_intent_chunk function."""

    def test_classify_empty_chunk(self):
        """Test classification of empty chunk."""
        result = classify_intent_chunk("")

        assert result["chunk_text"] == ""
        assert result["classification"] == IntentClassification.INVALID
        assert result["intent_type"] is None
        assert result["action"] == IntentAction.REJECT
        assert result["metadata"]["confidence"] == 0.0
        assert result["metadata"]["reason"] == "Empty chunk"

    def test_classify_whitespace_only_chunk(self):
        """Test classification of whitespace-only chunk."""
        result = classify_intent_chunk("   \n\t  ")

        assert result["chunk_text"] == "   \n\t  "
        assert result["classification"] == IntentClassification.INVALID
        assert result["action"] == IntentAction.REJECT

    def test_classify_dict_chunk(self):
        """Test classification of chunk passed as dict."""
        chunk = {"text": "Book a flight"}
        result = classify_intent_chunk(chunk)

        assert result["chunk_text"] == "Book a flight"
        assert result["classification"] == IntentClassification.ATOMIC

    def test_classify_without_llm_config(self):
        """Test classification without LLM config (fallback)."""
        result = classify_intent_chunk("Book a flight to NYC")

        assert result["chunk_text"] == "Book a flight to NYC"
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["action"] == IntentAction.HANDLE

    @patch(
        "intent_kit.node.classifiers.chunk_classifier.LLMFactory.generate_with_config"
    )
    @patch(
        "intent_kit.node.classifiers.chunk_classifier._parse_classification_response"
    )
    def test_classify_with_llm_config_success(self, mock_parse, mock_generate):
        """Test successful classification with LLM config."""
        mock_generate.return_value = "mock response"
        mock_parse.return_value = {
            "chunk_text": "Book a flight",
            "classification": IntentClassification.ATOMIC,
            "intent_type": "BookFlightIntent",
            "action": IntentAction.HANDLE,
            "metadata": {"confidence": 0.95, "reason": "Single clear intent"},
        }

        llm_config = {"provider": "openai", "model": "gpt-4"}
        result = classify_intent_chunk("Book a flight", llm_config)

        mock_generate.assert_called_once()
        mock_parse.assert_called_once_with("mock response", "Book a flight")
        assert result["classification"] == IntentClassification.ATOMIC

    @patch(
        "intent_kit.node.classifiers.chunk_classifier.LLMFactory.generate_with_config"
    )
    @patch(
        "intent_kit.node.classifiers.chunk_classifier._parse_classification_response"
    )
    def test_classify_with_llm_config_parse_failure(self, mock_parse, mock_generate):
        """Test classification when LLM parsing fails."""
        mock_generate.return_value = "mock response"
        mock_parse.return_value = None  # Parse failure

        llm_config = {"provider": "openai", "model": "gpt-4"}
        result = classify_intent_chunk("Book a flight", llm_config)

        # Should fall back to rule-based classification
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["action"] == IntentAction.HANDLE

    @patch(
        "intent_kit.node.classifiers.chunk_classifier.LLMFactory.generate_with_config"
    )
    def test_classify_with_llm_config_exception(self, mock_generate):
        """Test classification when LLM raises exception."""
        mock_generate.side_effect = Exception("LLM error")

        llm_config = {"provider": "openai", "model": "gpt-4"}
        result = classify_intent_chunk("Book a flight", llm_config)

        # Should fall back to rule-based classification
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["action"] == IntentAction.HANDLE


class TestCreateClassificationPrompt:
    """Test the _create_classification_prompt function."""

    def test_create_classification_prompt(self):
        """Test prompt creation."""
        prompt = _create_classification_prompt("Book a flight to NYC")

        assert "Book a flight to NYC" in prompt
        assert "Atomic|Composite|Ambiguous|Invalid" in prompt
        assert "handle|split|clarify|reject" in prompt
        assert "confidence" in prompt
        assert "reason" in prompt
        assert "JSON" in prompt

    def test_create_classification_prompt_with_special_characters(self):
        """Test prompt creation with special characters."""
        prompt = _create_classification_prompt(
            "Book a flight with 'quotes' and \"double quotes\""
        )

        assert "Book a flight with 'quotes' and \"double quotes\"" in prompt


class TestParseClassificationResponse:
    """Test the _parse_classification_response function."""

    @patch("intent_kit.node.classifiers.chunk_classifier.extract_json_from_text")
    def test_parse_valid_json_response(self, mock_extract):
        """Test parsing valid JSON response."""
        mock_extract.return_value = {
            "classification": "Atomic",
            "intent_type": "BookFlightIntent",
            "action": "handle",
            "confidence": 0.95,
            "reason": "Single clear intent",
        }

        result = _parse_classification_response("mock response", "Book a flight")

        assert result["chunk_text"] == "Book a flight"
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["intent_type"] == "BookFlightIntent"
        assert result["action"] == IntentAction.HANDLE
        assert result["metadata"]["confidence"] == 0.95
        assert result["metadata"]["reason"] == "Single clear intent"

    @patch("intent_kit.node.classifiers.chunk_classifier.extract_json_from_text")
    @patch("intent_kit.node.classifiers.chunk_classifier._manual_parse_classification")
    def test_parse_missing_fields(self, mock_manual, mock_extract):
        """Test parsing response with missing fields."""
        mock_extract.return_value = {
            "classification": "Atomic",
            "action": "handle",
            # Missing confidence and reason
        }
        mock_manual.return_value = {
            "chunk_text": "Book a flight",
            "classification": IntentClassification.ATOMIC,
            "intent_type": None,
            "action": IntentAction.HANDLE,
            "metadata": {"confidence": 0.7, "reason": "Manually parsed"},
        }

        result = _parse_classification_response("mock response", "Book a flight")

        mock_manual.assert_called_once_with("mock response", "Book a flight")
        assert result["classification"] == IntentClassification.ATOMIC

    @patch("intent_kit.node.classifiers.chunk_classifier.extract_json_from_text")
    @patch("intent_kit.node.classifiers.chunk_classifier._manual_parse_classification")
    def test_parse_invalid_enum_values(self, mock_manual, mock_extract):
        """Test parsing response with invalid enum values."""
        mock_extract.return_value = {
            "classification": "InvalidClassification",
            "action": "invalid_action",
            "confidence": 0.95,
            "reason": "test",
        }
        mock_manual.return_value = {
            "chunk_text": "Book a flight",
            "classification": IntentClassification.ATOMIC,
            "intent_type": None,
            "action": IntentAction.HANDLE,
            "metadata": {"confidence": 0.7, "reason": "Manually parsed"},
        }

        result = _parse_classification_response("mock response", "Book a flight")

        mock_manual.assert_called_once_with("mock response", "Book a flight")
        assert result["classification"] == IntentClassification.ATOMIC

    @patch("intent_kit.node.classifiers.chunk_classifier.extract_json_from_text")
    @patch("intent_kit.node.classifiers.chunk_classifier._manual_parse_classification")
    def test_parse_invalid_confidence(self, mock_manual, mock_extract):
        """Test parsing response with invalid confidence value."""
        mock_extract.return_value = {
            "classification": "Atomic",
            "action": "handle",
            "confidence": "not_a_number",
            "reason": "test",
        }
        mock_manual.return_value = {
            "chunk_text": "Book a flight",
            "classification": IntentClassification.ATOMIC,
            "intent_type": None,
            "action": IntentAction.HANDLE,
            "metadata": {"confidence": 0.7, "reason": "Manually parsed"},
        }

        result = _parse_classification_response("mock response", "Book a flight")

        mock_manual.assert_called_once_with("mock response", "Book a flight")
        assert result["classification"] == IntentClassification.ATOMIC

    @patch("intent_kit.node.classifiers.chunk_classifier.extract_json_from_text")
    @patch("intent_kit.node.classifiers.chunk_classifier._manual_parse_classification")
    def test_parse_no_json_found(self, mock_manual, mock_extract):
        """Test parsing when no JSON is found."""
        mock_extract.return_value = None
        mock_manual.return_value = {
            "chunk_text": "Book a flight",
            "classification": IntentClassification.ATOMIC,
            "intent_type": None,
            "action": IntentAction.HANDLE,
            "metadata": {"confidence": 0.7, "reason": "Manually parsed"},
        }

        result = _parse_classification_response("mock response", "Book a flight")

        mock_manual.assert_called_once_with("mock response", "Book a flight")
        assert result["classification"] == IntentClassification.ATOMIC


class TestManualParseClassification:
    """Test the _manual_parse_classification function."""

    @patch("intent_kit.node.classifiers.chunk_classifier.extract_key_value_pairs")
    def test_manual_parse_with_key_value_pairs(self, mock_extract):
        """Test manual parsing with key-value pairs."""
        mock_extract.return_value = {
            "classification": "Atomic",
            "intent_type": "BookFlightIntent",
            "action": "handle",
            "confidence": "0.95",
            "reason": "Single clear intent",
        }

        result = _manual_parse_classification("mock response", "Book a flight")

        assert result["chunk_text"] == "Book a flight"
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["intent_type"] == "BookFlightIntent"
        assert result["action"] == IntentAction.HANDLE
        assert result["metadata"]["confidence"] == 0.95
        assert result["metadata"]["reason"] == "Single clear intent"

    @patch("intent_kit.node.classifiers.chunk_classifier.extract_key_value_pairs")
    def test_manual_parse_missing_fields(self, mock_extract):
        """Test manual parsing with missing fields."""
        mock_extract.return_value = {
            "classification": "Atomic"
            # Missing other fields
        }

        result = _manual_parse_classification("mock response", "Book a flight")

        # Should fall back to keyword matching, but "mock response" has no keywords
        # so it defaults to INVALID
        assert result["classification"] == IntentClassification.INVALID
        assert result["action"] == IntentAction.REJECT

    def test_manual_parse_atomic_keywords(self):
        """Test manual parsing with atomic keywords."""
        result = _manual_parse_classification(
            "This is an atomic single intent", "Book a flight"
        )

        assert result["classification"] == IntentClassification.ATOMIC
        assert result["action"] == IntentAction.HANDLE
        assert result["metadata"]["reason"] == "Manually parsed as atomic"

    def test_manual_parse_composite_keywords(self):
        """Test manual parsing with composite keywords."""
        result = _manual_parse_classification(
            "This is a composite split intent", "Book a flight"
        )

        assert result["classification"] == IntentClassification.COMPOSITE
        assert result["action"] == IntentAction.SPLIT
        assert result["metadata"]["reason"] == "Manually parsed as composite"

    def test_manual_parse_ambiguous_keywords(self):
        """Test manual parsing with ambiguous keywords."""
        result = _manual_parse_classification(
            "This is an ambiguous clarify intent", "Book a flight"
        )

        assert result["classification"] == IntentClassification.AMBIGUOUS
        assert result["action"] == IntentAction.CLARIFY
        assert result["metadata"]["reason"] == "Manually parsed as ambiguous"

    def test_manual_parse_no_keywords(self):
        """Test manual parsing with no keywords."""
        result = _manual_parse_classification(
            "Random text without keywords", "Book a flight"
        )

        assert result["classification"] == IntentClassification.INVALID
        assert result["action"] == IntentAction.REJECT
        assert result["metadata"]["reason"] == "Manually parsed as invalid"


class TestFallbackClassify:
    """Test the _fallback_classify function."""

    def test_fallback_classify_short_text(self):
        """Test fallback classification for short text."""
        result = _fallback_classify("Hi")

        assert result["classification"] == IntentClassification.AMBIGUOUS
        assert result["action"] == IntentAction.CLARIFY
        assert result["metadata"]["reason"] == "Too short to classify"

    def test_fallback_classify_single_word(self):
        """Test fallback classification for single word."""
        result = _fallback_classify("Hello")

        assert result["classification"] == IntentClassification.AMBIGUOUS
        assert result["action"] == IntentAction.CLARIFY

    def test_fallback_classify_and_conjunction(self):
        """Test fallback classification with 'and' conjunction."""
        result = _fallback_classify("Cancel my flight and update my email")

        assert result["classification"] == IntentClassification.COMPOSITE
        assert result["action"] == IntentAction.SPLIT
        assert "conjunction" in result["metadata"]["reason"]

    def test_fallback_classify_plus_conjunction(self):
        """Test fallback classification with 'plus' conjunction."""
        result = _fallback_classify("Book a flight plus get weather")

        assert result["classification"] == IntentClassification.COMPOSITE
        assert result["action"] == IntentAction.SPLIT

    def test_fallback_classify_also_conjunction(self):
        """Test fallback classification with 'also' conjunction."""
        result = _fallback_classify("Book a flight also get weather")

        assert result["classification"] == IntentClassification.COMPOSITE
        assert result["action"] == IntentAction.SPLIT

    def test_fallback_classify_conjunction_no_action_verbs(self):
        """Test fallback classification with conjunction but no action verbs."""
        result = _fallback_classify("Hello and goodbye")

        # Should default to atomic since no action verbs
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["action"] == IntentAction.HANDLE

    def test_fallback_classify_normal_text(self):
        """Test fallback classification for normal text."""
        result = _fallback_classify("Book a flight to New York")

        assert result["classification"] == IntentClassification.ATOMIC
        assert result["action"] == IntentAction.HANDLE
        assert result["metadata"]["reason"] == "Single clear intent detected"

    def test_fallback_classify_case_insensitive(self):
        """Test fallback classification is case insensitive."""
        result = _fallback_classify("CANCEL my flight AND update my email")

        assert result["classification"] == IntentClassification.COMPOSITE
        assert result["action"] == IntentAction.SPLIT

    def test_fallback_classify_multiple_conjunctions(self):
        """Test fallback classification with multiple conjunctions."""
        result = _fallback_classify("Cancel flight and update email and get weather")

        # Current logic only checks for single conjunctions, so this defaults to atomic
        # since "update email and get weather" doesn't contain recognized action verbs
        assert result["classification"] == IntentClassification.ATOMIC
        assert result["action"] == IntentAction.HANDLE


class TestChunkClassifierIntegration:
    """Integration tests for chunk classifier."""

    def test_classify_various_input_types(self):
        """Test classification with various input types."""
        # String input
        result1 = classify_intent_chunk("Book a flight")
        assert result1["classification"] == IntentClassification.ATOMIC

        # Dict input
        result2 = classify_intent_chunk({"text": "Book a flight"})
        assert result2["classification"] == IntentClassification.ATOMIC

        # Object with __str__ method
        class MockChunk:
            def __str__(self):
                return "Book a flight"

        result3 = classify_intent_chunk(MockChunk())
        assert result3["classification"] == IntentClassification.ATOMIC

    def test_classify_edge_cases(self):
        """Test classification with edge cases."""
        # Very long text
        long_text = "Book a flight " * 100
        result = classify_intent_chunk(long_text)
        assert result["classification"] == IntentClassification.ATOMIC

        # Text with special characters
        special_text = "Book a flight with 'quotes' and \"double quotes\" and & symbols"
        result = classify_intent_chunk(special_text)
        assert result["classification"] == IntentClassification.ATOMIC
