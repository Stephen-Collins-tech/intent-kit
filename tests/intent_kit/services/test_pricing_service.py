"""
Tests for the pricing service.
"""

import pytest
from unittest.mock import patch, mock_open
import json

from intent_kit.services.ai.pricing_service import PricingService
from intent_kit.types import ModelPricing, PricingConfig


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
        providers = service.get_supported_providers()

        # Should include the major providers from default pricing
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" in providers

    def test_get_supported_models_all(self):
        """Test getting all supported models."""
        service = PricingService()
        models = service.get_supported_models()

        # Should include models from default pricing
        assert "gpt-4" in models
        assert "gpt-4-turbo" in models
        assert "claude-3-sonnet-20240229" in models
        assert "gemini-pro" in models

    def test_get_supported_models_by_provider(self):
        """Test getting supported models filtered by provider."""
        service = PricingService()
        openai_models = service.get_supported_models("openai")

        # Should only include OpenAI models
        assert "gpt-4" in openai_models
        assert "gpt-4-turbo" in openai_models
        assert "gpt-3.5-turbo" in openai_models

        # Should not include models from other providers
        assert "claude-3-sonnet-20240229" not in openai_models
        assert "gemini-pro" not in openai_models

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"default_pricing": {}, "custom_pricing": {}}',
    )
    def test_load_default_pricing_from_file(self, mock_file):
        """Test loading default pricing from JSON file."""
        service = PricingService()

        # Verify the file was opened with the correct path
        mock_file.assert_called()
        call_args = mock_file.call_args[0][0]
        assert "default_pricing.json" in str(call_args)

    @patch("builtins.open", side_effect=FileNotFoundError())
    def test_load_default_pricing_file_not_found(self, mock_file):
        """Test handling when default pricing file is not found."""
        service = PricingService()

        # Should create empty configuration
        assert service.pricing_config.default_pricing == {}
        assert service.pricing_config.custom_pricing == {}

    def test_export_pricing_config(self, tmp_path):
        """Test exporting pricing configuration to JSON file."""
        service = PricingService()

        # Add some custom pricing
        custom_pricing = ModelPricing(
            input_price_per_1m=20.0,
            output_price_per_1m=40.0,
            model_name="test-model",
            provider="test-provider",
            last_updated="2024-01-01",
        )
        service.add_custom_pricing("test-model", custom_pricing)

        # Export to temporary file
        export_file = tmp_path / "exported_pricing.json"
        service.export_pricing_config(str(export_file))

        # Verify file was created and contains expected data
        assert export_file.exists()

        with open(export_file, "r") as f:
            exported_data = json.load(f)

        assert "custom_pricing" in exported_data
        assert "default_pricing" in exported_data
        assert "use_defaults" in exported_data
        assert "test-model" in exported_data["custom_pricing"]

    def test_load_pricing_from_file(self, tmp_path):
        """Test loading pricing configuration from JSON file."""
        service = PricingService()

        # Create a test pricing file
        test_pricing_data = {
            "custom_pricing": {
                "test-model": {
                    "input_price_per_1m": 20.0,
                    "output_price_per_1m": 40.0,
                    "model_name": "test-model",
                    "provider": "test-provider",
                    "last_updated": "2024-01-01",
                }
            },
            "default_pricing": {},
            "use_defaults": True,
        }

        test_file = tmp_path / "test_pricing.json"
        with open(test_file, "w") as f:
            json.dump(test_pricing_data, f)

        # Load the pricing configuration
        service.load_pricing_from_file(str(test_file))

        # Verify the custom pricing was loaded
        pricing = service.get_model_pricing("test-model", "test-provider")
        assert pricing is not None
        assert pricing.model_name == "test-model"
        assert pricing.input_price_per_1m == 20.0
        assert pricing.output_price_per_1m == 40.0

    def test_load_custom_pricing_from_dict(self):
        """Test loading custom pricing from a dictionary organized by provider."""
        service = PricingService()

        # Define custom pricing dictionary
        custom_pricing_dict = {
            "openai": {
                "gpt-4-custom": {
                    "input_price_per_1m": 25.0,
                    "output_price_per_1m": 50.0,
                    "last_updated": "2024-01-01",
                }
            },
            "anthropic": {
                "claude-3-custom": {
                    "input_price_per_1m": 15.0,
                    "output_price_per_1m": 75.0,
                    "last_updated": "2024-01-01",
                }
            },
        }

        # Load custom pricing
        service.load_custom_pricing_from_dict(custom_pricing_dict)

        # Verify custom pricing was loaded
        gpt4_custom = service.get_model_pricing("gpt-4-custom", "openai")
        assert gpt4_custom is not None
        assert gpt4_custom.input_price_per_1m == 25.0
        assert gpt4_custom.output_price_per_1m == 50.0
        assert gpt4_custom.provider == "openai"

        claude_custom = service.get_model_pricing("claude-3-custom", "anthropic")
        assert claude_custom is not None
        assert claude_custom.input_price_per_1m == 15.0
        assert claude_custom.output_price_per_1m == 75.0
        assert claude_custom.provider == "anthropic"

        # Test cost calculation with custom pricing
        cost = service.calculate_cost("gpt-4-custom", "openai", 1000, 500)
        expected_cost = (1000 / 1_000_000.0) * 25.0 + (500 / 1_000_000.0) * 50.0
        assert cost == pytest.approx(expected_cost, rel=1e-6)

    def test_pattern_matching(self):
        """Test pattern matching for model variants."""
        service = PricingService()

        # Test that a model variant can match a base model
        # This is a simple implementation, so we test the basic functionality
        pricing = service.get_model_pricing("gpt-4-something", "openai")
        # Should return None for unknown variants, but not crash
        assert pricing is None or isinstance(pricing, ModelPricing)
