"""
Context Debugging Utilities

This module provides utilities for debugging context state, dependencies, and flow
through intent graphs. It includes functions for analyzing context dependencies,
generating debug output, and visualizing context flow.
"""

from typing import Dict, Any, Optional, List, cast
from datetime import datetime
import json
from . import IntentContext
from .dependencies import ContextDependencies, analyze_action_dependencies
from intent_kit.node import TreeNode
from intent_kit.utils.logger import Logger
from . import ContextHistoryEntry

logger = Logger(__name__)


def get_context_dependencies(graph: Any) -> Dict[str, ContextDependencies]:
    """
    Analyze the full dependency map for all nodes in a graph.

    Args:
        graph: IntentGraph instance to analyze

    Returns:
        Dictionary mapping node names to their context dependencies
    """
    dependencies = {}

    # Collect all nodes from root nodes
    all_nodes = []
    for root_node in graph.root_nodes:
        all_nodes.extend(_collect_all_nodes([root_node]))

    # Analyze dependencies for each node
    for node in all_nodes:
        node_deps = _analyze_node_dependencies(node)
        if node_deps:
            dependencies[node.name] = node_deps

    return dependencies


def validate_context_flow(graph: Any, context: IntentContext) -> Dict[str, Any]:
    """
    Validate the context flow for a graph and context.
    """
    dependencies = get_context_dependencies(graph)
    validation_results: Dict[str, Any] = {
        "valid": True,
        "missing_dependencies": {},
        "available_fields": set(context.keys()),
        "total_nodes": len(dependencies),
        "nodes_with_dependencies": 0,
        "warnings": [],
    }

    for node_name, deps in dependencies.items():
        validation = _validate_node_dependencies(deps, context)
        if not validation["valid"]:
            validation_results["valid"] = False
            validation_results["missing_dependencies"][node_name] = validation[
                "missing_inputs"
            ]

        if deps.inputs or deps.outputs:
            validation_results["nodes_with_dependencies"] += 1

    return validation_results


def trace_context_execution(
    graph: Any, user_input: str, context: IntentContext, output_format: str = "console"
) -> str:
    """
    Generate a detailed execution trace with context state changes.

    Args:
        graph: IntentGraph instance
        user_input: The user input that was processed
        context: Context object with execution history
        output_format: Output format ("console", "json")

    Returns:
        Formatted execution trace
    """
    # Capture history BEFORE we start reading context to avoid feedback loop
    history_before_debug: List[ContextHistoryEntry] = context.get_history()

    # Capture context state without adding to history
    context_state = _capture_full_context_state(context)

    # Analyze history to get operation counts
    set_ops = sum(
        1
        for entry in history_before_debug
        if hasattr(entry, "action") and entry.action == "set"
    )
    get_ops = sum(
        1
        for entry in history_before_debug
        if hasattr(entry, "action") and entry.action == "get"
    )
    delete_ops = sum(
        1
        for entry in history_before_debug
        if hasattr(entry, "action") and entry.action == "delete"
    )

    # Cast to satisfy mypy
    cast_dict = cast(Dict[str, Any], context_state["history_summary"])
    cast_dict.update(
        {
            "total_entries": len(history_before_debug),
            "set_operations": set_ops,
            "get_operations": get_ops,
            "delete_operations": delete_ops,
        }
    )

    trace_data = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "session_id": context.session_id,
        "execution_summary": {
            "total_fields": len(context.keys()),
            "history_entries": len(history_before_debug),
            "error_count": context.error_count(),
        },
        "context_state": context_state,
        "history": _format_context_history(history_before_debug),
    }

    if output_format == "json":
        json_str = json.dumps(trace_data, indent=2, default=str)
        return json_str
    else:  # console format
        return _format_console_trace(trace_data)


def _collect_all_nodes(nodes: List[TreeNode]) -> List[TreeNode]:
    """Recursively collect all nodes in a graph."""
    all_nodes = []
    visited = set()

    def collect_node(node: TreeNode):
        if node.node_id in visited:
            return
        visited.add(node.node_id)
        all_nodes.append(node)

        for child in node.children:
            collect_node(child)

    for node in nodes:
        collect_node(node)

    return all_nodes


def _analyze_node_dependencies(node: TreeNode) -> Optional[ContextDependencies]:
    """
    Analyze context dependencies for a specific node.

    Args:
        node: TreeNode to analyze

    Returns:
        ContextDependencies if analysis is possible, None otherwise
    """
    # Check if node has explicit dependencies
    if hasattr(node, "context_inputs") and hasattr(node, "context_outputs"):
        inputs: set = getattr(node, "context_inputs", set())
        outputs: set = getattr(node, "context_outputs", set())
        return ContextDependencies(
            inputs=inputs, outputs=outputs, description=f"Dependencies for {node.name}"
        )

    # Check if node has a handler function (HandlerNode)
    if hasattr(node, "handler"):
        handler = getattr(node, "handler")
        if callable(handler):
            return analyze_action_dependencies(handler)

    # Check if node has a classifier function (ClassifierNode)
    if hasattr(node, "classifier"):
        classifier = getattr(node, "classifier")
        if callable(classifier):
            # Classifiers typically don't modify context, but they might read from it
            return ContextDependencies(
                inputs=set(),
                outputs=set(),
                description=f"Classifier {node.name} (no context dependencies detected)",
            )

    return None


def _validate_node_dependencies(
    deps: ContextDependencies, context: IntentContext
) -> Dict[str, Any]:
    """
    Validate dependencies for a specific node against a context.

    Args:
        deps: ContextDependencies to validate
        context: Context to validate against

    Returns:
        Validation results dictionary
    """
    available_fields = context.keys()
    missing_inputs = deps.inputs - available_fields

    return {
        "valid": len(missing_inputs) == 0,
        "missing_inputs": missing_inputs,
        "available_inputs": deps.inputs & available_fields,
        "outputs": deps.outputs,
    }


def _capture_full_context_state(context: IntentContext) -> Dict[str, Any]:
    """
    Capture the complete state of a context object without adding to history.

    Args:
        context: Context to capture

    Returns:
        Dictionary with complete context state
    """
    state: Dict[str, Any] = {
        "session_id": context.session_id,
        "field_count": len(context.keys()),
        "fields": {},
        "history_summary": {
            "total_entries": 0,  # Will be set by caller
            "set_operations": 0,
            "get_operations": 0,
            "delete_operations": 0,
        },
        "error_summary": {"total_errors": context.error_count(), "recent_errors": []},
    }
    fields: Dict[str, Any] = state["fields"]

    # Capture all field values and metadata directly from internal state
    # to avoid adding GET operations to history
    with context._global_lock:
        for key, field in context._fields.items():
            with field.lock:
                value = field.value
                metadata = {
                    "created_at": field.created_at.isoformat(),
                    "last_modified": field.last_modified.isoformat(),
                    "modified_by": field.modified_by,
                }
                fields[key] = {"value": value, "metadata": metadata}

    # Get recent errors
    errors = context.get_errors(limit=5)
    state["error_summary"]["recent_errors"] = [
        {
            "timestamp": error.timestamp.isoformat(),
            "node_name": error.node_name,
            "error_message": error.error_message,
            "error_type": error.error_type,
        }
        for error in errors
    ]

    return state


def _format_context_history(history: List[Any]) -> List[Dict[str, Any]]:
    """
    Format context history for output.

    Args:
        history: List of context history entries

    Returns:
        Formatted history list
    """
    formatted = []
    for entry in history:
        formatted.append(
            {
                "timestamp": entry.timestamp.isoformat(),
                "action": entry.action,
                "key": entry.key,
                "value": entry.value,
                "modified_by": entry.modified_by,
            }
        )
    return formatted


def _format_console_trace(trace_data: Dict[str, Any]) -> str:
    """
    Format trace data for console output with soft colorization using Logger.

    Args:
        trace_data: Trace data dictionary

    Returns:
        Formatted console string with soft ANSI color codes
    """
    lines = []
    lines.append(logger.colorize_separator("=" * 60))
    lines.append(logger.colorize_section_title("CONTEXT EXECUTION TRACE"))
    lines.append(logger.colorize_separator("=" * 60))
    lines.append(
        logger.colorize_key_value(
            "Timestamp", trace_data["timestamp"], "field_label", "timestamp"
        )
    )
    lines.append(
        logger.colorize_key_value(
            "User Input", trace_data["user_input"], "field_label", "field_value"
        )
    )
    lines.append(
        logger.colorize_key_value(
            "Session ID", trace_data["session_id"], "field_label", "timestamp"
        )
    )
    lines.append("")

    # Execution summary
    summary = trace_data["execution_summary"]
    lines.append(logger.colorize_section_title("EXECUTION SUMMARY:"))
    lines.append(
        logger.colorize_key_value(
            "  Total Fields", summary["total_fields"], "field_label", "timestamp"
        )
    )
    lines.append(
        logger.colorize_key_value(
            "  History Entries", summary["history_entries"], "field_label", "timestamp"
        )
    )
    lines.append(
        logger.colorize_key_value(
            "  Error Count", summary["error_count"], "field_label", "timestamp"
        )
    )
    lines.append("")

    # Context state
    state = trace_data["context_state"]
    lines.append(logger.colorize_section_title("CONTEXT STATE:"))
    for key, field_data in state["fields"].items():
        value = field_data["value"]
        metadata = field_data["metadata"]

        # Format complex values more clearly
        if isinstance(value, list):
            lines.append(
                logger.colorize_key_value(
                    f"  {key}",
                    f"(list with {len(value)} items)",
                    "field_label",
                    "timestamp",
                )
            )
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    lines.append(
                        logger.colorize_key_value(
                            f"    [{i}]", dict(item), "field_label", "field_value"
                        )
                    )
                else:
                    lines.append(
                        logger.colorize_key_value(
                            f"    [{i}]", item, "field_label", "field_value"
                        )
                    )
        elif isinstance(value, dict):
            lines.append(
                logger.colorize_key_value(
                    f"  {key}",
                    f"(dict with {len(value)} items)",
                    "field_label",
                    "timestamp",
                )
            )
            for k, v in value.items():
                lines.append(
                    logger.colorize_key_value(
                        f"    {k}", v, "field_label", "field_value"
                    )
                )
        else:
            lines.append(
                logger.colorize_key_value(
                    f"  {key}", value, "field_label", "field_value"
                )
            )

        if metadata:
            lines.append(
                logger.colorize_key_value(
                    "    Modified",
                    metadata.get("last_modified", "Unknown"),
                    "field_label",
                    "timestamp",
                )
            )
            lines.append(
                logger.colorize_key_value(
                    "    By",
                    metadata.get("modified_by", "Unknown"),
                    "field_label",
                    "timestamp",
                )
            )
    lines.append("")

    # Recent history
    history = trace_data["history"]
    if history:
        lines.append(logger.colorize_section_title("RECENT HISTORY:"))
        for entry in history[-10:]:  # Last 10 entries
            timestamp = logger.colorize_timestamp(entry["timestamp"])
            action = logger.colorize_action(entry["action"].upper())
            key = logger.colorize_field_label(entry["key"])
            value = logger.colorize_field_value(str(entry["value"]))
            lines.append(f"  [{timestamp}] {action}: {key} = {value}")
        lines.append("")

    # Recent errors
    errors = state["error_summary"]["recent_errors"]
    if errors:
        lines.append(logger.colorize_section_title("RECENT ERRORS:"))
        for error in errors:
            timestamp = logger.colorize_timestamp(error["timestamp"])
            node_name = logger.colorize_error_soft(error["node_name"])
            error_msg = logger.colorize_error_soft(error["error_message"])
            lines.append(f"  [{timestamp}] {node_name}: {error_msg}")
        lines.append("")

    lines.append(logger.colorize_separator("=" * 60))
    return "\n".join(lines)
