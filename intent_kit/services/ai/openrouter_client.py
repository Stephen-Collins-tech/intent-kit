"""
OpenRouter client wrapper for intent-kit
"""

from intent_kit.utils.perf_util import PerfUtil
from intent_kit.types import StructuredLLMResponse, InputTokens, OutputTokens, Cost
from intent_kit.services.ai.pricing_service import PricingService
from intent_kit.services.ai.base_client import (
    BaseLLMClient,
    PricingConfiguration,
    ProviderPricing,
    ModelPricing,
)
from dataclasses import dataclass
from typing import Optional, Any, List, Union, Dict, Type, TypeVar
import json
import re
from intent_kit.utils.logger import get_logger

T = TypeVar("T")

# Try to import yaml, but don't fail if it's not available
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class OpenRouterChatCompletionMessage:
    """OpenRouter chat completion message structure."""

    content: str
    role: str
    refusal: Optional[str] = None
    annotations: Optional[Any] = None
    audio: Optional[Any] = None
    function_call: Optional[Any] = None
    tool_calls: Optional[Any] = None
    reasoning: Optional[Any] = None

    def __init__(
        self,
        content: str,
        role: str,
        refusal: Optional[str] = None,
        annotations: Optional[Any] = None,
        audio: Optional[Any] = None,
        function_call: Optional[Any] = None,
        tool_calls: Optional[Any] = None,
        reasoning: Optional[Any] = None,
    ):
        self.logger = get_logger("openrouter_client")
        self.content = content
        self.role = role
        self.refusal = refusal
        self.annotations = annotations
        self.audio = audio
        self.function_call = function_call
        self.tool_calls = tool_calls
        self.reasoning = reasoning

    def parse_content(self) -> Union[Dict, str]:
        """Try to parse content as JSON or YAML, fallback to string."""
        content = self.content.strip()
        self.logger.info(f"OpenRouter content in parse_content: {content}")

        cleaned_content = content
        json_block_pattern = re.compile(r"```json\s*([\s\S]*?)\s*```", re.IGNORECASE)
        match = json_block_pattern.search(content)
        if match:
            cleaned_content = match.group(1).strip()
        else:
            # Fallback: remove generic triple-backtick code blocks if present
            generic_block_pattern = re.compile(r"```\s*([\s\S]*?)\s*```")
            match = generic_block_pattern.search(content)
            if match:
                cleaned_content = match.group(1).strip()
            else:
                cleaned_content = content.strip()

        # Try JSON first
        try:
            return json.loads(cleaned_content)
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Error parsing content as JSON: {e}")

        # Try YAML if available
        if YAML_AVAILABLE:
            try:
                return yaml.safe_load(cleaned_content)
            except (yaml.YAMLError, ValueError) as e:
                self.logger.error(f"Error parsing content as YAML: {e}")

        # Fallback to original string
        return content

    def display(self) -> str:
        """Display the message in a readable format."""
        parsed_content = self.parse_content()
        if isinstance(parsed_content, dict):
            output = f"{self.role}: {json.dumps(parsed_content, indent=2)}"
        else:
            output = f"{self.role}: {self.content}"

        if self.refusal:
            output += f" (refusal: {self.refusal})"
        if self.annotations:
            output += f" (annotations: {self.annotations})"
        if self.audio:
            output += f" (audio: {self.audio})"
        if self.function_call:
            output += f" (function_call: {self.function_call})"
        if self.tool_calls:
            output += f" (tool_calls: {self.tool_calls})"
        if self.reasoning:
            output += f" (reasoning: {self.reasoning})"
        return output


@dataclass
class OpenRouterChoice:
    """OpenRouter choice structure."""

    finish_reason: str
    index: int
    message: OpenRouterChatCompletionMessage
    native_finish_reason: str
    logprobs: Optional[Any] = None

    def display(self) -> str:
        """Display the choice in a readable format."""
        parsed_content = self.message.parse_content()
        if isinstance(parsed_content, dict):
            return f"Choice[{self.index}]: {json.dumps(parsed_content, indent=2)}"
        elif self.message.content:
            return f"Choice[{self.index}]: {self.message.content}"
        else:
            return f"Choice[{self.index}]: {self.message.role} (finish_reason: {self.finish_reason}, native_finish_reason: {self.native_finish_reason})"

    def __str__(self) -> str:
        """String representation of the choice."""
        return self.display()

    @classmethod
    def from_raw(cls, raw_choice: Any) -> "OpenRouterChoice":
        """Create an OpenRouterChoice from a raw choice object."""
        return cls(
            finish_reason=str(getattr(raw_choice, "finish_reason", "")),
            index=int(getattr(raw_choice, "index", 0)),
            message=OpenRouterChatCompletionMessage(
                content=str(getattr(raw_choice.message, "content", "")),
                role=str(getattr(raw_choice.message, "role", "")),
                refusal=getattr(raw_choice.message, "refusal", None),
                annotations=getattr(raw_choice.message, "annotations", None),
                audio=getattr(raw_choice.message, "audio", None),
                function_call=getattr(raw_choice.message, "function_call", None),
                tool_calls=getattr(raw_choice.message, "tool_calls", None),
                reasoning=getattr(raw_choice.message, "reasoning", None),
            ),
            native_finish_reason=str(getattr(raw_choice, "native_finish_reason", "")),
            logprobs=getattr(raw_choice, "logprobs", None),
        )


@dataclass
class OpenRouterUsage:
    """OpenRouter usage structure."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class OpenRouterChatCompletion:
    """OpenRouter chat completion response structure."""

    id: str
    object: str
    created: int
    model: str
    choices: List[OpenRouterChoice]
    usage: Optional[OpenRouterUsage] = None


class OpenRouterClient(BaseLLMClient):
    def __init__(self, api_key: str, pricing_service: Optional[PricingService] = None):
        self.api_key = api_key
        super().__init__(
            name="openrouter_service", api_key=api_key, pricing_service=pricing_service
        )

    def _create_pricing_config(self) -> PricingConfiguration:
        """Create the pricing configuration for OpenRouter models."""
        config = PricingConfiguration()

        openrouter_provider = ProviderPricing("openrouter")
        openrouter_provider.models = {
            "google/gemma-2-9b-it": ModelPricing(
                model_name="google/gemma-2-9b-it",
                provider="openrouter",
                input_price_per_1m=0.01,
                output_price_per_1m=0.01,
                last_updated="2025-08-06",
            ),
            "meta-llama/llama-3.2-3b-instruct": ModelPricing(
                model_name="meta-llama/llama-3.2-3b-instruct",
                provider="openrouter",
                input_price_per_1m=0.003,
                output_price_per_1m=0.006,
                last_updated="2025-08-06",
            ),
            "moonshotai/kimi-k2": ModelPricing(
                model_name="moonshotai/kimi-k2",
                provider="openrouter",
                input_price_per_1m=0.6,
                output_price_per_1m=2.5,
                last_updated="2025-07-31",
            ),
            "mistralai/devstral-small": ModelPricing(
                model_name="mistralai/devstral-small",
                provider="openrouter",
                input_price_per_1m=0.07,
                output_price_per_1m=0.28,
                last_updated="2025-07-31",
            ),
            "qwen/qwen3-32b": ModelPricing(
                model_name="qwen/qwen3-32b",
                provider="openrouter",
                input_price_per_1m=0.027,
                output_price_per_1m=0.027,
                last_updated="2025-07-31",
            ),
            "z-ai/glm-4.5": ModelPricing(
                model_name="z-ai/glm-4.5",
                provider="openrouter",
                input_price_per_1m=0.2,
                output_price_per_1m=0.2,
                last_updated="2025-07-31",
            ),
            "qwen/qwen3-30b-a3b-instruct-2507": ModelPricing(
                model_name="qwen/qwen3-30b-a3b-instruct-2507",
                provider="openrouter",
                input_price_per_1m=0.2,
                output_price_per_1m=0.8,
                last_updated="2025-07-31",
            ),
            "mistralai/mistral-7b-instruct": ModelPricing(
                model_name="mistralai/mistral-7b-instruct",
                provider="openrouter",
                input_price_per_1m=0.1,
                output_price_per_1m=0.1,
                last_updated="2025-07-31",
            ),
            "mistralai/ministral-8b": ModelPricing(
                model_name="mistralai/ministral-8b",
                provider="openrouter",
                input_price_per_1m=0.15,
                output_price_per_1m=0.15,
                last_updated="2025-08-02",
            ),
            "mistralai/mistral-nemo-20b": ModelPricing(
                model_name="mistralai/mistral-nemo-20b",
                provider="openrouter",
                input_price_per_1m=0.008,
                output_price_per_1m=0.05,
                last_updated="2025-08-06",
            ),
            "liquid/lfm-40b": ModelPricing(
                model_name="liquid/lfm-40b",
                provider="openrouter",
                input_price_per_1m=0.15,
                output_price_per_1m=0.15,
                last_updated="2025-07-31",
            ),
        }
        config.providers["openrouter"] = openrouter_provider

        return config

    def _initialize_client(self, **kwargs) -> None:
        """Initialize the OpenRouter client."""
        self._client = self.get_client()

    def get_client(self):
        """Get the OpenRouter client."""
        try:
            import openai

            return openai.OpenAI(
                api_key=self.api_key, base_url="https://openrouter.ai/api/v1"
            )
        except ImportError as e:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            ) from e
        except Exception as e:
            # pylint: disable=broad-exception-raised
            raise Exception(
                "Error initializing OpenRouter client. Please check your API key and try again."
            ) from e

    def _ensure_imported(self):
        """Ensure the OpenAI package is imported."""
        if self._client is None:
            self._client = self.get_client()

    def _clean_response(self, content: str) -> str:
        """Clean the response content by removing newline characters and extra whitespace."""
        if not content:
            return ""

        # Remove newline characters and normalize whitespace
        cleaned = content.strip()

        return cleaned

    def generate(
        self, prompt: str, expected_type: Type[T], model: Optional[str] = None
    ) -> StructuredLLMResponse[T]:
        """Generate text using OpenRouter's LLM model."""
        self._ensure_imported()
        assert self._client is not None
        model = model or "mistralai/mistral-7b-instruct"

        perf_util = PerfUtil("openrouter_generate")
        perf_util.start()

        response: OpenRouterChatCompletion = self._client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )

        if not response.choices:
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            return StructuredLLMResponse(
                output={"error": "No choices returned from model"},
                expected_type=expected_type,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=self.calculate_cost(
                    model, "openrouter", input_tokens, output_tokens
                ),
                provider="openrouter",
                duration=perf_util.stop(),
            )

        # Extract content from the first choice
        first_choice = OpenRouterChoice.from_raw(response.choices[0])
        content = first_choice.message.parse_content()

        # Extract usage information
        input_tokens = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0
        cost = self.calculate_cost(model, "openrouter", input_tokens, output_tokens)
        duration = perf_util.stop()

        # Log cost information
        self.logger.log_cost(
            cost=cost,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider="openrouter",
            model=model,
            duration=duration,
        )

        return StructuredLLMResponse(
            output=content,
            expected_type=expected_type,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            provider="openrouter",
            duration=duration,
        )

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
