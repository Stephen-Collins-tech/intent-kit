"""
Clarifier node implementation.

This module provides the ClarifierNode class which is a leaf node that
requests clarification from the user when input is ambiguous or underspecified.
"""


from ..base import TreeNode
from ..enums import NodeType
from ..types import ExecutionResult, ExecutionError



class ClarifierNode(TreeNode):
    """Leaf node that requests clarification when user input is ambiguous or underspecified."""

    def __init__(
        self,
        name: Optional[str],
        clarification_prompt: str,
        expected_response_format: Optional[str] = None,
        max_clarification_attempts: int = 3,
        description: str = "",
        parent: Optional["TreeNode"] = None,
    ):
        super().__init__(name=name, description=description, children=[], parent=parent)
        self.clarification_prompt = clarification_prompt
        self.expected_response_format = expected_response_format
        self.max_clarification_attempts = max_clarification_attempts

    @property
    def node_type(self) -> NodeType:
        """Get the type of this node."""
        return NodeType.CLARIFY

    def execute(
        self, user_input: str, context: Optional[IntentContext] = None
    ) -> ExecutionResult:
        """Execute the clarifier node to request more information from the user.

        This node always returns a clarification request, indicating that
        the flow should pause and wait for user input.
        """
        # Create clarification message
        clarification_message = self._build_clarification_message(user_input)

        # Store clarification context if available
        clarification_context = {
            "original_input": user_input,
            "clarification_prompt": self.clarification_prompt,
            "expected_format": self.expected_response_format,
            "attempts": 0,
            "max_attempts": self.max_clarification_attempts,
        }

        if context:
            context.set("clarification_context", clarification_context)

        return ExecutionResult(
            success=False,  # Clarification requests are not "successful" executions
            node_name=self.name,
            node_path=self.get_path(),
            node_type=NodeType.CLARIFY,
            input=user_input,
            output={
                "clarification_message": clarification_message,
                "clarification_context": clarification_context,
                "requires_clarification": True,
            },
            error=ExecutionError(
                error_type="ClarificationNeeded",
                message=f"Clarification needed for input: '{user_input}'",
                node_name=self.name,
                node_path=self.get_path(),
                input_data={"original_input": user_input},
                params={
                    "clarification_prompt": self.clarification_prompt,
                    "expected_format": self.expected_response_format,
                    "max_attempts": self.max_clarification_attempts,
                },
            ),
            params={
                "clarification_prompt": self.clarification_prompt,
                "expected_format": self.expected_response_format,
                "max_attempts": self.max_clarification_attempts,
            },
            children_results=[],
        )

    def _build_clarification_message(self, user_input: str) -> str:
        """Build the clarification message to send to the user."""
        message = self.clarification_prompt

        # Replace placeholders if they exist
        if "{input}" in message:
            message = message.replace("{input}", user_input)

        # Add expected format information if provided
        if self.expected_response_format:
            message += f"\n\nPlease provide your response in the following format: {self.expected_response_format}"

        return message

    def handle_clarification_response(
        self, clarification_response: str, context: Optional[IntentContext] = None
    ) -> Dict[str, Any]:
        """Handle the user's clarification response.

        This method should be called when the user provides additional information
        after a clarification request. It validates the response and prepares
        it for re-processing.
        """
        clarification_context = None
        if context:
            clarification_context = context.get("clarification_context")

        if clarification_context:
            clarification_context["attempts"] += 1
            clarification_context["last_response"] = clarification_response

            # Check if we've exceeded max attempts
            if (
                clarification_context["attempts"]
                >= clarification_context["max_attempts"]
            ):
                return {
                    "success": False,
                    "error": "Maximum clarification attempts exceeded",
                    "original_input": clarification_context["original_input"],
                    "attempts": clarification_context["attempts"],
                }

        # Return the clarified input for re-processing
        return {
            "success": True,
            "clarified_input": clarification_response,
            "original_input": (
                clarification_context["original_input"]
                if clarification_context
                else "unknown"
            ),
            "attempts": (
                clarification_context["attempts"] if clarification_context else 1
            ),
        }
