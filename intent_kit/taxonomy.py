from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from intent_kit.context import IntentContext
from intent_kit.engine import ExecutionResult


class Taxonomy(ABC):
    """
    Abstract base class for intent taxonomies.

    All taxonomies must inherit from this class and implement the route method.
    This ensures a consistent interface for the IntentGraph to work with.
    """

    @abstractmethod
    def route(self, user_input: str, context: Optional[IntentContext] = None, debug: bool = False) -> ExecutionResult:
        """
        Route user input through the taxonomy.

        Args:
            user_input: The input string to process
            context: Optional context object for state sharing
            debug: Whether to print debug information

        Returns:
            ExecutionResult containing:
                - success: Whether the route was successful
                - params: Extracted parameters (or None if no match)
                - children_results: List of child results (or empty list if no children)
                - node_name: Name of the matched node (or None if no match)
                - node_path: Path to the matched node (or empty list if no match)
                - node_type: Type of the matched node (or None if no match)
                - input: The input string
                - output: Result of handler execution (or None if no match)
                - error: Error message if any (or None if successful)
        """
        pass
