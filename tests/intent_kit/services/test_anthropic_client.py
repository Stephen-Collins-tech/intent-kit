"""
Tests for Anthropic client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from intent_kit.services.anthropic_client import AnthropicClient


class TestAnthropicClient:
    """Test AnthropicClient class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        with patch("intent_kit.services.anthropic_client.anthropic") as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.Anthropic.return_value = mock_client

            client = AnthropicClient("test_api_key")

            assert client.api_key == "test_api_key"
            assert client._client == mock_client
            mock_anthropic.Anthropic.assert_called_once_with(api_key="test_api_key")

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_get_client_success(self, mock_anthropic):
        """Test successful client creation."""
        mock_client = Mock()
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")
        result = client.get_client()

        assert result == mock_client
        mock_anthropic.Anthropic.assert_called_once_with(api_key="test_api_key")

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_get_client_import_error(self, mock_anthropic):
        """Test client creation when Anthropic package is not installed."""
        mock_anthropic.side_effect = ImportError("No module named 'anthropic'")

        with pytest.raises(ImportError, match="Anthropic package not installed"):
            AnthropicClient("test_api_key")

    def test_ensure_imported_success(self):
        """Test _ensure_imported when client exists."""
        with patch("intent_kit.services.anthropic_client.anthropic") as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.Anthropic.return_value = mock_client

            client = AnthropicClient("test_api_key")
            # Should not raise
            client._ensure_imported()

    def test_ensure_imported_recreate_client(self):
        """Test _ensure_imported when client is None."""
        with patch("intent_kit.services.anthropic_client.anthropic") as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.Anthropic.return_value = mock_client

            client = AnthropicClient("test_api_key")
            client._client = None  # Simulate client being None

            client._ensure_imported()

            assert client._client == mock_client
            mock_anthropic.Anthropic.assert_called_with(api_key="test_api_key")

    def test_ensure_imported_import_error(self):
        """Test _ensure_imported when import fails."""
        with patch("intent_kit.services.anthropic_client.anthropic") as mock_anthropic:
            mock_anthropic.side_effect = ImportError("No module named 'anthropic'")

            client = AnthropicClient("test_api_key")
            client._client = None  # Simulate client being None

            with pytest.raises(ImportError, match="Anthropic package not installed"):
                client._ensure_imported()

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_success(self, mock_anthropic):
        """Test successful text generation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.content = "Generated response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")
        result = client.generate("Test prompt")

        assert result == "Generated response"
        mock_client.messages.create.assert_called_once_with(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": "Test prompt"}]
        )

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_with_custom_model(self, mock_anthropic):
        """Test text generation with custom model."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.content = "Generated response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")
        result = client.generate("Test prompt", model="claude-3-haiku-20240307")

        assert result == "Generated response"
        mock_client.messages.create.assert_called_once_with(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": "Test prompt"}]
        )

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_empty_response(self, mock_anthropic):
        """Test text generation with empty response."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.content = None
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")
        result = client.generate("Test prompt")

        assert result == ""

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_no_content(self, mock_anthropic):
        """Test text generation with no content in response."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")
        result = client.generate("Test prompt")

        assert result == ""

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_exception_handling(self, mock_anthropic):
        """Test text generation with exception handling."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")

        with pytest.raises(Exception, match="API Error"):
            client.generate("Test prompt")

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_text_alias(self, mock_anthropic):
        """Test generate_text alias method."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.content = "Generated response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")
        result = client.generate_text("Test prompt", model="claude-3-haiku-20240307")

        assert result == "Generated response"
        mock_client.messages.create.assert_called_once_with(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": "Test prompt"}]
        )

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_with_client_recreation(self, mock_anthropic):
        """Test generate when client needs to be recreated."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.content = "Generated response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")
        client._client = None  # Simulate client being None

        result = client.generate("Test prompt")

        assert result == "Generated response"
        # Should recreate client
        assert mock_anthropic.Anthropic.call_count == 2

    def test_is_available_method(self):
        """Test is_available class method."""
        # Test when anthropic is available
        with patch("intent_kit.services.anthropic_client.anthropic"):
            assert AnthropicClient.is_available() is True

        # Test when anthropic is not available
        with patch("intent_kit.services.anthropic_client.anthropic", side_effect=ImportError):
            assert AnthropicClient.is_available() is False

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_with_different_prompts(self, mock_anthropic):
        """Test generate with different prompt types."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.content = "Response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")

        # Test with simple prompt
        result1 = client.generate("Hello")
        assert result1 == "Response"

        # Test with complex prompt
        complex_prompt = "Please analyze the following text and provide a summary: This is a test."
        result2 = client.generate(complex_prompt)
        assert result2 == "Response"

        # Verify calls
        assert mock_client.messages.create.call_count == 2

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_with_different_models(self, mock_anthropic):
        """Test generate with different model types."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.content = "Response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")

        # Test with default model
        result1 = client.generate("Test")
        assert result1 == "Response"

        # Test with custom model
        result2 = client.generate("Test", model="claude-3-haiku-20240307")
        assert result2 == "Response"

        # Test with another model
        result3 = client.generate("Test", model="claude-3-opus-20240229")
        assert result3 == "Response"

        # Verify different models were used
        calls = mock_client.messages.create.call_args_list
        assert calls[0][1]["model"] == "claude-sonnet-4-20250514"
        assert calls[1][1]["model"] == "claude-3-haiku-20240307"
        assert calls[2][1]["model"] == "claude-3-opus-20240229"

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_with_multiple_content_parts(self, mock_anthropic):
        """Test generate with multiple content parts in response."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content1 = Mock()
        mock_content1.content = "Part 1"
        mock_content2 = Mock()
        mock_content2.content = "Part 2"
        mock_response.content = [mock_content1, mock_content2]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")
        result = client.generate("Test prompt")

        # Should concatenate all content parts
        assert result == "Part 1Part 2"

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_with_logging(self, mock_anthropic):
        """Test generate with debug logging."""
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.content = "Generated response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        with patch("intent_kit.services.anthropic_client.logger") as mock_logger:
            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt")

            assert result == "Generated response"
            mock_logger.debug.assert_called_once_with(
                "Anthropic generate response: Generated response"
            )

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_with_api_error(self, mock_anthropic):
        """Test generate with API error handling."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("Rate limit exceeded")
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")

        with pytest.raises(Exception, match="Rate limit exceeded"):
            client.generate("Test prompt")

    @patch("intent_kit.services.anthropic_client.anthropic")
    def test_generate_with_network_error(self, mock_anthropic):
        """Test generate with network error handling."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("Connection timeout")
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient("test_api_key")

        with pytest.raises(Exception, match="Connection timeout"):
            client.generate("Test prompt")

    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key."""
        with pytest.raises(TypeError):
            AnthropicClient()

    def test_client_initialization_with_empty_api_key(self):
        """Test client initialization with empty API key."""
        with patch("intent_kit.services.anthropic_client.anthropic") as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.Anthropic.return_value = mock_client

            client = AnthropicClient("")
            assert client.api_key == ""
            assert client._client == mock_client