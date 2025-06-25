"""
IntentGraph module for intent splitting and routing.

This module provides the IntentGraph class and supporting components for
handling multi-intent user inputs and routing them to appropriate taxonomies.
"""

from .intent_graph import IntentGraph
from .splitters import rule_splitter, llm_splitter, SplitterFunction
from .aggregation import aggregate_results, create_error_dict, create_no_intent_error, create_no_taxonomy_error

__all__ = [
    'IntentGraph',
    'rule_splitter',
    'llm_splitter',
    'SplitterFunction',
    'aggregate_results',
    'create_error_dict',
    'create_no_intent_error',
    'create_no_taxonomy_error'
]
