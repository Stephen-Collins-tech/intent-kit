# OpenRouter client wrapper for intent-kit
# Requires: pip install openai





logger = Logger("openrouter_service")


class OpenRouterClient(BaseLLMClient):
    def __init__def __init__(self, api_key: str): -> None:
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
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )

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

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text using OpenRouter's LLM model."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "openrouter-default"
        response = self._client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        if not response.choices:
            return ""
        content = response.choices[0].message.content
        return str(content) if content else ""

    def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        return self.generate(prompt, model)
