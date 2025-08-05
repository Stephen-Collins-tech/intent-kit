"""
Base LLM Client for intent-kit

This module provides a base class for all LLM client implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any, Dict, List
from datetime import datetime
from intent_kit.types import LLMResponse, Cost, InputTokens, OutputTokens
from intent_kit.services.ai.pricing_service import PricingService
from intent_kit.utils.logger import Logger


@dataclass
class AuditLogEntry:
    """Audit log entry for LLM interactions."""
    
    timestamp: datetime
    input_prompt: str
    output_response: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    cost: float
    duration: float


@dataclass
class ModelPricing:
    """Pricing information for a specific AI model."""

    model_name: str
    provider: str
    input_price_per_1m: float
    output_price_per_1m: float
    last_updated: str


@dataclass
class ProviderPricing:
    """Pricing information for all models from a specific provider."""

    provider_name: str
    models: Dict[str, ModelPricing] = field(default_factory=dict)


@dataclass
class PricingConfiguration:
    """Complete pricing configuration for all AI providers."""

    providers: Dict[str, ProviderPricing] = field(default_factory=dict)
    custom_pricing: Dict[str, ModelPricing] = field(default_factory=dict)


class BaseLLMClient(ABC):
    """Base class for all LLM client implementations."""

    logger: Logger

    def __init__(
        self,
        name: Optional[str] = None,
        pricing_service: Optional[PricingService] = None,
        **kwargs,
    ):
        """Initialize the base client."""
        self.logger = Logger(name or self.__class__.__name__.lower())
        self._client: Optional[Any] = None
        self.pricing_service = pricing_service or PricingService()
        self.pricing_config: PricingConfiguration = self._create_pricing_config()
        self.audit_log: List[AuditLogEntry] = []
        self._initialize_client(**kwargs)

    @abstractmethod
    def _initialize_client(self, **kwargs) -> None:
        """Initialize the underlying client. Must be implemented by subclasses."""
        pass

    def _create_pricing_config(self) -> PricingConfiguration:
        """Create the pricing configuration for this provider. Default implementation returns empty config."""
        return PricingConfiguration()

    @abstractmethod
    def get_client(self) -> Any:
        """Get the underlying client instance. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def _ensure_imported(self) -> None:
        """Ensure the required package is imported. Must be implemented by subclasses."""
        pass

    def _log_audit_entry(self, response: LLMResponse, prompt: str) -> None:
        """Log an audit entry for the LLM interaction."""
        audit_entry = AuditLogEntry(
            timestamp=datetime.now(),
            input_prompt=prompt,
            output_response=response.output,
            model=response.model,
            provider=response.provider,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost=response.cost,
            duration=response.duration,
        )
        self.audit_log.append(audit_entry)

    def get_audit_log(self) -> List[AuditLogEntry]:
        """Get the complete audit log."""
        return self.audit_log.copy()

    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        self.audit_log.clear()

    @abstractmethod
    def generate(self, prompt: str, model: Optional[str] = None) -> LLMResponse:
        """
        Generate text using the LLM model.

        Args:
            prompt: The text prompt to send to the model
            model: The model name to use (optional, uses default if not provided)

        Returns:
            LLMResponse containing the generated text, token usage, and cost
        """
        pass

    def calculate_cost(
        self,
        model: str,
        provider: str,
        input_tokens: InputTokens,
        output_tokens: OutputTokens,
    ) -> Cost:
        """Calculate the cost for a model usage using the pricing service."""
        return self.pricing_service.calculate_cost(
            model, provider, input_tokens, output_tokens
        )

    def get_model_pricing(self, model_name: str) -> Optional[ModelPricing]:
        """Get pricing information for a specific model from this provider's configuration."""
        for provider in self.pricing_config.providers.values():
            if model_name in provider.models:
                return provider.models[model_name]
        return None

    def list_available_models(self) -> list[str]:
        """Get a list of all available models from this provider's configuration."""
        models: list[str] = []
        for provider in self.pricing_config.providers.values():
            models.extend(provider.models.keys())
        return models

    @classmethod
    def is_available(cls) -> bool:
        """
        Check if the required package is available.

        Returns:
            True if the package is available, False otherwise
        """
        return True
