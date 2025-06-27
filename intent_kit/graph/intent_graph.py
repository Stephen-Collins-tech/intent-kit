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
from intent_kit.graph.aggregation import aggregate_results, create_error_dict, create_no_intent_error, create_no_taxonomy_error
from intent_kit.exceptions import NodeExecutionError, NodeInputValidationError, NodeOutputValidationError
from intent_kit.taxonomy import Taxonomy
import inspect


class IntentGraph:
    """
    The root-level dispatcher for user input.

    Each node is a high-level intent taxonomy (tree), and the graph enables:
    - Intent splitting: Decompose multi-intent user inputs into sub-intents
    - Flexible routing: Dispatch to one or more taxonomy trees
    - Multi-intent orchestration: Support for parallel or sequential execution
    - Context sharing: Pass context through all execution paths
    """

    def __init__(self, splitter: SplitterFunction = rule_splitter):
        """
        Initialize the IntentGraph with an empty taxonomy registry.

        Args:
            splitter: Function to use for splitting intents (default: rule_splitter)
        """
        self.taxonomies: dict[str, Taxonomy] = {}
        self.splitter = splitter
        self.logger = Logger(__name__)

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

    def route(self, user_input: str, context: Optional[IntentContext] = None, debug: bool = False, **splitter_kwargs) -> Dict[str, Any]:
        """
        Route user input through the graph with optional context support.

        Args:
            user_input: The input string to process
            context: Optional context object for state sharing
            debug: Whether to print debug information
            **splitter_kwargs: Additional arguments to pass to the splitter

        Returns:
            Dict containing results and errors from all matched taxonomies
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
            return {
                "results": [],
                "errors": [create_error_dict(
                    "splitter",
                    f"Splitter failed: {str(e)}",
                    type(e).__name__
                )]
            }

        if debug:
            self.logger.info(f"Intent splits: {intent_splits}")

        # If no intents were found, return error
        if not intent_splits:
            if debug:
                self.logger.warning("No recognizable intents found")
            return create_no_intent_error(self.list_taxonomies())

        # Route each intent to its taxonomy
        results = []
        errors = []

        for intent_split in intent_splits:
            taxonomy_name = intent_split["taxonomy"]
            split_text = intent_split["text"]

            if debug:
                self.logger.info(
                    f"Routing '{split_text}' to taxonomy '{taxonomy_name}'")

            # Check if taxonomy exists
            if taxonomy_name not in self.taxonomies:
                error = create_error_dict(
                    taxonomy_name,
                    f"Taxonomy '{taxonomy_name}' not found",
                    "TaxonomyNotFound"
                )
                errors.append(error)
                if debug:
                    self.logger.error(f"Taxonomy '{taxonomy_name}' not found")
                continue

            # Route to taxonomy with context support
            try:
                taxonomy = self.taxonomies[taxonomy_name]

                # Check if taxonomy route accepts context parameter
                if hasattr(taxonomy.route, '__code__'):
                    route_params = taxonomy.route.__code__.co_varnames
                    if 'context' in route_params:
                        result = taxonomy.route(
                            split_text, context=context, debug=debug)
                    else:
                        result = taxonomy.route(split_text, debug=debug)
                else:
                    # Try with context first, fall back to without
                    try:
                        result = taxonomy.route(
                            split_text, context=context, debug=debug)
                    except TypeError:
                        result = taxonomy.route(split_text, debug=debug)

                if debug:
                    self.logger.info(
                        f"Taxonomy '{taxonomy_name}' result: {result}")

                # Check if the result contains an error
                if result and isinstance(result, dict) and result.get('error'):
                    # Extract error information and add to context
                    error_message = result['error']
                    error_type = NodeExecutionError.__name__
                    node_name = result.get('intent', 'unknown')
                    params = result.get('params')

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

                    # Create error dict and add to errors list
                    error = create_error_dict(
                        taxonomy_name,
                        f"Node '{node_name}' failed: {error_message}",
                        error_type
                    )
                    errors.append(error)

                    if debug:
                        self.logger.error(
                            f"Node '{node_name}' in taxonomy '{taxonomy_name}' failed: {error_message}")
                else:
                    # No error, add to results
                    results.append(result)

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

                error = create_error_dict(
                    taxonomy_name,
                    f"Node '{node_name}' validation failed: {error_message}",
                    error_type
                )
                errors.append(error)
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

                error = create_error_dict(
                    taxonomy_name,
                    f"Node '{node_name}' execution failed: {error_message}",
                    error_type
                )
                errors.append(error)
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

                error = create_error_dict(
                    taxonomy_name,
                    error_message,
                    error_type
                )
                errors.append(error)
                if debug:
                    self.logger.error(
                        f"Taxonomy '{taxonomy_name}' failed: {e}")

        # Aggregate results
        aggregated = aggregate_results(results, errors)

        if debug:
            self.logger.info(f"Final aggregated result: {aggregated}")

        return aggregated
