"""
Pricing service for calculating LLM costs.
"""

from typing import Optional
from intent_kit.types import (
    PricingService as BasePricingService,
    ModelPricing,
    PricingConfig,
    InputTokens,
    OutputTokens,
    Cost,
)


class PricingService(BasePricingService):
    """Concrete implementation of the pricing service."""

    def __init__(self, pricing_config: Optional[PricingConfig] = None):
        """Initialize the pricing service with default or custom pricing."""
        self.pricing_config = pricing_config or self._create_default_pricing_config()

    def _create_default_pricing_config(self) -> PricingConfig:
        """Create default pricing configuration with common model prices."""
        default_pricing = {
            # OpenAI models
            "gpt-4": ModelPricing(
                input_price_per_1m=30.0,
                output_price_per_1m=60.0,
                model_name="gpt-4",
                provider="openai",
                last_updated="2024-01-01",
            ),
            "gpt-4-turbo": ModelPricing(
                input_price_per_1m=10.0,
                output_price_per_1m=30.0,
                model_name="gpt-4-turbo",
                provider="openai",
                last_updated="2024-01-01",
            ),
            "gpt-3.5-turbo": ModelPricing(
                input_price_per_1m=0.5,
                output_price_per_1m=1.5,
                model_name="gpt-3.5-turbo",
                provider="openai",
                last_updated="2024-01-01",
            ),
            # Anthropic models
            "claude-3-sonnet-20240229": ModelPricing(
                input_price_per_1m=3.0,
                output_price_per_1m=15.0,
                model_name="claude-3-sonnet-20240229",
                provider="anthropic",
                last_updated="2024-01-01",
            ),
            "claude-3-haiku-20240307": ModelPricing(
                input_price_per_1m=0.25,
                output_price_per_1m=1.25,
                model_name="claude-3-haiku-20240307",
                provider="anthropic",
                last_updated="2024-01-01",
            ),
            # Google models
            "gemini-pro": ModelPricing(
                input_price_per_1m=0.5,
                output_price_per_1m=1.5,
                model_name="gemini-pro",
                provider="google",
                last_updated="2024-01-01",
            ),
            "gemini-2.0-flash-lite": ModelPricing(
                input_price_per_1m=0.1,
                output_price_per_1m=0.3,
                model_name="gemini-2.0-flash-lite",
                provider="google",
                last_updated="2024-01-01",
            ),
            # OpenRouter models (common ones)
            "moonshotai/kimi-k2": ModelPricing(
                input_price_per_1m=0.5,
                output_price_per_1m=1.5,
                model_name="moonshotai/kimi-k2",
                provider="openrouter",
                last_updated="2024-01-01",
            ),
            "z-ai/glm-4.5": ModelPricing(
                input_price_per_1m=0.2,
                output_price_per_1m=0.6,
                model_name="z-ai/glm-4.5",
                provider="openrouter",
                last_updated="2024-01-01",
            ),
            "mistralai/mistral-7b-instruct": ModelPricing(
                input_price_per_1m=0.028,
                output_price_per_1m=0.054,
                model_name="mistralai/mistral-7b-instruct",
                provider="openrouter",
                last_updated="2024-01-01",
            ),
            "qwen/qwen3-32b": ModelPricing(
                input_price_per_1m=0.027,
                output_price_per_1m=0.027,
                model_name="qwen/qwen3-32b",
                provider="openrouter",
                last_updated="2024-01-01",
            ),
            "mistralai/devstral-small": ModelPricing(
                input_price_per_1m=0.07,
                output_price_per_1m=0.28,
                model_name="mistralai/devstral-small",
                provider="openrouter",
                last_updated="2024-01-01",
            ),
            "liquid/lfm-40b": ModelPricing(
                input_price_per_1m=0.15,
                output_price_per_1m=0.15,
                model_name="liquid/lfm-40b",
                provider="openrouter",
                last_updated="2024-01-01",
            ),
            # Ollama models (typically free)
            "llama2": ModelPricing(
                input_price_per_1m=0.0,
                output_price_per_1m=0.0,
                model_name="llama2",
                provider="ollama",
                last_updated="2024-01-01",
            ),
        }

        return PricingConfig(default_pricing=default_pricing, custom_pricing={})

    def get_model_pricing(
        self, model_name: str, provider: str
    ) -> Optional[ModelPricing]:
        """Get pricing information for a specific model."""
        # Check custom pricing first
        if model_name in self.pricing_config.custom_pricing:
            pricing = self.pricing_config.custom_pricing[model_name]
            if pricing.provider == provider:
                return pricing

        # Check default pricing
        if model_name in self.pricing_config.default_pricing:
            pricing = self.pricing_config.default_pricing[model_name]
            if pricing.provider == provider:
                return pricing

        return None

    def calculate_cost(
        self,
        model: str,
        provider: str,
        input_tokens: InputTokens,
        output_tokens: OutputTokens,
    ) -> Cost:
        """Calculate the cost for a model usage."""
        pricing = self.get_model_pricing(model, provider)

        if pricing is None:
            # Return 0.0 for unknown models
            return 0.0

        # Calculate cost: (tokens / 1M) * price_per_1M
        input_cost = (input_tokens / 1_000_000.0) * pricing.input_price_per_1m
        output_cost = (output_tokens / 1_000_000.0) * pricing.output_price_per_1m

        return input_cost + output_cost

    def add_custom_pricing(self, model_name: str, pricing: ModelPricing) -> None:
        """Add custom pricing for a model."""
        self.pricing_config.custom_pricing[model_name] = pricing
