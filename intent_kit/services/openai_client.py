"""
OpenAI client wrapper for intent-kit
"""

from intent_kit.utils.logger import Logger
from intent_kit.services.base_client import BaseLLMClient
from typing import Optional
from intent_kit.types import LLMResponse
from intent_kit.utils.perf_util import PerfUtil

# Dummy assignment for testing
openai = None

logger = Logger("openai_service")


class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        super().__init__(api_key=api_key)

    def _initialize_client(self, **kwargs) -> None:
        """Initialize the OpenAI client."""
        self._client = self.get_client()

    @classmethod
    def is_available(cls) -> bool:
        """Check if OpenAI package is available."""
        try:
            # Only check for import, do not actually use it
            import importlib.util

            return importlib.util.find_spec("openai") is not None
        except ImportError:
            return False

    def get_client(self):
        """Get the OpenAI client."""
        try:
            import openai

            return openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

    def _ensure_imported(self):
        """Ensure the OpenAI package is imported."""
        if self._client is None:
            self._client = self.get_client()

    def generate(self, prompt: str, model: Optional[str] = None) -> LLMResponse:
        """Generate text using OpenAI's GPT model."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "gpt-4"
        perf_util = PerfUtil("openai_generate")
        perf_util.start()
        response = self._client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1000
        )
        duration = perf_util.stop()
        if not response.choices:
            return LLMResponse(
                output="",
                model=model,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                provider="openai",
                duration=0.0,
            )
        content = response.choices[0].message.content
        if response.usage:
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
        else:
            input_tokens = 0
            output_tokens = 0
        duration = perf_util.stop()
        return LLMResponse(
            output=content,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=0.0,
            provider="openai",
            duration=duration,
        )
