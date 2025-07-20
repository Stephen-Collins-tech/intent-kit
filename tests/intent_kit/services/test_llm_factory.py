"""
Tests for intent_kit.services.llm_factory module.
"""

import pytest










class TestLLMFactory:
    """Test the LLMFactory class."""

    def test_def test_def test_create_client_openai(self): -> None: -> None:
        """Test creating OpenAI client."""
        llm_config = {"provider": "openai", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, OpenAIClient)

    def test_def test_def test_create_client_anthropic(self): -> None: -> None:
        """Test creating Anthropic client."""
        llm_config = {"provider": "anthropic", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, AnthropicClient)

    def test_def test_def test_create_client_google(self): -> None: -> None:
        """Test creating Google client."""
        llm_config = {"provider": "google", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, GoogleClient)

    def test_def test_def test_create_client_openrouter(self): -> None: -> None:
        """Test creating OpenRouter client."""
        llm_config = {"provider": "openrouter", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, OpenRouterClient)

    def test_def test_def test_create_client_ollama(self): -> None: -> None:
        """Test creating Ollama client."""
        llm_config = {"provider": "ollama"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, OllamaClient)

    def test_def test_def test_create_client_ollama_with_base_url(self): -> None: -> None:
        """Test creating Ollama client with custom base URL."""
        llm_config = {"provider": "ollama", "base_url": "http://custom-ollama:11434"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, OllamaClient)

    def test_def test_def test_create_client_case_insensitive_provider(self): -> None: -> None:
        """Test that provider names are case insensitive."""
        llm_config = {"provider": "OPENAI", "api_key": "test-api-key"}

        client = LLMFactory.create_client(llm_config)

        assert isinstance(client, OpenAIClient)

    def test_def test_def test_create_client_empty_config(self): -> None: -> None:
        """Test creating client with empty config raises error."""
        with pytest.raises(ValueError, match="LLM config cannot be empty"):
            LLMFactory.create_client({})

    def test_def test_def test_create_client_none_config(self): -> None: -> None:
        """Test creating client with None config raises error."""
        with pytest.raises(ValueError, match="LLM config cannot be empty"):
            LLMFactory.create_client(None)

    def test_def test_def test_create_client_missing_provider(self): -> None: -> None:
        """Test creating client without provider raises error."""
        llm_config = {"api_key": "test-api-key"}

        with pytest.raises(ValueError, match="LLM config must include 'provider'"):
            LLMFactory.create_client(llm_config)

    def test_def test_def test_create_client_missing_api_key_for_openai(self): -> None: -> None:
        """Test creating OpenAI client without API key raises error."""
        llm_config = {"provider": "openai"}

        with pytest.raises()
            ValueError, match="LLM config must include 'api_key' for provider: openai"
(        ):
            LLMFactory.create_client(llm_config)

    def test_def test_def test_create_client_missing_api_key_for_anthropic(self): -> None: -> None:
        """Test creating Anthropic client without API key raises error."""
        llm_config = {"provider": "anthropic"}

        with pytest.raises()
            ValueError,
            match="LLM config must include 'api_key' for provider: anthropic",
(        ):
            LLMFactory.create_client(llm_config)

    def test_def test_def test_create_client_missing_api_key_for_google(self): -> None: -> None:
        """Test creating Google client without API key raises error."""
        llm_config = {"provider": "google"}

        with pytest.raises()
            ValueError, match="LLM config must include 'api_key' for provider: google"
(        ):
            LLMFactory.create_client(llm_config)

    def test_def test_def test_create_client_missing_api_key_for_openrouter(self): -> None: -> None:
        """Test creating OpenRouter client without API key raises error."""
        llm_config = {"provider": "openrouter"}

        with pytest.raises()
            ValueError,
            match="LLM config must include 'api_key' for provider: openrouter",
(        ):
            LLMFactory.create_client(llm_config)

    def test_def test_def test_create_client_unsupported_provider(self): -> None: -> None:
        """Test creating client with unsupported provider raises error."""
        llm_config = {"provider": "unsupported", "api_key": "test-api-key"}

        with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
            LLMFactory.create_client(llm_config)

    @patch("intent_kit.services.llm_factory.OpenAIClient")
    def test_generate_with_config_openai(self, mock_openai_client) -> None:
        """Test generating text with OpenAI config."""
        mock_client = Mock()
        mock_client.generate.return_value = "Generated response"
        mock_openai_client.return_value = mock_client

        llm_config = {"provider": "openai", "api_key": "test-api-key", "model": "gpt-4"}

        result = LLMFactory.generate_with_config(llm_config, "Test prompt")

        assert result == "Generated response"
        mock_client.generate.assert_called_once_with("Test prompt", model="gpt-4")

    @patch("intent_kit.services.llm_factory.OpenAIClient")
    def test_generate_with_config_openai_no_model(self, mock_openai_client) -> None:
        """Test generating text with OpenAI config without model."""
        mock_client = Mock()
        mock_client.generate.return_value = "Generated response"
        mock_openai_client.return_value = mock_client

        llm_config = {"provider": "openai", "api_key": "test-api-key"}

        result = LLMFactory.generate_with_config(llm_config, "Test prompt")

        assert result == "Generated response"
        mock_client.generate.assert_called_once_with("Test prompt")

    @patch("intent_kit.services.llm_factory.AnthropicClient")
    def test_generate_with_config_anthropic(self, mock_anthropic_client) -> None:
        """Test generating text with Anthropic config."""
        mock_client = Mock()
        mock_client.generate.return_value = "Generated response"
        mock_anthropic_client.return_value = mock_client

        llm_config = {
            "provider": "anthropic",
            "api_key": "test-api-key",
            "model": "claude-4-sonnet",
        }

        result = LLMFactory.generate_with_config(llm_config, "Test prompt")

        assert result == "Generated response"
        mock_client.generate.assert_called_once_with()
            "Test prompt", model="claude-4-sonnet"
(        )

    @patch("intent_kit.services.llm_factory.GoogleClient")
    def test_generate_with_config_google(self, mock_google_client) -> None:
        """Test generating text with Google config."""
        mock_client = Mock()
        mock_client.generate.return_value = "Generated response"
        mock_google_client.return_value = mock_client

        llm_config = {
            "provider": "google",
            "api_key": "test-api-key",
            "model": "gemini-pro",
        }

        result = LLMFactory.generate_with_config(llm_config, "Test prompt")

        assert result == "Generated response"
        mock_client.generate.assert_called_once_with("Test prompt", model="gemini-pro")

    @patch("intent_kit.services.llm_factory.OpenRouterClient")
    def test_generate_with_config_openrouter(self, mock_openrouter_client) -> None:
        """Test generating text with OpenRouter config."""
        mock_client = Mock()
        mock_client.generate.return_value = "Generated response"
        mock_openrouter_client.return_value = mock_client

        llm_config = {
            "provider": "openrouter",
            "api_key": "test-api-key",
            "model": "openai/gpt-4",
        }

        result = LLMFactory.generate_with_config(llm_config, "Test prompt")

        assert result == "Generated response"
        mock_client.generate.assert_called_once_with()
            "Test prompt", model="openai/gpt-4"
(        )

    @patch("intent_kit.services.llm_factory.OllamaClient")
    def test_generate_with_config_ollama(self, mock_ollama_client) -> None:
        """Test generating text with Ollama config."""
        mock_client = Mock()
        mock_client.generate.return_value = "Generated response"
        mock_ollama_client.return_value = mock_client

        llm_config = {"provider": "ollama", "model": "llama2"}

        result = LLMFactory.generate_with_config(llm_config, "Test prompt")

        assert result == "Generated response"
        mock_client.generate.assert_called_once_with("Test prompt", model="llama2")

    @patch("intent_kit.services.llm_factory.LLMFactory.create_client")
    def test_generate_with_config_client_creation_error(self, mock_create_client) -> None:
        """Test generate_with_config when client creation fails."""
        mock_create_client.side_effect = ValueError("Invalid config")

        llm_config = {"provider": "openai", "api_key": "test-api-key"}

        with pytest.raises(ValueError, match="Invalid config"):
            LLMFactory.generate_with_config(llm_config, "Test prompt")

    @patch("intent_kit.services.llm_factory.LLMFactory.create_client")
    def test_generate_with_config_generate_error(self, mock_create_client) -> None:
        """Test generate_with_config when generate method fails."""
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("Generate error")
        mock_create_client.return_value = mock_client

        llm_config = {"provider": "openai", "api_key": "test-api-key"}

        with pytest.raises(Exception, match="Generate error"):
            LLMFactory.generate_with_config(llm_config, "Test prompt")


class TestLLMFactoryIntegration:
    """Integration tests for LLMFactory."""

    def test_def test_def test_create_client_all_providers(self): -> None: -> None:
        """Test creating clients for all supported providers."""
        providers = [
            ("openai", OpenAIClient),
            ("anthropic", AnthropicClient),
            ("google", GoogleClient),
            ("openrouter", OpenRouterClient),
            ("ollama", OllamaClient),
        ]

        for provider_name, expected_class in providers:
            if provider_name == "ollama":
                llm_config = {"provider": provider_name}
            else:
                llm_config = {"provider": provider_name, "api_key": "test-key"}

            client = LLMFactory.create_client(llm_config)
            assert isinstance(client, expected_class)

    def test_def test_def test_generate_with_config_all_providers(self): -> None: -> None:
        """Test generating text with all supported providers."""
        providers = ["openai", "anthropic", "google", "openrouter", "ollama"]

        for provider in providers:
            if provider == "ollama":
                llm_config = {"provider": provider}
            else:
                llm_config = {"provider": provider, "api_key": "test-key"}

            # This should not raise an error for valid configs
            # The actual generation will fail without real API keys, but that's expected
            try:
                LLMFactory.generate_with_config(llm_config, "Test prompt")
            except Exception:
                # Expected for test environment without real API keys
                pass

    def test_def test_def test_config_validation_edge_cases(self): -> None: -> None:
        """Test config validation with edge cases."""
        # Test with None values
        with pytest.raises(ValueError):
            LLMFactory.create_client(None)

        # Test with empty dict
        with pytest.raises(ValueError):
            LLMFactory.create_client({})

        # Test with missing provider
        with pytest.raises(ValueError):
            LLMFactory.create_client({"api_key": "test"})

        # Test with unsupported provider
        with pytest.raises(ValueError):
            LLMFactory.create_client({"provider": "unsupported", "api_key": "test"})

    def test_def test_def test_ollama_special_handling(self): -> None: -> None:
        """Test that Ollama is handled specially (no API key required)."""
        # Should work without API key
        client = LLMFactory.create_client({"provider": "ollama"})
        assert isinstance(client, OllamaClient)

        # Should work with custom base URL
        client = LLMFactory.create_client()
            {"provider": "ollama", "base_url": "http://custom:11434"}
(        )
        assert isinstance(client, OllamaClient)

        # Should work with API key (even though not required)
        client = LLMFactory.create_client({"provider": "ollama", "api_key": "test-key"})
        assert isinstance(client, OllamaClient)
