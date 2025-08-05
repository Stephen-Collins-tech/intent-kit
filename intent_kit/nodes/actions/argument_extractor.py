"""
Argument extractor entity for action nodes.

This module provides the ArgumentExtractor class which encapsulates
argument extraction functionality for action nodes.
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Union
from dataclasses import dataclass

from intent_kit.services.ai.base_client import BaseLLMClient
from intent_kit.services.ai.llm_factory import LLMFactory
from intent_kit.utils.logger import Logger

logger = Logger(__name__)

# Type alias for llm_config to support both dict and BaseLLMClient
LLMConfig = Union[Dict[str, Any], BaseLLMClient]


@dataclass
class ExtractionResult:
    """Result of argument extraction operation."""

    success: bool
    extracted_params: Dict[str, Any]
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost: Optional[float] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None


class ArgumentExtractor(ABC):
    """Abstract base class for argument extractors."""

    def __init__(self, param_schema: Dict[str, Type], name: str = "unknown"):
        """
        Initialize the argument extractor.

        Args:
            param_schema: Dictionary mapping parameter names to their types
            name: Name of the extractor for logging purposes
        """
        self.param_schema = param_schema
        self.name = name
        self.logger = Logger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def extract(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        """
        Extract arguments from user input.

        Args:
            user_input: The user's input text
            context: Optional context information

        Returns:
            ExtractionResult containing the extracted parameters and metadata
        """
        pass


class RuleBasedArgumentExtractor(ArgumentExtractor):
    """Rule-based argument extractor using pattern matching."""

    def extract(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        """
        Extract arguments using rule-based pattern matching.

        Args:
            user_input: The user's input text
            context: Optional context information (not used in rule-based extraction)

        Returns:
            ExtractionResult with extracted parameters
        """
        try:
            extracted_params = {}
            input_lower = user_input.lower()

            # Extract name parameter (for greetings)
            if "name" in self.param_schema:
                extracted_params.update(self._extract_name_parameter(input_lower))

            # Extract location parameter (for weather)
            if "location" in self.param_schema:
                extracted_params.update(self._extract_location_parameter(input_lower))

            # Extract calculation parameters
            if (
                "operation" in self.param_schema
                and "a" in self.param_schema
                and "b" in self.param_schema
            ):
                extracted_params.update(
                    self._extract_calculation_parameters(input_lower)
                )

            return ExtractionResult(success=True, extracted_params=extracted_params)

        except Exception as e:
            self.logger.error(f"Rule-based extraction failed: {e}")
            return ExtractionResult(success=False, extracted_params={}, error=str(e))

    def _extract_name_parameter(self, input_lower: str) -> Dict[str, str]:
        """Extract name parameter from input text."""
        name_patterns = [
            r"hello\s+([a-zA-Z]+)",
            r"hi\s+([a-zA-Z]+)",
            r"greet\s+([a-zA-Z]+)",
            r"hello\s+([a-zA-Z]+\s+[a-zA-Z]+)",
            r"hi\s+([a-zA-Z]+\s+[a-zA-Z]+)",
            # Handle "Hi Bob, help me with calculations" pattern
            r"hi\s+([a-zA-Z]+),",
            r"hello\s+([a-zA-Z]+),",
            # Handle "Hello Alice, what's 15 plus 7?" pattern
            r"hello\s+([a-zA-Z]+),\s+what",
            r"hi\s+([a-zA-Z]+),\s+what",
        ]

        for pattern in name_patterns:
            match = re.search(pattern, input_lower)
            if match:
                return {"name": match.group(1).title()}

        return {"name": "User"}

    def _extract_location_parameter(self, input_lower: str) -> Dict[str, str]:
        """Extract location parameter from input text."""
        location_patterns = [
            r"weather\s+in\s+([a-zA-Z\s]+)",
            r"in\s+([a-zA-Z\s]+)",
            # Handle "Weather in San Francisco and multiply 8 by 3" pattern
            r"weather\s+in\s+([a-zA-Z\s]+)\s+and",
            # Handle "weather in New York" pattern
            r"weather\s+in\s+([a-zA-Z\s]+)(?:\s|$)",
            # Handle "in New York" pattern
            r"in\s+([a-zA-Z\s]+)(?:\s|$)",
        ]

        for pattern in location_patterns:
            match = re.search(pattern, input_lower)
            if match:
                location = match.group(1).strip()
                # Clean up the location name
                if location:
                    return {"location": location.title()}

        return {"location": "Unknown"}

    def _extract_calculation_parameters(self, input_lower: str) -> Dict[str, Any]:
        """Extract calculation parameters from input text."""
        calc_patterns = [
            # Standard patterns
            r"(\d+(?:\.\d+)?)\s+(plus|add|minus|subtract|times|multiply|divided|divide)\s+(\d+(?:\.\d+)?)",
            r"what's\s+(\d+(?:\.\d+)?)\s+(plus|add|minus|subtract|times|multiply|divided|divide)\s+(\d+(?:\.\d+)?)",
            # Patterns with "by" (e.g., "multiply 8 by 3")
            r"(multiply|times)\s+(\d+(?:\.\d+)?)\s+by\s+(\d+(?:\.\d+)?)",
            r"(divide|divided)\s+(\d+(?:\.\d+)?)\s+by\s+(\d+(?:\.\d+)?)",
            # Patterns with "and" (e.g., "20 minus 5 and weather")
            r"(\d+(?:\.\d+)?)\s+(minus|subtract)\s+(\d+(?:\.\d+)?)",
            # Patterns with "what's" variations
            r"what's\s+(\d+(?:\.\d+)?)\s+(plus|add|minus|subtract|times|multiply|divided|divide)\s+(\d+(?:\.\d+)?)",
            r"what\s+is\s+(\d+(?:\.\d+)?)\s+(plus|add|minus|subtract|times|multiply|divided|divide)\s+(\d+(?:\.\d+)?)",
        ]

        for pattern in calc_patterns:
            match = re.search(pattern, input_lower)
            if match:
                # Handle different group arrangements
                if len(match.groups()) == 3:
                    if match.group(1) in ["multiply", "times", "divide", "divided"]:
                        # Pattern like "multiply 8 by 3"
                        return {
                            "operation": match.group(1),
                            "a": float(match.group(2)),
                            "b": float(match.group(3)),
                        }
                    else:
                        # Standard pattern like "8 plus 3"
                        return {
                            "a": float(match.group(1)),
                            "operation": match.group(2),
                            "b": float(match.group(3)),
                        }

        return {}


class LLMArgumentExtractor(ArgumentExtractor):
    """LLM-based argument extractor using AI models."""

    def __init__(
        self,
        param_schema: Dict[str, Type],
        llm_config: LLMConfig,
        extraction_prompt: Optional[str] = None,
        name: str = "unknown",
    ):
        """
        Initialize the LLM-based argument extractor.

        Args:
            param_schema: Dictionary mapping parameter names to their types
            llm_config: LLM configuration or client instance
            extraction_prompt: Optional custom prompt for extraction
            name: Name of the extractor for logging purposes
        """
        super().__init__(param_schema, name)
        self.llm_config = llm_config
        self.extraction_prompt = (
            extraction_prompt or self._get_default_extraction_prompt()
        )

    def extract(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        """
        Extract arguments using LLM-based extraction.

        Args:
            user_input: The user's input text
            context: Optional context information to include in the prompt

        Returns:
            ExtractionResult with extracted parameters and token information
        """
        try:
            # Build context information for the prompt
            context_info = ""
            if context:
                context_info = "\n\nAvailable Context Information:\n"
                for key, value in context.items():
                    context_info += f"- {key}: {value}\n"
                context_info += "\nUse this context information to help extract more accurate parameters."

            # Build the extraction prompt
            param_descriptions = "\n".join(
                [
                    f"- {param_name}: {param_type.__name__ if hasattr(param_type, '__name__') else str(param_type)}"
                    for param_name, param_type in self.param_schema.items()
                ]
            )

            prompt = self.extraction_prompt.format(
                user_input=user_input,
                param_descriptions=param_descriptions,
                param_names=", ".join(self.param_schema.keys()),
                context_info=context_info,
            )

            # Get LLM response
            response = LLMFactory.generate_with_config(self.llm_config, prompt)
            self.logger.debug(
                f"LLM response FROM LLM ARG EXTRACTOR extract method: {response}"
            )

            # Parse the response to extract parameters
            extracted_params = self._parse_llm_response(response.output)

            return ExtractionResult(
                success=True,
                extracted_params=extracted_params,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost=response.cost,
                provider=response.provider,
                model=response.model,
                duration=response.duration,
            )

        except Exception as e:
            self.logger.error(f"LLM argument extraction failed: {e}")
            return ExtractionResult(success=False, extracted_params={}, error=str(e))

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response to extract parameters."""
        extracted_params = {}

        # Try to parse as JSON first
        import json

        try:
            # Clean up JSON formatting if present
            cleaned_response = response_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            parsed_json = json.loads(cleaned_response)
            if isinstance(parsed_json, dict):
                for param_name, param_value in parsed_json.items():
                    if param_name in self.param_schema:
                        extracted_params[param_name] = param_value
            else:
                # Single value JSON
                if len(self.param_schema) == 1:
                    param_name = list(self.param_schema.keys())[0]
                    extracted_params[param_name] = parsed_json
        except json.JSONDecodeError:
            # Fall back to simple parsing: look for "param_name: value" patterns
            lines = response_text.strip().split("\n")
            for line in lines:
                line = line.strip()
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        param_name = parts[0].strip()
                        param_value = parts[1].strip()
                        if param_name in self.param_schema:
                            extracted_params[param_name] = param_value

        return extracted_params

    def _get_default_extraction_prompt(self) -> str:
        """Get the default argument extraction prompt template."""
        return """You are a parameter extractor. Given a user input, extract the required parameters.

User Input: {user_input}

Required Parameters:
{param_descriptions}

{context_info}

Instructions:
- Extract the required parameters from the user input
- Consider the available context information to help with extraction
- Return each parameter on a new line in the format: "param_name: value"
- If a parameter is not found, use a reasonable default or empty string
- Be specific and accurate in your extraction

Extracted Parameters:
"""


class ArgumentExtractorFactory:
    """Factory for creating argument extractors."""

    @staticmethod
    def create(
        param_schema: Dict[str, Type],
        llm_config: Optional[LLMConfig] = None,
        extraction_prompt: Optional[str] = None,
        name: str = "unknown",
    ) -> ArgumentExtractor:
        """
        Create an argument extractor based on the provided configuration.

        Args:
            param_schema: Dictionary mapping parameter names to their types
            llm_config: Optional LLM configuration or client instance for LLM-based extraction
            extraction_prompt: Optional custom prompt for LLM extraction
            name: Name of the extractor for logging purposes

        Returns:
            ArgumentExtractor instance
        """
        if llm_config and param_schema:
            # Use LLM-based extraction
            return LLMArgumentExtractor(
                param_schema=param_schema,
                llm_config=llm_config,
                extraction_prompt=extraction_prompt,
                name=name,
            )
        # Use rule-based extraction
        return RuleBasedArgumentExtractor(param_schema=param_schema, name=name)
