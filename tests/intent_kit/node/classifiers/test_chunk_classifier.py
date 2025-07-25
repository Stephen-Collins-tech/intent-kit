from intent_kit.node.classifiers.chunk_classifier import classify_intent_chunk
from intent_kit.types import IntentClassification, IntentAction


class DummyLLMFactory:
    def __init__(self, response):
        self._response = response

    def generate_with_config(self, config, prompt):
        return self._response


def test_classify_intent_chunk_fallback_atomic(monkeypatch):
    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.ATOMIC
    assert result.get("action") == IntentAction.HANDLE


def test_classify_intent_chunk_fallback_composite(monkeypatch):
    chunk = {"text": "Cancel my flight and update my email"}
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.COMPOSITE
    assert result.get("action") == IntentAction.SPLIT


def test_classify_intent_chunk_fallback_ambiguous(monkeypatch):
    chunk = {"text": "Hi"}
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.AMBIGUOUS
    assert result.get("action") == IntentAction.CLARIFY


def test_classify_intent_chunk_empty(monkeypatch):
    chunk = {"text": "   "}
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.INVALID
    assert result.get("action") == IntentAction.REJECT


def test_classify_intent_chunk_llm_json(monkeypatch):
    # Patch LLMFactory.generate_with_config to return valid JSON
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: '{"classification": "Atomic", "intent_type": "BookFlightIntent", "action": "handle", "confidence": 0.95, "reason": "Single clear booking intent"}',
    )
    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    assert result.get("classification") == IntentClassification.ATOMIC
    assert result.get("action") == IntentAction.HANDLE
    assert result.get("metadata", {}).get("confidence") == 0.95


def test_classify_intent_chunk_llm_manual(monkeypatch):
    # Patch LLMFactory.generate_with_config to return non-JSON
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: "classification: Composite\naction: split\nconfidence: 0.8\nreason: Detected multi-intent",
    )
    chunk = {"text": "Cancel my flight and update my email"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    assert result.get("classification") == IntentClassification.COMPOSITE
    assert result.get("action") == IntentAction.SPLIT
    assert result.get("metadata", {}).get("confidence") == 0.8


def test_classify_intent_chunk_llm_exception(monkeypatch):
    # Patch LLMFactory.generate_with_config to raise Exception
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: (_ for _ in ()).throw(Exception("LLM error")),
    )
    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    assert result.get("classification") == IntentClassification.ATOMIC
    assert result.get("action") == IntentAction.HANDLE


def test_classify_intent_chunk_string_input():
    """Test classification with string input instead of dict."""
    chunk = "Book a flight to NYC"
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.ATOMIC
    assert result.get("action") == IntentAction.HANDLE
    assert result.get("chunk_text") == "Book a flight to NYC"


def test_classify_intent_chunk_dict_without_text():
    """Test classification with dict that doesn't have 'text' key."""
    chunk = {"other_key": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.ATOMIC
    assert result.get("action") == IntentAction.HANDLE


def test_classify_intent_chunk_empty_string():
    """Test classification with empty string."""
    chunk = {"text": ""}
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.INVALID
    assert result.get("action") == IntentAction.REJECT


def test_classify_intent_chunk_whitespace_only():
    """Test classification with whitespace-only string."""
    chunk = {"text": "   \n\t  "}
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.INVALID
    assert result.get("action") == IntentAction.REJECT


def test_classify_intent_chunk_single_word():
    """Test classification with single word."""
    chunk = {"text": "Hello"}
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.AMBIGUOUS
    assert result.get("action") == IntentAction.CLARIFY


def test_classify_intent_chunk_fallback_conjunctions():
    """Test fallback classification with various conjunctions."""
    conjunctions = ["and", "plus", "also"]

    for conj in conjunctions:
        chunk = {"text": f"Cancel my flight {conj} update my email"}
        result = classify_intent_chunk(chunk, llm_config=None)
        assert result.get("classification") == IntentClassification.COMPOSITE
        assert result.get("action") == IntentAction.SPLIT


def test_classify_intent_chunk_fallback_conjunctions_case_insensitive():
    """Test fallback classification with conjunctions in different cases."""
    chunk = {"text": "Cancel my flight AND update my email"}
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.COMPOSITE
    assert result.get("action") == IntentAction.SPLIT


def test_classify_intent_chunk_fallback_conjunctions_no_action_verbs():
    """Test fallback classification with conjunctions but no action verbs."""
    chunk = {"text": "red and blue"}
    result = classify_intent_chunk(chunk, llm_config=None)
    assert result.get("classification") == IntentClassification.ATOMIC
    assert result.get("action") == IntentAction.HANDLE


def test_classify_intent_chunk_llm_invalid_json(monkeypatch):
    """Test LLM classification with invalid JSON response."""
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: "This is not valid JSON at all",
    )

    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    # Should fall back to manual parsing
    assert result.get("classification") in [
        IntentClassification.ATOMIC,
        IntentClassification.COMPOSITE,
        IntentClassification.AMBIGUOUS,
        IntentClassification.INVALID,
    ]


def test_classify_intent_chunk_llm_missing_required_fields(monkeypatch):
    """Test LLM classification with JSON missing required fields."""
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        # Missing required fields
        lambda config, prompt: '{"classification": "Atomic"}',
    )

    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    # Should fall back to manual parsing
    assert result.get("classification") in [
        IntentClassification.ATOMIC,
        IntentClassification.COMPOSITE,
        IntentClassification.AMBIGUOUS,
        IntentClassification.INVALID,
    ]


def test_classify_intent_chunk_llm_invalid_classification(monkeypatch):
    """Test LLM classification with invalid classification value."""
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: '{"classification": "InvalidType", "action": "handle", "confidence": 0.5, "reason": "test"}',
    )

    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    # Should fall back to manual parsing
    assert result.get("classification") in [
        IntentClassification.ATOMIC,
        IntentClassification.COMPOSITE,
        IntentClassification.AMBIGUOUS,
        IntentClassification.INVALID,
    ]


def test_classify_intent_chunk_llm_invalid_action(monkeypatch):
    """Test LLM classification with invalid action value."""
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: '{"classification": "Atomic", "action": "invalid_action", "confidence": 0.5, "reason": "test"}',
    )

    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    # Should fall back to manual parsing
    assert result.get("classification") in [
        IntentClassification.ATOMIC,
        IntentClassification.COMPOSITE,
        IntentClassification.AMBIGUOUS,
        IntentClassification.INVALID,
    ]


def test_classify_intent_chunk_llm_invalid_confidence(monkeypatch):
    """Test LLM classification with invalid confidence value."""
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: '{"classification": "Atomic", "action": "handle", "confidence": "not_a_number", "reason": "test"}',
    )

    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    # Should fall back to manual parsing
    assert result.get("classification") in [
        IntentClassification.ATOMIC,
        IntentClassification.COMPOSITE,
        IntentClassification.AMBIGUOUS,
        IntentClassification.INVALID,
    ]


def test_classify_intent_chunk_manual_parsing_atomic(monkeypatch):
    """Test manual parsing with atomic classification keywords."""
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: "This is an atomic classification with single intent",
    )

    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    assert result.get("classification") == IntentClassification.ATOMIC
    assert result.get("action") == IntentAction.HANDLE


def test_classify_intent_chunk_manual_parsing_composite(monkeypatch):
    """Test manual parsing with composite classification keywords."""
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: "This is a composite classification that should be split",
    )

    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    assert result.get("classification") == IntentClassification.COMPOSITE
    assert result.get("action") == IntentAction.SPLIT


def test_classify_intent_chunk_manual_parsing_ambiguous(monkeypatch):
    """Test manual parsing with ambiguous classification keywords."""
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: "This is ambiguous and needs clarification",
    )

    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    assert result.get("classification") == IntentClassification.AMBIGUOUS
    assert result.get("action") == IntentAction.CLARIFY


def test_classify_intent_chunk_manual_parsing_default(monkeypatch):
    """Test manual parsing with no recognizable keywords."""
    from intent_kit.node.classifiers import chunk_classifier as mod

    monkeypatch.setattr(
        mod.LLMFactory,
        "generate_with_config",
        lambda config, prompt: "Some random response without classification keywords",
    )

    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config={"provider": "openai"})
    assert result.get("classification") == IntentClassification.INVALID
    assert result.get("action") == IntentAction.REJECT


def test_classify_intent_chunk_result_structure():
    """Test that the result has the expected structure."""
    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config=None)

    # Check required fields
    assert "chunk_text" in result
    assert "classification" in result
    assert "intent_type" in result
    assert "action" in result
    assert "metadata" in result

    # Check metadata structure
    metadata = result.get("metadata", {})
    assert "confidence" in metadata
    assert "reason" in metadata

    # Check types
    assert isinstance(result["chunk_text"], str)
    assert isinstance(result["classification"], IntentClassification)
    assert isinstance(result["action"], IntentAction)
    assert isinstance(metadata["confidence"], float)
    assert isinstance(metadata["reason"], str)


def test_classify_intent_chunk_confidence_range():
    """Test that confidence values are in the expected range."""
    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config=None)

    metadata = result.get("metadata", {})
    confidence = metadata["confidence"]
    assert 0.0 <= confidence <= 1.0


def test_classify_intent_chunk_reason_not_empty():
    """Test that reason field is not empty."""
    chunk = {"text": "Book a flight to NYC"}
    result = classify_intent_chunk(chunk, llm_config=None)

    metadata = result.get("metadata", {})
    reason = metadata["reason"]
    assert len(reason) > 0
    assert isinstance(reason, str)
