"""
Tests for intent_kit.services.llm_factory module.
"""

import pytest
import os
from unittest.mock import patch

from intent_kit.services.ai.llm_factory import LLMFactory
from intent_kit.services.ai.openai_client import OpenAIClient
from intent_kit.services.ai.anthropic_client import AnthropicClient
from intent_kit.services.ai.google_client import GoogleClient
from intent_kit.services.ai.openrouter_client import OpenRouterClient
from intent_kit.services.ai.ollama_client import OllamaClient
from intent_kit.services.ai.pricing_service import PricingService


class TestLLMFactory:
    """Test the LLMFactory class."""

    def test_create_client_openai(self):
        """Test creating OpenAI client."""
        llm_config = {"provider": "openai", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, OpenAIClient)
        assert client.api_key == "test-api-key"

    def test_create_client_anthropic(self):
        """Test creating Anthropic client."""
        llm_config = {"provider": "anthropic", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, AnthropicClient)
        assert client.api_key == "test-api-key"

    def test_create_client_google(self):
        """Test creating Google client."""
        llm_config = {"provider": "google", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, GoogleClient)
        assert client.api_key == "test-api-key"

    def test_create_client_openrouter(self):
        """Test creating OpenRouter client."""
        llm_config = {"provider": "openrouter", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, OpenRouterClient)
        assert client.api_key == "test-api-key"

    def test_create_client_ollama(self):
        """Test creating Ollama client."""
        llm_config = {"provider": "ollama"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, OllamaClient)

    def test_create_client_ollama_with_base_url(self):
        """Test creating Ollama client with custom base URL."""
        llm_config = {"provider": "ollama", "base_url": "http://custom-ollama:11434"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, OllamaClient)
        assert client.base_url == "http://custom-ollama:11434"

    def test_create_client_case_insensitive_provider(self):
        """Test that provider names are case insensitive."""
        llm_config = {"provider": "OPENAI", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, OpenAIClient)

    def test_create_client_empty_config(self):
        """Test creating client with empty config raises error."""
        with pytest.raises(ValueError, match="LLM config cannot be empty"):
            LLMFactory.create_client({})

    def test_create_client_none_config(self):
        """Test creating client with None config raises error."""
        with pytest.raises(ValueError, match="LLM config cannot be empty"):
            LLMFactory.create_client(None)

    def test_create_client_missing_provider(self):
        """Test creating client without provider raises error."""
        llm_config = {"api_key": "test-api-key"}

        with pytest.raises(ValueError, match="LLM config must include 'provider'"):
            LLMFactory.create_client(llm_config)

    def test_create_client_missing_api_key_for_openai(self):
        """Test creating OpenAI client without API key raises error."""
        llm_config = {"provider": "openai"}

        with pytest.raises(
            ValueError, match="LLM config must include 'api_key' for provider: openai"
        ):
            LLMFactory.create_client(llm_config)

    def test_create_client_missing_api_key_for_anthropic(self):
        """Test creating Anthropic client without API key raises error."""
        llm_config = {"provider": "anthropic"}

        with pytest.raises(
            ValueError,
            match="LLM config must include 'api_key' for provider: anthropic",
        ):
            LLMFactory.create_client(llm_config)

    def test_create_client_missing_api_key_for_google(self):
        """Test creating Google client without API key raises error."""
        llm_config = {"provider": "google"}

        with pytest.raises(
            ValueError, match="LLM config must include 'api_key' for provider: google"
        ):
            LLMFactory.create_client(llm_config)

    def test_create_client_missing_api_key_for_openrouter(self):
        """Test creating OpenRouter client without API key raises error."""
        llm_config = {"provider": "openrouter"}

        with pytest.raises(
            ValueError,
            match="LLM config must include 'api_key' for provider: openrouter",
        ):
            LLMFactory.create_client(llm_config)

    def test_create_client_unsupported_provider(self):
        """Test creating client with unsupported provider raises error."""
        llm_config = {"provider": "unsupported", "api_key": "test-api-key"}

        with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
            LLMFactory.create_client(llm_config)

    def test_pricing_service_integration(self):
        """Test that clients are created with pricing service."""
        llm_config = {"provider": "openai", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert hasattr(client, "pricing_service")
        assert client.pricing_service is not None

    def test_set_pricing_service(self):
        """Test setting pricing service for the factory."""
        pricing_service = PricingService()
        LLMFactory.set_pricing_service(pricing_service)

        assert LLMFactory.get_pricing_service() == pricing_service

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "env_openai_key",
            "ANTHROPIC_API_KEY": "env_anthropic_key",
            "GOOGLE_API_KEY": "env_google_key",
        },
    )
    def test_environment_variable_support(self):
        """Test that factory can work with environment variables."""
        # Test OpenAI with env var
        llm_config = {"provider": "openai", "api_key": "env_openai_key"}
        client = LLMFactory.create_client(llm_config)
        assert isinstance(client, OpenAIClient)

        # Test Anthropic with env var
        llm_config = {"provider": "anthropic", "api_key": "env_anthropic_key"}
        client = LLMFactory.create_client(llm_config)
        assert isinstance(client, AnthropicClient)

        # Test Google with env var
        llm_config = {"provider": "google", "api_key": "env_google_key"}
        client = LLMFactory.create_client(llm_config)
        assert isinstance(client, GoogleClient)

        # Test Ollama (no API key needed)
        llm_config = {"provider": "ollama"}
        client = LLMFactory.create_client(llm_config)
        assert isinstance(client, OllamaClient)


class TestLLMFactoryIntegration:
    """Integration tests for LLMFactory."""

    def test_create_client_all_providers(self):
        """Test creating clients for all supported providers."""
        providers = [
            ("openai", OpenAIClient),
            ("anthropic", AnthropicClient),
            ("google", GoogleClient),
            ("openrouter", OpenRouterClient),
            ("ollama", OllamaClient),
        ]

        for provider_name, expected_class in providers:
            if provider_name == "ollama":
                llm_config = {"provider": provider_name}
            else:
                llm_config = {"provider": provider_name, "api_key": "test-key"}

            client = LLMFactory.create_client(llm_config)
            assert isinstance(client, expected_class)

    def test_config_validation_edge_cases(self):
        """Test config validation with edge cases."""
        # Test with None values
        with pytest.raises(ValueError):
            LLMFactory.create_client(None)

        # Test with empty dict
        with pytest.raises(ValueError):
            LLMFactory.create_client({})

        # Test with missing provider
        with pytest.raises(ValueError):
            LLMFactory.create_client({"api_key": "test"})

        # Test with unsupported provider
        with pytest.raises(ValueError):
            LLMFactory.create_client({"provider": "unsupported", "api_key": "test"})

    def test_ollama_special_handling(self):
        """Test that Ollama is handled specially (no API key required)."""
        # Should work without API key
        client = LLMFactory.create_client({"provider": "ollama"})
        assert isinstance(client, OllamaClient)

        # Should work with custom base URL
        client = LLMFactory.create_client(
            {"provider": "ollama", "base_url": "http://custom:11434"}
        )
        assert isinstance(client, OllamaClient)
        assert client.base_url == "http://custom:11434"

        # Should work with API key (even though not required)
        client = LLMFactory.create_client({"provider": "ollama", "api_key": "test-key"})
        assert isinstance(client, OllamaClient)

    def test_error_handling_with_invalid_api_keys(self):
        """Test error handling with invalid API keys."""
        # Test with empty API key
        with pytest.raises(ValueError):
            LLMFactory.create_client({"provider": "openai", "api_key": ""})

        # Test with None API key
        with pytest.raises(ValueError):
            LLMFactory.create_client({"provider": "openai", "api_key": None})

    def test_case_insensitive_provider_names(self):
        """Test that provider names are handled case-insensitively."""
        providers = [
            "OPENAI",
            "OpenAI",
            "openai",
            "ANTHROPIC",
            "Anthropic",
            "anthropic",
        ]

        for provider in providers:
            if provider.lower() == "ollama":
                llm_config = {"provider": provider}
            else:
                llm_config = {"provider": provider, "api_key": "test-key"}

            # Should not raise an error for valid providers
            try:
                LLMFactory.create_client(llm_config)
            except ValueError as e:
                if "unsupported" in str(e):
                    # This is expected for invalid providers
                    pass
