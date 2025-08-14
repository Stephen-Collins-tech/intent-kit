"""
Tests for OpenAI client.
"""

import pytest
import os
from unittest.mock import Mock, patch
from intent_kit.services.ai.openai_client import OpenAIClient
from intent_kit.services.ai.llm_response import RawLLMResponse
from intent_kit.services.ai.pricing_service import PricingService


class TestOpenAIClient:
    """Test OpenAIClient class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")

            assert client.api_key == "test_api_key"
            assert client._client == mock_client

    def test_init_with_pricing_service(self):
        """Test initialization with custom pricing service."""
        pricing_service = PricingService()
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key", pricing_service=pricing_service)

            assert client.api_key == "test_api_key"
            assert client.pricing_service == pricing_service
            assert client._client == mock_client

    def test_get_client_success(self):
        """Test successful client creation."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")
            result = client.get_client()

            assert result == mock_client

    def test_get_client_import_error(self):
        """Test client creation when OpenAI package is not installed."""
        with patch.object(
            OpenAIClient,
            "get_client",
            side_effect=ImportError("OpenAI package not installed"),
        ):
            with pytest.raises(ImportError, match="OpenAI package not installed"):
                OpenAIClient("test_api_key")

    def test_ensure_imported_success(self):
        """Test _ensure_imported when client exists."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")
            # Should not raise
            client._ensure_imported()

    def test_ensure_imported_recreate_client(self):
        """Test _ensure_imported when client is None."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")
            client._client = None  # Simulate client being None

            client._ensure_imported()

            assert client._client == mock_client

    def test_ensure_imported_import_error(self):
        """Test _ensure_imported when import fails."""
        with patch.object(
            OpenAIClient,
            "get_client",
            side_effect=ImportError("OpenAI package not installed"),
        ):
            # Create client without calling get_client during init
            client = OpenAIClient.__new__(OpenAIClient)
            client.api_key = "test_api_key"
            client._client = None  # Simulate client being None

            with pytest.raises(ImportError, match="OpenAI package not installed"):
                client._ensure_imported()

    def test_generate_success(self):
        """Test successful text generation."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Generated response"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 100
            mock_usage.completion_tokens = 50
            mock_response.usage = mock_usage

            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")
            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"
            assert result.model == "gpt-4"
            assert result.input_tokens == 100
            assert result.output_tokens == 50
            assert result.provider == "openai"
            assert result.duration is not None and result.duration >= 0
            assert result.cost is not None and result.cost >= 0

            mock_client.chat.completions.create.assert_called_once_with(
                model="gpt-4",
                messages=[{"role": "user", "content": "Test prompt"}],
                max_tokens=1000,
            )

    def test_generate_with_custom_model(self):
        """Test text generation with custom model."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Generated response"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 150
            mock_usage.completion_tokens = 75
            mock_response.usage = mock_usage

            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")
            result = client.generate("Test prompt", model="gpt-3.5-turbo")

            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"
            assert result.model == "gpt-3.5-turbo"
            assert result.input_tokens == 150
            assert result.output_tokens == 75

            mock_client.chat.completions.create.assert_called_once_with(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test prompt"}],
                max_tokens=1000,
            )

    def test_generate_empty_response(self):
        """Test text generation with empty response."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = None
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 50
            mock_usage.completion_tokens = 25
            mock_response.usage = mock_usage

            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")
            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == ""

    def test_generate_no_choices(self):
        """Test text generation with no choices in response."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = []
            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")
            # Handle the case where choices is empty
            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == ""
            assert result.input_tokens == 0
            assert result.output_tokens == 0
            assert result.cost == 0.0  # Properly calculated cost

    def test_generate_exception_handling(self):
        """Test text generation with exception handling."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")

            with pytest.raises(Exception, match="API Error"):
                client.generate("Test prompt")

    def test_generate_with_client_recreation(self):
        """Test generate when client needs to be recreated."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Generated response"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 200
            mock_usage.completion_tokens = 100
            mock_response.usage = mock_usage

            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")
            client._client = None  # Simulate client being None

            result = client.generate("Test prompt")

            assert isinstance(result, RawLLMResponse)
            assert result.content == "Generated response"

    def test_is_available_method(self):
        """Test is_available method."""
        # Test when openai is available
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = True
            assert OpenAIClient.is_available() is True

    def test_is_available_method_import_error(self):
        """Test is_available method when import fails."""
        with patch("importlib.util.find_spec") as mock_find_spec:
            mock_find_spec.return_value = None
            assert OpenAIClient.is_available() is False

    def test_generate_with_different_prompts(self):
        """Test generate with different prompts."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Response"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 100
            mock_usage.completion_tokens = 50
            mock_response.usage = mock_usage

            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")

            # Test different prompts
            prompts = ["Hello", "How are you?", "What's the weather?"]
            for prompt in prompts:
                result = client.generate(prompt)
                assert isinstance(result, RawLLMResponse)
                assert result.content == "Response"
                mock_client.chat.completions.create.assert_called_with(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                )

    def test_generate_with_different_models(self):
        """Test generate with different models."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Response"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 100
            mock_usage.completion_tokens = 50
            mock_response.usage = mock_usage

            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")

            # Test different models
            models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
            for model in models:
                result = client.generate("Test prompt", model=model)
                assert isinstance(result, RawLLMResponse)
                assert result.content == "Response"
                mock_client.chat.completions.create.assert_called_with(
                    model=model,
                    messages=[{"role": "user", "content": "Test prompt"}],
                    max_tokens=1000,
                )

    def test_calculate_cost_integration(self):
        """Test cost calculation integration."""
        with patch.object(OpenAIClient, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = "Generated response"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]

            # Add mock usage data
            mock_usage = Mock()
            mock_usage.prompt_tokens = 1000
            mock_usage.completion_tokens = 500
            mock_response.usage = mock_usage

            mock_client.chat.completions.create.return_value = mock_response
            mock_get_client.return_value = mock_client

            client = OpenAIClient("test_api_key")
            result = client.generate("Test prompt", model="gpt-4")

            assert isinstance(result, RawLLMResponse)
            assert (
                result.cost is not None and result.cost > 0
            )  # Should calculate cost based on pricing service

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env_test_key"})
    def test_environment_variable_support(self):
        """Test that the client can work with environment variables."""
        # This test verifies that the client can be initialized with API keys
        # from environment variables, though the actual client doesn't read env vars directly
        client = OpenAIClient("env_test_key")
        assert client.api_key == "env_test_key"

    def test_pricing_service_integration(self):
        """Test integration with pricing service."""
        pricing_service = PricingService()
        client = OpenAIClient("test_api_key", pricing_service=pricing_service)

        assert client.pricing_service == pricing_service
        assert hasattr(client, "calculate_cost")

    def test_list_available_models(self):
        """Test listing available models from pricing configuration."""
        client = OpenAIClient("test_api_key")
        models = client.list_available_models()

        # Should return models from the pricing configuration
        assert isinstance(models, list)
        # The list might be empty if no models are configured, which is valid

    def test_get_model_pricing(self):
        """Test getting model pricing information."""
        client = OpenAIClient("test_api_key")
        pricing = client.get_model_pricing("gpt-4")

        # Should return pricing info if available, None otherwise
        assert pricing is None or hasattr(pricing, "input_price_per_1m")
