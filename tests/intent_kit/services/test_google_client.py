"""
Tests for Google client.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from intent_kit.services.google_client import GoogleClient


class TestGoogleClient:
    """Test GoogleClient class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        with patch("intent_kit.services.google_client.genai") as mock_genai:
            mock_client = Mock()
            mock_genai.Client.return_value = mock_client

            client = GoogleClient("test_api_key")

            assert client.api_key == "test_api_key"
            assert client._client == mock_client
            mock_genai.Client.assert_called_once_with(api_key="test_api_key")

    @patch("intent_kit.services.google_client.genai")
    def test_get_client_success(self, mock_genai):
        """Test successful client creation."""
        mock_client = Mock()
        mock_genai.Client.return_value = mock_client

        client = GoogleClient("test_api_key")
        result = client.get_client()

        assert result == mock_client
        mock_genai.Client.assert_called_once_with(api_key="test_api_key")

    @patch("intent_kit.services.google_client.genai")
    def test_get_client_import_error(self, mock_genai):
        """Test client creation when Google GenAI package is not installed."""
        mock_genai.side_effect = ImportError("No module named 'google.genai'")

        with pytest.raises(ImportError, match="Google GenAI package not installed"):
            GoogleClient("test_api_key")

    def test_ensure_imported_success(self):
        """Test _ensure_imported when client exists."""
        with patch("intent_kit.services.google_client.genai") as mock_genai:
            mock_client = Mock()
            mock_genai.Client.return_value = mock_client

            client = GoogleClient("test_api_key")
            # Should not raise
            client._ensure_imported()

    def test_ensure_imported_recreate_client(self):
        """Test _ensure_imported when client is None."""
        with patch("intent_kit.services.google_client.genai") as mock_genai:
            mock_client = Mock()
            mock_genai.Client.return_value = mock_client

            client = GoogleClient("test_api_key")
            client._client = None  # Simulate client being None

            client._ensure_imported()

            assert client._client == mock_client
            mock_genai.Client.assert_called_with(api_key="test_api_key")

    def test_ensure_imported_import_error(self):
        """Test _ensure_imported when import fails."""
        with patch("intent_kit.services.google_client.genai") as mock_genai:
            mock_genai.side_effect = ImportError("No module named 'google.genai'")

            client = GoogleClient("test_api_key")
            client._client = None  # Simulate client being None

            with pytest.raises(ImportError, match="Google GenAI package not installed"):
                client._ensure_imported()

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_success(self, mock_types, mock_genai):
        """Test successful text generation."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Generated response"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")
        result = client.generate("Test prompt")

        assert result == "Generated response"
        mock_client.models.generate_content.assert_called_once_with(
            model="gemini-2.0-flash-lite",
            contents=mock_content,
            config=mock_config,
        )

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_with_custom_model(self, mock_types, mock_genai):
        """Test text generation with custom model."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Generated response"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")
        result = client.generate("Test prompt", model="gemini-1.5-pro")

        assert result == "Generated response"
        mock_client.models.generate_content.assert_called_once_with(
            model="gemini-1.5-pro",
            contents=mock_content,
            config=mock_config,
        )

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_empty_response(self, mock_types, mock_genai):
        """Test text generation with empty response."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = None
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")
        result = client.generate("Test prompt")

        assert result == ""

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_exception_handling(self, mock_types, mock_genai):
        """Test text generation with exception handling."""
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")

        with pytest.raises(Exception, match="API Error"):
            client.generate("Test prompt")

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_with_logging(self, mock_types, mock_genai):
        """Test generate with debug logging."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Generated response"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        with patch("intent_kit.services.google_client.logger") as mock_logger:
            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt")

            assert result == "Generated response"
            mock_logger.debug.assert_called_once_with(
                "Google generate_text response: Generated response"
            )

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_with_error_logging(self, mock_types, mock_genai):
        """Test generate with error logging."""
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        with patch("intent_kit.services.google_client.logger") as mock_logger:
            client = GoogleClient("test_api_key")

            with pytest.raises(Exception, match="API Error"):
                client.generate("Test prompt")

            mock_logger.error.assert_called_once_with(
                "Error generating text with Google GenAI: API Error"
            )

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_with_client_recreation(self, mock_types, mock_genai):
        """Test generate when client needs to be recreated."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Generated response"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")
        client._client = None  # Simulate client being None

        result = client.generate("Test prompt")

        assert result == "Generated response"
        # Should recreate client
        assert mock_genai.Client.call_count == 2

    def test_is_available_method(self):
        """Test is_available class method."""
        # Test when google.genai is available
        with patch("intent_kit.services.google_client.genai"):
            assert GoogleClient.is_available() is True

        # Test when google.genai is not available
        with patch("intent_kit.services.google_client.genai", side_effect=ImportError):
            assert GoogleClient.is_available() is False

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_with_different_prompts(self, mock_types, mock_genai):
        """Test generate with different prompt types."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Response"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")

        # Test with simple prompt
        result1 = client.generate("Hello")
        assert result1 == "Response"

        # Test with complex prompt
        complex_prompt = "Please analyze the following text and provide a summary: This is a test."
        result2 = client.generate(complex_prompt)
        assert result2 == "Response"

        # Verify calls
        assert mock_client.models.generate_content.call_count == 2

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_with_different_models(self, mock_types, mock_genai):
        """Test generate with different model types."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Response"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")

        # Test with default model
        result1 = client.generate("Test")
        assert result1 == "Response"

        # Test with custom model
        result2 = client.generate("Test", model="gemini-1.5-pro")
        assert result2 == "Response"

        # Test with another model
        result3 = client.generate("Test", model="gemini-1.5-flash")
        assert result3 == "Response"

        # Verify different models were used
        calls = mock_client.models.generate_content.call_args_list
        assert calls[0][1]["model"] == "gemini-2.0-flash-lite"
        assert calls[1][1]["model"] == "gemini-1.5-pro"
        assert calls[2][1]["model"] == "gemini-1.5-flash"

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_content_structure(self, mock_types, mock_genai):
        """Test that content structure is created correctly."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "Response"
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")
        client.generate("Test prompt")

        # Verify content structure
        mock_types.Content.assert_called_once_with(
            role="user",
            parts=[mock_part],
        )
        mock_types.Part.from_text.assert_called_once_with(text="Test prompt")
        mock_types.GenerateContentConfig.assert_called_once_with(
            response_mime_type="text/plain",
        )

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_with_api_error(self, mock_types, mock_genai):
        """Test generate with API error handling."""
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("Rate limit exceeded")
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")

        with pytest.raises(Exception, match="Rate limit exceeded"):
            client.generate("Test prompt")

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_with_network_error(self, mock_types, mock_genai):
        """Test generate with network error handling."""
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("Connection timeout")
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")

        with pytest.raises(Exception, match="Connection timeout"):
            client.generate("Test prompt")

    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key."""
        with pytest.raises(TypeError):
            GoogleClient()

    def test_client_initialization_with_empty_api_key(self):
        """Test client initialization with empty API key."""
        with patch("intent_kit.services.google_client.genai") as mock_genai:
            mock_client = Mock()
            mock_genai.Client.return_value = mock_client

            client = GoogleClient("")
            assert client.api_key == ""
            assert client._client == mock_client

    @patch("intent_kit.services.google_client.genai")
    @patch("intent_kit.services.google_client.types")
    def test_generate_with_empty_string_response(self, mock_types, mock_genai):
        """Test generate with empty string response."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        # Mock the types
        mock_content = Mock()
        mock_part = Mock()
        mock_config = Mock()
        mock_types.Content.return_value = mock_content
        mock_types.Part.from_text.return_value = mock_part
        mock_types.GenerateContentConfig.return_value = mock_config

        client = GoogleClient("test_api_key")
        result = client.generate("Test prompt")

        assert result == ""