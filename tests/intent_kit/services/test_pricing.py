"""
Tests for pricing classes.
"""

import pytest

from intent_kit.services.ai.pricing import (
    ModelPricing,
    PricingConfig,
    PricingService,
)


class TestModelPricing:
    """Test the ModelPricing dataclass."""

    def test_model_pricing_creation(self):
        """Test creating a ModelPricing instance."""
        pricing = ModelPricing(
            input_price_per_1m=0.001,
            output_price_per_1m=0.002,
            model_name="gpt-4",
            provider="openai",
            last_updated="2024-01-01",
        )

        assert pricing.input_price_per_1m == 0.001
        assert pricing.output_price_per_1m == 0.002
        assert pricing.model_name == "gpt-4"
        assert pricing.provider == "openai"
        assert pricing.last_updated == "2024-01-01"

    def test_model_pricing_equality(self):
        """Test ModelPricing equality."""
        pricing1 = ModelPricing(
            input_price_per_1m=0.001,
            output_price_per_1m=0.002,
            model_name="gpt-4",
            provider="openai",
            last_updated="2024-01-01",
        )
        pricing2 = ModelPricing(
            input_price_per_1m=0.001,
            output_price_per_1m=0.002,
            model_name="gpt-4",
            provider="openai",
            last_updated="2024-01-01",
        )

        assert pricing1 == pricing2

    def test_model_pricing_inequality(self):
        """Test ModelPricing inequality."""
        pricing1 = ModelPricing(
            input_price_per_1m=0.001,
            output_price_per_1m=0.002,
            model_name="gpt-4",
            provider="openai",
            last_updated="2024-01-01",
        )
        pricing2 = ModelPricing(
            input_price_per_1m=0.002,  # Different price
            output_price_per_1m=0.002,
            model_name="gpt-4",
            provider="openai",
            last_updated="2024-01-01",
        )

        assert pricing1 != pricing2


class TestPricingConfig:
    """Test the PricingConfig dataclass."""

    def test_pricing_config_creation(self):
        """Test creating a PricingConfig instance."""
        default_pricing = {
            "gpt-4": ModelPricing(
                input_price_per_1m=0.001,
                output_price_per_1m=0.002,
                model_name="gpt-4",
                provider="openai",
                last_updated="2024-01-01",
            )
        }
        custom_pricing = {
            "custom-model": ModelPricing(
                input_price_per_1m=0.0005,
                output_price_per_1m=0.001,
                model_name="custom-model",
                provider="custom",
                last_updated="2024-01-01",
            )
        }

        config = PricingConfig(
            default_pricing=default_pricing,
            custom_pricing=custom_pricing,
        )

        assert len(config.default_pricing) == 1
        assert len(config.custom_pricing) == 1
        assert "gpt-4" in config.default_pricing
        assert "custom-model" in config.custom_pricing

    def test_pricing_config_empty(self):
        """Test creating a PricingConfig with empty pricing."""
        config = PricingConfig(default_pricing={}, custom_pricing={})

        assert len(config.default_pricing) == 0
        assert len(config.custom_pricing) == 0


class TestPricingService:
    """Test the PricingService abstract base class."""

    def test_pricing_service_can_be_instantiated(self):
        """Test that PricingService can be instantiated (uses NotImplementedError)."""
        service = PricingService()
        assert isinstance(service, PricingService)

    def test_pricing_service_calculate_cost_raises_not_implemented(self):
        """Test that calculate_cost method raises NotImplementedError."""
        service = PricingService()
        with pytest.raises(
            NotImplementedError, match="Subclasses must implement calculate_cost\\(\\)"
        ):
            service.calculate_cost("gpt-4", "openai", 100, 50)

    def test_pricing_service_implementation(self):
        """Test a concrete implementation of PricingService."""

        class ConcretePricingService(PricingService):
            def calculate_cost(
                self,
                model: str,
                provider: str,
                input_tokens: int,
                output_tokens: int,
            ) -> float:
                return 0.01

        service = ConcretePricingService()
        cost = service.calculate_cost("gpt-4", "openai", 100, 50)
        assert cost == 0.01
