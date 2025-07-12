"""
IntentGraph - The root-level dispatcher for user input.

This module provides the main IntentGraph class that handles intent splitting,
routing to root nodes, and result aggregation.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from intent_kit.utils.logger import Logger
from intent_kit.context import IntentContext
from intent_kit.types import SplitterFunction, IntentChunk
from intent_kit.graph.validation import (
    validate_splitter_routing,
    validate_graph_structure,
    validate_node_types,
    GraphValidationError,
)

# from intent_kit.graph.aggregation import aggregate_results, create_error_dict, create_no_intent_error, create_no_tree_error
from intent_kit.node import ExecutionResult
from intent_kit.node import ExecutionError
from intent_kit.node.enums import NodeType
from intent_kit.node import TreeNode
import os
from intent_kit.node.classifiers import classify_intent_chunk
from intent_kit.types import IntentAction

# Add imports for visualization
try:
    import networkx as nx
    from pyvis.network import Network  # type: ignore

    VIZ_AVAILABLE = True
except ImportError:
    nx = None  # type: ignore
    Network = None  # type: ignore
    VIZ_AVAILABLE = False


class IntentGraph:
    """
    The root-level dispatcher for user input.

    The graph contains root nodes that can handle different types of intents.
    Input splitting happens in isolation and routes to appropriate root nodes.
    Trees emerge naturally from the parent-child relationships between nodes.
    """

    def __init__(
        self,
        root_nodes: Optional[List[TreeNode]] = None,
        splitter: Optional[SplitterFunction] = None,
        visualize: bool = False,
        llm_config: Optional[dict] = None,
        debug_context: bool = False,
        context_trace: bool = False,
    ):
        """
        Initialize the IntentGraph with root nodes.

        Args:
            root_nodes: List of root nodes that can handle intents
            splitter: Function to use for splitting intents (default: pass-through splitter)
            visualize: If True, render the final output to an interactive graph HTML file
            llm_config: LLM configuration for chunk classification (optional)
            debug_context: If True, enable context debugging and state tracking
            context_trace: If True, enable detailed context tracing with timestamps
        """
        self.root_nodes: List[TreeNode] = root_nodes or []

        # Default to pass-through splitter if none provided
        if splitter is None:

            def pass_through_splitter(
                user_input: str, debug: bool = False
            ) -> List[IntentChunk]:
                """Pass-through splitter that doesn't split the input."""
                return [user_input]

            self.splitter: SplitterFunction = pass_through_splitter
        else:
            self.splitter = splitter

        self.logger = Logger(__name__)
        self.visualize = visualize
        self.llm_config = llm_config
        self.debug_context = debug_context
        self.context_trace = context_trace

    def add_root_node(self, root_node: TreeNode, validate: bool = True) -> None:
        """
        Add a root node to the graph.

        Args:
            root_node: The root node to add
            validate: Whether to validate the graph after adding the node
        """
        if not isinstance(root_node, TreeNode):
            raise ValueError("Root node must be a TreeNode")

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

        # Validate splitter routing
        if validate_routing:
            validate_splitter_routing(all_nodes)

        # Get comprehensive validation stats
        stats = validate_graph_structure(all_nodes)

        self.logger.info("Graph validation completed successfully")
        return stats

    def validate_splitter_routing(self) -> None:
        """
        Validate that all splitter nodes only route to classifier nodes.

        Raises:
            GraphValidationError: If any splitter node routes to a non-classifier node
        """
        all_nodes = []
        for root_node in self.root_nodes:
            all_nodes.extend(self._collect_all_nodes([root_node]))

        validate_splitter_routing(all_nodes)

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

    def _call_splitter(
        self,
        user_input: str,
        debug: bool,
        context: Optional[IntentContext] = None,
        **splitter_kwargs,
    ) -> list:
        """
        Call the splitter function with appropriate parameters.

        Args:
            user_input: The input string to process
            debug: Whether to enable debug logging
            context: Optional context object to pass to splitter
            **splitter_kwargs: Additional arguments for the splitter

        Returns:
            List of intent chunks
        """
        # Pass context to splitter if it accepts it
        try:
            result = self.splitter(
                user_input, debug, context=context, **splitter_kwargs
            )
        except TypeError:
            # Fallback for splitters that don't accept context
            result = self.splitter(user_input, debug, **splitter_kwargs)
        return list(result)  # Convert Sequence to list

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

        # Classify the chunk to determine action
        classification = classify_intent_chunk(chunk, self.llm_config)
        action = classification.get("action")

        # If action is reject, return None
        if action == IntentAction.REJECT:
            if debug:
                self.logger.info(f"Chunk '{chunk}' rejected by classifier")
            return None

        # Simple routing logic: try to find a root node that matches the chunk
        # This could be enhanced with more sophisticated matching
        chunk_lower = chunk.lower()

        for node in self.root_nodes:
            # Check if node name appears in the chunk
            if node.name.lower() in chunk_lower:
                if debug:
                    self.logger.info(
                        f"Routed chunk '{chunk}' to root node '{node.name}' by name match"
                    )
                return node

            # Check for keyword matches (could be enhanced)
            keywords = getattr(node, "keywords", [])
            for keyword in keywords:
                if keyword.lower() in chunk_lower:
                    if debug:
                        self.logger.info(
                            f"Routed chunk '{chunk}' to root node '{node.name}' by keyword '{keyword}'"
                        )
                    return node

        # If no specific match, return the first root node as fallback
        if debug:
            self.logger.info(
                f"No specific match for chunk '{chunk}', using first root node '{self.root_nodes[0].name}' as fallback"
            )
        return self.root_nodes[0] if self.root_nodes else None

    def route(
        self,
        user_input: str,
        context: Optional[IntentContext] = None,
        debug: bool = False,
        debug_context: Optional[bool] = None,
        context_trace: Optional[bool] = None,
        **splitter_kwargs,
    ) -> ExecutionResult:
        """
        Route user input through the graph with optional context support.

        Args:
            user_input: The input string to process
            context: Optional context object for state sharing
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

        # Split the input into chunks
        try:
            intent_chunks = self._call_splitter(
                user_input=user_input, debug=debug, **splitter_kwargs
            )

        except Exception as e:
            self.logger.error(f"Splitter error: {e}")
            return ExecutionResult(
                success=False,
                params=None,
                children_results=[],
                node_name="splitter",
                node_path=[],
                node_type=NodeType.SPLITTER,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="SplitterError",
                    message=str(e),
                    node_name="splitter",
                    node_path=[],
                ),
            )

        if debug:
            self.logger.info(f"Intent chunks: {intent_chunks}")

        # If no chunks were found, return error
        if not intent_chunks:
            if debug:
                self.logger.warning("No intent chunks found")
            return ExecutionResult(
                success=False,
                params=None,
                children_results=[],
                node_name="no_intent",
                node_path=[],
                node_type=NodeType.UNHANDLED_CHUNK,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="NoIntentFound",
                    message="No intent chunks found",
                    node_name="unhandled_chunk",
                    node_path=[],
                ),
            )

        # Route each chunk to an appropriate root node
        children_results = []
        all_errors = []
        all_outputs = []
        all_params = []

        # Use a queue to process chunks, with recursion limit
        chunks_to_process = list(intent_chunks)  # Copy the list
        processed_chunks: set = set()  # Track processed chunks to avoid infinite loops
        max_recursion_depth = 10  # Prevent infinite recursion

        while chunks_to_process and len(processed_chunks) < max_recursion_depth:
            chunk = chunks_to_process.pop(0)

            # Create a unique identifier for this chunk to avoid infinite loops
            # Use a robust hashing strategy that works for both hashable (e.g. str)
            # and unhashable (e.g. dict) chunk objects.
            # Converting to `repr` preserves enough uniqueness while ensuring the
            # object is hashable.
            chunk_id = hash(repr(chunk))
            if chunk_id in processed_chunks:
                continue  # Skip if we've already processed this exact chunk
            processed_chunks.add(chunk_id)

            # Handle both string and dict chunks
            if isinstance(chunk, str):
                chunk_text = chunk
            elif isinstance(chunk, dict) and "text" in chunk:
                chunk_text = chunk["text"]
            else:
                chunk_text = str(chunk)

            if debug:
                self.logger.info(f"Classifying chunk: '{chunk_text}'")
            classification = classify_intent_chunk(chunk, self.llm_config)
            action = classification.get("action")

            if action == IntentAction.HANDLE:
                # Route to root node as before
                root_node = self._route_chunk_to_root_node(chunk_text, debug)
                if root_node is None:
                    error_result = ExecutionResult(
                        success=False,
                        params=None,
                        children_results=[],
                        node_name="no_root_node",
                        node_path=[],
                        node_type=NodeType.UNKNOWN,
                        input=chunk_text,
                        output=None,
                        error=ExecutionError(
                            error_type="NoRootNodeFound",
                            message=f"No root node found for chunk: '{chunk_text}'",
                            node_name="no_root_node",
                            node_path=[],
                        ),
                    )
                    children_results.append(error_result)
                    all_errors.append(f"No root node found for chunk: '{chunk_text}'")
                    if debug:
                        self.logger.error(
                            f"No root node found for chunk: '{chunk_text}'"
                        )
                    continue
                try:
                    # Context debugging: capture state before execution
                    context_state_before = None
                    if debug_context_enabled and context:
                        context_state_before = self._capture_context_state(
                            context, f"before_{root_node.name}"
                        )

                    result = root_node.execute(chunk_text, context=context)

                    if result is None:
                        error_result = ExecutionResult(
                            success=False,
                            params=None,
                            children_results=[],
                            node_name=root_node.name,
                            node_path=[],
                            node_type=root_node.node_type,
                            input=chunk_text,
                            output=None,
                            error=ExecutionError(
                                error_type="NodeExecutionReturnedNone",
                                message=f"Node '{root_node.name}' execute() returned None instead of ExecutionResult.",
                                node_name=root_node.name,
                                node_path=[],
                            ),
                        )
                        children_results.append(error_result)
                        all_errors.append(
                            f"Node '{root_node.name}' execute() returned None."
                        )
                        if debug:
                            self.logger.error(
                                f"Node '{root_node.name}' execute() returned None instead of ExecutionResult."
                            )
                        continue

                    # Context debugging: capture state after execution
                    if debug_context_enabled and context:
                        context_state_after = self._capture_context_state(
                            context, f"after_{root_node.name}"
                        )
                        self._log_context_changes(
                            context_state_before,
                            context_state_after,
                            root_node.name,
                            debug,
                            context_trace_enabled,
                        )

                    if debug:
                        self.logger.info(
                            f"Root node '{root_node.name}' result: {result}"
                        )
                    children_results.append(result)
                    if result.success and result.output is not None:
                        all_outputs.append(result.output)
                    if result.params is not None:
                        all_params.append(result.params)
                    if result.error:
                        all_errors.append(
                            f"Root node '{root_node.name}': {result.error.message}"
                        )
                except Exception as e:
                    error_message = str(e)
                    error_type = type(e).__name__
                    error_result = ExecutionResult(
                        success=False,
                        params=None,
                        children_results=[],
                        node_name="unknown",
                        node_path=[],
                        node_type=NodeType.UNKNOWN,
                        input=chunk_text,
                        output=None,
                        error=ExecutionError(
                            error_type=error_type,
                            message=error_message,
                            node_name="unknown",
                            node_path=[],
                        ),
                    )
                    children_results.append(error_result)
                    all_errors.append(
                        f"Root node '{root_node.name}' failed: {error_message}"
                    )
                    if debug:
                        self.logger.error(f"Root node '{root_node.name}' failed: {e}")
            elif action == IntentAction.SPLIT:
                # Recursively split and route
                if debug:
                    self.logger.info(f"Recursively splitting chunk: '{chunk_text}'")
                sub_chunks = self._call_splitter(chunk_text, debug, **splitter_kwargs)
                # Add sub_chunks to the front of the queue for processing
                chunks_to_process = sub_chunks + chunks_to_process
            elif action == IntentAction.CLARIFY:
                # Stub: Add a result indicating clarification is needed
                error_result = ExecutionResult(
                    success=False,
                    params=None,
                    children_results=[],
                    node_name="clarify",
                    node_path=[],
                    node_type=NodeType.CLARIFY,
                    input=chunk_text,
                    output=None,
                    error=ExecutionError(
                        error_type="ClarificationNeeded",
                        message=f"Clarification needed for chunk: '{chunk_text}'",
                        node_name="clarify",
                        node_path=[],
                    ),
                )
                children_results.append(error_result)
                all_errors.append(f"Clarification needed for chunk: '{chunk_text}'")
                if debug:
                    self.logger.warning(
                        f"Clarification needed for chunk: '{chunk_text}'"
                    )
            elif action == IntentAction.REJECT:
                # Stub: Add a result indicating rejection
                error_result = ExecutionResult(
                    success=False,
                    params=None,
                    children_results=[],
                    node_name="reject",
                    node_path=[],
                    node_type=NodeType.UNKNOWN,
                    input=chunk_text,
                    output=None,
                    error=ExecutionError(
                        error_type="RejectedChunk",
                        message=f"Rejected chunk: '{chunk_text}'",
                        node_name="reject",
                        node_path=[],
                    ),
                )
                children_results.append(error_result)
                all_errors.append(f"Rejected chunk: '{chunk_text}'")
                if debug:
                    self.logger.warning(f"Rejected chunk: '{chunk_text}'")
            else:
                # Unknown action
                error_result = ExecutionResult(
                    success=False,
                    params=None,
                    children_results=[],
                    node_name="unknown_action",
                    node_path=[],
                    node_type=NodeType.UNKNOWN,
                    input=chunk_text,
                    output=None,
                    error=ExecutionError(
                        error_type="UnknownAction",
                        message=f"Unknown action for chunk: '{chunk_text}'",
                        node_name="unknown_action",
                        node_path=[],
                    ),
                )
                children_results.append(error_result)
                all_errors.append(f"Unknown action for chunk: '{chunk_text}'")
                if debug:
                    self.logger.error(f"Unknown action for chunk: '{chunk_text}'")

        # Check if we hit the recursion limit
        if len(processed_chunks) >= max_recursion_depth:
            error_result = ExecutionResult(
                success=False,
                params=None,
                children_results=[],
                node_name="recursion_limit",
                node_path=[],
                node_type=NodeType.UNKNOWN,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="RecursionLimitExceeded",
                    message=f"Recursion limit exceeded ({max_recursion_depth} chunks processed)",
                    node_name="recursion_limit",
                    node_path=[],
                ),
            )
            children_results.append(error_result)
            all_errors.append(
                f"Recursion limit exceeded ({max_recursion_depth} chunks processed)"
            )
            if debug:
                self.logger.error(
                    f"Recursion limit exceeded ({max_recursion_depth} chunks processed)"
                )

        # Determine overall success and create aggregated result
        overall_success = len(all_errors) == 0 and len(children_results) > 0

        # If there's only one successful result and no errors, return it directly
        if (
            len(children_results) == 1
            and len(all_errors) == 0
            and children_results[0].success
        ):
            result = children_results[0]
            # Add visualization if requested
            if self.visualize:
                try:
                    html_path = self._render_execution_graph(
                        children_results, user_input
                    )
                    if html_path:
                        if result.output is None:
                            result.output = {"visualization_html": html_path}
                        elif isinstance(result.output, dict):
                            result.output["visualization_html"] = html_path
                        else:
                            result.output = {
                                "output": result.output,
                                "visualization_html": html_path,
                            }
                except Exception as e:
                    self.logger.error(f"Visualization failed: {e}")
            return result

        # Aggregate outputs and params
        aggregated_output = (
            all_outputs
            if len(all_outputs) > 1
            else (all_outputs[0] if all_outputs else None)
        )
        aggregated_params = (
            all_params
            if len(all_params) > 1
            else (all_params[0] if all_params else None)
        )

        # Ensure params is a dict or None
        if aggregated_params is not None and not isinstance(aggregated_params, dict):
            aggregated_params = {"params": aggregated_params}

        # Create aggregated error if there are any errors
        aggregated_error = None
        if all_errors:
            aggregated_error = ExecutionError(
                error_type="AggregatedErrors",
                message="; ".join(all_errors),
                node_name="intent_graph",
                node_path=[],
            )

        # Create visualization if requested
        visualization_html = None
        if self.visualize:
            try:
                html_path = self._render_execution_graph(children_results, user_input)
                visualization_html = html_path
            except Exception as e:
                self.logger.error(f"Visualization failed: {e}")
                visualization_html = None

        # Add visualization to output if available
        if visualization_html:
            if aggregated_output is None:
                aggregated_output = {"visualization_html": visualization_html}
            elif isinstance(aggregated_output, dict):
                aggregated_output["visualization_html"] = visualization_html
            else:
                aggregated_output = {
                    "output": aggregated_output,
                    "visualization_html": visualization_html,
                }

        if debug:
            self.logger.info(f"Final aggregated result: {overall_success}")

        return ExecutionResult(
            success=overall_success,
            params=aggregated_params,
            children_results=children_results,
            node_name="intent_graph",
            node_path=[],
            node_type=NodeType.GRAPH,
            input=user_input,
            output=aggregated_output,
            error=aggregated_error,
        )

    def _render_execution_graph(
        self, children_results: list[ExecutionResult], user_input: str
    ) -> str:
        """
        Render the execution path as an interactive HTML graph and return the file path.
        """
        if not self.visualize:
            return ""

        if not VIZ_AVAILABLE:
            raise ImportError(
                "networkx and pyvis are required for visualization. Please install with: uv pip install 'intent-kit[viz]'"
            )

        try:
            # Import here to ensure it's available
            from pyvis.network import Network

            # Build the graph from the execution path
            net = Network(height="600px", width="100%", directed=True, notebook=False)
            net.barnes_hut()
            execution_paths = []

            # Extract execution paths from all children results
            for result in children_results:
                # Add the current result to the path
                execution_paths.append(
                    {
                        "node_name": result.node_name,
                        "node_type": result.node_type,
                        "success": result.success,
                        "input": result.input,
                        "output": result.output,
                        "error": result.error,
                        "params": result.params,
                    }
                )

                # Add child results recursively
                for child_result in result.children_results:
                    child_paths = self._extract_execution_paths(child_result)
                    execution_paths.extend(child_paths)

            if not execution_paths:
                # fallback to errors
                execution_paths = []
                for result in children_results:
                    if result.error:
                        execution_paths.append(
                            {
                                "node_name": result.node_name,
                                "node_type": "error",
                                "error": result.error,
                            }
                        )

            # Add nodes and edges
            last_node_id = None
            for idx, node in enumerate(execution_paths):
                node_id = f"{node['node_name']}_{idx}"
                label = f"{node['node_name']}\n{node['node_type']}"
                if node.get("error"):
                    label += f"\nERROR: {node['error']}"
                elif node.get("output"):
                    label += f"\nOutput: {str(node['output'])[:40]}"
                # Color coding
                if node["node_type"] == "error":
                    color = "#ffcccc"  # red
                elif node["node_type"] == "classifier":
                    color = "#99ccff"  # blue
                elif node["node_type"] == "intent":
                    color = "#ccffcc"  # green
                else:
                    color = "#ccccff"  # fallback
                net.add_node(node_id, label=label, color=color)
                if last_node_id is not None:
                    net.add_edge(last_node_id, node_id)
                last_node_id = node_id
            if not execution_paths:
                net.add_node("no_path", label="No execution path", color="#cccccc")

            # Save to HTML file
            html_dir = os.path.join(os.getcwd(), "intentkit_graphs")
            os.makedirs(html_dir, exist_ok=True)
            html_path = os.path.join(
                html_dir, f"intent_graph_{abs(hash(user_input)) % 100000}.html"
            )

            # Generate HTML and write to file manually
            html_content = net.generate_html()
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return html_path
        except Exception as e:
            self.logger.error(f"Failed to render graph: {e}")
            raise

    def _extract_execution_paths(self, result: ExecutionResult) -> list:
        """
        Recursively extract execution paths from an ExecutionResult.

        Args:
            result: The ExecutionResult to extract paths from

        Returns:
            List of execution path nodes
        """
        paths = []

        # Add current node
        paths.append(
            {
                "node_name": result.node_name,
                "node_type": result.node_type,
                "success": result.success,
                "input": result.input,
                "output": result.output,
                "error": result.error,
                "params": result.params,
                "node_id": getattr(result, "node_id", None),
            }
        )

        # Recursively add children
        for child_result in result.children_results:
            child_paths = self._extract_execution_paths(child_result)
            paths.extend(child_paths)

        return paths

    def _capture_context_state(
        self, context: IntentContext, label: str
    ) -> Dict[str, Any]:
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
