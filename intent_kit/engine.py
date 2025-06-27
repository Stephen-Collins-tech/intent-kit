from typing import Any, Callable, Dict, Optional
from .node import IntentNode, ClassifierNode, TaxonomyNode
from .utils.logger import Logger
from .context import IntentContext

logger = Logger("engine")


def execute_taxonomy(
    *,
    user_input: str,
    node: TaxonomyNode,
    context: Optional[IntentContext] = None,
    debug: bool = False
) -> Dict[str, Any]:
    """
    Execute the intent taxonomy tree for a given user input and optional context.

    Args:
        user_input: The input string to process
        node: The root node of the taxonomy tree
        context: Optional context object for state sharing
        debug: Whether to print debug information

    Returns:
        Dict containing:
            - intent: Name of the matched intent
            - node_name: Name of the matched node
            - params: Extracted parameters
            - output: Result of handler execution
            - error: Error message if any
            - execution_path: List of all nodes executed with their results
    """
    # Execute the root node, which will recursively execute all children
    result = node.execute(user_input, context)

    # Flatten the results to get the complete execution path
    execution_path = flatten_execution_results(result)

    # Find the final intent result (the last intent node in the path)
    final_intent = None
    final_node_name = None
    final_params = None
    final_output = None
    final_error = result.get("error")

    for node_result in execution_path:
        if node_result["node_type"] == "intent":
            final_intent = node_result["node_name"]
            final_node_name = node_result["node_name"]
            final_params = node_result["params"]
            final_output = node_result["output"]
            final_error = node_result.get("error")

    return {
        "intent": final_intent,
        "node_name": final_node_name,
        "params": final_params,
        "output": final_output,
        "error": final_error,
        "execution_path": execution_path
    }


def flatten_execution_results(result: Dict[str, Any]) -> list:
    """
    Flatten the nested execution results into a flat list showing the complete path.

    Args:
        result: The result from a node execution

    Returns:
        List of node results in execution order
    """
    execution_path = []

    # Add the current node result
    execution_path.append({
        "node_name": result["node_name"],
        "node_path": result["node_path"],
        "node_type": result["node_type"],
        "params": result["params"],
        "output": result["output"],
        "error": result.get("error")
    })

    # Recursively add children results
    for child_result in result.get("children_results", []):
        child_path = flatten_execution_results(child_result)
        execution_path.extend(child_path)

    return execution_path
