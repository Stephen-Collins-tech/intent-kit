# Anthropic Claude client wrapper for intent-kit
# Requires: pip install anthropic

from intent_kit.utils.logger import Logger

logger = Logger("anthropic_service")


class AnthropicClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
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
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Anthropic package not installed. Install with: pip install anthropic"
                )

    def generate(self, prompt: str, model: str = "claude-sonnet-4-20250514") -> str:
        """Generate text using Anthropic's Claude model."""
        self._ensure_imported()
        response = self._client.messages.create(
            model=model, max_tokens=1000, messages=[{"role": "user", "content": prompt}]
        )
        content = response.content
        logger.debug(f"Anthropic generate response: {content}")
        return str(content) if content else ""

    # Keep generate_text as an alias for backward compatibility
    def generate_text(
        self, prompt: str, model: str = "claude-sonnet-4-20250514"
    ) -> str:
        """Alias for generate method (backward compatibility)."""
        return self.generate(prompt, model)
