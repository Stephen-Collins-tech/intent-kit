"""
Intent Kit - A Python library for building hierarchical intent classification and execution systems.

This library provides a DAG-based intent architecture with classifier, extractor, action, and clarification nodes,
supports multiple AI service backends, and enables context-aware execution.
"""

from intent_kit.core import (
    IntentDAG,
    DAGBuilder,
    GraphNode,
    ExecutionResult,
    ExecutionError,
    NodeProtocol,
    run_dag,
    ContextProtocol,
    DefaultContext,
)

# run_dag is available from core.traversal

__version__ = "0.6.1"

__all__ = [
    "IntentDAG",
    "DAGBuilder",
    "GraphNode",
    "ExecutionResult",
    "ExecutionError",
    "NodeProtocol",
    "run_dag",
    "ContextProtocol",
    "DefaultContext",
]
