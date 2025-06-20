from typing import Any, Callable, Dict, Optional
from .node import IntentNode, ClassifierNode, TaxonomyNode
from .utils.logger import Logger

logger = Logger("engine")


def execute_taxonomy(
    *,
    user_input: str,
    node: TaxonomyNode,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Execute the intent taxonomy tree for a given user input.

    Args:
        user_input: The input string to process
        node: The root node of the taxonomy tree
        debug: Whether to print debug information

    Returns:
        Dict containing:
            - intent: Name of the matched intent
            - params: Extracted parameters
            - output: Result of handler execution
            - error: Error message if any
    """
    current = node

    # Traverse the tree until we reach an Intent node
    while isinstance(current, ClassifierNode):
        if debug:
            logger.debug(
                f"At node: {current.name} (children: {[c.name for c in current.children]})")

        chosen = current.classifier(user_input, current.children)
        if not chosen:
            return {
                "intent": None,
                "params": None,
                "output": None,
                "error": f"Classifier at '{current.name}' could not route input."
            }
        current = chosen

    # We should now be at an Intent node
    if not isinstance(current, IntentNode):
        return {
            "intent": None,
            "params": None,
            "output": None,
            "error": "Reached non-intent leaf node."
        }

    # Execute the intent node
    result = current.execute(user_input)

    # Convert the new result format to the expected format
    return {
        "intent": current.name,
        "params": result["params"],
        "output": result["output"],
        "error": result["error"]
    }
