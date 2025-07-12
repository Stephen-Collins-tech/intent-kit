"""
Specific tests for rule_splitter function.
"""

import unittest
from intent_kit.node.splitters import rule_splitter


class TestRuleSplitter(unittest.TestCase):
    """Test cases for rule_splitter function."""

    def test_single_intent_no_splitting(self):
        """Test single intent that doesn't need splitting."""
        result = rule_splitter("I need help with something")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "I need help with something")

    def test_multi_intent_and_conjunction(self):
        """Test multi-intent with 'and' conjunction."""
        result = rule_splitter("travel help and account support")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_multi_intent_comma_conjunction(self):
        """Test multi-intent with comma conjunction."""
        result = rule_splitter("travel help, account support")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_multi_intent_semicolon_conjunction(self):
        """Test multi-intent with semicolon conjunction."""
        result = rule_splitter("travel help; account support")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_multi_intent_also_conjunction(self):
        """Test multi-intent with 'also' conjunction."""
        result = rule_splitter("travel help also account support")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_multi_intent_plus_conjunction(self):
        """Test multi-intent with 'plus' conjunction."""
        result = rule_splitter("travel help plus account support")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_multi_intent_as_well_as_conjunction(self):
        """Test multi-intent with 'as well as' conjunction."""
        result = rule_splitter("travel help as well as account support")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_case_insensitive_splitting(self):
        """Test case-insensitive conjunction splitting."""
        result = rule_splitter("travel help AND account support")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_multiple_conjunctions(self):
        """Test input with multiple conjunctions."""
        result = rule_splitter(
            "travel help, account support and booking flights")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")
        self.assertEqual(result[2], "booking flights")

    def test_no_match_found(self):
        """Test when no conjunctions are found."""
        result = rule_splitter(
            "I need help with something completely unrelated")
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0], "I need help with something completely unrelated")

    def test_empty_input(self):
        """Test handling of empty input."""
        result = rule_splitter("")
        self.assertEqual(len(result), 0)

    def test_whitespace_only_input(self):
        """Test handling of whitespace-only input."""
        result = rule_splitter("   ")
        self.assertEqual(len(result), 0)

    def test_debug_logging(self):
        """Test debug logging functionality."""
        result = rule_splitter("travel help and account support", debug=True)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")


if __name__ == "__main__":
    unittest.main()
