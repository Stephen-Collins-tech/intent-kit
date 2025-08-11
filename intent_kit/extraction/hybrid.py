"""
Hybrid argument extraction strategy.

This module provides a hybrid extractor that combines rule-based and LLM extraction.
"""

from typing import Mapping, Any, Optional
from .base import ExtractionResult, ArgumentSchema, ExtractorChain
from .llm import LLMArgumentExtractor, LLMConfig
from .rule_based import RuleBasedArgumentExtractor


class HybridArgumentExtractor:
    """Hybrid argument extractor combining rule-based and LLM extraction."""

    def __init__(
        self,
        llm_config: LLMConfig,
        extraction_prompt: Optional[str] = None,
        name: str = "hybrid",
        rule_first: bool = True,
    ):
        """
        Initialize the hybrid extractor.

        Args:
            llm_config: LLM configuration or client instance
            extraction_prompt: Optional custom prompt for LLM extraction
            name: Name of the extractor
            rule_first: Whether to run rule-based extraction first (default: True)
        """
        self.rule_first = rule_first
        self.name = name

        # Create the individual extractors
        self.rule_extractor = RuleBasedArgumentExtractor(name=name)
        self.llm_extractor = LLMArgumentExtractor(
            llm_config=llm_config,
            extraction_prompt=extraction_prompt,
            name=f"{name}_llm",
        )

        # Create the chain
        if rule_first:
            self.chain = ExtractorChain(self.rule_extractor, self.llm_extractor)
        else:
            self.chain = ExtractorChain(self.llm_extractor, self.rule_extractor)

    def extract(
        self,
        text: str,
        *,
        context: Mapping[str, Any],
        schema: Optional[ArgumentSchema] = None,
    ) -> ExtractionResult:
        """
        Extract arguments using hybrid extraction.

        Args:
            text: The input text to extract arguments from
            context: Context information to aid extraction
            schema: Optional schema defining expected arguments

        Returns:
            ExtractionResult with extracted parameters from both methods
        """
        return self.chain.extract(text, context=context, schema=schema)
