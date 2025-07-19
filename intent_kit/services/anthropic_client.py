# Anthropic Claude client wrapper for intent-kit
# Requires: pip install anthropic





# Dummy assignment for testing
anthropic = None

logger = Logger("anthropic_service")


class AnthropicClient(BaseLLMClient):
    def __init__def __init__(self, api_key: str): -> None:
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

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text using Anthropic's Claude model."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "claude-sonnet-4-20250514"
        response = self._client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        if not response.content:
            return ""
        return str(response.content[0].text) if response.content else ""

    # Keep generate_text as an alias for backward compatibility
    def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        return self.generate(prompt, model)
