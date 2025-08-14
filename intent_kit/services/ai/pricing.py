"""
Pricing models and services for AI model cost calculation.
"""

from dataclasses import dataclass
from abc import ABC
from typing import Dict

# Type aliases
InputTokens = int
OutputTokens = int
Cost = float


@dataclass
class ModelPricing:
    """Pricing information for a specific model."""

    input_price_per_1m: float
    output_price_per_1m: float
    model_name: str
    provider: str
    last_updated: str  # ISO date string


@dataclass
class PricingConfig:
    """Configuration for model pricing."""

    default_pricing: Dict[str, ModelPricing]
    custom_pricing: Dict[str, ModelPricing]


class PricingService(ABC):
    """Abstract base class for pricing services."""

    def calculate_cost(
        self,
        model: str,
        provider: str,
        input_tokens: InputTokens,
        output_tokens: OutputTokens,
    ) -> Cost:
        """Abstract method to calculate the cost for a model usage using the pricing service."""
        raise NotImplementedError("Subclasses must implement calculate_cost()")
