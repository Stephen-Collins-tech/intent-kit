"""
Classifiers module - consolidated classifier functionality.

This module provides both classifier functions and the ClassifierNode class
for routing user inputs to appropriate child nodes.
"""

from .node import ClassifierNode
from .keyword import keyword_classifier
from .llm_classifier import (
    create_llm_classifier,
    create_llm_arg_extractor,
    get_default_classification_prompt,
    get_default_extraction_prompt,
)
from .chunk_classifier import classify_intent_chunk

__all__ = [
    # Node class
    "ClassifierNode",
    # Classifier functions
    "keyword_classifier",
    "create_llm_classifier",
    "create_llm_arg_extractor",
    "get_default_classification_prompt",
    "get_default_extraction_prompt",
    "classify_intent_chunk",
]
