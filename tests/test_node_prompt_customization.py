"""
Tests for node-level prompt customization feature.
"""

from unittest.mock import Mock, patch
from intent_kit.builder import handler, llm_classifier
from intent_kit.node.base import TreeNode


class TestNodePromptCustomization:
    """Test node-level prompt customization functionality."""

    def test_base_treenode_custom_prompts(self):
        """Test that TreeNode base class supports custom prompts."""
        # Create a concrete test class to avoid abstract class instantiation
        class TestTreeNode(TreeNode):
            def execute(self, user_input: str, context=None):
                return None
        
        # Test with no custom prompts
        node = TestTreeNode(
            name="test",
            description="Test node",
            custom_prompts=None
        )
        assert node.custom_prompts == {}
        assert not node.has_custom_prompts()
        assert node.get_custom_prompt("test", "default") == "default"

        # Test with custom prompts
        custom_prompts = {"extraction": "custom extraction prompt"}
        node = TestTreeNode(
            name="test",
            description="Test node",
            custom_prompts=custom_prompts
        )
        assert node.custom_prompts == custom_prompts
        assert node.has_custom_prompts()
        assert node.get_custom_prompt("extraction", "default") == "custom extraction prompt"
        assert node.get_custom_prompt("nonexistent", "default") == "default"

    def test_handler_with_custom_prompts(self):
        """Test handler creation with custom prompts."""
        # Mock LLM config
        llm_config = {"provider": "openai", "model": "gpt-4"}
        
        # Test handler with custom extraction prompt
        handler_node = handler(
            name="test_handler",
            description="Test handler",
            handler_func=lambda x: f"Hello {x}",
            param_schema={"name": str},
            llm_config=llm_config,
            custom_prompts={
                "extraction": "Custom extraction prompt with {user_input}"
            }
        )
        
        assert handler_node.has_custom_prompts()
        assert "extraction" in handler_node.custom_prompts
        assert handler_node.get_custom_prompt("extraction", "default") == "Custom extraction prompt with {user_input}"

    def test_handler_without_custom_prompts(self):
        """Test handler creation without custom prompts (default behavior)."""
        # Mock LLM config
        llm_config = {"provider": "openai", "model": "gpt-4"}
        
        # Test handler without custom prompts
        handler_node = handler(
            name="test_handler",
            description="Test handler",
            handler_func=lambda x: f"Hello {x}",
            param_schema={"name": str},
            llm_config=llm_config
        )
        
        assert not handler_node.has_custom_prompts()
        assert handler_node.custom_prompts == {}

    def test_llm_classifier_with_custom_prompts(self):
        """Test LLM classifier creation with custom prompts."""
        # Mock LLM config
        llm_config = {"provider": "openai", "model": "gpt-4"}
        
        # Create a mock child node
        child_node = Mock(spec=TreeNode)
        child_node.name = "test_child"
        child_node.description = "Test child description"
        
        # Test classifier with custom classification prompt
        classifier_node = llm_classifier(
            name="test_classifier",
            children=[child_node],
            llm_config=llm_config,
            custom_prompts={
                "classification": "Custom classification prompt with {user_input}"
            }
        )
        
        assert classifier_node.has_custom_prompts()
        assert "classification" in classifier_node.custom_prompts
        assert classifier_node.get_custom_prompt("classification", "default") == "Custom classification prompt with {user_input}"

    def test_llm_classifier_without_custom_prompts(self):
        """Test LLM classifier creation without custom prompts (default behavior)."""
        # Mock LLM config
        llm_config = {"provider": "openai", "model": "gpt-4"}
        
        # Create a mock child node
        child_node = Mock(spec=TreeNode)
        child_node.name = "test_child"
        child_node.description = "Test child description"
        
        # Test classifier without custom prompts
        classifier_node = llm_classifier(
            name="test_classifier",
            children=[child_node],
            llm_config=llm_config
        )
        
        assert not classifier_node.has_custom_prompts()
        assert classifier_node.custom_prompts == {}

    def test_custom_prompts_priority(self):
        """Test that custom prompts take priority over builder-level prompts."""
        # Mock LLM config
        llm_config = {"provider": "openai", "model": "gpt-4"}
        
        # Test handler with both builder-level and custom prompts
        handler_node = handler(
            name="test_handler",
            description="Test handler",
            handler_func=lambda x: f"Hello {x}",
            param_schema={"name": str},
            llm_config=llm_config,
            extraction_prompt="Builder-level prompt",  # Should be ignored
            custom_prompts={
                "extraction": "Custom extraction prompt"  # Should be used
            }
        )
        
        # The custom prompt should take priority
        assert handler_node.get_custom_prompt("extraction", "default") == "Custom extraction prompt"

    def test_custom_prompts_warning_logging(self):
        """Test that warnings are logged when custom prompts are used."""
        # Mock LLM config
        llm_config = {"provider": "openai", "model": "gpt-4"}
        
        with patch('intent_kit.utils.logger.Logger.warning') as mock_warning:
            # Create handler with custom prompts
            handler(
                name="test_handler",
                description="Test handler",
                handler_func=lambda x: f"Hello {x}",
                param_schema={"name": str},
                llm_config=llm_config,
                custom_prompts={
                    "extraction": "Custom extraction prompt"
                }
            )
            
            # Verify warning was logged
            mock_warning.assert_called()
            warning_message = mock_warning.call_args[0][0]
            assert "custom prompts" in warning_message.lower()
            assert "advanced feature" in warning_message.lower()

    def test_multiple_custom_prompts(self):
        """Test that multiple custom prompts can be set."""
        # Mock LLM config
        llm_config = {"provider": "openai", "model": "gpt-4"}
        
        custom_prompts = {
            "extraction": "Custom extraction prompt",
            "classification": "Custom classification prompt",
            "other": "Other custom prompt"
        }
        
        handler_node = handler(
            name="test_handler",
            description="Test handler",
            handler_func=lambda x: f"Hello {x}",
            param_schema={"name": str},
            llm_config=llm_config,
            custom_prompts=custom_prompts
        )
        
        assert handler_node.custom_prompts == custom_prompts
        assert handler_node.get_custom_prompt("extraction", "default") == "Custom extraction prompt"
        assert handler_node.get_custom_prompt("classification", "default") == "Custom classification prompt"
        assert handler_node.get_custom_prompt("other", "default") == "Other custom prompt"
        assert handler_node.get_custom_prompt("nonexistent", "default") == "default"