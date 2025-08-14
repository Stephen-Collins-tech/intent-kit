from typing import Protocol, runtime_checkable, Any
from typing import Dict, Set, List, Optional, Union
from dataclasses import dataclass, field

from .context import ContextProtocol

EdgeLabel = Optional[str]

# Context is now defined in core.context.ContextProtocol


@dataclass
class GraphNode:
    """A node in the intent DAG."""

    id: str
    type: str
    config: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate node configuration."""
        if not self.id:
            raise ValueError("Node ID cannot be empty")
        if not self.type:
            raise ValueError("Node type cannot be empty")


@dataclass
class IntentDAG:
    """A directed acyclic graph for intent processing - pure data structure."""

    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    adj: Dict[str, Dict[EdgeLabel, Set[str]]] = field(default_factory=dict)
    rev: Dict[str, Set[str]] = field(default_factory=dict)
    entrypoints: Union[list[str], tuple[str, ...]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of a node execution in the DAG."""

    data: Any = None
    next_edges: Optional[List[str]] = None
    terminate: bool = False
    metrics: Dict[str, Any] = field(default_factory=dict)
    context_patch: Dict[str, Any] = field(default_factory=dict)

    def merge_metrics(self, other: Dict[str, Any]) -> None:
        """Merge metrics from another source.

        Args:
            other: Dictionary of metrics to merge
        """
        for key, value in other.items():
            if key in self.metrics:
                # For numeric values, add them; otherwise replace
                if isinstance(self.metrics[key], (int, float)) and isinstance(
                    value, (int, float)
                ):
                    self.metrics[key] += value
                else:
                    self.metrics[key] = value
            else:
                self.metrics[key] = value


@runtime_checkable
class NodeProtocol(Protocol):
    """Protocol for nodes that can be executed in the DAG."""

    def execute(self, user_input: str, ctx: ContextProtocol) -> ExecutionResult:
        """Execute the node with given input and context.

        Args:
            user_input: The user input to process
            ctx: The execution context

        Returns:
            ExecutionResult containing the result and next steps
        """
        ...
