"""
LLM-powered classifiers for intent-kit

This module provides LLM-powered classification functions that can be used
with ClassifierNode and HandlerNode.
"""

from typing import Dict, Any, List, Optional, Callable
from ..base import TreeNode
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.utils.logger import Logger
import re

logger = Logger("llm_classifier")


def create_llm_classifier(
    llm_config: Dict[str, Any], classification_prompt: str, node_descriptions: List[str]
) -> Callable[[str, List[TreeNode], Optional[Dict[str, Any]]], Optional[TreeNode]]:
    """
    Create an LLM-powered classifier function.

    Args:
        llm_config: LLM configuration dictionary
        classification_prompt: Prompt template for classification
        node_descriptions: List of descriptions for each child node

    Returns:
        Classifier function that can be used with ClassifierNode
    """

    def llm_classifier(
        user_input: str,
        children: List[TreeNode],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[TreeNode]:
        """
        LLM-powered classifier that selects the most appropriate child node.

        Args:
            user_input: User's input text
            children: List of available child nodes
            context: Optional context information to include in the prompt

        Returns:
            Selected child node or None if no match
        """
        try:
            # Build context information for the prompt
            context_info = ""
            if context:
                context_info = "\n\nAvailable Context Information:\n"
                for key, value in context.items():
                    context_info += f"- {key}: {value}\n"
                context_info += "\nUse this context information to make better classification decisions."

            # Build the classification prompt
            prompt = classification_prompt.format(
                user_input=user_input,
                node_descriptions="\n".join(
                    [
                        f"{i}. {child.name}: {child.description}"
                        for i, child in enumerate(children)
                    ]
                ),
                num_nodes=len(children),
                context_info=context_info,
            )

            # Get LLM response
            response = LLMFactory.generate_with_config(llm_config, prompt)

            # Parse the response to get the selected node index
            # Expect response to be a number (1-based index)
            try:
                # Try to extract just the number from the response
                response_text = response.strip()

                # Look for patterns like "Your choice (number only): 3" or "The choice is: 3"
                # Make patterns more specific to avoid matching context numbers like years/timestamps

                logger.debug(
                    f"Response text BEFORE SELECTED_INDEX PROBLEM: {response_text}"
                )
                selected_index = None
                match = re.search(
                    r"^(\d{1,2})\s*$", response_text, re.IGNORECASE | re.MULTILINE
                )
                logger.debug(f"Match: {match}")
                if match:
                    # Parse the number and validate it's in the correct range
                    parsed_number = int(match.group(1))
                    logger.debug(
                        f"LLM returned number: {parsed_number} (response: {response_text})"
                    )
                    logger.debug(f"Children: {[child.name for child in children]}")
                    logger.debug(f"Selected index: {selected_index}")

                    selected_index = parsed_number
                    logger.debug(f"Selected index after assignment: {selected_index}")
                else:
                    logger.debug(f"No number pattern matched: {response_text}")

                # If no pattern matched, try to parse the entire response as a number
                if selected_index is None:
                    # Clean up the response text - remove markdown formatting, asterisks, etc.
                    cleaned_text = re.sub(r"[^\d]", "", response_text)
                    if cleaned_text:
                        # Only take the first 1-2 digits to avoid long numbers like years
                        first_digits = cleaned_text[:2]
                        if first_digits.isdigit():
                            parsed_number = int(first_digits)

                            # Handle both 0-based and 1-based indexing
                            if parsed_number == 0:
                                # If LLM returns 0, treat it as "no valid choice" unless it's the only option
                                if len(children) == 1:
                                    selected_index = 0  # Only option
                                else:
                                    selected_index = None  # No valid choice
                            elif parsed_number >= 1 and parsed_number <= len(children):
                                # Convert 1-based to 0-based
                                selected_index = parsed_number - 1
                            else:
                                # Invalid number
                                selected_index = None

                if selected_index is not None and 0 <= selected_index < len(children):
                    return children[selected_index]
                else:
                    logger.warning(
                        f"LLM returned invalid index: {selected_index} (valid range: 0-{len(children)-1})"
                    )
                    logger.warning(
                        f"Available children: {[child.name for child in children]}"
                    )
                    logger.warning(f"Raw LLM response: {response_text}")
                    return None
            except ValueError as e:
                logger.warning(
                    f"LLM response could not be parsed as integer: {response}"
                )
                logger.warning(f"Parse error: {e}")
                return None

        except Exception as e:
            logger.error(f"LLM classifier error: {str(e)}")
            return None

    return llm_classifier


def create_llm_arg_extractor(
    llm_config: Dict[str, Any], extraction_prompt: str, param_schema: Dict[str, Any]
) -> Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]]:
    """
    Create an LLM-powered argument extractor function.

    Args:
        llm_config: LLM configuration dictionary
        extraction_prompt: Prompt template for argument extraction
        param_schema: Parameter schema defining expected parameters

    Returns:
        Argument extractor function that can be used with HandlerNode
    """

    def llm_arg_extractor(
        user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        LLM-powered argument extractor that extracts parameters from user input.

        Args:
            user_input: User's input text
            context: Optional context information to include in the prompt

        Returns:
            Dictionary of extracted parameters
        """
        try:
            # Build context information for the prompt
            context_info = ""
            if context:
                context_info = "\n\nAvailable Context Information:\n"
                for key, value in context.items():
                    context_info += f"- {key}: {value}\n"
                context_info += "\nUse this context information to help extract more accurate parameters."

            # Build the extraction prompt
            logger.debug(f"LLM arg extractor param_schema: {param_schema}")
            logger.debug(
                f"LLM arg extractor param_schema types: {[(name, type(param_type)) for name, param_type in param_schema.items()]}"
            )

            param_descriptions = "\n".join(
                [
                    f"- {param_name}: {param_type.__name__ if hasattr(param_type, '__name__') else str(param_type)}"
                    for param_name, param_type in param_schema.items()
                ]
            )

            prompt = extraction_prompt.format(
                user_input=user_input,
                param_descriptions=param_descriptions,
                param_names=", ".join(param_schema.keys()),
                context_info=context_info,
            )

            # Get LLM response
            # Obfuscate API key in debug log
            safe_config = llm_config.copy()
            if "api_key" in safe_config:
                safe_config["api_key"] = "***OBFUSCATED***"
            logger.debug(f"LLM arg extractor config: {safe_config}")
            logger.debug(f"LLM arg extractor prompt: {prompt}")
            response = LLMFactory.generate_with_config(llm_config, prompt)

            # Parse the response to extract parameters
            # For now, we'll use a simple approach - in the future this could be JSON parsing
            extracted_params = {}

            # Simple parsing: look for "param_name: value" patterns
            lines = response.strip().split("\n")
            for line in lines:
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key in param_schema:
                        extracted_params[key] = value

            logger.debug(f"LLM arg extractor extracted: {extracted_params}")
            return extracted_params

        except Exception as e:
            logger.error(f"LLM arg extractor error: {str(e)}")
            return {}

    return llm_arg_extractor


def get_default_classification_prompt() -> str:
    """Get the default classification prompt template."""
    return """You are an intent classifier. Given a user input, select the most appropriate intent from the available options.

User Input: {user_input}

Available Intents:
{node_descriptions}

{context_info}

Instructions:
- Analyze the user input carefully
- Consider the available context information when making your decision
- Select the intent that best matches the user's request
- Return only the number (1-{num_nodes}) corresponding to your choice
- If no intent matches, return 0

Your choice (number only):"""


def get_default_extraction_prompt() -> str:
    """Get the default argument extraction prompt template."""
    return """You are a parameter extractor. Given a user input, extract the required parameters.

User Input: {user_input}

Required Parameters:
{param_descriptions}

{context_info}

Instructions:
- Extract the required parameters from the user input
- Consider the available context information to help with extraction
- Return each parameter on a new line in the format: "param_name: value"
- If a parameter is not found, use a reasonable default or empty string
- Be specific and accurate in your extraction

Extracted Parameters:
"""
