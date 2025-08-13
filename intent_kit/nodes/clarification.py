"""DAG ClarificationNode implementation for user clarification."""

from typing import Any, Dict, Optional
from intent_kit.core.types import NodeProtocol, ExecutionResult
from intent_kit.core.context import ContextProtocol
from intent_kit.utils.logger import Logger
from intent_kit.utils.type_coercion import validate_raw_content


class ClarificationNode(NodeProtocol):
    """A node that handles unclear user intent by asking for clarification.

    This node is typically reached when a classifier cannot determine the user's intent.
    It provides a helpful message asking the user to clarify their request.
    """

    def __init__(
        self,
        name: str,
        clarification_message: Optional[str] = None,
        available_options: Optional[list[str]] = None,
        description: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        custom_prompt: Optional[str] = None,
    ):
        """Initialize the clarification node.

        Args:
            name: Name of the node
            clarification_message: Custom message to ask for clarification
            available_options: List of available options to suggest to the user
            description: Description of the node's purpose
            llm_config: LLM configuration for generating contextual clarification messages
            custom_prompt: Custom prompt for generating clarification messages
        """
        self.name = name
        self.clarification_message = clarification_message
        self.available_options = available_options or []
        self.description = description or "Ask user to clarify their intent"
        self.llm_config = llm_config or {}
        self.custom_prompt = custom_prompt
        self.logger = Logger(name)

    def _default_message(self) -> str:
        """Generate a default clarification message."""
        return (
            "I'm not sure what you'd like me to do. "
            "Could you please clarify your request?"
        )

    def execute(self, user_input: str, ctx: ContextProtocol) -> ExecutionResult:
        """Execute the clarification node.

        Args:
            user_input: The original user input that was unclear
            ctx: The execution context

        Returns:
            ExecutionResult with clarification message and termination flag
        """
        # Generate clarification message using LLM if configured
        if self.llm_config and self.custom_prompt:
            clarification_text = self._generate_clarification_with_llm(user_input, ctx)
        else:
            # Use static message
            clarification_text = self._format_message()

        # Context information will be added via context_patch

        return ExecutionResult(
            data={
                "clarification_message": clarification_text,
                "original_input": user_input,
                "available_options": self.available_options,
                "node_type": "clarification",
            },
            next_edges=None,  # Terminate the DAG
            terminate=True,
            metrics={},
            context_patch={
                "clarification_requested": True,
                "original_input": user_input,
                "available_options": self.available_options,
                "clarification_message": clarification_text,
            },
        )

    def _generate_clarification_with_llm(self, user_input: str, ctx: Any) -> str:
        """Generate a contextual clarification message using LLM."""
        try:
            # Get LLM service from context
            llm_service = ctx.get("llm_service") if hasattr(ctx, "get") else None

            if not llm_service or not self.llm_config:
                self.logger.warning("LLM service not available, using static message")
                return self._format_message()

            # Build prompt for clarification
            prompt = self._build_clarification_prompt(user_input, ctx)

            # Get model from config or use default
            model = self.llm_config.get("model", "gpt-3.5-turbo")

            # Get client from shared service
            llm_client = llm_service.get_client(self.llm_config)

            # Get raw response
            raw_response = llm_client.generate(prompt, model=model)

            # Parse the response using the validation utility
            clarification_text = validate_raw_content(raw_response.content, str)

            self.logger.info(f"Generated clarification message: {clarification_text}")
            return clarification_text

        except Exception as e:
            self.logger.error(f"LLM clarification generation failed: {e}")
            return self._format_message()

    def _build_clarification_prompt(self, user_input: str, ctx: Any) -> str:
        """Build the clarification prompt."""
        if self.custom_prompt:
            return self.custom_prompt.format(user_input=user_input)

        # Build context info
        context_info = ""
        if ctx and hasattr(ctx, "snapshot"):
            context_data = ctx.snapshot()
            if context_data:
                context_info = f"\nAvailable Context:\n{context_data}"

        # Build available options text
        options_text = ""
        if self.available_options:
            options_text = "\n".join(f"- {option}" for option in self.available_options)

        return f"""You are a helpful assistant that asks for clarification when user intent is unclear.

User Input: {user_input}

Clarification Task: {self.name}
Description: {self.description}

{context_info}

Available Options:
{options_text}

Instructions:
- Generate a helpful clarification message
- Be polite and specific about what you need to know
- Reference the available options if provided
- Keep the message concise but informative
- Ask for specific information that would help clarify the user's intent

Generate a clarification message:"""

    def _format_message(self) -> str:
        """Format the clarification message with available options if provided."""
        # Use custom message if provided, otherwise use default
        message = self.clarification_message or self._default_message()

        if not self.available_options:
            return message

        options_text = "\n".join(f"- {option}" for option in self.available_options)
        return f"{message}\n\nAvailable options:\n{options_text}"
