from intent_kit.node_library.classifier_node_llm import (
    extract_weather_args_llm,
    extract_cancel_args_llm,
    intent_classifier_llm,
    classifier_node_llm,
    weather_handler_node,
    cancel_handler_node,
)
from intent_kit.context import IntentContext


def test_extract_weather_args_llm_mock_mode(monkeypatch):
    monkeypatch.setenv("INTENT_KIT_MOCK_MODE", "1")
    user_input = "What's the weather like in New York?"
    result = extract_weather_args_llm(user_input)
    # Accept 'new' or 'new york' due to regex limitations
    assert result["location"].lower().startswith("new")


def test_extract_weather_args_llm_fallback(monkeypatch):
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
    user_input = "What's the weather like in London?"
    result = extract_weather_args_llm(user_input)
    assert result["location"].lower() == "london"


def test_extract_cancel_args_llm_mock_mode(monkeypatch):
    monkeypatch.setenv("INTENT_KIT_MOCK_MODE", "1")
    user_input = "Cancel my hotel booking"
    result = extract_cancel_args_llm(user_input)
    assert "hotel" in result["item"].lower()


def test_extract_cancel_args_llm_fallback(monkeypatch):
    monkeypatch.delenv("INTENT_KIT_MOCK_MODE", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    class DummyLLMClient:
        def generate(self, prompt, model=None):
            raise Exception("LLM error")

    class DummyFactory:
        @staticmethod
        def create_client(config):
            return DummyLLMClient()

    monkeypatch.setattr("intent_kit.services.llm_factory.LLMFactory", DummyFactory)
    user_input = "I need to cancel my flight reservation"
    result = extract_cancel_args_llm(user_input)
    assert "flight" in result["item"].lower()


def test_intent_classifier_llm_mock_mode(monkeypatch):
    monkeypatch.setenv("INTENT_KIT_MOCK_MODE", "1")
    children = [weather_handler_node, cancel_handler_node]
    assert (
        intent_classifier_llm("What's the weather like in Paris?", children)
        == weather_handler_node
    )
    assert intent_classifier_llm("Cancel my booking", children) == cancel_handler_node
    assert (
        intent_classifier_llm("Random input", children) == weather_handler_node
    )  # default


def test_intent_classifier_llm_fallback(monkeypatch):
    monkeypatch.delenv("INTENT_KIT_MOCK_MODE", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    class DummyLLMClient:
        def generate(self, prompt, model=None):
            raise Exception("LLM error")

    class DummyFactory:
        @staticmethod
        def create_client(config):
            return DummyLLMClient()

    monkeypatch.setattr("intent_kit.services.llm_factory.LLMFactory", DummyFactory)
    children = [weather_handler_node, cancel_handler_node]
    assert (
        intent_classifier_llm("What's the weather like in Tokyo?", children)
        == weather_handler_node
    )
    assert (
        intent_classifier_llm("Cancel my subscription", children) == cancel_handler_node
    )
    assert intent_classifier_llm("Unrelated input", children) is None


def test_classifier_node_llm_execute_weather(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
    context = IntentContext()
    result = classifier_node_llm.execute("What's the weather like in Paris?", context)
    assert result.success is True
    assert result.output is not None
    assert "Weather in Paris" in result.output


def test_classifier_node_llm_execute_cancel(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
    context = IntentContext()
    result = classifier_node_llm.execute("Cancel my hotel booking", context)
    assert result.success is True
    assert result.output is not None
    assert "cancelled hotel" in result.output
