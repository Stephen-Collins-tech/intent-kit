"""DAG validation utilities for intent-kit."""

from typing import Dict, Set, Optional, List
from collections import defaultdict, deque
from intent_kit.core.types import IntentDAG
from intent_kit.core.exceptions import CycleError


def validate_dag_structure(
    dag: IntentDAG, producer_labels: Optional[Dict[str, Set[str]]] = None
) -> List[str]:
    """Validate the DAG structure.

    Args:
        dag: The DAG to validate
        producer_labels: Optional dictionary mapping node_id to set of labels it can produce

    Returns:
        List of validation issues (empty if all valid)

    Raises:
        CycleError: If a cycle is detected
        ValueError: If basic structure is invalid
    """
    issues = []

    try:
        # Basic structure validation
        _validate_ids(dag)
        _validate_entrypoints(dag)

        # Cycle detection
        _validate_acyclic(dag)

        # Reachability
        unreachable = _validate_reachability(dag)
        if unreachable:
            issues.append(f"Unreachable nodes: {', '.join(unreachable)}")

        # Label validation (optional)
        if producer_labels:
            label_issues = _validate_labels(dag, producer_labels)
            issues.extend(label_issues)

    except (ValueError, CycleError):
        # Re-raise these as they indicate fundamental problems
        raise

    return issues


def _validate_ids(dag: IntentDAG) -> None:
    """Validate that all referenced IDs exist."""
    # Check entrypoints
    for entrypoint in dag.entrypoints:
        if entrypoint not in dag.nodes:
            raise ValueError(f"Entrypoint {entrypoint} does not exist in nodes")

    # Check edges
    for src, labels in dag.adj.items():
        if src not in dag.nodes:
            raise ValueError(f"Edge source {src} does not exist in nodes")
        for label, dsts in labels.items():
            for dst in dsts:
                if dst not in dag.nodes:
                    raise ValueError(f"Edge destination {dst} does not exist in nodes")

    # Check reverse adjacency
    for dst, srcs in dag.rev.items():
        if dst not in dag.nodes:
            raise ValueError(f"Reverse edge destination {dst} does not exist in nodes")
        for src in srcs:
            if src not in dag.nodes:
                raise ValueError(f"Reverse edge source {src} does not exist in nodes")


def _validate_entrypoints(dag: IntentDAG) -> None:
    """Validate that entrypoints exist and are reachable."""
    if not dag.entrypoints:
        raise ValueError("DAG must have at least one entrypoint")

    for entrypoint in dag.entrypoints:
        if entrypoint not in dag.nodes:
            raise ValueError(f"Entrypoint {entrypoint} does not exist in nodes")


def _validate_acyclic(dag: IntentDAG) -> None:
    """Validate that the DAG has no cycles using Kahn's algorithm."""
    # Calculate in-degrees
    in_degree = defaultdict(int)
    for node_id in dag.nodes:
        in_degree[node_id] = len(dag.rev.get(node_id, set()))

    # Kahn's algorithm
    queue: deque[str] = deque()
    for node_id in dag.nodes:
        if in_degree[node_id] == 0:
            queue.append(node_id)

    visited = 0
    topo_order = []

    while queue:
        node_id = queue.popleft()
        topo_order.append(node_id)
        visited += 1

        # Reduce in-degree of neighbors
        for label, dsts in dag.adj.get(node_id, {}).items():
            for dst in dsts:
                in_degree[dst] -= 1
                if in_degree[dst] == 0:
                    queue.append(dst)

    # If we didn't visit all nodes, there's a cycle
    if visited != len(dag.nodes):
        # Find the cycle using DFS
        cycle_path = _find_cycle_dfs(dag)
        raise CycleError(
            f"DAG contains a cycle with {len(cycle_path)} nodes", cycle_path
        )


def _find_cycle_dfs(dag: IntentDAG) -> List[str]:
    """Find a cycle in the DAG using DFS."""
    visited = set()
    rec_stack = set()
    cycle_path = []

    def dfs(node_id: str) -> bool:
        visited.add(node_id)
        rec_stack.add(node_id)
        cycle_path.append(node_id)

        for label, dsts in dag.adj.get(node_id, {}).items():
            for dst in dsts:
                if dst not in visited:
                    if dfs(dst):
                        return True
                elif dst in rec_stack:
                    # Found a cycle
                    cycle_start = cycle_path.index(dst)
                    cycle_path[:] = cycle_path[cycle_start:] + [dst]
                    return True

        rec_stack.remove(node_id)
        cycle_path.pop()
        return False

    # Try DFS from each unvisited node
    for node_id in dag.nodes:
        if node_id not in visited:
            if dfs(node_id):
                return cycle_path

    return []


def _validate_reachability(dag: IntentDAG) -> List[str]:
    """Validate that all nodes are reachable from entrypoints."""
    # BFS from all entrypoints
    visited = set()
    queue = deque(dag.entrypoints)

    while queue:
        node_id = queue.popleft()
        if node_id in visited:
            continue

        visited.add(node_id)

        # Add all neighbors
        for label, dsts in dag.adj.get(node_id, {}).items():
            for dst in dsts:
                if dst not in visited:
                    queue.append(dst)

    # Find unreachable nodes
    unreachable = []
    for node_id in dag.nodes:
        if node_id not in visited:
            unreachable.append(node_id)

    return unreachable


def _validate_labels(dag: IntentDAG, producer_labels: Dict[str, Set[str]]) -> List[str]:
    """Validate that node labels match outgoing edge labels."""
    issues = []

    for node_id, labels in producer_labels.items():
        if node_id not in dag.nodes:
            issues.append(f"Node {node_id} in producer_labels does not exist")
            continue

        # Get all outgoing edge labels for this node
        outgoing_labels = set()
        for label in dag.adj.get(node_id, {}).keys():
            if label is not None:  # Skip default/fall-through edges
                outgoing_labels.add(label)

        # Check if all produced labels have corresponding edges
        for label in labels:
            if label not in outgoing_labels:
                issues.append(
                    f"Node {node_id} can produce label '{label}' but has no corresponding edge"
                )

    return issues
