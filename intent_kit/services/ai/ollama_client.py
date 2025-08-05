"""
Ollama client wrapper for intent-kit
"""

from dataclasses import dataclass
from typing import Optional
from intent_kit.services.ai.base_client import (
    BaseLLMClient,
    PricingConfiguration,
    ProviderPricing,
    ModelPricing,
)
from intent_kit.services.ai.pricing_service import PricingService
from intent_kit.types import LLMResponse, InputTokens, OutputTokens, Cost
from intent_kit.utils.perf_util import PerfUtil


@dataclass
class OllamaUsage:
    """Ollama usage structure."""

    prompt_eval_count: int
    eval_count: int
    total_count: int


@dataclass
class OllamaGenerateResponse:
    """Ollama generate response structure."""

    response: str
    usage: Optional[OllamaUsage] = None


@dataclass
class OllamaModel:
    """Ollama model structure."""

    model: str
    size: Optional[int] = None
    digest: Optional[str] = None
    modified_at: Optional[str] = None


class OllamaClient(BaseLLMClient):
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        pricing_service: Optional[PricingService] = None,
    ):
        self.base_url = base_url
        super().__init__(
            name="ollama_service", base_url=base_url, pricing_service=pricing_service
        )

    def _create_pricing_config(self) -> PricingConfiguration:
        """Create the pricing configuration for Ollama models."""
        config = PricingConfiguration()

        ollama_provider = ProviderPricing("ollama")
        ollama_provider.models = {
            "llama2": ModelPricing(
                model_name="llama2",
                provider="ollama",
                input_price_per_1m=0.0,  # Ollama is typically free
                output_price_per_1m=0.0,
                last_updated="2025-01-15",
            ),
            "llama3": ModelPricing(
                model_name="llama3",
                provider="ollama",
                input_price_per_1m=0.0,
                output_price_per_1m=0.0,
                last_updated="2025-01-15",
            ),
            "mistral": ModelPricing(
                model_name="mistral",
                provider="ollama",
                input_price_per_1m=0.0,
                output_price_per_1m=0.0,
                last_updated="2025-01-15",
            ),
            "codellama": ModelPricing(
                model_name="codellama",
                provider="ollama",
                input_price_per_1m=0.0,
                output_price_per_1m=0.0,
                last_updated="2025-01-15",
            ),
        }
        config.providers["ollama"] = ollama_provider

        return config

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
        except Exception as e:
            # pylint: disable=broad-exception-raised
            raise Exception(
                "Error initializing Ollama client. Please check your connection and try again."
            ) from e

    def _ensure_imported(self):
        """Ensure the Ollama package is imported."""
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
        """Generate text using Ollama's LLM model."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "llama2"
        perf_util = PerfUtil("ollama_generate")
        perf_util.start()

        try:
            response = self._client.generate(
                model=model,
                prompt=prompt,
            )

            # Convert to our custom dataclass structure
            usage = None
            if response.get("usage"):
                usage = OllamaUsage(
                    prompt_eval_count=response.get("usage").get("prompt_eval_count", 0),
                    eval_count=response.get("usage").get("eval_count", 0),
                    total_count=response.get("usage").get("prompt_eval_count", 0)
                    + response.get("usage").get("eval_count", 0),
                )

            ollama_response = OllamaGenerateResponse(
                response=response.get("response", ""),
                usage=usage,
            )

            # Extract token information
            if ollama_response.usage:
                input_tokens = ollama_response.usage.prompt_eval_count
                output_tokens = ollama_response.usage.eval_count
            else:
                input_tokens = 0
                output_tokens = 0

            # Calculate cost using local pricing configuration (Ollama is typically free)
            cost = self.calculate_cost(model, "ollama", input_tokens, output_tokens)

            duration = perf_util.stop()

            # Log cost information with cost per token
            self.logger.log_cost(
                cost=cost,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                provider="ollama",
                model=model,
                duration=duration,
            )

            response = LLMResponse(
                output=self._clean_response(ollama_response.response),
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,  # ollama is free...
                provider="ollama",
                duration=duration,
            )
            
            # Log audit entry
            self._log_audit_entry(response, prompt)
            
            return response

        except Exception as e:
            self.logger.error(f"Error generating text with Ollama: {e}")
            raise

    def generate_stream(self, prompt: str, model: str = "llama2"):
        """Generate text using Ollama model with streaming."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            for chunk in self._client.generate(model=model, prompt=prompt, stream=True):
                yield chunk["response"]
        except Exception as e:
            self.logger.error(f"Error streaming with Ollama: {e}")
            raise

    def chat(self, messages: list, model: str = "llama2") -> str:
        """Chat with Ollama model using messages format."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            response = self._client.chat(model=model, messages=messages)
            content = response["message"]["content"]
            self.logger.debug(f"Ollama chat response: {content}")
            return str(content) if content else ""
        except Exception as e:
            self.logger.error(f"Error chatting with Ollama: {e}")
            raise

    def chat_stream(self, messages: list, model: str = "llama2"):
        """Chat with Ollama model using messages format with streaming."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            for chunk in self._client.chat(model=model, messages=messages, stream=True):
                yield chunk["message"]["content"]
        except Exception as e:
            self.logger.error(f"Error streaming chat with Ollama: {e}")
            raise

    def list_models(self):
        """List available models on the Ollama server."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            models_response = self._client.list()
            self.logger.debug(f"Ollama list response: {models_response}")

            # The correct type is ListResponse, which has a .models attribute
            if hasattr(models_response, "models"):
                models = models_response.models
            else:
                self.logger.error(f"Unexpected response structure: {models_response}")
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
                    self.logger.warning(f"Unexpected model entry: {model}")

            model_names = [name for name in model_names if name]
            self.logger.debug(f"Extracted model names: {model_names}")
            return model_names

        except Exception as e:
            self.logger.error(f"Error listing Ollama models: {e}")
            return []

    def show_model(self, model: str):
        """Show model information."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            return self._client.show(model)
        except Exception as e:
            self.logger.error(f"Error showing model {model}: {e}")
            raise

    def pull_model(self, model: str):
        """Pull a model from the Ollama library."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        try:
            return self._client.pull(model)
        except Exception as e:
            self.logger.error(f"Error pulling model {model}: {e}")
            raise

    @classmethod
    def is_available(cls) -> bool:
        """Check if Ollama package is available."""
        try:
            import importlib.util

            return importlib.util.find_spec("ollama") is not None
        except ImportError:
            return False

    def calculate_cost(
        self,
        model: str,
        provider: str,
        input_tokens: InputTokens,
        output_tokens: OutputTokens,
    ) -> Cost:
        """Calculate the cost for a model usage using local pricing configuration."""
        # Get pricing from local configuration
        model_pricing = self.get_model_pricing(model)
        if model_pricing is None:
            self.logger.warning(
                f"No pricing found for model {model}, using base pricing service"
            )
            return super().calculate_cost(model, provider, input_tokens, output_tokens)

        # Calculate cost using local pricing data (Ollama is typically free)
        input_cost = (input_tokens / 1_000_000) * model_pricing.input_price_per_1m
        output_cost = (output_tokens / 1_000_000) * model_pricing.output_price_per_1m
        total_cost = input_cost + output_cost

        return total_cost
