"""
LLM response classes for handling AI service responses.
"""

import json
from dataclasses import dataclass
from typing import (
    Dict,
    Any,
    Optional,
    Type,
    TypeVar,
    Generic,
    Union,
    cast,
)
from intent_kit.utils.type_coercion import (
    validate_type,
    validate_raw_content,
    TypeValidationError,
)

# Try to import yaml at module load time
try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# Type aliases
TokenUsage = str
InputTokens = int
OutputTokens = int
TotalTokens = int
Cost = float
Provider = str
Model = str
Output = str
Duration = float  # in seconds

# Type variable for structured output
T = TypeVar("T")

# Structured output type - can be any structured data
StructuredOutput = Union[Dict[str, Any], list, Any]

# Type-safe output that can be either structured or string
TypedOutput = Union[StructuredOutput, str]


@dataclass
class LLMResponse:
    """Response from an LLM."""

    output: TypedOutput
    model: Model
    input_tokens: InputTokens
    output_tokens: OutputTokens
    cost: Cost
    provider: Provider
    duration: Duration

    @property
    def total_tokens(self) -> TotalTokens:
        """Total tokens used in the response."""
        return self.input_tokens + self.output_tokens

    def get_structured_output(self) -> StructuredOutput:
        """Get the output as structured data, parsing if necessary."""
        if isinstance(self.output, (dict, list)):
            return self.output
        elif isinstance(self.output, str):
            # Try to parse as JSON
            try:
                return json.loads(self.output)
            except (json.JSONDecodeError, ValueError):
                # Try to parse as YAML
                if yaml is not None:
                    try:
                        parsed = yaml.safe_load(self.output)
                        # Only return YAML result if it's a dict or list, otherwise wrap in dict
                        if isinstance(parsed, (dict, list)):
                            return parsed
                        else:
                            return {"raw_content": self.output}
                    except (yaml.YAMLError, ValueError):
                        pass
                # Return as dict with raw string
                return {"raw_content": self.output}
        else:
            return {"raw_content": str(self.output)}

    def get_string_output(self) -> str:
        """Get the output as a string."""
        if isinstance(self.output, str):
            return self.output
        else:
            import json

            return json.dumps(self.output, indent=2)


@dataclass
class RawLLMResponse:
    """Raw response from an LLM service before type validation."""

    content: str
    model: str
    provider: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost: Optional[float] = None
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}

    @property
    def total_tokens(self) -> Optional[int]:
        """Return total tokens if both input and output are available."""
        if self.input_tokens is not None and self.output_tokens is not None:
            return self.input_tokens + self.output_tokens
        return None

    def to_structured_response(
        self, expected_type: Type[T]
    ) -> "StructuredLLMResponse[T]":
        """Convert to StructuredLLMResponse with type validation.

        Args:
            expected_type: The expected type for validation

        Returns:
            StructuredLLMResponse with validated output
        """

        # Use the consolidated validation utility
        validated_output = validate_raw_content(self.content, expected_type)

        return StructuredLLMResponse(
            output=validated_output,
            expected_type=expected_type,
            model=self.model,
            input_tokens=self.input_tokens or 0,
            output_tokens=self.output_tokens or 0,
            cost=self.cost or 0.0,
            provider=self.provider,
            duration=self.duration or 0.0,
        )


class StructuredLLMResponse(LLMResponse, Generic[T]):
    """LLM response that guarantees structured output."""

    def __init__(
        self,
        output: StructuredOutput,
        expected_type: Optional[Type[T]] = None,
        **kwargs,
    ):
        """Initialize with structured output.

        Args:
            output: The raw output from the LLM
            expected_type: Optional type to coerce the output into using type validation
            **kwargs: Additional arguments for LLMResponse
        """
        # Parse string output into structured data
        parsed_output: StructuredOutput
        if isinstance(output, str):
            # If expected_type is str, don't try to parse as JSON/YAML
            if expected_type is str:
                parsed_output = output
            else:
                parsed_output = self._parse_string_to_structured(output)
        else:
            parsed_output = output

        # If expected_type is provided, validate and coerce the output
        if expected_type is not None:
            try:
                # First try to convert the parsed output to the expected type
                converted_output = self._convert_to_expected_type(
                    parsed_output, expected_type
                )
                parsed_output = validate_type(converted_output, expected_type)
            except Exception as e:
                # If validation fails, keep the original parsed output
                # but store the error for debugging
                parsed_output = {
                    "raw_content": parsed_output,
                    "validation_error": str(e),
                    "expected_type": str(expected_type),
                }

        # Initialize the parent class with required fields
        super().__init__(
            output=parsed_output,
            model=kwargs.get("model", ""),
            input_tokens=kwargs.get("input_tokens", 0),
            output_tokens=kwargs.get("output_tokens", 0),
            cost=kwargs.get("cost", 0.0),
            provider=kwargs.get("provider", ""),
            duration=kwargs.get("duration", 0.0),
        )

        # Store the expected type for later use
        self._expected_type = expected_type

    def get_validated_output(self) -> Union[T, StructuredOutput]:
        """Get the output validated against the expected type.

        Returns:
            The validated output of the expected type, or raw output if no type specified

        Raises:
            TypeValidationError: If the output cannot be validated against the expected type
        """
        if self._expected_type is None:
            return self.output

        # If validation failed during initialization, the output will contain error info
        if isinstance(self.output, dict) and "validation_error" in self.output:

            raise TypeValidationError(
                self.output["validation_error"],
                self.output.get("raw_content"),
                self._expected_type,
            )

        # For simple types (not generics), check if already the right type
        try:
            if isinstance(self.output, self._expected_type):
                return self.output
        except TypeError:
            # Generic types like List[str] can't be used with isinstance
            pass

        # Otherwise, try to validate now

        return validate_type(self.output, self._expected_type)  # type: ignore

    def _parse_string_to_structured(self, output_str: str) -> StructuredOutput:
        """Parse a string into structured data with better JSON/YAML detection."""
        # Clean the string - remove common LLM artifacts
        cleaned_str = output_str.strip()

        # Remove markdown code blocks if present
        import re

        json_block_pattern = re.compile(r"```json\s*([\s\S]*?)\s*```", re.IGNORECASE)
        yaml_block_pattern = re.compile(r"```yaml\s*([\s\S]*?)\s*```", re.IGNORECASE)
        generic_block_pattern = re.compile(r"```\s*([\s\S]*?)\s*```")

        # Try to extract from JSON code block first
        match = json_block_pattern.search(cleaned_str)
        if match:
            cleaned_str = match.group(1).strip()
        else:
            # Try YAML code block
            match = yaml_block_pattern.search(cleaned_str)
            if match:
                cleaned_str = match.group(1).strip()
            else:
                # Try generic code block
                match = generic_block_pattern.search(cleaned_str)
                if match:
                    cleaned_str = match.group(1).strip()

        # Try to parse as JSON first
        try:
            import json

            result = json.loads(cleaned_str)
            return result
        except (json.JSONDecodeError, ValueError):
            pass

        if yaml is not None:
            # Try to parse as YAML (try both cleaned and original string)
            for test_str in [cleaned_str, output_str]:
                try:
                    parsed = yaml.safe_load(test_str)
                    # Only return YAML result if it's a dict or list, otherwise wrap in dict
                    if isinstance(parsed, (dict, list)):
                        return parsed
                except (yaml.YAMLError, ValueError, ImportError):
                    continue

        # If parsing fails, wrap in a dict
        return {"raw_content": output_str}

    def _convert_to_expected_type(self, data: Any, expected_type: Type[T]) -> T:
        """Convert data to the expected type with intelligent coercion."""
        # If data is already the right type, return it
        if isinstance(data, expected_type):
            return data

        # Handle common type conversions
        if expected_type is dict:
            if isinstance(data, str):
                # Try to parse string as JSON/YAML
                return cast(T, self._parse_string_to_structured(data))
            elif isinstance(data, list):
                # Convert list to dict with index keys
                return cast(T, {str(i): item for i, item in enumerate(data)})
            else:
                return cast(T, {"raw_content": str(data)})

        elif expected_type is list:
            if isinstance(data, str):
                # Try to parse string as JSON/YAML
                parsed = self._parse_string_to_structured(data)
                if isinstance(parsed, list):
                    return cast(T, parsed)
                else:
                    return cast(T, [parsed])
            elif isinstance(data, dict):
                # Convert dict to list of values
                return cast(T, list(data.values()))
            else:
                return cast(T, [data])

        elif expected_type is str:
            if isinstance(data, (dict, list)):
                import json

                return cast(T, json.dumps(data, indent=2))
            else:
                return cast(T, str(data))

        elif expected_type is int:
            if isinstance(data, str):
                # Try to extract number from string
                import re

                numbers = re.findall(r"-?\d+", data)
                if numbers:
                    return cast(T, int(numbers[0]))
            elif isinstance(data, (int, float)):
                return cast(T, int(data))
            else:
                return cast(T, 0)

        elif expected_type is float:
            if isinstance(data, str):
                # Try to extract number from string
                import re

                numbers = re.findall(r"-?\d+\.?\d*", data)
                if numbers:
                    return cast(T, float(numbers[0]))
            elif isinstance(data, (int, float)):
                return cast(T, float(data))
            else:
                return cast(T, 0.0)

        # For other types, try to use the type validator
        from intent_kit.utils.type_coercion import validate_type

        return cast(T, validate_type(data, expected_type))

    @classmethod
    def from_llm_response(
        cls, response: LLMResponse, expected_type: Type[T]
    ) -> "StructuredLLMResponse[T]":
        """Create a StructuredLLMResponse from an LLMResponse.

        Args:
            response: The LLMResponse to convert
            expected_type: Optional type to coerce the output into using type validation
        """
        return cls(
            output=response.output,
            expected_type=expected_type,
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost=response.cost,
            provider=response.provider,
            duration=response.duration,
        )
