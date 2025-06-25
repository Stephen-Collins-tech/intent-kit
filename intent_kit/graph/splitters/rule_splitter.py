"""
Rule-based intent splitter for IntentGraph.
"""
from typing import Dict, List, Optional, Any
import re
from intent_kit.utils.logger import Logger


def rule_splitter(user_input: str, taxonomies: Dict[str, Any], debug: bool = False) -> List[Dict[str, str]]:
    """
    Rule-based intent splitter using keyword matching and conjunctions.

    Args:
        user_input: The user's input string
        taxonomies: Dictionary of available taxonomies {name: taxonomy_object}
        debug: Whether to enable debug logging

    Returns:
        List of dicts with format [{"taxonomy": "name", "text": "split_text"}]
    """
    logger = Logger(__name__)

    if debug:
        logger.info(f"Rule-based splitting input: '{user_input}'")
        logger.info(f"Available taxonomies: {list(taxonomies.keys())}")

    taxonomy_names = list(taxonomies.keys())
    results = []

    # Separate word and punctuation conjunctions for regex
    word_conjunctions = ["and", "also", "plus", "as well as"]
    punct_conjunctions = [",", ";"]
    conjunctions = word_conjunctions + punct_conjunctions

    # Build regex pattern for conjunctions
    word_pattern = r"|".join([fr"\\b{conj}\\b" for conj in word_conjunctions])
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

    # If we have multiple parts, try to match each part to a taxonomy
    if len(parts) > 1:
        matched_taxonomies = set()
        unmatched_parts = []

        for part in parts:
            taxonomy = _find_matching_taxonomy(part, taxonomy_names, debug)
            if taxonomy and taxonomy not in matched_taxonomies:
                results.append({"taxonomy": taxonomy, "text": part})
                matched_taxonomies.add(taxonomy)
                if debug:
                    logger.info(f"Assigned '{part}' to taxonomy '{taxonomy}'")
            else:
                unmatched_parts.append(part)

        # Always fallback if number of parts equals number of taxonomies
        if len(parts) == len(taxonomy_names):
            if debug and len(results) < len(parts):
                logger.info(
                    f"Fallback: assigning parts in order to taxonomies: {list(zip(parts, taxonomy_names))}")
            return [{"taxonomy": taxonomy, "text": part} for part, taxonomy in zip(parts, taxonomy_names)]

        # If we found some matches, return them
        if results:
            return results

    # Single intent or no multi-intent matches found
    taxonomy = _find_matching_taxonomy(user_input, taxonomy_names, debug)
    if taxonomy:
        results.append({"taxonomy": taxonomy, "text": user_input})
        if debug:
            logger.info(
                f"Single intent: assigned '{user_input}' to taxonomy '{taxonomy}'")

    return results


def _find_matching_taxonomy(text: str, taxonomy_names: List[str], debug: bool = False) -> Optional[str]:
    """Find the best matching taxonomy for the given text."""
    logger = Logger(__name__)
    text_lower = text.lower()

    # Look for exact taxonomy name matches first
    for name in taxonomy_names:
        if name.lower() in text_lower:
            if debug:
                logger.info(f"Found taxonomy '{name}' in text '{text}'")
            return name

    # Look for partial matches
    for name in taxonomy_names:
        name_words = name.lower().split('_')
        for word in name_words:
            if word in text_lower and len(word) > 2:
                if debug:
                    logger.info(
                        f"Found partial match: '{word}' from taxonomy '{name}' in text '{text}'")
                return name

    # Look for keyword-based matches
    keyword_mappings = {
        "travel": ["flight", "cancel", "book", "reserve", "trip", "travel", "airline"],
        "account": ["email", "update", "password", "reset", "account", "profile", "settings"],
        "support": ["support", "assist", "issue", "problem", "trouble"]
    }

    for taxonomy_name in taxonomy_names:
        if taxonomy_name in keyword_mappings:
            keywords = keyword_mappings[taxonomy_name]
            for keyword in keywords:
                if keyword in text_lower:
                    if debug:
                        logger.info(
                            f"Found keyword match: '{keyword}' for taxonomy '{taxonomy_name}' in text '{text}'")
                    return taxonomy_name

    if debug:
        logger.warning(f"No taxonomy match found for text: '{text}'")
    return None
