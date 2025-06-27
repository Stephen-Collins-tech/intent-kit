"""
LLM-powered classifiers for intent-kit

This module provides LLM-powered classification functions that can be used
with ClassifierNode and IntentNode.
"""

from typing import Dict, Any, List, Optional, Callable
from intent_kit.node import TaxonomyNode
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.utils.logger import Logger
import re

logger = Logger("llm_classifier")


def create_llm_classifier(
    llm_config: Dict[str, Any],
    classification_prompt: str,
    node_descriptions: List[str]
) -> Callable[[str, List[TaxonomyNode], Optional[Dict[str, Any]]], Optional[TaxonomyNode]]:
    """
    Create an LLM-powered classifier function.

    Args:
        llm_config: LLM configuration dictionary
        classification_prompt: Prompt template for classification
        node_descriptions: List of descriptions for each child node

    Returns:
        Classifier function that can be used with ClassifierNode
    """
    def llm_classifier(user_input: str, children: List[TaxonomyNode], context: Optional[Dict[str, Any]] = None) -> Optional[TaxonomyNode]:
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
                node_descriptions="\n".join([
                    f"{i+1}. {child.name}: {child.description}"
                    for i, child in enumerate(children)
                ]),
                num_nodes=len(children),
                context_info=context_info
            )

            # Get LLM response
            response = LLMFactory.generate_with_config(llm_config, prompt)

            # Parse the response to get the selected node index
            # Expect response to be a number (1-based index)
            try:
                # Try to extract just the number from the response
                response_text = response.strip()

                # Look for patterns like "Your choice (number only): 3" or "The choice is: 3"
                number_patterns = [
                    r'choice.*?(\d+)',
                    r'answer.*?(\d+)',
                    r'(\d+)',
                    r'number.*?(\d+)'
                ]

                selected_index = None
                for pattern in number_patterns:
                    match = re.search(pattern, response_text, re.IGNORECASE)
                    if match:
                        # Convert to 0-based
                        selected_index = int(match.group(1)) - 1
                        break

                # If no pattern matched, try to parse the entire response as a number
                if selected_index is None:
                    selected_index = int(response_text) - \
                        1  # Convert to 0-based

                if 0 <= selected_index < len(children):
                    logger.debug(
                        f"LLM classifier selected node {selected_index}: {children[selected_index].name}")
                    return children[selected_index]
                else:
                    logger.warning(
                        f"LLM returned invalid index: {selected_index}")
                    return None
            except ValueError:
                logger.warning(
                    f"LLM response could not be parsed as integer: {response}")
                return None

        except Exception as e:
            logger.error(f"LLM classifier error: {str(e)}")
            return None

    return llm_classifier


def create_llm_arg_extractor(
    llm_config: Dict[str, Any],
    extraction_prompt: str,
    param_schema: Dict[str, Any]
) -> Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]]:
    """
    Create an LLM-powered argument extractor function.

    Args:
        llm_config: LLM configuration dictionary
        extraction_prompt: Prompt template for argument extraction
        param_schema: Parameter schema defining expected parameters

    Returns:
        Argument extractor function that can be used with IntentNode
    """
    def llm_arg_extractor(user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
            param_descriptions = "\n".join([
                f"- {param_name}: {param_type.__name__}"
                for param_name, param_type in param_schema.items()
            ])

            prompt = extraction_prompt.format(
                user_input=user_input,
                param_descriptions=param_descriptions,
                param_names=", ".join(param_schema.keys()),
                context_info=context_info
            )

            # Get LLM response
            logger.debug(f"LLM arg extractor config: {llm_config}")
            logger.debug(f"LLM arg extractor prompt: {prompt}")
            response = LLMFactory.generate_with_config(llm_config, prompt)

            # Parse the response to extract parameters
            # For now, we'll use a simple approach - in the future this could be JSON parsing
            extracted_params = {}

            # Simple parsing: look for "param_name: value" patterns
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
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
