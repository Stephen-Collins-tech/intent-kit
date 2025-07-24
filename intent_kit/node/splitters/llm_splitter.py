"""
LLM-based intent splitter for IntentGraph.
"""

from typing import List, Sequence, Callable, Optional, Dict, Any, Union
from intent_kit.utils.logger import Logger
from intent_kit.types import IntentChunk
from intent_kit.utils.text_utils import extract_json_array_from_text

logger = Logger(__name__)


def llm_splitter(
    user_input: str, debug: bool = False, llm_client=None
) -> Sequence[IntentChunk]:
    """
    LLM-based intent splitter using AI models.

    Args:
        user_input: The user's input string
        debug: Whether to enable debug logging
        llm_client: LLM client instance (optional)

    Returns:
        List of intent chunks as strings
    """
    if debug:
        logger.info(f"LLM-based splitting input: '{user_input}'")

    if not llm_client:
        if debug:
            logger.warning(
                "No LLM client available, falling back to rule-based splitting"
            )
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
                    "LLM parsing returned no results, falling back to rule-based"
                )
            from .rule_splitter import rule_splitter

            return rule_splitter(user_input, debug)

    except Exception as e:
        if debug:
            logger.error(f"LLM splitting failed: {e}, falling back to rule-based")

        # Fallback to rule-based splitting
        from .rule_splitter import rule_splitter

        return rule_splitter(user_input, debug)


def _create_splitting_prompt(user_input: str) -> str:
    """Create a prompt for the LLM to split nodes."""
    return f"""Given the user input: "{user_input}"

Please split this into separate nodes if it contains multiple distinct requests. If the input contains multiple nodes, separate them. If it's a single intent, return it as is.

Return your response as a JSON array of strings, where each string represents a separate intent chunk.

For example:
- Input: "Cancel my flight and update my email"
- Response: ["cancel my flight", "update my email"]

- Input: "Book a flight to NYC"
- Response: ["book a flight to NYC"]

Your response:"""


def _parse_llm_response(response: str) -> List[str]:
    """Parse the LLM response into the expected format."""
    try:
        # Use the new utility to extract JSON array
        parsed = extract_json_array_from_text(response)
        if parsed and isinstance(parsed, list):
            results = []
            for item in parsed:
                if isinstance(item, str):
                    results.append(item.strip())
            return results
        # If JSON parsing fails, try manual extraction from the utility
        manual = extract_json_array_from_text(response, fallback_to_manual=True)
        if manual:
            return [str(item).strip() for item in manual]
        return []
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return []


def create_llm_splitter(
    llm_config: Union[Dict[str, Any], Any],  # Accepts dict or BaseLLMClient
    splitting_prompt: Optional[str] = None,
) -> Callable[[str, bool], Sequence[IntentChunk]]:
    """
    Create an LLM-powered splitter function.

    Args:
        llm_config: LLM configuration dictionary or client instance.
        splitting_prompt: Optional custom prompt for splitting.

    Returns:
        Splitter function that can be used with SplitterNode.
    """

    def splitter_func(user_input: str, debug: bool = False) -> Sequence[IntentChunk]:
        # Always use the module-level logger
        client = None
        if isinstance(llm_config, dict):
            client = llm_config.get("llm_client")
        else:
            client = llm_config

        if not client:
            if debug:
                logger.warning(
                    "No LLM client provided to splitter, falling back to rule-based splitting"
                )
            from .rule_splitter import rule_splitter

            return rule_splitter(user_input, debug)

        prompt = splitting_prompt or _create_splitting_prompt(user_input)
        if debug:
            logger.info(f"LLM splitter prompt: {prompt}")

        try:
            response = client.generate(prompt)
            if debug:
                logger.info(f"LLM splitter response: {response}")
            results = _parse_llm_response(response)
            if debug:
                logger.info(f"LLM splitter parsed results: {results}")
            if results:
                return results
            else:
                if debug:
                    logger.warning(
                        "LLM splitter returned no results, falling back to rule-based splitting"
                    )
                from .rule_splitter import rule_splitter

                return rule_splitter(user_input, debug)
        except Exception as e:
            if debug:
                logger.error(
                    f"LLM splitter failed: {e}, falling back to rule-based splitting"
                )
            from .rule_splitter import rule_splitter

            return rule_splitter(user_input, debug)

    return splitter_func
