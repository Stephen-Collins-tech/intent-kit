"""
Specific tests for llm_splitter function.
"""

import unittest
from unittest.mock import Mock
from intent_kit.node.splitters import (
    llm_splitter,
    _create_splitting_prompt,
    _parse_llm_response,
    create_llm_splitter,
)


class TestLLMSplitterFunction(unittest.TestCase):
    """Test cases for the llm_splitter function."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm_client = Mock()

    def test_llm_splitting_success_valid_json(self):
        """Test successful LLM-based splitting with valid JSON response."""
        self.mock_llm_client.generate.return_value = (
            '["cancel my flight", "update my email"]'
        )
        result = llm_splitter(
            "Cancel my flight and update my email", llm_client=self.mock_llm_client
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "cancel my flight")
        self.assertEqual(result[1], "update my email")

    def test_llm_splitting_success_single_intent(self):
        """Test successful LLM-based splitting with single intent."""
        self.mock_llm_client.generate.return_value = '["I need travel help"]'
        result = llm_splitter("I need travel help", llm_client=self.mock_llm_client)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "I need travel help")

    def test_llm_splitting_fallback_no_client(self):
        """Test fallback to rule-based when no LLM client provided."""
        # Should fallback to rule_splitter
        result = llm_splitter("travel help and account support", llm_client=None)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_llm_splitting_fallback_exception(self):
        """Test fallback to rule-based when LLM raises exception."""
        self.mock_llm_client.generate.side_effect = Exception("LLM service unavailable")
        result = llm_splitter(
            "travel help and account support", llm_client=self.mock_llm_client
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_llm_splitting_fallback_invalid_json(self):
        """Test fallback to rule-based when LLM returns invalid JSON."""
        self.mock_llm_client.generate.return_value = "invalid json response"
        result = llm_splitter(
            "travel help and account support", llm_client=self.mock_llm_client
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_llm_splitting_fallback_empty_response(self):
        """Test fallback to rule-based when LLM returns empty response."""
        self.mock_llm_client.generate.return_value = ""
        result = llm_splitter(
            "travel help and account support", llm_client=self.mock_llm_client
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_llm_splitting_fallback_no_results(self):
        """Test fallback to rule-based when LLM parsing returns no results."""
        self.mock_llm_client.generate.return_value = "[]"
        result = llm_splitter(
            "travel help and account support", llm_client=self.mock_llm_client
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_llm_splitting_manual_parsing_fallback(self):
        """Test manual parsing fallback when JSON parsing fails."""
        self.mock_llm_client.generate.return_value = "chunk1, chunk2"
        result = llm_splitter(
            "travel help and account support", llm_client=self.mock_llm_client
        )
        # Should now extract quoted/comma-separated items
        self.assertEqual(result, ["chunk1", "chunk2"])

    def test_prompt_creation(self):
        """Test that the LLM prompt is created correctly."""
        prompt = _create_splitting_prompt("test input")
        self.assertIn("test input", prompt)
        self.assertIn("JSON array", prompt)
        self.assertIn("separate nodes", prompt)

    def test_debug_logging(self):
        """Test debug logging functionality."""
        self.mock_llm_client.generate.return_value = '["travel help"]'
        # Should not raise, just exercise debug path
        result = llm_splitter(
            "travel help", debug=True, llm_client=self.mock_llm_client
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "travel help")

    def test_llm_client_called_with_prompt(self):
        """Test that LLM client is called with the generated prompt."""
        self.mock_llm_client.generate.return_value = '["travel help"]'
        llm_splitter("travel help", llm_client=self.mock_llm_client)
        self.mock_llm_client.generate.assert_called_once()
        call_args = self.mock_llm_client.generate.call_args[0][0]
        self.assertIn("travel help", call_args)

    def test_parse_llm_response_valid_json(self):
        """Test parsing of valid JSON response."""
        response = '["cancel flight", "update email"]'
        result = _parse_llm_response(response)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "cancel flight")
        self.assertEqual(result[1], "update email")

    def test_parse_llm_response_invalid_json(self):
        """Test parsing of invalid JSON response."""
        response = "invalid json"
        result = _parse_llm_response(response)
        self.assertEqual(len(result), 0)

    def test_parse_llm_response_malformed_json(self):
        """Test parsing of malformed JSON response."""
        response = "[123]"  # Not strings
        result = _parse_llm_response(response)
        self.assertEqual(len(result), 0)

    def test_parse_llm_response_wrong_type(self):
        """Test parsing of response with wrong data type."""
        response = '"not an array"'
        result = _parse_llm_response(response)
        # Manual parsing should extract the quoted string
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "not an array")

    def test_parse_llm_response_quoted_strings(self):
        """Test manual parsing with quoted strings."""
        response = 'chunk1, "chunk2", chunk3'
        result = _parse_llm_response(response)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "chunk2")

    def test_parse_llm_response_numbered_items(self):
        """Test manual parsing with numbered items."""
        response = "1. cancel flight\n2. update email"
        result = _parse_llm_response(response)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "cancel flight")
        self.assertEqual(result[1], "update email")

    def test_parse_llm_response_dash_items(self):
        """Test manual parsing with dash-separated items."""
        response = "- cancel flight\n- update email"
        result = _parse_llm_response(response)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "cancel flight")
        self.assertEqual(result[1], "update email")


class TestCreateLLMSplitter(unittest.TestCase):
    """Test cases for the create_llm_splitter function."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm_client = Mock()

    def test_create_llm_splitter_with_dict_config(self):
        """Test creating splitter with dictionary config containing LLM client."""
        config = {"llm_client": self.mock_llm_client}
        self.mock_llm_client.generate.return_value = '["chunk1", "chunk2"]'

        splitter_func = create_llm_splitter(llm_config=config)
        result = splitter_func("input", False)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "chunk1")
        self.assertEqual(result[1], "chunk2")

    def test_create_llm_splitter_with_client_instance(self):
        """Test creating splitter with direct client instance."""
        self.mock_llm_client.generate.return_value = '["single chunk"]'

        splitter_func = create_llm_splitter(llm_config=self.mock_llm_client)
        result = splitter_func("input", False)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "single chunk")

    def test_create_llm_splitter_with_custom_prompt(self):
        """Test creating splitter with custom splitting prompt."""
        config = {"llm_client": self.mock_llm_client}
        custom_prompt = "Custom prompt: {input}"
        self.mock_llm_client.generate.return_value = '["custom result"]'

        splitter_func = create_llm_splitter(
            llm_config=config, splitting_prompt=custom_prompt
        )
        result = splitter_func("input", False)

        # Verify custom prompt was used
        call_args = self.mock_llm_client.generate.call_args[0][0]
        self.assertIn("Custom prompt: {input}", call_args)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "custom result")

    def test_create_llm_splitter_fallback_no_client_in_dict(self):
        """Test fallback when dict config has no llm_client."""
        config = {"other_key": "value"}

        splitter_func = create_llm_splitter(llm_config=config)
        result = splitter_func("travel help and account support", False)

        # Should fallback to rule-based splitting
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_create_llm_splitter_fallback_none_client(self):
        """Test fallback when client is None."""
        splitter_func = create_llm_splitter(llm_config=None)
        result = splitter_func("travel help and account support", False)

        # Should fallback to rule-based splitting
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_create_llm_splitter_fallback_exception(self):
        """Test fallback when LLM client raises exception."""
        self.mock_llm_client.generate.side_effect = Exception("LLM error")
        config = {"llm_client": self.mock_llm_client}

        splitter_func = create_llm_splitter(llm_config=config)
        result = splitter_func("travel help and account support", False)

        # Should fallback to rule-based splitting
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_create_llm_splitter_fallback_invalid_response(self):
        """Test fallback when LLM returns invalid response."""
        self.mock_llm_client.generate.return_value = "invalid response"
        config = {"llm_client": self.mock_llm_client}

        splitter_func = create_llm_splitter(llm_config=config)
        result = splitter_func("travel help and account support", False)

        # Should fallback to rule-based splitting
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")

    def test_create_llm_splitter_debug_logging(self):
        """Test debug logging in created splitter function."""
        config = {"llm_client": self.mock_llm_client}
        self.mock_llm_client.generate.return_value = '["debug test"]'

        splitter_func = create_llm_splitter(llm_config=config)
        result = splitter_func("input", True)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "debug test")

    def test_create_llm_splitter_function_signature(self):
        """Test that created splitter function has correct signature."""
        config = {"llm_client": self.mock_llm_client}

        splitter_func = create_llm_splitter(llm_config=config)

        # Check that function accepts expected parameters
        import inspect

        sig = inspect.signature(splitter_func)
        params = list(sig.parameters.keys())

        self.assertIn("user_input", params)
        self.assertIn("debug", params)
        self.assertEqual(len(params), 2)  # Only user_input and debug

    def test_create_llm_splitter_uses_default_prompt_when_none_provided(self):
        """Test that default prompt is used when no custom prompt provided."""
        config = {"llm_client": self.mock_llm_client}
        self.mock_llm_client.generate.return_value = '["default prompt result"]'

        splitter_func = create_llm_splitter(llm_config=config)
        result = splitter_func("input", False)

        # Verify default prompt was used
        call_args = self.mock_llm_client.generate.call_args[0][0]
        self.assertIn("input", call_args)
        self.assertIn("JSON array", call_args)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "default prompt result")

    def test_create_llm_splitter_empty_dict_config(self):
        """Test creating splitter with empty dictionary config."""
        config = {}

        splitter_func = create_llm_splitter(llm_config=config)
        result = splitter_func("travel help and account support", False)

        # Should fallback to rule-based splitting
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "travel help")
        self.assertEqual(result[1], "account support")


def test_parse_llm_response_valid_json():
    response = '["cancel flight", "update email"]'
    result = _parse_llm_response(response)
    assert result == ["cancel flight", "update email"]


def test_parse_llm_response_malformed_json():
    response = "[123]"
    result = _parse_llm_response(response)
    assert result == []


def test_parse_llm_response_quoted_strings():
    response = 'chunk1, "chunk2", chunk3'
    result = _parse_llm_response(response)
    assert result == ["chunk2"]


def test_parse_llm_response_numbered_items():
    response = "1. cancel flight\n2. update email"
    result = _parse_llm_response(response)
    assert result == ["cancel flight", "update email"]


def test_parse_llm_response_dash_items():
    response = "- cancel flight\n- update email"
    result = _parse_llm_response(response)
    assert result == ["cancel flight", "update email"]


def test_parse_llm_response_empty():
    response = ""
    result = _parse_llm_response(response)
    assert result == []


def test_parse_llm_response_garbage():
    response = "nonsense text with no structure"
    result = _parse_llm_response(response)
    assert result == []


if __name__ == "__main__":
    unittest.main()
