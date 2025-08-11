"""
Context - Thread-safe context object for sharing state between workflow steps.

This module provides the core Context class that enables state sharing
between different steps of a workflow, across conversations, and between taxonomies.
"""

from .base_context import BaseContext
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Set
from threading import Lock
import traceback
from datetime import datetime


@dataclass
class ContextField:
    """A lockable field in the context with metadata tracking."""

    value: Any
    lock: Lock = field(default_factory=Lock)
    last_modified: datetime = field(default_factory=datetime.now)
    modified_by: Optional[str] = field(default=None)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ContextHistoryEntry:
    """An entry in the context history log."""

    timestamp: datetime
    action: str  # 'set', 'get', 'delete'
    key: str
    value: Any
    modified_by: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class ContextErrorEntry:
    """An error entry in the context error log."""

    timestamp: datetime
    node_name: str
    user_input: str
    error_message: str
    error_type: str
    stack_trace: str
    params: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


@dataclass
class ContextOperationEntry:
    """An operation entry in the context operation log."""

    timestamp: datetime
    operation_type: str
    node_name: Optional[str]
    success: bool
    user_input: Optional[str] = None
    duration: Optional[float] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    session_id: Optional[str] = None


class Context(BaseContext):
    """
    Thread-safe context object for sharing state between workflow steps.

    Features:
    - Field-level locking for concurrent access
    - Complete audit trail of all operations
    - Error tracking with detailed information
    - Session-based isolation
    - Type-safe field access
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize a new Context.

        Args:
            session_id: Unique identifier for this context session
            debug: Enable debug logging
        """
        super().__init__(session_id=session_id)
        self._fields: Dict[str, ContextField] = {}
        self._history: List[ContextHistoryEntry] = []
        self._errors: List[ContextErrorEntry] = []
        self._operations: List[ContextOperationEntry] = []
        self._global_lock = Lock()

        # Track important context keys that should be logged for debugging
        self._important_context_keys: Set[str] = set()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from context with field-level locking.

        Args:
            key: The field key to retrieve
            default: Default value if key doesn't exist

        Returns:
            The field value or default
        """
        with self._global_lock:
            if key not in self._fields:
                self.logger.debug(
                    f"Key '{key}' not found, returning default: {default}"
                )
                self._log_history("get", key, default, None)
                return default
            field = self._fields[key]

        with field.lock:
            value = field.value
            self.logger.debug_structured(
                {
                    "action": "get",
                    "key": key,
                    "value": value,
                    "session_id": self.session_id,
                },
                "Context Retrieval",
            )
            self._log_history("get", key, value, None)
            return value

    def set(self, key: str, value: Any, modified_by: Optional[str] = None) -> None:
        """
        Set a value in context with field-level locking and history tracking.

        Args:
            key: The field key to set
            value: The value to store
            modified_by: Identifier for who/what modified this field
        """
        with self._global_lock:
            if key not in self._fields:
                self._fields[key] = ContextField(value)
                # Set modified_by for new fields
                self._fields[key].modified_by = modified_by
                self.logger.debug_structured(
                    {
                        "action": "create",
                        "key": key,
                        "value": value,
                        "modified_by": modified_by,
                        "session_id": self.session_id,
                    },
                    "Context Field Created",
                )
            else:
                field = self._fields[key]
                with field.lock:
                    old_value = field.value
                    field.value = value
                    field.last_modified = datetime.now()
                    field.modified_by = modified_by
                    self.logger.debug_structured(
                        {
                            "action": "update",
                            "key": key,
                            "old_value": old_value,
                            "new_value": value,
                            "modified_by": modified_by,
                            "session_id": self.session_id,
                        },
                        "Context Field Updated",
                    )

            self._log_history("set", key, value, modified_by)

    def delete(self, key: str, modified_by: Optional[str] = None) -> bool:
        """
        Delete a field from context.

        Args:
            key: The field key to delete
            modified_by: Identifier for who/what deleted this field

        Returns:
            True if field was deleted, False if it didn't exist
        """
        with self._global_lock:
            if key not in self._fields:
                self.logger.debug(f"Attempted to delete non-existent key '{key}'")
                self._log_history("delete", key, None, modified_by)
                return False

            del self._fields[key]
            self.logger.debug_structured(
                {
                    "action": "delete",
                    "key": key,
                    "modified_by": modified_by,
                    "session_id": self.session_id,
                },
                "Context Field Deleted",
            )
            self._log_history("delete", key, None, modified_by)
            return True

    def has(self, key: str) -> bool:
        """
        Check if a field exists in context.

        Args:
            key: The field key to check

        Returns:
            True if field exists, False otherwise
        """
        with self._global_lock:
            return key in self._fields

    def keys(self) -> Set[str]:
        """
        Get all field keys in the context.

        Returns:
            Set of all field keys
        """
        with self._global_lock:
            return set(self._fields.keys())

    def get_history(
        self, key: Optional[str] = None, limit: Optional[int] = None
    ) -> List[ContextHistoryEntry]:
        """
        Get the history of context operations.

        Args:
            key: Filter history to specific key (optional)
            limit: Maximum number of entries to return (optional)

        Returns:
            List of history entries
        """
        with self._global_lock:
            if key:
                filtered_history = [
                    entry for entry in self._history if entry.key == key
                ]
            else:
                filtered_history = self._history.copy()

            if limit:
                filtered_history = filtered_history[-limit:]

            return filtered_history

    def get_field_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific field.

        Args:
            key: The field key

        Returns:
            Dictionary with field metadata or None if field doesn't exist
        """
        with self._global_lock:
            if key not in self._fields:
                return None

            field = self._fields[key]
            return {
                "created_at": field.created_at,
                "last_modified": field.last_modified,
                "modified_by": field.modified_by,
                "value": field.value,
            }

    def mark_important(self, key: str) -> None:
        """
        Mark a context key as important for debugging.

        Args:
            key: The context key to mark as important
        """
        self._important_context_keys.add(key)

    def clear(self, modified_by: Optional[str] = None) -> None:
        """
        Clear all fields from context.

        Args:
            modified_by: Identifier for who/what cleared the context
        """
        with self._global_lock:
            keys = list(self._fields.keys())
            self._fields.clear()
            self.logger.debug_structured(
                {
                    "action": "clear",
                    "cleared_keys": keys,
                    "modified_by": modified_by,
                    "session_id": self.session_id,
                },
                "Context Cleared",
            )
            self._log_history("clear", "all", None, modified_by)

    def _log_history(
        self, action: str, key: str, value: Any, modified_by: Optional[str]
    ) -> None:
        """Log an operation to the history."""
        entry = ContextHistoryEntry(
            timestamp=datetime.now(),
            action=action,
            key=key,
            value=value,
            modified_by=modified_by,
            session_id=self.session_id,
        )
        self._history.append(entry)

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
        with self._global_lock:
            error_entry = ContextErrorEntry(
                timestamp=datetime.now(),
                node_name=node_name,
                user_input=user_input,
                error_message=error_message,
                error_type=error_type,
                stack_trace=traceback.format_exc(),
                params=params,
                session_id=self.session_id,
            )
            self._errors.append(error_entry)

            self.logger.error(f"Added error to context: {node_name}: {error_message}")

    def get_errors(
        self, node_name: Optional[str] = None, limit: Optional[int] = None
    ) -> List[ContextErrorEntry]:
        """
        Get errors from the context error log.

        Args:
            node_name: Filter errors by node name (optional)
            limit: Maximum number of errors to return (optional)

        Returns:
            List of error entries
        """
        with self._global_lock:
            filtered_errors = self._errors.copy()

            if node_name:
                filtered_errors = [
                    error for error in filtered_errors if error.node_name == node_name
                ]

            if limit:
                filtered_errors = filtered_errors[-limit:]

            return filtered_errors

    def clear_errors(self) -> None:
        """Clear all errors from the context."""
        with self._global_lock:
            error_count = len(self._errors)
            self._errors.clear()
            self.logger.debug(f"Cleared {error_count} errors from context")

    def get_error_count(self) -> int:
        """Get the total number of errors in the context."""
        with self._global_lock:
            return len(self._errors)

    def error_count(self) -> int:
        """Get the total number of errors in the context. (Legacy method)"""
        return self.get_error_count()

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
        with self._global_lock:
            operation_entry = ContextOperationEntry(
                timestamp=datetime.now(),
                operation_type=operation_type,
                node_name=node_name,
                success=success,
                user_input=user_input,
                duration=duration,
                params=params,
                result=result,
                error_message=error_message,
                session_id=self.session_id,
            )
            self._operations.append(operation_entry)

            status = "✅ SUCCESS" if success else "❌ FAILED"
            self.logger.info(
                f"Operation tracked: {operation_type} - {status} - {node_name or 'unknown'}"
            )

    def get_operations(
        self,
        operation_type: Optional[str] = None,
        node_name: Optional[str] = None,
        success: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[ContextOperationEntry]:
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
        with self._global_lock:
            filtered_operations = self._operations.copy()

            if operation_type:
                filtered_operations = [
                    op
                    for op in filtered_operations
                    if op.operation_type == operation_type
                ]

            if node_name:
                filtered_operations = [
                    op for op in filtered_operations if op.node_name == node_name
                ]

            if success is not None:
                filtered_operations = [
                    op for op in filtered_operations if op.success == success
                ]

            if limit:
                filtered_operations = filtered_operations[-limit:]

            return filtered_operations

    def get_operation_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive operation statistics.

        Returns:
            Dictionary containing operation statistics
        """
        with self._global_lock:
            total_ops = len(self._operations)
            if total_ops == 0:
                return {
                    "total_operations": 0,
                    "successful_operations": 0,
                    "failed_operations": 0,
                    "success_rate": 0.0,
                    "operations_by_type": {},
                    "operations_by_node": {},
                    "error_types": {},
                }

            successful_ops = len([op for op in self._operations if op.success])
            failed_ops = total_ops - successful_ops

            # Group by operation type
            ops_by_type = {}
            for op in self._operations:
                if op.operation_type not in ops_by_type:
                    ops_by_type[op.operation_type] = {"success": 0, "failed": 0}

                if op.success:
                    ops_by_type[op.operation_type]["success"] += 1
                else:
                    ops_by_type[op.operation_type]["failed"] += 1

            # Group by node
            ops_by_node = {}
            for op in self._operations:
                node_key = op.node_name or "unknown"
                if node_key not in ops_by_node:
                    ops_by_node[node_key] = {"success": 0, "failed": 0}

                if op.success:
                    ops_by_node[node_key]["success"] += 1
                else:
                    ops_by_node[node_key]["failed"] += 1

            # Error types from failed operations
            error_types = {}
            for op in self._operations:
                if not op.success and op.error_message:
                    # Extract error type from error message (simple heuristic)
                    error_type = (
                        op.error_message.split(":")[0]
                        if ":" in op.error_message
                        else "unknown_error"
                    )
                    error_types[error_type] = error_types.get(error_type, 0) + 1

            return {
                "total_operations": total_ops,
                "successful_operations": successful_ops,
                "failed_operations": failed_ops,
                "success_rate": successful_ops / total_ops if total_ops > 0 else 0.0,
                "operations_by_type": ops_by_type,
                "operations_by_node": ops_by_node,
                "error_types": error_types,
            }

    def clear_operations(self) -> None:
        """Clear all operations from the context."""
        with self._global_lock:
            operation_count = len(self._operations)
            self._operations.clear()
            self.logger.debug(f"Cleared {operation_count} operations from context")

    def get_operation_count(self) -> int:
        """Get the total number of operations in the context."""
        with self._global_lock:
            return len(self._operations)

    def print_operation_summary(self) -> None:
        """Print a comprehensive summary of operations and errors."""
        stats = self.get_operation_stats()
        total_errors = self.get_error_count()

        print("\n" + "=" * 80)
        print("CONTEXT OPERATION & ERROR SUMMARY")
        print("=" * 80)

        # Overall Statistics
        total_ops = stats["total_operations"]
        successful_ops = stats["successful_operations"]
        failed_ops = stats["failed_operations"]
        success_rate = stats["success_rate"]

        print("\n📊 OVERALL STATISTICS:")
        print(f"   Total Operations: {total_ops}")
        print(f"   ✅ Successful: {successful_ops} ({success_rate*100:.1f}%)")
        print(f"   ❌ Failed: {failed_ops} ({(1-success_rate)*100:.1f}%)")
        print(f"   🚨 Total Errors Collected: {total_errors}")

        # Success Rate by Operation Type
        if stats["operations_by_type"]:
            print("\n📋 SUCCESS RATE BY OPERATION TYPE:")
            for op_type, type_stats in stats["operations_by_type"].items():
                total_for_type = type_stats["success"] + type_stats["failed"]
                type_success_rate = (
                    (type_stats["success"] / total_for_type * 100)
                    if total_for_type > 0
                    else 0
                )
                print(f"   {op_type}:")
                print(f"     ✅ Success: {type_stats['success']}")
                print(f"     ❌ Failed: {type_stats['failed']}")
                print(f"     📈 Success Rate: {type_success_rate:.1f}%")

        # Success Rate by Node
        if stats["operations_by_node"]:
            print("\n🔧 SUCCESS RATE BY NODE:")
            for node_name, node_stats in stats["operations_by_node"].items():
                total_for_node = node_stats["success"] + node_stats["failed"]
                node_success_rate = (
                    (node_stats["success"] / total_for_node * 100)
                    if total_for_node > 0
                    else 0
                )
                print(f"   {node_name}:")
                print(f"     ✅ Success: {node_stats['success']}")
                print(f"     ❌ Failed: {node_stats['failed']}")
                print(f"     📈 Success Rate: {node_success_rate:.1f}%")

        # Error Types Distribution
        if stats["error_types"]:
            print("\n🚨 ERROR TYPES DISTRIBUTION:")
            sorted_errors = sorted(
                stats["error_types"].items(), key=lambda x: x[1], reverse=True
            )
            for error_type, count in sorted_errors:
                percentage = (count / failed_ops * 100) if failed_ops > 0 else 0
                print(f"   {error_type}: {count} ({percentage:.1f}%)")

        print("\n" + "=" * 80)

    def __str__(self) -> str:
        """String representation of the context."""
        with self._global_lock:
            field_count = len(self._fields)
            history_count = len(self._history)
            error_count = len(self._errors)
            operation_count = len(self._operations)

        return f"Context(session_id={self.session_id}, fields={field_count}, history={history_count}, errors={error_count}, operations={operation_count})"

    def export_to_dict(self) -> Dict[str, Any]:
        """Export the context to a dictionary for serialization."""
        with self._global_lock:
            # Compute operation stats directly to avoid deadlock
            total_ops = len(self._operations)
            if total_ops == 0:
                operation_stats = {
                    "total_operations": 0,
                    "successful_operations": 0,
                    "failed_operations": 0,
                    "success_rate": 0.0,
                    "operations_by_type": {},
                    "operations_by_node": {},
                    "error_types": {},
                }
            else:
                successful_ops = len([op for op in self._operations if op.success])
                failed_ops = total_ops - successful_ops

                # Group by operation type
                ops_by_type = {}
                for op in self._operations:
                    if op.operation_type not in ops_by_type:
                        ops_by_type[op.operation_type] = {"success": 0, "failed": 0}

                    if op.success:
                        ops_by_type[op.operation_type]["success"] += 1
                    else:
                        ops_by_type[op.operation_type]["failed"] += 1

                # Group by node
                ops_by_node = {}
                for op in self._operations:
                    node_key = op.node_name or "unknown"
                    if node_key not in ops_by_node:
                        ops_by_node[node_key] = {"success": 0, "failed": 0}

                    if op.success:
                        ops_by_node[node_key]["success"] += 1
                    else:
                        ops_by_node[node_key]["failed"] += 1

                # Error types from failed operations
                error_types = {}
                for op in self._operations:
                    if not op.success and op.error_message:
                        # Extract error type from error message (simple heuristic)
                        error_type = (
                            op.error_message.split(":")[0]
                            if ":" in op.error_message
                            else "unknown_error"
                        )
                        error_types[error_type] = error_types.get(error_type, 0) + 1

                operation_stats = {
                    "total_operations": total_ops,
                    "successful_operations": successful_ops,
                    "failed_operations": failed_ops,
                    "success_rate": (
                        successful_ops / total_ops if total_ops > 0 else 0.0
                    ),
                    "operations_by_type": ops_by_type,
                    "operations_by_node": ops_by_node,
                    "error_types": error_types,
                }

            return {
                "session_id": self.session_id,
                "fields": {
                    key: {
                        "value": field.value,
                        "created_at": field.created_at.isoformat(),
                        "last_modified": field.last_modified.isoformat(),
                        "modified_by": field.modified_by,
                    }
                    for key, field in self._fields.items()
                },
                "history_count": len(self._history),
                "error_count": len(self._errors),
                "operation_count": len(self._operations),
                "operation_stats": operation_stats,
                "important_keys": list(self._important_context_keys),
            }

    def __repr__(self) -> str:
        """Detailed string representation of the context."""
        return self.__str__()
