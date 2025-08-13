"""Core DAG and graph functionality for intent-kit."""

# Core types and data structures
from .types import IntentDAG, GraphNode, EdgeLabel, NodeProtocol, ExecutionResult

# DAG building and manipulation
from .dag import DAGBuilder

# Graph execution
from .traversal import run_dag

# Validation utilities
from .validation import validate_dag_structure

from .context import ContextProtocol, DefaultContext

# Exceptions
from .exceptions import (
    CycleError,
    TraversalError,
    TraversalLimitError,
    ContextConflictError,
    ExecutionError,
)

__all__ = [
    # Types
    "IntentDAG",
    "GraphNode",
    "EdgeLabel",
    "NodeProtocol",
    "ExecutionResult",
    "ContextProtocol",
    # DAG building
    "DAGBuilder",
    # Graph execution
    "run_dag",
    "DefaultContext",
    # Validation
    "validate_dag_structure",
    # Exceptions
    "CycleError",
    "TraversalError",
    "TraversalLimitError",
    "ContextConflictError",
    "ExecutionError",
]
