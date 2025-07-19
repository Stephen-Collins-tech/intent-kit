"""
Tests for OpenRouter client functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Optional

from intent_kit.services.openrouter_client import OpenRouterClient


class TestOpenRouterClient:
    """Test cases for OpenRouterClient class."""

    def test_init_with_api_key(self):
        """Test OpenRouterClient initialization with API key."""
        client = OpenRouterClient("test_api_key")
        
        assert client.api_key == "test_api_key"
        assert client._client is None

    def test_get_client_success(self):
        """Test successful client creation."""
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai_client = Mock()
            mock_openai.OpenAI.return_value = mock_openai_client
            
            client = OpenRouterClient("test_api_key")
            result = client.get_client()
            
            assert result == mock_openai_client
            mock_openai.OpenAI.assert_called_once_with(
                api_key="test_api_key",
                base_url="https://openrouter.ai/api/v1"
            )

    def test_get_client_import_error(self):
        """Test client creation when openai is not installed."""
        with patch('intent_kit.services.openrouter_client.openai', None):
            client = OpenRouterClient("test_api_key")
            
            with pytest.raises(ImportError) as exc_info:
                client.get_client()
            
            assert "OpenAI package not installed" in str(exc_info.value)

    def test_ensure_imported_success(self):
        """Test _ensure_imported when client is None."""
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai_client = Mock()
            mock_openai.OpenAI.return_value = mock_openai_client
            
            client = OpenRouterClient("test_api_key")
            client._client = None
            client._ensure_imported()
            
            assert client._client == mock_openai_client

    def test_ensure_imported_already_imported(self):
        """Test _ensure_imported when client already exists."""
        mock_client = Mock()
        client = OpenRouterClient("test_api_key")
        client._client = mock_client
        
        client._ensure_imported()
        
        # Should not change the existing client
        assert client._client == mock_client

    def test_clean_response_empty(self):
        """Test cleaning empty response."""
        client = OpenRouterClient("test_api_key")
        
        result = client._clean_response("")
        assert result == ""
        
        result = client._clean_response(None)
        assert result == ""

    def test_clean_response_with_content(self):
        """Test cleaning response with content."""
        client = OpenRouterClient("test_api_key")
        
        result = client._clean_response("  hello world  \n")
        assert result == "hello world"
        
        result = client._clean_response("  multiple\n  lines  ")
        assert result == "multiple\n  lines"

    def test_generate_success(self):
        """Test successful text generation."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Generated response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            result = client.generate("test prompt")
            
            assert result == "Generated response"
            mock_client.chat.completions.create.assert_called_once_with(
                model="openrouter-default",
                messages=[{"role": "user", "content": "test prompt"}],
                max_tokens=1000
            )

    def test_generate_with_custom_model(self):
        """Test text generation with custom model."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Custom model response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            result = client.generate("test prompt", model="custom-model")
            
            assert result == "Custom model response"
            mock_client.chat.completions.create.assert_called_once_with(
                model="custom-model",
                messages=[{"role": "user", "content": "test prompt"}],
                max_tokens=1000
            )

    def test_generate_empty_response(self):
        """Test text generation with empty response."""
        mock_response = Mock()
        mock_response.choices = []
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            result = client.generate("test prompt")
            
            assert result == ""

    def test_generate_none_content(self):
        """Test text generation with None content."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = None
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            result = client.generate("test prompt")
            
            assert result == ""

    def test_generate_exception_handling(self):
        """Test text generation with exception."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            
            with pytest.raises(Exception) as exc_info:
                client.generate("test prompt")
            
            assert "API Error" in str(exc_info.value)

    def test_generate_text_alias(self):
        """Test generate_text alias method."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Alias response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            result = client.generate_text("test prompt")
            
            assert result == "Alias response"

    def test_initialize_client(self):
        """Test _initialize_client method."""
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai_client = Mock()
            mock_openai.OpenAI.return_value = mock_openai_client
            
            client = OpenRouterClient("test_api_key")
            client._initialize_client()
            
            assert client._client == mock_openai_client

    def test_generate_with_client_recreation(self):
        """Test generation when client needs to be recreated."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Recreated response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            client._client = None  # Simulate client being None
            result = client.generate("test prompt")
            
            assert result == "Recreated response"
            assert client._client == mock_client

    def test_generate_with_different_prompts(self):
        """Test generation with different prompts."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            
            # Test different prompts
            client.generate("prompt 1")
            client.generate("prompt 2")
            
            assert mock_client.chat.completions.create.call_count == 2
            calls = mock_client.chat.completions.create.call_args_list
            assert calls[0][1]["messages"][0]["content"] == "prompt 1"
            assert calls[1][1]["messages"][0]["content"] == "prompt 2"

    def test_generate_with_different_models(self):
        """Test generation with different models."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            
            # Test different models
            client.generate("prompt", model="model1")
            client.generate("prompt", model="model2")
            
            assert mock_client.chat.completions.create.call_count == 2
            calls = mock_client.chat.completions.create.call_args_list
            assert calls[0][1]["model"] == "model1"
            assert calls[1][1]["model"] == "model2"

    def test_generate_with_empty_string_response(self):
        """Test generation with empty string response."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = ""
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            result = client.generate("test prompt")
            
            assert result == ""

    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key."""
        with pytest.raises(TypeError):
            OpenRouterClient(None)

    def test_client_initialization_with_empty_api_key(self):
        """Test client initialization with empty API key."""
        client = OpenRouterClient("")
        
        # Should not raise an error, but client creation might fail
        assert client.api_key == ""

    def test_generate_with_api_error(self):
        """Test generation with API error."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            
            with pytest.raises(Exception) as exc_info:
                client.generate("test prompt")
            
            assert "Rate limit exceeded" in str(exc_info.value)

    def test_generate_with_network_error(self):
        """Test generation with network error."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("Connection failed")
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            
            with pytest.raises(Exception) as exc_info:
                client.generate("test prompt")
            
            assert "Connection failed" in str(exc_info.value)


class TestOpenRouterClientIntegration:
    """Integration tests for OpenRouterClient."""

    def test_full_workflow(self):
        """Test complete workflow from initialization to generation."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Integration test response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            # Initialize client
            client = OpenRouterClient("test_api_key")
            
            # Generate text
            result = client.generate("integration test prompt")
            
            # Verify results
            assert result == "Integration test response"
            assert client._client == mock_client
            assert client.api_key == "test_api_key"

    def test_multiple_generations(self):
        """Test multiple generations with the same client."""
        mock_responses = []
        for i in range(3):
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = f"Response {i+1}"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_responses.append(mock_response)
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = mock_responses
        
        with patch('intent_kit.services.openrouter_client.openai') as mock_openai:
            mock_openai.OpenAI.return_value = mock_client
            
            client = OpenRouterClient("test_api_key")
            
            # Generate multiple responses
            results = []
            for i in range(3):
                result = client.generate(f"prompt {i+1}")
                results.append(result)
            
            # Verify results
            assert results == ["Response 1", "Response 2", "Response 3"]
            assert mock_client.chat.completions.create.call_count == 3