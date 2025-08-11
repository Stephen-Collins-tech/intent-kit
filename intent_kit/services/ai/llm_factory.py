"""
LLM Factory for intent-kit

This module provides a factory for creating LLM clients based on provider configuration.
"""

from intent_kit.services.ai.openai_client import OpenAIClient
from intent_kit.services.ai.anthropic_client import AnthropicClient
from intent_kit.services.ai.google_client import GoogleClient
from intent_kit.services.ai.openrouter_client import OpenRouterClient
from intent_kit.services.ai.ollama_client import OllamaClient
from intent_kit.services.ai.pricing_service import PricingService
from intent_kit.utils.logger import Logger
from intent_kit.services.ai.base_client import BaseLLMClient

logger = Logger("llm_factory")


class LLMFactory:
    """Factory for creating LLM clients."""

    # Static pricing service instance
    _pricing_service = PricingService()

    @classmethod
    def set_pricing_service(cls, pricing_service: PricingService) -> None:
        """Set the pricing service for the factory."""
        cls._pricing_service = pricing_service

    @classmethod
    def get_pricing_service(cls) -> PricingService:
        """Get the current pricing service."""
        return cls._pricing_service

    @staticmethod
    def create_client(llm_config):
        """
        Create an LLM client based on the configuration or use a provided BaseLLMClient instance.
        """
        if isinstance(llm_config, BaseLLMClient):
            return llm_config
        if not llm_config:
            raise ValueError("LLM config cannot be empty")
        provider = llm_config.get("provider")
        api_key = llm_config.get("api_key")
        if not provider:
            raise ValueError("LLM config must include 'provider'")
        provider = provider.lower()

        if provider == "ollama":
            base_url = llm_config.get("base_url", "http://localhost:11434")
            return OllamaClient(
                base_url=base_url, pricing_service=LLMFactory._pricing_service
            )
        if not api_key:
            raise ValueError(
                f"LLM config must include 'api_key' for provider: {provider}"
            )
        if provider == "openai":
            return OpenAIClient(
                api_key=api_key, pricing_service=LLMFactory._pricing_service
            )
        elif provider == "anthropic":
            return AnthropicClient(
                api_key=api_key, pricing_service=LLMFactory._pricing_service
            )
        elif provider == "google":
            return GoogleClient(
                api_key=api_key, pricing_service=LLMFactory._pricing_service
            )
        elif provider == "openrouter":
            return OpenRouterClient(
                api_key=api_key, pricing_service=LLMFactory._pricing_service
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
