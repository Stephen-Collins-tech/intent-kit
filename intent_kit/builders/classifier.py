"""
Classifier builder for creating classifier nodes with fluent interface.

This module provides a builder class for creating ClassifierNode instances
with a more readable and type-safe approach.
"""

from typing import Callable, List, Optional, Union
from intent_kit.node import TreeNode
from intent_kit.node.classifiers import ClassifierNode
from intent_kit.node.actions import RemediationStrategy
from intent_kit.utils.node_factory import (
    create_classifier_node,
    create_default_classifier,
)
from .base import Builder


class ClassifierBuilder(Builder):
    """Builder for creating classifier nodes with fluent interface."""

    def __init__(self, name: str):
        """Initialize the classifier builder.

        Args:
            name: Name of the classifier node
        """
        super().__init__(name)
        self.classifier_func: Optional[Callable] = None
        self.children: List[TreeNode] = []
        self.remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = (
            None
        )

    def with_classifier(self, classifier_func: Callable) -> "ClassifierBuilder":
        """Set the classifier function.

        Args:
            classifier_func: Function to classify between children

        Returns:
            Self for method chaining
        """
        self.classifier_func = classifier_func
        return self

    def with_children(self, children: List[TreeNode]) -> "ClassifierBuilder":
        """Set the child nodes.

        Args:
            children: List of child nodes to classify between

        Returns:
            Self for method chaining
        """
        self.children = children
        return self

    def add_child(self, child: TreeNode) -> "ClassifierBuilder":
        """Add a child node.

        Args:
            child: Child node to add

        Returns:
            Self for method chaining
        """
        self.children.append(child)
        return self

    def with_remediation_strategies(
        self, strategies: List[Union[str, RemediationStrategy]]
    ) -> "ClassifierBuilder":
        """Set remediation strategies.

        Args:
            strategies: List of remediation strategies

        Returns:
            Self for method chaining
        """
        self.remediation_strategies = strategies
        return self

    def build(self) -> ClassifierNode:
        """Build and return the ClassifierNode instance.

        Returns:
            Configured ClassifierNode instance

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields using base class method
        self._validate_required_field("children", self.children, "with_children")

        # Use default classifier if none provided
        if not self.classifier_func:
            self.classifier_func = create_default_classifier()

        return create_classifier_node(
            name=self.name,
            description=self.description,
            classifier_func=self.classifier_func,
            children=self.children,
            remediation_strategies=self.remediation_strategies,
        )
