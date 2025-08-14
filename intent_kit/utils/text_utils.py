"""
Text Utilities for Intent Kit

This module provides utilities for working with text that needs to be deserialized,
particularly for handling LLM responses and other structured text data.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from intent_kit.utils.logger import Logger

# Create a module-level logger
_logger = Logger(__name__)


def _extract_json_only(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from text without manual extraction fallback.

    Args:
        text: Text that may contain JSON

    Returns:
        Parsed JSON as dict, or None if no valid JSON found
    """
    if not text or not isinstance(text, str):
        return None

    # Try to find JSON in ```json blocks first
    json_block_pattern = r"```json\s*\n(.*?)\n```"
    json_blocks = re.findall(json_block_pattern, text, re.DOTALL)

    for block in json_blocks:
        try:
            parsed = json.loads(block.strip())
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError as e:
            _logger.debug_structured(
                {
                    "error_type": "JSONDecodeError",
                    "error_message": str(e),
                    "block_content": (
                        block[:100] + "..." if len(block) > 100 else block
                    ),
                    "source": "json_block",
                },
                "JSON Block Parse Failed",
            )

    # Try to find JSON in ``` blocks (without json specifier)
    code_block_pattern = r"```\s*\n(.*?)\n```"
    code_blocks = re.findall(code_block_pattern, text, re.DOTALL)

    for block in code_blocks:
        try:
            parsed = json.loads(block.strip())
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError as e:
            _logger.debug_structured(
                {
                    "error_type": "JSONDecodeError",
                    "error_message": str(e),
                    "block_content": (
                        block[:100] + "..." if len(block) > 100 else block
                    ),
                    "source": "code_block",
                },
                "Code Block Parse Failed",
            )

    # Try to find JSON object pattern in the entire text
    json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError as e:
            _logger.debug_structured(
                {
                    "error_type": "JSONDecodeError",
                    "error_message": str(e),
                    "json_str": (
                        json_str[:100] + "..." if len(json_str) > 100 else json_str
                    ),
                    "source": "regex_match",
                },
                "Regex JSON Parse Failed",
            )

    return None


def _extract_json_array_only(text: str) -> Optional[List[Any]]:
    """
    Extract JSON array from text without manual extraction fallback.

    Args:
        text: Text that may contain JSON array

    Returns:
        Parsed JSON array as list, or None if no valid JSON array found
    """
    if not text or not isinstance(text, str):
        return None

    # Try to find JSON array in ```json blocks first
    json_block_pattern = r"```json\s*\n(.*?)\n```"
    json_blocks = re.findall(json_block_pattern, text, re.DOTALL)

    for block in json_blocks:
        try:
            parsed = json.loads(block.strip())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError as e:
            _logger.debug_structured(
                {
                    "error_type": "JSONDecodeError",
                    "error_message": str(e),
                    "block_content": (
                        block[:100] + "..." if len(block) > 100 else block
                    ),
                    "source": "json_block",
                },
                "JSON Block Parse Failed",
            )

    # Try to find JSON array in ``` blocks (without json specifier)
    code_block_pattern = r"```\s*\n(.*?)\n```"
    code_blocks = re.findall(code_block_pattern, text, re.DOTALL)

    for block in code_blocks:
        try:
            parsed = json.loads(block.strip())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError as e:
            _logger.debug_structured(
                {
                    "error_type": "JSONDecodeError",
                    "error_message": str(e),
                    "block_content": (
                        block[:100] + "..." if len(block) > 100 else block
                    ),
                    "source": "code_block",
                },
                "Code Block Parse Failed",
            )

    # Try to find JSON array pattern in the entire text
    json_array_match = re.search(
        r"\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]", text, re.DOTALL
    )
    if json_array_match:
        json_str = json_array_match.group(0)
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError as e:
            _logger.debug_structured(
                {
                    "error_type": "JSONDecodeError",
                    "error_message": str(e),
                    "json_str": (
                        json_str[:100] + "..." if len(json_str) > 100 else json_str
                    ),
                    "source": "regex_match",
                },
                "Regex JSON Array Parse Failed",
            )

    return None


def extract_json_from_text(text: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text using multiple strategies.

    Args:
        text: Text that may contain JSON

    Returns:
        Parsed JSON as dict, or None if no valid JSON found
    """
    if not text:
        return None

    # First try automatic extraction
    result = _extract_json_only(text)
    if result is not None:
        return result

    # Fall back to manual extraction
    return _manual_json_extraction(text)


def extract_json_array_from_text(text: Optional[str]) -> Optional[List[Any]]:
    """
    Extract JSON array from text using multiple strategies.

    Args:
        text: Text that may contain JSON array

    Returns:
        Parsed JSON array as list, or None if no valid JSON array found
    """
    if not text:
        return None

    # First try automatic extraction
    result = _extract_json_array_only(text)
    if result is not None:
        return result

    # Fall back to manual extraction
    return _manual_array_extraction(text)


def extract_key_value_pairs(text: Optional[str]) -> Dict[str, Any]:
    """
    Extract key-value pairs from text using various formats.

    Args:
        text: Text containing key-value pairs

    Returns:
        Dictionary of key-value pairs
    """
    if not text:
        return {}

    pairs = {}
    content = text.strip()

    # Pattern 1: "key": value format (JSON-like)
    pattern1 = r'"([^"]+)":\s*([^\n,}]+)'
    matches = re.findall(pattern1, content)
    for key, value in matches:
        pairs[key.strip()] = _clean_value(value.strip())

    # Pattern 2: key: value format
    pattern2 = r"(\w+)\s*:\s*([^,\n}]+)"
    matches = re.findall(pattern2, content)
    for key, value in matches:
        if key not in pairs:  # Don't override quoted keys
            pairs[key.strip()] = _clean_value(value.strip())

    # Pattern 3: key = value format
    pattern3 = r"(\w+)\s*=\s*([^,\n}]+)"
    matches = re.findall(pattern3, content)
    for key, value in matches:
        if key not in pairs:
            pairs[key.strip()] = _clean_value(value.strip())

    return pairs


def is_deserializable_json(text: Optional[str]) -> bool:
    """
    Check if text can be deserialized as JSON.

    Args:
        text: Text to check

    Returns:
        True if text can be deserialized as JSON, False otherwise
    """
    if not text:
        return False

    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def clean_for_deserialization(text: Optional[str]) -> str:
    """
    Clean text for JSON deserialization by removing common formatting issues.

    Args:
        text: Text to clean

    Returns:
        Cleaned text ready for JSON deserialization
    """
    if not text:
        return ""

    # Remove leading/trailing whitespace
    cleaned = text.strip()

    # Remove markdown code block markers
    cleaned = re.sub(r"```json\s*\n", "", cleaned)
    cleaned = re.sub(r"```\s*\n", "", cleaned)
    cleaned = re.sub(r"\n```", "", cleaned)

    # Remove extra whitespace around brackets
    cleaned = re.sub(r"\s*{\s*", "{", cleaned)
    cleaned = re.sub(r"\s*}\s*", "}", cleaned)
    cleaned = re.sub(r"\s*\[\s*", "[", cleaned)
    cleaned = re.sub(r"\s*\]\s*", "]", cleaned)

    # Fix common JSON issues
    cleaned = re.sub(
        r"([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', cleaned
    )  # Quote unquoted keys
    cleaned = re.sub(
        r":\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*([,}])", r': "\1"\2', cleaned
    )  # Quote unquoted string values

    # Normalize spacing around colons
    cleaned = re.sub(r":\s+", ": ", cleaned)

    # Remove trailing commas before closing brackets/braces
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    return cleaned


def extract_structured_data(
    text: Optional[str], expected_type: str = "auto"
) -> Tuple[Optional[Any], str]:
    """
    Extract structured data from text with automatic type detection.

    Args:
        text: Text containing structured data
        expected_type: Expected data type ("auto", "dict", "list", "string")

    Returns:
        Tuple of (extracted_data, extraction_method)
    """
    if not text:
        return None, "no_data"

    # Clean the text first
    cleaned_text = clean_for_deserialization(text)

    # Try to extract based on expected type
    if expected_type == "dict":
        json_obj = _extract_json_only(cleaned_text)
        if json_obj is not None:
            return json_obj, "json_object"
        manual_obj = _manual_json_extraction(cleaned_text)
        if manual_obj is not None:
            return manual_obj, "manual_object"
        return None, "failed_dict"

    elif expected_type == "list":
        json_array = _extract_json_array_only(cleaned_text)
        if json_array is not None:
            return json_array, "json_array"
        manual_array = _manual_array_extraction(cleaned_text)
        if manual_array is not None:
            return manual_array, "manual_array"
        return None, "failed_list"

    elif expected_type == "string":
        extracted_string = _extract_clean_string(cleaned_text)
        if extracted_string is not None:
            return extracted_string, "string"
        return None, "failed_string"

    else:  # auto
        # Try JSON object first
        json_obj = _extract_json_only(cleaned_text)
        if json_obj is not None:
            return json_obj, "json_object"

        # Try JSON array
        json_array = _extract_json_array_only(cleaned_text)
        if json_array is not None:
            return json_array, "json_array"

        # Try manual extraction for object
        manual_obj = _manual_json_extraction(cleaned_text)
        if manual_obj is not None:
            return manual_obj, "manual_object"

        # Try manual extraction for array
        manual_array = _manual_array_extraction(cleaned_text)
        if manual_array is not None:
            return manual_array, "manual_array"

        # Try string extraction
        extracted_string = _extract_clean_string(cleaned_text)
        if extracted_string is not None:
            return extracted_string, "string"

        return None, "failed_auto"


def _manual_json_extraction(text: str) -> Optional[Dict[str, Any]]:
    """
    Manually extract JSON object from text using regex patterns.

    Args:
        text: Text to extract from

    Returns:
        Extracted JSON object or None
    """
    # Look for object patterns
    object_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
    match = re.search(object_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Try to extract from common patterns first
    # Pattern: { key: value, key2: value2 }
    brace_pattern = re.search(r"\{([^}]+)\}", text)
    if brace_pattern:
        content = brace_pattern.group(1)
        pairs = extract_key_value_pairs(content)
        if pairs:
            return pairs

    # Extract key-value pairs from the entire text
    pairs = extract_key_value_pairs(text)
    if pairs:
        return pairs

    return None


def _manual_array_extraction(text: str) -> Optional[List[Any]]:
    """
    Manually extract JSON array from text using regex patterns.

    Args:
        text: Text to extract from

    Returns:
        Extracted JSON array or None
    """
    # Look for array patterns
    array_pattern = r"\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]"
    match = re.search(array_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Extract quoted strings
    quoted_strings = re.findall(r'"([^"]*)"', text)
    if quoted_strings:
        return [s.strip() for s in quoted_strings if s.strip()]

    # Extract numbered items
    numbered_items = re.findall(r"\d+\.\s*(.+)", text)
    if numbered_items:
        return [item.strip() for item in numbered_items if item.strip()]

    # Extract dash-separated items
    dash_items = re.findall(r"-\s*(.+)", text)
    if dash_items:
        return [item.strip() for item in dash_items if item.strip()]

    # Extract comma-separated items
    comma_items = re.findall(r"([^,]+)", text)
    if comma_items:
        cleaned_items = [item.strip() for item in comma_items if item.strip()]
        if len(cleaned_items) > 1:
            return cleaned_items

    return None


def _extract_clean_string(text: str) -> Optional[str]:
    """
    Extract a clean string from text.

    Args:
        text: Text to extract from

    Returns:
        Clean string or None
    """
    # Remove quotes and extra whitespace
    cleaned = text.strip().strip("\"'")
    if cleaned:
        return cleaned
    return None


def _clean_value(value: str) -> Any:
    """
    Clean and convert a value string to appropriate type.

    Args:
        value: String value to clean

    Returns:
        Cleaned value with appropriate type
    """
    value = value.strip()

    # Try to convert to number
    try:
        if "." in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        pass

    # Try to convert to boolean
    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    # Return as string
    return value.strip('"')


def validate_json_structure(
    data: Any, required_keys: Optional[List[str]] = None
) -> bool:
    """
    Validate that data has the expected JSON structure.

    Args:
        data: Data to validate
        required_keys: List of required keys (for dict validation)

    Returns:
        True if data has valid structure, False otherwise
    """
    if data is None:
        return False

    if required_keys:
        if not isinstance(data, dict):
            return False
        return all(key in data for key in required_keys)

    return True
