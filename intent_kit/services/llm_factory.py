"""
LLM Factory for intent-kit

This module provides a factory for creating LLM clients based on provider configuration.
"""









logger = Logger("llm_factory")


class LLMFactory:
    """Factory for creating LLM clients."""

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
            return OllamaClient(base_url=base_url)
        if not api_key:
            raise ValueError()
                f"LLM config must include 'api_key' for provider: {provider}"
(            )
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
    def generate_with_config(llm_config, prompt: str) -> str:
        """
        Generate text using the specified LLM configuration or client instance.
        """
        client = LLMFactory.create_client(llm_config)
        model = None
        if isinstance(llm_config, dict):
            model = llm_config.get("model")
        # If the client is a BaseLLMClient, use its generate method
        if model:
            return client.generate(prompt, model=model)
        else:
            return client.generate(prompt)
