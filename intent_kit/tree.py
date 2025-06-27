from typing import Any, Callable, List, Optional, Dict, Type, Set
from .node import IntentNode, ClassifierNode, TaxonomyNode
from .classifiers.llm_classifier import (
    create_llm_classifier,
    create_llm_arg_extractor,
    get_default_classification_prompt,
    get_default_extraction_prompt
)


class TreeBuilder:
    """Utility class for building intent taxonomy trees."""

    @staticmethod
    def intent_node(
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
        parent: Optional[TaxonomyNode] = None
    ) -> IntentNode:
        """Create a new Intent node."""
        return IntentNode(
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
    def llm_intent_node(
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
        parent: Optional[TaxonomyNode] = None
    ) -> IntentNode:
        """Create a new Intent node with LLM-powered argument extraction."""
        if not extraction_prompt:
            extraction_prompt = get_default_extraction_prompt()

        arg_extractor = create_llm_arg_extractor(
            llm_config, extraction_prompt, param_schema)

        return IntentNode(
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
        classifier: Callable[[str, List[TaxonomyNode], Optional[Dict[str, Any]]], Optional[TaxonomyNode]],
        children: List[TaxonomyNode],
        description: str = "",
        parent: Optional[TaxonomyNode] = None
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
        children: List[TaxonomyNode],
        llm_config: Dict[str, Any],
        classification_prompt: Optional[str] = None,
        description: str = "",
        parent: Optional[TaxonomyNode] = None
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
