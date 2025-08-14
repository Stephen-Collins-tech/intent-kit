"""DAG ActionNode implementation for action execution."""

import time
from typing import Any, Callable, Dict, Optional, List
from intent_kit.core.types import NodeProtocol, ExecutionResult
from intent_kit.core.context import ContextProtocol
from intent_kit.utils.logger import Logger


class ActionNode(NodeProtocol):
    """Action node for DAG execution that uses parameters from context."""

    def __init__(
        self,
        name: str,
        action: Callable[..., Any],
        description: str = "",
        terminate_on_success: bool = True,
        param_key: str = "extracted_params",
        context_read: Optional[List[str]] = None,
        context_write: Optional[List[str]] = None,
        param_keys: Optional[List[str]] = None,
    ):
        """Initialize the DAG action node.

        Args:
            name: Node name
            action: Function to execute
            description: Node description
            terminate_on_success: Whether to terminate after successful execution
            param_key: Key in context to get parameters from
            context_read: List of context keys to read and pass to action
            context_write: List of context keys that the action will write
        """
        self.name = name
        self.action = action
        self.description = description
        self.terminate_on_success = terminate_on_success
        self.param_key = param_key
        self.context_read = context_read or []
        self.context_write = context_write or []
        # List of parameter keys to check
        self.param_keys = param_keys or [param_key]
        self.logger = Logger(name)

    def execute(self, user_input: str, ctx: ContextProtocol) -> ExecutionResult:
        """Execute the action node using parameters from context.

        Args:
            user_input: User input string (not used, parameters come from context)
            ctx: Execution context containing extracted parameters

        Returns:
            ExecutionResult with action results
        """
        # Get parameters from context
        params = self._get_params_from_context(ctx)

        # Read additional context values if specified
        context_values = {}
        for key in self.context_read:
            value = ctx.get(key)
            if value is not None:
                context_values[key] = value

        # The _get_params_from_context method now handles multiple parameter keys
        # including name_params, location_params, and extracted_params

        # Merge extracted params with context values
        all_params = {**params, **context_values}

        # Debug logging to see what parameters are being passed
        self.logger.info(f"Action parameters: {all_params}")
        self.logger.info(f"Context read keys: {self.context_read}")
        self.logger.info(f"Context values: {context_values}")

        # Execute the action with all parameters
        action_result = self.action(**all_params)

        # Create context patch with action result
        context_patch = {"action_result": action_result, "action_name": self.name}

        # Add context write operations if specified
        # For now, we'll write the extracted params to the specified context keys
        # In a more sophisticated implementation, the action could return a dict
        # with context updates
        for key in self.context_write:
            if key in all_params:
                context_patch[key] = all_params[key]
            elif key == "user.name" and "name" in all_params:
                # Special case: write extracted name to user.name
                context_patch[key] = all_params["name"]
            elif key == "user.first_seen" and "name" in all_params:
                # Special case: set first seen timestamp when name is extracted
                context_patch[key] = time.time()
            elif key == "weather.requests":
                # Special case: increment weather request counter
                current_count = ctx.get("weather.requests", 0)
                context_patch[key] = current_count + 1
            elif key == "weather.last_location" and "location" in all_params:
                # Special case: write extracted location to weather.last_location
                context_patch[key] = all_params["location"]

        return ExecutionResult(
            data=action_result,
            next_edges=["next"] if not self.terminate_on_success else None,
            terminate=self.terminate_on_success,
            metrics={},
            context_patch=context_patch,
        )

    @property
    def context_read_keys(self) -> List[str]:
        """List of context keys to read before execution."""
        return self.context_read

    @property
    def context_write_keys(self) -> List[str]:
        """List of context keys to write after execution."""
        return self.context_write

    def _get_params_from_context(self, ctx: Any) -> Dict[str, Any]:
        """Extract parameters from context."""
        if not ctx or not hasattr(ctx, "get"):
            self.logger.warning("No context available, using empty parameters")
            return {}

        # Merge parameters from all configured param_keys
        merged_params = {}

        # Try to get parameters from the configured param_key first
        params = ctx.get(self.param_key)
        if params is not None:
            if isinstance(params, dict):
                merged_params.update(params)
            else:
                self.logger.warning(
                    f"Parameters at '{self.param_key}' are not a dict: {type(params)}"
                )

        # If param_keys are configured, also check those
        for key in self.param_keys:
            if (
                key == self.param_key
            ):  # Skip the primary key since we already checked it
                continue
            params = ctx.get(key)
            if params is not None and isinstance(params, dict):
                self.logger.debug(
                    f"Found parameters in '{key}' instead of '{self.param_key}'"
                )
                merged_params.update(params)

        # Only warn if we couldn't find parameters in any of the expected locations
        if not merged_params:
            self.logger.debug(
                f"No parameters found in context for keys: {self.param_keys}"
            )

        return merged_params
