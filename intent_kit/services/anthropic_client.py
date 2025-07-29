"""
Anthropic Claude client wrapper for intent-kit.
"""

from intent_kit.utils.logger import Logger
from intent_kit.services.base_client import BaseLLMClient
from intent_kit.types import LLMResponse
from typing import Optional
from intent_kit.utils.perf_util import PerfUtil

# Dummy assignment for testing
anthropic = None

logger = Logger("anthropic_service")


class AnthropicClient(BaseLLMClient):
    def __init__(self, api_key: str):
        if not api_key:
            raise TypeError("API key is required")
        self.api_key = api_key
        super().__init__(api_key=api_key)

    def _initialize_client(self, **kwargs) -> None:
        """Initialize the Anthropic client."""
        self._client = self.get_client()

    def get_client(self):
        """Get the Anthropic client."""
        try:
            import anthropic

            return anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )

    def _ensure_imported(self):
        """Ensure the Anthropic package is imported."""
        if self._client is None:
            self._client = self.get_client()

    def generate(self, prompt: str, model: Optional[str] = None) -> LLMResponse:
        """Generate text using Anthropic's Claude model."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "claude-sonnet-4-20250514"
        perf_util = PerfUtil("anthropic_generate")
        perf_util.start()
        response = self._client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        if not response.content:
            return LLMResponse(
                output="",
                model=model,
                input_tokens=0,
                output_tokens=0,
                cost=0,
                provider="anthropic",
                duration=0.0,
            )
        if response.usage:
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
        else:
            input_tokens = 0
            output_tokens = 0
        cost = 0
        duration = perf_util.stop()
        return LLMResponse(
            output=str(response.content[0].text),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            provider="anthropic",
            duration=duration,
        )
