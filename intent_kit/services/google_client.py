"""
Google GenAI client wrapper for intent-kit
"""

from intent_kit.utils.logger import Logger
from intent_kit.services.base_client import BaseLLMClient
from typing import Optional
from intent_kit.types import LLMResponse
from intent_kit.utils.perf_util import PerfUtil

# Dummy assignment for testing
google = None

logger = Logger("google_service")


class GoogleClient(BaseLLMClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        super().__init__(api_key=api_key)

    def _initialize_client(self, **kwargs) -> None:
        """Initialize the Google GenAI client."""
        self._client = self.get_client()

    @classmethod
    def is_available(cls) -> bool:
        """Check if Google GenAI package is available."""
        try:
            # Only check for import, do not actually use it
            import importlib.util

            return importlib.util.find_spec("google.genai") is not None
        except ImportError:
            return False

    def get_client(self):
        """Get the Google GenAI client."""
        try:
            from google import genai

            return genai.Client(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Google GenAI package not installed. Install with: pip install google-genai"
            )

    def _ensure_imported(self):
        """Ensure the Google GenAI package is imported."""
        if self._client is None:
            self._client = self.get_client()

    def generate(self, prompt: str, model: Optional[str] = None) -> LLMResponse:
        """Generate text using Google's Gemini model."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "gemini-2.0-flash-lite"
        perf_util = PerfUtil("google_generate")
        perf_util.start()
        try:
            from google.genai import types

            content = types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            )
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
            )

            response = self._client.models.generate_content(
                model=model,
                contents=content,
                config=generate_content_config,
            )

            logger.debug(f"Google generate response: {response.text}")
            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
            else:
                input_tokens = 0
                output_tokens = 0
            duration = perf_util.stop()
            return LLMResponse(
                output=str(response.text) if response.text else "",
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=0.0,
                provider="google",
                duration=duration,
            )

        except Exception as e:
            logger.error(f"Error generating text with Google GenAI: {e}")
            raise
