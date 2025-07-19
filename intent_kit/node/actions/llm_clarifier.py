"""
LLM-powered clarifiers for intent-kit

This module provides LLM-powered clarification functions that can be used
with ClarifierNode to generate contextual clarification prompts.
"""






logger = Logger(__name__)

# Type alias for llm_config to support both dict and BaseLLMClient
LLMConfig = Union[Dict[str, Any], BaseLLMClient]


def create_llm_clarifier(
    llm_config: LLMConfig,
    clarification_prompt_template: str,
    expected_response_format: Optional[str] = None,
    max_clarification_attempts: int = 3,
) -> Callable[[str, Optional[Dict[str, Any]]], str]:
    """
    Create an LLM-powered clarifier function.

    Args:
        llm_config: LLM configuration or client instance
        clarification_prompt_template: Template for generating clarification prompts
        expected_response_format: Optional format specification for expected response
        max_clarification_attempts: Maximum number of clarification attempts

    Returns:
        Clarifier function that generates contextual clarification prompts
    """

    def llm_clarifier(
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        LLM-powered clarifier that generates contextual clarification prompts.

        Args:
            user_input: User's input text that needs clarification
            context: Optional context information to include in the prompt

        Returns:
            Generated clarification message
        """
        try:
            # Build context information for the prompt
            context_info = ""
            if context:
                context_info = "\n\nAvailable Context Information:\n"
                for key, value in context.items():
                    context_info += f"- {key}: {value}\n"
                context_info += "\nUse this context information to generate more relevant clarification prompts."

            # Build the clarification prompt
            prompt = clarification_prompt_template.format(
                user_input=user_input,
                context_info=context_info,
                expected_format=expected_response_format
                or "Please provide more specific details",
                max_attempts=max_clarification_attempts,
            )

            # Get LLM response
            if isinstance(llm_config, dict):
                # Obfuscate API key in debug log
                safe_config = llm_config.copy()
                if "api_key" in safe_config:
                    safe_config["api_key"] = "***OBFUSCATED***"
                logger.debug(f"LLM clarifier config: {safe_config}")
                logger.debug(f"LLM clarifier prompt: {prompt}")
                response = LLMFactory.generate_with_config(llm_config, prompt)
            else:
                # Use BaseLLMClient instance directly
                logger.debug(f"LLM clarifier using client: {type(llm_config).__name__}")
                logger.debug(f"LLM clarifier prompt: {prompt}")
                response = llm_config.generate(prompt)

            # Clean up the response
            clarification_message = response.strip()

            # Add expected format information if provided
            if expected_response_format:
                clarification_message += f"\n\nPlease provide your response in the following format: {expected_response_format}"

            logger.debug(f"LLM clarifier generated message: {clarification_message}")
            return clarification_message

        except Exception as e:
            logger.error(f"LLM clarification failed: {e}")
            # Fallback to a simple clarification message
            fallback_message = (
                f"Your request '{user_input}' is unclear. Please provide more details."
            )
            if expected_response_format:
                fallback_message += f"\n\nPlease provide your response in the following format: {expected_response_format}"
            return fallback_message

    return llm_clarifier


def get_default_clarification_prompt() -> str:
    """
    Get the default prompt template for LLM clarifiers.

    Returns:
        Default clarification prompt template
    """
    return """You are a helpful assistant that generates clarification prompts when user requests are unclear or incomplete.

User Input: {user_input}

{context_info}

Your task is to generate a helpful clarification prompt that:
1. Acknowledges the user's intent
2. Identifies what information is missing or unclear
3. Asks for the specific details needed
4. Provides guidance on the expected format

Expected Response Format: {expected_format}
Maximum Clarification Attempts: {max_attempts}

Generate a clear,
    helpful clarification prompt that will help the user provide the missing information. Be specific about what details are needed and why they're important.

Clarification Prompt:"""


def create_llm_clarifier_node(
    name: str,
    llm_config: LLMConfig,
    clarification_prompt_template: Optional[str] = None,
    expected_response_format: Optional[str] = None,
    max_clarification_attempts: int = 3,
    description: str = "",
):
    """
    Create a ClarifierNode with LLM-powered clarification.

    Args:
        name: Name of the clarifier node
        llm_config: LLM configuration or client instance
        clarification_prompt_template: Optional custom prompt template
        expected_response_format: Optional format specification for expected response
        max_clarification_attempts: Maximum number of clarification attempts
        description: Description of the clarifier

    Returns:
        Configured ClarifierNode with LLM-powered clarification
    """
    from .clarifier import ClarifierNode

    # Use default prompt if none provided
    if clarification_prompt_template is None:
        clarification_prompt_template = get_default_clarification_prompt()

    # Create the LLM clarifier function
    llm_clarifier_func = create_llm_clarifier(
        llm_config=llm_config,
        clarification_prompt_template=clarification_prompt_template,
        expected_response_format=expected_response_format,
        max_clarification_attempts=max_clarification_attempts,
    )

    # Create a custom ClarifierNode that uses the LLM clarifier
    class LLMClarifierNode(ClarifierNode):
        """ClarifierNode that uses LLM to generate contextual clarification prompts."""

        def __init__def __init__(self, llm_clarifier_func: Callable): -> None:
            super().__init__(
                name=name,
                clarification_prompt="",  # Will be generated by LLM
                expected_response_format=expected_response_format,
                max_clarification_attempts=max_clarification_attempts,
                description=description,
            )
            self.llm_clarifier_func = llm_clarifier_func

        def _build_clarification_message(self, user_input: str) -> str:
            """Build the clarification message using LLM."""
            return self.llm_clarifier_func(user_input)

    return LLMClarifierNode(llm_clarifier_func)
