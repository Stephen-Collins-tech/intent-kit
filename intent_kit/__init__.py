"""
IntentKit - A Python library for building hierarchical intent classification and execution systems.

This library provides:
- Tree-based intent architecture with classifier and intent nodes
- IntentGraph for multi-intent routing and splitting
- Context-aware execution with dependency tracking
- Multiple AI service backends (OpenAI, Anthropic, Google AI, Ollama)
- Interactive visualization of execution paths
"""

from .node import TreeNode, NodeType
from .classifiers import ClassifierNode
from .handlers import HandlerNode
from .splitters import SplitterNode
from .builder import (
    IntentGraphBuilder,
    handler,
    llm_classifier,
    llm_splitter_node,
    rule_splitter_node,
    create_intent_graph,
)
from .graph import IntentGraph
from .context import IntentContext
from .context.debug import (
    get_context_dependencies,
    validate_context_flow,
    trace_context_execution,
)
from .classifiers import keyword_classifier
from .classifiers.llm_classifier import create_llm_classifier, create_llm_arg_extractor
from .splitters import rule_splitter, llm_splitter
from .services.llm_factory import LLMFactory

__version__ = "0.1.0"

__all__ = [
    # Core components
    "HandlerNode",
    "TreeNode",
    "NodeType",
    "ClassifierNode",
    "SplitterNode",
    "IntentGraph",
    "IntentContext",
    # Classifiers
    "keyword_classifier",
    "create_llm_classifier",
    "create_llm_arg_extractor",
    # Splitters
    "rule_splitter",
    "llm_splitter",
    # Services
    "LLMFactory",
    # New high-level API (recommended)
    "IntentGraphBuilder",
    "handler",
    "llm_classifier",
    "llm_splitter_node",
    "rule_splitter_node",
    "create_intent_graph",
    # Context debugging utilities
    "get_context_dependencies",
    "validate_context_flow",
    "trace_context_execution",
]
