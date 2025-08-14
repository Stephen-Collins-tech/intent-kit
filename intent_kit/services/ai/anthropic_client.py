"""
Anthropic client wrapper for intent-kit
"""

from dataclasses import dataclass
from typing import Optional, List, TypeVar
from intent_kit.services.ai.base_client import (
    BaseLLMClient,
    PricingConfiguration,
    ProviderPricing,
    ModelPricing,
)
from intent_kit.services.ai.pricing_service import PricingService
from intent_kit.types import InputTokens, OutputTokens, Cost
from .llm_response import RawLLMResponse
from intent_kit.utils.perf_util import PerfUtil

T = TypeVar("T")

# Dummy assignment for testing
anthropic = None


@dataclass
class AnthropicUsage:
    """Anthropic usage structure."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class AnthropicMessage:
    """Anthropic message structure."""

    content: str
    role: str


@dataclass
class AnthropicResponse:
    """Anthropic response structure."""

    content: List[AnthropicMessage]
    usage: Optional[AnthropicUsage] = None


class AnthropicClient(BaseLLMClient):
    def __init__(self, api_key: str, pricing_service: Optional[PricingService] = None):
        if not api_key:
            raise TypeError("API key is required")
        self.api_key = api_key
        super().__init__(
            name="anthropic_service", api_key=api_key, pricing_service=pricing_service
        )

    def _create_pricing_config(self) -> PricingConfiguration:
        """Create the pricing configuration for Anthropic models."""
        config = PricingConfiguration()

        anthropic_provider = ProviderPricing("anthropic")
        anthropic_provider.models = {
            "claude-opus-4-20250514": ModelPricing(
                model_name="claude-opus-4-20250514",
                provider="anthropic",
                input_price_per_1m=3.0,
                output_price_per_1m=15.0,
                last_updated="2025-01-15",
            ),
            "claude-3-7-sonnet-20250219": ModelPricing(
                model_name="claude-3-7-sonnet-20250219",
                provider="anthropic",
                input_price_per_1m=3.0,
                output_price_per_1m=15.0,
                last_updated="2025-01-15",
            ),
            "claude-3-5-haiku-20241022": ModelPricing(
                model_name="claude-3-5-haiku-20241022",
                provider="anthropic",
                input_price_per_1m=0.8,
                output_price_per_1m=4.0,
                last_updated="2025-01-15",
            ),
        }
        config.providers["anthropic"] = anthropic_provider

        return config

    def _initialize_client(self, **kwargs) -> None:
        """Initialize the Anthropic client."""
        self._client = self.get_client()

    @classmethod
    def is_available(cls) -> bool:
        """Check if Anthropic package is available."""
        try:
            # Only check for import, do not actually use it
            import importlib.util

            return importlib.util.find_spec("anthropic") is not None
        except ImportError:
            return False

    def get_client(self):
        """Get the Anthropic client."""
        try:
            import anthropic

            return anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )
        except Exception as e:
            # pylint: disable=broad-exception-raised
            raise Exception(
                "Error initializing Anthropic client. Please check your API key and try again."
            ) from e

    def _ensure_imported(self):
        """Ensure the Anthropic package is imported."""
        if self._client is None:
            self._client = self.get_client()

    def _clean_response(self, content: str) -> str:
        """Clean the response content by removing newline characters and extra whitespace."""
        if not content:
            return ""

        # Remove newline characters and normalize whitespace
        cleaned = content.strip()

        return cleaned

    def generate(
        self, prompt: str, model: str = "claude-3-5-sonnet-20241022"
    ) -> RawLLMResponse:
        """Generate text using Anthropic's Claude model."""
        self._ensure_imported()
        assert self._client is not None
        model = model or "claude-3-5-sonnet-20241022"
        perf_util = PerfUtil("anthropic_generate")
        perf_util.start()

        try:
            response = self._client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract content from the response
            if not response.content:
                return RawLLMResponse(
                    content="",
                    model=model,
                    provider="anthropic",
                    input_tokens=0,
                    output_tokens=0,
                    cost=0,
                    duration=0.0,
                )

            # Extract text content from the first content item
            output_text = response.content[0].text if response.content else ""

            # Extract token information
            input_tokens = 0
            output_tokens = 0
            if response.usage:
                input_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
                output_tokens = getattr(response.usage, "completion_tokens", 0) or 0

            # Calculate cost using local pricing configuration
            cost = self.calculate_cost(model, "anthropic", input_tokens, output_tokens)

            duration = perf_util.stop()

            # Log cost information with cost per token
            self.logger.log_cost(
                cost=cost,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                provider="anthropic",
                model=model,
                duration=duration,
            )

            return RawLLMResponse(
                content=self._clean_response(output_text),
                model=model,
                provider="anthropic",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                duration=duration,
            )

        except Exception as e:
            self.logger.error(f"Error generating text with Anthropic: {e}")
            raise

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

        # Calculate cost using local pricing data
        input_cost = (input_tokens / 1_000_000) * model_pricing.input_price_per_1m
        output_cost = (output_tokens / 1_000_000) * model_pricing.output_price_per_1m
        total_cost = input_cost + output_cost

        return total_cost
