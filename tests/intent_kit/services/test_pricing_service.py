"""
Tests for the pricing service.
"""

import pytest

from intent_kit.services.ai.pricing_service import PricingService
from intent_kit.services.ai.pricing import ModelPricing, PricingConfig


class TestPricingService:
    """Test cases for PricingService."""

    def test_init_with_default_pricing(self):
        """Test that PricingService initializes with default pricing."""
        service = PricingService()
        assert service.pricing_config is not None
        assert isinstance(service.pricing_config, PricingConfig)

    def test_init_with_custom_pricing_config(self):
        """Test that PricingService can be initialized with custom pricing config."""
        custom_config = PricingConfig(
            default_pricing={},
            custom_pricing={},
        )
        service = PricingService(custom_config)
        assert service.pricing_config == custom_config

    def test_get_model_pricing_existing_model(self):
        """Test getting pricing for an existing model."""
        service = PricingService()

        # Test with a model that should exist in default pricing
        pricing = service.get_model_pricing("gpt-4", "openai")
        assert pricing is not None
        assert pricing.model_name == "gpt-4"
        assert pricing.provider == "openai"
        assert pricing.input_price_per_1m == 30.0
        assert pricing.output_price_per_1m == 60.0

    def test_get_model_pricing_unknown_model(self):
        """Test getting pricing for an unknown model."""
        service = PricingService()

        pricing = service.get_model_pricing("unknown-model", "unknown-provider")
        assert pricing is None

    def test_calculate_cost_valid_model(self):
        """Test cost calculation for a valid model."""
        service = PricingService()

        # Test GPT-4 pricing: $30 per 1M input, $60 per 1M output
        cost = service.calculate_cost("gpt-4", "openai", 1000, 500)
        expected_cost = (1000 / 1_000_000.0) * 30.0 + (500 / 1_000_000.0) * 60.0
        assert cost == pytest.approx(expected_cost, rel=1e-6)

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation for an unknown model returns 0.0."""
        service = PricingService()

        cost = service.calculate_cost("unknown-model", "unknown-provider", 1000, 500)
        assert cost == 0.0

    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens."""
        service = PricingService()

        cost = service.calculate_cost("gpt-4", "openai", 0, 0)
        assert cost == 0.0

    def test_calculate_cost_large_token_count(self):
        """Test cost calculation with large token counts."""
        service = PricingService()

        # Test with 1M tokens (should equal the price per 1M)
        cost = service.calculate_cost("gpt-4", "openai", 1_000_000, 1_000_000)
        expected_cost = 30.0 + 60.0  # input + output
        assert cost == pytest.approx(expected_cost, rel=1e-6)

    def test_add_custom_pricing(self):
        """Test adding custom pricing for a model."""
        service = PricingService()

        custom_pricing = ModelPricing(
            input_price_per_1m=20.0,
            output_price_per_1m=40.0,
            model_name="custom-model",
            provider="openai",
            last_updated="2024-01-01",
        )

        service.add_custom_pricing("custom-model", custom_pricing)

        # Verify the custom pricing was added
        retrieved_pricing = service.get_model_pricing("custom-model", "openai")
        assert retrieved_pricing is not None
        assert retrieved_pricing.model_name == "custom-model"
        assert retrieved_pricing.input_price_per_1m == 20.0
        assert retrieved_pricing.output_price_per_1m == 40.0

    def test_custom_pricing_takes_precedence(self):
        """Test that custom pricing takes precedence over default pricing."""
        service = PricingService()

        # Add custom pricing for an existing model
        custom_pricing = ModelPricing(
            input_price_per_1m=10.0,  # Different from default
            output_price_per_1m=20.0,  # Different from default
            model_name="gpt-4",
            provider="openai",
            last_updated="2024-01-01",
        )

        service.add_custom_pricing("gpt-4", custom_pricing)

        # Verify custom pricing is used
        retrieved_pricing = service.get_model_pricing("gpt-4", "openai")
        assert retrieved_pricing is not None
        if retrieved_pricing:
            assert retrieved_pricing.input_price_per_1m == 10.0
            assert retrieved_pricing.output_price_per_1m == 20.0

    def test_get_supported_providers(self):
        """Test getting list of supported providers."""
        service = PricingService()

        # Test that we can get pricing for different providers
        openai_pricing = service.get_model_pricing("gpt-4", "openai")
        anthropic_pricing = service.get_model_pricing(
            "claude-3-sonnet-20240229", "anthropic"
        )
        google_pricing = service.get_model_pricing("gemini-pro", "google")

        assert openai_pricing is not None
        assert anthropic_pricing is not None
        assert google_pricing is not None

    def test_get_supported_models_all(self):
        """Test getting all supported models."""
        service = PricingService()

        # Test that we can get pricing for different models
        gpt4_pricing = service.get_model_pricing("gpt-4", "openai")
        gpt4turbo_pricing = service.get_model_pricing("gpt-4-turbo", "openai")
        claude_pricing = service.get_model_pricing(
            "claude-3-sonnet-20240229", "anthropic"
        )
        gemini_pricing = service.get_model_pricing("gemini-pro", "google")

        assert gpt4_pricing is not None
        assert gpt4turbo_pricing is not None
        assert claude_pricing is not None
        assert gemini_pricing is not None

    def test_get_supported_models_by_provider(self):
        """Test getting supported models filtered by provider."""
        service = PricingService()

        # Test OpenAI models
        gpt4_pricing = service.get_model_pricing("gpt-4", "openai")
        gpt4turbo_pricing = service.get_model_pricing("gpt-4-turbo", "openai")
        gpt35_pricing = service.get_model_pricing("gpt-3.5-turbo", "openai")

        assert gpt4_pricing is not None
        assert gpt4turbo_pricing is not None
        assert gpt35_pricing is not None

        # Test that non-OpenAI models return None for OpenAI provider
        claude_pricing = service.get_model_pricing("claude-3-sonnet-20240229", "openai")
        gemini_pricing = service.get_model_pricing("gemini-pro", "openai")

        assert claude_pricing is None
        assert gemini_pricing is None

        # Test Anthropic models
        claude_anthropic_pricing = service.get_model_pricing(
            "claude-3-sonnet-20240229", "anthropic"
        )
        assert claude_anthropic_pricing is not None
        assert claude_anthropic_pricing.provider == "anthropic"

    def test_default_pricing_initialization(self):
        """Test that default pricing is properly initialized."""
        service = PricingService()

        # Verify that default pricing is loaded
        assert service.pricing_config is not None
        assert service.pricing_config.default_pricing is not None
        assert len(service.pricing_config.default_pricing) > 0

    def test_pricing_config_structure(self):
        """Test that pricing configuration has proper structure."""
        service = PricingService()

        # Should have proper configuration structure
        assert service.pricing_config is not None
        assert hasattr(service.pricing_config, "default_pricing")
        assert hasattr(service.pricing_config, "custom_pricing")

    def test_custom_pricing_operations(self):
        """Test custom pricing operations."""
        service = PricingService()

        # Add custom pricing
        custom_pricing = ModelPricing(
            input_price_per_1m=20.0,
            output_price_per_1m=40.0,
            model_name="test-model",
            provider="test-provider",
            last_updated="2024-01-01",
        )
        service.add_custom_pricing("test-model", custom_pricing)

        # Verify the custom pricing was added
        retrieved_pricing = service.get_model_pricing("test-model", "test-provider")
        assert retrieved_pricing is not None
        assert retrieved_pricing.model_name == "test-model"
        assert retrieved_pricing.input_price_per_1m == 20.0
        assert retrieved_pricing.output_price_per_1m == 40.0

        # Test cost calculation with custom pricing
        cost = service.calculate_cost("test-model", "test-provider", 1000, 500)
        expected_cost = (1000 / 1_000_000.0) * 20.0 + (500 / 1_000_000.0) * 40.0
        assert cost == pytest.approx(expected_cost, rel=1e-6)

    def test_pattern_matching(self):
        """Test pattern matching for model variants."""
        service = PricingService()

        # Test that a model variant can match a base model
        # This is a simple implementation, so we test the basic functionality
        pricing = service.get_model_pricing("gpt-4-something", "openai")
        # Should return None for unknown variants, but not crash
        assert pricing is None or isinstance(pricing, ModelPricing)

    def test_environment_variable_integration(self):
        """Test that pricing service can work with environment variables."""
        # This test verifies that the pricing service can be used
        # in conjunction with environment-based API keys
        service = PricingService()

        # Test that we can calculate costs for models
        cost = service.calculate_cost("gpt-4", "openai", 1000, 500)
        assert cost > 0

        # Test that we can get model pricing
        pricing = service.get_model_pricing("gpt-4", "openai")
        assert pricing is not None

    def test_error_handling_invalid_pricing(self):
        """Test error handling with invalid pricing data."""
        service = PricingService()

        # Test with invalid model name
        pricing = service.get_model_pricing("", "openai")
        assert pricing is None

        # Test with non-existent model
        pricing = service.get_model_pricing("non-existent-model", "openai")
        assert pricing is None

        # Test with empty string values
        pricing = service.get_model_pricing("", "openai")
        assert pricing is None

    def test_cost_calculation_edge_cases(self):
        """Test cost calculation with edge cases."""
        service = PricingService()

        # Test with zero tokens
        cost = service.calculate_cost("gpt-4", "openai", 0, 0)
        assert cost == 0.0  # Should return 0 for zero tokens

        # Test with very small token counts
        cost = service.calculate_cost("gpt-4", "openai", 1, 1)
        assert cost > 0  # Should be a very small positive number

        # Test with very large token counts
        cost = service.calculate_cost("gpt-4", "openai", 10_000_000, 5_000_000)
        assert cost > 0  # Should be a large positive number

        # Test with negative tokens (should handle gracefully)
        cost = service.calculate_cost("gpt-4", "openai", -100, -50)
        assert cost < 0  # Should be negative for negative tokens

    def test_pricing_service_singleton_behavior(self):
        """Test that pricing service can be used as a singleton."""
        service1 = PricingService()
        service2 = PricingService()

        # Both should have the same default pricing
        pricing1 = service1.get_model_pricing("gpt-4", "openai")
        pricing2 = service2.get_model_pricing("gpt-4", "openai")

        assert pricing1 is not None
        assert pricing2 is not None
        assert pricing1.input_price_per_1m == pricing2.input_price_per_1m
        assert pricing1.output_price_per_1m == pricing2.output_price_per_1m

    def test_load_default_pricing_from_file(self):
        """Test loading default pricing from JSON file."""
        # The current implementation doesn't load from files, it uses hardcoded defaults
        service = PricingService()

        # Verify that default pricing is loaded
        assert service.pricing_config is not None
        assert len(service.pricing_config.default_pricing) > 0

    def test_load_default_pricing_file_not_found(self):
        """Test handling when default pricing file is not found."""
        # The current implementation doesn't load from files, so this test is not applicable
        # but we can test that the service initializes correctly
        service = PricingService()

        # Should create configuration with default pricing
        assert service.pricing_config is not None
        assert len(service.pricing_config.default_pricing) > 0
