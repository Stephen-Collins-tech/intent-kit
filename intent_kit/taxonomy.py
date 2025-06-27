from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from intent_kit.context import IntentContext
from intent_kit.engine import execute_taxonomy
from intent_kit.tree import TaxonomyNode


class Taxonomy(ABC):
    """
    Abstract base class for intent taxonomies.

    All taxonomies must inherit from this class and implement the route method.
    This ensures a consistent interface for the IntentGraph to work with.
    """

    @abstractmethod
    def route(self, user_input: str, context: Optional[IntentContext] = None, debug: bool = False) -> Dict[str, Any]:
        """
        Route user input through the taxonomy.

        Args:
            user_input: The input string to process
            context: Optional context object for state sharing
            debug: Whether to print debug information

        Returns:
            Dict containing:
                - intent: Name of the matched intent (or None if no match)
                - node_name: Name of the matched node (or None if no match)
                - params: Extracted parameters (or None if no match)
                - output: Result of handler execution (or None if no match)
                - error: Error message if any (or None if successful)
        """
        pass


class TreeTaxonomy(Taxonomy):
    """
    Concrete implementation of Taxonomy that wraps tree-based taxonomies.

    This class provides a bridge between the old tree-based taxonomy system
    and the new abstract Taxonomy interface.
    """

    def __init__(self, root_node: TaxonomyNode):
        """
        Initialize the TreeTaxonomy with a root node.

        Args:
            root_node: The root node of the taxonomy tree
        """
        self.root_node = root_node

    def route(self, user_input: str, context: Optional[IntentContext] = None, debug: bool = False) -> Dict[str, Any]:
        """
        Route user input through the taxonomy tree.

        Args:
            user_input: The input string to process
            context: Optional context object for state sharing
            debug: Whether to print debug information

        Returns:
            Dict containing the routing result
        """
        return execute_taxonomy(
            user_input=user_input,
            node=self.root_node,
            context=context,
            debug=debug
        )

# Example taxonomy for testing
