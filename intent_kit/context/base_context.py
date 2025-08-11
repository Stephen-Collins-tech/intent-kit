"""
Base Context - Abstract base class for context management.

This module provides the BaseContext ABC that defines the common interface
and shared characteristics for all context implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import uuid
from intent_kit.utils.logger import Logger


class BaseContext(ABC):
    """
    Abstract base class for context management implementations.

    This class defines the common interface and shared characteristics
    for all context implementations, including:
    - Session-based architecture
    - Debug logging support
    - Error tracking capabilities
    - State persistence patterns
    - Thread safety considerations
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize a new BaseContext.

        Args:
            session_id: Unique identifier for this context session
            debug: Enable debug logging
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.logger = Logger(self.__class__.__name__)

    @abstractmethod
    def get_error_count(self) -> int:
        """
        Get the total number of errors in the context.

        Returns:
            Number of errors tracked
        """
        pass

    @abstractmethod
    def add_error(
        self,
        node_name: str,
        user_input: str,
        error_message: str,
        error_type: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add an error to the context error log.

        Args:
            node_name: Name of the node where the error occurred
            user_input: The user input that caused the error
            error_message: The error message
            error_type: The type of error
            params: Optional parameters that were being processed
        """
        pass

    @abstractmethod
    def get_errors(
        self, node_name: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Any]:
        """
        Get errors from the context error log.

        Args:
            node_name: Filter errors by node name (optional)
            limit: Maximum number of errors to return (optional)

        Returns:
            List of error entries
        """
        pass

    @abstractmethod
    def clear_errors(self) -> None:
        """Clear all errors from the context."""
        pass

    @abstractmethod
    def track_operation(
        self,
        operation_type: str,
        success: bool,
        node_name: Optional[str] = None,
        user_input: Optional[str] = None,
        duration: Optional[float] = None,
        params: Optional[Dict[str, Any]] = None,
        result: Optional[Any] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Track an operation in the context operation log.

        Args:
            operation_type: Type/category of the operation
            success: Whether the operation succeeded
            node_name: Name of the node that executed the operation
            user_input: The user input that triggered the operation
            duration: Time taken to execute the operation in seconds
            params: Parameters used in the operation
            result: Result of the operation if successful
            error_message: Error message if operation failed
        """
        pass

    @abstractmethod
    def get_operations(
        self,
        operation_type: Optional[str] = None,
        node_name: Optional[str] = None,
        success: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[Any]:
        """
        Get operations from the context operation log.

        Args:
            operation_type: Filter by operation type (optional)
            node_name: Filter by node name (optional)
            success: Filter by success status (optional)
            limit: Maximum number of operations to return (optional)

        Returns:
            List of operation entries
        """
        pass

    @abstractmethod
    def get_operation_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive operation statistics.

        Returns:
            Dictionary containing operation statistics
        """
        pass

    @abstractmethod
    def clear_operations(self) -> None:
        """Clear all operations from the context."""
        pass

    @abstractmethod
    def get_operation_count(self) -> int:
        """
        Get the total number of operations in the context.

        Returns:
            Number of operations tracked
        """
        pass

    @abstractmethod
    def get_history(
        self, key: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Any]:
        """
        Get the history of context operations.

        Args:
            key: Filter history to specific key (optional)
            limit: Maximum number of entries to return (optional)

        Returns:
            List of history entries
        """
        pass

    @abstractmethod
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export the context to a dictionary for serialization.

        Returns:
            Dictionary representation of the context
        """
        pass

    def get_session_id(self) -> str:
        """
        Get the session ID for this context.

        Returns:
            The session ID
        """
        return self.session_id

    def log_error(self, message: str, **kwargs) -> None:
        """
        Log an error message.

        Args:
            message: The message to log
            **kwargs: Additional structured data to log
        """
        if kwargs:
            self.logger.debug_structured(kwargs, message)
        else:
            self.logger.error(message)

    def print_operation_summary(self) -> None:
        """
        Print a comprehensive summary of operations and errors.

        This is a convenience method that can be overridden by subclasses
        to provide custom reporting formats.
        """
        stats = self.get_operation_stats()
        total_errors = self.get_error_count()

        print("\n" + "=" * 80)
        print("OPERATION & ERROR SUMMARY")
        print("=" * 80)

        # Basic statistics
        total_ops = stats.get("total_operations", 0)
        successful_ops = stats.get("successful_operations", 0)
        failed_ops = stats.get("failed_operations", 0)
        success_rate = stats.get("success_rate", 0.0)

        print("\n📊 OVERALL STATISTICS:")
        print(f"   Total Operations: {total_ops}")
        print(f"   ✅ Successful: {successful_ops} ({success_rate*100:.1f}%)")
        print(f"   ❌ Failed: {failed_ops} ({(1-success_rate)*100:.1f}%)")
        print(f"   🚨 Total Errors Collected: {total_errors}")
        print("\n" + "=" * 80)

    def __str__(self) -> str:
        """String representation of the context."""
        return f"{self.__class__.__name__}(session_id={self.session_id})"

    def __repr__(self) -> str:
        """Detailed string representation of the context."""
        return self.__str__()
