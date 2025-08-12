"""DAG traversal engine for intent-kit."""

from collections import deque
from time import perf_counter
from typing import Any, Callable, Dict, Optional, Tuple

from ..nodes.classifier import ClassifierNode
from ..nodes.action import ActionNode
from ..nodes.extractor import DAGExtractorNode
from ..nodes.clarification import ClarificationNode

from .exceptions import TraversalLimitError, TraversalError, ContextConflictError
from .types import IntentDAG
from .types import NodeProtocol, ExecutionResult, Context


def run_dag(
    dag: IntentDAG,
    ctx: Context,
    user_input: str,
    max_steps: int = 1000,
    max_fanout_per_node: int = 16,
    resolve_impl: Optional[Callable[[Any], NodeProtocol]] = None,
    enable_memoization: bool = False,
    llm_service: Optional[Any] = None,
) -> Tuple[Optional[ExecutionResult], Dict[str, Any]]:
    """Execute a DAG starting from entrypoints using BFS traversal.

    Args:
        dag: The DAG to execute
        ctx: The execution context
        user_input: The user input to process
        max_steps: Maximum number of steps to execute
        max_fanout_per_node: Maximum number of outgoing edges per node
        resolve_impl: Function to resolve node type to implementation
        enable_memoization: Whether to enable node memoization

    Returns:
        Tuple of (last execution result, aggregated metrics)

    Raises:
        TraversalLimitError: When traversal limits are exceeded
        TraversalError: When traversal fails due to node errors
        ContextConflictError: When context patches conflict
    """
    if not dag.entrypoints:
        raise TraversalError("No entrypoints defined in DAG")

    # Attach LLM service to context if provided
    if llm_service is not None:
        ctx.set("llm_service", llm_service, modified_by="traversal:init")

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
            raise TraversalLimitError(
                f"Exceeded max_steps limit of {max_steps}")

        node = dag.nodes[node_id]

        # Apply merged context patch for this node
        if node_id in context_patches:
            _apply_context_patch(ctx, context_patches[node_id], node_id)
            # Clear the patch after applying it
            del context_patches[node_id]

        # Check memoization cache
        if enable_memoization:
            cache_key = _create_memo_key(node_id, ctx, user_input)
            if cache_key in memo_cache:
                result = memo_cache[cache_key]
                _log_node_execution(node_id, node.type, 0.0, result, ctx)
                last_result = result
                _merge_metrics(total_metrics, result.metrics)

                # Apply context patch from memoized result
                if result.context_patch:
                    _apply_context_patch(ctx, result.context_patch, node_id)

                if result.terminate:
                    break

                _enqueue_next_nodes(
                    dag, node_id, result, q, seen_steps,
                    max_fanout_per_node, context_patches
                )
                continue

        # Resolve node implementation
        if resolve_impl is None:
            raise TraversalError(
                f"No implementation resolver provided for node {node_id}")

        impl = resolve_impl(node)
        if impl is None:
            raise TraversalError(
                f"Could not resolve implementation for node {node_id}")

        # Execute node
        t0 = perf_counter()
        try:
            # Execute node - LLM service is now available in context
            result = impl.execute(user_input, ctx)
        except Exception as e:
            # Handle node execution errors
            dt = (perf_counter() - t0) * 1000
            _log_node_error(node_id, node.type, dt, str(e), ctx)

            # Apply error context patch
            error_patch = {
                "last_error": str(e),
                "error_node": node_id,
                "error_type": type(e).__name__,
                "error_timestamp": perf_counter()
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
        _log_node_execution(node_id, node.type, dt, result, ctx)

        # Update metrics
        _merge_metrics(total_metrics, result.metrics)

        # Apply context patch from current result
        if result.context_patch:
            _apply_context_patch(ctx, result.context_patch, node_id)

        last_result = result

        # Enqueue next nodes (unless terminating)
        if not result.terminate:
            _enqueue_next_nodes(
                dag, node_id, result, q, seen_steps,
                max_fanout_per_node, context_patches
            )

    return last_result, total_metrics


def resolve_impl_direct(node: Any) -> NodeProtocol:
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
    if 'name' not in config:
        config['name'] = node.id

    if node_type == "dag_classifier":
        return ClassifierNode(**config)
    elif node_type == "dag_action":
        return ActionNode(**config)
    elif node_type == "dag_extractor":
        return DAGExtractorNode(**config)
    elif node_type == "dag_clarification":
        return ClarificationNode(**config)
    else:
        raise ValueError(
            f"Unsupported node type '{node_type}'. "
            f"Supported types: dag_classifier, dag_action, dag_extractor, dag_clarification"
        )


def _apply_context_patch(ctx: Context, patch: Dict[str, Any], node_id: str) -> None:
    """Apply a context patch to the context.

    Args:
        ctx: The context to update
        patch: The patch to apply
        node_id: The node ID for logging
    """
    for key, value in patch.items():
        try:
            ctx.set(key, value, modified_by=f"traversal:{node_id}")
        except Exception as e:
            raise ContextConflictError(
                f"Failed to apply context patch for key '{key}' from node {node_id}: {e}"
            )


def _create_memo_key(node_id: str, ctx: Context, user_input: str) -> tuple[str, str, str]:
    """Create a memoization key for a node execution.

    Args:
        node_id: The node ID
        ctx: The context
        user_input: The user input

    Returns:
        A tuple key for memoization
    """
    # Create a hash of important context fields
    context_hash = hash(str(sorted(ctx.keys())))
    input_hash = hash(user_input)
    return (node_id, str(context_hash), str(input_hash))


def _enqueue_next_nodes(
    dag: IntentDAG,
    node_id: str,
    result: ExecutionResult,
    q: deque,
    seen_steps: set[tuple[str, Optional[str]]],
    max_fanout_per_node: int,
    context_patches: Dict[str, Dict[str, Any]]
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
            if isinstance(total_metrics[key], (int, float)) and isinstance(value, (int, float)):
                total_metrics[key] += value
            else:
                total_metrics[key] = value
        else:
            total_metrics[key] = value


def _log_node_execution(
    node_id: str,
    node_type: str,
    duration_ms: float,
    result: ExecutionResult,
    ctx: Context
) -> None:
    """Log node execution details.

    Args:
        node_id: The node ID
        node_type: The node type
        duration_ms: Execution duration in milliseconds
        result: The execution result
        ctx: The context
    """
    log_data = {
        "node_id": node_id,
        "node_type": node_type,
        "duration_ms": round(duration_ms, 2),
        "terminate": result.terminate,
        "next_edges": result.next_edges,
        "context_patch_keys": list(result.context_patch.keys()) if result.context_patch else [],
        "metrics": result.metrics
    }

    if hasattr(ctx, 'logger'):
        ctx.logger.info(log_data)
    else:
        print(f"Node execution: {log_data}")


def _log_node_error(
    node_id: str,
    node_type: str,
    duration_ms: float,
    error_message: str,
    ctx: Context
) -> None:
    """Log node error details.

    Args:
        node_id: The node ID
        node_type: The node type
        duration_ms: Execution duration in milliseconds
        error_message: The error message
        ctx: The context
    """
    log_data = {
        "node_id": node_id,
        "node_type": node_type,
        "duration_ms": round(duration_ms, 2),
        "error": error_message,
        "status": "error"
    }

    if hasattr(ctx, 'logger'):
        ctx.logger.error(log_data)
    else:
        print(f"Node error: {log_data}")
