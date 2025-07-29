"""
Data classes and types for the node system.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from intent_kit.node.enums import NodeType
from intent_kit.types import InputTokens, Cost, Provider, TotalTokens, Duration


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
    output_tokens: Optional[TotalTokens] = 0
    input_tokens: Optional[InputTokens] = 0
    cost: Optional[Cost] = 0.0
    provider: Optional[Provider] = None
    model: Optional[str] = None
    error: Optional[ExecutionError] = None
    params: Optional[Dict[str, Any]] = None
    children_results: List["ExecutionResult"] = field(default_factory=list)
    duration: Optional[Duration] = 0.0

    @property
    def total_tokens(self) -> Optional[TotalTokens]:
        """Return the total tokens."""
        if self.output_tokens is None or self.input_tokens is None:
            return None
        return self.output_tokens + self.input_tokens

    def display(self) -> str:
        """Return a human-readable summary of all members of the execution result."""
        lines = [
            "ExecutionResult(",
            f"  success={self.success!r},",
            f"  node_name={self.node_name!r},",
            f"  node_path={self.node_path!r},",
            f"  node_type={self.node_type!r},",
            f"  input={self.input!r},",
            f"  output={self.output!r},",
            f"  total_tokens={self.total_tokens!r},",
            f"  input_tokens={self.input_tokens!r},",
            f"  output_tokens={self.output_tokens!r},",
            f"  cost={self.cost!r},",
            f"  provider={self.provider!r},",
            f"  model={self.model!r},",
            f"  error={self.error!r},",
            f"  params={self.params!r},",
            f"  children_results=[{', '.join(child.node_name for child in self.children_results)}],",
            f"  duration={self.duration!r}",
            ")",
        ]
        return "\n".join(lines)

    def to_json(self) -> dict:
        """Return a JSON-serializable dict representation of the execution result."""
        return {
            "success": self.success,
            "node_name": self.node_name,
            "node_path": self.node_path,
            "node_type": self.node_type,
            "input": self.input,
            "output": self.output,
            "total_tokens": self.total_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost": self.cost,
            "provider": self.provider if self.provider else None,
            "model": self.model,
            "error": self.error.to_dict() if self.error else None,
            "params": self.params,
            "children_results": [child.to_json() for child in self.children_results],
            "duration": self.duration,
        }
