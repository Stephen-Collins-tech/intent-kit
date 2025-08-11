"""
LLM-based argument extraction strategy.

This module provides an LLM-based extractor using AI models.
"""

import json
from typing import Mapping, Any, Optional, Dict, Union
from .base import ExtractionResult, ArgumentSchema
from intent_kit.services.ai.llm_factory import LLMFactory
from intent_kit.services.ai.base_client import BaseLLMClient


LLMConfig = Union[Dict[str, Any], BaseLLMClient]


class LLMArgumentExtractor:
    """LLM-based argument extractor using AI models."""

    def __init__(
        self,
        llm_config: LLMConfig,
        extraction_prompt: Optional[str] = None,
        name: str = "llm",
    ):
        """
        Initialize the LLM-based extractor.

        Args:
            llm_config: LLM configuration or client instance
            extraction_prompt: Optional custom prompt for extraction
            name: Name of the extractor
        """
        self.llm_config = llm_config
        self.extraction_prompt = (
            extraction_prompt or self._get_default_extraction_prompt()
        )
        self.name = name

    def extract(
        self,
        text: str,
        *,
        context: Mapping[str, Any],
        schema: Optional[ArgumentSchema] = None,
    ) -> ExtractionResult:
        """
        Extract arguments using LLM-based extraction.

        Args:
            text: The input text to extract arguments from
            context: Context information to include in the prompt
            schema: Optional schema defining expected arguments

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

            # Build parameter descriptions
            param_descriptions = ""
            param_names = []
            if schema:
                if "properties" in schema:
                    for param_name, param_info in schema["properties"].items():
                        param_type = param_info.get("type", "string")
                        param_desc = param_info.get("description", "")
                        param_descriptions += f"- {param_name}: {param_type}"
                        if param_desc:
                            param_descriptions += f" ({param_desc})"
                        param_descriptions += "\n"
                        param_names.append(param_name)
                elif "required" in schema:
                    param_names = schema["required"]
                    param_descriptions = "\n".join(
                        [f"- {param}: string" for param in param_names]
                    )

            # Build the extraction prompt
            prompt = self.extraction_prompt.format(
                user_input=text,
                param_descriptions=param_descriptions,
                param_names=", ".join(param_names) if param_names else "none",
                context_info=context_info,
            )

            # Get LLM response
            response = LLMFactory.generate_with_config(self.llm_config, prompt)

            # Parse the response to extract parameters
            extracted_params = self._parse_llm_response(response.output, param_names)

            return ExtractionResult(
                args=extracted_params,
                confidence=0.9,  # LLM extraction is generally more confident
                warnings=[],
                metadata={
                    "method": "llm",
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost": response.cost,
                    "provider": response.provider,
                    "model": response.model,
                    "duration": response.duration,
                },
            )

        except Exception as e:
            return ExtractionResult(
                args={},
                confidence=0.0,
                warnings=[f"LLM argument extraction failed: {str(e)}"],
                metadata={"method": "llm", "error": str(e)},
            )

    def _parse_llm_response(
        self, response_text: str, expected_params: Optional[list] = None
    ) -> Dict[str, Any]:
        """Parse LLM response to extract parameters."""
        extracted_params = {}

        # Try to parse as JSON first
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
                    if expected_params is None or param_name in expected_params:
                        extracted_params[param_name] = param_value
            else:
                # Single value JSON
                if expected_params and len(expected_params) == 1:
                    param_name = expected_params[0]
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
                        if expected_params is None or param_name in expected_params:
                            # Try to convert to appropriate type
                            try:
                                # Try to convert to number if it looks like one
                                if (
                                    param_value.replace(".", "")
                                    .replace("-", "")
                                    .isdigit()
                                ):
                                    if "." in param_value:
                                        extracted_params[param_name] = float(
                                            param_value
                                        )
                                    else:
                                        extracted_params[param_name] = int(param_value)
                                else:
                                    extracted_params[param_name] = param_value
                            except ValueError:
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
- Return the parameters as a JSON object
- If a parameter is not found, use a reasonable default or null
- Be specific and accurate in your extraction

Return only the JSON object with the extracted parameters:
"""
