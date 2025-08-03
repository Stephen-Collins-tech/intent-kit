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
    CLARIFY = "clarify"
    GRAPH = "graph"


class ClassifierType(Enum):
    """Enumeration of classifier implementation types."""

    RULE = "rule"
    LLM = "llm"
