"""
Text Utilities for Intent Kit

This module provides utilities for working with text that needs to be deserialized,
particularly for handling LLM responses and other structured text data.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from intent_kit.utils.logger import Logger


class TextUtil:
    """
    Static utility class for text processing and JSON extraction.

    This class provides methods for extracting JSON from text, handling various
    formats including code blocks, and cleaning text for deserialization.
    """

    _logger = Logger(__name__)

    @staticmethod
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
                TextUtil._logger.debug_structured(
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
                TextUtil._logger.debug_structured(
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
                TextUtil._logger.debug_structured(
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

        # Try to parse the entire text as JSON
        try:
            parsed = json.loads(text.strip())
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError as e:
            TextUtil._logger.debug_structured(
                {
                    "error_type": "JSONDecodeError",
                    "error_message": str(e),
                    "text_length": len(text),
                    "source": "full_text",
                },
                "Full Text Parse Failed",
            )

        return None

    @staticmethod
    def _extract_json_array_only(text: str) -> Optional[List[Any]]:
        """
        Extract JSON array from text without manual extraction fallback.

        Args:
            text: Text that may contain a JSON array

        Returns:
            Parsed JSON array as list, or None if no valid JSON array found
        """
        if not text or not isinstance(text, str):
            return None

        # Try to find JSON in ```json blocks first
        json_block_pattern = r"```json\s*\n(.*?)\n```"
        json_blocks = re.findall(json_block_pattern, text, re.DOTALL)

        for block in json_blocks:
            try:
                parsed = json.loads(block.strip())
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError as e:
                TextUtil._logger.debug_structured(
                    {
                        "error_type": "JSONDecodeError",
                        "error_message": str(e),
                        "block_content": (
                            block[:100] + "..." if len(block) > 100 else block
                        ),
                        "source": "json_block",
                        "expected_type": "array",
                    },
                    "JSON Array Block Parse Failed",
                )

        # Try to find JSON in ``` blocks (without json specifier)
        code_block_pattern = r"```\s*\n(.*?)\n```"
        code_blocks = re.findall(code_block_pattern, text, re.DOTALL)

        for block in code_blocks:
            try:
                parsed = json.loads(block.strip())
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError as e:
                TextUtil._logger.debug_structured(
                    {
                        "error_type": "JSONDecodeError",
                        "error_message": str(e),
                        "block_content": (
                            block[:100] + "..." if len(block) > 100 else block
                        ),
                        "source": "code_block",
                        "expected_type": "array",
                    },
                    "Code Block Array Parse Failed",
                )

        # Try to find JSON array pattern in the entire text
        array_match = re.search(r"\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]", text, re.DOTALL)
        if array_match:
            json_str = array_match.group(0)
            try:
                parsed = json.loads(json_str)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError as e:
                TextUtil._logger.debug_structured(
                    {
                        "error_type": "JSONDecodeError",
                        "error_message": str(e),
                        "json_str": (
                            json_str[:100] + "..." if len(json_str) > 100 else json_str
                        ),
                        "source": "regex_array_match",
                        "expected_type": "array",
                    },
                    "Regex Array Parse Failed",
                )

        # Try to parse the entire text as JSON
        try:
            parsed = json.loads(text.strip())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError as e:
            TextUtil._logger.debug_structured(
                {
                    "error_type": "JSONDecodeError",
                    "error_message": str(e),
                    "text_length": len(text),
                    "source": "full_text",
                    "expected_type": "array",
                },
                "Full Text Array Parse Failed",
            )

        return None

    @staticmethod
    def extract_json_from_text(text: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from text, handling various formats including code blocks.

        Args:
            text: Text that may contain JSON

        Returns:
            Parsed JSON as dict, or None if no valid JSON found
        """
        # Handle edge cases
        if text is None or not isinstance(text, str):
            return None

        # Try pure JSON extraction first
        result = TextUtil._extract_json_only(text)
        if result:
            return result

        # Fallback to manual extraction
        return TextUtil._manual_json_extraction(text)

    @staticmethod
    def extract_json_array_from_text(text: Optional[str]) -> Optional[List[Any]]:
        """
        Extract JSON array from text, handling various formats including code blocks.

        Args:
            text: Text that may contain a JSON array

        Returns:
            Parsed JSON array as list, or None if no valid JSON array found
        """
        # Handle edge cases
        if text is None or not isinstance(text, str):
            return None

        # Try pure JSON extraction first
        result = TextUtil._extract_json_array_only(text)
        if result:
            return result

        # Fallback to manual extraction
        return TextUtil._manual_array_extraction(text)

    @staticmethod
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
            pairs[key.strip()] = TextUtil._clean_value(value.strip())

        # Pattern 2: key: value
        kv_pattern2 = re.findall(r"(\w+)\s*:\s*([^,\n}]+)", text)
        for key, value in kv_pattern2:
            if key not in pairs:  # Don't override quoted keys
                pairs[key.strip()] = TextUtil._clean_value(value.strip())

        # Pattern 3: key = value
        kv_pattern3 = re.findall(r"(\w+)\s*=\s*([^,\n}]+)", text)
        for key, value in kv_pattern3:
            if key not in pairs:
                pairs[key.strip()] = TextUtil._clean_value(value.strip())

        return pairs

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
                json_array = TextUtil._extract_json_array_only(text)
                if json_array:
                    return json_array, "json_array"

            # Check if it looks like a JSON object
            if text.strip().startswith("{") and text.strip().endswith("}"):
                json_obj = TextUtil._extract_json_only(text)
                if json_obj:
                    return json_obj, "json_object"

        # Try JSON object first
        if expected_type in ["auto", "dict"]:
            json_obj = TextUtil._extract_json_only(text)
            if json_obj:
                return json_obj, "json_object"

        # Try JSON array
        if expected_type in ["auto", "list"]:
            json_array = TextUtil._extract_json_array_only(text)
            if json_array:
                return json_array, "json_array"

        # Try manual extraction
        if expected_type in ["auto", "dict"]:
            manual_obj = TextUtil._manual_json_extraction(text)
            if manual_obj:
                return manual_obj, "manual_object"

        if expected_type in ["auto", "list"]:
            manual_array = TextUtil._manual_array_extraction(text)
            if manual_array:
                return manual_array, "manual_array"

        # Fallback to string extraction
        if expected_type in ["auto", "string"]:
            extracted_string = TextUtil._extract_clean_string(text)
            if extracted_string:
                return extracted_string, "string"

        return None, "failed"

    @staticmethod
    def _manual_json_extraction(text: str) -> Optional[Dict[str, Any]]:
        """Manually extract JSON-like object from text."""
        # Try to extract from common patterns first
        # Pattern: { key: value, key2: value2 }
        brace_pattern = re.search(r"\{([^}]+)\}", text)
        if brace_pattern:
            content = brace_pattern.group(1)
            pairs = TextUtil.extract_key_value_pairs(content)
            if pairs:
                return pairs

        # Extract key-value pairs from the entire text
        pairs = TextUtil.extract_key_value_pairs(text)
        if pairs:
            return pairs

        return None

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
