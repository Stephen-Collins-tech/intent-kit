"""
Tests for clarification node module.
"""

import pytest
from unittest.mock import Mock, patch
from intent_kit.nodes.clarification import ClarificationNode
from intent_kit.core.types import ExecutionResult


class TestClarificationNode:
    """Test the ClarificationNode class."""

    def test_clarification_node_initialization(self):
        """Test ClarificationNode initialization with all parameters."""
        node = ClarificationNode(
            name="test_clarification",
            clarification_message="Please clarify your request",
            available_options=["option1", "option2", "option3"],
            description="Test clarification node",
            llm_config={"model": "gpt-4", "provider": "openai"},
            custom_prompt="Custom clarification prompt: {user_input}",
        )
        
        assert node.name == "test_clarification"
        assert node.clarification_message == "Please clarify your request"
        assert node.available_options == ["option1", "option2", "option3"]
        assert node.description == "Test clarification node"
        assert node.llm_config == {"model": "gpt-4", "provider": "openai"}
        assert node.custom_prompt == "Custom clarification prompt: {user_input}"

    def test_clarification_node_initialization_defaults(self):
        """Test ClarificationNode initialization with defaults."""
        node = ClarificationNode(name="test_clarification")
        
        assert node.name == "test_clarification"
        assert node.clarification_message is None
        assert node.available_options == []
        assert node.description == "Ask user to clarify their intent"
        assert node.llm_config == {}
        assert node.custom_prompt is None

    def test_default_message(self):
        """Test the default clarification message."""
        node = ClarificationNode(name="test_clarification")
        message = node._default_message()
        
        assert "I'm not sure what you'd like me to do" in message
        assert "Could you please clarify your request" in message

    def test_execute_with_static_message(self):
        """Test execution with static clarification message."""
        node = ClarificationNode(
            name="test_clarification",
            clarification_message="Please provide more details",
            available_options=["option1", "option2"],
        )
        
        mock_ctx = Mock()
        result = node.execute("unclear input", mock_ctx)
        
        assert isinstance(result, ExecutionResult)
        assert result.data["clarification_message"] == "Please provide more details\n\nAvailable options:\n- option1\n- option2"
        assert result.data["original_input"] == "unclear input"
        assert result.data["available_options"] == ["option1", "option2"]
        assert result.data["node_type"] == "clarification"
        assert result.next_edges is None
        assert result.terminate is True
        assert result.context_patch["clarification_requested"] is True
        assert result.context_patch["original_input"] == "unclear input"
        assert result.context_patch["available_options"] == ["option1", "option2"]

    def test_execute_with_default_message(self):
        """Test execution with default clarification message."""
        node = ClarificationNode(name="test_clarification")
        
        mock_ctx = Mock()
        result = node.execute("unclear input", mock_ctx)
        
        assert isinstance(result, ExecutionResult)
        assert "I'm not sure what you'd like me to do" in result.data["clarification_message"]
        assert result.data["original_input"] == "unclear input"
        assert result.data["available_options"] == []
        assert result.terminate is True

    def test_execute_with_options(self):
        """Test execution with available options."""
        node = ClarificationNode(
            name="test_clarification",
            available_options=["search", "create", "delete"],
        )
        
        mock_ctx = Mock()
        result = node.execute("unclear input", mock_ctx)
        
        message = result.data["clarification_message"]
        assert "I'm not sure what you'd like me to do" in message
        assert "Available options:" in message
        assert "- search" in message
        assert "- create" in message
        assert "- delete" in message

    @patch('intent_kit.nodes.clarification.validate_raw_content')
    def test_execute_with_llm_generation(self, mock_validate_raw_content):
        """Test execution with LLM-generated clarification message."""
        node = ClarificationNode(
            name="test_clarification",
            llm_config={"model": "gpt-4", "provider": "openai"},
            custom_prompt="Generate clarification for: {user_input}",
        )
        
        # Mock context
        mock_ctx = Mock()
        mock_llm_service = Mock()
        mock_ctx.get.return_value = mock_llm_service
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Please provide more specific details about what you need."
        
        mock_llm_service.get_client.return_value.generate.return_value = mock_response
        mock_validate_raw_content.return_value = "Please provide more specific details about what you need."
        
        result = node.execute("unclear input", mock_ctx)
        
        assert isinstance(result, ExecutionResult)
        assert result.data["clarification_message"] == "Please provide more specific details about what you need."
        assert result.terminate is True

    def test_execute_with_llm_no_service(self):
        """Test execution when LLM service is not available."""
        node = ClarificationNode(
            name="test_clarification",
            llm_config={"model": "gpt-4", "provider": "openai"},
            custom_prompt="Generate clarification for: {user_input}",
        )
        
        mock_ctx = Mock()
        mock_ctx.get.return_value = None  # No LLM service
        
        result = node.execute("unclear input", mock_ctx)
        
        assert isinstance(result, ExecutionResult)
        assert "I'm not sure what you'd like me to do" in result.data["clarification_message"]
        assert result.terminate is True

    def test_execute_with_llm_no_config(self):
        """Test execution when LLM config is not available."""
        node = ClarificationNode(
            name="test_clarification",
            custom_prompt="Generate clarification for: {user_input}",
        )
        
        mock_ctx = Mock()
        mock_ctx.get.return_value = Mock()  # LLM service exists but no config
        
        result = node.execute("unclear input", mock_ctx)
        
        assert isinstance(result, ExecutionResult)
        assert "I'm not sure what you'd like me to do" in result.data["clarification_message"]
        assert result.terminate is True

    @patch('intent_kit.nodes.clarification.validate_raw_content')
    def test_execute_with_llm_error(self, mock_validate_raw_content):
        """Test execution when LLM generation fails."""
        node = ClarificationNode(
            name="test_clarification",
            llm_config={"model": "gpt-4", "provider": "openai"},
            custom_prompt="Generate clarification for: {user_input}",
        )
        
        # Mock context
        mock_ctx = Mock()
        mock_llm_service = Mock()
        mock_ctx.get.return_value = mock_llm_service
        
        # Mock LLM service to raise error
        mock_llm_service.get_client.return_value.generate.side_effect = Exception("LLM error")
        
        result = node.execute("unclear input", mock_ctx)
        
        assert isinstance(result, ExecutionResult)
        assert "I'm not sure what you'd like me to do" in result.data["clarification_message"]
        assert result.terminate is True

    def test_build_clarification_prompt_with_custom_prompt(self):
        """Test building clarification prompt with custom prompt."""
        node = ClarificationNode(
            name="test_clarification",
            custom_prompt="Custom prompt: {user_input}",
        )
        
        mock_ctx = Mock()
        prompt = node._build_clarification_prompt("test input", mock_ctx)
        
        assert prompt == "Custom prompt: test input"

    def test_build_clarification_prompt_without_custom_prompt(self):
        """Test building clarification prompt without custom prompt."""
        node = ClarificationNode(
            name="test_clarification",
            description="Test clarification",
            available_options=["option1", "option2"],
        )
        
        mock_ctx = Mock()
        mock_ctx.snapshot.return_value = {"user_id": "123"}
        
        prompt = node._build_clarification_prompt("test input", mock_ctx)
        
        assert "You are a helpful assistant that asks for clarification" in prompt
        assert "User Input: test input" in prompt
        assert "Clarification Task: test_clarification" in prompt
        assert "Description: Test clarification" in prompt
        assert "Available Context:" in prompt
        assert "{'user_id': '123'}" in prompt
        assert "Available Options:" in prompt
        assert "- option1" in prompt
        assert "- option2" in prompt
        assert "Generate a clarification message:" in prompt

    def test_build_clarification_prompt_no_context(self):
        """Test building clarification prompt without context."""
        node = ClarificationNode(
            name="test_clarification",
            available_options=["option1"],
        )
        
        mock_ctx = Mock()
        mock_ctx.snapshot.return_value = None
        
        prompt = node._build_clarification_prompt("test input", mock_ctx)
        
        assert "User Input: test input" in prompt
        assert "Available Context:" not in prompt
        assert "- option1" in prompt

    def test_build_clarification_prompt_no_options(self):
        """Test building clarification prompt without options."""
        node = ClarificationNode(name="test_clarification")
        
        mock_ctx = Mock()
        prompt = node._build_clarification_prompt("test input", mock_ctx)
        
        assert "User Input: test input" in prompt
        assert "Available Options:" in prompt
        # The prompt includes "Instructions:" which contains "- " characters
        # So we need to be more specific about checking for option list items
        assert "Available Options:\n" in prompt
        # Check that there are no option items after "Available Options:"
        options_section = prompt.split("Available Options:")[1]
        # Just check that there are no lines that start with "- " in the options section
        # but exclude the instructions section
        lines_after_options = options_section.split("\n\nInstructions:")[0].split("\n")
        option_lines = [line.strip() for line in lines_after_options if line.strip()]
        assert not any(line.startswith("- ") for line in option_lines)

    def test_format_message_with_custom_message(self):
        """Test formatting message with custom clarification message."""
        node = ClarificationNode(
            name="test_clarification",
            clarification_message="Please provide more details",
            available_options=["option1", "option2"],
        )
        
        message = node._format_message()
        
        assert message == "Please provide more details\n\nAvailable options:\n- option1\n- option2"

    def test_format_message_with_default_message(self):
        """Test formatting message with default clarification message."""
        node = ClarificationNode(
            name="test_clarification",
            available_options=["option1"],
        )
        
        message = node._format_message()
        
        assert "I'm not sure what you'd like me to do" in message
        assert "Could you please clarify your request" in message
        assert "Available options:" in message
        assert "- option1" in message

    def test_format_message_no_options(self):
        """Test formatting message without options."""
        node = ClarificationNode(
            name="test_clarification",
            clarification_message="Please clarify",
        )
        
        message = node._format_message()
        
        assert message == "Please clarify"
        assert "Available options:" not in message

    def test_format_message_default_no_options(self):
        """Test formatting message with default message and no options."""
        node = ClarificationNode(name="test_clarification")
        
        message = node._format_message()
        
        assert "I'm not sure what you'd like me to do" in message
        assert "Could you please clarify your request" in message
        assert "Available options:" not in message

    @patch('intent_kit.nodes.clarification.validate_raw_content')
    def test_generate_clarification_with_llm_success(self, mock_validate_raw_content):
        """Test successful LLM clarification generation."""
        node = ClarificationNode(
            name="test_clarification",
            llm_config={"model": "gpt-4", "provider": "openai"},
        )
        
        # Mock context
        mock_ctx = Mock()
        mock_llm_service = Mock()
        mock_ctx.get.return_value = mock_llm_service
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Please provide more specific details."
        
        mock_llm_service.get_client.return_value.generate.return_value = mock_response
        mock_validate_raw_content.return_value = "Please provide more specific details."
        
        result = node._generate_clarification_with_llm("test input", mock_ctx)
        
        assert result == "Please provide more specific details."

    def test_generate_clarification_with_llm_no_service(self):
        """Test LLM clarification generation when service is not available."""
        node = ClarificationNode(
            name="test_clarification",
            llm_config={"model": "gpt-4", "provider": "openai"},
        )
        
        mock_ctx = Mock()
        mock_ctx.get.return_value = None
        
        result = node._generate_clarification_with_llm("test input", mock_ctx)
        
        assert "I'm not sure what you'd like me to do" in result

    def test_generate_clarification_with_llm_no_config(self):
        """Test LLM clarification generation when config is not available."""
        node = ClarificationNode(name="test_clarification")
        
        mock_ctx = Mock()
        mock_ctx.get.return_value = Mock()
        
        result = node._generate_clarification_with_llm("test input", mock_ctx)
        
        assert "I'm not sure what you'd like me to do" in result

    @patch('intent_kit.nodes.clarification.validate_raw_content')
    def test_generate_clarification_with_llm_error(self, mock_validate_raw_content):
        """Test LLM clarification generation when it fails."""
        node = ClarificationNode(
            name="test_clarification",
            llm_config={"model": "gpt-4", "provider": "openai"},
        )
        
        # Mock context
        mock_ctx = Mock()
        mock_llm_service = Mock()
        mock_ctx.get.return_value = mock_llm_service
        
        # Mock LLM service to raise error
        mock_llm_service.get_client.return_value.generate.side_effect = Exception("LLM error")
        
        result = node._generate_clarification_with_llm("test input", mock_ctx)
        
        assert "I'm not sure what you'd like me to do" in result

    def test_execute_metrics_empty(self):
        """Test that execution returns empty metrics."""
        node = ClarificationNode(name="test_clarification")
        
        mock_ctx = Mock()
        result = node.execute("test input", mock_ctx)
        
        assert result.metrics == {}