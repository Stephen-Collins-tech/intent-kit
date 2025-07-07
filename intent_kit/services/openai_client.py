# OpenAI client wrapper for intent-kit
# Requires: pip install openai

from intent_kit.utils.logger import Logger

logger = Logger("openai_service")


class OpenAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = self.get_client()

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
            try:
                import openai

                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )

    def generate(self, prompt: str, model: str = "gpt-4") -> str:
        """Generate text using OpenAI's GPT model."""
        self._ensure_imported()
        response = self._client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1000
        )
        content = response.choices[0].message.content
        return str(content) if content else ""

    # Keep generate_text as an alias for backward compatibility
    def generate_text(self, prompt: str, model: str = "gpt-4") -> str:
        """Alias for generate method (backward compatibility)."""
        return self.generate(prompt, model)
