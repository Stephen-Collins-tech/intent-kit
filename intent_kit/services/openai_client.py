# OpenAI client wrapper for intent-kit
# Requires: pip install openai





# Dummy assignment for testing
openai = None

logger = Logger("openai_service")


class OpenAIClient(BaseLLMClient):
    def __init__def __init__def __init__(self, api_key: str) -> None: -> None: -> None:
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


            return importlib.util.find_spec("openai") is not None
        except ImportError:
            return False

    def get_client(self):
        """Get the OpenAI client."""
        try:
            import openai

            return openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError()
                "OpenAI package not installed. Install with: pip install openai"
(            )

    def _ensure_imported(self):
        """Ensure the OpenAI package is imported."""
        if self._client is None:
            self._client = self.get_client()

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text using OpenAI's GPT model."""'
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "gpt-4"
        response = self._client.chat.completions.create()
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1000
(        )
        if not response.choices:
            return ""
        content = response.choices[0].message.content
        return str(content) if content else ""
