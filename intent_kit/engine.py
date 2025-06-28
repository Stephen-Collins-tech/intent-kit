from typing import Any, Callable, Dict, Optional
from .node import IntentNode, ClassifierNode, TaxonomyNode, ExecutionResult, ExecutionError
from .utils.logger import Logger
from .context import IntentContext

logger = Logger("engine")


def execute_taxonomy(
    *,
    user_input: str,
    node: TaxonomyNode,
    context: Optional[IntentContext] = None,
    debug: bool = False
) -> ExecutionResult:
    """
    Execute the intent taxonomy tree for a given user input and optional context.

    Args:
        user_input: The input string to process
        node: The root node of the taxonomy tree
        context: Optional context object for state sharing
        debug: Whether to print debug information

    Returns:
        ExecutionResult containing:
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

    # Find the final successful intent result (the last successful intent node in the path)
    final_intent = None
    final_node_name = None
    final_params = None
    final_output = None
    final_error = result.error.message if result.error else None

    # Collect all errors from the execution path for debugging
    execution_errors = []
    for node_result in execution_path:
        if node_result.get("error"):
            execution_errors.append({
                "node_name": node_result["node_name"],
                "node_path": node_result["node_path"],
                "node_type": node_result["node_type"],
                "error": node_result["error"]
            })

    for node_result in execution_path:
        if node_result["node_type"] == "intent" and node_result.get("success", True):
            # Only consider successful intent nodes
            final_intent = node_result["node_name"]
            final_node_name = node_result["node_name"]
            final_params = node_result["params"]
            final_output = node_result["output"]
            # Preserve error information even for successful nodes (for debugging)
            final_error = node_result.get(
                "error").message if node_result.get("error") else None

    # If no successful intent node, set error from the first failed intent node or root
    if final_intent is None:
        for node_result in execution_path:
            if node_result["node_type"] == "intent" and node_result.get("error"):
                final_error = node_result["error"].message if node_result["error"] else None
                break
        # fallback to root error if still None
        if final_error is None:
            final_error = result.error.message if result.error else None
        final_params = None
        final_output = None

    return ExecutionResult(
        success=final_intent is not None,
        params=final_params,
        children_results=[],
        node_name=final_node_name or "unknown",
        node_path=[],
        node_type="taxonomy",
        input=user_input,
        output=final_output,
        error=ExecutionError(
            error_type="TaxonomyError",
            message=final_error or "Unknown error",
            node_name=final_node_name or "unknown",
            node_path=[]
        ) if final_error else None
    )


def flatten_execution_results(result: ExecutionResult) -> list:
    """
    Flatten the nested execution results into a flat list showing the complete path.

    Args:
        result: The result from a node execution

    Returns:
        List of node results in execution order
    """
    execution_path = []

    # Add the current node result
    # Preserve error information even when success is True for debugging purposes
    # This ensures we don't lose error information from the execution path
    execution_path.append({
        "node_name": result.node_name,
        "node_path": result.node_path,
        "node_type": result.node_type,
        "success": result.success,
        "input": result.input,
        "output": result.output,
        "error": result.error,  # Always preserve error information
        "params": result.params
    })

    # Recursively add children results
    for child_result in result.children_results:
        child_path = flatten_execution_results(child_result)
        execution_path.extend(child_path)

    return execution_path
