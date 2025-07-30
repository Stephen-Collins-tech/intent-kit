"""
LLM-powered classifiers for intent-kit

This module provides LLM-powered classification functions that can be used
with ClassifierNode and HandlerNode.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from intent_kit.services.base_client import BaseLLMClient
from intent_kit.services.llm_factory import LLMFactory
from intent_kit.utils.logger import Logger
from intent_kit.nodes.types import ExecutionResult, ExecutionError
from intent_kit.nodes.enums import NodeType
from ..base import TreeNode

logger = Logger(__name__)

# Type alias for llm_config to support both dict and BaseLLMClient
LLMConfig = Union[Dict[str, Any], BaseLLMClient]


def create_llm_classifier(
    llm_config: Optional[LLMConfig],
    classification_prompt: str,
    node_descriptions: List[str],
) -> Callable[[str, List["TreeNode"], Optional[Dict[str, Any]]], "ExecutionResult"]:
    """
    Create an LLM-powered classifier function.

    Args:
        llm_config: (Optional) LLM configuration or client instance. If None, the builder or graph should inject a default.
        classification_prompt: Prompt template for classification
        node_descriptions: List of descriptions for each child node

    Returns:
        Classifier function that returns an ExecutionResult with chosen_child parameter
    """

    def llm_classifier(
        user_input: str,
        children: List["TreeNode"],
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """
        LLM-powered classifier that determines which child node to execute.

        Args:
            user_input: User's input text
            children: List of available child nodes
            context: Optional context information to include in the prompt

        Returns:
            ExecutionResult with chosen_child parameter indicating which child to execute
        """
        logger.debug(f"LLM classifier input: {user_input}")
        if llm_config is None:
            return ExecutionResult(
                success=False,
                node_name="llm_classifier",
                node_path=[],
                node_type=NodeType.CLASSIFIER,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="ValueError",
                    message="No llm_config provided to LLM classifier. Please set a default on the graph or provide one at the node level.",
                    node_name="llm_classifier",
                    node_path=[],
                ),
                params=None,
                children_results=[],
            )

        try:
            # Build context information for the prompt
            context_info = ""
            if context:
                context_info = "\n\nAvailable Context Information:\n"
                for key, value in context.items():
                    context_info += f"- {key}: {value}\n"
                context_info += "\nUse this context information to help make more accurate classifications."

            # Build the classification prompt
            formatted_node_descriptions = "\n".join(
                [f"- {desc}" for desc in node_descriptions]
            )

            prompt = classification_prompt.format(
                user_input=user_input,
                node_descriptions=formatted_node_descriptions,
                context_info=context_info,
                num_nodes=len(children),
            )

            # Get LLM response
            if isinstance(llm_config, dict):
                # Obfuscate API key in debug log
                safe_config = llm_config.copy()
                if "api_key" in safe_config:
                    safe_config["api_key"] = "***OBFUSCATED***"
                logger.debug(f"LLM classifier config: {safe_config}")
                logger.debug(f"LLM classifier prompt: {prompt}")
                response = LLMFactory.generate_with_config(llm_config, prompt)
            else:
                # Use BaseLLMClient instance directly
                logger.debug(
                    f"LLM classifier using client: {type(llm_config).__name__}"
                )
                logger.debug(f"LLM classifier prompt: {prompt}")
                response = llm_config.generate(prompt)

            # Parse the response to get the selected node name
            selected_node_name = response.output.strip()
            logger.debug(f"LLM raw output: {response}")
            logger.debug(f"LLM classifier selected node: {selected_node_name}")
            logger.debug(f"LLM classifier children: {children}")

            # Find the child node with the matching name
            chosen_child = None
            for child in children:
                logger.debug(f"LLM classifier child in for loop: {child.name}")
                if child.name == selected_node_name:
                    logger.debug(
                        f"LLM classifier child in for loop found: {child.name}"
                    )
                    chosen_child = child
                    break

            # If no exact match, try partial matching
            if not chosen_child:
                for child in children:
                    if (
                        selected_node_name.lower() in child.name.lower()
                        or child.name.lower() in selected_node_name.lower()
                    ):
                        chosen_child = child
                        break

            # Create result with chosen child information
            available_children = [child.name for child in children]
            params = {
                "available_children": available_children,
                "chosen_child": chosen_child.name if chosen_child else None,
            }
            logger.debug(f"LLM classifier params: {params}")
            logger.debug(f"LLM classifier response: {response}")
            logger.debug(f"LLM classifier chosen child: {chosen_child}")

            if chosen_child:
                logger.debug(
                    f"RETURNING LLM classifier chosen child: {chosen_child}")
                logger.debug(
                    f"RETURNING LLM classifier chosen child.name: {chosen_child.name}"
                )
                logger.debug(
                    f"RETURNING LLM classifier chosen response.output: {response.output}"
                )
                logger.debug(
                    f"RETURNING LLM classifier chosen response.output_tokens: {response.output_tokens}"
                )
                logger.debug(
                    f"RETURNING LLM classifier chosen response.input_tokens: {response.input_tokens}"
                )
                return ExecutionResult(
                    success=True,
                    node_name="llm_classifier",
                    node_path=[],
                    node_type=NodeType.CLASSIFIER,
                    input=user_input,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    output=chosen_child.name.strip().replace("\n", ""),
                    error=None,
                    params=params,
                    children_results=[],
                )
            else:
                # If still no match, return error result
                logger.warning(
                    f"No child node found matching '{selected_node_name}'")
                return ExecutionResult(
                    success=False,
                    node_name="llm_classifier",
                    node_path=[],
                    node_type=NodeType.CLASSIFIER,
                    input=user_input,
                    output=None,
                    error=ExecutionError(
                        error_type="NoMatchFound",
                        message=f"No child node found matching '{selected_node_name}'",
                        node_name="llm_classifier",
                        node_path=[],
                    ),
                    params=params,
                    children_results=[],
                )

        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return ExecutionResult(
                success=False,
                node_name="llm_classifier",
                node_path=[],
                node_type=NodeType.CLASSIFIER,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type=type(e).__name__,
                    message=str(e),
                    node_name="llm_classifier",
                    node_path=[],
                ),
                params=None,
                children_results=[],
            )

    return llm_classifier


def create_llm_arg_extractor(
    llm_config: LLMConfig, extraction_prompt: str, param_schema: Dict[str, Any]
) -> Callable[[str, Optional[Dict[str, Any]]], Union[Dict[str, Any], ExecutionResult]]:
    """
    Create an LLM-powered argument extractor function.

    Args:
        llm_config: LLM configuration or client instance
        extraction_prompt: Prompt template for argument extraction
        param_schema: Parameter schema defining expected parameters

    Returns:
        Argument extractor function that can be used with HandlerNode
    """

    def llm_arg_extractor(
        user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], ExecutionResult]:
        """
        LLM-powered argument extractor that extracts parameters from user input.

        Args:
            user_input: User's input text
            context: Optional context information to include in the prompt

        Returns:
            Dictionary of extracted parameters or ExecutionResult with token info
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
            if isinstance(llm_config, dict):
                safe_config = llm_config.copy()
                if "api_key" in safe_config:
                    safe_config["api_key"] = "***OBFUSCATED***"
                logger.debug(f"LLM arg extractor config: {safe_config}")
                logger.debug(f"LLM arg extractor prompt: {prompt}")
                response = LLMFactory.generate_with_config(llm_config, prompt)
            else:
                # Use BaseLLMClient instance directly
                logger.debug(
                    f"LLM arg extractor using client: {type(llm_config).__name__}"
                )
                logger.debug(f"LLM arg extractor prompt: {prompt}")
                response = llm_config.generate(prompt)

            # Parse the response to extract parameters
            # For now, we'll use a simple approach - in the future this could be JSON parsing
            extracted_params = {}

            # Simple parsing: look for "param_name: value" patterns
            lines = response.output.strip().split("\n")
            for line in lines:
                line = line.strip()
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        param_name = parts[0].strip()
                        param_value = parts[1].strip()
                        if param_name in param_schema:
                            extracted_params[param_name] = param_value

            logger.debug(f"Extracted parameters: {extracted_params}")

            # Return ExecutionResult with token information
            return ExecutionResult(
                success=True,
                node_name="llm_arg_extractor",
                node_path=[],
                node_type=NodeType.ACTION,  # This is used in action context
                input=user_input,
                output=extracted_params,
                error=None,
                params=extracted_params,
                children_results=[],
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost=response.cost,
                provider=response.provider,
                model=response.model,
                duration=response.duration,
            )

        except Exception as e:
            logger.error(f"LLM argument extraction failed: {e}")
            raise

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
