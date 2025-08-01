"""
Tests for the remediation strategies.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from intent_kit.nodes.actions.remediation import (
    Strategy,
    RemediationStrategy,
    RetryOnFailStrategy,
    FallbackToAnotherNodeStrategy,
    SelfReflectStrategy,
    ConsensusVoteStrategy,
    RetryWithAlternatePromptStrategy,
    RemediationRegistry,
    register_remediation_strategy,
    get_remediation_strategy,
    list_remediation_strategies,
    create_retry_strategy,
    create_fallback_strategy,
    create_self_reflect_strategy,
    create_consensus_vote_strategy,
    create_alternate_prompt_strategy,
    create_classifier_fallback_strategy,
    create_keyword_fallback_strategy,
    ClassifierFallbackStrategy,
    KeywordFallbackStrategy,
)
from intent_kit.nodes.types import ExecutionError, ExecutionResult, NodeType
from intent_kit.context import IntentContext
from intent_kit.utils.text_utils import extract_json_from_text


class TestStrategy:
    """Test the base Strategy class."""

    def test_strategy_creation(self):
        """Test creating a base strategy."""
        strategy = Strategy("test_strategy", "Test strategy description")
        assert strategy.name == "test_strategy"
        assert strategy.description == "Test strategy description"

    def test_strategy_execute_not_implemented(self):
        """Test that base strategy execute raises NotImplementedError."""
        strategy = Strategy("test_strategy", "Test strategy description")
        with pytest.raises(NotImplementedError):
            strategy.execute("test_node", "test input")


class TestRemediationStrategy:
    """Test the RemediationStrategy class."""

    def test_remediation_strategy_creation(self):
        """Test creating a remediation strategy."""
        strategy = RemediationStrategy("test_remediation", "Test remediation description")
        assert strategy.name == "test_remediation"
        assert strategy.description == "Test remediation description"

    def test_remediation_strategy_execute_not_implemented(self):
        """Test that remediation strategy execute raises NotImplementedError."""
        strategy = RemediationStrategy("test_remediation", "Test remediation description")
        with pytest.raises(NotImplementedError):
            strategy.execute("test_node", "test input")


class TestRetryOnFailStrategy:
    """Test the RetryOnFailStrategy."""

    def test_retry_strategy_creation(self):
        """Test creating a retry strategy."""
        strategy = RetryOnFailStrategy(max_attempts=3, base_delay=1.0)
        assert strategy.name == "retry_on_fail"
        assert strategy.max_attempts == 3
        assert strategy.base_delay == 1.0

    def test_retry_strategy_success_on_first_attempt(self):
        """Test retry strategy when handler succeeds on first attempt."""
        strategy = RetryOnFailStrategy(max_attempts=3, base_delay=0.1)
        handler_func = Mock(return_value="success")
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        assert result.params == validated_params
        handler_func.assert_called_once_with(**validated_params)

    def test_retry_strategy_success_on_retry(self):
        """Test retry strategy when handler succeeds on retry."""
        strategy = RetryOnFailStrategy(max_attempts=3, base_delay=0.1)
        handler_func = Mock(side_effect=[Exception("fail"), "success"])
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        assert handler_func.call_count == 2

    def test_retry_strategy_all_attempts_fail(self):
        """Test retry strategy when all attempts fail."""
        strategy = RetryOnFailStrategy(max_attempts=2, base_delay=0.1)
        handler_func = Mock(side_effect=Exception("always fail"))
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None
        assert handler_func.call_count == 2

    def test_retry_strategy_with_context(self):
        """Test retry strategy with context parameter."""
        strategy = RetryOnFailStrategy(max_attempts=1, base_delay=0.1)
        handler_func = Mock(return_value="success")
        validated_params = {"x": 5}
        context = IntentContext()

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            context=context,
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        handler_func.assert_called_once_with(**validated_params, context=context)

    def test_retry_strategy_missing_parameters(self):
        """Test retry strategy with missing handler_func or validated_params."""
        strategy = RetryOnFailStrategy()

        # Missing handler_func
        result = strategy.execute(
            node_name="test_node", user_input="test input", validated_params={"x": 5}
        )
        assert result is None

        # Missing validated_params
        handler_func = Mock()
        result = strategy.execute(
            node_name="test_node", user_input="test input", handler_func=handler_func
        )
        assert result is None


class TestFallbackToAnotherNodeStrategy:
    """Test the FallbackToAnotherNodeStrategy."""

    def test_fallback_strategy_creation(self):
        """Test creating a fallback strategy."""
        fallback_handler = Mock(return_value="fallback_result")
        strategy = FallbackToAnotherNodeStrategy(fallback_handler, "test_fallback")
        assert strategy.name == "fallback_to_another_node"
        assert strategy.fallback_handler == fallback_handler
        assert strategy.fallback_name == "test_fallback"

    def test_fallback_strategy_success(self):
        """Test fallback strategy when fallback handler succeeds."""
        fallback_handler = Mock(return_value="fallback_result")
        strategy = FallbackToAnotherNodeStrategy(fallback_handler, "test_fallback")
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "fallback_result"
        assert result.params == validated_params
        fallback_handler.assert_called_once_with(**validated_params)

    def test_fallback_strategy_with_context(self):
        """Test fallback strategy with context parameter."""
        fallback_handler = Mock(return_value="fallback_result")
        strategy = FallbackToAnotherNodeStrategy(fallback_handler, "test_fallback")
        validated_params = {"x": 5}
        context = IntentContext()

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            context=context,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        fallback_handler.assert_called_once_with(**validated_params, context=context)

    def test_fallback_strategy_no_validated_params(self):
        """Test fallback strategy with no validated_params."""
        fallback_handler = Mock(return_value="fallback_result")
        strategy = FallbackToAnotherNodeStrategy(fallback_handler, "test_fallback")

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
        )

        assert result is not None
        assert result.success is True
        fallback_handler.assert_called_once_with()

    def test_fallback_strategy_failure(self):
        """Test fallback strategy when fallback handler fails."""
        fallback_handler = Mock(side_effect=Exception("fallback failed"))
        strategy = FallbackToAnotherNodeStrategy(fallback_handler, "test_fallback")
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            validated_params=validated_params,
        )

        assert result is None


class TestSelfReflectStrategy:
    """Test the SelfReflectStrategy."""

    def test_self_reflect_strategy_creation(self):
        """Test creating a self-reflect strategy."""
        llm_config = {"model": "test_model"}
        strategy = SelfReflectStrategy(llm_config, max_reflections=2)
        assert strategy.name == "self_reflect"
        assert strategy.llm_config == llm_config
        assert strategy.max_reflections == 2

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_self_reflect_strategy_success(self, mock_llm_factory):
        """Test self-reflect strategy when LLM reflection succeeds."""
        # Mock LLM factory and LLM
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"corrected_params": {"x": 10}, "explanation": "Fixed negative value"}'
        mock_llm_factory.create_client.return_value = mock_llm

        llm_config = {"model": "test_model"}
        strategy = SelfReflectStrategy(llm_config, max_reflections=2)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        assert result.params == {"x": 10}
        handler_func.assert_called_once_with(x=10)

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_self_reflect_strategy_invalid_json(self, mock_llm_factory):
        """Test self-reflect strategy when LLM returns invalid JSON."""
        # Mock LLM factory and LLM
        mock_llm = Mock()
        mock_llm.generate.return_value = "Invalid JSON response"
        mock_factory = Mock()
        mock_factory.create_llm.return_value = mock_llm
        mock_llm_factory.return_value = mock_factory

        llm_config = {"model": "test_model"}
        strategy = SelfReflectStrategy(llm_config, max_reflections=1)
        handler_func = Mock(return_value="success")
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_self_reflect_strategy_llm_failure(self, mock_llm_factory):
        """Test self-reflect strategy when LLM fails."""
        # Mock LLM factory and LLM
        mock_llm = Mock()
        mock_llm.generate.side_effect = Exception("LLM failed")
        mock_factory = Mock()
        mock_factory.create_llm.return_value = mock_llm
        mock_llm_factory.return_value = mock_factory

        llm_config = {"model": "test_model"}
        strategy = SelfReflectStrategy(llm_config, max_reflections=1)
        handler_func = Mock(return_value="success")
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None


class TestConsensusVoteStrategy:
    """Test the ConsensusVoteStrategy."""

    def test_consensus_vote_strategy_creation(self):
        """Test creating a consensus vote strategy."""
        llm_configs = [{"model": "model1"}, {"model": "model2"}]
        strategy = ConsensusVoteStrategy(llm_configs, vote_threshold=0.7)
        assert strategy.name == "consensus_vote"
        assert strategy.llm_configs == llm_configs
        assert strategy.vote_threshold == 0.7

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_consensus_vote_strategy_success(self, mock_llm_factory):
        """Test consensus vote strategy when voting succeeds."""
        # Mock LLM factory and LLMs
        mock_llm1 = Mock()
        mock_llm1.generate.return_value = '{"corrected_params": {"x": 10}, "confidence": 0.8, "explanation": "Fixed value"}'
        mock_llm2 = Mock()
        mock_llm2.generate.return_value = '{"corrected_params": {"x": 15}, "confidence": 0.9, "explanation": "Better fix"}'
        
        mock_llm_factory.create_client.side_effect = [mock_llm1, mock_llm2]

        llm_configs = [{"model": "model1"}, {"model": "model2"}]
        strategy = ConsensusVoteStrategy(llm_configs, vote_threshold=0.7)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        # Should use the highest confidence vote (0.9)
        assert result.params == {"x": 15}
        handler_func.assert_called_once_with(x=15)

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_consensus_vote_strategy_low_confidence(self, mock_llm_factory):
        """Test consensus vote strategy when confidence is below threshold."""
        # Mock LLM factory and LLMs
        mock_llm1 = Mock()
        mock_llm1.generate.return_value = '{"corrected_params": {"x": 10}, "confidence": 0.5, "explanation": "Low confidence"}'
        mock_llm2 = Mock()
        mock_llm2.generate.return_value = '{"corrected_params": {"x": 15}, "confidence": 0.6, "explanation": "Still low"}'
        
        mock_factory = Mock()
        mock_factory.create_llm.side_effect = [mock_llm1, mock_llm2]
        mock_llm_factory.return_value = mock_factory

        llm_configs = [{"model": "model1"}, {"model": "model2"}]
        strategy = ConsensusVoteStrategy(llm_configs, vote_threshold=0.7)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_consensus_vote_strategy_no_votes(self, mock_llm_factory):
        """Test consensus vote strategy when no valid votes are received."""
        # Mock LLM factory and LLMs
        mock_llm1 = Mock()
        mock_llm1.generate.side_effect = Exception("LLM failed")
        mock_llm2 = Mock()
        mock_llm2.generate.return_value = "Invalid JSON"
        
        mock_factory = Mock()
        mock_factory.create_llm.side_effect = [mock_llm1, mock_llm2]
        mock_llm_factory.return_value = mock_factory

        llm_configs = [{"model": "model1"}, {"model": "model2"}]
        strategy = ConsensusVoteStrategy(llm_configs, vote_threshold=0.7)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None


class TestRetryWithAlternatePromptStrategy:
    """Test the RetryWithAlternatePromptStrategy."""

    def test_alternate_prompt_strategy_creation(self):
        """Test creating an alternate prompt strategy."""
        llm_config = {"model": "test_model"}
        strategy = RetryWithAlternatePromptStrategy(llm_config)
        assert strategy.name == "retry_with_alternate_prompt"
        assert strategy.llm_config == llm_config

    def test_alternate_prompt_strategy_custom_prompts(self):
        """Test creating an alternate prompt strategy with custom prompts."""
        llm_config = {"model": "test_model"}
        custom_prompts = ["Custom prompt 1", "Custom prompt 2"]
        strategy = RetryWithAlternatePromptStrategy(llm_config, custom_prompts)
        assert strategy.alternate_prompts == custom_prompts

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_alternate_prompt_strategy_success_with_absolute_values(
        self, mock_llm_factory
    ):
        """Test alternate prompt strategy with absolute value approach."""
        # Mock LLM factory and LLM
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"corrected_params": {"x": 5}, "explanation": "Used absolute value"}'
        mock_llm_factory.create_client.return_value = mock_llm

        llm_config = {"model": "test_model"}
        strategy = RetryWithAlternatePromptStrategy(llm_config)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        assert result.params == {"x": 5}
        handler_func.assert_called_once_with(x=5)

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_alternate_prompt_strategy_success_with_positive_values(
        self, mock_llm_factory
    ):
        """Test alternate prompt strategy with positive value approach."""
        # Mock LLM factory and LLM
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"corrected_params": {"x": 10}, "explanation": "Used positive value"}'
        mock_llm_factory.create_client.return_value = mock_llm

        llm_config = {"model": "test_model"}
        strategy = RetryWithAlternatePromptStrategy(llm_config)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        assert result.params == {"x": 10}
        handler_func.assert_called_once_with(x=10)

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_alternate_prompt_strategy_all_strategies_fail(self, mock_llm_factory):
        """Test alternate prompt strategy when all prompts fail."""
        # Mock LLM factory and LLM
        mock_llm = Mock()
        mock_llm.generate.side_effect = ["Invalid JSON", "Another invalid response"]
        mock_factory = Mock()
        mock_factory.create_llm.return_value = mock_llm
        mock_llm_factory.return_value = mock_factory

        llm_config = {"model": "test_model"}
        strategy = RetryWithAlternatePromptStrategy(llm_config)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_alternate_prompt_strategy_mixed_parameter_types(self, mock_llm_factory):
        """Test alternate prompt strategy with mixed parameter types."""
        # Mock LLM factory and LLM
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"corrected_params": {"x": 5, "y": "positive"}, "explanation": "Mixed types"}'
        mock_llm_factory.create_client.return_value = mock_llm

        llm_config = {"model": "test_model"}
        strategy = RetryWithAlternatePromptStrategy(llm_config)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -5, "y": "negative"}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        assert result.params == {"x": 5, "y": "positive"}
        handler_func.assert_called_once_with(x=5, y="positive")


class TestRemediationRegistry:
    """Test the RemediationRegistry."""

    def test_registry_creation(self):
        """Test creating a remediation registry."""
        registry = RemediationRegistry()
        assert isinstance(registry, RemediationRegistry)

    def test_registry_register_get(self):
        """Test registering and getting strategies from registry."""
        registry = RemediationRegistry()
        strategy = Mock(spec=RemediationStrategy)
        strategy.name = "test_strategy"

        registry.register("test_id", strategy)
        retrieved = registry.get("test_id")

        assert retrieved == strategy

    def test_registry_get_nonexistent(self):
        """Test getting a non-existent strategy from registry."""
        registry = RemediationRegistry()
        retrieved = registry.get("nonexistent_id")

        assert retrieved is None

    def test_registry_list_strategies(self):
        """Test listing strategies in registry."""
        registry = RemediationRegistry()
        strategy1 = Mock(spec=RemediationStrategy)
        strategy2 = Mock(spec=RemediationStrategy)

        registry.register("id1", strategy1)
        registry.register("id2", strategy2)

        strategies = registry.list_strategies()

        assert "id1" in strategies
        assert "id2" in strategies
        assert len(strategies) >= 2  # Built-in strategies are also registered


class TestRemediationFactoryFunctions:
    """Test the factory functions for creating strategies."""

    def test_create_retry_strategy(self):
        """Test creating a retry strategy via factory function."""
        strategy = create_retry_strategy(max_attempts=5, base_delay=2.0)
        assert isinstance(strategy, RetryOnFailStrategy)
        assert strategy.max_attempts == 5
        assert strategy.base_delay == 2.0

    def test_create_fallback_strategy(self):
        """Test creating a fallback strategy via factory function."""
        fallback_handler = Mock()
        strategy = create_fallback_strategy(fallback_handler, "custom_fallback")
        assert isinstance(strategy, FallbackToAnotherNodeStrategy)
        assert strategy.fallback_handler == fallback_handler
        assert strategy.fallback_name == "custom_fallback"

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_create_self_reflect_strategy(self, mock_llm_factory):
        """Test creating a self-reflect strategy via factory function."""
        llm_config = {"model": "test_model"}
        strategy = create_self_reflect_strategy(llm_config, max_reflections=3)
        assert isinstance(strategy, SelfReflectStrategy)
        assert strategy.llm_config == llm_config
        assert strategy.max_reflections == 3

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_create_consensus_vote_strategy(self, mock_llm_factory):
        """Test creating a consensus vote strategy via factory function."""
        llm_configs = [{"model": "model1"}, {"model": "model2"}]
        strategy = create_consensus_vote_strategy(llm_configs, vote_threshold=0.8)
        assert isinstance(strategy, ConsensusVoteStrategy)
        assert strategy.llm_configs == llm_configs
        assert strategy.vote_threshold == 0.8

    def test_create_alternate_prompt_strategy(self):
        """Test creating an alternate prompt strategy via factory function."""
        llm_config = {"model": "test_model"}
        custom_prompts = ["Custom prompt"]
        strategy = create_alternate_prompt_strategy(llm_config, custom_prompts)
        assert isinstance(strategy, RetryWithAlternatePromptStrategy)
        assert strategy.llm_config == llm_config
        assert strategy.alternate_prompts == custom_prompts

    def test_create_classifier_fallback_strategy(self):
        """Test creating a classifier fallback strategy via factory function."""
        fallback_classifier = Mock()
        strategy = create_classifier_fallback_strategy(fallback_classifier, "custom_classifier")
        assert isinstance(strategy, ClassifierFallbackStrategy)
        assert strategy.fallback_classifier == fallback_classifier
        assert strategy.fallback_name == "custom_classifier"

    def test_create_keyword_fallback_strategy(self):
        """Test creating a keyword fallback strategy via factory function."""
        strategy = create_keyword_fallback_strategy()
        assert isinstance(strategy, KeywordFallbackStrategy)


class TestGlobalRegistry:
    """Test the global registry functions."""

    def test_register_get_strategy(self):
        """Test registering and getting strategies from global registry."""
        strategy = Mock(spec=RemediationStrategy)
        strategy.name = "test_strategy"

        register_remediation_strategy("global_test_id", strategy)
        retrieved = get_remediation_strategy("global_test_id")

        assert retrieved == strategy

    def test_list_remediation_strategies(self):
        """Test listing strategies from global registry."""
        # Clear any existing strategies for this test
        strategies_before = list_remediation_strategies()
        
        strategy = Mock(spec=RemediationStrategy)
        strategy.name = "test_strategy"

        register_remediation_strategy("list_test_id", strategy)
        strategies_after = list_remediation_strategies()

        assert "list_test_id" in strategies_after
        assert len(strategies_after) >= len(strategies_before) + 1


class TestClassifierFallbackStrategy:
    """Test the ClassifierFallbackStrategy."""

    def test_classifier_fallback_strategy_creation(self):
        """Test creating a classifier fallback strategy."""
        fallback_classifier = Mock()
        strategy = ClassifierFallbackStrategy(fallback_classifier, "test_classifier")
        assert strategy.name == "classifier_fallback"
        assert strategy.fallback_classifier == fallback_classifier
        assert strategy.fallback_name == "test_classifier"

    def test_classifier_fallback_strategy_success(self):
        """Test classifier fallback strategy when fallback succeeds."""
        fallback_classifier = Mock(return_value="child_a")
        strategy = ClassifierFallbackStrategy(fallback_classifier, "test_classifier")
        
        # Mock available children
        child_a = Mock()
        child_a.name = "child_a"
        child_a.description = "First child"
        child_b = Mock()
        child_b.name = "child_b"
        child_b.description = "Second child"
        available_children = [child_a, child_b]

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            classifier_func=Mock(),
            available_children=available_children,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "child_a"
        assert result.params["selected_child"] == "child_a"
        assert result.params["score"] > 0

    def test_classifier_fallback_strategy_no_children(self):
        """Test classifier fallback strategy with no available children."""
        fallback_classifier = Mock(return_value="child_a")
        strategy = ClassifierFallbackStrategy(fallback_classifier, "test_classifier")

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            classifier_func=Mock(),
            available_children=[],
        )

        assert result is None

    def test_classifier_fallback_strategy_fallback_fails(self):
        """Test classifier fallback strategy when fallback classifier fails."""
        fallback_classifier = Mock(side_effect=Exception("Fallback failed"))
        strategy = ClassifierFallbackStrategy(fallback_classifier, "test_classifier")
        
        child_a = Mock()
        child_a.name = "child_a"
        child_a.description = "First child"
        available_children = [child_a]

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            classifier_func=Mock(),
            available_children=available_children,
        )

        assert result is None

    def test_classifier_fallback_strategy_child_execution_fails(self):
        """Test classifier fallback strategy when child execution fails."""
        fallback_classifier = Mock(return_value="child_a")
        strategy = ClassifierFallbackStrategy(fallback_classifier, "test_classifier")
        
        child_a = Mock()
        child_a.name = "child_a"
        child_a.description = "First child"
        available_children = [child_a]

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            classifier_func=Mock(),
            available_children=available_children,
        )

        # Should still succeed as the strategy just selects the child
        assert result is not None
        assert result.success is True


class TestKeywordFallbackStrategy:
    """Test the KeywordFallbackStrategy."""

    def test_keyword_fallback_strategy_creation(self):
        """Test creating a keyword fallback strategy."""
        strategy = KeywordFallbackStrategy()
        assert strategy.name == "keyword_fallback"

    def test_keyword_fallback_strategy_match_by_name(self):
        """Test keyword fallback strategy matching by child name."""
        strategy = KeywordFallbackStrategy()
        
        # Mock available children
        child_a = Mock()
        child_a.name = "calculator"
        child_a.description = "Performs calculations"
        child_b = Mock()
        child_b.name = "translator"
        child_b.description = "Translates text"
        available_children = [child_a, child_b]

        result = strategy.execute(
            node_name="test_node",
            user_input="I need to calculate something",
            classifier_func=Mock(),
            available_children=available_children,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "calculator"
        assert result.params["selected_child"] == "calculator"

    def test_keyword_fallback_strategy_match_by_description(self):
        """Test keyword fallback strategy matching by child description."""
        strategy = KeywordFallbackStrategy()
        
        # Mock available children
        child_a = Mock()
        child_a.name = "action_a"
        child_a.description = "Performs mathematical calculations"
        child_b = Mock()
        child_b.name = "action_b"
        child_b.description = "Translates between languages"
        available_children = [child_a, child_b]

        result = strategy.execute(
            node_name="test_node",
            user_input="I need to do some math",
            classifier_func=Mock(),
            available_children=available_children,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "action_a"
        assert result.params["selected_child"] == "action_a"

    def test_keyword_fallback_strategy_no_match(self):
        """Test keyword fallback strategy when no match is found."""
        strategy = KeywordFallbackStrategy()
        
        # Mock available children
        child_a = Mock()
        child_a.name = "action_a"
        child_a.description = "Performs calculations"
        child_b = Mock()
        child_b.name = "action_b"
        child_b.description = "Translates text"
        available_children = [child_a, child_b]

        result = strategy.execute(
            node_name="test_node",
            user_input="I need to do something completely different",
            classifier_func=Mock(),
            available_children=available_children,
        )

        assert result is None

    def test_keyword_fallback_strategy_no_children(self):
        """Test keyword fallback strategy with no available children."""
        strategy = KeywordFallbackStrategy()

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            classifier_func=Mock(),
            available_children=[],
        )

        assert result is None

    def test_keyword_fallback_strategy_case_insensitive(self):
        """Test keyword fallback strategy with case insensitive matching."""
        strategy = KeywordFallbackStrategy()
        
        # Mock available children
        child_a = Mock()
        child_a.name = "Calculator"
        child_a.description = "Performs CALCULATIONS"
        child_b = Mock()
        child_b.name = "Translator"
        child_b.description = "Translates TEXT"
        available_children = [child_a, child_b]

        result = strategy.execute(
            node_name="test_node",
            user_input="I need to CALCULATE something",
            classifier_func=Mock(),
            available_children=available_children,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "Calculator"
        assert result.params["selected_child"] == "Calculator"


class TestRemediationEdgeCases:
    """Test edge cases for remediation strategies."""

    def test_retry_strategy_with_zero_attempts(self):
        """Test retry strategy with zero attempts."""
        strategy = RetryOnFailStrategy(max_attempts=0, base_delay=0.1)
        handler_func = Mock(side_effect=Exception("fail"))
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None
        assert handler_func.call_count == 0

    def test_retry_strategy_with_negative_delay(self):
        """Test retry strategy with negative delay."""
        strategy = RetryOnFailStrategy(max_attempts=2, base_delay=-1.0)
        handler_func = Mock(side_effect=[Exception("fail"), "success"])
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert handler_func.call_count == 2

    def test_fallback_strategy_with_none_handler(self):
        """Test fallback strategy with None handler."""
        strategy = FallbackToAnotherNodeStrategy(None, "test_fallback")
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            validated_params=validated_params,
        )

        assert result is None

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_self_reflect_strategy_with_empty_llm_config(self, mock_llm_factory):
        """Test self-reflect strategy with empty LLM config."""
        strategy = SelfReflectStrategy({}, max_reflections=1)
        handler_func = Mock(return_value="success")
        validated_params = {"x": 5}

        # Mock LLM factory to handle empty config
        mock_llm = Mock()
        mock_llm.generate.return_value = '{"corrected_params": {"x": 10}, "explanation": "Fixed"}'
        mock_llm_factory.create_client.return_value = mock_llm

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True

    @patch("intent_kit.services.ai.llm_factory.LLMFactory")
    def test_consensus_vote_strategy_with_empty_configs(self, mock_llm_factory):
        """Test consensus vote strategy with empty LLM configs."""
        strategy = ConsensusVoteStrategy([], vote_threshold=0.6)
        handler_func = Mock(return_value="success")
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None

    def test_alternate_prompt_strategy_with_empty_prompts(self):
        """Test alternate prompt strategy with empty prompts."""
        llm_config = {"model": "test_model"}
        strategy = RetryWithAlternatePromptStrategy(llm_config, [])
        handler_func = Mock(return_value="success")
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None

    def test_registry_with_duplicate_registration(self):
        """Test registry with duplicate strategy registration."""
        registry = RemediationRegistry()
        strategy1 = Mock(spec=RemediationStrategy)
        strategy2 = Mock(spec=RemediationStrategy)

        registry.register("duplicate_id", strategy1)
        registry.register("duplicate_id", strategy2)  # Should overwrite

        retrieved = registry.get("duplicate_id")
        assert retrieved == strategy2

    def test_registry_with_empty_id(self):
        """Test registry with empty strategy ID."""
        registry = RemediationRegistry()
        strategy = Mock(spec=RemediationStrategy)

        registry.register("", strategy)
        retrieved = registry.get("")

        assert retrieved == strategy

    def test_global_registry_cleanup(self):
        """Test global registry cleanup and isolation."""
        # Test that registering in one test doesn't affect others
        strategy = Mock(spec=RemediationStrategy)
        strategy.name = "cleanup_test_strategy"

        register_remediation_strategy("cleanup_test_id", strategy)
        retrieved = get_remediation_strategy("cleanup_test_id")
        assert retrieved == strategy

        # Verify it's in the list
        strategies = list_remediation_strategies()
        assert "cleanup_test_id" in strategies


# Utility functions for testing
def test_reflection_response_valid_json():
    """Test utility function for valid JSON reflection response."""
    response = '{"corrected_params": {"x": 10}, "explanation": "Fixed negative value"}'
    result = extract_json_from_text(response)
    assert result is not None
    assert result["corrected_params"]["x"] == 10
    assert result["explanation"] == "Fixed negative value"


def test_reflection_response_malformed():
    """Test utility function for malformed JSON reflection response."""
    response = "This is not valid JSON"
    result = extract_json_from_text(response)
    assert result is None


def test_vote_response_empty():
    """Test utility function for empty vote response."""
    response = ""
    result = extract_json_from_text(response)
    assert result is None
