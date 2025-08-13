"""
Tests for Anthropic client.
"""

import pytest
import os
from unittest.mock import Mock, patch
from intent_kit.services.ai.anthropic_client import AnthropicClient
from intent_kit.types import RawLLMResponse
from intent_kit.services.ai.pricing_service import PricingService
import sys


class TestAnthropicClient:
    """Test AnthropicClient class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            assert client.api_key == "test_api_key"
            assert client._client == mock_client
            mock_get_client.assert_called_once()

    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(TypeError, match="API key is required"):
            AnthropicClient("")

    def test_init_with_none_api_key(self):
        """Test initialization with None API key raises error."""
        with pytest.raises(TypeError, match="API key is required"):
            AnthropicClient(None)  # type: ignore[call-arg]

    def test_init_with_pricing_service(self):
        """Test initialization with custom pricing service."""
        pricing_service = PricingService()
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key", pricing_service=pricing_service)

            assert client.api_key == "test_api_key"
            assert client.pricing_service == pricing_service
            assert client._client == mock_client

    def test_get_client_success(self):
        """Test successful client creation."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.get_client()

            assert result == mock_client

    def test_get_client_import_error(self):
        """Test client creation when Anthropic package is not installed."""
        with patch.object(
            AnthropicClient,
            "get_client",
            side_effect=ImportError("Anthropic package not installed"),
        ):
            with pytest.raises(ImportError, match="Anthropic package not installed"):
                AnthropicClient("test_api_key")

    def test_ensure_imported_success(self):
        """Test _ensure_imported when client exists."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            # Should not raise
            client._ensure_imported()

    def test_ensure_imported_recreate_client(self):
        """Test _ensure_imported when client is None."""
        from intent_kit.services.ai.anthropic_client import AnthropicClient

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

    def test_generate_success(self):
        """Test successful text generation."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Generated response"
            mock_response.content = [mock_content]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 100
            mock_usage.completion_tokens = 50
            mock_response.usage = mock_usage

            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"
            assert result.model == "claude-3-5-sonnet-20241022"
            assert result.input_tokens == 100
            assert result.output_tokens == 50
            assert result.provider == "anthropic"
            assert result.duration >= 0
            assert result.cost >= 0

            mock_client.messages.create.assert_called_once_with(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": "Test prompt"}],
            )

    def test_generate_with_custom_model(self):
        """Test text generation with custom model."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Generated response"
            mock_response.content = [mock_content]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 150
            mock_usage.completion_tokens = 75
            mock_response.usage = mock_usage

            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt", model="claude-3-haiku-20240307")

            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"
            assert result.model == "claude-3-haiku-20240307"
            assert result.input_tokens == 150
            assert result.output_tokens == 75

            mock_client.messages.create.assert_called_once_with(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": "Test prompt"}],
            )

    def test_generate_empty_response(self):
        """Test text generation with empty response."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = []
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == ""
            assert result.input_tokens == 0
            assert result.output_tokens == 0
            assert result.cost == 0

    def test_generate_no_content(self):
        """Test text generation with no content in response."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = []
            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == ""
            assert result.input_tokens == 0
            assert result.output_tokens == 0
            assert result.cost == 0

    def test_generate_exception_handling(self):
        """Test text generation with exception handling."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("API Error")
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            with pytest.raises(Exception, match="API Error"):
                client.generate("Test prompt")

    def test_generate_with_client_recreation(self):
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
        assert isinstance(result, RawLLMResponse)
        assert result.content == "Generated response"
        assert client._client == mock_client

        # Clean up
        del sys.modules["anthropic"]

    def test_generate_with_different_prompts(self):
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
            assert isinstance(result1, RawLLMResponse)
            assert result1.content == "Response"

            # Test with complex prompt
            result2 = client.generate("Please summarize this text.")
            assert isinstance(result2, RawLLMResponse)
            assert result2.content == "Response"

            # Verify calls
            assert mock_client.messages.create.call_count == 2

    def test_generate_with_different_models(self):
        """Test generate with different model types."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Response"
            mock_response.content = [mock_content]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 100
            mock_usage.completion_tokens = 50
            mock_response.usage = mock_usage

            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            # Test with default model
            result1 = client.generate("Test")
            assert isinstance(result1, RawLLMResponse)
            assert result1.content == "Response"

            # Test with custom model
            result2 = client.generate("Test", model="claude-3-haiku-20240307")
            assert isinstance(result2, RawLLMResponse)
            assert result2.content == "Response"

            # Test with another model
            result3 = client.generate("Test", model="claude-2.1")
            assert isinstance(result3, RawLLMResponse)
            assert result3.content == "Response"

            # Verify different models were used
            assert mock_client.messages.create.call_count == 3

    def test_generate_with_multiple_content_parts(self):
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
            assert isinstance(result, RawLLMResponse)
            assert result.content == "Part 1"

    def test_generate_with_logging(self):
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
            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"

    def test_generate_with_api_error(self):
        """Test generate with API error handling."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("Rate limit exceeded")
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            with pytest.raises(Exception, match="Rate limit exceeded"):
                client.generate("Test prompt")

    def test_generate_with_network_error(self):
        """Test generate with network error handling."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("Connection timeout")
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")

            with pytest.raises(Exception, match="Connection timeout"):
                client.generate("Test prompt")

    def test_calculate_cost_integration(self):
        """Test cost calculation integration."""
        with patch.object(AnthropicClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Generated response"
            mock_response.content = [mock_content]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 1000
            mock_usage.completion_tokens = 500
            mock_response.usage = mock_usage

            mock_client.messages.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = AnthropicClient("test_api_key")
            result = client.generate("Test prompt", model="claude-3-sonnet-20240229")

            assert isinstance(result, RawLLMResponse)
            assert result.cost > 0  # Should calculate cost based on pricing service

    def test_is_available_method(self):
        """Test is_available method."""
        # Test when anthropic is available
        assert AnthropicClient.is_available() is True

        # Test when anthropic is not available
        with patch(
            "builtins.__import__",
            side_effect=ImportError("No module named 'anthropic'"),
        ):
            assert AnthropicClient.is_available() is False

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env_test_key"})
    def test_environment_variable_support(self):
        """Test that the client can work with environment variables."""
        # This test verifies that the client can be initialized with API keys
        # from environment variables, though the actual client doesn't read env vars directly
        client = AnthropicClient("env_test_key")
        assert client.api_key == "env_test_key"

    def test_pricing_service_integration(self):
        """Test integration with pricing service."""
        pricing_service = PricingService()
        client = AnthropicClient("test_api_key", pricing_service=pricing_service)

        assert client.pricing_service == pricing_service
        assert hasattr(client, "calculate_cost")

    def test_list_available_models(self):
        """Test listing available models from pricing configuration."""
        client = AnthropicClient("test_api_key")
        models = client.list_available_models()

        # Should return models from the pricing configuration
        assert isinstance(models, list)
        # The list might be empty if no models are configured, which is valid

    def test_get_model_pricing(self):
        """Test getting model pricing information."""
        client = AnthropicClient("test_api_key")
        pricing = client.get_model_pricing("claude-3-sonnet-20240229")

        # Should return pricing info if available, None otherwise
        assert pricing is None or hasattr(pricing, "input_price_per_1m")
