"""
Text Utilities for Intent Kit

This module provides utilities for working with text that needs to be deserialized,
particularly for handling LLM responses and other structured text data.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from intent_kit.utils.logger import Logger

logger = Logger(__name__)


def extract_json_from_text(
    text: Optional[str], fallback_to_manual: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Extract JSON object from text, handling various formats and edge cases.
    Now also supports extracting from ```json ... ``` blocks.
    """
    if not text or not isinstance(text, str):
        return None

    # First, look for a ```json ... ``` block
    json_block = re.search(r"```json\s*([\s\S]*?)```", text, re.IGNORECASE)
    if json_block:
        json_str = json_block.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.debug(f"JSON decode error in ```json block: {e}")

    # Try to find JSON object pattern
    json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.debug(f"JSON decode error: {e}")

    # Try to find JSON array pattern
    array_match = re.search(r"\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]", text, re.DOTALL)
    if array_match:
        json_str = array_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.debug(f"JSON array decode error: {e}")

    if fallback_to_manual:
        return _manual_json_extraction(text)

    return None


def extract_json_array_from_text(
    text: Optional[str], fallback_to_manual: bool = True
) -> Optional[List[Any]]:
    """
    Extract JSON array from text, handling various formats and edge cases.
    Now also supports extracting from ```json ... ``` blocks.
    """
    if not text or not isinstance(text, str):
        return None

    # First, look for a ```json ... ``` block
    json_block = re.search(r"```json\s*([\s\S]*?)```", text, re.IGNORECASE)
    if json_block:
        json_str = json_block.group(1).strip()
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError as e:
            logger.debug(f"JSON array decode error in ```json block: {e}")

    # Try to find JSON array pattern
    array_match = re.search(r"\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]", text, re.DOTALL)
    if array_match:
        json_str = array_match.group(0)
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError as e:
            logger.debug(f"JSON array decode error: {e}")

    if fallback_to_manual:
        return _manual_array_extraction(text)

    return None


def extract_key_value_pairs(text: Optional[str]) -> Dict[str, Any]:
    """
    Extract key-value pairs from text using various patterns.

    Args:
        text: The text to extract key-value pairs from

    Returns:
        Dictionary of extracted key-value pairs
    """
    if not text or not isinstance(text, str):
        return {}

    pairs = {}

    # Pattern 1: "key": value
    kv_pattern1 = re.findall(r'"([^"]+)"\s*:\s*([^,\n}]+)', text)
    for key, value in kv_pattern1:
        pairs[key.strip()] = _clean_value(value.strip())

    # Pattern 2: key: value
    kv_pattern2 = re.findall(r"(\w+)\s*:\s*([^,\n}]+)", text)
    for key, value in kv_pattern2:
        if key not in pairs:  # Don't override quoted keys
            pairs[key.strip()] = _clean_value(value.strip())

    # Pattern 3: key = value
    kv_pattern3 = re.findall(r"(\w+)\s*=\s*([^,\n}]+)", text)
    for key, value in kv_pattern3:
        if key not in pairs:
            pairs[key.strip()] = _clean_value(value.strip())

    return pairs


def is_deserializable_json(text: Optional[str]) -> bool:
    """
    Check if text can be deserialized as valid JSON.

    Args:
        text: The text to check

    Returns:
        True if text is valid JSON, False otherwise
    """
    if not text or not isinstance(text, str):
        return False

    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def clean_for_deserialization(text: Optional[str]) -> str:
    """
    Clean text to make it more likely to be deserializable.

    Args:
        text: The text to clean

    Returns:
        Cleaned text that's more likely to be valid JSON
    """
    if not text or not isinstance(text, str):
        return ""

    # Remove common LLM response artifacts
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    text = re.sub(r"^```\s*", "", text)

    # Fix common JSON issues
    text = re.sub(
        r"([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'\1"\2":', text
    )  # Quote unquoted keys
    text = re.sub(
        r":\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*([,}])", r': "\1"\2', text
    )  # Quote unquoted string values

    # Normalize spacing around colons
    text = re.sub(r":\s+", ": ", text)

    # Fix trailing commas
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)

    return text.strip()


def extract_structured_data(
    text: Optional[str], expected_type: str = "auto"
) -> Tuple[Optional[Any], str]:
    """
    Extract structured data from text with type detection.

    Args:
        text: The text to extract data from
        expected_type: Expected data type ("auto", "dict", "list", "string")

    Returns:
        Tuple of (extracted_data, extraction_method_used)
    """
    if not text or not isinstance(text, str):
        return None, "empty"

    # For auto detection, try to determine the type first
    if expected_type == "auto":
        # Check if it looks like a JSON array
        if text.strip().startswith("[") and text.strip().endswith("]"):
            json_array = extract_json_array_from_text(text, fallback_to_manual=False)
            if json_array:
                return json_array, "json_array"

        # Check if it looks like a JSON object
        if text.strip().startswith("{") and text.strip().endswith("}"):
            json_obj = extract_json_from_text(text, fallback_to_manual=False)
            if json_obj:
                return json_obj, "json_object"

    # Try JSON object first
    if expected_type in ["auto", "dict"]:
        json_obj = extract_json_from_text(text, fallback_to_manual=False)
        if json_obj:
            return json_obj, "json_object"

    # Try JSON array
    if expected_type in ["auto", "list"]:
        json_array = extract_json_array_from_text(text, fallback_to_manual=False)
        if json_array:
            return json_array, "json_array"

    # Try manual extraction
    if expected_type in ["auto", "dict"]:
        manual_obj = _manual_json_extraction(text)
        if manual_obj:
            return manual_obj, "manual_object"

    if expected_type in ["auto", "list"]:
        manual_array = _manual_array_extraction(text)
        if manual_array:
            return manual_array, "manual_array"

    # Fallback to string extraction
    if expected_type in ["auto", "string"]:
        extracted_string = _extract_clean_string(text)
        if extracted_string:
            return extracted_string, "string"

    return None, "failed"


def _manual_json_extraction(text: str) -> Optional[Dict[str, Any]]:
    """Manually extract JSON-like object from text."""
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
    """Manually extract array-like data from text."""

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
    """Extract a clean string from text."""
    # Remove common artifacts
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`.*?`", "", text)

    # Extract content between quotes
    quoted = re.findall(r'"([^"]*)"', text)
    if quoted:
        return quoted[0].strip()

    # Return cleaned text
    cleaned = text.strip()
    if cleaned and len(cleaned) > 0:
        return cleaned

    return None


def _clean_value(value: str) -> Any:
    """Clean and convert a value string to appropriate type."""
    value = value.strip()

    # Try to convert to appropriate type
    if value.lower() in ["true", "false"]:
        return value.lower() == "true"
    elif value.lower() == "null":
        return None
    elif value.isdigit():
        return int(value)
    elif re.match(r"^\d+\.\d+$", value):
        return float(value)
    elif value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    else:
        return value


def validate_json_structure(
    data: Any, required_keys: Optional[List[str]] = None
) -> bool:
    """
    Validate that extracted data has the expected structure.

    Args:
        data: The data to validate
        required_keys: List of required keys if data should be a dict

    Returns:
        True if data has valid structure, False otherwise
    """
    if data is None:
        return False

    if required_keys and isinstance(data, dict):
        return all(key in data for key in required_keys)

    return True
