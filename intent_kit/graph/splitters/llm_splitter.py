"""
LLM-based intent splitter for IntentGraph.
"""
from typing import Dict, List, Any, Optional
import re
import json
from intent_kit.utils.logger import Logger


def llm_splitter(user_input: str, taxonomies: Dict[str, Any], debug: bool = False, llm_client=None) -> List[Dict[str, str]]:
    """
    LLM-based intent splitter using AI models.

    Args:
        user_input: The user's input string
        taxonomies: Dictionary of available taxonomies {name: taxonomy_object}
        debug: Whether to enable debug logging
        llm_client: LLM client instance (optional)

    Returns:
        List of dicts with format [{"taxonomy": "name", "text": "split_text"}]
    """
    logger = Logger(__name__)

    if debug:
        logger.info(f"LLM-based splitting input: '{user_input}'")
        logger.info(f"Available taxonomies: {list(taxonomies.keys())}")

    if not llm_client:
        if debug:
            logger.warning(
                "No LLM client available, falling back to rule-based splitting")
        # Fallback to rule-based splitting
        from .rule_splitter import rule_splitter
        return rule_splitter(user_input, taxonomies, debug)

    try:
        # Create prompt for LLM
        prompt = _create_splitting_prompt(user_input, list(taxonomies.keys()))

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
            return rule_splitter(user_input, taxonomies, debug)

    except Exception as e:
        if debug:
            logger.error(
                f"LLM splitting failed: {e}, falling back to rule-based")

        # Fallback to rule-based splitting
        from .rule_splitter import rule_splitter
        return rule_splitter(user_input, taxonomies, debug)


def _create_splitting_prompt(user_input: str, taxonomy_names: List[str]) -> str:
    """Create a prompt for the LLM to split intents."""
    return f"""Given the user input: "{user_input}"

And the available taxonomies: {taxonomy_names}

Please split this into separate intents and assign each to the appropriate taxonomy. If the input contains multiple intents, separate them. If it's a single intent, assign it to the best matching taxonomy.

Return your response as a JSON array with this exact format:
[{{"taxonomy": "taxonomy_name", "text": "the relevant text portion"}}]

For example:
- Input: "Cancel my flight and update my email"
- Taxonomies: ["travel", "account"]
- Response: [{{"taxonomy": "travel", "text": "cancel my flight"}}, {{"taxonomy": "account", "text": "update my email"}}]

Your response:"""


def _parse_llm_response(response: str) -> List[Dict]:
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
                    if isinstance(item, dict) and "taxonomy" in item and "text" in item:
                        results.append({
                            "taxonomy": str(item["taxonomy"]),
                            "text": str(item["text"])
                        })
                return results

        # If JSON parsing fails, try to extract manually
        return _extract_manual_parsing(response)

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return []


def _extract_manual_parsing(response: str) -> List[Dict]:
    """Fallback manual parsing if JSON parsing fails."""
    results = []

    # Look for patterns like "taxonomy: name, text: content"
    pattern = r'taxonomy["\s]*:["\s]*["\']?([^"\',\]]+)["\s]*[,}\]]\s*text["\s]*:["\s]*["\']?([^"\',\]]+)["\s]*[,}\]\]]'
    matches = re.findall(pattern, response, re.IGNORECASE)

    for match in matches:
        taxonomy, text = match
        results.append({
            "taxonomy": taxonomy.strip(),
            "text": text.strip()
        })

    return results
