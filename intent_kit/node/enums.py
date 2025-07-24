"""
Enums for the node system.
"""

from enum import Enum


class NodeType(Enum):
    """Enumeration of valid node types in the intent tree."""

    # Base node types
    UNKNOWN = "unknown"

    # Specialized node types
    ACTION = "action"
    CLASSIFIER = "classifier"
    SPLITTER = "splitter"
    CLARIFY = "clarify"
    GRAPH = "graph"

    # Special types for execution results
    UNHANDLED_CHUNK = "unhandled_chunk"


class ClassifierType(Enum):
    """Enumeration of classifier implementation types."""

    RULE = "rule"
    LLM = "llm"
    KEYWORD = "keyword"
    CHUNK = "chunk"


class SplitterType(Enum):
    """Enumeration of splitter implementation types."""

    RULE = "rule"
    LLM = "llm"
    FUNCTION = "function"
