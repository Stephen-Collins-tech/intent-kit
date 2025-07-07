"""
Splitters module - consolidated splitter functionality.

This module provides both splitter functions and the SplitterNode class
for handling multi-intent user inputs.
"""

from .node import SplitterNode
from .functions import rule_splitter, llm_splitter
from .types import SplitterFunction

__all__ = [
    # Node class
    "SplitterNode",
    # Splitter functions
    "rule_splitter",
    "llm_splitter",
    "SplitterFunction",
]
