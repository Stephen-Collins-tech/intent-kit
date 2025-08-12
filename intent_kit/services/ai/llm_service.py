"""Shared LLM service for intent-kit."""

from typing import Dict, Any, Optional, Type, TypeVar
from intent_kit.services.ai.llm_factory import LLMFactory
from intent_kit.services.ai.base_client import BaseLLMClient
from intent_kit.types import RawLLMResponse, StructuredLLMResponse
from intent_kit.utils.logger import Logger

T = TypeVar("T")


class LLMService:
    """LLM service for use within a specific DAG instance."""

    def __init__(self):
        """Initialize the LLM service."""
        self._clients: Dict[str, BaseLLMClient] = {}
        self._logger = Logger("llm_service")

    def get_client(self, llm_config: Dict[str, Any]) -> BaseLLMClient:
        """Get or create an LLM client for the given configuration.

        Args:
            llm_config: LLM configuration dictionary

        Returns:
            BaseLLMClient instance
        """
        # Create a cache key from the config
        cache_key = self._create_cache_key(llm_config)

        # Return cached client if it exists
        if cache_key in self._clients:
            return self._clients[cache_key]

        # Create new client
        try:
            client = LLMFactory.create_client(llm_config)
            self._clients[cache_key] = client
            self._logger.info(
                f"Created new LLM client for config: {cache_key}")
            return client
        except Exception as e:
            self._logger.error(f"Failed to create LLM client: {e}")
            raise

    def _create_cache_key(self, llm_config: Dict[str, Any]) -> str:
        """Create a cache key from LLM configuration."""
        provider = llm_config.get("provider", "unknown")
        model = llm_config.get("model", "default")
        api_key = llm_config.get("api_key", "")

        # Create a hash-like key (simplified)
        return f"{provider}:{model}:{hash(api_key) % 10000}"

    def clear_cache(self) -> None:
        """Clear the client cache."""
        self._clients.clear()
        self._logger.info("Cleared LLM client cache")

    def list_cached_clients(self) -> list[str]:
        """List all cached client keys."""
        return list(self._clients.keys())

    def generate_raw(
        self, prompt: str, llm_config: Dict[str, Any]
    ) -> RawLLMResponse:
        """Generate a raw response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            llm_config: LLM configuration dictionary
            
        Returns:
            RawLLMResponse with the raw content and metadata
        """
        client = self.get_client(llm_config)
        model = llm_config.get("model", "default")
        return client.generate(prompt, model)

    def generate_structured(
        self, prompt: str, llm_config: Dict[str, Any], expected_type: Type[T]
    ) -> StructuredLLMResponse[T]:
        """Generate a structured response with type validation.
        
        Args:
            prompt: The prompt to send to the LLM
            llm_config: LLM configuration dictionary
            expected_type: The expected type for validation
            
        Returns:
            StructuredLLMResponse with validated output
        """
        raw_response = self.generate_raw(prompt, llm_config)
        return raw_response.to_structured_response(expected_type)
