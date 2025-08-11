"""
Context package - Thread-safe context management for workflow state.

This package provides context management classes that enable state sharing
between different steps of a workflow, across conversations, and between taxonomies.

The package includes:
- BaseContext: Abstract base class for context implementations
- Context: Thread-safe context object for state management
- StackContext: Execution stack tracking with context state snapshots
- StackFrame: Individual frame in the execution stack
"""

# Import all context classes
from .base_context import BaseContext
from .context import Context
from .stack_context import StackContext, StackFrame

__all__ = [
    "BaseContext",
    "Context",
    "StackContext",
    "StackFrame",
]
