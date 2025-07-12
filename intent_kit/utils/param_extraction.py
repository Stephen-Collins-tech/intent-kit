"""
Parameter extraction utilities for intent graph nodes.

This module provides functions for extracting parameters from user input
using both rule-based and LLM-based approaches.
"""

import re
from typing import Any, Callable, Dict, Type, Optional
from intent_kit.utils.logger import Logger

logger = Logger("param_extraction")


def parse_param_schema(schema_data: Dict[str, str]) -> Dict[str, Type]:
    """Parse parameter schema from JSON string types to Python types.

    Args:
        schema_data: Dictionary mapping parameter names to string type names

    Returns:
        Dictionary mapping parameter names to Python types

    Raises:
        ValueError: If an unknown type is encountered
    """
    type_map = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
    }

    param_schema = {}
    for param_name, type_name in schema_data.items():
        if type_name not in type_map:
            raise ValueError(f"Unknown parameter type: {type_name}")
        param_schema[param_name] = type_map[type_name]

    return param_schema


def create_rule_based_extractor(
    param_schema: Dict[str, Type],
) -> Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]]:
    """Create a rule-based argument extractor function.

    Args:
        param_schema: Dictionary mapping parameter names to their types

    Returns:
        Function that extracts parameters from text using simple rules
    """

    def simple_extractor(
        user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Simple keyword-based argument extractor."""
        extracted_params = {}
        input_lower = user_input.lower()

        # Extract name parameter (for greetings)
        if "name" in param_schema:
            extracted_params.update(_extract_name_parameter(input_lower))

        # Extract location parameter (for weather)
        if "location" in param_schema:
            extracted_params.update(_extract_location_parameter(input_lower))

        # Extract calculation parameters
        if "operation" in param_schema and "a" in param_schema and "b" in param_schema:
            extracted_params.update(_extract_calculation_parameters(input_lower))

        return extracted_params

    return simple_extractor


def _extract_name_parameter(input_lower: str) -> Dict[str, str]:
    """Extract name parameter from input text."""
    name_patterns = [
        r"hello\s+([a-zA-Z]+)",
        r"hi\s+([a-zA-Z]+)",
        r"greet\s+([a-zA-Z]+)",
        r"hello\s+([a-zA-Z]+\s+[a-zA-Z]+)",
        r"hi\s+([a-zA-Z]+\s+[a-zA-Z]+)",
    ]

    for pattern in name_patterns:
        match = re.search(pattern, input_lower)
        if match:
            return {"name": match.group(1).title()}

    return {"name": "User"}


def _extract_location_parameter(input_lower: str) -> Dict[str, str]:
    """Extract location parameter from input text."""
    location_patterns = [
        r"weather\s+in\s+([a-zA-Z\s]+)",
        r"in\s+([a-zA-Z\s]+)",
    ]

    for pattern in location_patterns:
        match = re.search(pattern, input_lower)
        if match:
            return {"location": match.group(1).strip().title()}

    return {"location": "Unknown"}


def _extract_calculation_parameters(input_lower: str) -> Dict[str, Any]:
    """Extract calculation parameters from input text."""
    calc_patterns = [
        r"(\d+(?:\.\d+)?)\s+(plus|add|minus|subtract|times|multiply|divided|divide)\s+(\d+(?:\.\d+)?)",
        r"what's\s+(\d+(?:\.\d+)?)\s+(plus|add|minus|subtract|times|multiply|divided|divide)\s+(\d+(?:\.\d+)?)",
    ]

    for pattern in calc_patterns:
        match = re.search(pattern, input_lower)
        if match:
            return {
                "a": float(match.group(1)),
                "operation": match.group(2),
                "b": float(match.group(3)),
            }

    return {}


def create_arg_extractor(
    param_schema: Dict[str, Type],
    llm_config: Optional[Dict[str, Any]] = None,
    extraction_prompt: Optional[str] = None,
    node_name: str = "unknown",
) -> Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]]:
    """Create an argument extractor function.

    Args:
        param_schema: Dictionary mapping parameter names to their types
        llm_config: Optional LLM configuration for LLM-based extraction
        extraction_prompt: Optional custom prompt for LLM extraction
        node_name: Name of the node for logging purposes

    Returns:
        Function that extracts parameters from text
    """
    if llm_config and param_schema:
        # Use LLM-based extraction
        logger.debug(f"Creating LLM-based extractor for node '{node_name}'")
        from intent_kit.node.classifiers import (
            create_llm_arg_extractor,
            get_default_extraction_prompt,
        )

        if not extraction_prompt:
            extraction_prompt = get_default_extraction_prompt()
        return create_llm_arg_extractor(llm_config, extraction_prompt, param_schema)
    else:
        # Use rule-based extraction
        logger.debug(f"Creating rule-based extractor for node '{node_name}'")
        return create_rule_based_extractor(param_schema)
