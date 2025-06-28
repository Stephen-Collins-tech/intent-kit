"""
IntentGraph - The root-level dispatcher for user input.

This module provides the main IntentGraph class that handles intent splitting,
taxonomy routing, and result aggregation.
"""

from typing import Dict, Any, Optional, Callable
from intent_kit.utils.logger import Logger
from intent_kit.context import IntentContext
from intent_kit.graph.splitters import rule_splitter
from intent_kit.graph.splitters.splitter_types import SplitterFunction
# from intent_kit.graph.aggregation import aggregate_results, create_error_dict, create_no_intent_error, create_no_taxonomy_error
from intent_kit.engine import ExecutionResult
from intent_kit.node import ExecutionError
from intent_kit.exceptions import NodeExecutionError, NodeInputValidationError, NodeOutputValidationError
from intent_kit.taxonomy import Taxonomy
import os

# Add imports for visualization
try:
    import networkx as nx
    from pyvis.network import Network
    VIZ_AVAILABLE = True
except ImportError as e:
    nx = None
    Network = None
    VIZ_AVAILABLE = False


class IntentGraph:
    """
    The root-level dispatcher for user input.

    Each node is a high-level intent taxonomy (tree), and the graph enables:
    - Intent splitting: Decompose multi-intent user inputs into sub-intents
    - Flexible routing: Dispatch to one or more taxonomy trees
    - Multi-intent orchestration: Support for parallel or sequential execution
    - Context sharing: Pass context through all execution paths
    """

    def __init__(self, splitter: SplitterFunction = rule_splitter, visualize: bool = False):
        """
        Initialize the IntentGraph with an empty taxonomy registry.

        Args:
            splitter: Function to use for splitting intents (default: rule_splitter)
            visualize: If True, render the final output (error or success) to an interactive graph HTML file
        """
        self.taxonomies: dict[str, Taxonomy] = {}
        self.splitter = splitter
        self.logger = Logger(__name__)
        self.visualize = visualize

    def register_taxonomy(self, name: str, taxonomy: Taxonomy) -> None:
        """
        Register a taxonomy in the graph.

        Args:
            name: The name of the taxonomy
            taxonomy: The taxonomy instance (must inherit from Taxonomy)
        """
        if not isinstance(taxonomy, Taxonomy):
            raise ValueError(
                f"Taxonomy '{name}' must inherit from Taxonomy base class")

        self.taxonomies[name] = taxonomy
        self.logger.info(f"Registered taxonomy: {name}")

    def remove_taxonomy(self, name: str) -> None:
        """
        Remove a taxonomy from the graph.

        Args:
            name: The name of the taxonomy to remove
        """
        if name in self.taxonomies:
            del self.taxonomies[name]
            self.logger.info(f"Removed taxonomy: {name}")
        else:
            self.logger.warning(f"Taxonomy '{name}' not found for removal")

    def list_taxonomies(self) -> list:
        """
        List all registered taxonomies.

        Returns:
            List of taxonomy names
        """
        return list(self.taxonomies.keys())

    def _call_splitter(self, user_input: str, debug: bool, context: Optional[IntentContext] = None, **splitter_kwargs) -> list:
        """
        Call the splitter function with appropriate parameters.

        Args:
            user_input: The input string to process
            debug: Whether to enable debug logging
            context: Optional context object (not passed to splitter)
            **splitter_kwargs: Additional arguments for the splitter

        Returns:
            List of intent splits
        """
        # Call splitter (context-aware splitters can access context via closure or other means)
        return self.splitter(user_input, self.taxonomies, debug, **splitter_kwargs)

    def route(self, user_input: str, context: Optional[IntentContext] = None, debug: bool = False, **splitter_kwargs) -> ExecutionResult:
        """
        Route user input through the graph with optional context support.

        Args:
            user_input: The input string to process
            context: Optional context object for state sharing
            debug: Whether to print debug information
            **splitter_kwargs: Additional arguments to pass to the splitter

        Returns:
            ExecutionResult containing aggregated results and errors from all matched taxonomies
        """
        if debug:
            self.logger.info(f"Processing input: {user_input}")
            if context:
                self.logger.info(f"Using context: {context}")

        # Split the input into intents
        try:
            intent_splits = self._call_splitter(
                user_input=user_input,
                debug=debug,
                **splitter_kwargs
            )

        except Exception as e:
            self.logger.error(f"Splitter error: {e}")
            return ExecutionResult(
                success=False,
                params=None,
                children_results=[],
                node_name="splitter",
                node_path=[],
                node_type="splitter",
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="SplitterError",
                    message=str(e),
                    node_name="splitter",
                    node_path=[]
                )
            )

        if debug:
            self.logger.info(f"Intent splits: {intent_splits}")

        # If no intents were found, return error
        if not intent_splits:
            if debug:
                self.logger.warning("No recognizable intents found")
            return ExecutionResult(
                success=False,
                params=None,
                children_results=[],
                node_name="no_intent",
                node_path=[],
                node_type="no_intent",
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="NoIntentFound",
                    message="No recognizable intents found",
                    node_name="no_intent",
                    node_path=[]
                )
            )

        # Route each intent to its taxonomy
        children_results = []
        all_errors = []
        all_outputs = []
        all_params = []

        for intent_split in intent_splits:
            taxonomy_name = intent_split["taxonomy"]
            split_text = intent_split["text"]

            if debug:
                self.logger.info(
                    f"Routing '{split_text}' to taxonomy '{taxonomy_name}'")

            # Check if taxonomy exists
            if taxonomy_name not in self.taxonomies:
                error_result = ExecutionResult(
                    success=False,
                    params=None,
                    children_results=[],
                    node_name="taxonomy_not_found",
                    node_path=[],
                    node_type="error",
                    input=split_text,
                    output=None,
                    error=ExecutionError(
                        error_type="TaxonomyNotFound",
                        message=f"Taxonomy '{taxonomy_name}' not found",
                        node_name="taxonomy_not_found",
                        node_path=[]
                    )
                )
                children_results.append(error_result)
                all_errors.append(f"Taxonomy '{taxonomy_name}' not found")
                if debug:
                    self.logger.error(f"Taxonomy '{taxonomy_name}' not found")
                continue

            # Route to taxonomy with context support
            try:
                taxonomy = self.taxonomies[taxonomy_name]

                result = taxonomy.route(
                    split_text, context=context, debug=debug)

                if debug:
                    self.logger.info(
                        f"Taxonomy '{taxonomy_name}' result: {result}")

                # Add the result to children_results
                children_results.append(result)

                # Collect outputs and params for aggregation
                if result.success and result.output is not None:
                    all_outputs.append(result.output)
                if result.params is not None:
                    all_params.append(result.params)

                # Check if the result contains an error
                if result.error:
                    all_errors.append(
                        f"Taxonomy '{taxonomy_name}': {result.error.message}")

            except (NodeInputValidationError, NodeOutputValidationError) as e:
                # Handle validation errors specifically
                error_message = str(e)
                error_type = type(e).__name__
                node_name = e.node_name
                node_id = e.node_id
                node_path = e.node_path

                # Add error to context if available
                if context:
                    context.add_error(
                        node_name=node_name,
                        taxonomy_name=taxonomy_name,
                        user_input=split_text,
                        error_message=error_message,
                        error_type=error_type,
                        params=None
                    )

                error_result = ExecutionResult(
                    success=False,
                    params=None,
                    children_results=[],
                    node_name=node_name,
                    node_path=node_path,
                    node_type="error",
                    input=split_text,
                    output=None,
                    error=ExecutionError(
                        error_type=error_type,
                        message=f"Node '{node_name}' validation failed: {error_message}",
                        node_name=node_name,
                        node_path=node_path,
                        node_id=node_id,
                        taxonomy_name=taxonomy_name
                    )
                )
                children_results.append(error_result)
                all_errors.append(
                    f"Node '{node_name}' validation failed: {error_message}")

                if debug:
                    self.logger.error(
                        f"Node '{node_name}' (ID: {node_id}, Path: {'.'.join(node_path)}) in taxonomy '{taxonomy_name}' validation failed: {error_message}")

            except NodeExecutionError as e:
                # Handle execution errors specifically
                error_message = str(e)
                error_type = type(e).__name__
                node_name = e.node_name
                node_id = e.node_id
                node_path = e.node_path
                params = e.params

                # Add error to context if available
                if context:
                    context.add_error(
                        node_name=node_name,
                        taxonomy_name=taxonomy_name,
                        user_input=split_text,
                        error_message=error_message,
                        error_type=error_type,
                        params=params
                    )

                error_result = ExecutionResult(
                    success=False,
                    params=None,
                    children_results=[],
                    node_name=node_name,
                    node_path=node_path,
                    node_type="error",
                    input=split_text,
                    output=None,
                    error=ExecutionError(
                        error_type=error_type,
                        message=f"Node '{node_name}' execution failed: {error_message}",
                        node_name=node_name,
                        node_path=node_path,
                        node_id=node_id,
                        taxonomy_name=taxonomy_name,
                        params=params
                    )
                )
                children_results.append(error_result)
                all_errors.append(
                    f"Node '{node_name}' execution failed: {error_message}")

                if debug:
                    self.logger.error(
                        f"Node '{node_name}' (ID: {node_id}, Path: {'.'.join(node_path)}) in taxonomy '{taxonomy_name}' execution failed: {error_message}")

            except Exception as e:
                error_message = str(e)
                error_type = type(e).__name__

                # Add error to context if available
                if context:
                    context.add_error(
                        node_name="unknown",
                        taxonomy_name=taxonomy_name,
                        user_input=split_text,
                        error_message=error_message,
                        error_type=error_type,
                        params=None
                    )

                error_result = ExecutionResult(
                    success=False,
                    params=None,
                    children_results=[],
                    node_name="unknown",
                    node_path=[],
                    node_type="error",
                    input=split_text,
                    output=None,
                    error=ExecutionError(
                        error_type=error_type,
                        message=error_message,
                        node_name="unknown",
                        node_path=[],
                        taxonomy_name=taxonomy_name
                    )
                )
                children_results.append(error_result)
                all_errors.append(
                    f"Taxonomy '{taxonomy_name}' failed: {error_message}")

                if debug:
                    self.logger.error(
                        f"Taxonomy '{taxonomy_name}' failed: {e}")

        # Determine overall success and create aggregated result
        overall_success = len(all_errors) == 0 and len(children_results) > 0

        # Aggregate outputs and params
        aggregated_output = all_outputs if len(all_outputs) > 1 else (
            all_outputs[0] if all_outputs else None)
        aggregated_params = all_params if len(all_params) > 1 else (
            all_params[0] if all_params else None)

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
                node_path=[]
            )

        # Create visualization if requested
        visualization_html = None
        if self.visualize:
            try:
                html_path = self._render_execution_graph(
                    children_results, user_input)
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
                    "visualization_html": visualization_html
                }

        if debug:
            self.logger.info(f"Final aggregated result: {overall_success}")

        return ExecutionResult(
            success=overall_success,
            params=aggregated_params,
            children_results=children_results,
            node_name="intent_graph",
            node_path=[],
            node_type="intent_graph",
            input=user_input,
            output=aggregated_output,
            error=aggregated_error
        )

    def _render_execution_graph(self, children_results: list[ExecutionResult], user_input: str) -> str:
        """
        Render the execution path as an interactive HTML graph and return the file path.
        """
        if not VIZ_AVAILABLE:
            raise ImportError(
                "networkx and pyvis are required for visualization. Please install with: uv pip install 'intent-kit[viz]'")

        try:
            # Import here to ensure it's available
            from pyvis.network import Network

            # Build the graph from the execution path
            net = Network(height="600px", width="100%",
                          directed=True, notebook=False)
            net.barnes_hut()
            execution_paths = []

            # Extract execution paths from all children results
            for result in children_results:
                # Add the current result to the path
                execution_paths.append({
                    "node_name": result.node_name,
                    "node_type": result.node_type,
                    "success": result.success,
                    "input": result.input,
                    "output": result.output,
                    "error": result.error,
                    "params": result.params
                })

                # Add child results recursively
                for child_result in result.children_results:
                    child_paths = self._extract_execution_paths(child_result)
                    execution_paths.extend(child_paths)

            if not execution_paths:
                # fallback to errors
                execution_paths = []
                for result in children_results:
                    if result.error:
                        execution_paths.append({
                            "node_name": result.node_name,
                            "node_type": "error",
                            "error": result.error
                        })

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
                if node['node_type'] == 'error':
                    color = "#ffcccc"  # red
                elif node['node_type'] == 'classifier':
                    color = "#99ccff"  # blue
                elif node['node_type'] == 'intent':
                    color = "#ccffcc"  # green
                else:
                    color = "#ccccff"  # fallback
                net.add_node(node_id, label=label, color=color)
                if last_node_id is not None:
                    net.add_edge(last_node_id, node_id)
                last_node_id = node_id
            if not execution_paths:
                net.add_node("no_path", label="No execution path",
                             color="#cccccc")

            # Save to HTML file
            html_dir = os.path.join(os.getcwd(), "intentkit_graphs")
            os.makedirs(html_dir, exist_ok=True)
            html_path = os.path.join(
                html_dir, f"intent_graph_{abs(hash(user_input)) % 100000}.html")

            # Generate HTML and write to file manually
            html_content = net.generate_html()
            with open(html_path, 'w', encoding='utf-8') as f:
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
        paths.append({
            "node_name": result.node_name,
            "node_type": result.node_type,
            "success": result.success,
            "input": result.input,
            "output": result.output,
            "error": result.error,
            "params": result.params
        })

        # Recursively add children
        for child_result in result.children_results:
            child_paths = self._extract_execution_paths(child_result)
            paths.extend(child_paths)

        return paths
