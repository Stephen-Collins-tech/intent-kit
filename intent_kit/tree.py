from typing import Any, Callable, List, Optional, Dict, Type
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
        name: str,
        param_schema: Dict[str, Type],
        handler: Callable[..., Any],
        arg_extractor: Callable[[str], Dict[str, Any]],
        input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
        output_validator: Optional[Callable[[Any], bool]] = None,
        description: str = ""
    ) -> IntentNode:
        """Create a new Intent node."""
        return IntentNode(
            name,
            param_schema,
            handler,
            arg_extractor,
            input_validator,
            output_validator,
            description
        )

    @staticmethod
    def llm_intent_node(
        *,
        name: str,
        param_schema: Dict[str, Type],
        handler: Callable[..., Any],
        llm_config: Dict[str, Any],
        extraction_prompt: Optional[str] = None,
        input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
        output_validator: Optional[Callable[[Any], bool]] = None,
        description: str = ""
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
            input_validator,
            output_validator,
            description
        )

    @staticmethod
    def classifier_node(
        *,
        name: str,
        classifier: Callable[[str, List[TaxonomyNode]], Optional[TaxonomyNode]],
        children: List[TaxonomyNode],
        description: str = ""
    ) -> ClassifierNode:
        """Create a new ClassifierNode."""
        return ClassifierNode(name, classifier, children, description)

    @staticmethod
    def llm_classifier_node(
        *,
        name: str,
        children: List[TaxonomyNode],
        llm_config: Dict[str, Any],
        classification_prompt: Optional[str] = None,
        description: str = ""
    ) -> ClassifierNode:
        """Create a new ClassifierNode with LLM-powered classification."""
        if not classification_prompt:
            classification_prompt = get_default_classification_prompt()

        # Get descriptions from children for the prompt
        node_descriptions = [child.description for child in children]

        classifier = create_llm_classifier(
            llm_config, classification_prompt, node_descriptions)

        return ClassifierNode(name, classifier, children, description)
