"""DAG-specific exceptions for intent-kit."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExecutionError(Exception):
    """Error that occurred during node execution."""

    message: str
    node_name: str
    node_path: List[str]
    error_type: str = "ExecutionError"
    node_id: Optional[str] = None
    original_exception: Optional[Exception] = None

    def __str__(self) -> str:
        return f"{self.error_type}: {self.message} (node: {self.node_name})"

    @classmethod
    def from_exception(
        cls,
        exception: Exception,
        node_name: str,
        node_path: List[str],
        node_id: Optional[str] = None,
    ) -> "ExecutionError":
        """Create an ExecutionError from an exception."""
        return cls(
            message=str(exception),
            node_name=node_name,
            node_path=node_path,
            error_type=type(exception).__name__,
            node_id=node_id,
            original_exception=exception,
        )


class TraversalLimitError(RuntimeError):
    """Raised when traversal limits are exceeded."""

    pass


class NodeError(RuntimeError):
    """Raised when a node execution fails."""

    pass


class TraversalError(RuntimeError):
    """Raised when traversal fails due to node errors or other issues."""

    pass


class ContextConflictError(RuntimeError):
    """Raised when context patches conflict and cannot be merged."""

    pass


class CycleError(RuntimeError):
    """Raised when a cycle is detected in the DAG."""

    def __init__(self, message: str, cycle_path: list[str]):
        super().__init__(message)
        self.cycle_path = cycle_path


class NodeResolutionError(RuntimeError):
    """Raised when a node implementation cannot be resolved."""

    pass
