"""
Intent Kit Exceptions

This module provides Node-related exception classes for the intent-kit project.
"""

from typing import Optional, List


class NodeError(Exception):
    """Base exception for node-related errors."""

    pass


class NodeExecutionError(NodeError):
    """Raised when a node execution fails."""

    def __init__(
        self,
        node_name: str,
        error_message: str,
        params=None,
        node_id: Optional[str] = None,
        node_path: Optional[List[str]] = None,
    ):
        """
        Initialize the exception.

        Args:
            node_name: The name of the node that failed
            error_message: The error message from the execution
            params: The parameters that were passed to the node
            node_id: The UUID of the node (from Node.node_id)
            node_path: The path from root to this node (from Node.get_path())
        """
        self.node_name = node_name
        self.error_message = error_message
        self.params = params or {}
        self.node_id = node_id
        self.node_path = node_path or []

        path_str = " -> ".join(node_path) if node_path else "unknown"
        message = f"Node '{node_name}' (path: {path_str}) failed: {error_message}"
        super().__init__(message)


class NodeValidationError(NodeError):
    """Base exception for node validation errors."""

    pass


class NodeInputValidationError(NodeValidationError):
    """Raised when node input validation fails."""

    def __init__(
        self,
        node_name: str,
        validation_error: str,
        input_data=None,
        node_id: Optional[str] = None,
        node_path: Optional[List[str]] = None,
    ):
        """
        Initialize the exception.

        Args:
            node_name: The name of the node that failed validation
            validation_error: The validation error message
            input_data: The input data that failed validation
            node_id: The UUID of the node (from Node.node_id)
            node_path: The path from root to this node (from Node.get_path())
        """
        self.node_name = node_name
        self.validation_error = validation_error
        self.input_data = input_data or {}
        self.node_id = node_id
        self.node_path = node_path or []

        path_str = " -> ".join(node_path) if node_path else "unknown"
        message = f"Node '{node_name}' (path: {path_str}) input validation failed: {validation_error}"
        super().__init__(message)


class NodeOutputValidationError(NodeValidationError):
    """Raised when node output validation fails."""

    def __init__(
        self,
        node_name: str,
        validation_error: str,
        output_data=None,
        node_id: Optional[str] = None,
        node_path: Optional[List[str]] = None,
    ):
        """
        Initialize the exception.

        Args:
            node_name: The name of the node that failed validation
            validation_error: The validation error message
            output_data: The output data that failed validation
            node_id: The UUID of the node (from Node.node_id)
            node_path: The path from root to this node (from Node.get_path())
        """
        self.node_name = node_name
        self.validation_error = validation_error
        self.output_data = output_data
        self.node_id = node_id
        self.node_path = node_path or []

        path_str = " -> ".join(node_path) if node_path else "unknown"
        message = f"Node '{node_name}' (path: {path_str}) output validation failed: {validation_error}"
        super().__init__(message)


class NodeNotFoundError(NodeError):
    """Raised when a requested node is not found."""

    def __init__(self, node_name: str, available_nodes=None):
        """
        Initialize the exception.

        Args:
            node_name: The name of the node that was not found
            available_nodes: List of available node names
        """
        self.node_name = node_name
        self.available_nodes = available_nodes or []

        message = f"Node '{node_name}' not found"
        super().__init__(message)


class NodeArgumentExtractionError(NodeError):
    """Raised when argument extraction for a node fails."""

    def __init__(self, node_name: str, error_message: str, user_input=None):
        """
        Initialize the exception.

        Args:
            node_name: The name of the node that failed argument extraction
            error_message: The error message from argument extraction
            user_input: The user input that failed extraction
        """
        self.node_name = node_name
        self.error_message = error_message
        self.user_input = user_input

        message = f"Node '{node_name}' argument extraction failed: {error_message}"
        super().__init__(message)


__all__ = [
    "NodeError",
    "NodeExecutionError",
    "NodeValidationError",
    "NodeInputValidationError",
    "NodeOutputValidationError",
    "NodeNotFoundError",
    "NodeArgumentExtractionError",
]
