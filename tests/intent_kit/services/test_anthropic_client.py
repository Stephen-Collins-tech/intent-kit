"""
Tests for Anthropic client.
"""

import pytest


import sys


class TestAnthropicClient:
    """Test AnthropicClient class."""

    def test_def test_init_with_api_key(self): -> None:
        """Test initialization with API key."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            assert client.api_key == "test_api_key"
            assert client._client == mock_client
            mock_get_client.assert_called_once()

    def test_def test_get_client_success(self): -> None:
        """Test successful client creation."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.get_client()

            assert result == mock_client

    def test_def test_get_client_import_error(self): -> None:
        """Test client creation when Anthropic package is not installed."""
        with patch.object(
            AnthropicClient,
            "get_client",
            side_effect=ImportError("Anthropic package not installed"),
        ):
            with pytest.raises(ImportError, match="Anthropic package not installed"):
                AnthropicClient("test_api_key")

    def test_def test_ensure_imported_success(self): -> None:
        """Test _ensure_imported when client exists."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            # Should not raise
            client._ensure_imported()

    def test_def test_ensure_imported_recreate_client(self): -> None:
        """Test _ensure_imported when client is None."""


        mock_anthropic = Mock()
        mock_client = Mock()
        mock_anthropic.Anthropic.return_value = mock_client
        sys.modules["anthropic"] = mock_anthropic

        client = AnthropicClient("test_api_key")
        client._client = None  # Simulate client being None

        client._ensure_imported()

        assert client._client == mock_client

        # Clean up
        del sys.modules["anthropic"]

    def test_def test_generate_success(self): -> None:
        """Test successful text generation."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Generated response"
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt")
            assert result == "Generated response"
            mock_client.messages.create.assert_called_once_with(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": "Test prompt"}],
            )

    def test_def test_generate_with_custom_model(self): -> None:
        """Test text generation with custom model."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Generated response"
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt", model="claude-3-haiku-20240307")
            assert result == "Generated response"
            mock_client.messages.create.assert_called_once_with(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": "Test prompt"}],
            )

    def test_def test_generate_empty_response(self): -> None:
        """Test text generation with empty response."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = []
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt")

            assert result == ""

    def test_def test_generate_no_content(self): -> None:
        """Test text generation with no content in response."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = []
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt")

            assert result == ""

    def test_def test_generate_exception_handling(self): -> None:
        """Test text generation with exception handling."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("API Error")
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            with pytest.raises(Exception, match="API Error"):
                client.generate("Test prompt")

    def test_def test_generate_text_alias(self): -> None:
        """Test generate_text alias method."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Generated response"
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate_text(
                "Test prompt", model="claude-3-haiku-20240307"
            )
            assert result == "Generated response"
            mock_client.messages.create.assert_called_once_with(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": "Test prompt"}],
            )

    def test_def test_generate_with_client_recreation(self): -> None:
        """Test generate when client needs to be recreated."""
        mock_anthropic = Mock()
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Generated response"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client
        sys.modules["anthropic"] = mock_anthropic

        client = AnthropicClient("test_api_key")
        client._client = None  # Simulate client being None

        result = client.generate("Test prompt")
        assert result == "Generated response"
        assert client._client == mock_client

        # Clean up
        del sys.modules["anthropic"]

    # Note: is_available method doesn't exist on AnthropicClient class
    # These tests have been removed as they test non-existent functionality

    def test_def test_generate_with_different_prompts(self): -> None:
        """Test generate with different prompt types."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Response"
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            # Test with simple prompt
            result1 = client.generate("Hello")
            assert result1 == "Response"

            # Test with complex prompt
            result2 = client.generate("Please summarize this text.")
            assert result2 == "Response"

            # Verify calls
            assert mock_client.messages.create.call_count == 2

    def test_def test_generate_with_different_models(self): -> None:
        """Test generate with different model types."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Response"
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            # Test with default model
            result1 = client.generate("Test")
            assert result1 == "Response"

            # Test with custom model
            result2 = client.generate("Test", model="claude-3-haiku-20240307")
            assert result2 == "Response"

            # Test with another model
            result3 = client.generate("Test", model="claude-2.1")
            assert result3 == "Response"

            # Verify different models were used
            assert mock_client.messages.create.call_count == 3

    def test_def test_generate_with_multiple_content_parts(self): -> None:
        """Test generate with multiple content parts in response."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            # Simulate multiple content parts
            mock_content1 = Mock()
            mock_content1.text = "Part 1"
            mock_content2 = Mock()
            mock_content2.text = "Part 2"
            mock_response.content = [mock_content1, mock_content2]
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt")
            assert result == "Part 1"

    def test_def test_generate_with_logging(self): -> None:
        """Test generate with debug logging."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Generated response"
            mock_response.content = [mock_content]
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt")
            assert result == "Generated response"
            # Note: No debug logging is currently implemented in the generate method

    def test_def test_generate_with_api_error(self): -> None:
        """Test generate with API error handling."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("Rate limit exceeded")
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            with pytest.raises(Exception, match="Rate limit exceeded"):
                client.generate("Test prompt")

    def test_def test_generate_with_network_error(self): -> None:
        """Test generate with network error handling."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("Connection timeout")
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            with pytest.raises(Exception, match="Connection timeout"):
                client.generate("Test prompt")

    def test_def test_client_initialization_without_api_key(self): -> None:
        """Test client initialization without API key."""
        with pytest.raises(TypeError):
            AnthropicClient(api_key=None)  # type: ignore[call-arg]

    def test_def test_client_initialization_with_empty_api_key(self): -> None:
        """Test client initialization with empty API key."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            with pytest.raises(TypeError):
                AnthropicClient("")
