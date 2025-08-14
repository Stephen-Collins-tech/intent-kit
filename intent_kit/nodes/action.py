"""DAG ActionNode implementation for action execution."""

from typing import Any, Callable, Dict
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
    ):
        """Initialize the DAG action node.

        Args:
            name: Node name
            action: Function to execute
            description: Node description
            terminate_on_success: Whether to terminate after successful execution
            param_key: Key in context to get parameters from
        """
        self.name = name
        self.action = action
        self.description = description
        self.terminate_on_success = terminate_on_success
        self.param_key = param_key
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

        # Execute the action with parameters
        action_result = self.action(**params)

        return ExecutionResult(
            data=action_result,
            next_edges=["next"] if not self.terminate_on_success else None,
            terminate=self.terminate_on_success,
            metrics={},
            context_patch={"action_result": action_result, "action_name": self.name},
        )

    def _get_params_from_context(self, ctx: Any) -> Dict[str, Any]:
        """Extract parameters from context."""
        if not ctx or not hasattr(ctx, "get"):
            self.logger.warning("No context available, using empty parameters")
            return {}

        # Get parameters directly from context using the param_key
        params = ctx.get(self.param_key)
        if params is not None:
            if isinstance(params, dict):
                return params
            else:
                self.logger.warning(
                    f"Parameters at '{self.param_key}' are not a dict: {type(params)}"
                )
                return {}

        self.logger.warning(f"Parameter key '{self.param_key}' not found in context")
        return {}
