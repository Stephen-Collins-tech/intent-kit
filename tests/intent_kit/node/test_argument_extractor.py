"""
Tests for the ArgumentExtractor entity.
"""

from intent_kit.nodes.actions.argument_extractor import (
    RuleBasedArgumentExtractor,
    LLMArgumentExtractor,
    ArgumentExtractorFactory,
    ExtractionResult,
)


class TestRuleBasedArgumentExtractor:
    """Test the rule-based argument extractor."""

    def test_extract_name_parameter(self):
        """Test extracting name parameter from user input."""
        param_schema = {"name": str}
        extractor = RuleBasedArgumentExtractor(param_schema, "test_extractor")

        # Test basic name extraction
        result = extractor.extract("Hello Alice")
        assert result.success
        assert result.extracted_params["name"] == "Alice"

        # Test name with comma
        result = extractor.extract("Hi Bob, help me with calculations")
        assert result.success
        assert result.extracted_params["name"] == "Bob"

        # Test no name found
        result = extractor.extract("What's the weather like?")
        assert result.success
        assert result.extracted_params["name"] == "User"

    def test_extract_location_parameter(self):
        """Test extracting location parameter from user input."""
        param_schema = {"location": str}
        extractor = RuleBasedArgumentExtractor(param_schema, "test_extractor")

        # Test weather location
        result = extractor.extract("Weather in San Francisco")
        assert result.success
        assert result.extracted_params["location"] == "San Francisco"

        # Test location with "in"
        result = extractor.extract("What's the weather like in New York?")
        assert result.success
        assert result.extracted_params["location"] == "New York"

        # Test no location found
        result = extractor.extract("Hello there")
        assert result.success
        assert result.extracted_params["location"] == "Unknown"

    def test_extract_calculation_parameters(self):
        """Test extracting calculation parameters from user input."""
        param_schema = {"operation": str, "a": float, "b": float}
        extractor = RuleBasedArgumentExtractor(param_schema, "test_extractor")

        # Test basic calculation
        result = extractor.extract("What's 15 plus 7?")
        assert result.success
        assert result.extracted_params["a"] == 15.0
        assert result.extracted_params["operation"] == "plus"
        assert result.extracted_params["b"] == 7.0

        # Test multiplication with "by"
        result = extractor.extract("Multiply 8 by 3")
        assert result.success
        assert result.extracted_params["operation"] == "multiply"
        assert result.extracted_params["a"] == 8.0
        assert result.extracted_params["b"] == 3.0

        # Test no calculation found
        result = extractor.extract("Hello there")
        assert result.success
        assert result.extracted_params == {}

    def test_extract_multiple_parameters(self):
        """Test extracting multiple parameters at once."""
        param_schema = {
            "name": str,
            "location": str,
            "operation": str,
            "a": float,
            "b": float,
        }
        extractor = RuleBasedArgumentExtractor(param_schema, "test_extractor")

        # Test combined input
        result = extractor.extract("Hi Alice, what's 20 minus 5 and weather in Boston")
        assert result.success
        assert result.extracted_params["name"] == "Alice"
        assert result.extracted_params["location"] == "Boston"
        assert result.extracted_params["a"] == 20.0
        assert result.extracted_params["operation"] == "minus"
        assert result.extracted_params["b"] == 5.0

    def test_extraction_failure(self):
        """Test handling of extraction failures."""
        param_schema = {"name": str}
        extractor = RuleBasedArgumentExtractor(param_schema, "test_extractor")

        # Mock a failure by passing None
        result = extractor.extract(None)  # type: ignore
        assert not result.success
        assert result.error is not None


class TestArgumentExtractorFactory:
    """Test the argument extractor factory."""

    def test_create_rule_based_extractor(self):
        """Test creating a rule-based extractor."""
        param_schema = {"name": str}
        extractor = ArgumentExtractorFactory.create(
            param_schema=param_schema, name="test_extractor"
        )

        assert isinstance(extractor, RuleBasedArgumentExtractor)
        assert extractor.param_schema == param_schema
        assert extractor.name == "test_extractor"

    def test_create_llm_extractor(self):
        """Test creating an LLM-based extractor."""
        param_schema = {"name": str}
        llm_config = {"provider": "openai", "model": "gpt-3.5-turbo"}

        extractor = ArgumentExtractorFactory.create(
            param_schema=param_schema, llm_config=llm_config, name="test_extractor"
        )

        assert isinstance(extractor, LLMArgumentExtractor)
        assert extractor.param_schema == param_schema
        assert extractor.name == "test_extractor"
        assert extractor.llm_config == llm_config


class TestExtractionResult:
    """Test the ExtractionResult dataclass."""

    def test_basic_extraction_result(self):
        """Test creating a basic extraction result."""
        result = ExtractionResult(success=True, extracted_params={"name": "Alice"})

        assert result.success
        assert result.extracted_params == {"name": "Alice"}
        assert result.input_tokens is None
        assert result.output_tokens is None
        assert result.cost is None
        assert result.provider is None
        assert result.model is None
        assert result.duration is None
        assert result.error is None

    def test_llm_extraction_result(self):
        """Test creating an LLM extraction result with token info."""
        result = ExtractionResult(
            success=True,
            extracted_params={"name": "Alice"},
            input_tokens=100,
            output_tokens=50,
            cost=0.002,
            provider="openai",
            model="gpt-3.5-turbo",
            duration=1.5,
        )

        assert result.success
        assert result.extracted_params == {"name": "Alice"}
        assert result.input_tokens == 100
        assert result.output_tokens == 50
        assert result.cost == 0.002
        assert result.provider == "openai"
        assert result.model == "gpt-3.5-turbo"
        assert result.duration == 1.5

    def test_failed_extraction_result(self):
        """Test creating a failed extraction result."""
        result = ExtractionResult(
            success=False, extracted_params={}, error="Failed to parse input"
        )

        assert not result.success
        assert result.extracted_params == {}
        assert result.error == "Failed to parse input"
