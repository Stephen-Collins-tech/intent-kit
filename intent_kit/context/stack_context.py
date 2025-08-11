"""
Stack Context - Tracks function calls and Context state during graph execution.

This module provides the StackContext class that maintains a stack of function
calls and their associated Context state at each point in the execution.
"""

from .base_context import BaseContext
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, TYPE_CHECKING
import uuid
from datetime import datetime

if TYPE_CHECKING:
    from intent_kit.context import Context


@dataclass
class StackFrame:
    """A frame in the execution stack with function call and context state."""

    frame_id: str
    timestamp: datetime
    function_name: str
    node_name: str
    node_path: List[str]
    user_input: str
    parameters: Dict[str, Any]
    context_state: Dict[str, Any]
    context_field_count: int
    context_history_count: int
    context_error_count: int
    depth: int
    parent_frame_id: Optional[str] = None
    children_frame_ids: List[str] = field(default_factory=list)
    execution_result: Optional[Dict[str, Any]] = None
    error_info: Optional[Dict[str, Any]] = None


class StackContext(BaseContext):
    """
    Tracks function calls and Context state during graph execution.

    Features:
    - Stack-based execution tracking
    - Context state snapshots at each frame
    - Parent-child relationship tracking
    - Error state preservation
    - Complete audit trail
    """

    def __init__(self, context: "Context"):
        """
        Initialize a new StackContext.

        Args:
            context: The Context object to track
            debug: Enable debug logging (defaults to context's debug mode)
        """
        # Use the context's session_id and debug mode
        super().__init__(session_id=context.session_id)
        self.context = context
        self._frames: List[StackFrame] = []
        self._frame_map: Dict[str, StackFrame] = {}
        self._current_frame_id: Optional[str] = None
        self._frame_counter = 0

    def push_frame(
        self,
        function_name: str,
        node_name: str,
        node_path: List[str],
        user_input: str,
        parameters: Dict[str, Any],
    ) -> str:
        """
        Push a new frame onto the stack.

        Args:
            function_name: Name of the function being called
            node_name: Name of the node being executed
            node_path: Path from root to this node
            user_input: The user input being processed
            parameters: Parameters passed to the function

        Returns:
            Frame ID for the new frame
        """
        frame_id = str(uuid.uuid4())
        depth = len(self._frames)

        # Capture current context state
        context_state = {}
        context_field_count = len(self.context.keys())
        context_history_count = len(self.context.get_history())
        context_error_count = self.context.error_count()

        # Get all current context fields
        for key in self.context.keys():
            value = self.context.get(key)
            metadata = self.context.get_field_metadata(key)
            context_state[key] = {"value": value, "metadata": metadata}

        frame = StackFrame(
            frame_id=frame_id,
            timestamp=datetime.now(),
            function_name=function_name,
            node_name=node_name,
            node_path=node_path,
            user_input=user_input,
            parameters=parameters,
            context_state=context_state,
            context_field_count=context_field_count,
            context_history_count=context_history_count,
            context_error_count=context_error_count,
            depth=depth,
            parent_frame_id=self._current_frame_id,
        )

        # Add to parent's children if there is a parent
        if self._current_frame_id and self._current_frame_id in self._frame_map:
            parent_frame = self._frame_map[self._current_frame_id]
            parent_frame.children_frame_ids.append(frame_id)

        self._frames.append(frame)
        self._frame_map[frame_id] = frame
        self._current_frame_id = frame_id
        self._frame_counter += 1

        self.logger.debug_structured(
            {
                "action": "push_frame",
                "frame_id": frame_id,
                "function_name": function_name,
                "node_name": node_name,
                "depth": depth,
                "context_field_count": context_field_count,
            },
            "Stack Frame Pushed",
        )

        return frame_id

    def pop_frame(
        self,
        execution_result: Optional[Dict[str, Any]] = None,
        error_info: Optional[Dict[str, Any]] = None,
    ) -> Optional[StackFrame]:
        """
        Pop the current frame from the stack.

        Args:
            execution_result: Result of the function execution
            error_info: Error information if execution failed

        Returns:
            The popped frame or None if stack is empty
        """
        if not self._current_frame_id:
            return None

        frame = self._frame_map[self._current_frame_id]
        frame.execution_result = execution_result
        frame.error_info = error_info

        # Update to parent frame
        self._current_frame_id = frame.parent_frame_id

        self.logger.debug_structured(
            {
                "action": "pop_frame",
                "frame_id": frame.frame_id,
                "function_name": frame.function_name,
                "node_name": frame.node_name,
                "success": execution_result is not None and error_info is None,
            },
            "Stack Frame Popped",
        )

        return frame

    def get_current_frame(self) -> Optional[StackFrame]:
        """Get the current frame."""
        if not self._current_frame_id:
            return None
        return self._frame_map[self._current_frame_id]

    def get_stack_depth(self) -> int:
        """Get the current stack depth."""
        return len(self._frames)

    def get_all_frames(self) -> List[StackFrame]:
        """Get all frames in chronological order."""
        return self._frames.copy()

    def get_frame_by_id(self, frame_id: str) -> Optional[StackFrame]:
        """Get a frame by its ID."""
        return self._frame_map.get(frame_id)

    def get_frames_by_node(self, node_name: str) -> List[StackFrame]:
        """Get all frames for a specific node."""
        return [frame for frame in self._frames if frame.node_name == node_name]

    def get_frames_by_function(self, function_name: str) -> List[StackFrame]:
        """Get all frames for a specific function."""
        return [frame for frame in self._frames if frame.function_name == function_name]

    def get_error_frames(self) -> List[StackFrame]:
        """Get all frames that had errors."""
        return [frame for frame in self._frames if frame.error_info is not None]

    def get_context_changes_between_frames(
        self, frame1_id: str, frame2_id: str
    ) -> Dict[str, Any]:
        """
        Get context changes between two frames.

        Args:
            frame1_id: ID of the first frame
            frame2_id: ID of the second frame

        Returns:
            Dictionary containing context changes
        """
        frame1 = self._frame_map.get(frame1_id)
        frame2 = self._frame_map.get(frame2_id)

        if not frame1 or not frame2:
            return {}

        state1 = frame1.context_state
        state2 = frame2.context_state

        changes = {
            "added_fields": {},
            "removed_fields": {},
            "modified_fields": {},
            "field_count_change": frame2.context_field_count
            - frame1.context_field_count,
            "history_count_change": frame2.context_history_count
            - frame1.context_history_count,
            "error_count_change": frame2.context_error_count
            - frame1.context_error_count,
        }

        # Find added fields
        for key in state2:
            if key not in state1:
                changes["added_fields"][key] = state2[key]

        # Find removed fields
        for key in state1:
            if key not in state2:
                changes["removed_fields"][key] = state1[key]

        # Find modified fields
        for key in state1:
            if key in state2 and state1[key]["value"] != state2[key]["value"]:
                changes["modified_fields"][key] = {
                    "old_value": state1[key]["value"],
                    "new_value": state2[key]["value"],
                    "old_metadata": state1[key]["metadata"],
                    "new_metadata": state2[key]["metadata"],
                }

        return changes

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the execution."""
        total_frames = len(self._frames)
        error_frames = len(self.get_error_frames())
        successful_frames = total_frames - error_frames

        # Get unique nodes and functions
        unique_nodes = set(frame.node_name for frame in self._frames)
        unique_functions = set(frame.function_name for frame in self._frames)

        # Get max depth
        max_depth = max(frame.depth for frame in self._frames) if self._frames else 0

        return {
            "total_frames": total_frames,
            "successful_frames": successful_frames,
            "error_frames": error_frames,
            "success_rate": successful_frames / total_frames if total_frames > 0 else 0,
            "unique_nodes": list(unique_nodes),
            "unique_functions": list(unique_functions),
            "max_depth": max_depth,
            "session_id": self.context.session_id,
        }

    def print_stack_trace(self, include_context: bool = False) -> None:
        """Print a human-readable stack trace."""
        print(f"\n=== Stack Trace (Session: {self.context.session_id}) ===")
        print(f"Total Frames: {len(self._frames)}")
        print(f"Current Depth: {self.get_stack_depth()}")

        for i, frame in enumerate(self._frames):
            indent = "  " * frame.depth
            status = "❌" if frame.error_info else "✅"

            print(
                f"{indent}{status} Frame {i+1}: {frame.function_name} ({frame.node_name})"
            )
            print(f"{indent}  Path: {' -> '.join(frame.node_path)}")
            print(
                f"{indent}  Input: {frame.user_input[:50]}{'...' if len(frame.user_input) > 50 else ''}"
            )
            print(f"{indent}  Context Fields: {frame.context_field_count}")
            print(f"{indent}  Timestamp: {frame.timestamp}")

            if frame.error_info:
                print(
                    f"{indent}  Error: {frame.error_info.get('message', 'Unknown error')}"
                )

            if include_context and frame.context_state:
                print(f"{indent}  Context State:")
                for key, data in frame.context_state.items():
                    print(f"{indent}    {key}: {data['value']}")

        print("=" * 60)

    def export_to_dict(self) -> Dict[str, Any]:
        """Export the stack context to a dictionary for serialization."""
        return {
            "session_id": self.context.session_id,
            "total_frames": len(self._frames),
            "current_frame_id": self._current_frame_id,
            "frames": [
                {
                    "frame_id": frame.frame_id,
                    "timestamp": frame.timestamp.isoformat(),
                    "function_name": frame.function_name,
                    "node_name": frame.node_name,
                    "node_path": frame.node_path,
                    "user_input": frame.user_input,
                    "parameters": frame.parameters,
                    "context_state": frame.context_state,
                    "context_field_count": frame.context_field_count,
                    "context_history_count": frame.context_history_count,
                    "context_error_count": frame.context_error_count,
                    "depth": frame.depth,
                    "parent_frame_id": frame.parent_frame_id,
                    "children_frame_ids": frame.children_frame_ids,
                    "execution_result": frame.execution_result,
                    "error_info": frame.error_info,
                }
                for frame in self._frames
            ],
            "summary": self.get_execution_summary(),
        }

    def get_error_count(self) -> int:
        """Get the total number of errors in the context."""
        return self.context.get_error_count()

    def add_error(
        self,
        node_name: str,
        user_input: str,
        error_message: str,
        error_type: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an error to the context error log."""
        self.context.add_error(node_name, user_input, error_message, error_type, params)

    def get_errors(
        self, node_name: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Any]:
        """Get errors from the context error log."""
        return self.context.get_errors(node_name, limit)

    def clear_errors(self) -> None:
        """Clear all errors from the context."""
        self.context.clear_errors()

    def get_history(
        self, key: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Any]:
        """Get the history of context operations."""
        return self.context.get_history(key, limit)

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
        """Track an operation in the context operation log."""
        self.context.track_operation(
            operation_type,
            success,
            node_name,
            user_input,
            duration,
            params,
            result,
            error_message,
        )

    def get_operations(
        self,
        operation_type: Optional[str] = None,
        node_name: Optional[str] = None,
        success: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[Any]:
        """Get operations from the context operation log."""
        return self.context.get_operations(operation_type, node_name, success, limit)

    def get_operation_stats(self) -> Dict[str, Any]:
        """Get comprehensive operation statistics."""
        return self.context.get_operation_stats()

    def clear_operations(self) -> None:
        """Clear all operations from the context."""
        self.context.clear_operations()

    def get_operation_count(self) -> int:
        """Get the total number of operations in the context."""
        return self.context.get_operation_count()
