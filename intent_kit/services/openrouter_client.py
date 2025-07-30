"""
OpenRouter client wrapper for intent-kit
"""

from intent_kit.utils.logger import Logger
from intent_kit.services.base_client import BaseLLMClient
from intent_kit.types import LLMResponse
from typing import Optional
from intent_kit.utils.perf_util import PerfUtil

logger = Logger("openrouter_service")


class OpenRouterClient(BaseLLMClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        super().__init__(api_key=api_key)

    def _initialize_client(self, **kwargs) -> None:
        """Initialize the OpenRouter client."""
        self._client = self.get_client()

    def get_client(self):
        """Get the OpenRouter client."""
        try:
            import openai

            return openai.OpenAI(
                api_key=self.api_key, base_url="https://openrouter.ai/api/v1"
            )
        except ImportError as e:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            ) from e
        except Exception as e:
            # pylint: disable=broad-exception-raised
            raise Exception(
                "Error initializing OpenRouter client. Please check your API key and try again."
            ) from e

    def _ensure_imported(self):
        """Ensure the OpenAI package is imported."""
        if self._client is None:
            self._client = self.get_client()

    def _clean_response(self, content: str) -> str:
        """Clean the response content by removing newline characters and extra whitespace."""
        if not content:
            return ""

        # Remove newline characters and normalize whitespace
        cleaned = content.strip()

        return cleaned

    def generate(self, prompt: str, model: Optional[str] = None) -> LLMResponse:
        """Generate text using OpenRouter's LLM model."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "openrouter-default"
        perf_util = PerfUtil("openrouter_generate")
        perf_util.start()
        response = self._client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        if not response.choices:
            return LLMResponse(
                output="",
                model=model,
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                provider="openrouter",
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
        logger.info(f"OpenRouter duration: {duration}")
        return LLMResponse(
            output=content,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=0.0,
            provider="openrouter",
            duration=duration,
        )
