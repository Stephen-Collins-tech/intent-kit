"""
Rule-based intent splitter for IntentGraph.
"""

from typing import List
import re
from intent_kit.utils.logger import Logger
from intent_kit.types import IntentChunk


def rule_splitter(user_input: str, debug: bool = False) -> List[IntentChunk]:
    """
    Rule-based intent splitter using keyword matching and conjunctions.

    Args:
        user_input: The user's input string
        debug: Whether to enable debug logging

    Returns:
        List of intent chunks as strings
    """
    logger = Logger(__name__)

    if debug:
        logger.info(f"Rule-based splitting input: '{user_input}'")

    # Separate word and punctuation conjunctions for regex
    word_conjunctions = ["and", "also", "plus", "as well as"]
    punct_conjunctions = [",", ";"]

    # Build regex pattern for conjunctions
    # For word conjunctions, use word boundaries
    word_pattern = r"|".join([rf"\b{re.escape(conj)}\b" for conj in word_conjunctions])
    # For punctuation, just escape them
    punct_pattern = r"|".join([re.escape(conj) for conj in punct_conjunctions])

    if word_pattern and punct_pattern:
        conjunction_pattern = f"{word_pattern}|{punct_pattern}"
    elif word_pattern:
        conjunction_pattern = word_pattern
    else:
        conjunction_pattern = punct_pattern

    parts = re.split(conjunction_pattern, user_input, flags=re.IGNORECASE)
    parts = [part.strip() for part in parts if part.strip()]

    if debug:
        logger.info(f"Split into parts: {parts}")

    # Return the split parts
    return parts
