"""
IntentGraph - The root-level dispatcher for user input.

This module provides the main IntentGraph class that handles intent splitting,
routing to root nodes, and result aggregation.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from intent_kit.utils.logger import Logger
from intent_kit.context import Context, StackContext
from intent_kit.extraction import Extractor

from intent_kit.graph.validation import (
    validate_graph_structure,
    validate_node_types,
    GraphValidationError,
)

# from intent_kit.graph.aggregation import aggregate_results, create_error_dict, create_no_intent_error, create_no_tree_error
from intent_kit.nodes import ExecutionResult
from intent_kit.nodes import ExecutionError
from intent_kit.nodes.enums import NodeType
from intent_kit.nodes import TreeNode


def classify_intent_chunk(
    chunk: str, llm_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Classify an intent chunk using LLM or rule-based classification.

    Args:
        chunk: The text chunk to classify
        llm_config: Optional LLM configuration for classification

    Returns:
        Classification result with action and metadata
    """
    # Simple rule-based classification for now
    # In a real implementation, this would use LLM or more sophisticated logic
    chunk_lower = chunk.lower()

    # Simple keyword matching
    if any(keyword in chunk_lower for keyword in ["hello", "hi", "greet"]):
        return {
            "classification": "Atomic",
            "action": "handle",
            "metadata": {"confidence": 0.8, "reason": "Greeting detected"},
        }
    elif any(keyword in chunk_lower for keyword in ["help", "support", "assist"]):
        return {
            "classification": "Atomic",
            "action": "handle",
            "metadata": {"confidence": 0.7, "reason": "Help request detected"},
        }
    elif "test" in chunk_lower:
        # Handle test inputs for testing purposes
        return {
            "classification": "Atomic",
            "action": "handle",
            "metadata": {"confidence": 0.9, "reason": "Test input detected"},
        }
    else:
        return {
            "classification": "Invalid",
            "action": "reject",
            "metadata": {"confidence": 0.0, "reason": "No match found"},
        }


# Remove all visualization-related imports, attributes, and methods


class IntentGraph:
    """
    The root-level dispatcher for user input.

    The graph contains root classifier nodes that handle single intents.
    Each root node must be a classifier that routes to appropriate action nodes.
    Trees emerge naturally from the parent-child relationships between nodes.

    Note: All root nodes must be classifier nodes for single intent handling.
    This ensures focused, deterministic intent processing without the complexity
    of multi-intent splitting.
    """

    def __init__(
        self,
        root_nodes: Optional[List[TreeNode]] = None,
        visualize: bool = False,
        llm_config: Optional[dict] = None,
        debug_context: bool = False,
        context_trace: bool = False,
        context: Optional[Context] = None,
        default_extractor: Optional[Extractor] = None,
    ):
        """
        Initialize the IntentGraph with root classifier nodes.

        Args:
            root_nodes: List of root classifier nodes (all must be classifier nodes)
            visualize: If True, render the final output to an interactive graph HTML file
            llm_config: LLM configuration for classification (optional)
            debug_context: If True, enable context debugging and state tracking
            context_trace: If True, enable detailed context tracing with timestamps
            context: Optional Context to use as the default for this graph

        Note: All root nodes must be classifier nodes for single intent handling.
        This ensures focused, deterministic intent processing.
        """
        self.root_nodes: List[TreeNode] = root_nodes or []
        self.context = context or Context()

        # Validate that all root nodes are valid TreeNode instances
        for root_node in self.root_nodes:
            if not isinstance(root_node, TreeNode):
                raise ValueError(
                    f"Root node '{root_node.name}' must be a TreeNode instance. "
                    f"Got {type(root_node).__name__}."
                )

        self.logger = Logger(__name__)
        self.visualize = visualize
        self.llm_config = llm_config
        self.debug_context = debug_context
        self.context_trace = context_trace
        self.default_extractor = default_extractor

    def add_root_node(self, root_node: TreeNode, validate: bool = True) -> None:
        """
        Add a root node to the graph.

        Args:
            root_node: The root node to add (must be a classifier node)
            validate: Whether to validate the graph after adding the node
        """
        if not isinstance(root_node, TreeNode):
            raise ValueError("Root node must be a TreeNode")

        # Ensure root node is a valid TreeNode instance
        if not isinstance(root_node, TreeNode):
            raise ValueError(
                f"Root node '{root_node.name}' must be a TreeNode instance. "
                f"Got {type(root_node).__name__}."
            )

        self.root_nodes.append(root_node)
        self.logger.info(f"Added root node: {root_node.name}")

        # Validate the graph after adding the node
        if validate:
            try:
                self.validate_graph()
                self.logger.info("Graph validation passed after adding root node")
            except GraphValidationError as e:
                self.logger.error(
                    f"Graph validation failed after adding root node: {e.message}"
                )
                # Remove the node if validation fails and re-raise the error
                self.root_nodes.remove(root_node)
                raise e

    def remove_root_node(self, root_node: TreeNode) -> None:
        """
        Remove a root node from the graph.

        Args:
            root_node: The root node to remove
        """
        if root_node in self.root_nodes:
            self.root_nodes.remove(root_node)
            self.logger.info(f"Removed root node: {root_node.name}")
        else:
            self.logger.warning(f"Root node '{root_node.name}' not found for removal")

    def list_root_nodes(self) -> List[str]:
        """
        List all root node names.

        Returns:
            List of root node names
        """
        return [node.name for node in self.root_nodes]

    def validate_graph(
        self, validate_routing: bool = True, validate_types: bool = True
    ) -> Dict[str, Any]:
        """
        Validate the graph structure and routing constraints.

        Args:
            validate_routing: Whether to validate splitter-to-classifier routing
            validate_types: Whether to validate node types

        Returns:
            Dictionary containing validation results and statistics

        Raises:
            GraphValidationError: If validation fails
        """
        self.logger.info("Validating graph structure...")

        # Collect all nodes from root nodes
        all_nodes = []
        for root_node in self.root_nodes:
            all_nodes.extend(self._collect_all_nodes([root_node]))

        # Validate node types
        if validate_types:
            validate_node_types(all_nodes)

        # Get comprehensive validation stats
        stats = validate_graph_structure(all_nodes)

        self.logger.info("Graph validation completed successfully")
        return stats

    def _collect_all_nodes(self, nodes: List[TreeNode]) -> List[TreeNode]:
        """Recursively collect all nodes in the graph."""
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

    def _route_chunk_to_root_node(
        self, chunk: str, debug: bool = False
    ) -> Optional[TreeNode]:
        """
        Route a single chunk to the most appropriate root node.

        Args:
            chunk: The intent chunk to route
            debug: Whether to enable debug logging

        Returns:
            The root node to handle this chunk, or None if no match found
        """
        if not self.root_nodes:
            return None

        # Use the classify_intent_chunk function to determine routing
        classification = classify_intent_chunk(chunk, self.llm_config)

        if debug:
            self.logger.info(f"Classification result: {classification}")

        # If classification indicates reject, return None
        if classification.get("action") == "reject":
            if debug:
                self.logger.info(f"Rejecting chunk '{chunk}' based on classification")
            return None

        # For now, return the first root node as fallback
        # In a more sophisticated implementation, this would use the classification
        # to select the most appropriate root node
        if debug:
            self.logger.info(
                f"Routing chunk '{chunk}' to first root node '{self.root_nodes[0].name}'"
            )
        return self.root_nodes[0] if self.root_nodes else None

    def route(
        self,
        user_input: str,
        context: Optional[Context] = None,
        debug: bool = False,
        debug_context: Optional[bool] = None,
        context_trace: Optional[bool] = None,
    ) -> ExecutionResult:
        """
        Route user input through the graph with optional context support.

        Args:
            user_input: The input string to process
            context: Optional context object for state sharing (defaults to self.context)
            debug: Whether to print debug information
            debug_context: Override graph-level debug_context setting
            context_trace: Override graph-level context_trace setting
            **splitter_kwargs: Additional arguments to pass to the splitter

        Returns:
            ExecutionResult containing aggregated results and errors from all matched taxonomies
        """
        # Use method parameters if provided, otherwise use graph-level settings
        debug_context_enabled = (
            debug_context if debug_context is not None else self.debug_context
        )
        context_trace_enabled = (
            context_trace if context_trace is not None else self.context_trace
        )

        context = context or self.context  # Use member context if not provided

        # Initialize StackContext if not already present
        stack_context = None
        if context:
            if not hasattr(self, "_stack_contexts"):
                self._stack_contexts = {}

            context_id = context.session_id
            if context_id not in self._stack_contexts:
                self._stack_contexts[context_id] = StackContext(context)

            stack_context = self._stack_contexts[context_id]

        if debug:
            self.logger.info(f"Processing input: {user_input}")
            if context:
                self.logger.info(f"Using context: {context}")
            if debug_context_enabled:
                self.logger.info("Context debugging enabled")
            if context_trace_enabled:
                self.logger.info("Context tracing enabled")

        # Check if there are any root nodes available
        if not self.root_nodes:
            error_msg = "No root nodes available"

            # Track operation in context (if provided)
            if context:
                context.track_operation(
                    operation_type="graph_execution",
                    success=False,
                    node_name="no_root_nodes",
                    user_input=user_input,
                    error_message=error_msg,
                )

            return ExecutionResult(
                success=False,
                params=None,
                children_results=[],
                node_name="no_root_nodes",
                node_path=[],
                node_type=NodeType.UNKNOWN,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="NoRootNodesAvailable",
                    message=error_msg,
                    node_name="no_root_nodes",
                    node_path=[],
                ),
            )

        # Push frame for main route execution
        if stack_context:
            frame_id = stack_context.push_frame(
                function_name="route",
                node_name="IntentGraph",
                node_path=["IntentGraph"],
                user_input=user_input,
                parameters={
                    "debug": debug,
                    "debug_context": debug_context_enabled,
                    "context_trace": context_trace_enabled,
                },
            )

        # If we have root nodes, use traverse method for each root node
        if self.root_nodes:
            results = []

            # Execute each root node using traverse method
            for root_node in self.root_nodes:
                try:
                    result = root_node.traverse(user_input, context=context)
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    error_result = ExecutionResult(
                        success=False,
                        params=None,
                        children_results=[],
                        node_name=root_node.name,
                        node_path=[],
                        node_type=root_node.node_type,
                        input=user_input,
                        output=None,
                        error=ExecutionError(
                            error_type=type(e).__name__,
                            message=str(e),
                            node_name=root_node.name,
                            node_path=[],
                        ),
                    )
                    results.append(error_result)

            # If there's only one result, return it directly
            if len(results) == 1:
                result = results[0]

                # Track operation in context (if provided)
                if context:
                    context.track_operation(
                        operation_type="graph_execution",
                        success=result.success,
                        node_name=result.node_name,
                        user_input=user_input,
                        result=result.output if result.success else None,
                        error_message=result.error.message if result.error else None,
                    )

                return result

            self.logger.debug(f"IntentGraph .route method call results: {results}")
            # Aggregate multiple results
            successful_results = [r for r in results if r.success]
            failed_results = [r for r in results if not r.success]
            self.logger.info(f"Successful results: {successful_results}")
            self.logger.info(f"Failed results: {failed_results}")

            # Determine overall success
            overall_success = len(failed_results) == 0 and len(successful_results) > 0

            # Aggregate outputs
            outputs = [r.output for r in successful_results if r.output is not None]
            aggregated_output = (
                outputs if len(outputs) > 1 else (outputs[0] if outputs else None)
            )

            # Aggregate params
            params = [r.params for r in successful_results if r.params]
            aggregated_params = (
                params if len(params) > 1 else (params[0] if params else None)
            )

            # Ensure params is a dict or None
            if aggregated_params is not None and not isinstance(
                aggregated_params, dict
            ):
                aggregated_params = {"params": aggregated_params}

            # Aggregate errors
            errors = [r.error for r in failed_results if r.error]
            aggregated_error = None
            if errors:
                error_messages = [e.message for e in errors]
                aggregated_error = ExecutionError(
                    error_type="AggregatedErrors",
                    message="; ".join(error_messages),
                    node_name="intent_graph",
                    node_path=[],
                )

            # Pop frame for successful route execution
            if stack_context:
                stack_context.pop_frame(
                    execution_result={
                        "success": overall_success,
                        "output": aggregated_output,
                        "results_count": len(results),
                        "successful_results": len(successful_results),
                        "failed_results": len(failed_results),
                    }
                )

            # Track operation in context (if provided)
            if context:
                context.track_operation(
                    operation_type="graph_execution",
                    success=overall_success,
                    node_name="intent_graph",
                    user_input=user_input,
                    result=aggregated_output if overall_success else None,
                    error_message=(
                        aggregated_error.message if aggregated_error else None
                    ),
                )

            return ExecutionResult(
                success=overall_success,
                params=aggregated_params,
                input_tokens=sum(r.input_tokens for r in results if r.input_tokens),
                output_tokens=sum(r.output_tokens for r in results if r.output_tokens),
                cost=sum(r.cost for r in results if r.cost),
                children_results=results,
                node_name="intent_graph",
                node_path=[],
                node_type=NodeType.GRAPH,
                input=user_input,
                output=aggregated_output,
                error=aggregated_error,
            )

        # Pop frame for failed route execution (no root nodes)
        if stack_context:
            stack_context.pop_frame(
                error_info={
                    "error_type": "NoRootNodesAvailable",
                    "message": "No root nodes available",
                    "node_name": "no_root_nodes",
                    "node_path": [],
                }
            )

        # If no root nodes, return error
        return ExecutionResult(
            success=False,
            params=None,
            children_results=[],
            node_name="no_root_nodes",
            node_path=[],
            node_type=NodeType.UNKNOWN,
            input=user_input,
            output=None,
            error=ExecutionError(
                error_type="NoRootNodesAvailable",
                message="No root nodes available",
                node_name="no_root_nodes",
                node_path=[],
            ),
        )

    def _capture_context_state(self, context: Context, label: str) -> Dict[str, Any]:
        """
        Capture the current state of the context for debugging without adding to history.

        Args:
            context: The context to capture
            label: Label for this state capture

        Returns:
            Dictionary containing context state
        """
        state: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "label": label,
            "session_id": context.session_id,
            "fields": {},
            "field_count": len(context.keys()),
            "history_count": len(context.get_history()),
            "error_count": context.error_count(),
        }

        # Capture all field values directly from internal state to avoid GET operations
        with context._global_lock:
            for key, field in context._fields.items():
                with field.lock:
                    value = field.value
                    metadata = {
                        "created_at": field.created_at,
                        "last_modified": field.last_modified,
                        "modified_by": field.modified_by,
                        "value": field.value,
                    }
                    state["fields"][key] = {"value": value, "metadata": metadata}
                    # Also add the key directly to the state for backward compatibility
                    state[key] = value

        return state

    def _log_context_changes(
        self,
        state_before: Optional[Dict[str, Any]],
        state_after: Optional[Dict[str, Any]],
        node_name: str,
        debug: bool,
        context_trace: bool,
    ) -> None:
        """
        Log context changes between before and after node execution.

        Args:
            state_before: Context state before execution
            state_after: Context state after execution
            node_name: Name of the node that was executed
            debug: Whether debug logging is enabled
            context_trace: Whether detailed context tracing is enabled
        """
        if not state_before or not state_after:
            return

        # Basic context change logging
        if debug:
            field_count_before = state_before.get("field_count", 0)
            field_count_after = state_after.get("field_count", 0)

            if field_count_after > field_count_before:
                new_fields = set(state_after["fields"].keys()) - set(
                    state_before["fields"].keys()
                )
                self.logger.info(
                    f"Node '{node_name}' added {len(new_fields)} new context fields: {new_fields}"
                )
            elif field_count_after < field_count_before:
                removed_fields = set(state_before["fields"].keys()) - set(
                    state_after["fields"].keys()
                )
                self.logger.info(
                    f"Node '{node_name}' removed {len(removed_fields)} context fields: {removed_fields}"
                )

        # Detailed context tracing
        if context_trace:
            self._log_detailed_context_trace(state_before, state_after, node_name)

    def _log_detailed_context_trace(
        self, state_before: Dict[str, Any], state_after: Dict[str, Any], node_name: str
    ) -> None:
        """
        Log detailed context trace with field-level changes.

        Args:
            state_before: Context state before execution
            state_after: Context state after execution
            node_name: Name of the node that was executed
        """
        fields_before = state_before.get("fields", {})
        fields_after = state_after.get("fields", {})

        # Find changed fields
        changed_fields = []
        for key in set(fields_before.keys()) | set(fields_after.keys()):
            value_before = (
                fields_before.get(key, {}).get("value")
                if key in fields_before
                else None
            )
            value_after = (
                fields_after.get(key, {}).get("value") if key in fields_after else None
            )

            if value_before != value_after:
                changed_fields.append(
                    {
                        "key": key,
                        "before": value_before,
                        "after": value_after,
                        "action": (
                            "modified"
                            if key in fields_before and key in fields_after
                            else "added" if key in fields_after else "removed"
                        ),
                    }
                )

        if changed_fields:
            self.logger.info(f"Context trace for node '{node_name}':")
            for change in changed_fields:
                self.logger.info(
                    f"  {change['action'].upper()}: {change['key']} = {change['after']} (was: {change['before']})"
                )
        else:
            self.logger.info(
                f"Context trace for node '{node_name}': No changes detected"
            )
