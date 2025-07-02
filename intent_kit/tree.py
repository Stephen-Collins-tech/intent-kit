from typing import Any, Callable, List, Optional, Dict, Type, Set, Sequence
from .node import TreeNode
from .classifiers import ClassifierNode
from .splitters import SplitterNode
from .handlers import HandlerNode
from .classifiers.llm_classifier import (
    create_llm_classifier,
    create_llm_arg_extractor,
    get_default_classification_prompt,
    get_default_extraction_prompt
)
from .splitters import rule_splitter, llm_splitter
from .types import IntentChunk


class TreeBuilder:
    """Utility class for building intent trees."""

    @staticmethod
    def handler_node(
        *,
        name: Optional[str] = None,
        param_schema: Dict[str, Type],
        handler: Callable[..., Any],
        arg_extractor: Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]],
        context_inputs: Optional[Set[str]] = None,
        context_outputs: Optional[Set[str]] = None,
        input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
        output_validator: Optional[Callable[[Any], bool]] = None,
        description: str = "",
        parent: Optional[TreeNode] = None
    ) -> HandlerNode:
        """Create a new Handler node."""
        return HandlerNode(
            name,
            param_schema,
            handler,
            arg_extractor,
            context_inputs,
            context_outputs,
            input_validator,
            output_validator,
            description,
            parent
        )

    @staticmethod
    def llm_handler_node(
        *,
        name: Optional[str] = None,
        param_schema: Dict[str, Type],
        handler: Callable[..., Any],
        llm_config: Dict[str, Any],
        context_inputs: Optional[Set[str]] = None,
        context_outputs: Optional[Set[str]] = None,
        extraction_prompt: Optional[str] = None,
        input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
        output_validator: Optional[Callable[[Any], bool]] = None,
        description: str = "",
        parent: Optional[TreeNode] = None
    ) -> HandlerNode:
        """Create a new Handler node with LLM-powered argument extraction."""
        if not extraction_prompt:
            extraction_prompt = get_default_extraction_prompt()

        arg_extractor = create_llm_arg_extractor(
            llm_config, extraction_prompt, param_schema)

        return HandlerNode(
            name,
            param_schema,
            handler,
            arg_extractor,
            context_inputs,
            context_outputs,
            input_validator,
            output_validator,
            description,
            parent
        )

    @staticmethod
    def classifier_node(
        *,
        name: Optional[str] = None,
        classifier: Callable[[str, List[TreeNode], Optional[Dict[str, Any]]], Optional[TreeNode]],
        children: List[TreeNode],
        description: str = "",
        parent: Optional[TreeNode] = None
    ) -> ClassifierNode:
        """Create a new ClassifierNode."""
        classifier_node = ClassifierNode(
            name, classifier, children, description, parent)

        # Set parent reference for all children to this classifier node
        for child in children:
            child.parent = classifier_node

        return classifier_node

    @staticmethod
    def llm_classifier_node(
        *,
        name: Optional[str] = None,
        children: List[TreeNode],
        llm_config: Dict[str, Any],
        classification_prompt: Optional[str] = None,
        description: str = "",
        parent: Optional[TreeNode] = None
    ) -> ClassifierNode:
        """Create a new ClassifierNode with LLM-powered classification."""
        if not classification_prompt:
            classification_prompt = get_default_classification_prompt()

        # Get descriptions from children for the prompt
        node_descriptions = [child.description for child in children]

        classifier = create_llm_classifier(
            llm_config, classification_prompt, node_descriptions)

        classifier_node = ClassifierNode(
            name, classifier, children, description, parent)

        # Set parent reference for all children to this classifier node
        for child in children:
            child.parent = classifier_node

        return classifier_node

    @staticmethod
    def splitter_node(
        *,
        name: Optional[str] = None,
        splitter_function: Callable[[str, bool], Sequence[IntentChunk]],
        children: List[TreeNode],
        description: str = "",
        parent: Optional[TreeNode] = None,
        llm_client=None
    ) -> SplitterNode:
        """Create a new SplitterNode with a custom splitter function."""
        splitter_node = SplitterNode(
            name, splitter_function, children, description, parent, llm_client)

        # Set parent reference for all children to this splitter node
        for child in children:
            child.parent = splitter_node

        return splitter_node

    @staticmethod
    def rule_splitter_node(
        *,
        name: Optional[str] = None,
        children: List[TreeNode],
        description: str = "",
        parent: Optional[TreeNode] = None
    ) -> SplitterNode:
        """Create a new SplitterNode using rule-based splitting."""
        splitter_node = SplitterNode(
            name, rule_splitter, children, description, parent)

        # Set parent reference for all children to this splitter node
        for child in children:
            child.parent = splitter_node

        return splitter_node

    @staticmethod
    def llm_splitter_node(
        *,
        name: Optional[str] = None,
        children: List[TreeNode],
        llm_config: Dict[str, Any],
        description: str = "",
        parent: Optional[TreeNode] = None
    ) -> SplitterNode:
        """Create a new SplitterNode with LLM-powered splitting."""
        # Create a wrapper function that provides the LLM client to llm_splitter
        def llm_splitter_wrapper(user_input: str, debug: bool = False) -> Sequence[IntentChunk]:
            # Extract LLM client from config
            llm_client = llm_config.get('llm_client')
            return llm_splitter(user_input, debug, llm_client)

        splitter_node = SplitterNode(
            name, llm_splitter_wrapper, children, description, parent,
            llm_client=llm_config.get('llm_client'))

        # Set parent reference for all children to this splitter node
        for child in children:
            child.parent = splitter_node

        return splitter_node
