from intent_kit.node_library.action_node_llm import (
    extract_booking_args_llm,
    action_node_llm,
    booking_handler,
)
from intent_kit.context import IntentContext


def test_extract_booking_args_llm_mock_mode(monkeypatch):
    monkeypatch.setenv("INTENT_KIT_MOCK_MODE", "1")
    user_input = "Book a flight to Paris for next Friday"
    context = {"user_id": "testuser"}
    result = extract_booking_args_llm(user_input, context)
    assert result["destination"].lower() == "paris"
    assert result["date"].lower() == "next friday"
    assert result["user_id"] == "testuser"


def test_extract_booking_args_llm_fallback(monkeypatch):
    monkeypatch.delenv("INTENT_KIT_MOCK_MODE", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
    # Patch LLMFactory to raise Exception to force fallback

    class DummyLLMClient:
        def generate(self, prompt, model=None):
            raise Exception("LLM error")

    class DummyFactory:
        @staticmethod
        def create_client(config):
            return DummyLLMClient()

    monkeypatch.setattr("intent_kit.services.llm_factory.LLMFactory", DummyFactory)
    user_input = "Book a flight to Rome for the weekend"
    context = {"user_id": "testuser"}
    result = extract_booking_args_llm(user_input, context)
    assert result["destination"].lower() == "rome"
    assert result["date"].lower() == "the weekend"
    assert result["user_id"] == "testuser"


def test_booking_handler_and_context():
    context = IntentContext()
    result = booking_handler("Tokyo", "tomorrow", context)
    assert "Tokyo" in result
    assert "tomorrow" in result
    assert "Booking #1" in result
    # Context should be updated
    assert context.get("booking_count") == 1
    assert context.get("last_destination") == "Tokyo"


def test_action_node_llm_execute(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
    context = IntentContext()
    # The ActionNode expects params extracted by arg_extractor
    params = extract_booking_args_llm("Book a flight to Berlin", {"user_id": "u1"})
    # Simulate ActionNode param extraction and execution
    output = action_node_llm.action(params["destination"], params["date"], context)
    assert "Berlin" in output
    assert context.get("booking_count") == 1
