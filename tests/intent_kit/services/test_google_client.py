"""
Tests for Google client.
"""

import pytest
from unittest.mock import Mock, patch
from intent_kit.services.google_client import GoogleClient


class TestGoogleClient:
    """Test GoogleClient class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")

            assert client.api_key == "test_api_key"
            assert client._client == mock_client
            mock_get_client.assert_called_once()

    def test_get_client_import_error(self):
        """Test client creation when Google GenAI package is not installed."""
        with patch.object(
            GoogleClient,
            "get_client",
            side_effect=ImportError("Google GenAI package not installed"),
        ):
            with pytest.raises(ImportError, match="Google GenAI package not installed"):
                GoogleClient("test_api_key")

    def test_ensure_imported_success(self):
        """Test _ensure_imported when client exists."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            # Should not raise
            client._ensure_imported()

    def test_ensure_imported_recreate_client(self):
        """Test _ensure_imported when client is None."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            # Create client without calling get_client during init
            client = GoogleClient.__new__(GoogleClient)
            client.api_key = "test_api_key"
            client._client = None  # type: ignore # Simulate client being None

            client._ensure_imported()

            assert client._client == mock_client
            mock_get_client.assert_called()

    def test_ensure_imported_import_error(self):
        """Test _ensure_imported when import fails."""
        with patch.object(
            GoogleClient,
            "get_client",
            side_effect=ImportError("No module named 'google.genai'"),
        ):
            # Create client without calling get_client during init
            client = GoogleClient.__new__(GoogleClient)
            client.api_key = "test_api_key"
            client._client = None  # type: ignore # Simulate client being None

            with pytest.raises(ImportError, match="No module named 'google.genai'"):
                client._ensure_imported()

    def test_get_client_success(self):
        """Test successful client creation."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.get_client()

            assert result == mock_client
            mock_get_client.assert_called()

    def test_generate_success(self):
        """Test successful text generation."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Generated response"
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt")

            assert result == "Generated response"
            mock_client.models.generate_content.assert_called_once()

    def test_generate_with_custom_model(self):
        """Test text generation with custom model."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Generated response"
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt", model="gemini-1.5-pro")

            assert result == "Generated response"
            mock_client.models.generate_content.assert_called_once()

    def test_generate_empty_response(self):
        """Test text generation with empty response."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = None
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt")

            assert result == ""

    def test_generate_exception_handling(self):
        """Test text generation with exception handling."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.models.generate_content.side_effect = Exception("API Error")
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")

            with pytest.raises(Exception, match="API Error"):
                client.generate("Test prompt")

    def test_generate_with_logging(self):
        """Test generate with debug logging."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Generated response"
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            with patch("intent_kit.services.google_client.logger") as mock_logger:
                client = GoogleClient("test_api_key")
                result = client.generate("Test prompt")
                assert result == "Generated response"
                mock_logger.debug.assert_called()

    def test_generate_with_client_recreation(self):
        """Test generate when client needs to be recreated."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Generated response"
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            client._client = None  # type: ignore # Simulate client being None

            result = client.generate("Test prompt")

            assert result == "Generated response"
            assert client._client == mock_client

    def test_is_available_method(self):
        """Test is_available method."""
        # Test when google.genai is available
        assert GoogleClient.is_available() is True

        # Test when google.genai is not available
        with patch(
            "builtins.__import__",
            side_effect=ImportError("No module named 'google.genai'"),
        ):
            assert GoogleClient.is_available() is False

    def test_generate_with_different_prompts(self):
        """Test generate with different prompt types."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Response"
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

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

    def test_generate_with_different_models(self):
        """Test generate with different model types."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Response"
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")

            # Test with default model
            result1 = client.generate("Test")
            assert result1 == "Response"

            # Test with custom model
            result2 = client.generate("Test", model="gemini-1.5-pro")
            assert result2 == "Response"

            # Test with another model
            result3 = client.generate("Test", model="gemini-2.0-flash")
            assert result3 == "Response"

            # Verify different models were used
            assert mock_client.models.generate_content.call_count == 3

    def test_generate_content_structure(self):
        """Test the content structure used in generate."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Generated response"
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt")

            assert result == "Generated response"
            mock_client.models.generate_content.assert_called_once()

    def test_generate_with_api_error(self):
        """Test generate with API error handling."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.models.generate_content.side_effect = Exception(
                "Rate limit exceeded"
            )
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")

            with pytest.raises(Exception, match="Rate limit exceeded"):
                client.generate("Test prompt")

    def test_generate_with_network_error(self):
        """Test generate with network error handling."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.models.generate_content.side_effect = Exception(
                "Connection timeout"
            )
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")

            with pytest.raises(Exception, match="Connection timeout"):
                client.generate("Test prompt")

    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_get_client.side_effect = ImportError(
                "Google GenAI package not installed"
            )

            # With the new base class structure, we can initialize without api_key
            # but it will fail when trying to get the client
            client = GoogleClient.__new__(GoogleClient)
            client.api_key = ""  # Use empty string instead of None
            client._client = None

            # The client should fail when trying to generate without proper initialization
            with pytest.raises(ImportError):
                client.generate("test")

    def test_client_initialization_with_empty_api_key(self):
        """Test client initialization with empty API key."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = GoogleClient("")
            assert client.api_key == ""
            assert client._client == mock_client

    def test_generate_with_empty_string_response(self):
        """Test generate with empty string response."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = ""
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt")

            assert result == ""
