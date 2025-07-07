"""Service registry for intentify with optional dependencies."""

from typing import Dict, Type, Any
from .google_client import GoogleClient
from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient
from .ollama_client import OllamaClient


class ServiceRegistry:
    """Registry for AI services with optional dependencies."""

    _services: Dict[str, Type] = {
        "google": GoogleClient,
        "anthropic": AnthropicClient,
        "openai": OpenAIClient,
        "ollama": OllamaClient,
    }

    @classmethod
    def get_available_services(cls) -> Dict[str, bool]:
        """Get a dictionary of service names and their availability."""
        available = {}
        for name, service_class in cls._services.items():
            if hasattr(service_class, "is_available"):
                available[name] = service_class.is_available()
            else:
                available[name] = True  # Assume available if no check method
        return available

    @classmethod
    def create_service(cls, service_name: str, **kwargs) -> Any:
        """Create a service instance if available."""
        if service_name not in cls._services:
            raise ValueError(f"Unknown service: {service_name}")

        service_class = cls._services[service_name]

        if hasattr(service_class, "is_available") and not service_class.is_available():
            raise ImportError(
                f"Service '{service_name}' is not available. "
                f"Install required dependencies: pip install intentify[openai]"
            )

        return service_class(**kwargs)

    @classmethod
    def register_service(cls, name: str, service_class: Type):
        """Register a new service class."""
        cls._services[name] = service_class


# Convenience functions


def get_available_services() -> Dict[str, bool]:
    """Get available services."""
    return ServiceRegistry.get_available_services()


def create_service(service_name: str, **kwargs) -> Any:
    """Create a service instance."""
    return ServiceRegistry.create_service(service_name, **kwargs)
