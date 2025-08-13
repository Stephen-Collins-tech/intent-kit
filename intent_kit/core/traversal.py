"""DAG traversal engine for intent-kit."""

from collections import deque
from time import perf_counter
from typing import Any, Dict, Optional, Tuple

from ..nodes.classifier import ClassifierNode
from ..nodes.action import ActionNode
from ..nodes.extractor import ExtractorNode
from ..nodes.clarification import ClarificationNode

from .exceptions import TraversalLimitError, TraversalError
from .types import IntentDAG, GraphNode
from .types import NodeProtocol, ExecutionResult
from .context import ContextProtocol, ContextPatch, DefaultContext
from ..services.ai.llm_service import LLMService


def run_dag(
    dag: IntentDAG,
    user_input: str,
    ctx: Optional[ContextProtocol] = None,
    max_steps: int = 1000,
    max_fanout_per_node: int = 16,
    enable_memoization: bool = False,
    llm_service: Optional[LLMService] = None,
) -> Tuple[ExecutionResult, ContextProtocol]:
    """Execute a DAG starting from entrypoints using BFS traversal.

    Args:
        dag: The DAG to execute
        user_input: The user input to process
        ctx: The execution context (defaults to DefaultContext if not provided)
        max_steps: Maximum number of steps to execute
        max_fanout_per_node: Maximum number of outgoing edges per node
        enable_memoization: Whether to enable node memoization
        llm_service: LLM service instance (defaults to new LLMService if not provided)

    Returns:
        Tuple of (last execution result, context)

    Raises:
        TraversalLimitError: When traversal limits are exceeded
        TraversalError: When traversal fails due to node errors
        ContextConflictError: When context patches conflict
    """
    if not dag.entrypoints:
        raise TraversalError("No entrypoints defined in DAG")

    # Create default context if not provided
    if ctx is None:
        ctx = DefaultContext()

    # Create default LLM service if not provided
    if llm_service is None:
        llm_service = LLMService()

    # Attach LLM service and DAG metadata to context
    ctx.set("llm_service", llm_service, modified_by="traversal:init")
    if hasattr(dag, "metadata"):
        ctx.set("metadata", dag.metadata, modified_by="traversal:init")

    # Initialize worklist with entrypoints
    q = deque(dag.entrypoints)
    seen_steps: set[tuple[str, Optional[str]]] = set()
    steps = 0
    last_result: Optional[ExecutionResult] = None
    total_metrics: Dict[str, Any] = {}
    context_patches: Dict[str, Dict[str, Any]] = {}
    memo_cache: Dict[tuple[str, str, str], ExecutionResult] = {}

    while q:
        node_id = q.popleft()
        steps += 1

        if steps > max_steps:
            raise TraversalLimitError(f"Exceeded max_steps limit of {max_steps}")

        node = dag.nodes[node_id]

        # Apply merged context patch for this node
        if node_id in context_patches:
            patch = ContextPatch(data=context_patches[node_id], provenance=node_id)
            ctx.apply_patch(patch)
            # Clear the patch after applying it
            del context_patches[node_id]

        # Check memoization cache
        if enable_memoization:
            cache_key = _create_memo_key(node_id, ctx, user_input)
            if cache_key in memo_cache:
                result = memo_cache[cache_key]
                if hasattr(ctx, "logger"):
                    input_summary = f"input='{user_input[:50]}{'...' if len(user_input) > 50 else ''}'"
                    output_summary = f"output='{str(result.data)[:50]}{'...' if len(str(result.data)) > 50 else ''}'"
                    ctx.logger.info(
                        f"Node execution completed (memoized): {node_id} ({node.type}) in 0.00ms | {input_summary} | {output_summary}"
                    )
                last_result = result
                _merge_metrics(total_metrics, result.metrics)

                # Apply context patch from memoized result
                if result.context_patch:
                    patch = ContextPatch(data=result.context_patch, provenance=node_id)
                    ctx.apply_patch(patch)

                if result.terminate:
                    break

                _enqueue_next_nodes(
                    dag,
                    node_id,
                    result,
                    q,
                    seen_steps,
                    max_fanout_per_node,
                    context_patches,
                )
                continue

        # Resolve node implementation
        impl = _create_node(node)

        if impl is None:
            raise TraversalError(f"Could not resolve implementation for node {node_id}")

        # Execute node
        t0 = perf_counter()

        # Track start of node execution
        if hasattr(ctx, "logger"):
            ctx.logger.debug(f"Node execution started: {node_id} ({node.type})")

        try:
            # Execute node - LLM service is now available in context
            result = impl.execute(user_input, ctx)
        except Exception as e:
            # Handle node execution errors
            dt = (perf_counter() - t0) * 1000
            if hasattr(ctx, "logger"):
                input_summary = (
                    f"input='{user_input[:50]}{'...' if len(user_input) > 50 else ''}'"
                )
                ctx.logger.error(
                    f"Node execution failed: {node_id} ({node.type}) after {dt:.2f}ms | {input_summary} | error: {str(e)}"
                )

            # Apply error context patch
            error_patch = {
                "last_error": str(e),
                "error_node": node_id,
                "error_type": type(e).__name__,
                "error_timestamp": perf_counter(),
            }

            # Route via "error" edge if exists
            if "error" in dag.adj.get(node_id, {}):
                for error_target in dag.adj[node_id]["error"]:
                    step = (error_target, "error")
                    if step not in seen_steps:
                        seen_steps.add(step)
                        q.append(error_target)
                        context_patches[error_target] = error_patch
            else:
                # Stop traversal if no error handler
                raise TraversalError(f"Node {node_id} failed: {e}")
            continue

        dt = (perf_counter() - t0) * 1000

        # Cache result if memoization enabled
        if enable_memoization:
            cache_key = _create_memo_key(node_id, ctx, user_input)
            memo_cache[cache_key] = result

        # Log execution
        if hasattr(ctx, "logger"):
            input_summary = (
                f"input='{user_input[:50]}{'...' if len(user_input) > 50 else ''}'"
            )
            output_summary = f"output='{str(result.data)[:50]}{'...' if len(str(result.data)) > 50 else ''}'"
            ctx.logger.info(
                f"Node execution completed: {node_id} ({node.type}) in {dt:.2f}ms | {input_summary} | {output_summary}"
            )

        # Update metrics
        _merge_metrics(total_metrics, result.metrics)

        # Apply context patch from current result
        if result.context_patch:
            patch = ContextPatch(data=result.context_patch, provenance=node_id)
            ctx.apply_patch(patch)

        # Store the last result
        last_result = result

        # Check if we should terminate
        if result.terminate:
            break

        # Enqueue next nodes (unless terminating)
        _enqueue_next_nodes(
            dag, node_id, result, q, seen_steps, max_fanout_per_node, context_patches
        )

    if last_result is None:
        raise TraversalError("No nodes were executed")

    return last_result, ctx


def _create_node(node: GraphNode) -> NodeProtocol:
    """Resolve a GraphNode to its implementation by directly creating known node types.

    This bypasses the registry system and directly creates nodes for known types.

    Args:
        node: The GraphNode to resolve

    Returns:
        A NodeProtocol instance

    Raises:
        NodeResolutionError: If the node type is not supported
    """
    node_type = node.type

    # Add node ID as name if not present
    config = node.config.copy()
    if "name" not in config:
        config["name"] = node.id

    if node_type == "classifier":
        # Provide default output_labels if not specified
        if "output_labels" not in config:
            config["output_labels"] = ["next", "error"]
        return ClassifierNode(**config)
    elif node_type == "action":
        # Provide default action if not specified
        if "action" not in config:
            config["action"] = lambda **kwargs: "default_action_result"
        return ActionNode(**config)
    elif node_type == "extractor":
        return ExtractorNode(**config)
    elif node_type == "clarification":
        return ClarificationNode(**config)
    else:
        raise ValueError(
            f"Unsupported node type '{node_type}'. "
            f"Supported types: classifier, action, extractor, clarification"
        )


def _create_memo_key(
    node_id: str, ctx: ContextProtocol, user_input: str
) -> tuple[str, str, str]:
    """Create a memoization key for a node execution.

    Args:
        node_id: The node ID
        ctx: The context
        user_input: The user input

    Returns:
        A tuple key for memoization
    """
    # Use the new fingerprint method for stable memoization
    context_hash = ctx.fingerprint()
    input_hash = hash(user_input)
    return (node_id, context_hash, str(input_hash))


def _enqueue_next_nodes(
    dag: IntentDAG,
    node_id: str,
    result: ExecutionResult,
    q: deque,
    seen_steps: set[tuple[str, Optional[str]]],
    max_fanout_per_node: int,
    context_patches: Dict[str, Dict[str, Any]],
) -> None:
    """Enqueue next nodes based on execution result.

    Args:
        dag: The DAG
        node_id: Current node ID
        result: Execution result
        q: Queue to add nodes to
        seen_steps: Set of seen steps
        max_fanout_per_node: Maximum fanout per node
        context_patches: Context patches for downstream nodes
    """
    labels = result.next_edges or []
    if not labels:
        return

    fanout_count = 0
    for label in labels:
        outgoing_edges = dag.adj.get(node_id, {}).get(label, set())
        for next_node in outgoing_edges:
            step = (next_node, label)
            if step not in seen_steps:
                seen_steps.add(step)
                q.append(next_node)
                fanout_count += 1

                if fanout_count > max_fanout_per_node:
                    raise TraversalLimitError(
                        f"Exceeded max_fanout_per_node limit of {max_fanout_per_node} for node {node_id}"
                    )

                # Merge context patches for downstream nodes
                if result.context_patch:
                    if next_node not in context_patches:
                        context_patches[next_node] = {}
                    context_patches[next_node].update(result.context_patch)


def _merge_metrics(total_metrics: Dict[str, Any], node_metrics: Dict[str, Any]) -> None:
    """Merge node metrics into total metrics.

    Args:
        total_metrics: The total metrics to update
        node_metrics: The node metrics to merge
    """
    for key, value in node_metrics.items():
        if key in total_metrics:
            # For numeric values, add them; otherwise replace
            if isinstance(total_metrics[key], (int, float)) and isinstance(
                value, (int, float)
            ):
                total_metrics[key] += value
            else:
                total_metrics[key] = value
        else:
            total_metrics[key] = value
