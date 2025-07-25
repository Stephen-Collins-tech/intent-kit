# Ollama client wrapper for intent-kit
# Requires: pip install ollama

from intent_kit.utils.logger import Logger
from intent_kit.services.base_client import BaseLLMClient
from typing import Optional

logger = Logger("ollama_service")


class OllamaClient(BaseLLMClient):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        super().__init__(base_url=base_url)

    def _initialize_client(self, **kwargs) -> None:
        """Initialize the Ollama client."""
        self._client = self.get_client()

    def get_client(self):
        """Get the Ollama client."""
        try:
            from ollama import Client

            return Client(host=self.base_url)
        except ImportError:
            raise ImportError(
                "Ollama package not installed. Install with: pip install ollama"
            )

    def _ensure_imported(self):
        """Ensure the Ollama package is imported."""
        if self._client is None:
            self._client = self.get_client()

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text using Ollama's LLM model."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "llama2"
        response = self._client.generate(
            model=model,
            prompt=prompt,
        )
        result = response.get("response", "")
        return result if result is not None else ""

    def generate_stream(self, prompt: str, model: str = "llama2"):
        """Generate text using Ollama model with streaming."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            for chunk in self._client.generate(model=model, prompt=prompt, stream=True):
                yield chunk["response"]
        except Exception as e:
            logger.error(f"Error streaming with Ollama: {e}")
            raise

    def chat(self, messages: list, model: str = "llama2") -> str:
        """Chat with Ollama model using messages format."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            response = self._client.chat(model=model, messages=messages)
            content = response["message"]["content"]
            logger.debug(f"Ollama chat response: {content}")
            return str(content) if content else ""
        except Exception as e:
            logger.error(f"Error chatting with Ollama: {e}")
            raise

    def chat_stream(self, messages: list, model: str = "llama2"):
        """Chat with Ollama model using messages format with streaming."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            for chunk in self._client.chat(model=model, messages=messages, stream=True):
                yield chunk["message"]["content"]
        except Exception as e:
            logger.error(f"Error streaming chat with Ollama: {e}")
            raise

    def list_models(self):
        """List available models on the Ollama server."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            models_response = self._client.list()
            logger.debug(f"Ollama list response: {models_response}")

            # The correct type is ListResponse, which has a .models attribute
            if hasattr(models_response, "models"):
                models = models_response.models
            else:
                logger.error(f"Unexpected response structure: {models_response}")
                return []

            # Each model is a ListResponse.Model with a .model attribute
            model_names = []
            for model in models:
                if hasattr(model, "model") and model.model:
                    model_names.append(model.model)
                elif isinstance(model, dict) and "model" in model:
                    model_names.append(model["model"])
                elif isinstance(model, str):
                    model_names.append(model)
                else:
                    logger.warning(f"Unexpected model entry: {model}")

            model_names = [name for name in model_names if name]
            logger.debug(f"Extracted model names: {model_names}")
            return model_names

        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []

    def show_model(self, model: str):
        """Show model information."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            return self._client.show(model)
        except Exception as e:
            logger.error(f"Error showing model {model}: {e}")
            raise

    def pull_model(self, model: str):
        """Pull a model from the Ollama library."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            return self._client.pull(model)
        except Exception as e:
            logger.error(f"Error pulling model {model}: {e}")
            raise

    @classmethod
    def is_available(cls) -> bool:
        """Check if Ollama package is available."""
        try:
            import importlib.util

            return importlib.util.find_spec("ollama") is not None
        except ImportError:
            return False
