"""
Graph validation module for IntentKit.

This module provides validation functions to ensure proper routing constraints
and graph structure in intent graphs.
"""

from typing import List, Dict, Any, Optional
from intent_kit.node import TreeNode
from intent_kit.node.enums import NodeType
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


def validate_splitter_routing(graph_nodes: List[TreeNode]) -> None:
    """
    Validate that all splitter nodes only route to classifier nodes.

    Args:
        graph_nodes: List of all nodes in the graph to validate

    Raises:
        GraphValidationError: If any splitter node routes to a non-classifier node
    """
    logger = Logger(__name__)
    logger.debug("Validating splitter-to-classifier routing constraints...")

    for node in graph_nodes:
        if node.node_type == NodeType.SPLITTER:
            logger.debug(f"Checking splitter node: {node.name}")

            for child in node.children:
                if child.node_type != NodeType.CLASSIFIER:
                    error_msg = (
                        f"Invalid pipeline: Splitter node '{node.name}' outputs to "
                        f"non-classifier node '{child.name}' of type '{child.node_type}'. "
                        f"All splitter outputs must route only to classifier nodes."
                    )
                    logger.error(error_msg)
                    raise GraphValidationError(
                        message=error_msg,
                        node_name=node.name,
                        child_name=child.name,
                        child_type=child.node_type,
                    )
                else:
                    logger.debug(
                        f"  ✓ Splitter '{node.name}' correctly routes to classifier '{child.name}'"
                    )

    logger.info("Splitter routing validation passed ✓")


def validate_graph_structure(graph_nodes: List[TreeNode]) -> Dict[str, Any]:
    """
    Validate the overall graph structure and return statistics.

    Args:
        graph_nodes: List of all nodes in the graph to validate

    Returns:
        Dictionary containing graph statistics and validation results
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

    # Validate splitter routing
    try:
        validate_splitter_routing(all_nodes)
        routing_valid = True
    except GraphValidationError as e:
        routing_valid = False
        logger.error(f"Routing validation failed: {e.message}")

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
    Validate that all nodes have valid node types.

    Args:
        nodes: List of nodes to validate

    Raises:
        GraphValidationError: If any node has an invalid or unknown type
    """
    logger = Logger(__name__)
    logger.debug("Validating node types...")

    for node in nodes:
        if node.node_type not in NodeType:
            error_msg = f"Invalid node type '{node.node_type}' for node '{node.name}'. Valid types: {NodeType}"
            logger.error(error_msg)
            raise GraphValidationError(
                message=error_msg, node_name=node.name, child_type=node.node_type
            )

    logger.info("Node type validation passed ✓")
