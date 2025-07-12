"""
Serialization utilities for IntentGraph.

This module provides functionality to create IntentGraph instances from JSON definitions
and function registries, enabling portable intent graph configurations.
"""

from typing import Dict, List, Optional, Callable
from intent_kit.utils.logger import Logger


class FunctionRegistry:
    """Registry for mapping function names to callable functions."""

    def __init__(self, functions: Optional[Dict[str, Callable]] = None):
        """
        Initialize the function registry.

        Args:
            functions: Dictionary mapping function names to callable functions
        """
        self.functions: Dict[str, Callable] = functions or {}
        self.logger = Logger(__name__)

    def register(self, name: str, func: Callable) -> None:
        """Register a function with the given name."""
        self.functions[name] = func
        self.logger.debug(f"Registered function '{name}'")

    def get(self, name: str) -> Optional[Callable]:
        """Get a function by name."""
        return self.functions.get(name)

    def has(self, name: str) -> bool:
        """Check if a function is registered."""
        return name in self.functions

    def list_functions(self) -> List[str]:
        """List all registered function names."""
        return list(self.functions.keys())
