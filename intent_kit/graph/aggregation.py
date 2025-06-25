"""
Result aggregation logic for the IntentGraph.

This module handles combining results from multiple taxonomies and error handling.
"""

from typing import Dict, List, Any, Optional
from intent_kit.utils.logger import Logger


def aggregate_results(results: Optional[List[Dict]], errors: Optional[List[Dict]]) -> Dict[str, Any]:
    """
    Aggregate results from multiple taxonomies into a consistent format.

    Args:
        results: List of taxonomy results
        errors: List of error messages

    Returns:
        Consistent format dict: {"results": [...], "errors": [...]}
    """
    logger = Logger(__name__)

    # Ensure we always return the consistent format
    aggregated = {
        "results": results if results is not None else [],
        "errors": errors if errors is not None else []
    }

    logger.debug(
        f"Aggregated {len(aggregated['results'])} results and {len(aggregated['errors'])} errors")

    return aggregated


def create_error_dict(taxonomy: str, error_message: str, error_type: str = "Exception") -> Dict[str, str]:
    """
    Create a standardized error dictionary.

    Args:
        taxonomy: The taxonomy name that caused the error
        error_message: The error message
        error_type: The type of error (default: "Exception")

    Returns:
        Error dict with format: {"taxonomy": "name", "error": "type: message"}
    """
    return {
        "taxonomy": taxonomy,
        "error": f"{error_type}: {error_message}"
    }


def create_no_intent_error(suggestions: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create an error for when no recognizable intent is found.

    Args:
        suggestions: Optional list of suggested taxonomies

    Returns:
        Error dict for no intent found
    """
    error = {
        "error": "No recognizable intent found.",
        "suggestions": suggestions if suggestions is not None else []
    }

    return {
        "results": [],
        "errors": [error]
    }


def create_no_taxonomy_error(available_taxonomies: List[str]) -> Dict[str, Any]:
    """
    Create an error for when no taxonomy matches the input.

    Args:
        available_taxonomies: List of available taxonomy names

    Returns:
        Error dict for no taxonomy match
    """
    error = {
        "error": "No taxonomy matched input.",
        "available_taxonomies": available_taxonomies
    }

    return {
        "results": [],
        "errors": [error]
    }
