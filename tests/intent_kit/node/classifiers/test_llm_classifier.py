import pytest
from intent_kit.node.classifiers.llm_classifier import (
    create_llm_classifier,
    create_llm_arg_extractor,
    get_default_classification_prompt,
    get_default_extraction_prompt,
)
from intent_kit.services.base_client import BaseLLMClient
from intent_kit.node.base import TreeNode
from typing import List, cast
from intent_kit.types import LLMResponse
from intent_kit.node.types import ExecutionResult


class DummyChild(TreeNode):
    def __init__(self, name):
        super().__init__(name=name, description="dummy")

    def execute(self, user_input, context=None):
        return None


class DummyLLMClient(BaseLLMClient):
    def __init__(self, response):
        super().__init__()
        self._response = response

    def generate(self, prompt, model=None):
        # Return an LLMResponse object instead of a string
        return LLMResponse(
            output=self._response,
            model=model or "dummy-model",
            input_tokens=10,
            output_tokens=5,
            cost=0.0,
            provider="dummy",
            duration=0.1,
        )

    def _initialize_client(self, **kwargs):
        return self

    def get_client(self):
        return self

    def get_model(self):
        return None

    def _ensure_imported(self):
        pass


def test_create_llm_classifier_exact_match():
    children = [DummyChild("weather"), DummyChild("cancel")]
    llm_config = DummyLLMClient("weather")
    prompt = "{user_input}\n{node_descriptions}\n{context_info}\n"
    node_descs = ["weather: Weather handler", "cancel: Cancel handler"]
    classifier = create_llm_classifier(llm_config, prompt, node_descs)
    result = classifier("What's the weather?", cast(List[TreeNode], children), None)
    # Now expect an ExecutionResult with chosen_child parameter
    assert isinstance(result, ExecutionResult)
    assert result.success
    assert result.params and result.params.get("chosen_child") == "weather"


def test_create_llm_classifier_partial_match():
    children = [DummyChild("weather"), DummyChild("cancel")]
    llm_config = DummyLLMClient("cancel handler")
    prompt = "{user_input}\n{node_descriptions}\n{context_info}\n"
    node_descs = ["weather: Weather handler", "cancel: Cancel handler"]
    classifier = create_llm_classifier(llm_config, prompt, node_descs)
    result = classifier("Cancel my booking", cast(List[TreeNode], children), None)
    # Now expect an ExecutionResult with chosen_child parameter
    assert isinstance(result, ExecutionResult)
    assert result.success
    assert result.params and result.params.get("chosen_child") == "cancel"


def test_create_llm_classifier_no_match():
    children = [DummyChild("weather"), DummyChild("cancel")]
    llm_config = DummyLLMClient("unknown")
    prompt = "{user_input}\n{node_descriptions}\n{context_info}\n"
    node_descs = ["weather: Weather handler", "cancel: Cancel handler"]
    classifier = create_llm_classifier(llm_config, prompt, node_descs)
    result = classifier("Unrelated input", cast(List[TreeNode], children), None)
    # Now expect an ExecutionResult that indicates no match
    assert isinstance(result, ExecutionResult)
    assert not result.success


def test_create_llm_classifier_error():
    children = [DummyChild("weather"), DummyChild("cancel")]

    class ErrorLLM(BaseLLMClient):
        def __init__(self):
            super().__init__()

        def generate(self, prompt, model=None):
            raise Exception("LLM error")

        def _initialize_client(self, **kwargs):
            return self

        def get_client(self):
            return self

        def get_model(self):
            return None

        def _ensure_imported(self):
            pass

    llm_config = ErrorLLM()
    prompt = "{user_input}\n{node_descriptions}\n{context_info}\n"
    node_descs = ["weather: Weather handler", "cancel: Cancel handler"]
    classifier = create_llm_classifier(llm_config, prompt, node_descs)
    result = classifier("What's the weather?", cast(List[TreeNode], children), None)
    # Now expect an ExecutionResult with error
    assert isinstance(result, ExecutionResult)
    assert not result.success
    assert result.error is not None


def test_create_llm_arg_extractor_basic():
    llm_config = DummyLLMClient("destination: Paris\ndate: tomorrow")
    prompt = "{user_input}\n{param_descriptions}\n{context_info}\n"
    param_schema = {"destination": str, "date": str}
    extractor = create_llm_arg_extractor(llm_config, prompt, param_schema)
    result = extractor("Book a flight to Paris tomorrow", None)
    # Now expect an ExecutionResult
    assert isinstance(result, ExecutionResult)
    assert result.success
    assert result.params is not None
    assert result.params["destination"] == "Paris"
    assert result.params["date"] == "tomorrow"


def test_create_llm_arg_extractor_missing_param():
    llm_config = DummyLLMClient("destination: Paris")
    prompt = "{user_input}\n{param_descriptions}\n{context_info}\n"
    param_schema = {"destination": str, "date": str}
    extractor = create_llm_arg_extractor(llm_config, prompt, param_schema)
    result = extractor("Book a flight to Paris", None)
    # Now expect an ExecutionResult
    assert isinstance(result, ExecutionResult)
    assert result.success
    assert result.params is not None
    assert result.params["destination"] == "Paris"
    assert "date" not in result.params


def test_create_llm_arg_extractor_error():
    class ErrorLLM(BaseLLMClient):
        def __init__(self):
            super().__init__()

        def generate(self, prompt, model=None):
            raise Exception("LLM error")

        def _initialize_client(self, **kwargs):
            return self

        def get_client(self):
            return self

        def get_model(self):
            return None

        def _ensure_imported(self):
            pass

    llm_config = ErrorLLM()
    prompt = "{user_input}\n{param_descriptions}\n{context_info}\n"
    param_schema = {"destination": str}
    extractor = create_llm_arg_extractor(llm_config, prompt, param_schema)
    with pytest.raises(Exception):
        extractor("Book a flight to Paris", None)


def test_get_default_classification_prompt():
    prompt = get_default_classification_prompt()
    assert isinstance(prompt, str)
    assert "{user_input}" in prompt
    assert "{node_descriptions}" in prompt


def test_get_default_extraction_prompt():
    prompt = get_default_extraction_prompt()
    assert isinstance(prompt, str)
    assert "{user_input}" in prompt
    assert "{param_descriptions}" in prompt
