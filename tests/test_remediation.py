"""
Tests for the remediation strategies.
"""

import json
from unittest.mock import Mock, patch, MagicMock
from intent_kit.node.actions.remediation import (
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
)
from intent_kit.node.types import ExecutionError
from intent_kit.context import IntentContext
from intent_kit.utils.text_utils import extract_json_from_text


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
        fallback_handler = Mock()
        strategy = FallbackToAnotherNodeStrategy(fallback_handler, "fallback_name")
        assert strategy.name == "fallback_to_another_node"
        assert strategy.fallback_handler == fallback_handler
        assert strategy.fallback_name == "fallback_name"

    def test_fallback_strategy_success(self):
        """Test fallback strategy when fallback handler succeeds."""
        fallback_handler = Mock(return_value="fallback success")
        strategy = FallbackToAnotherNodeStrategy(fallback_handler, "fallback")
        validated_params = {"x": 5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=Mock(),
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "fallback success"
        assert result.node_name == "fallback"
        fallback_handler.assert_called_once_with(**validated_params)

    def test_fallback_strategy_with_context(self):
        """Test fallback strategy with context parameter."""
        fallback_handler = Mock(return_value="fallback success")
        strategy = FallbackToAnotherNodeStrategy(fallback_handler, "fallback")
        validated_params = {"x": 5}
        context = IntentContext()

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            context=context,
            handler_func=Mock(),
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        fallback_handler.assert_called_once_with(**validated_params, context=context)

    def test_fallback_strategy_no_validated_params(self):
        """Test fallback strategy when no validated_params provided."""
        fallback_handler = Mock(return_value="fallback success")
        strategy = FallbackToAnotherNodeStrategy(fallback_handler, "fallback")

        result = strategy.execute(
            node_name="test_node", user_input="test input", handler_func=Mock()
        )

        assert result is not None
        assert result.success is True
        fallback_handler.assert_called_once_with(user_input="test input")

    def test_fallback_strategy_failure(self):
        """Test fallback strategy when fallback handler fails."""
        fallback_handler = Mock(side_effect=Exception("fallback failed"))
        strategy = FallbackToAnotherNodeStrategy(fallback_handler, "fallback")

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=Mock(),
            validated_params={"x": 5},
        )

        assert result is None


class TestSelfReflectStrategy:
    """Test the SelfReflectStrategy."""

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_self_reflect_strategy_creation(self, mock_llm_factory):
        """Test creating a self-reflect strategy."""
        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        strategy = SelfReflectStrategy(llm_config, max_reflections=2)
        assert strategy.name == "self_reflect"
        assert strategy.llm_config == llm_config
        assert strategy.max_reflections == 2

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_self_reflect_strategy_success(self, mock_llm_factory):
        """Test self-reflect strategy when LLM provides good analysis."""
        # Mock LLM client
        mock_client = Mock()
        mock_client.generate.return_value = json.dumps(
            {
                "analysis": "The handler failed because of negative input",
                "suggestions": ["Use absolute value", "Use positive numbers"],
                "modified_params": {"x": 5},
                "confidence": 0.8,
            }
        )
        mock_llm_factory.create_client.return_value = mock_client

        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        strategy = SelfReflectStrategy(llm_config, max_reflections=1)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -3}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
            original_error=ExecutionError(
                error_type="ValueError",
                message="Cannot handle negative numbers",
                node_name="test_node",
                node_path=["test_node"],
            ),
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        assert result.params == {"x": 5}  # Modified params
        handler_func.assert_called_once_with(x=5)

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_self_reflect_strategy_invalid_json(self, mock_llm_factory):
        """Test self-reflect strategy when LLM returns invalid JSON."""
        # Mock LLM client
        mock_client = Mock()
        mock_client.generate.return_value = "invalid json"
        mock_llm_factory.create_client.return_value = mock_client

        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        strategy = SelfReflectStrategy(llm_config, max_reflections=1)
        handler_func = Mock(return_value="success")
        validated_params = {"x": 3}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        # Should use original params when JSON is invalid
        assert result.params == validated_params

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_self_reflect_strategy_llm_failure(self, mock_llm_factory):
        """Test self-reflect strategy when LLM fails."""
        # Mock LLM client that raises exception
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("LLM error")
        mock_llm_factory.create_client.return_value = mock_client

        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        strategy = SelfReflectStrategy(llm_config, max_reflections=1)
        handler_func = Mock()
        validated_params = {"x": 3}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None


class TestConsensusVoteStrategy:
    """Test the ConsensusVoteStrategy."""

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_consensus_vote_strategy_creation(self, mock_llm_factory):
        """Test creating a consensus vote strategy."""
        llm_configs = [
            {"provider": "openai", "model": "gpt-4", "api_key": "test-key"},
            {"provider": "google", "model": "gemini", "api_key": "test-key"},
        ]
        strategy = ConsensusVoteStrategy(llm_configs, vote_threshold=0.6)
        assert strategy.name == "consensus_vote"
        assert strategy.llm_configs == llm_configs
        assert strategy.vote_threshold == 0.6

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_consensus_vote_strategy_success(self, mock_llm_factory):
        """Test consensus vote strategy when models agree."""
        # Mock LLM clients
        mock_client1 = Mock()
        mock_client1.generate.return_value = json.dumps(
            {
                "approach": "Use positive numbers",
                "confidence": 0.8,
                "modified_params": {"x": 5},
                "reasoning": "Negative numbers cause errors",
            }
        )

        mock_client2 = Mock()
        mock_client2.generate.return_value = json.dumps(
            {
                "approach": "Use absolute value",
                "confidence": 0.9,
                "modified_params": {"x": 3},
                "reasoning": "Convert negative to positive",
            }
        )

        mock_llm_factory.create_client.side_effect = [mock_client1, mock_client2]

        llm_configs = [
            {"provider": "openai", "model": "gpt-4", "api_key": "test-key"},
            {"provider": "google", "model": "gemini", "api_key": "test-key"},
        ]
        strategy = ConsensusVoteStrategy(llm_configs, vote_threshold=0.5)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -3}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
            original_error=ExecutionError(
                error_type="ValueError",
                message="Cannot handle negative numbers",
                node_name="test_node",
                node_path=["test_node"],
            ),
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        # Should use the highest confidence vote (model 2 with x=3)
        assert result.params == {"x": 3}

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_consensus_vote_strategy_low_confidence(self, mock_llm_factory):
        """Test consensus vote strategy when confidence is too low."""
        # Mock LLM clients with low confidence
        mock_client1 = Mock()
        mock_client1.generate.return_value = json.dumps(
            {
                "approach": "Try something",
                "confidence": 0.3,
                "modified_params": {"x": 5},
                "reasoning": "Low confidence approach",
            }
        )

        mock_client2 = Mock()
        mock_client2.generate.return_value = json.dumps(
            {
                "approach": "Try another thing",
                "confidence": 0.4,
                "modified_params": {"x": 3},
                "reasoning": "Another low confidence approach",
            }
        )

        mock_llm_factory.create_client.side_effect = [mock_client1, mock_client2]

        llm_configs = [
            {"provider": "openai", "model": "gpt-4", "api_key": "test-key"},
            {"provider": "google", "model": "gemini", "api_key": "test-key"},
        ]
        strategy = ConsensusVoteStrategy(
            llm_configs, vote_threshold=0.6
        )  # Higher threshold
        handler_func = Mock()
        validated_params = {"x": -3}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None  # Should fail due to low confidence

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_consensus_vote_strategy_no_votes(self, mock_llm_factory):
        """Test consensus vote strategy when no models provide valid votes."""
        # Mock LLM client that fails
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("LLM error")
        mock_llm_factory.create_client.return_value = mock_client

        llm_configs = [{"provider": "openai", "model": "gpt-4", "api_key": "test-key"}]
        strategy = ConsensusVoteStrategy(llm_configs, vote_threshold=0.6)
        handler_func = Mock()
        validated_params = {"x": -3}

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
        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        strategy = RetryWithAlternatePromptStrategy(llm_config)
        assert strategy.name == "retry_with_alternate_prompt"
        assert strategy.llm_config == llm_config
        assert len(strategy.alternate_prompts) == 4

    def test_alternate_prompt_strategy_custom_prompts(self):
        """Test alternate prompt strategy with custom prompts."""
        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        custom_prompts = ["Try {user_input}", "Test {user_input}"]
        strategy = RetryWithAlternatePromptStrategy(llm_config, custom_prompts)
        assert strategy.alternate_prompts == custom_prompts

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_alternate_prompt_strategy_success_with_absolute_values(
        self, mock_llm_factory
    ):
        """Test alternate prompt strategy with absolute value modification."""
        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        strategy = RetryWithAlternatePromptStrategy(llm_config)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -3}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        # Should use absolute value of -3, which is 3
        assert result.params == {"x": 3}

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_alternate_prompt_strategy_success_with_positive_values(
        self, mock_llm_factory
    ):
        """Test alternate prompt strategy with positive value modification."""
        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        strategy = RetryWithAlternatePromptStrategy(llm_config)
        handler_func = Mock(side_effect=[Exception("fail"), "success"])
        validated_params = {"x": -3}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        assert result.output == "success"
        # Should use max(0, -3) = 0
        assert result.params == {"x": 0}

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_alternate_prompt_strategy_all_strategies_fail(self, mock_llm_factory):
        """Test alternate prompt strategy when all strategies fail."""
        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        strategy = RetryWithAlternatePromptStrategy(llm_config)
        handler_func = Mock(side_effect=Exception("always fail"))
        validated_params = {"x": -3}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is None

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_alternate_prompt_strategy_mixed_parameter_types(self, mock_llm_factory):
        """Test alternate prompt strategy with mixed parameter types."""
        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        strategy = RetryWithAlternatePromptStrategy(llm_config)
        handler_func = Mock(return_value="success")
        validated_params = {"x": -3, "y": "test", "z": 0.5}

        result = strategy.execute(
            node_name="test_node",
            user_input="test input",
            handler_func=handler_func,
            validated_params=validated_params,
        )

        assert result is not None
        assert result.success is True
        # Should modify numeric parameters only
        assert result.params is not None
        assert result.params["x"] == 3  # Absolute value
        assert result.params["y"] == "test"  # Unchanged
        assert result.params["z"] == 0.5  # Unchanged (already positive)


class TestRemediationRegistry:
    """Test the RemediationRegistry."""

    def test_registry_creation(self):
        """Test creating a remediation registry."""
        registry = RemediationRegistry()
        assert isinstance(registry._strategies, dict)
        assert len(registry._strategies) == 0

    def test_registry_register_get(self):
        """Test registering and getting strategies."""
        registry = RemediationRegistry()
        strategy = Mock(spec=RemediationStrategy)
        strategy.name = "test_strategy"

        registry.register("test_id", strategy)
        retrieved = registry.get("test_id")
        assert retrieved == strategy

    def test_registry_get_nonexistent(self):
        """Test getting a non-existent strategy."""
        registry = RemediationRegistry()
        result = registry.get("nonexistent")
        assert result is None

    def test_registry_list_strategies(self):
        """Test listing registered strategies."""
        registry = RemediationRegistry()
        strategy1 = Mock(spec=RemediationStrategy)
        strategy2 = Mock(spec=RemediationStrategy)

        registry.register("strategy1", strategy1)
        registry.register("strategy2", strategy2)

        strategies = registry.list_strategies()
        assert "strategy1" in strategies
        assert "strategy2" in strategies
        assert len(strategies) == 2


class TestRemediationFactoryFunctions:
    """Test the factory functions for creating remediation strategies."""

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

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_create_self_reflect_strategy(self, mock_llm_factory):
        """Test creating a self-reflect strategy via factory function."""
        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        strategy = create_self_reflect_strategy(llm_config, max_reflections=3)
        assert isinstance(strategy, SelfReflectStrategy)
        assert strategy.llm_config == llm_config
        assert strategy.max_reflections == 3

    @patch("intent_kit.services.llm_factory.LLMFactory")
    def test_create_consensus_vote_strategy(self, mock_llm_factory):
        """Test creating a consensus vote strategy via factory function."""
        llm_configs = [
            {"provider": "openai", "model": "gpt-4", "api_key": "test-key"},
            {"provider": "google", "model": "gemini", "api_key": "test-key"},
        ]
        strategy = create_consensus_vote_strategy(llm_configs, vote_threshold=0.7)
        assert isinstance(strategy, ConsensusVoteStrategy)
        assert strategy.llm_configs == llm_configs
        assert strategy.vote_threshold == 0.7

    def test_create_alternate_prompt_strategy(self):
        """Test creating an alternate prompt strategy via factory function."""
        llm_config = {"provider": "openai", "model": "gpt-4", "api_key": "test-key"}
        custom_prompts = ["Custom prompt 1", "Custom prompt 2"]
        strategy = create_alternate_prompt_strategy(llm_config, custom_prompts)
        assert isinstance(strategy, RetryWithAlternatePromptStrategy)
        assert strategy.llm_config == llm_config
        assert strategy.alternate_prompts == custom_prompts


class TestGlobalRegistry:
    """Test the global remediation registry."""

    def test_register_get_strategy(self):
        """Test registering and getting strategies from global registry."""
        strategy = Mock(spec=RemediationStrategy)
        strategy.name = "global_test_strategy"

        register_remediation_strategy("global_test", strategy)
        retrieved = get_remediation_strategy("global_test")
        assert retrieved == strategy

    def test_list_remediation_strategies(self):
        """Test listing all registered remediation strategies."""
        # Clear any existing strategies for this test
        strategies = list_remediation_strategies()
        initial_count = len(strategies)

        # Register a new strategy
        strategy = Mock(spec=RemediationStrategy)
        register_remediation_strategy("test_list_strategy", strategy)

        # Check that it's in the list
        updated_strategies = list_remediation_strategies()
        assert len(updated_strategies) == initial_count + 1
        assert "test_list_strategy" in updated_strategies


def test_reflection_response_valid_json():
    with patch(
        "intent_kit.services.llm_factory.LLMFactory.create_client"
    ) as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate.return_value = (
            '{"analysis": "Looks good", "confidence": 0.9}'
        )
        mock_create_client.return_value = mock_client
        reflection_response = '{"analysis": "Looks good", "confidence": 0.9}'
        data = extract_json_from_text(reflection_response)
        assert data == {"analysis": "Looks good", "confidence": 0.9}


def test_reflection_response_malformed():
    with patch(
        "intent_kit.services.llm_factory.LLMFactory.create_client"
    ) as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate.return_value = "analysis: Looks good, confidence: 0.9"
        mock_create_client.return_value = mock_client
        reflection_response = "analysis: Looks good, confidence: 0.9"
        data = extract_json_from_text(reflection_response)
        assert data == {"analysis": "Looks good", "confidence": 0.9}


def test_vote_response_empty():
    with patch(
        "intent_kit.services.llm_factory.LLMFactory.create_client"
    ) as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate.return_value = ""
        mock_create_client.return_value = mock_client
        vote_response = ""
        data = extract_json_from_text(vote_response)
        assert data is None or data == {}
