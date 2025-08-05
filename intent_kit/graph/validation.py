"""
Graph validation module for IntentKit.

This module provides validation functions to ensure proper routing constraints
and graph structure in intent graphs.
"""

from typing import List, Dict, Any, Optional
from intent_kit.nodes import TreeNode
from intent_kit.nodes.enums import NodeType
from intent_kit.utils.logger import Logger


class GraphValidationError(Exception):
    """Exception raised when graph validation fails."""

    def __init__(
        self,
        message: str,
        node_name: Optional[str] = None,
        child_name: Optional[str] = None,
        child_type: Optional[NodeType] = None,
    ):
        self.message = message
        self.node_name = node_name
        self.child_name = child_name
        self.child_type = child_type
        super().__init__(self.message)


def validate_graph_structure(graph_nodes: List[TreeNode]) -> Dict[str, Any]:
    """
    Validate the structure of an intent graph.

    Args:
        graph_nodes: List of root nodes in the graph

    Returns:
        Dictionary containing validation statistics
    """
    logger = Logger(__name__)
    logger.debug("Validating graph structure...")

    # Collect all nodes recursively
    all_nodes = _collect_all_nodes(graph_nodes)

    # Count nodes by type
    node_counts: Dict[Any, int] = {}
    for node in all_nodes:
        node_type = node.node_type
        node_counts[node_type] = node_counts.get(node_type, 0) + 1

    # Splitter routing validation removed - no splitter node type exists
    routing_valid = True

    # Check for cycles (basic check)
    has_cycles = _check_for_cycles(all_nodes)

    # Check for orphaned nodes
    orphaned_nodes = _find_orphaned_nodes(all_nodes)

    stats = {
        "total_nodes": len(all_nodes),
        "node_counts": node_counts,
        "routing_valid": routing_valid,
        "has_cycles": has_cycles,
        "orphaned_nodes": [node.name for node in orphaned_nodes],
        "orphaned_count": len(orphaned_nodes),
    }

    # Log structured validation results
    logger.debug_structured(
        {
            "total_nodes": len(all_nodes),
            "node_counts": node_counts,
            "routing_valid": routing_valid,
            "has_cycles": has_cycles,
            "orphaned_nodes": [node.name for node in orphaned_nodes],
            "orphaned_count": len(orphaned_nodes),
        },
        "Graph Structure Validation",
    )

    logger.info(
        f"Graph validation complete: {stats['total_nodes']} total nodes, "
        f"routing valid: {routing_valid}, cycles: {has_cycles}"
    )

    return stats


def _collect_all_nodes(nodes: List[TreeNode]) -> List[TreeNode]:
    """Recursively collect all nodes in the graph."""
    all_nodes = []
    visited = set()

    def collect_node(node: TreeNode):
        if node.node_id in visited:
            return
        visited.add(node.node_id)
        all_nodes.append(node)

        for child in node.children:
            collect_node(child)

    for node in nodes:
        collect_node(node)

    return all_nodes


def _check_for_cycles(nodes: List[TreeNode]) -> bool:
    """Check for cycles in the graph using DFS."""
    visited = set()
    rec_stack = set()

    def has_cycle_dfs(node: TreeNode) -> bool:
        if node.node_id in rec_stack:
            return True
        if node.node_id in visited:
            return False

        visited.add(node.node_id)
        rec_stack.add(node.node_id)

        for child in node.children:
            if has_cycle_dfs(child):
                return True

        rec_stack.remove(node.node_id)
        return False

    for node in nodes:
        if node.node_id not in visited:
            if has_cycle_dfs(node):
                return True

    return False


def _find_orphaned_nodes(nodes: List[TreeNode]) -> List[TreeNode]:
    """Find nodes that have no parent (orphaned)."""
    orphaned = []

    for node in nodes:
        if node.parent is None:
            orphaned.append(node)

    return orphaned


def validate_node_types(nodes: List[TreeNode]) -> None:
    """
    Validate that all nodes have valid types.

    Args:
        nodes: List of nodes to validate

    Raises:
        GraphValidationError: If any node has an invalid type
    """
    logger = Logger(__name__)
    logger.debug("Validating node types...")

    invalid_nodes = []
    for node in nodes:
        if not hasattr(node, "node_type") or node.node_type is None:
            invalid_nodes.append(node)

    if invalid_nodes:
        error_msg = f"Found {len(invalid_nodes)} nodes with invalid types: {[node.name for node in invalid_nodes]}"
        logger.error(error_msg)
        raise GraphValidationError(error_msg)

    # Log structured validation results
    logger.debug_structured(
        {
            "total_nodes": len(nodes),
            "valid_nodes": len(nodes) - len(invalid_nodes),
            "invalid_nodes": len(invalid_nodes),
            "node_types": [
                (
                    node.node_type.value
                    if hasattr(node, "node_type") and node.node_type
                    else None
                )
                for node in nodes
            ],
        },
        "Node Type Validation",
    )

    logger.info("Node type validation passed ✓")
