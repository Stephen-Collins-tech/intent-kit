"""
Tests for OpenAI client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from intent_kit.services.openai_client import OpenAIClient


class TestOpenAIClient:
    """Test OpenAIClient class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        with patch("intent_kit.services.openai_client.openai") as mock_openai:
            mock_client = Mock()
            mock_openai.OpenAI.return_value = mock_client

            client = OpenAIClient("test_api_key")

            assert client.api_key == "test_api_key"
            assert client._client == mock_client
            mock_openai.OpenAI.assert_called_once_with(api_key="test_api_key")

    @patch("intent_kit.services.openai_client.openai")
    def test_get_client_success(self, mock_openai):
        """Test successful client creation."""
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient("test_api_key")
        result = client.get_client()

        assert result == mock_client
        mock_openai.OpenAI.assert_called_once_with(api_key="test_api_key")

    @patch("intent_kit.services.openai_client.openai")
    def test_get_client_import_error(self, mock_openai):
        """Test client creation when OpenAI package is not installed."""
        mock_openai.side_effect = ImportError("No module named 'openai'")

        with pytest.raises(ImportError, match="OpenAI package not installed"):
            OpenAIClient("test_api_key")

    def test_ensure_imported_success(self):
        """Test _ensure_imported when client exists."""
        with patch("intent_kit.services.openai_client.openai") as mock_openai:
            mock_client = Mock()
            mock_openai.OpenAI.return_value = mock_client

            client = OpenAIClient("test_api_key")
            # Should not raise
            client._ensure_imported()

    def test_ensure_imported_recreate_client(self):
        """Test _ensure_imported when client is None."""
        with patch("intent_kit.services.openai_client.openai") as mock_openai:
            mock_client = Mock()
            mock_openai.OpenAI.return_value = mock_client

            client = OpenAIClient("test_api_key")
            client._client = None  # Simulate client being None

            client._ensure_imported()

            assert client._client == mock_client
            mock_openai.OpenAI.assert_called_with(api_key="test_api_key")

    def test_ensure_imported_import_error(self):
        """Test _ensure_imported when import fails."""
        with patch("intent_kit.services.openai_client.openai") as mock_openai:
            mock_openai.side_effect = ImportError("No module named 'openai'")

            client = OpenAIClient("test_api_key")
            client._client = None  # Simulate client being None

            with pytest.raises(ImportError, match="OpenAI package not installed"):
                client._ensure_imported()

    @patch("intent_kit.services.openai_client.openai")
    def test_generate_success(self, mock_openai):
        """Test successful text generation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Generated response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient("test_api_key")
        result = client.generate("Test prompt")

        assert result == "Generated response"
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "Test prompt"}],
            max_tokens=1000
        )

    @patch("intent_kit.services.openai_client.openai")
    def test_generate_with_custom_model(self, mock_openai):
        """Test text generation with custom model."""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Generated response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient("test_api_key")
        result = client.generate("Test prompt", model="gpt-3.5-turbo")

        assert result == "Generated response"
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test prompt"}],
            max_tokens=1000
        )

    @patch("intent_kit.services.openai_client.openai")
    def test_generate_empty_response(self, mock_openai):
        """Test text generation with empty response."""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = None
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient("test_api_key")
        result = client.generate("Test prompt")

        assert result == ""

    @patch("intent_kit.services.openai_client.openai")
    def test_generate_no_choices(self, mock_openai):
        """Test text generation with no choices in response."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient("test_api_key")
        result = client.generate("Test prompt")

        assert result == ""

    @patch("intent_kit.services.openai_client.openai")
    def test_generate_exception_handling(self, mock_openai):
        """Test text generation with exception handling."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient("test_api_key")

        with pytest.raises(Exception, match="API Error"):
            client.generate("Test prompt")

    @patch("intent_kit.services.openai_client.openai")
    def test_generate_text_alias(self, mock_openai):
        """Test generate_text alias method."""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Generated response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient("test_api_key")
        result = client.generate_text("Test prompt", model="gpt-3.5-turbo")

        assert result == "Generated response"
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test prompt"}],
            max_tokens=1000
        )

    @patch("intent_kit.services.openai_client.openai")
    def test_generate_with_client_recreation(self, mock_openai):
        """Test generate when client needs to be recreated."""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Generated response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient("test_api_key")
        client._client = None  # Simulate client being None

        result = client.generate("Test prompt")

        assert result == "Generated response"
        # Should recreate client
        assert mock_openai.OpenAI.call_count == 2

    def test_is_available_method(self):
        """Test is_available class method."""
        # Test when openai is available
        with patch("intent_kit.services.openai_client.openai"):
            assert OpenAIClient.is_available() is True

        # Test when openai is not available
        with patch("intent_kit.services.openai_client.openai", side_effect=ImportError):
            assert OpenAIClient.is_available() is False

    @patch("intent_kit.services.openai_client.openai")
    def test_generate_with_different_prompts(self, mock_openai):
        """Test generate with different prompt types."""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient("test_api_key")

        # Test with simple prompt
        result1 = client.generate("Hello")
        assert result1 == "Response"

        # Test with complex prompt
        complex_prompt = "Please analyze the following text and provide a summary: This is a test."
        result2 = client.generate(complex_prompt)
        assert result2 == "Response"

        # Verify calls
        assert mock_client.chat.completions.create.call_count == 2

    @patch("intent_kit.services.openai_client.openai")
    def test_generate_with_different_models(self, mock_openai):
        """Test generate with different model types."""
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient("test_api_key")

        # Test with default model
        result1 = client.generate("Test")
        assert result1 == "Response"

        # Test with custom model
        result2 = client.generate("Test", model="gpt-3.5-turbo")
        assert result2 == "Response"

        # Test with another model
        result3 = client.generate("Test", model="gpt-4-turbo")
        assert result3 == "Response"

        # Verify different models were used
        calls = mock_client.chat.completions.create.call_args_list
        assert calls[0][1]["model"] == "gpt-4"
        assert calls[1][1]["model"] == "gpt-3.5-turbo"
        assert calls[2][1]["model"] == "gpt-4-turbo"