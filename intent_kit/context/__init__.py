"""
IntentContext - Thread-safe context object for sharing state between workflow steps.

This module provides the core IntentContext class that enables state sharing
between different steps of a workflow, across conversations, and between taxonomies.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Set
from threading import Lock
import uuid
import traceback
from datetime import datetime
from intent_kit.utils.logger import Logger


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


class IntentContext:
    """
    Thread-safe context object for sharing state between workflow steps.

    Features:
    - Field-level locking for concurrent access
    - Complete audit trail of all operations
    - Error tracking with detailed information
    - Session-based isolation
    - Type-safe field access
    """

    def __init__(self, session_id: Optional[str] = None, debug: bool = False):
        """
        Initialize a new IntentContext.

        Args:
            session_id: Unique identifier for this context session
            debug: Enable debug logging
        """
        self.session_id = session_id or str(uuid.uuid4())
        self._fields: Dict[str, ContextField] = {}
        self._history: List[ContextHistoryEntry] = []
        self._errors: List[ContextErrorEntry] = []
        self._global_lock = Lock()
        self._debug = debug
        self.logger = Logger(__name__)

        if self._debug:
            self.logger.info(
                f"Created IntentContext with session_id: {self.session_id}"
            )

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
                if self._debug:
                    self.logger.debug(
                        f"Key '{key}' not found, returning default: {default}"
                    )
                self._log_history("get", key, default, None)
                return default
            field = self._fields[key]

        with field.lock:
            value = field.value
            if self._debug:
                self.logger.debug(f"Retrieved '{key}' = {value}")
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
                if self._debug:
                    self.logger.debug(f"Created new field '{key}' = {value}")
            else:
                field = self._fields[key]
                with field.lock:
                    old_value = field.value
                    field.value = value
                    field.last_modified = datetime.now()
                    field.modified_by = modified_by
                    if self._debug:
                        self.logger.debug(
                            f"Updated field '{key}' from {old_value} to {value}"
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
                if self._debug:
                    self.logger.debug(f"Attempted to delete non-existent key '{key}'")
                self._log_history("delete", key, None, modified_by)
                return False

            del self._fields[key]
            if self._debug:
                self.logger.debug(f"Deleted field '{key}'")
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

    def clear(self, modified_by: Optional[str] = None) -> None:
        """
        Clear all fields from context.

        Args:
            modified_by: Identifier for who/what cleared the context
        """
        with self._global_lock:
            keys = list(self._fields.keys())
            self._fields.clear()
            if self._debug:
                self.logger.debug(f"Cleared all fields: {keys}")
            self._log_history("clear", "ALL", None, modified_by)

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

            if self._debug:
                self.logger.error(
                    f"Added error to context: {node_name}: {error_message}"
                )

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
            if self._debug:
                self.logger.debug(f"Cleared {error_count} errors from context")

    def error_count(self) -> int:
        """Get the total number of errors in the context."""
        with self._global_lock:
            return len(self._errors)

    def __str__(self) -> str:
        """String representation of the context."""
        with self._global_lock:
            field_count = len(self._fields)
            history_count = len(self._history)
            error_count = len(self._errors)

        return f"IntentContext(session_id={self.session_id}, fields={field_count}, history={history_count}, errors={error_count})"

    def __repr__(self) -> str:
        """Detailed string representation of the context."""
        return self.__str__()
