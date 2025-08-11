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


class SemanticError(NodeError):
    """Base exception for semantic errors in intent processing."""

    def __init__(self, error_message: str, context_info=None):
        """
        Initialize the exception.

        Args:
            error_message: The semantic error message
            context_info: Additional context information about the error
        """
        self.error_message = error_message
        self.context_info = context_info or {}
        super().__init__(error_message)


class ClassificationError(SemanticError):
    """Raised when intent classification fails or produces invalid results."""

    def __init__(
        self,
        user_input: str,
        error_message: str,
        available_intents=None,
        classifier_output=None,
    ):
        """
        Initialize the exception.

        Args:
            user_input: The user input that failed classification
            error_message: The classification error message
            available_intents: List of available intents
            classifier_output: The raw output from the classifier
        """
        self.user_input = user_input
        self.available_intents = available_intents or []
        self.classifier_output = classifier_output

        message = f"Intent classification failed for '{user_input}': {error_message}"
        super().__init__(message)


class ParameterExtractionError(SemanticError):
    """Raised when parameter extraction from user input fails."""

    def __init__(
        self,
        node_name: str,
        user_input: str,
        error_message: str,
        required_params=None,
        extracted_params=None,
    ):
        """
        Initialize the exception.

        Args:
            node_name: The name of the node that failed parameter extraction
            user_input: The user input that failed extraction
            error_message: The extraction error message
            required_params: The parameters that were required
            extracted_params: The parameters that were successfully extracted
        """
        self.node_name = node_name
        self.user_input = user_input
        self.required_params = required_params or {}
        self.extracted_params = extracted_params or {}

        message = f"Parameter extraction failed for '{node_name}' with input '{user_input}': {error_message}"
        super().__init__(message)


class ContextStateError(SemanticError):
    """Raised when there are issues with context state management."""

    def __init__(
        self, error_message: str, context_key=None, context_value=None, operation=None
    ):
        """
        Initialize the exception.

        Args:
            error_message: The context error message
            context_key: The context key involved in the error
            context_value: The context value involved in the error
            operation: The operation that caused the error (get, set, delete)
        """
        self.context_key = context_key
        self.context_value = context_value
        self.operation = operation

        message = f"Context state error: {error_message}"
        super().__init__(message)


class GraphExecutionError(SemanticError):
    """Raised when graph execution fails at a semantic level."""

    def __init__(self, error_message: str, node_path=None, execution_context=None):
        """
        Initialize the exception.

        Args:
            error_message: The execution error message
            node_path: The path of nodes that were executed
            execution_context: Additional context about the execution
        """
        self.node_path = node_path or []
        self.execution_context = execution_context or {}

        path_str = " -> ".join(node_path) if node_path else "unknown"
        message = f"Graph execution error (path: {path_str}): {error_message}"
        super().__init__(message)


class ValidationError(SemanticError):
    """Raised when semantic validation fails."""

    def __init__(self, error_message: str, validation_type=None, data=None):
        """
        Initialize the exception.

        Args:
            error_message: The validation error message
            validation_type: The type of validation that failed
            data: The data that failed validation
        """
        self.validation_type = validation_type
        self.data = data

        message = f"Validation error ({validation_type}): {error_message}"
        super().__init__(message)


__all__ = [
    "NodeError",
    "NodeExecutionError",
    "NodeValidationError",
    "NodeInputValidationError",
    "NodeOutputValidationError",
    "NodeNotFoundError",
    "NodeArgumentExtractionError",
    "SemanticError",
    "ClassificationError",
    "ParameterExtractionError",
    "ContextStateError",
    "GraphExecutionError",
    "ValidationError",
]
