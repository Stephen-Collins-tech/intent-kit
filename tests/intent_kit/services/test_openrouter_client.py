"""Tests for the OpenRouter client."""

from unittest.mock import Mock, patch
from intent_kit.services.ai.openrouter_client import (
    OpenRouterClient,
    OpenRouterChatCompletionMessage,
    OpenRouterChoice,
    OpenRouterUsage,
    OpenRouterChatCompletion,
)


class TestOpenRouterChatCompletionMessage:
    """Test cases for OpenRouterChatCompletionMessage."""

    def test_message_creation(self):
        """Test creating a message with basic fields."""
        message = OpenRouterChatCompletionMessage(content="Hello, world!", role="user")

        assert message.content == "Hello, world!"
        assert message.role == "user"
        assert message.refusal is None
        assert message.annotations is None

    def test_message_creation_with_optional_fields(self):
        """Test creating a message with all optional fields."""
        message = OpenRouterChatCompletionMessage(
            content="Hello, world!",
            role="assistant",
            refusal="I cannot help with that",
            annotations={"confidence": 0.9},
            audio={"format": "mp3"},
            function_call={"name": "test_function"},
            tool_calls=[{"type": "function"}],
            reasoning="This is my reasoning",
        )

        assert message.content == "Hello, world!"
        assert message.role == "assistant"
        assert message.refusal == "I cannot help with that"
        assert message.annotations == {"confidence": 0.9}
        assert message.audio == {"format": "mp3"}
        assert message.function_call == {"name": "test_function"}
        assert message.tool_calls == [{"type": "function"}]
        assert message.reasoning == "This is my reasoning"

    def test_parse_content_plain_text(self):
        """Test parsing plain text content."""
        message = OpenRouterChatCompletionMessage(content="Hello, world!", role="user")

        result = message.parse_content()
        assert result == "Hello, world!"

    def test_parse_content_json(self):
        """Test parsing JSON content."""
        json_content = '{"message": "Hello", "status": "success"}'
        message = OpenRouterChatCompletionMessage(
            content=json_content, role="assistant"
        )

        result = message.parse_content()
        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"

    def test_parse_content_json_in_code_block(self):
        """Test parsing JSON content in code block."""
        json_content = '```json\n{"message": "Hello"}\n```'
        message = OpenRouterChatCompletionMessage(
            content=json_content, role="assistant"
        )

        result = message.parse_content()
        assert isinstance(result, dict)
        assert result["message"] == "Hello"

    def test_parse_content_generic_code_block(self):
        """Test parsing content in generic code block."""
        content = '```\n{"message": "Hello"}\n```'
        message = OpenRouterChatCompletionMessage(content=content, role="assistant")

        result = message.parse_content()
        assert isinstance(result, dict)
        assert result["message"] == "Hello"

    def test_parse_content_invalid_json(self):
        """Test parsing invalid JSON content."""
        invalid_json = '{"message": "Hello", "status":}'  # Missing value
        message = OpenRouterChatCompletionMessage(
            content=invalid_json, role="assistant"
        )

        result = message.parse_content()
        # The actual implementation tries to parse this and returns a dict with None for missing values
        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] is None

    @patch("intent_kit.services.ai.openrouter_client.YAML_AVAILABLE", True)
    @patch("intent_kit.services.ai.openrouter_client.yaml")
    def test_parse_content_yaml(self, mock_yaml):
        """Test parsing YAML content."""
        yaml_content = "message: Hello\nstatus: success"
        mock_yaml.safe_load.return_value = {"message": "Hello", "status": "success"}

        message = OpenRouterChatCompletionMessage(
            content=yaml_content, role="assistant"
        )

        result = message.parse_content()
        assert isinstance(result, dict)
        assert result["message"] == "Hello"
        assert result["status"] == "success"

    @patch("intent_kit.services.ai.openrouter_client.YAML_AVAILABLE", False)
    def test_parse_content_yaml_not_available(self):
        """Test parsing YAML content when YAML is not available."""
        yaml_content = "message: Hello\nstatus: success"
        message = OpenRouterChatCompletionMessage(
            content=yaml_content, role="assistant"
        )

        result = message.parse_content()
        assert result == yaml_content

    def test_display_plain_text(self):
        """Test displaying plain text message."""
        message = OpenRouterChatCompletionMessage(content="Hello, world!", role="user")

        result = message.display()
        assert "user: Hello, world!" in result

    def test_display_json_content(self):
        """Test displaying JSON content."""
        json_content = '{"message": "Hello"}'
        message = OpenRouterChatCompletionMessage(
            content=json_content, role="assistant"
        )

        result = message.display()
        assert "assistant:" in result
        assert '"message": "Hello"' in result

    def test_display_with_optional_fields(self):
        """Test displaying message with optional fields."""
        message = OpenRouterChatCompletionMessage(
            content="Hello, world!",
            role="assistant",
            refusal="I cannot help",
            annotations={"confidence": 0.9},
        )

        result = message.display()
        assert "assistant: Hello, world!" in result
        assert "(refusal: I cannot help)" in result
        assert "(annotations: {'confidence': 0.9})" in result


class TestOpenRouterChoice:
    """Test cases for OpenRouterChoice."""

    def test_choice_creation(self):
        """Test creating a choice with basic fields."""
        message = OpenRouterChatCompletionMessage(
            content="Hello, world!", role="assistant"
        )

        choice = OpenRouterChoice(
            finish_reason="stop", index=0, message=message, native_finish_reason="stop"
        )

        assert choice.finish_reason == "stop"
        assert choice.index == 0
        assert choice.message == message
        assert choice.native_finish_reason == "stop"
        assert choice.logprobs is None

    def test_choice_creation_with_logprobs(self):
        """Test creating a choice with logprobs."""
        message = OpenRouterChatCompletionMessage(
            content="Hello, world!", role="assistant"
        )

        choice = OpenRouterChoice(
            finish_reason="stop",
            index=0,
            message=message,
            native_finish_reason="stop",
            logprobs={"token_logprobs": [0.1, 0.2]},
        )

        assert choice.logprobs == {"token_logprobs": [0.1, 0.2]}

    def test_display_plain_text(self):
        """Test displaying choice with plain text."""
        message = OpenRouterChatCompletionMessage(
            content="Hello, world!", role="assistant"
        )

        choice = OpenRouterChoice(
            finish_reason="stop", index=0, message=message, native_finish_reason="stop"
        )

        result = choice.display()
        assert "Choice[0]: Hello, world!" in result

    def test_display_json_content(self):
        """Test displaying choice with JSON content."""
        message = OpenRouterChatCompletionMessage(
            content='{"message": "Hello"}', role="assistant"
        )

        choice = OpenRouterChoice(
            finish_reason="stop", index=0, message=message, native_finish_reason="stop"
        )

        result = choice.display()
        assert "Choice[0]:" in result
        assert '"message": "Hello"' in result

    def test_display_empty_content(self):
        """Test displaying choice with empty content."""
        message = OpenRouterChatCompletionMessage(content="", role="assistant")

        choice = OpenRouterChoice(
            finish_reason="stop", index=0, message=message, native_finish_reason="stop"
        )

        result = choice.display()
        assert (
            "Choice[0]: assistant (finish_reason: stop, native_finish_reason: stop)"
            in result
        )

    def test_str_representation(self):
        """Test string representation of choice."""
        message = OpenRouterChatCompletionMessage(
            content="Hello, world!", role="assistant"
        )

        choice = OpenRouterChoice(
            finish_reason="stop", index=0, message=message, native_finish_reason="stop"
        )

        result = str(choice)
        assert "Choice[0]: Hello, world!" in result

    def test_from_raw(self):
        """Test creating choice from raw object."""
        # Create mock raw choice object
        mock_message = Mock()
        mock_message.content = "Hello, world!"
        mock_message.role = "assistant"
        mock_message.refusal = None
        mock_message.annotations = None
        mock_message.audio = None
        mock_message.function_call = None
        mock_message.tool_calls = None
        mock_message.reasoning = None

        mock_raw_choice = Mock()
        mock_raw_choice.finish_reason = "stop"
        mock_raw_choice.index = 0
        mock_raw_choice.message = mock_message
        mock_raw_choice.native_finish_reason = "stop"
        mock_raw_choice.logprobs = None

        choice = OpenRouterChoice.from_raw(mock_raw_choice)

        assert choice.finish_reason == "stop"
        assert choice.index == 0
        assert choice.message.content == "Hello, world!"
        assert choice.message.role == "assistant"
        assert choice.native_finish_reason == "stop"

    def test_from_raw_with_missing_attributes(self):
        """Test creating choice from raw object with missing attributes."""
        # Create mock raw choice object with missing attributes
        mock_message = Mock()
        mock_message.content = "Hello, world!"
        mock_message.role = "assistant"

        mock_raw_choice = Mock()
        mock_raw_choice.finish_reason = "stop"
        mock_raw_choice.index = 0
        mock_raw_choice.message = mock_message
        mock_raw_choice.native_finish_reason = "stop"

        # Remove attributes to test fallbacks
        del mock_raw_choice.logprobs
        del mock_message.refusal
        del mock_message.annotations
        del mock_message.audio
        del mock_message.function_call
        del mock_message.tool_calls
        del mock_message.reasoning

        choice = OpenRouterChoice.from_raw(mock_raw_choice)

        assert choice.finish_reason == "stop"
        assert choice.index == 0
        assert choice.message.content == "Hello, world!"
        assert choice.message.role == "assistant"
        assert choice.native_finish_reason == "stop"
        assert choice.logprobs is None


class TestOpenRouterUsage:
    """Test cases for OpenRouterUsage."""

    def test_usage_creation(self):
        """Test creating usage object."""
        usage = OpenRouterUsage(
            prompt_tokens=100, completion_tokens=50, total_tokens=150
        )

        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150


class TestOpenRouterChatCompletion:
    """Test cases for OpenRouterChatCompletion."""

    def test_completion_creation(self):
        """Test creating completion object."""
        message = OpenRouterChatCompletionMessage(
            content="Hello, world!", role="assistant"
        )

        choice = OpenRouterChoice(
            finish_reason="stop", index=0, message=message, native_finish_reason="stop"
        )

        usage = OpenRouterUsage(
            prompt_tokens=100, completion_tokens=50, total_tokens=150
        )

        completion = OpenRouterChatCompletion(
            id="test-id",
            object="chat.completion",
            created=1234567890,
            model="test-model",
            choices=[choice],
            usage=usage,
        )

        assert completion.id == "test-id"
        assert completion.object == "chat.completion"
        assert completion.created == 1234567890
        assert completion.model == "test-model"
        assert len(completion.choices) == 1
        assert completion.choices[0] == choice
        assert completion.usage == usage

    def test_completion_creation_without_usage(self):
        """Test creating completion object without usage."""
        message = OpenRouterChatCompletionMessage(
            content="Hello, world!", role="assistant"
        )

        choice = OpenRouterChoice(
            finish_reason="stop", index=0, message=message, native_finish_reason="stop"
        )

        completion = OpenRouterChatCompletion(
            id="test-id",
            object="chat.completion",
            created=1234567890,
            model="test-model",
            choices=[choice],
        )

        assert completion.usage is None


class TestOpenRouterClient:
    """Test cases for OpenRouterClient."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = OpenRouterClient(api_key="test-key")

        assert client.api_key == "test-key"
        # The base client creates a logger with the name
        assert hasattr(client, "logger")

    def test_create_pricing_config(self):
        """Test creating pricing configuration."""
        client = OpenRouterClient(api_key="test-key")
        config = client._create_pricing_config()

        assert "openrouter" in config.providers
        openrouter_provider = config.providers["openrouter"]
        # Check that the provider has the expected structure
        assert hasattr(openrouter_provider, "models")

        # Check that some models are configured
        assert len(openrouter_provider.models) > 0
        assert "mistralai/mistral-7b-instruct" in openrouter_provider.models

    def test_ensure_imported(self):
        """Test ensuring client is imported."""
        client = OpenRouterClient(api_key="test-key")
        client._client = None

        with patch.object(client, "get_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            client._ensure_imported()

            assert client._client == mock_client
            mock_get_client.assert_called_once()

    def test_clean_response(self):
        """Test cleaning response content."""
        client = OpenRouterClient(api_key="test-key")

        # Test with normal content
        result = client._clean_response("Hello, world!")
        assert result == "Hello, world!"

        # Test with extra whitespace
        result = client._clean_response("  Hello, world!  \n")
        assert result == "Hello, world!"

        # Test with empty content
        result = client._clean_response("")
        assert result == ""

        result = client._clean_response(None)  # type: ignore
        assert result == ""

    @patch.object(OpenRouterClient, "_ensure_imported")
    @patch.object(OpenRouterClient, "calculate_cost")
    def test_generate_success(self, mock_calculate_cost, mock_ensure_imported):
        """Test successful text generation."""
        # Create mock client and response
        mock_client = Mock()
        mock_choice = Mock()
        mock_choice.finish_reason = "stop"
        mock_choice.index = 0
        mock_choice.native_finish_reason = "stop"
        mock_choice.logprobs = None

        mock_message = Mock()
        mock_message.content = "Hello, world!"
        mock_message.role = "assistant"
        mock_message.refusal = None
        mock_message.annotations = None
        mock_message.audio = None
        mock_message.function_call = None
        mock_message.tool_calls = None
        mock_message.reasoning = None
        mock_choice.message = mock_message

        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 50

        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        mock_response.id = "test-id"
        mock_response.object = "chat.completion"
        mock_response.created = 1234567890
        mock_response.model = "test-model"

        mock_client.chat.completions.create.return_value = mock_response

        client = OpenRouterClient(api_key="test-key")
        client._client = mock_client
        mock_calculate_cost.return_value = 0.01

        with patch(
            "intent_kit.services.ai.openrouter_client.PerfUtil"
        ) as mock_perf_util:
            mock_perf = Mock()
            mock_perf.start.return_value = None
            mock_perf.stop.return_value = 1.5
            mock_perf_util.return_value = mock_perf

            result = client.generate("Test prompt", "test-model")

            assert result.content == "Hello, world!"
            assert result.model == "test-model"
            assert result.provider == "openrouter"
            assert result.input_tokens == 100
            assert result.output_tokens == 50
            assert result.cost == 0.01
            assert result.duration == 1.5

            mock_client.chat.completions.create.assert_called_once_with(
                model="test-model",
                messages=[{"role": "user", "content": "Test prompt"}],
                max_tokens=1000,
            )

    @patch.object(OpenRouterClient, "_ensure_imported")
    @patch.object(OpenRouterClient, "calculate_cost")
    def test_generate_no_choices(self, mock_calculate_cost, mock_ensure_imported):
        """Test generation with no choices returned."""
        # Create mock client and response with no choices
        mock_client = Mock()
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 0

        mock_response = Mock()
        mock_response.choices = []
        mock_response.usage = mock_usage

        mock_client.chat.completions.create.return_value = mock_response

        client = OpenRouterClient(api_key="test-key")
        client._client = mock_client
        mock_calculate_cost.return_value = 0.01

        with patch(
            "intent_kit.services.ai.openrouter_client.PerfUtil"
        ) as mock_perf_util:
            mock_perf = Mock()
            mock_perf.start.return_value = None
            mock_perf.stop.return_value = 1.5
            mock_perf_util.return_value = mock_perf

            result = client.generate("Test prompt", "test-model")

            assert result.content == "No choices returned from model"
            assert result.model == "test-model"
            assert result.provider == "openrouter"
            assert result.input_tokens == 100
            assert result.output_tokens == 0
            assert result.cost == 0.01
            assert result.duration == 1.5

    @patch.object(OpenRouterClient, "_ensure_imported")
    @patch.object(OpenRouterClient, "calculate_cost")
    def test_generate_no_usage(self, mock_calculate_cost, mock_ensure_imported):
        """Test generation with no usage information."""
        # Create mock client and response with no usage
        mock_client = Mock()
        mock_choice = Mock()
        mock_choice.finish_reason = "stop"
        mock_choice.index = 0
        mock_choice.native_finish_reason = "stop"
        mock_choice.logprobs = None

        mock_message = Mock()
        mock_message.content = "Hello, world!"
        mock_message.role = "assistant"
        mock_message.refusal = None
        mock_message.annotations = None
        mock_message.audio = None
        mock_message.function_call = None
        mock_message.tool_calls = None
        mock_message.reasoning = None
        mock_choice.message = mock_message

        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.usage = None

        mock_client.chat.completions.create.return_value = mock_response

        client = OpenRouterClient(api_key="test-key")
        client._client = mock_client
        mock_calculate_cost.return_value = 0.01

        with patch(
            "intent_kit.services.ai.openrouter_client.PerfUtil"
        ) as mock_perf_util:
            mock_perf = Mock()
            mock_perf.start.return_value = None
            mock_perf.stop.return_value = 1.5
            mock_perf_util.return_value = mock_perf

            result = client.generate("Test prompt", "test-model")

            assert result.content == "Hello, world!"
            assert result.input_tokens == 0
            assert result.output_tokens == 0
            assert result.cost == 0.01
            assert result.duration == 1.5

    def test_calculate_cost_with_local_pricing(self):
        """Test cost calculation with local pricing."""
        client = OpenRouterClient(api_key="test-key")

        # Mock get_model_pricing to return a pricing object
        mock_pricing = Mock()
        mock_pricing.input_price_per_1m = 0.1
        mock_pricing.output_price_per_1m = 0.2

        with patch.object(client, "get_model_pricing", return_value=mock_pricing):
            cost = client.calculate_cost("test-model", "openrouter", 1000, 500)

            # Expected: (1000/1M * 0.1) + (500/1M * 0.2) = 0.0001 + 0.0001 = 0.0002
            expected_cost = (1000 / 1_000_000) * 0.1 + (500 / 1_000_000) * 0.2
            assert cost == expected_cost

    def test_calculate_cost_without_local_pricing(self):
        """Test cost calculation without local pricing."""
        client = OpenRouterClient(api_key="test-key")

        with patch.object(client, "get_model_pricing", return_value=None):
            with patch.object(client, "logger") as mock_logger:
                # Test that the method handles missing pricing gracefully
                cost = client.calculate_cost("test-model", "openrouter", 1000, 500)

                # Should return 0.0 when no pricing is available
                assert cost == 0.0
                mock_logger.warning.assert_called_once_with(
                    "No pricing found for model test-model, using base pricing service"
                )
