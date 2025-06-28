"""
IntentGraph module for intent splitting and routing.

This module provides the IntentGraph class and supporting components for
handling multi-intent user inputs and routing them to appropriate taxonomies.
"""

from .intent_graph import IntentGraph
from .splitters import rule_splitter, llm_splitter, SplitterFunction

__all__ = [
    'IntentGraph',
    'rule_splitter',
    'llm_splitter',
    'SplitterFunction',
]
