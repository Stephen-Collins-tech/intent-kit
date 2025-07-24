from intent_kit.node_library.splitter_node_llm import split_text_llm, splitter_node_llm


def test_split_text_llm_mock_mode_and(monkeypatch):
    monkeypatch.setenv("INTENT_KIT_MOCK_MODE", "1")
    user_input = "Book a flight to Paris and check the weather in London"
    result = split_text_llm(user_input)
    assert len(result) == 2
    assert "paris" in result[0].lower()
    assert "weather" in result[1].lower()


def test_split_text_llm_mock_mode_no_conjunction(monkeypatch):
    monkeypatch.setenv("INTENT_KIT_MOCK_MODE", "1")
    user_input = "Just one request"
    result = split_text_llm(user_input)
    assert result == [user_input]


def test_split_text_llm_fallback(monkeypatch):
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
    user_input = "Book a flight to Paris and check the weather in London"
    result = split_text_llm(user_input)
    assert result == [user_input]


def test_splitter_node_llm_execute_mock(monkeypatch):
    monkeypatch.setenv("INTENT_KIT_MOCK_MODE", "1")
    user_input = "Book a flight to Paris and check the weather in London"
    result = splitter_node_llm.execute(user_input)
    assert getattr(result, "success", None) is True
    output = getattr(result, "output", None)
    assert isinstance(output, list)
    assert len(output) == 2
    assert "paris" in output[0].lower()
    assert "weather" in output[1].lower()


def test_splitter_node_llm_execute_fallback(monkeypatch):
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
    user_input = "Book a flight to Paris and check the weather in London"
    result = splitter_node_llm.execute(user_input)
    assert getattr(result, "success", None) is True
    output = getattr(result, "output", None)
    assert output == [user_input]
