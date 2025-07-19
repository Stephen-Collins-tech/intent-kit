"""
Tests for the LLM Clarifier functionality.
"""

import pytest
from unittest.mock import Mock, patch
from intent_kit.node.actions import create_llm_clarifier, get_default_clarification_prompt, create_llm_clarifier_node
from intent_kit.node.enums import NodeType
from intent_kit.node.types import ExecutionResult, ExecutionError
from intent_kit.context import IntentContext


class TestLLMClarifier:
    """Test cases for LLM Clarifier functionality."""

    def test_get_default_clarification_prompt(self):
        """Test that the default clarification prompt is properly formatted."""
        prompt = get_default_clarification_prompt()
        
        assert isinstance(prompt, str)
        assert "You are a helpful assistant" in prompt
        assert "{user_input}" in prompt
        assert "{context_info}" in prompt
        assert "{expected_format}" in prompt
        assert "{max_attempts}" in prompt

    def test_create_llm_clarifier_basic(self):
        """Test creating a basic LLM clarifier function."""
        # Mock LLM config
        mock_llm_config = {"provider": "openrouter", "model": "google/gemma-3-27b-it"}
        
        # Mock LLM response
        mock_response = "I need more details about your booking request. Please specify the destination and date."
        
        with patch('intent_kit.services.llm_factory.LLMFactory.generate_with_config') as mock_generate:
            mock_generate.return_value = mock_response
            
            clarifier_func = create_llm_clarifier(
                llm_config=mock_llm_config,
                clarification_prompt_template="Generate a clarification for: {user_input}",
                expected_response_format="Please specify: [destination] [date]",
                max_clarification_attempts=3
            )
            
            result = clarifier_func("book something")
            
            assert result == mock_response + "\n\nPlease provide your response in the following format: Please specify: [destination] [date]"
            mock_generate.assert_called_once()

    def test_create_llm_clarifier_with_context(self):
        """Test LLM clarifier with context information."""
        mock_llm_config = {"provider": "openrouter", "model": "google/gemma-3-27b-it"}
        mock_response = "Based on your previous bookings, I need more details about your flight request."
        
        with patch('intent_kit.services.llm_factory.LLMFactory.generate_with_config') as mock_generate:
            mock_generate.return_value = mock_response
            
            clarifier_func = create_llm_clarifier(
                llm_config=mock_llm_config,
                clarification_prompt_template="Generate a clarification for: {user_input}\n{context_info}",
                expected_response_format="Please specify: [details]"
            )
            
            context = {"previous_bookings": "Paris, London", "user_preferences": "window seat"}
            result = clarifier_func("book flight", context=context)
            
            assert mock_response in result
            mock_generate.assert_called_once()

    def test_create_llm_clarifier_fallback_on_error(self):
        """Test that LLM clarifier falls back to simple message on error."""
        mock_llm_config = {"provider": "openrouter", "model": "switchpoint/router"}
        
        with patch('intent_kit.services.llm_factory.LLMFactory.generate_with_config') as mock_generate:
            mock_generate.side_effect = Exception("API error")
            
            clarifier_func = create_llm_clarifier(
                llm_config=mock_llm_config,
                clarification_prompt_template="Generate a clarification for: {user_input}",
                expected_response_format="Please specify: [details]"
            )
            
            result = clarifier_func("book something")
            
            assert "Your request 'book something' is unclear" in result
            assert "Please specify: [details]" in result

    def test_create_llm_clarifier_node(self):
        """Test creating an LLM clarifier node."""
        mock_llm_config = {"provider": "openrouter", "model": "switchpoint/router"}
        mock_response = "I need more details about your request."
        
        with patch('intent_kit.services.llm_factory.LLMFactory.generate_with_config') as mock_generate:
            mock_generate.return_value = mock_response
            
            node = create_llm_clarifier_node(
                name="test_llm_clarifier",
                llm_config=mock_llm_config,
                expected_response_format="Please specify: [details]",
                max_clarification_attempts=3,
                description="Test LLM clarifier"
            )
            
            assert node.name == "test_llm_clarifier"
            assert node.node_type == NodeType.CLARIFY
            assert node.expected_response_format == "Please specify: [details]"
            assert node.max_clarification_attempts == 3
            assert node.description == "Test LLM clarifier"

    def test_llm_clarifier_node_execution(self):
        """Test that LLM clarifier node executes correctly."""
        mock_llm_config = {"provider": "openrouter", "model": "switchpoint/router"}
        mock_response = "I need more details about your booking request."
        
        with patch('intent_kit.services.llm_factory.LLMFactory.generate_with_config') as mock_generate:
            mock_generate.return_value = mock_response
            
            node = create_llm_clarifier_node(
                name="test_llm_clarifier",
                llm_config=mock_llm_config,
                expected_response_format="Please specify: [details]"
            )
            
            result = node.execute("book something")
            
            assert isinstance(result, ExecutionResult)
            assert result.success is False
            assert result.node_type == NodeType.CLARIFY
            assert result.node_name == "test_llm_clarifier"
            assert result.output["requires_clarification"] is True
            assert mock_response in result.output["clarification_message"]

    def test_llm_clarifier_node_with_custom_prompt(self):
        """Test LLM clarifier node with custom prompt template."""
        mock_llm_config = {"provider": "openrouter", "model": "switchpoint/router"}
        mock_response = "Custom clarification message."
        
        custom_prompt = "Generate a custom clarification for: {user_input}"
        
        with patch('intent_kit.services.llm_factory.LLMFactory.generate_with_config') as mock_generate:
            mock_generate.return_value = mock_response
            
            node = create_llm_clarifier_node(
                name="test_llm_clarifier",
                llm_config=mock_llm_config,
                clarification_prompt_template=custom_prompt,
                expected_response_format="Please specify: [details]"
            )
            
            result = node.execute("book something")
            
            assert mock_response in result.output["clarification_message"]
            mock_generate.assert_called_once()

    def test_llm_clarifier_node_with_context(self):
        """Test LLM clarifier node with context."""
        mock_llm_config = {"provider": "openrouter", "model": "switchpoint/router"}
        mock_response = "Based on your preferences, I need more details."
        
        with patch('intent_kit.services.llm_factory.LLMFactory.generate_with_config') as mock_generate:
            mock_generate.return_value = mock_response
            
            node = create_llm_clarifier_node(
                name="test_llm_clarifier",
                llm_config=mock_llm_config,
                expected_response_format="Please specify: [details]"
            )
            
            context = IntentContext()
            context.set("user_preferences", "window seat")
            
            result = node.execute("book flight", context=context)
            
            assert result.success is False
            assert mock_response in result.output["clarification_message"]
            
            # Check that clarification context was stored
            clarification_context = context.get("clarification_context")
            assert clarification_context is not None
            assert clarification_context["original_input"] == "book flight"

    def test_llm_clarifier_node_handle_clarification_response(self):
        """Test LLM clarifier node handling clarification responses."""
        mock_llm_config = {"provider": "openrouter", "model": "switchpoint/router"}
        
        node = create_llm_clarifier_node(
            name="test_llm_clarifier",
            llm_config=mock_llm_config,
            max_clarification_attempts=2
        )
        
        context = IntentContext()
        context.set("clarification_context", {
            "original_input": "book",
            "attempts": 0,
            "max_attempts": 2
        })
        
        response = node.handle_clarification_response("book a flight to Paris", context)
        
        assert response["success"] is True
        assert response["clarified_input"] == "book a flight to Paris"
        assert response["original_input"] == "book"
        assert response["attempts"] == 1

    def test_llm_clarifier_node_max_attempts(self):
        """Test LLM clarifier node max attempts handling."""
        mock_llm_config = {"provider": "openrouter", "model": "switchpoint/router"}
        
        node = create_llm_clarifier_node(
            name="test_llm_clarifier",
            llm_config=mock_llm_config,
            max_clarification_attempts=2
        )
        
        context = IntentContext()
        context.set("clarification_context", {
            "original_input": "book",
            "attempts": 2,  # Already at max
            "max_attempts": 2
        })
        
        response = node.handle_clarification_response("another attempt", context)
        
        assert response["success"] is False
        assert response["error"] == "Maximum clarification attempts exceeded"
        assert response["attempts"] == 3

    def test_llm_clarifier_node_without_expected_format(self):
        """Test LLM clarifier node without expected response format."""
        mock_llm_config = {"provider": "openrouter", "model": "switchpoint/router"}
        mock_response = "I need more details about your request."
        
        with patch('intent_kit.services.llm_factory.LLMFactory.generate_with_config') as mock_generate:
            mock_generate.return_value = mock_response
            
            node = create_llm_clarifier_node(
                name="test_llm_clarifier",
                llm_config=mock_llm_config
                # No expected_response_format
            )
            
            result = node.execute("book something")
            
            assert mock_response in result.output["clarification_message"]
            # Should not have format information appended
            assert "Please provide your response in the following format" not in result.output["clarification_message"]

    def test_llm_clarifier_node_error_structure(self):
        """Test that LLM clarifier node error has proper structure."""
        mock_llm_config = {"provider": "openrouter", "model": "switchpoint/router"}
        mock_response = "I need more details."
        
        with patch('intent_kit.services.llm_factory.LLMFactory.generate_with_config') as mock_generate:
            mock_generate.return_value = mock_response
            
            node = create_llm_clarifier_node(
                name="test_llm_clarifier",
                llm_config=mock_llm_config
            )
            
            result = node.execute("test input")
            
            error = result.error
            assert error.error_type == "ClarificationNeeded"
            assert "test input" in error.message
            assert error.node_name == "test_llm_clarifier"
            assert isinstance(error.node_path, list)
            assert error.input_data is not None
            assert "original_input" in error.input_data
            assert error.params is not None