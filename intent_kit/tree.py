from typing import Any, Callable, List, Optional, Dict, Type
from .node import IntentNode, ClassifierNode, TaxonomyNode


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
    def classifier_node(
        *,
        name: str,
        classifier: Callable[[str, List[TaxonomyNode]], Optional[TaxonomyNode]],
        children: List[TaxonomyNode],
        description: str = ""
    ) -> ClassifierNode:
        """Create a new ClassifierNode."""
        return ClassifierNode(name, classifier, children, description)
