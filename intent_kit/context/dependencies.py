"""
Context Dependency Declarations

This module provides utilities for declaring and managing context dependencies
for intents and actions. This enables dependency graph building and validation.
"""

from typing import Set, Dict, Any, Optional, Protocol
from dataclasses import dataclass
from . import IntentContext


@dataclass
class ContextDependencies:
    """Declares what context fields an intent reads and writes."""

    inputs: Set[str]  # Fields this intent reads from context
    outputs: Set[str]  # Fields this intent writes to context
    description: str = ""  # Human-readable description of dependencies


class ContextAwareAction(Protocol):
    """Protocol for actions that can read/write context."""

    @property
    def context_dependencies(self) -> ContextDependencies:
        """Return the context dependencies for this action."""
        ...

    def __call__(self, context: IntentContext, **kwargs) -> Any:
        """Execute the action with context access."""
        ...


def declare_dependencies(
    inputs: Set[str], outputs: Set[str], description: str = ""
) -> ContextDependencies:
    """
    Create a context dependency declaration.

    Args:
        inputs: Set of context field names this intent reads
        outputs: Set of context field names this intent writes
        description: Human-readable description of dependencies

    Returns:
        ContextDependencies object
    """
    return ContextDependencies(inputs=inputs, outputs=outputs, description=description)


def validate_context_dependencies(
    dependencies: ContextDependencies, context: IntentContext, strict: bool = False
) -> Dict[str, Any]:
    """
    Validate that required context fields are available.

    Args:
        dependencies: The dependency declaration to validate
        context: The context to validate against
        strict: If True, fail if any input fields are missing

    Returns:
        Dict with validation results:
            - valid: bool
            - missing_inputs: Set[str]
            - available_inputs: Set[str]
            - warnings: List[str]
    """
    available_fields = context.keys()
    missing_inputs: set = dependencies.inputs - available_fields
    available_inputs: set = dependencies.inputs & available_fields

    warnings = []
    if missing_inputs and strict:
        warnings.append(f"Missing required context inputs: {missing_inputs}")

    if missing_inputs and not strict:
        warnings.append(f"Optional context inputs not available: {missing_inputs}")

    return {
        "valid": len(missing_inputs) == 0 or not strict,
        "missing_inputs": missing_inputs,
        "available_inputs": available_inputs,
        "warnings": warnings,
    }


def merge_dependencies(*dependencies: ContextDependencies) -> ContextDependencies:
    """
    Merge multiple dependency declarations.

    Args:
        *dependencies: ContextDependencies objects to merge

    Returns:
        Merged ContextDependencies object
    """
    if not dependencies:
        return declare_dependencies(set(), set(), "Empty dependencies")

    merged_inputs: set = set()
    merged_outputs: set = set()
    descriptions: list = []

    for dep in dependencies:
        merged_inputs.update(dep.inputs)
        merged_outputs.update(dep.outputs)
        if dep.description:
            descriptions.append(dep.description)

    # Remove outputs from inputs (outputs can be read by the same action)
    merged_inputs -= merged_outputs

    return ContextDependencies(
        inputs=merged_inputs,
        outputs=merged_outputs,
        description="; ".join(descriptions) if descriptions else "",
    )


def analyze_action_dependencies(action: Any) -> Optional[ContextDependencies]:
    """
    Analyze an action function to extract context dependencies.

    This is a best-effort analysis based on function annotations and docstrings.
    For precise dependency tracking, use explicit declarations.

    Args:
        action: The action function to analyze

    Returns:
        ContextDependencies if analysis is possible, None otherwise
    """
    if not callable(action):
        return None

    # Check if action has explicit dependencies
    if hasattr(action, "context_dependencies"):
        return action.context_dependencies

    # Check if action has dependency annotations
    if hasattr(action, "__annotations__"):
        annotations = action.__annotations__
        if "context_inputs" in annotations and "context_outputs" in annotations:
            inputs: set = getattr(action, "context_inputs", set())
            outputs: set = getattr(action, "context_outputs", set())
            return declare_dependencies(inputs, outputs)

    # Check docstring for dependency hints
    if hasattr(action, "__doc__") and action.__doc__:
        doc = action.__doc__.lower()
        inputs = set()
        outputs = set()

        # Simple pattern matching for common phrases
        if "context" in doc:
            if "read" in doc or "get" in doc:
                # This is a heuristic - in practice, explicit declarations are better
                pass
            if "write" in doc or "set" in doc or "update" in doc:
                pass

    return None


def create_dependency_graph(
    nodes: Dict[str, ContextDependencies],
) -> Dict[str, Set[str]]:
    """
    Create a dependency graph from node dependencies.

    Args:
        nodes: Dict mapping node names to their dependencies

    Returns:
        Dict mapping node names to sets of dependent nodes
    """
    graph: Dict[str, Set[str]] = {}

    for node_name, deps in nodes.items():
        graph[node_name] = set()

        for other_name, other_deps in nodes.items():
            if node_name == other_name:
                continue

            # Check if other node depends on this node's outputs
            if deps.outputs & other_deps.inputs:
                graph[node_name].add(other_name)

    return graph


def detect_circular_dependencies(graph: Dict[str, Set[str]]) -> Optional[list]:
    """
    Detect circular dependencies in a dependency graph.

    Args:
        graph: Dependency graph from create_dependency_graph

    Returns:
        List of nodes in circular dependency if found, None otherwise
    """
    visited = set()
    rec_stack = set()

    def dfs(node: str, path: list) -> Optional[list]:
        if node in rec_stack:
            # Found a cycle
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]

        if node in visited:
            return None

        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, set()):
            result = dfs(neighbor, path)
            if result:
                return result

        path.pop()
        rec_stack.remove(node)
        return None

    for node in graph:
        if node not in visited:
            result = dfs(node, [])
            if result:
                return result

    return None
