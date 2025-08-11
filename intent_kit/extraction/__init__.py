"""
Extraction module for intent-kit.

This module provides a first-class plugin architecture for argument extraction.
Nodes depend on extraction interfaces, not specific implementations.
"""

from .base import (
    Extractor,
    ExtractorChain,
    ExtractionResult,
    ArgumentSchema,
)

# Import strategies to register them
try:
    from . import rule_based
    from . import llm
    from . import hybrid
except ImportError:
    pass

__all__ = [
    "Extractor",
    "ExtractorChain",
    "ExtractionResult",
    "ArgumentSchema",
]
