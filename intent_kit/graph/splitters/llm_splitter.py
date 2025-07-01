"""
LLM-based intent splitter for IntentGraph.
"""
from typing import Dict, List, Any, Optional, Sequence
import re
import json
from intent_kit.utils.logger import Logger
from intent_kit.graph.splitters.splitter_types import IntentChunk


def llm_splitter(user_input: str, debug: bool = False, llm_client=None) -> Sequence[IntentChunk]:
    """
    LLM-based intent splitter using AI models.

    Args:
        user_input: The user's input string
        debug: Whether to enable debug logging
        llm_client: LLM client instance (optional)

    Returns:
        List of intent chunks as strings
    """
    logger = Logger(__name__)

    if debug:
        logger.info(f"LLM-based splitting input: '{user_input}'")

    if not llm_client:
        if debug:
            logger.warning(
                "No LLM client available, falling back to rule-based splitting")
        # Fallback to rule-based splitting
        from .rule_splitter import rule_splitter
        return rule_splitter(user_input, debug)

    try:
        # Create prompt for LLM
        prompt = _create_splitting_prompt(user_input)

        if debug:
            logger.info(f"LLM prompt: {prompt}")

        # Get response from LLM
        response = llm_client.generate(prompt)

        if debug:
            logger.info(f"LLM response: {response}")

        # Parse the response
        results = _parse_llm_response(response)

        if debug:
            logger.info(f"Parsed results: {results}")

        # If we got valid results, return them
        if results:
            return results
        else:
            # If no valid results, fallback to rule-based
            if debug:
                logger.warning(
                    "LLM parsing returned no results, falling back to rule-based")
            from .rule_splitter import rule_splitter
            return rule_splitter(user_input, debug)

    except Exception as e:
        if debug:
            logger.error(
                f"LLM splitting failed: {e}, falling back to rule-based")

        # Fallback to rule-based splitting
        from .rule_splitter import rule_splitter
        return rule_splitter(user_input, debug)


def _create_splitting_prompt(user_input: str) -> str:
    """Create a prompt for the LLM to split intents."""
    return f"""Given the user input: "{user_input}"

Please split this into separate intents if it contains multiple distinct requests. If the input contains multiple intents, separate them. If it's a single intent, return it as is.

Return your response as a JSON array of strings, where each string represents a separate intent chunk.

For example:
- Input: "Cancel my flight and update my email"
- Response: ["cancel my flight", "update my email"]

- Input: "Book a flight to NYC"
- Response: ["book a flight to NYC"]

Your response:"""


def _parse_llm_response(response: str) -> List[str]:
    """Parse the LLM response into the expected format."""
    logger = Logger(__name__)

    try:
        # Try to extract JSON from the response
        # Look for JSON array pattern
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            parsed = json.loads(json_str)

            # Validate the format
            if isinstance(parsed, list):
                results = []
                for item in parsed:
                    if isinstance(item, str):
                        results.append(item.strip())
                return results

        # If JSON parsing fails, try to extract manually
        return _extract_manual_parsing(response)

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return []


def _extract_manual_parsing(response: str) -> List[str]:
    """Fallback manual parsing when JSON parsing fails."""
    logger = Logger(__name__)

    # Try to extract quoted strings
    quoted_strings = re.findall(r'"([^"]*)"', response)
    if quoted_strings:
        return [s.strip() for s in quoted_strings if s.strip()]

    # Try to extract numbered items
    numbered_items = re.findall(r'\d+\.\s*(.+)', response)
    if numbered_items:
        return [item.strip() for item in numbered_items if item.strip()]

    # Try to extract dash-separated items
    dash_items = re.findall(r'-\s*(.+)', response)
    if dash_items:
        return [item.strip() for item in dash_items if item.strip()]

    logger.warning("Manual parsing failed, returning empty list")
    return []
