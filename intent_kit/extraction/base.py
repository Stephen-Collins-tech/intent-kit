"""
Base extraction interfaces and types.

This module defines the core extraction protocol and supporting types.
"""

from typing import Protocol, Mapping, Any, Optional, Dict, List, TypedDict
from dataclasses import dataclass


class ArgumentSchema(TypedDict, total=False):
    """Schema definition for argument extraction."""

    required: List[str]
    properties: Dict[str, Any]
    type: str
    description: str


@dataclass
class ExtractionResult:
    """Result of argument extraction operation."""

    args: Dict[str, Any]
    confidence: float
    warnings: List[str]
    metadata: Optional[Dict[str, Any]] = None


class Extractor(Protocol):
    """Protocol for argument extractors."""

    name: str

    def extract(
        self,
        text: str,
        *,
        context: Mapping[str, Any],
        schema: Optional[ArgumentSchema] = None,
    ) -> ExtractionResult:
        """
        Extract arguments from text.

        Args:
            text: The input text to extract arguments from
            context: Context information to aid extraction
            schema: Optional schema defining expected arguments

        Returns:
            ExtractionResult with extracted arguments and metadata
        """
        ...


class ExtractorChain:
    """Chain multiple extractors together."""

    def __init__(self, *extractors: Extractor):
        """
        Initialize the extractor chain.

        Args:
            *extractors: Variable number of extractors to chain
        """
        self.extractors = extractors
        self.name = f"chain_{'_'.join(ex.name for ex in extractors)}"

    def extract(
        self,
        text: str,
        *,
        context: Mapping[str, Any],
        schema: Optional[ArgumentSchema] = None,
    ) -> ExtractionResult:
        """
        Extract arguments using all extractors in the chain.

        Args:
            text: The input text to extract arguments from
            context: Context information to aid extraction
            schema: Optional schema defining expected arguments

        Returns:
            Merged ExtractionResult from all extractors
        """
        merged = ExtractionResult(args={}, confidence=0.0, warnings=[], metadata={})

        for extractor in self.extractors:
            result = extractor.extract(text, context=context, schema=schema)

            # Merge arguments (later extractors can override earlier ones)
            merged.args.update(result.args)

            # Take the highest confidence
            merged.confidence = max(merged.confidence, result.confidence)

            # Collect all warnings
            merged.warnings.extend(result.warnings)

            # Merge metadata
            if result.metadata:
                if merged.metadata is None:
                    merged.metadata = {}
                merged.metadata.update(result.metadata)

        return merged
