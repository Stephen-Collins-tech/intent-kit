"""
IntentKit - A Python library for building hierarchical intent classification and execution systems.

This library provides:
- Tree-based intent architecture with classifier and intent nodes
- IntentGraph for multi-intent routing and splitting
- Context-aware execution with dependency tracking
- Multiple AI service backends (OpenAI, Anthropic, Google AI, Ollama)
- Interactive visualization of execution paths
"""

from .nodes import TreeNode, NodeType
from .nodes.classifiers import ClassifierNode
from .nodes.actions import ActionNode

from .graph.builder import IntentGraphBuilder
from .context import IntentContext

# Export node factory functions for easier access
from .utils.node_factory import action, llm_classifier

__version__ = "0.5.0"

__all__ = [
    "IntentGraphBuilder",
    "TreeNode",
    "NodeType",
    "ClassifierNode",
    "ActionNode",
    "IntentContext",
    "action",
    "llm_classifier",
]
