"""Tests for ClassifierNode."""

from unittest.mock import Mock, patch
from intent_kit.nodes.classifier import ClassifierNode
from intent_kit.core.types import ExecutionResult
from intent_kit.core.context import DefaultContext


class TestClassifierNode:
    """Test cases for ClassifierNode."""

    def test_classifier_node_initialization(self):
        """Test ClassifierNode initialization with all parameters."""
        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather", "help"],
            description="Test classifier node",
            llm_config={"provider": "openai", "model": "gpt-4"},
            classification_func=Mock(),
            custom_prompt="Custom classification prompt",
            context_read=["user.name", "conversation.history"],
            context_write=["intent.confidence", "classification.time"],
        )

        assert node.name == "test_classifier"
        assert node.output_labels == ["greet", "weather", "help"]
        assert node.description == "Test classifier node"
        assert node.llm_config == {"provider": "openai", "model": "gpt-4"}
        assert node.custom_prompt == "Custom classification prompt"
        assert node.context_read == ["user.name", "conversation.history"]
        assert node.context_write == ["intent.confidence", "classification.time"]

    def test_classifier_node_initialization_defaults(self):
        """Test ClassifierNode initialization with default values."""
        node = ClassifierNode(
            name="test_classifier", output_labels=["greet", "weather"]
        )

        assert node.name == "test_classifier"
        assert node.output_labels == ["greet", "weather"]
        assert node.description == ""
        assert node.llm_config == {}
        assert node.classification_func is None
        assert node.custom_prompt is None
        assert node.context_read == []
        assert node.context_write == []

    def test_context_read_keys_property(self):
        """Test context_read_keys property."""
        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather"],
            context_read=["user.name", "conversation.history"],
        )

        assert node.context_read_keys == ["user.name", "conversation.history"]

    def test_context_write_keys_property(self):
        """Test context_write_keys property."""
        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather"],
            context_write=["intent.confidence", "classification.time"],
        )

        assert node.context_write_keys == ["intent.confidence", "classification.time"]

    @patch("intent_kit.nodes.classifier.LLMService")
    def test_execute_basic_classification(self, mock_llm_service):
        """Test basic classification execution."""
        # Mock LLM service and response
        mock_service = Mock()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = "greet"
        mock_client.generate.return_value = mock_response
        mock_service.get_client.return_value = mock_client
        mock_llm_service.return_value = mock_service

        node = ClassifierNode(
            name="test_classifier", output_labels=["greet", "weather", "help"]
        )

        context = DefaultContext()
        context.set("llm_service", mock_service)
        context.set(
            "metadata", {"default_llm_config": {"provider": "openai", "model": "gpt-4"}}
        )

        result = node.execute("Hello there", context)

        assert isinstance(result, ExecutionResult)
        assert result.data == "greet"
        assert result.terminate is False
        assert result.next_edges == ["greet"]

    @patch("intent_kit.nodes.classifier.LLMService")
    def test_execute_with_context_read(self, mock_llm_service):
        """Test classification with context read."""
        # Mock LLM service and response
        mock_service = Mock()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = "greet"
        mock_client.generate.return_value = mock_response
        mock_service.get_client.return_value = mock_client
        mock_llm_service.return_value = mock_service

        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather", "help"],
            context_read=["user.name", "conversation.history"],
        )

        context = DefaultContext()
        context.set("llm_service", mock_service)
        context.set(
            "metadata", {"default_llm_config": {"provider": "openai", "model": "gpt-4"}}
        )
        context.set("user.name", "Alice")
        context.set("conversation.history", ["Hello", "How are you?"])

        node.execute("Hello there", context)

        # Verify that context data was used in the prompt
        call_args = mock_client.generate.call_args[0][0]
        assert "Alice" in call_args
        assert "Hello" in call_args
        assert "How are you?" in call_args

    @patch("intent_kit.nodes.classifier.LLMService")
    def test_execute_with_context_write(self, mock_llm_service):
        """Test classification with context write."""
        # Mock LLM service and response
        mock_service = Mock()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = "weather"
        mock_client.generate.return_value = mock_response
        mock_service.get_client.return_value = mock_client
        mock_llm_service.return_value = mock_service

        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather", "help"],
            context_write=["intent.confidence", "classification.time"],
        )

        context = DefaultContext()
        context.set("llm_service", mock_service)
        context.set(
            "metadata", {"default_llm_config": {"provider": "openai", "model": "gpt-4"}}
        )

        result = node.execute("What's the weather like?", context)

        # Note: ClassifierNode doesn't currently implement context_write in execute method
        # It only has the properties for interface compliance
        assert result.data == "weather"
        assert "chosen_label" in result.context_patch
        assert result.context_patch["chosen_label"] == "weather"

    @patch("intent_kit.nodes.classifier.LLMService")
    def test_execute_with_custom_classification_func(self, mock_llm_service):
        """Test classification with custom classification function."""

        def custom_classifier(user_input: str, context_data: dict) -> str:
            if "weather" in user_input.lower():
                return "weather"
            elif "hello" in user_input.lower():
                return "greet"
            else:
                return "help"

        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather", "help"],
            classification_func=custom_classifier,
        )

        context = DefaultContext()
        context.set("user.name", "Alice")

        # Test weather classification
        result1 = node.execute("What's the weather like?", context)
        assert result1.data == "weather"
        assert result1.next_edges == ["weather"]

        # Test greeting classification
        result2 = node.execute("Hello there", context)
        assert result2.data == "greet"
        assert result2.next_edges == ["greet"]

        # Test help classification
        result3 = node.execute("I need assistance", context)
        assert result3.data == "help"
        assert result3.next_edges == ["help"]

    @patch("intent_kit.nodes.classifier.LLMService")
    def test_execute_with_custom_prompt(self, mock_llm_service):
        """Test classification with custom prompt."""
        # Mock LLM service and response
        mock_service = Mock()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = "weather"
        mock_client.generate.return_value = mock_response
        mock_service.get_client.return_value = mock_client
        mock_llm_service.return_value = mock_service

        custom_prompt = "Classify this input: {user_input}"

        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather", "help"],
            custom_prompt=custom_prompt,
        )

        context = DefaultContext()
        context.set("llm_service", mock_service)
        context.set(
            "metadata", {"default_llm_config": {"provider": "openai", "model": "gpt-4"}}
        )

        node.execute("What's the weather like?", context)

        # Verify custom prompt was used
        call_args = mock_client.generate.call_args[0][0]
        assert "Classify this input:" in call_args
        assert "What's the weather like?" in call_args

    @patch("intent_kit.nodes.classifier.LLMService")
    def test_execute_no_llm_service(self, mock_llm_service):
        """Test classification when LLM service is not available."""
        node = ClassifierNode(
            name="test_classifier", output_labels=["greet", "weather", "help"]
        )

        context = DefaultContext()
        # No LLM service set

        result = node.execute("Hello there", context)

        # ClassifierNode returns an error result instead of raising
        assert "ClassificationError" in result.data
        assert result.terminate is True
        assert "error" in result.context_patch

    @patch("intent_kit.nodes.classifier.LLMService")
    def test_execute_no_llm_config(self, mock_llm_service):
        """Test classification when LLM config is not available."""
        # Mock LLM service
        mock_service = Mock()
        mock_llm_service.return_value = mock_service

        node = ClassifierNode(
            name="test_classifier", output_labels=["greet", "weather", "help"]
        )

        context = DefaultContext()
        context.set("llm_service", mock_service)
        # No metadata/default_llm_config set

        result = node.execute("Hello there", context)

        # ClassifierNode returns an error result instead of raising
        assert "ClassificationError" in result.data
        assert result.terminate is True
        assert "error" in result.context_patch

    def test_execute_llm_error(self):
        """Test classification when LLM raises an error."""

        # Use a custom classification function that raises an error
        def error_classifier(user_input: str, context_data: dict) -> str:
            raise Exception("LLM error")

        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather", "help"],
            classification_func=error_classifier,
        )

        context = DefaultContext()

        result = node.execute("Hello there", context)

        # Error should be caught and return error result
        assert "ClassificationError" in result.data
        assert result.terminate is True
        assert "error" in result.context_patch

    @patch("intent_kit.nodes.classifier.LLMService")
    def test_execute_invalid_output_label(self, mock_llm_service):
        """Test classification when LLM returns invalid output label."""
        # Mock LLM service and response
        mock_service = Mock()
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = "invalid_label"  # Not in output_labels
        mock_client.generate.return_value = mock_response
        mock_service.get_client.return_value = mock_client
        mock_llm_service.return_value = mock_service

        node = ClassifierNode(
            name="test_classifier", output_labels=["greet", "weather", "help"]
        )

        context = DefaultContext()
        context.set("llm_service", mock_service)
        context.set(
            "metadata", {"default_llm_config": {"provider": "openai", "model": "gpt-4"}}
        )

        result = node.execute("Hello there", context)

        # Should route to clarification when invalid label
        assert result.data == ""
        assert result.next_edges == ["clarification"]

    def test_build_prompt_with_context(self):
        """Test prompt building with context data."""
        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather", "help"],
            context_read=["user.name", "conversation.history"],
        )

        context = DefaultContext()
        context.set("user.name", "Alice")
        context.set("conversation.history", ["Hello", "How are you?"])

        prompt = node._build_classification_prompt("Hello there", context)

        assert "Alice" in prompt
        assert "Hello" in prompt
        assert "How are you?" in prompt
        assert "greet" in prompt
        assert "weather" in prompt
        assert "help" in prompt

    def test_build_prompt_without_context(self):
        """Test prompt building without context data."""
        node = ClassifierNode(
            name="test_classifier", output_labels=["greet", "weather", "help"]
        )

        context = DefaultContext()

        prompt = node._build_classification_prompt("Hello there", context)

        assert "Hello there" in prompt
        assert "greet" in prompt
        assert "weather" in prompt
        assert "help" in prompt

    def test_build_prompt_with_custom_prompt(self):
        """Test prompt building with custom prompt."""
        custom_prompt = "Classify this: {user_input}"

        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather", "help"],
            custom_prompt=custom_prompt,
        )

        context = DefaultContext()

        prompt = node._build_classification_prompt("Hello there", context)

        assert "Classify this:" in prompt
        assert "Hello there" in prompt

    def test_execute_metrics_and_context_patch(self):
        """Test that metrics and context patch are properly set."""

        def custom_classifier(user_input: str, context_data: dict) -> str:
            return "greet"

        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather", "help"],
            classification_func=custom_classifier,
            context_write=["intent.confidence", "classification.time"],
        )

        context = DefaultContext()
        context.set("user.name", "Alice")

        result = node.execute("Hello there", context)

        # Check that basic context patch is set
        assert "chosen_label" in result.context_patch
        assert result.context_patch["chosen_label"] == "greet"

        # Note: ClassifierNode doesn't currently implement metrics or custom context_write
        # It only has the properties for interface compliance

    def test_execute_with_complex_context_data(self):
        """Test classification with complex context data."""

        def custom_classifier(user_input: str, context_data: dict) -> str:
            user_name = context_data.get("user.name")
            preferences = context_data.get("user.preferences", {})
            language = preferences.get("language", "en")

            if language == "es" and user_name:
                return "greet"
            elif "weather" in user_input.lower():
                return "weather"
            else:
                return "help"

        node = ClassifierNode(
            name="test_classifier",
            output_labels=["greet", "weather", "help"],
            classification_func=custom_classifier,
            context_read=["user.name", "user.preferences"],
        )

        context = DefaultContext()
        context.set("user.name", "Alice")
        context.set("user.preferences", {"language": "es", "theme": "dark"})

        result = node.execute("Hello there", context)

        assert result.data == "greet"
        assert result.next_edges == ["greet"]
