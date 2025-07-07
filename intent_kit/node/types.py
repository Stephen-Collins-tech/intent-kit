"""
Data classes and types for the node system.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from intent_kit.node.enums import NodeType


@dataclass
class ExecutionError:
    """Structured error information for execution results."""

    error_type: str
    message: str
    node_name: str
    node_path: List[str]
    node_id: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Any] = None
    params: Optional[Dict[str, Any]] = None
    original_exception: Optional[Exception] = None

    @classmethod
    def from_exception(
        cls,
        exception: Exception,
        node_name: str,
        node_path: List[str],
        node_id: Optional[str] = None,
    ) -> "ExecutionError":
        """Create an ExecutionError from an exception."""
        if hasattr(exception, "validation_error"):
            return cls(
                error_type=type(exception).__name__,
                message=getattr(exception, "validation_error", str(exception)),
                node_name=node_name,
                node_path=node_path,
                node_id=node_id,
                input_data=getattr(exception, "input_data", None),
                params=getattr(exception, "input_data", None),
            )
        elif hasattr(exception, "error_message"):
            return cls(
                error_type=type(exception).__name__,
                message=getattr(exception, "error_message", str(exception)),
                node_name=node_name,
                node_path=node_path,
                node_id=node_id,
                params=getattr(exception, "params", None),
            )
        else:
            return cls(
                error_type=type(exception).__name__,
                message=str(exception),
                node_name=node_name,
                node_path=node_path,
                node_id=node_id,
                original_exception=exception,
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary representation."""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "node_name": self.node_name,
            "node_path": self.node_path,
            "node_id": self.node_id,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "params": self.params,
        }


@dataclass
class ExecutionResult:
    """Standardized execution result structure for all nodes."""

    success: bool
    node_name: str
    node_path: List[str]
    node_type: NodeType
    input: str
    output: Optional[Any]
    error: Optional[ExecutionError]
    params: Optional[Dict[str, Any]]
    children_results: List["ExecutionResult"]
    visualization_html: Optional[str] = None
