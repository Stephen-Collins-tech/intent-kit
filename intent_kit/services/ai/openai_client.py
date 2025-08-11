"""
OpenAI client wrapper for intent-kit
"""

from dataclasses import dataclass
from typing import Optional, List, Type, TypeVar
from intent_kit.services.ai.base_client import (
    BaseLLMClient,
    PricingConfiguration,
    ProviderPricing,
    ModelPricing,
)
from intent_kit.services.ai.pricing_service import PricingService
from intent_kit.types import StructuredLLMResponse, InputTokens, OutputTokens, Cost
from intent_kit.utils.perf_util import PerfUtil

T = TypeVar("T")

# Dummy assignment for testing
openai = None


@dataclass
class OpenAIUsage:
    """OpenAI usage structure."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class OpenAIMessage:
    """OpenAI message structure."""

    content: str
    role: str


@dataclass
class OpenAIChoice:
    """OpenAI choice structure."""

    message: OpenAIMessage
    finish_reason: str
    index: int


@dataclass
class OpenAIChatCompletion:
    """OpenAI chat completion response structure."""

    id: str
    object: str
    created: int
    model: str
    choices: List[OpenAIChoice]
    usage: Optional[OpenAIUsage] = None


class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, pricing_service: Optional[PricingService] = None):
        self.api_key = api_key
        super().__init__(
            name="openai_service", api_key=api_key, pricing_service=pricing_service
        )

    def _create_pricing_config(self) -> PricingConfiguration:
        """Create the pricing configuration for OpenAI models."""
        config = PricingConfiguration()

        openai_provider = ProviderPricing("openai")
        openai_provider.models = {
            "gpt-5-2025-08-07": ModelPricing(
                model_name="gpt-5-2025-08-07",
                provider="openai",
                input_price_per_1m=1.25,
                output_price_per_1m=10.0,
                last_updated="2025-08-09",
            ),
            "gpt-4": ModelPricing(
                model_name="gpt-4",
                provider="openai",
                input_price_per_1m=30.0,
                output_price_per_1m=60.0,
                last_updated="2025-01-15",
            ),
            "gpt-4-turbo": ModelPricing(
                model_name="gpt-4-turbo",
                provider="openai",
                input_price_per_1m=10.0,
                output_price_per_1m=30.0,
                last_updated="2025-01-15",
            ),
            "gpt-4o": ModelPricing(
                model_name="gpt-4o",
                provider="openai",
                input_price_per_1m=5.0,
                output_price_per_1m=15.0,
                last_updated="2025-01-15",
            ),
            "gpt-4o-mini": ModelPricing(
                model_name="gpt-4o-mini",
                provider="openai",
                input_price_per_1m=0.15,
                output_price_per_1m=0.6,
                last_updated="2025-01-15",
            ),
            "gpt-3.5-turbo": ModelPricing(
                model_name="gpt-3.5-turbo",
                provider="openai",
                input_price_per_1m=0.5,
                output_price_per_1m=1.5,
                last_updated="2025-01-15",
            ),
        }
        config.providers["openai"] = openai_provider

        return config

    def _initialize_client(self, **kwargs) -> None:
        """Initialize the OpenAI client."""
        self._client = self.get_client()

    @classmethod
    def is_available(cls) -> bool:
        """Check if OpenAI package is available."""
        try:
            # Only check for import, do not actually use it
            import importlib.util

            return importlib.util.find_spec("openai") is not None
        except ImportError:
            return False

    def get_client(self):
        """Get the OpenAI client."""
        try:
            import openai

            return openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )
        except Exception as e:
            # pylint: disable=broad-exception-raised
            raise Exception(
                "Error initializing OpenAI client. Please check your API key and try again."
            ) from e

    def _ensure_imported(self):
        """Ensure the OpenAI package is imported."""
        if self._client is None:
            self._client = self.get_client()

    def _clean_response(self, content: Optional[str]) -> str:
        """Clean the response content by removing newline characters and extra whitespace."""
        if content is None:
            return ""  # Convert None to empty string

        if not content:
            return ""

        # Remove newline characters and normalize whitespace
        cleaned = content.strip()

        return cleaned

    def generate(
        self, prompt: str, model: str, expected_type: Type[T]
    ) -> StructuredLLMResponse[T]:
        """Generate text using OpenAI's GPT model."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "gpt-4"
        perf_util = PerfUtil("openai_generate")
        perf_util.start()

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1000,
            )

            # Convert to our custom dataclass structure
            usage = None
            if response.usage:
                # Handle both real and mocked usage metadata
                prompt_tokens = getattr(response.usage, "prompt_tokens", 0)
                completion_tokens = getattr(response.usage, "completion_tokens", 0)

                # Safe arithmetic for mocked objects
                try:
                    total_tokens = prompt_tokens + completion_tokens
                except (TypeError, ValueError):
                    total_tokens = 0

                usage = OpenAIUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                )

            # Convert choices to our custom structure
            choices = []
            for choice in response.choices:
                choices.append(
                    OpenAIChoice(
                        message=OpenAIMessage(
                            content=choice.message.content or "",
                            role=choice.message.role,
                        ),
                        finish_reason=choice.finish_reason or "",
                        index=choice.index,
                    )
                )

            openai_response = OpenAIChatCompletion(
                id=response.id,
                object=response.object,
                created=response.created,
                model=response.model,
                choices=choices,
                usage=usage,
            )

            if not openai_response.choices:
                return StructuredLLMResponse(
                    output="",
                    expected_type=expected_type,
                    model=model,
                    input_tokens=0,
                    output_tokens=0,
                    cost=0.0,
                    provider="openai",
                    duration=0.0,
                )

            # Extract content from the first choice
            content = openai_response.choices[0].message.content

            # Extract token information
            if openai_response.usage:
                # Handle both real and mocked usage metadata
                input_tokens = getattr(openai_response.usage, "prompt_tokens", 0)
                output_tokens = getattr(openai_response.usage, "completion_tokens", 0)

                # Convert to int if they're mocked objects or ensure they're integers
                try:
                    input_tokens = int(input_tokens) if input_tokens is not None else 0
                except (TypeError, ValueError):
                    input_tokens = 0

                try:
                    output_tokens = (
                        int(output_tokens) if output_tokens is not None else 0
                    )
                except (TypeError, ValueError):
                    output_tokens = 0
            else:
                input_tokens = 0
                output_tokens = 0

            # Calculate cost using local pricing configuration
            cost = self.calculate_cost(model, "openai", input_tokens, output_tokens)

            duration = perf_util.stop()

            # Log cost information with cost per token
            self.logger.log_cost(
                cost=cost,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                provider="openai",
                model=model,
                duration=duration,
            )

            return StructuredLLMResponse(
                output=self._clean_response(content),
                expected_type=expected_type,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                provider="openai",
                duration=duration,
            )

        except Exception as e:
            self.logger.error(f"Error generating text with OpenAI: {e}")
            raise

    def calculate_cost(
        self,
        model: str,
        provider: str,
        input_tokens: InputTokens,
        output_tokens: OutputTokens,
    ) -> Cost:
        """Calculate the cost for a model usage using local pricing configuration."""
        # Get pricing from local configuration
        model_pricing = self.get_model_pricing(model)
        if model_pricing is None:
            self.logger.warning(
                f"No pricing found for model {model}, using base pricing service"
            )
            return super().calculate_cost(model, provider, input_tokens, output_tokens)

        # Calculate cost using local pricing data
        input_cost = (input_tokens / 1_000_000) * model_pricing.input_price_per_1m
        output_cost = (output_tokens / 1_000_000) * model_pricing.output_price_per_1m
        total_cost = input_cost + output_cost

        # Log structured cost calculation info
        self.logger.debug_structured(
            {
                "model": model,
                "provider": provider,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost,
                "pricing_source": "local",
            },
            "Cost Calculation",
        )

        return total_cost
