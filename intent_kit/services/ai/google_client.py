"""
Google GenAI client wrapper for intent-kit
"""

from dataclasses import dataclass
from typing import Optional
from intent_kit.services.ai.base_client import (
    BaseLLMClient,
    PricingConfiguration,
    ProviderPricing,
    ModelPricing,
)
from intent_kit.services.ai.pricing_service import PricingService
from intent_kit.types import LLMResponse, InputTokens, OutputTokens, Cost
from intent_kit.utils.perf_util import PerfUtil

# Dummy assignment for testing
google = None


@dataclass
class GoogleUsageMetadata:
    """Google GenAI usage metadata structure."""

    prompt_token_count: int
    candidates_token_count: int
    total_token_count: int


@dataclass
class GoogleGenerateContentResponse:
    """Google GenAI generate content response structure."""

    text: str
    usage_metadata: Optional[GoogleUsageMetadata] = None


class GoogleClient(BaseLLMClient):
    def __init__(self, api_key: str, pricing_service: Optional[PricingService] = None):
        self.api_key = api_key
        super().__init__(
            name="google_service", api_key=api_key, pricing_service=pricing_service
        )

    def _create_pricing_config(self) -> PricingConfiguration:
        """Create the pricing configuration for Google GenAI models."""
        config = PricingConfiguration()

        google_provider = ProviderPricing("google")
        google_provider.models = {
            "gemini-2.5-flash-lite": ModelPricing(
                model_name="gemini-2.5-flash-lite",
                provider="google",
                input_price_per_1m=0.1,
                output_price_per_1m=0.3,
                last_updated="2025-08-02",
            ),
            "gemini-2.5-flash": ModelPricing(
                model_name="gemini-2.5-flash",
                provider="google",
                input_price_per_1m=0.3,
                output_price_per_1m=2.5,
                last_updated="2025-08-02",
            ),
            "gemini-2.5-pro": ModelPricing(
                model_name="gemini-2.5-pro",
                provider="google",
                input_price_per_1m=1.25,
                output_price_per_1m=10.0,
                last_updated="2025-08-02",
            ),
        }
        config.providers["google"] = google_provider

        return config

    def _initialize_client(self, **kwargs) -> None:
        """Initialize the Google GenAI client."""
        self._client = self.get_client()

    @classmethod
    def is_available(cls) -> bool:
        """Check if Google GenAI package is available."""
        try:
            # Only check for import, do not actually use it
            import importlib.util

            return importlib.util.find_spec("google.genai") is not None
        except ImportError:
            return False

    def get_client(self):
        """Get the Google GenAI client."""
        try:
            from google import genai

            return genai.Client(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Google GenAI package not installed. Install with: pip install google-genai"
            )
        except Exception as e:
            # pylint: disable=broad-exception-raised
            raise Exception(
                "Error initializing Google GenAI client. Please check your API key and try again."
            ) from e

    def _ensure_imported(self):
        """Ensure the Google GenAI package is imported."""
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

    def generate(self, prompt: str, model: Optional[str] = None) -> LLMResponse:
        """Generate text using Google's Gemini model."""
        self._ensure_imported()
        assert self._client is not None  # Type assertion for linter
        model = model or "gemini-2.0-flash-lite"
        perf_util = PerfUtil("google_generate")
        perf_util.start()

        try:
            from google.genai import types

            content = types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            )
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
            )

            response = self._client.models.generate_content(
                model=model,
                contents=content,
                config=generate_content_config,
            )

            # Convert to our custom dataclass structure
            usage_metadata = None
            if response.usage_metadata:
                # Handle both real and mocked usage metadata
                prompt_count = getattr(response.usage_metadata, "prompt_token_count", 0)
                candidates_count = getattr(
                    response.usage_metadata, "candidates_token_count", 0
                )

                # Safe arithmetic for mocked objects
                if hasattr(prompt_count, "__add__") and hasattr(
                    candidates_count, "__add__"
                ):
                    total_count = prompt_count + candidates_count
                else:
                    total_count = 0

                usage_metadata = GoogleUsageMetadata(
                    prompt_token_count=prompt_count,
                    candidates_token_count=candidates_count,
                    total_token_count=total_count,
                )

            google_response = GoogleGenerateContentResponse(
                text=str(response.text) if response.text else "",
                usage_metadata=usage_metadata,
            )

            self.logger.debug(f"Google generate response: {google_response.text}")

            # Extract token information
            if google_response.usage_metadata:
                # Handle both real and mocked usage metadata
                input_tokens = getattr(
                    google_response.usage_metadata, "prompt_token_count", 0
                )
                output_tokens = getattr(
                    google_response.usage_metadata, "candidates_token_count", 0
                )

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
            cost = self.calculate_cost(model, "google", input_tokens, output_tokens)

            duration = perf_util.stop()

            # Log cost information with cost per token
            self.logger.log_cost(
                cost=cost,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                provider="google",
                model=model,
                duration=duration,
            )

            return LLMResponse(
                output=self._clean_response(google_response.text),
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                provider="google",
                duration=duration,
            )

        except Exception as e:
            self.logger.error(f"Error generating text with Google GenAI: {e}")
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

        return total_cost
