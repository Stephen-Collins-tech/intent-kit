"""
Specific tests for llm_splitter function.
"""
import unittest
from unittest.mock import Mock, patch
from intent_kit.graph.splitters.llm_splitter import llm_splitter, _create_splitting_prompt, _parse_llm_response


class TestLLMSplitterFunction(unittest.TestCase):
    """Test cases for the llm_splitter function."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm_client = Mock()
        self.taxonomies = {
            "travel": Mock(),
            "account": Mock(),
            "support": Mock()
        }

    def test_llm_splitting_success_valid_json(self):
        """Test successful LLM-based splitting with valid JSON response."""
        self.mock_llm_client.generate.return_value = (
            '[{"taxonomy": "travel", "text": "cancel my flight"}, '
            '{"taxonomy": "account", "text": "update my email"}]'
        )
        result = llm_splitter(
            "Cancel my flight and update my email",
            self.taxonomies,
            llm_client=self.mock_llm_client
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["taxonomy"], "travel")
        self.assertEqual(result[0]["text"], "cancel my flight")
        self.assertEqual(result[1]["taxonomy"], "account")
        self.assertEqual(result[1]["text"], "update my email")

    def test_llm_splitting_success_single_intent(self):
        """Test successful LLM-based splitting with single intent."""
        self.mock_llm_client.generate.return_value = (
            '[{"taxonomy": "travel", "text": "I need travel help"}]'
        )
        result = llm_splitter(
            "I need travel help",
            self.taxonomies,
            llm_client=self.mock_llm_client
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")
        self.assertEqual(result[0]["text"], "I need travel help")

    def test_llm_splitting_fallback_no_client(self):
        """Test fallback to rule-based when no LLM client provided."""
        # Should fallback to rule_splitter
        result = llm_splitter("travel help", self.taxonomies, llm_client=None)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")

    def test_llm_splitting_fallback_exception(self):
        """Test fallback to rule-based when LLM raises exception."""
        self.mock_llm_client.generate.side_effect = Exception(
            "LLM service unavailable")
        result = llm_splitter("travel help", self.taxonomies,
                              llm_client=self.mock_llm_client)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")

    def test_llm_splitting_fallback_invalid_json(self):
        """Test fallback to rule-based when LLM returns invalid JSON."""
        self.mock_llm_client.generate.return_value = "invalid json response"
        result = llm_splitter("travel help", self.taxonomies,
                              llm_client=self.mock_llm_client)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")

    def test_llm_splitting_fallback_empty_response(self):
        """Test fallback to rule-based when LLM returns empty response."""
        self.mock_llm_client.generate.return_value = ""
        result = llm_splitter("travel help", self.taxonomies,
                              llm_client=self.mock_llm_client)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")

    def test_llm_splitting_fallback_no_results(self):
        """Test fallback to rule-based when LLM parsing returns no results."""
        self.mock_llm_client.generate.return_value = '[]'
        result = llm_splitter("travel help", self.taxonomies,
                              llm_client=self.mock_llm_client)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")

    def test_llm_splitting_manual_parsing_fallback(self):
        """Test manual parsing fallback when JSON parsing fails."""
        self.mock_llm_client.generate.return_value = 'taxonomy: travel, text: travel help'
        result = llm_splitter("travel help", self.taxonomies,
                              llm_client=self.mock_llm_client)
        # Should fallback to rule-based splitting since manual parsing also fails
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")

    def test_prompt_creation(self):
        """Test that the LLM prompt is created correctly."""
        prompt = _create_splitting_prompt("test input", ["travel", "account"])
        self.assertIn("test input", prompt)
        self.assertIn("travel", prompt)
        self.assertIn("account", prompt)
        self.assertIn("JSON array", prompt)
        self.assertIn("taxonomy", prompt)
        self.assertIn("text", prompt)

    def test_debug_logging(self):
        """Test debug logging functionality."""
        self.mock_llm_client.generate.return_value = (
            '[{"taxonomy": "travel", "text": "travel help"}]'
        )
        # Should not raise, just exercise debug path
        result = llm_splitter(
            "travel help", self.taxonomies, debug=True, llm_client=self.mock_llm_client
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["taxonomy"], "travel")

    def test_llm_client_called_with_prompt(self):
        """Test that LLM client is called with the generated prompt."""
        self.mock_llm_client.generate.return_value = (
            '[{"taxonomy": "travel", "text": "travel help"}]'
        )
        llm_splitter("travel help", self.taxonomies,
                     llm_client=self.mock_llm_client)
        self.mock_llm_client.generate.assert_called_once()
        call_args = self.mock_llm_client.generate.call_args[0][0]
        self.assertIn("travel help", call_args)
        self.assertIn("travel", call_args)

    def test_parse_llm_response_valid_json(self):
        """Test parsing of valid JSON response."""
        response = '[{"taxonomy": "travel", "text": "cancel flight"}, {"taxonomy": "account", "text": "update email"}]'
        result = _parse_llm_response(response)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["taxonomy"], "travel")
        self.assertEqual(result[0]["text"], "cancel flight")
        self.assertEqual(result[1]["taxonomy"], "account")
        self.assertEqual(result[1]["text"], "update email")

    def test_parse_llm_response_invalid_json(self):
        """Test parsing of invalid JSON response."""
        response = "invalid json"
        result = _parse_llm_response(response)
        self.assertEqual(len(result), 0)

    def test_parse_llm_response_malformed_json(self):
        """Test parsing of malformed JSON response."""
        response = '[{"taxonomy": "travel"}]'  # Missing "text" field
        result = _parse_llm_response(response)
        self.assertEqual(len(result), 0)

    def test_parse_llm_response_wrong_type(self):
        """Test parsing of response with wrong data type."""
        response = '"not an array"'
        result = _parse_llm_response(response)
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    unittest.main()
