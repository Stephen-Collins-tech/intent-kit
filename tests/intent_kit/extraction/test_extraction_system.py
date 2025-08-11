"""
Tests for the extraction system.

This module tests the new first-class extraction plugin architecture.
"""

from intent_kit.extraction import (
    ExtractorChain,
    ExtractionResult,
    ArgumentSchema,
)
from intent_kit.extraction.rule_based import RuleBasedArgumentExtractor


class TestExtractionSystem:
    """Test the extraction system functionality."""

    def test_extraction_result_creation(self):
        """Test creating an ExtractionResult."""
        result = ExtractionResult(
            args={"name": "Alice", "location": "New York"},
            confidence=0.8,
            warnings=["Missing required parameter: age"],
            metadata={"method": "rule_based"},
        )

        assert result.args == {"name": "Alice", "location": "New York"}
        assert result.confidence == 0.8
        assert result.warnings == ["Missing required parameter: age"]
        assert result.metadata == {"method": "rule_based"}

    def test_argument_schema_creation(self):
        """Test creating an ArgumentSchema."""
        schema: ArgumentSchema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "User's name"},
                "age": {"type": "integer", "description": "User's age"},
            },
            "required": ["name"],
        }

        assert schema["type"] == "object"
        assert "name" in schema["properties"]
        assert "name" in schema["required"]

    def test_extractor_chain(self):
        """Test the ExtractorChain functionality."""
        extractor1 = RuleBasedArgumentExtractor()
        extractor2 = RuleBasedArgumentExtractor()

        chain = ExtractorChain(extractor1, extractor2)
        assert chain.name == "chain_rule_based_rule_based"
        assert len(chain.extractors) == 2

    def test_extractor_chain_extraction(self):
        """Test extraction using ExtractorChain."""
        extractor1 = RuleBasedArgumentExtractor()
        extractor2 = RuleBasedArgumentExtractor()

        chain = ExtractorChain(extractor1, extractor2)

        # Test with a simple schema
        schema: ArgumentSchema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }

        result = chain.extract("Hello Alice", context={}, schema=schema)

        assert isinstance(result, ExtractionResult)
        assert "name" in result.args
        assert result.args["name"] == "Alice"
        assert result.confidence > 0
