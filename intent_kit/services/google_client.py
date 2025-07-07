# Google GenAI client wrapper for intent-kit
# Requires: pip install google-genai

from intent_kit.utils.logger import Logger

logger = Logger("google_service")


class GoogleClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = self.get_client()

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
            try:
                from google import genai

                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Google GenAI package not installed. Install with: pip install google-genai"
                )

    def generate(self, prompt: str, model: str = "gemini-2.0-flash-lite") -> str:
        """Generate text using Google's Gemini model."""
        self._ensure_imported()

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

            logger.debug(f"Google generate_text response: {response.text}")
            return str(response.text) if response.text else ""

        except Exception as e:
            logger.error(f"Error generating text with Google GenAI: {e}")
            raise
