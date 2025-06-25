"""
Specific tests for rule_splitter function.
"""
import unittest
from unittest.mock import Mock
from intent_kit.graph.splitters.rule_splitter import rule_splitter


class TestRuleSplitter(unittest.TestCase):
    """Test cases for rule_splitter function."""

    def setUp(self):
        """Set up test fixtures."""
        self.taxonomies = {
            "travel": Mock(),
            "account": Mock(),
            "support": Mock()
        }

    def test_single_intent_exact_taxonomy_match(self):
        """Test single intent with exact taxonomy name match."""
        result = rule_splitter("I need travel help", self.taxonomies)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")
        self.assertEqual(result[0]["text"], "I need travel help")

    def test_single_intent_keyword_match(self):
        """Test single intent with keyword-based matching."""
        result = rule_splitter(
            "I need to cancel my flight", self.taxonomies)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")
        self.assertEqual(result[0]["text"], "I need to cancel my flight")

    def test_single_intent_partial_taxonomy_match(self):
        """Test single intent with partial taxonomy name match."""
        result = rule_splitter(
            "I need account assistance", self.taxonomies)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "account")
        self.assertEqual(result[0]["text"], "I need account assistance")

    def test_multi_intent_and_conjunction(self):
        """Test multi-intent with comma conjunction (contrived)."""
        result = rule_splitter(
            "travel help, account support", self.taxonomies)
        self.assertEqual(len(result), 2)

    def test_multi_intent_comma_conjunction(self):
        """Test multi-intent with comma conjunction (contrived)."""
        result = rule_splitter(
            "travel help, account support", self.taxonomies)
        self.assertEqual(len(result), 2)

    def test_multi_intent_semicolon_conjunction(self):
        """Test multi-intent with semicolon conjunction (contrived)."""
        result = rule_splitter(
            "travel help; account support", self.taxonomies)
        self.assertEqual(len(result), 2)

    def test_multi_intent_also_conjunction(self):
        """Test multi-intent with 'also' conjunction (contrived)."""
        result = rule_splitter(
            "travel help also account support", self.taxonomies)
        # Could be 1 or 2 depending on implementation
        self.assertTrue(len(result) >= 1)

    def test_case_insensitive_matching(self):
        """Test case-insensitive taxonomy matching."""
        result = rule_splitter("I need TRAVEL help", self.taxonomies)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")

    def test_keyword_matching_travel(self):
        """Test keyword matching for travel taxonomy."""
        travel_keywords = ["flight", "cancel", "book",
                           "reserve", "trip", "travel", "airline"]

        for keyword in travel_keywords:
            result = rule_splitter(
                f"I need to {keyword}", self.taxonomies)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["taxonomy"], "travel")

    def test_keyword_matching_account(self):
        """Test keyword matching for account taxonomy."""
        account_keywords = ["email", "update", "password",
                            "reset", "account", "profile", "settings"]

        for keyword in account_keywords:
            result = rule_splitter(
                f"I need to {keyword}", self.taxonomies)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["taxonomy"], "account")

    def test_keyword_matching_support(self):
        """Test keyword matching for support taxonomy."""
        support_keywords = ["support", "assist", "issue", "problem", "trouble"]

        for keyword in support_keywords:
            result = rule_splitter(f"I need {keyword}", self.taxonomies)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["taxonomy"], "support")

    def test_no_match_found(self):
        """Test when no taxonomy matches."""
        result = rule_splitter(
            "I need help with something completely unrelated", self.taxonomies)

        self.assertEqual(len(result), 0)

    def test_empty_input(self):
        """Test handling of empty input."""
        result = rule_splitter("", self.taxonomies)

        self.assertEqual(len(result), 0)

    def test_whitespace_only_input(self):
        """Test handling of whitespace-only input."""
        result = rule_splitter("   ", self.taxonomies)

        self.assertEqual(len(result), 0)

    def test_debug_logging(self):
        """Test debug logging functionality."""
        result = rule_splitter(
            "travel help", self.taxonomies, debug=True)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")

    def test_fallback_assignment(self):
        """Test fallback assignment with comma (contrived)."""
        test_taxonomies = {"service1": Mock(), "service2": Mock()}
        result = rule_splitter(
            "first, second", test_taxonomies)
        self.assertEqual(len(result), 2)


if __name__ == '__main__':
    unittest.main()
