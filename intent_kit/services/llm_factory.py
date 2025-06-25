"""
LLM Factory for intent-kit

This module provides a factory for creating LLM clients based on provider configuration.
"""

from typing import Dict, Any, Optional
from intent_kit.services.openai_client import OpenAIClient
from intent_kit.services.anthropic_client import AnthropicClient
from intent_kit.services.google_client import GoogleClient
from intent_kit.services.openrouter_client import OpenRouterClient
from intent_kit.utils.logger import Logger

logger = Logger("llm_factory")


class LLMFactory:
    """Factory for creating LLM clients."""

    @staticmethod
    def create_client(llm_config: Dict[str, Any]):
        """
        Create an LLM client based on the configuration.

        Args:
            llm_config: Dictionary with keys:
                - provider: "openai", "anthropic", "google", "openrouter"
                - api_key: API key for the provider
                - model: Model name (optional, uses defaults)
                - max_tokens: Maximum tokens (optional)
                - temperature: Temperature (optional)

        Returns:
            LLM client instance

        Raises:
            ValueError: If provider is not supported or config is invalid
        """
        if not llm_config:
            raise ValueError("LLM config cannot be empty")

        provider = llm_config.get("provider")
        api_key = llm_config.get("api_key")

        if not provider:
            raise ValueError("LLM config must include 'provider'")
        if not api_key:
            raise ValueError("LLM config must include 'api_key'")

        provider = provider.lower()

        if provider == "openai":
            return OpenAIClient(api_key=api_key)
        elif provider == "anthropic":
            return AnthropicClient(api_key=api_key)
        elif provider == "google":
            return GoogleClient(api_key=api_key)
        elif provider == "openrouter":
            return OpenRouterClient(api_key=api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @staticmethod
    def generate_with_config(llm_config: Dict[str, Any], prompt: str) -> str:
        """
        Generate text using the specified LLM configuration.

        Args:
            llm_config: LLM configuration dictionary
            prompt: Text prompt to send to the LLM

        Returns:
            Generated text response
        """
        client = LLMFactory.create_client(llm_config)

        # Extract optional parameters
        model = llm_config.get("model")
        max_tokens = llm_config.get("max_tokens")
        temperature = llm_config.get("temperature")

        # For now, we'll use the default generate method
        # In the future, we can extend this to pass additional parameters
        if model:
            return client.generate(prompt, model=model)
        else:
            return client.generate(prompt)
