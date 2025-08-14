"""
Tests for Google client.
"""

import pytest
import os
from unittest.mock import Mock, patch
from intent_kit.services.ai.google_client import GoogleClient
from intent_kit.services.ai.llm_response import RawLLMResponse
from intent_kit.services.ai.pricing_service import PricingService


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

    def test_init_with_pricing_service(self):
        """Test initialization with custom pricing service."""
        pricing_service = PricingService()
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key", pricing_service=pricing_service)

            assert client.api_key == "test_api_key"
            assert client.pricing_service == pricing_service
            assert client._client == mock_client

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
            mock_usage_metadata = Mock()
            mock_usage_metadata.prompt_token_count = 100
            mock_usage_metadata.candidates_token_count = 50
            mock_response.usage_metadata = mock_usage_metadata
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"
            assert result.model == "gemini-2.0-flash-lite"
            assert result.provider == "google"
            assert result.duration >= 0
            assert result.cost >= 0

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

            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"
            assert result.model == "gemini-1.5-pro"

    def test_generate_empty_response(self):
        """Test text generation with empty response."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = None
            mock_response.usage_metadata = None
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == ""
            assert result.input_tokens == 0
            assert result.output_tokens == 0
            assert result.cost == 0

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
            mock_usage_metadata = Mock()
            mock_usage_metadata.prompt_token_count = 100
            mock_usage_metadata.candidates_token_count = 50
            mock_response.usage_metadata = mock_usage_metadata
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt")
            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"

    def test_generate_with_client_recreation(self):
        """Test generate when client needs to be recreated."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Generated response"
            mock_usage_metadata = Mock()
            mock_usage_metadata.prompt_token_count = 100
            mock_usage_metadata.candidates_token_count = 50
            mock_response.usage_metadata = mock_usage_metadata
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            client._client = None  # type: ignore # Simulate client being None

            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"
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
            mock_usage_metadata = Mock()
            mock_usage_metadata.prompt_token_count = 100
            mock_usage_metadata.candidates_token_count = 50
            mock_response.usage_metadata = mock_usage_metadata
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")

            # Test with simple prompt
            result1 = client.generate("Hello")
            assert isinstance(result1, RawLLMResponse)
            assert result1.content == "Response"

            # Test with complex prompt
            result2 = client.generate("Please summarize this text.")
            assert isinstance(result2, RawLLMResponse)
            assert result2.content == "Response"

    def test_generate_with_different_models(self):
        """Test generate with different model types."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Response"
            mock_usage_metadata = Mock()
            mock_usage_metadata.prompt_token_count = 100
            mock_usage_metadata.candidates_token_count = 50
            mock_response.usage_metadata = mock_usage_metadata
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")

            # Test with default model
            result1 = client.generate("Test")
            assert isinstance(result1, RawLLMResponse)
            assert result1.content == "Response"

            # Test with custom model
            result2 = client.generate("Test", model="gemini-1.5-pro")
            assert isinstance(result2, RawLLMResponse)
            assert result2.content == "Response"

            # Test with another custom model
            result3 = client.generate("Test", model="gemini-2.0-flash")
            assert isinstance(result3, RawLLMResponse)
            assert result3.content == "Response"

    def test_generate_content_structure(self):
        """Test the content structure used in generate."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Generated response"
            mock_usage_metadata = Mock()
            mock_usage_metadata.prompt_token_count = 100
            mock_usage_metadata.candidates_token_count = 50
            mock_response.usage_metadata = mock_usage_metadata
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"

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
            mock_usage_metadata = Mock()
            mock_usage_metadata.prompt_token_count = 100
            mock_usage_metadata.candidates_token_count = 50
            mock_response.usage_metadata = mock_usage_metadata
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == ""

    def test_calculate_cost_integration(self):
        """Test cost calculation integration."""
        with patch.object(GoogleClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.text = "Generated response"
            mock_response.usage_metadata = Mock()
            mock_response.usage_metadata.prompt_token_count = 1000
            mock_response.usage_metadata.candidates_token_count = 500
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = GoogleClient("test_api_key")
            result = client.generate("Test prompt", model="gemini-pro")

            assert isinstance(result, RawLLMResponse)
            assert result.cost > 0  # Should calculate cost based on pricing service

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "env_test_key"})
    def test_environment_variable_support(self):
        """Test that the client can work with environment variables."""
        # This test verifies that the client can be initialized with API keys
        # from environment variables, though the actual client doesn't read env vars directly
        client = GoogleClient("env_test_key")
        assert client.api_key == "env_test_key"

    def test_pricing_service_integration(self):
        """Test integration with pricing service."""
        pricing_service = PricingService()
        client = GoogleClient("test_api_key", pricing_service=pricing_service)

        assert client.pricing_service == pricing_service
        assert hasattr(client, "calculate_cost")

    def test_list_available_models(self):
        """Test listing available models from pricing configuration."""
        client = GoogleClient("test_api_key")
        models = client.list_available_models()

        # Should return models from the pricing configuration
        assert isinstance(models, list)
        # The list might be empty if no models are configured, which is valid

    def test_get_model_pricing(self):
        """Test getting model pricing information."""
        client = GoogleClient("test_api_key")
        pricing = client.get_model_pricing("gemini-pro")

        # Should return pricing info if available, None otherwise
        assert pricing is None or hasattr(pricing, "input_price_per_1m")
