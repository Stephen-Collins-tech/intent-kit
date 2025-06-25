"""
IntentGraph - The root-level dispatcher for user input.

This module provides the main IntentGraph class that handles intent splitting,
taxonomy routing, and result aggregation.
"""

from typing import Dict, Any, Optional, Callable
from intent_kit.utils.logger import Logger
from intent_kit.graph.splitters import rule_splitter
from intent_kit.graph.splitters.splitter_types import SplitterFunction
from intent_kit.graph.aggregation import aggregate_results, create_error_dict, create_no_intent_error, create_no_taxonomy_error


class IntentGraph:
    """
    The root-level dispatcher for user input.

    Each node is a high-level intent taxonomy (tree), and the graph enables:
    - Intent splitting: Decompose multi-intent user inputs into sub-intents
    - Flexible routing: Dispatch to one or more taxonomy trees
    - Multi-intent orchestration: Support for parallel or sequential execution
    """

    def __init__(self, splitter: SplitterFunction = rule_splitter):
        """
        Initialize the IntentGraph with an empty taxonomy registry.

        Args:
            splitter: Function to use for splitting intents (default: rule_splitter)
        """
        self.taxonomies: Dict[str, Any] = {}
        self.splitter = splitter
        self.logger = Logger(__name__)

    def register_taxonomy(self, name: str, taxonomy: Any) -> None:
        """
        Register a taxonomy in the graph.

        Args:
            name: The name of the taxonomy
            taxonomy: The taxonomy instance (must support .route() method)
        """
        if not hasattr(taxonomy, 'route'):
            raise ValueError(
                f"Taxonomy '{name}' must support a .route() method")

        self.taxonomies[name] = taxonomy
        self.logger.info(f"Registered taxonomy: {name}")

    def remove_taxonomy(self, name: str) -> bool:
        """
        Remove a taxonomy from the graph.

        Args:
            name: The name of the taxonomy to remove

        Returns:
            True if taxonomy was removed, False if it didn't exist
        """
        if name in self.taxonomies:
            del self.taxonomies[name]
            self.logger.info(f"Removed taxonomy: {name}")
            return True
        else:
            self.logger.warning(f"Taxonomy '{name}' not found for removal")
            return False

    def list_taxonomies(self) -> list[str]:
        """
        Get a list of registered taxonomy names.

        Returns:
            List of registered taxonomy names
        """
        return list(self.taxonomies.keys())

    def route(self, user_input: str, debug: bool = False, **splitter_kwargs) -> Dict[str, Any]:
        """
        Route user input to appropriate taxonomies.

        Args:
            user_input: The user's input string
            debug: Whether to enable debug logging
            **splitter_kwargs: Additional arguments to pass to the splitter function

        Returns:
            Dict with format: {"results": [...], "errors": [...]}
        """
        if debug:
            self.logger.info(f"Routing input: '{user_input}'")
            self.logger.info(f"Available taxonomies: {self.list_taxonomies()}")

        # Check if we have any taxonomies registered
        if not self.taxonomies:
            if debug:
                self.logger.warning("No taxonomies registered")
            return create_no_taxonomy_error([])

        # Split the input into intents
        intent_splits = self.splitter(
            user_input, self.taxonomies, debug, **splitter_kwargs)

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

            # Route to taxonomy
            try:
                taxonomy = self.taxonomies[taxonomy_name]
                result = taxonomy.route(split_text, debug=debug)

                if debug:
                    self.logger.info(
                        f"Taxonomy '{taxonomy_name}' result: {result}")

                results.append(result)

            except Exception as e:
                error = create_error_dict(
                    taxonomy_name,
                    str(e),
                    type(e).__name__
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
