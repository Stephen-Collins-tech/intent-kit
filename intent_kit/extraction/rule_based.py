"""
Rule-based argument extraction strategy.

This module provides a rule-based extractor using pattern matching.
"""

import re
from typing import Mapping, Any, Optional, Dict
from .base import ExtractionResult, ArgumentSchema


class RuleBasedArgumentExtractor:
    """Rule-based argument extractor using pattern matching."""

    def __init__(self, name: str = "rule_based"):
        """
        Initialize the rule-based extractor.

        Args:
            name: Name of the extractor
        """
        self.name = name

    def extract(
        self,
        text: str,
        *,
        context: Mapping[str, Any],
        schema: Optional[ArgumentSchema] = None,
    ) -> ExtractionResult:
        """
        Extract arguments using rule-based pattern matching.

        Args:
            text: The input text to extract arguments from
            context: Context information (not used in rule-based extraction)
            schema: Optional schema defining expected arguments

        Returns:
            ExtractionResult with extracted parameters
        """
        try:
            extracted_params = {}
            input_lower = text.lower()
            warnings = []

            # Extract name parameter (for greetings)
            if schema and "name" in schema.get("properties", {}):
                name_result = self._extract_name_parameter(input_lower)
                if name_result:
                    extracted_params.update(name_result)

            # Extract location parameter (for weather)
            if schema and "location" in schema.get("properties", {}):
                location_result = self._extract_location_parameter(input_lower)
                if location_result:
                    extracted_params.update(location_result)

            # Extract calculation parameters
            if schema and all(
                param in schema.get("properties", {})
                for param in ["operation", "a", "b"]
            ):
                calc_result = self._extract_calculation_parameters(input_lower)
                if calc_result:
                    extracted_params.update(calc_result)

            # Check for missing required parameters
            if schema and "required" in schema:
                missing_params = []
                for required_param in schema["required"]:
                    if required_param not in extracted_params:
                        missing_params.append(required_param)
                        warnings.append(f"Missing required parameter: {required_param}")

                if missing_params:
                    # Fill missing params with defaults
                    for param in missing_params:
                        if param == "name":
                            extracted_params[param] = "User"
                        elif param == "location":
                            extracted_params[param] = "Unknown"
                        else:
                            extracted_params[param] = None

            confidence = 0.8 if not warnings else 0.6

            return ExtractionResult(
                args=extracted_params,
                confidence=confidence,
                warnings=warnings,
                metadata={
                    "method": "rule_based",
                    "patterns_matched": len(extracted_params),
                },
            )

        except Exception as e:
            return ExtractionResult(
                args={},
                confidence=0.0,
                warnings=[f"Rule-based extraction failed: {str(e)}"],
                metadata={"method": "rule_based", "error": str(e)},
            )

    def _extract_name_parameter(self, input_lower: str) -> Optional[Dict[str, str]]:
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

        return None

    def _extract_location_parameter(self, input_lower: str) -> Optional[Dict[str, str]]:
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

        return None

    def _extract_calculation_parameters(
        self, input_lower: str
    ) -> Optional[Dict[str, Any]]:
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

        return None
