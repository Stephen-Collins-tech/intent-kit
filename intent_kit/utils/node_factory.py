"""
Node factory utilities for creating intent graph nodes.

This module provides factory functions for creating different types of nodes
with consistent patterns and common functionality.
"""

from typing import Any, Callable, List, Optional, Dict, Type, Set, Union, Sequence
from intent_kit.node import TreeNode
from intent_kit.node.classifiers import ClassifierNode
from intent_kit.node.actions import ActionNode, RemediationStrategy
from intent_kit.node.splitters import SplitterNode, rule_splitter, llm_splitter
from intent_kit.utils.logger import Logger
from intent_kit.types import IntentChunk
from intent_kit.graph import IntentGraph

# LLM classifier imports
from intent_kit.node.classifiers import (
    create_llm_classifier,
    get_default_classification_prompt,
)

# Utility imports
from intent_kit.utils.param_extraction import create_arg_extractor

logger = Logger("node_factory")


def set_parent_relationships(parent: TreeNode, children: List[TreeNode]) -> None:
    """Set parent-child relationships for a list of children.

    Args:
        parent: The parent node
        children: List of child nodes to set parent references for
    """
    for child in children:
        child.parent = parent


def create_action_node(
    *,
    name: str,
    description: str,
    action_func: Callable[..., Any],
    param_schema: Dict[str, Type],
    arg_extractor: Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]],
    context_inputs: Optional[Set[str]] = None,
    context_outputs: Optional[Set[str]] = None,
    input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
    output_validator: Optional[Callable[[Any], bool]] = None,
    remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = None,
) -> ActionNode:
    """Create an action node with the given configuration.

    Args:
        name: Name of the action node
        description: Description of what this action does
        action_func: Function to execute when this action is triggered
        param_schema: Dictionary mapping parameter names to their types
        arg_extractor: Function to extract parameters from user input
        context_inputs: Optional set of context keys this action reads from
        context_outputs: Optional set of context keys this action writes to
        input_validator: Optional function to validate extracted parameters
        output_validator: Optional function to validate action output
        remediation_strategies: Optional list of remediation strategies

    Returns:
        Configured ActionNode
    """
    return ActionNode(
        name=name,
        param_schema=param_schema,
        action=action_func,
        arg_extractor=arg_extractor,
        context_inputs=context_inputs,
        context_outputs=context_outputs,
        input_validator=input_validator,
        output_validator=output_validator,
        description=description,
        remediation_strategies=remediation_strategies,
    )


def create_classifier_node(
    *,
    name: str,
    description: str,
    classifier_func: Callable,
    children: List[TreeNode],
    remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = None,
) -> ClassifierNode:
    """Create a classifier node with the given configuration.

    Args:
        name: Name of the classifier node
        description: Description of the classifier
        classifier_func: Function to classify between children
        children: List of child nodes to classify between
        remediation_strategies: Optional list of remediation strategies

    Returns:
        Configured ClassifierNode
    """
    classifier_node = ClassifierNode(
        name=name,
        description=description,
        classifier=classifier_func,
        children=children,
        remediation_strategies=remediation_strategies,
    )

    # Set parent relationships
    set_parent_relationships(classifier_node, children)

    return classifier_node


def create_splitter_node(
    *,
    name: str,
    description: str,
    splitter_func: Callable,
    children: List[TreeNode],
    llm_client: Optional[Any] = None,
) -> SplitterNode:
    """Create a splitter node with the given configuration.

    Args:
        name: Name of the splitter node
        description: Description of the splitter
        splitter_func: Function to split intents
        children: List of child nodes to route to
        llm_client: Optional LLM client for LLM-based splitting

    Returns:
        Configured SplitterNode
    """
    splitter_node = SplitterNode(
        name=name,
        splitter_function=splitter_func,
        children=children,
        description=description,
        llm_client=llm_client,
    )

    # Set parent relationships
    set_parent_relationships(splitter_node, children)

    return splitter_node


def create_default_classifier() -> Callable:
    """Create a default classifier that returns the first child.

    Returns:
        Default classifier function
    """

    def default_classifier(
        user_input: str,
        children: List[TreeNode],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[TreeNode]:
        return children[0] if children else None

    return default_classifier


# High-level helper functions for creating nodes
def action(
    *,
    name: str,
    description: str,
    action_func: Callable[..., Any],
    param_schema: Dict[str, Type],
    llm_config: Optional[Dict[str, Any]] = None,
    extraction_prompt: Optional[str] = None,
    context_inputs: Optional[Set[str]] = None,
    context_outputs: Optional[Set[str]] = None,
    input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
    output_validator: Optional[Callable[[Any], bool]] = None,
    remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = None,
) -> TreeNode:
    """Create an action node with automatic argument extraction.

    Args:
        name: Name of the action node
        description: Description of what this action does
        action_func: Function to execute when this action is triggered
        param_schema: Dictionary mapping parameter names to their types
        llm_config: Optional LLM configuration for LLM-based argument extraction.
                   If not provided, uses a simple rule-based extractor.
        extraction_prompt: Optional custom prompt for LLM argument extraction
        context_inputs: Optional set of context keys this action reads from
        context_outputs: Optional set of context keys this action writes to
        input_validator: Optional function to validate extracted parameters
        output_validator: Optional function to validate action output
        remediation_strategies: Optional list of remediation strategies

    Returns:
        Configured ActionNode

    Example:
        >>> greet_action = action(
        ...     name="greet",
        ...     description="Greet the user",
        ...     action_func=lambda name: f"Hello {name}!",
        ...     param_schema={"name": str},
        ...     llm_config=LLM_CONFIG
        ... )
    """
    # Create argument extractor using shared utility
    arg_extractor = create_arg_extractor(
        param_schema=param_schema,
        llm_config=llm_config,
        extraction_prompt=extraction_prompt,
        node_name=name,
    )

    return create_action_node(
        name=name,
        description=description,
        action_func=action_func,
        param_schema=param_schema,
        arg_extractor=arg_extractor,
        context_inputs=context_inputs,
        context_outputs=context_outputs,
        input_validator=input_validator,
        output_validator=output_validator,
        remediation_strategies=remediation_strategies,
    )


def llm_classifier(
    *,
    name: str,
    children: List[TreeNode],
    llm_config: Dict[str, Any],
    classification_prompt: Optional[str] = None,
    description: str = "",
    remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = None,
) -> TreeNode:
    """Create an LLM-powered classifier node with auto-wired children descriptions.

    Args:
        name: Name of the classifier node
        children: List of child nodes to classify between
        llm_config: LLM configuration for classification
        classification_prompt: Optional custom classification prompt
        description: Optional description of the classifier

    Returns:
        Configured ClassifierNode with auto-wired children descriptions

    Example:
        >>> classifier = llm_classifier(
        ...     name="root",
        ...     children=[greet_action, calc_action, weather_action],
        ...     llm_config=LLM_CONFIG
        ... )
    """
    if not children:
        raise ValueError("llm_classifier requires at least one child node")

    # Auto-wire children descriptions for the classifier
    node_descriptions = []
    for child in children:
        if hasattr(child, "description") and child.description:
            node_descriptions.append(f"{child.name}: {child.description}")
        else:
            # Use name as fallback if no description
            node_descriptions.append(child.name)
            logger.warning(
                f"Child node '{child.name}' has no description, using name as fallback"
            )

    if not classification_prompt:
        classification_prompt = get_default_classification_prompt()

    classifier = create_llm_classifier(
        llm_config, classification_prompt, node_descriptions
    )

    return create_classifier_node(
        name=name,
        description=description,
        classifier_func=classifier,
        children=children,
        remediation_strategies=remediation_strategies,
    )


def llm_splitter_node(
    *,
    name: str,
    children: List[TreeNode],
    llm_config: Dict[str, Any],
    description: str = "",
) -> TreeNode:
    """Create an LLM-powered splitter node for multi-intent handling.

    Args:
        name: Name of the splitter node
        children: List of child nodes to route to
        llm_config: LLM configuration for splitting
        description: Optional description of the splitter

    Returns:
        Configured SplitterNode with LLM-powered splitting

    Example:
        >>> splitter = llm_splitter_node(
        ...     name="multi_intent_splitter",
        ...     children=[classifier_node],
        ...     llm_config=LLM_CONFIG
        ... )
    """

    # Create a wrapper function that provides the LLM client to llm_splitter
    def llm_splitter_wrapper(
        user_input: str, debug: bool = False
    ) -> Sequence[IntentChunk]:
        # Extract LLM client from config
        llm_client = llm_config.get("llm_client")
        return llm_splitter(user_input, debug, llm_client)

    return create_splitter_node(
        name=name,
        description=description,
        splitter_func=llm_splitter_wrapper,
        children=children,
        llm_client=llm_config.get("llm_client"),
    )


def rule_splitter_node(
    *, name: str, children: List[TreeNode], description: str = ""
) -> TreeNode:
    """Create a rule-based splitter node for multi-intent handling.

    Args:
        name: Name of the splitter node
        children: List of child nodes to route to
        description: Optional description of the splitter

    Returns:
        Configured SplitterNode with rule-based splitting

    Example:
        >>> splitter = rule_splitter_node(
        ...     name="rule_based_splitter",
        ...     children=[classifier_node],
        ... )
    """
    return create_splitter_node(
        name=name,
        description=description,
        splitter_func=rule_splitter,
        children=children,
    )


def create_intent_graph(root_node: TreeNode) -> "IntentGraph":
    """Create an IntentGraph with the given root node.

    Args:
        root_node: The root TreeNode for the graph

    Returns:
        Configured IntentGraph instance
    """
    from intent_kit.builders import IntentGraphBuilder

    return IntentGraphBuilder().root(root_node).build()


__all__ = [
    "set_parent_relationships",
    "create_action_node",
    "create_classifier_node",
    "create_splitter_node",
    "create_default_classifier",
    "action",
    "llm_classifier",
    "llm_splitter_node",
    "rule_splitter_node",
    "create_intent_graph",
]
