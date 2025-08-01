"""
IntentGraph module for intent splitting and routing.

This module provides the IntentGraph class and supporting components for
handling multi-intent user inputs and routing them to appropriate taxonomies.
"""

from .intent_graph import IntentGraph
from .builder import IntentGraphBuilder

__all__ = [
    "IntentGraph",
    "IntentGraphBuilder",
]
