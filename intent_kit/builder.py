from typing import Any, Callable, List, Optional, Dict, Type, Set, Sequence, Union
from .node import TreeNode
from .classifiers import ClassifierNode
from .splitters import SplitterNode
from .handlers import HandlerNode
from .classifiers.llm_classifier import (
    create_llm_classifier,
    create_llm_arg_extractor,
    get_default_classification_prompt,
    get_default_extraction_prompt,
)
from .types import IntentChunk
from .graph import IntentGraph
from .utils.logger import Logger

# Import splitter functions for builder methods
from .splitters.functions import rule_splitter, llm_splitter
from .handlers.remediation import RemediationStrategy


logger = Logger("builder")


class IntentGraphBuilder:
    """Builder class for creating IntentGraph instances with a fluent interface."""

    def __init__(self):
        self._root_node: Optional[TreeNode] = None
        self._splitter = None
        self._debug_context = False
        self._context_trace = False

    def root(self, node: TreeNode) -> "IntentGraphBuilder":
        """Set the root node for the intent graph.

        Args:
            node: The root TreeNode to use for the graph

        Returns:
            Self for method chaining
        """
        self._root_node = node
        return self

    def splitter(self, splitter_func) -> "IntentGraphBuilder":
        """Set a custom splitter function for the intent graph.

        Args:
            splitter_func: Function to use for splitting intents

        Returns:
            Self for method chaining
        """
        self._splitter = splitter_func
        return self

    def build(self) -> IntentGraph:
        """Build and return the IntentGraph instance.

        Returns:
            Configured IntentGraph instance

        Raises:
            ValueError: If no root node has been set
        """
        if self._root_node is None:
            raise ValueError("No root node set. Call .root() before .build()")

        if self._splitter:
            graph = IntentGraph(
                splitter=self._splitter,
                debug_context=self._debug_context,
                context_trace=self._context_trace,
            )
        else:
            graph = IntentGraph(
                debug_context=self._debug_context, context_trace=self._context_trace
            )
        graph.add_root_node(self._root_node)
        return graph

    def debug_context(self, enabled: bool = True) -> "IntentGraphBuilder":
        """Enable context debugging for the intent graph.

        Args:
            enabled: Whether to enable context debugging

        Returns:
            Self for method chaining
        """
        self._debug_context = enabled
        return self

    def context_trace(self, enabled: bool = True) -> "IntentGraphBuilder":
        """Enable detailed context tracing for the intent graph.

        Args:
            enabled: Whether to enable context tracing

        Returns:
            Self for method chaining
        """
        self._context_trace = enabled
        return self


def handler(
    *,
    name: str,
    description: str,
    handler_func: Callable[..., Any],
    param_schema: Dict[str, Type],
    llm_config: Optional[Dict[str, Any]] = None,
    extraction_prompt: Optional[str] = None,
    context_inputs: Optional[Set[str]] = None,
    context_outputs: Optional[Set[str]] = None,
    input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
    output_validator: Optional[Callable[[Any], bool]] = None,
    remediation_strategies: Optional[List[Union[str, "RemediationStrategy"]]] = None,
) -> TreeNode:
    """Create a handler node with automatic argument extraction.

    Args:
        name: Name of the handler node
        description: Description of what this handler does
        handler_func: Function to execute when this handler is triggered
        param_schema: Dictionary mapping parameter names to their types
        llm_config: Optional LLM configuration for LLM-based argument extraction.
                   If not provided, uses a simple rule-based extractor.
        extraction_prompt: Optional custom prompt for LLM argument extraction
        context_inputs: Optional set of context keys this handler reads from
        context_outputs: Optional set of context keys this handler writes to
        input_validator: Optional function to validate extracted parameters
        output_validator: Optional function to validate handler output

    Returns:
        Configured HandlerNode

    Example:
        >>> greet_handler = handler(
        ...     name="greet",
        ...     description="Greet the user",
        ...     handler_func=lambda name: f"Hello {name}!",
        ...     param_schema={"name": str},
        ...     llm_config=LLM_CONFIG
        ... )
    """
    # Create argument extractor based on configuration
    if llm_config:
        # Use LLM-based extraction
        if not extraction_prompt:
            extraction_prompt = get_default_extraction_prompt()

        arg_extractor = create_llm_arg_extractor(
            llm_config, extraction_prompt, param_schema
        )
    else:
        # Use simple rule-based extraction as fallback
        def simple_arg_extractor(
            text: str, context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Simple rule-based argument extractor."""
            extracted = {}

            # For each parameter, try to extract it using simple rules
            for param_name, param_type in param_schema.items():
                if isinstance(param_type, type) and param_type is str:
                    # For string parameters, try to find relevant text
                    if param_name.lower() in ["name", "location", "operation"]:
                        # Extract the last word as a simple heuristic
                        words = text.split()
                        if words:
                            extracted[param_name] = words[-1]
                    else:
                        # Default: use the entire text for string params
                        extracted[param_name] = text.strip()
                elif isinstance(param_type, type) and param_type in [int, float]:
                    # For numeric parameters, try to find numbers in text
                    import re

                    numbers = re.findall(r"\d+(?:\.\d+)?", text)
                    if numbers:
                        try:
                            extracted[param_name] = param_type(numbers[0])
                        except (ValueError, IndexError):
                            # Use default values for common parameters
                            if param_name in ["a", "first"]:
                                extracted[param_name] = param_type(10)
                            elif param_name in ["b", "second"]:
                                extracted[param_name] = param_type(5)
                            else:
                                extracted[param_name] = param_type(0)
                    else:
                        # Use default values
                        if param_name in ["a", "first"]:
                            extracted[param_name] = param_type(10)
                        elif param_name in ["b", "second"]:
                            extracted[param_name] = param_type(5)
                        else:
                            extracted[param_name] = param_type(0)
                else:
                    # For other types, use a default value
                    if isinstance(param_type, type) and param_type is bool:
                        extracted[param_name] = True  # type: ignore
                    else:
                        extracted[param_name] = None  # type: ignore

            return extracted

        arg_extractor = simple_arg_extractor

    return HandlerNode(
        name=name,
        param_schema=param_schema,
        handler=handler_func,
        arg_extractor=arg_extractor,
        context_inputs=context_inputs,
        context_outputs=context_outputs,
        input_validator=input_validator,
        output_validator=output_validator,
        description=description,
        remediation_strategies=remediation_strategies,
    )


def llm_classifier(
    *,
    name: str,
    children: List[TreeNode],
    llm_config: Dict[str, Any],
    classification_prompt: Optional[str] = None,
    description: str = "",
    remediation_strategies: Optional[List[Union[str, "RemediationStrategy"]]] = None,
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
        ...     children=[greet_handler, calc_handler, weather_handler],
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

    classifier_node = ClassifierNode(
        name=name,
        classifier=classifier,
        children=children,
        description=description,
        remediation_strategies=remediation_strategies,
    )

    # Set parent reference for all children to this classifier node
    for child in children:
        child.parent = classifier_node

    return classifier_node


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

    splitter_node = SplitterNode(
        name=name,
        splitter_function=llm_splitter_wrapper,
        children=children,
        description=description,
        llm_client=llm_config.get("llm_client"),
    )

    # Set parent reference for all children to this splitter node
    for child in children:
        child.parent = splitter_node

    return splitter_node


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
    splitter_node = SplitterNode(
        name=name,
        splitter_function=rule_splitter,
        children=children,
        description=description,
    )

    # Set parent reference for all children to this splitter node
    for child in children:
        child.parent = splitter_node

    return splitter_node


# Convenience function for creating a complete graph
def create_intent_graph(root_node: TreeNode) -> IntentGraph:
    """Create an IntentGraph with the given root node.

    Args:
        root_node: The root TreeNode for the graph

    Returns:
        Configured IntentGraph instance
    """
    return IntentGraphBuilder().root(root_node).build()
