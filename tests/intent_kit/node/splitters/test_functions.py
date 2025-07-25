"""
Tests for splitters functions module.
"""

from unittest.mock import patch
from intent_kit.node.splitters.functions import rule_splitter, llm_splitter


class TestSplitterFunctions:
    """Test cases for splitter functions."""

    def test_rule_splitter_import(self):
        """Test that rule_splitter is properly imported."""
        from intent_kit.node.splitters.functions import rule_splitter

        assert rule_splitter is not None
        assert callable(rule_splitter)

    def test_llm_splitter_import(self):
        """Test that llm_splitter is properly imported."""
        from intent_kit.node.splitters.functions import llm_splitter

        assert llm_splitter is not None
        assert callable(llm_splitter)

    def test_module_all(self):
        """Test that __all__ contains the expected functions."""
        from intent_kit.node.splitters.functions import __all__

        assert "rule_splitter" in __all__
        assert "llm_splitter" in __all__
        assert len(__all__) == 2

    def test_rule_splitter_call(self):
        """Test calling rule_splitter function."""
        result = rule_splitter("test input")

        assert isinstance(result, list)
        assert len(result) >= 1

    def test_llm_splitter_call(self):
        """Test calling llm_splitter function."""
        result = llm_splitter("test input")

        assert isinstance(result, list)
        assert len(result) >= 1

    def test_rule_splitter_actual_functionality(self):
        """Test actual rule_splitter functionality."""
        # This test calls the actual rule_splitter function
        # We'll test with a simple input that should be split
        result = rule_splitter("Hello world. This is a test.")

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(chunk, str) for chunk in result)

    @patch("intent_kit.node.splitters.rule_splitter.rule_splitter")
    def test_llm_splitter_with_context(self, mock_rule_splitter):
        """Test llm_splitter with additional context."""
        mock_rule_splitter.return_value = ["chunk1", "chunk2"]

        # Test with additional parameters that might be passed
        result = llm_splitter("test input", debug=True)

        assert result == ["chunk1", "chunk2"]
        # Note: The actual call might not include context, but we're testing the interface

    def test_rule_splitter_edge_cases(self):
        """Test rule_splitter with edge cases."""
        # Empty string
        result = rule_splitter("")
        assert isinstance(result, list)

        # Single sentence
        result = rule_splitter("Hello.")
        assert isinstance(result, list)
        assert len(result) >= 1

        # Multiple sentences
        result = rule_splitter("Hello. World. Test.")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_rule_splitter_special_characters(self):
        """Test rule_splitter with special characters."""
        # Test with various punctuation
        test_input = "Hello! How are you? I'm fine. Thank you."
        result = rule_splitter(test_input)

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(chunk, str) for chunk in result)
