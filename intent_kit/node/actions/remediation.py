"""
Remediation strategies for intent-kit.

This module provides a pluggable remediation system for handling node execution failures.
Strategies can be registered by string ID or as custom callable functions.
"""

import time
import json
from typing import Any, Callable, Dict, List, Optional
from ..types import ExecutionResult, ExecutionError
from ..enums import NodeType
from intent_kit.context import IntentContext
from intent_kit.utils.logger import Logger
from intent_kit.utils.text_utils import extract_json_from_text


class RemediationStrategy:
    """Base class for remediation strategies."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.logger = Logger(name)

    def execute(
        self,
        node_name: str,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        **kwargs,
    ) -> Optional[ExecutionResult]:
        """
        Execute the remediation strategy.

        Args:
            node_name: Name of the node that failed
            user_input: Original user input
            context: Optional context object
            original_error: The original error that triggered remediation
            **kwargs: Additional strategy-specific parameters

        Returns:
            ExecutionResult if remediation succeeded, None if it failed
        """
        raise NotImplementedError("Subclasses must implement execute()")


class RetryOnFailStrategy(RemediationStrategy):
    """Simple retry strategy with exponential backoff."""

    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        super().__init__(
            "retry_on_fail",
            f"Retry up to {max_attempts} times with exponential backoff",
        )
        self.max_attempts = max_attempts
        self.base_delay = base_delay

    def execute(
        self,
        node_name: str,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        handler_func: Optional[Callable] = None,
        validated_params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[ExecutionResult]:
        """Retry the handler function with the same parameters."""
        if not handler_func or validated_params is None:
            self.logger.warning(
                f"RetryOnFailStrategy: Missing action_func or validated_params for {node_name}"
            )
            return None

        for attempt in range(1, self.max_attempts + 1):
            try:
                self.logger.info(
                    f"RetryOnFailStrategy: Attempt {attempt}/{self.max_attempts} for {node_name}"
                )

                # Add context if available
                if context is not None:
                    output = handler_func(**validated_params, context=context)
                else:
                    output = handler_func(**validated_params)

                self.logger.info(
                    f"RetryOnFailStrategy: Success on attempt {attempt} for {node_name}"
                )

                return ExecutionResult(
                    success=True,
                    node_name=node_name,
                    node_path=[node_name],
                    node_type=NodeType.ACTION,
                    input=user_input,
                    output=output,
                    error=None,
                    params=validated_params,
                    children_results=[],
                )

            except Exception as e:
                self.logger.warning(
                    f"RetryOnFailStrategy: Attempt {attempt} failed for {node_name}: {type(e).__name__}: {str(e)}"
                )

                if attempt < self.max_attempts:
                    delay = self.base_delay * (
                        2 ** (attempt - 1)
                    )  # Exponential backoff
                    self.logger.info(
                        f"RetryOnFailStrategy: Waiting {delay}s before retry"
                    )
                    time.sleep(delay)

        self.logger.error(
            f"RetryOnFailStrategy: All {self.max_attempts} attempts failed for {node_name}"
        )
        return None


class FallbackToAnotherNodeStrategy(RemediationStrategy):
    """Fallback to a specified alternative handler."""

    def __init__(self, fallback_handler: Callable, fallback_name: str = "fallback"):
        super().__init__("fallback_to_another_node", f"Fallback to {fallback_name}")
        self.fallback_handler = fallback_handler
        self.fallback_name = fallback_name

    def execute(
        self,
        node_name: str,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        validated_params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[ExecutionResult]:
        """Execute the fallback handler."""
        try:
            self.logger.info(
                f"FallbackToAnotherNodeStrategy: Executing {self.fallback_name} for {node_name}"
            )

            # Use the same parameters if possible, otherwise use minimal params
            if validated_params is not None:
                if context is not None:
                    output = self.fallback_handler(**validated_params, context=context)
                else:
                    output = self.fallback_handler(**validated_params)
            else:
                # Minimal fallback with just the input
                if context is not None:
                    output = self.fallback_handler(
                        user_input=user_input, context=context
                    )
                else:
                    output = self.fallback_handler(user_input=user_input)

            return ExecutionResult(
                success=True,
                node_name=self.fallback_name,
                node_path=[self.fallback_name],
                node_type=NodeType.ACTION,  # Default to action type
                input=user_input,
                output=output,
                error=None,
                params=validated_params or {},
                children_results=[],
            )

        except Exception as e:
            self.logger.error(
                f"FallbackToAnotherNodeStrategy: Fallback {self.fallback_name} failed for {node_name}: {type(e).__name__}: {str(e)}"
            )
            return None


class SelfReflectStrategy(RemediationStrategy):
    """LLM critiques its own output and retries with improved approach."""

    def __init__(self, llm_config: Dict[str, Any], max_reflections: int = 2):
        super().__init__(
            "self_reflect", f"LLM self-reflection with up to {max_reflections} attempts"
        )
        self.llm_config = llm_config
        self.max_reflections = max_reflections

    def execute(
        self,
        node_name: str,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        handler_func: Optional[Callable] = None,
        validated_params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[ExecutionResult]:
        """Use LLM to critique and improve the approach."""
        if not handler_func or validated_params is None:
            self.logger.warning(
                f"SelfReflectStrategy: Missing handler_func or validated_params for {node_name}"
            )
            return None

        from intent_kit.services.llm_factory import LLMFactory

        llm_client = LLMFactory.create_client(self.llm_config)

        for reflection in range(self.max_reflections):
            try:
                self.logger.info(
                    f"SelfReflectStrategy: Reflection {reflection + 1}/{self.max_reflections} for {node_name}"
                )

                # Create reflection prompt
                reflection_prompt = f"""
The handler '{node_name}' failed with error: {original_error.message if original_error else 'Unknown error'}

User input: {user_input}
Parameters: {validated_params}

Please analyze the failure and suggest improvements:
1. What went wrong?
2. How can we fix it?
3. What should we try differently?

Provide your analysis in JSON format:
{{
    "analysis": "What went wrong",
    "suggestions": ["suggestion1", "suggestion2"],
    "modified_params": {{"param": "new_value"}},
    "confidence": 0.8
}}
"""

                # Get LLM reflection
                reflection_response = llm_client.generate(reflection_prompt)

                try:
                    reflection_data = extract_json_from_text(reflection_response) or {}
                    self.logger.info(
                        f"SelfReflectStrategy: LLM reflection for {node_name}: {reflection_data.get('analysis', 'No analysis')}"
                    )

                    # Try with modified parameters if suggested
                    modified_params = reflection_data.get(
                        "modified_params", validated_params
                    )

                    if context is not None:
                        output = handler_func(**modified_params, context=context)
                    else:
                        output = handler_func(**modified_params)

                    self.logger.info(
                        f"SelfReflectStrategy: Success after reflection {reflection + 1} for {node_name}"
                    )

                    return ExecutionResult(
                        success=True,
                        node_name=node_name,
                        node_path=[node_name],
                        node_type=NodeType.ACTION,
                        input=user_input,
                        output=output,
                        error=None,
                        params=modified_params,
                        children_results=[],
                    )

                except json.JSONDecodeError:
                    self.logger.warning(
                        f"SelfReflectStrategy: Invalid JSON response from LLM for {node_name}"
                    )
                    # Try with original parameters as fallback
                    if context is not None:
                        output = handler_func(**validated_params, context=context)
                    else:
                        output = handler_func(**validated_params)

                    return ExecutionResult(
                        success=True,
                        node_name=node_name,
                        node_path=[node_name],
                        node_type=NodeType.ACTION,
                        input=user_input,
                        output=output,
                        error=None,
                        params=validated_params,
                        children_results=[],
                    )

            except Exception as e:
                self.logger.warning(
                    f"SelfReflectStrategy: Reflection {reflection + 1} failed for {node_name}: {type(e).__name__}: {str(e)}"
                )

        self.logger.error(
            f"SelfReflectStrategy: All {self.max_reflections} reflections failed for {node_name}"
        )
        return None


class ConsensusVoteStrategy(RemediationStrategy):
    """Ensemble voting among multiple LLM approaches."""

    def __init__(self, llm_configs: List[Dict[str, Any]], vote_threshold: float = 0.6):
        super().__init__(
            "consensus_vote",
            f"Ensemble voting with {len(llm_configs)} models, threshold {vote_threshold}",
        )
        self.llm_configs = llm_configs
        self.vote_threshold = vote_threshold

    def execute(
        self,
        node_name: str,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        handler_func: Optional[Callable] = None,
        validated_params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[ExecutionResult]:
        """Use multiple LLMs to vote on the best approach."""
        if not handler_func or validated_params is None:
            self.logger.warning(
                f"ConsensusVoteStrategy: Missing handler_func or validated_params for {node_name}"
            )
            return None

        from intent_kit.services.llm_factory import LLMFactory

        # Create voting prompt
        voting_prompt = f"""
The handler '{node_name}' failed with error: {original_error.message if original_error else 'Unknown error'}

User input: {user_input}
Parameters: {validated_params}

Please analyze this failure and suggest parameter modifications to fix it.
Focus on modifying the input parameters, not the handler logic.

For example, if the error is about negative numbers, suggest using absolute values or positive numbers.

Provide your response in JSON format:
{{
    "approach": "description of the approach",
    "confidence": 0.8,
    "modified_params": {{"param": "new_value"}},
    "reasoning": "why this approach should work"
}}

Common parameter modifications:
- For negative numbers: use absolute value or max(0, value)
- For missing values: use reasonable defaults
- For type mismatches: convert to correct type
"""

        votes = []
        successful_votes = 0

        for i, llm_config in enumerate(self.llm_configs):
            try:
                self.logger.info(
                    f"ConsensusVoteStrategy: Getting vote {i + 1}/{len(self.llm_configs)} for {node_name}"
                )

                llm_client = LLMFactory.create_client(llm_config)
                vote_response = llm_client.generate(voting_prompt)

                try:
                    vote_data = extract_json_from_text(vote_response) or {}

                    # Ensure modified_params is properly structured
                    modified_params = vote_data.get("modified_params", {})
                    if not isinstance(modified_params, dict):
                        modified_params = {}

                    # Merge with original validated_params to ensure all required params are present
                    final_params = validated_params.copy()
                    final_params.update(modified_params)

                    # Convert string values to appropriate types based on original validated_params
                    for key, original_value in validated_params.items():
                        if key in final_params:
                            new_value = final_params[key]
                            if isinstance(original_value, int) and isinstance(
                                new_value, str
                            ):
                                try:
                                    # Try to convert string to int
                                    final_params[key] = int(new_value)
                                except (ValueError, TypeError):
                                    # If conversion fails, try to evaluate simple expressions
                                    if new_value == "abs(x)":
                                        final_params[key] = abs(original_value)
                                    elif new_value == "max(0, x)":
                                        final_params[key] = max(0, original_value)
                                    else:
                                        # Keep original value if conversion fails
                                        final_params[key] = original_value
                            elif isinstance(original_value, float) and isinstance(
                                new_value, str
                            ):
                                try:
                                    final_params[key] = float(new_value)
                                except (ValueError, TypeError):
                                    final_params[key] = original_value

                    # Apply automatic parameter modifications if LLM didn't suggest any
                    if not modified_params:
                        for key, original_value in validated_params.items():
                            if (
                                isinstance(original_value, (int, float))
                                and original_value < 0
                            ):
                                # For negative numbers, use absolute value
                                final_params[key] = abs(original_value)

                    votes.append(
                        {
                            "model": f"model_{i}",
                            "approach": vote_data.get("approach", "unknown"),
                            "confidence": vote_data.get("confidence", 0.5),
                            "modified_params": final_params,
                            "reasoning": vote_data.get(
                                "reasoning", "No reasoning provided"
                            ),
                        }
                    )
                    successful_votes += 1

                except json.JSONDecodeError:
                    self.logger.warning(
                        f"ConsensusVoteStrategy: Invalid JSON from model {i} for {node_name}"
                    )

            except Exception as e:
                self.logger.warning(
                    f"ConsensusVoteStrategy: Model {i} failed for {node_name}: {type(e).__name__}: {str(e)}"
                )

        if not votes:
            self.logger.error(
                f"ConsensusVoteStrategy: No successful votes for {node_name}"
            )
            return None

        # Calculate consensus
        total_confidence = sum(vote["confidence"] for vote in votes)
        avg_confidence = total_confidence / len(votes)

        self.logger.info(
            f"ConsensusVoteStrategy: {successful_votes}/{len(self.llm_configs)} models voted for {node_name}, avg confidence: {avg_confidence:.2f}"
        )

        if avg_confidence >= self.vote_threshold:
            # Use the highest confidence vote
            best_vote = max(votes, key=lambda v: v["confidence"])

            try:
                self.logger.info(
                    f"ConsensusVoteStrategy: Attempting execution with params: {best_vote['modified_params']}"
                )

                if context is not None:
                    output = handler_func(
                        **best_vote["modified_params"], context=context
                    )
                else:
                    output = handler_func(**best_vote["modified_params"])

                self.logger.info(
                    f"ConsensusVoteStrategy: Success with consensus approach for {node_name}"
                )

                return ExecutionResult(
                    success=True,
                    node_name=node_name,
                    node_path=[node_name],
                    node_type=NodeType.ACTION,
                    input=user_input,
                    output=output,
                    error=None,
                    params=best_vote["modified_params"],
                    children_results=[],
                )

            except Exception as e:
                self.logger.error(
                    f"ConsensusVoteStrategy: Execution failed despite consensus for {node_name}: {type(e).__name__}: {str(e)}"
                )
                self.logger.error(
                    f"ConsensusVoteStrategy: Params that caused failure: {best_vote['modified_params']}"
                )

        self.logger.error(
            f"ConsensusVoteStrategy: Insufficient confidence ({avg_confidence:.2f} < {self.vote_threshold}) for {node_name}"
        )
        return None


class RetryWithAlternatePromptStrategy(RemediationStrategy):
    """Retry with modified prompt template."""

    def __init__(
        self, llm_config: Dict[str, Any], alternate_prompts: Optional[List[str]] = None
    ):
        super().__init__(
            "retry_with_alternate_prompt",
            f"Retry with {len(alternate_prompts) if alternate_prompts else 'default'} alternate prompts",
        )
        self.llm_config = llm_config
        if alternate_prompts is not None and isinstance(alternate_prompts, list):
            self.alternate_prompts = alternate_prompts
        else:
            self.alternate_prompts = [
                "Try with absolute value: {user_input}",
                "Try with positive number: {user_input}",
                "Try with default value: {user_input}",
                "Try with zero: {user_input}",
            ]

    def execute(
        self,
        node_name: str,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        handler_func: Optional[Callable] = None,
        validated_params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[ExecutionResult]:
        """Try different parameter modifications."""
        if not handler_func or validated_params is None:
            self.logger.warning(
                f"RetryWithAlternatePromptStrategy: Missing handler_func or validated_params for {node_name}"
            )
            return None

        # Try different parameter modification strategies
        modification_strategies = [
            # Strategy 1: Try with absolute values for numeric parameters
            lambda params: {
                k: abs(v) if isinstance(v, (int, float)) else v
                for k, v in params.items()
            },
            # Strategy 2: Try with positive values for numeric parameters
            lambda params: {
                k: max(0, v) if isinstance(v, (int, float)) else v
                for k, v in params.items()
            },
            # Strategy 3: Try with default values (1 for numbers, empty string for strings)
            lambda params: {
                k: (
                    (1 if isinstance(v, (int, float)) else "")
                    if v is None or (isinstance(v, (int, float)) and v < 0)
                    else v
                )
                for k, v in params.items()
            },
            # Strategy 4: Try with zero for numeric parameters
            lambda params: {
                k: 0 if isinstance(v, (int, float)) else v for k, v in params.items()
            },
        ]

        for i, strategy in enumerate(modification_strategies):
            try:
                self.logger.info(
                    f"RetryWithAlternatePromptStrategy: Trying modification strategy {i + 1}/{len(modification_strategies)} for {node_name}"
                )

                # Apply the modification strategy
                modified_params = strategy(validated_params)

                if context is not None:
                    output = handler_func(**modified_params, context=context)
                else:
                    output = handler_func(**modified_params)

                self.logger.info(
                    f"RetryWithAlternatePromptStrategy: Success with strategy {i + 1} for {node_name}"
                )

                return ExecutionResult(
                    success=True,
                    node_name=node_name,
                    node_path=[node_name],
                    node_type=NodeType.ACTION,
                    input=user_input,
                    output=output,
                    error=None,
                    params=modified_params,
                    children_results=[],
                )

            except Exception as e:
                self.logger.warning(
                    f"RetryWithAlternatePromptStrategy: Strategy {i + 1} failed for {node_name}: {type(e).__name__}: {str(e)}"
                )

        self.logger.error(
            f"RetryWithAlternatePromptStrategy: All {len(modification_strategies)} strategies failed for {node_name}"
        )
        return None


class RemediationRegistry:
    """Registry for remediation strategies."""

    def __init__(self):
        self._strategies: Dict[str, RemediationStrategy] = {}
        self._register_builtin_strategies()

    def _register_builtin_strategies(self):
        """Register built-in remediation strategies."""
        # These will be registered when strategies are created
        pass

    def register(self, strategy_id: str, strategy: RemediationStrategy):
        """Register a remediation strategy."""
        self._strategies[strategy_id] = strategy

    def get(self, strategy_id: str) -> Optional[RemediationStrategy]:
        """Get a remediation strategy by ID."""
        return self._strategies.get(strategy_id)

    def list_strategies(self) -> List[str]:
        """List all registered strategy IDs."""
        return list(self._strategies.keys())


# Global registry instance
_remediation_registry = RemediationRegistry()


def register_remediation_strategy(strategy_id: str, strategy: RemediationStrategy):
    """Register a remediation strategy in the global registry."""
    _remediation_registry.register(strategy_id, strategy)


def get_remediation_strategy(strategy_id: str) -> Optional[RemediationStrategy]:
    """Get a remediation strategy from the global registry."""
    return _remediation_registry.get(strategy_id)


def list_remediation_strategies() -> List[str]:
    """List all registered remediation strategies."""
    return _remediation_registry.list_strategies()


def create_retry_strategy(
    max_attempts: int = 3, base_delay: float = 1.0
) -> RemediationStrategy:
    """Create a retry strategy with specified parameters."""
    strategy = RetryOnFailStrategy(max_attempts=max_attempts, base_delay=base_delay)
    register_remediation_strategy("retry_on_fail", strategy)
    return strategy


def create_fallback_strategy(
    fallback_handler: Callable, fallback_name: str = "fallback"
) -> RemediationStrategy:
    """Create a fallback strategy with specified handler."""
    strategy = FallbackToAnotherNodeStrategy(fallback_handler, fallback_name)
    register_remediation_strategy("fallback_to_another_node", strategy)
    return strategy


def create_self_reflect_strategy(
    llm_config: Dict[str, Any], max_reflections: int = 2
) -> RemediationStrategy:
    """Create a self-reflection strategy with specified LLM config."""
    strategy = SelfReflectStrategy(llm_config, max_reflections)
    register_remediation_strategy("self_reflect", strategy)
    return strategy


def create_consensus_vote_strategy(
    llm_configs: List[Dict[str, Any]], vote_threshold: float = 0.6
) -> RemediationStrategy:
    """Create a consensus voting strategy with multiple LLM configs."""
    strategy = ConsensusVoteStrategy(llm_configs, vote_threshold)
    register_remediation_strategy("consensus_vote", strategy)
    return strategy


def create_alternate_prompt_strategy(
    llm_config: Dict[str, Any], alternate_prompts: Optional[List[str]] = None
) -> RemediationStrategy:
    """Create an alternate prompt strategy with specified prompts."""
    if alternate_prompts is None:
        alternate_prompts = [
            "Please try a different approach: {user_input}",
            "Consider this alternative perspective: {user_input}",
            "Let's approach this step by step: {user_input}",
            "Think about this from a different angle: {user_input}",
        ]
    strategy = RetryWithAlternatePromptStrategy(llm_config, alternate_prompts)
    register_remediation_strategy("retry_with_alternate_prompt", strategy)
    return strategy


# Initialize built-in strategies
create_retry_strategy()
create_fallback_strategy(
    lambda **kwargs: "Fallback handler executed", "default_fallback"
)


class ClassifierFallbackStrategy(RemediationStrategy):
    """Fallback strategy for classifiers that tries alternative classification methods."""

    def __init__(
        self, fallback_classifier: Callable, fallback_name: str = "fallback_classifier"
    ):
        super().__init__("classifier_fallback", f"Fallback to {fallback_name}")
        self.fallback_classifier = fallback_classifier
        self.fallback_name = fallback_name

    def execute(
        self,
        node_name: str,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        classifier_func: Optional[Callable] = None,
        available_children: Optional[List] = None,
        **kwargs,
    ) -> Optional[ExecutionResult]:
        """Execute the fallback classifier."""
        try:
            self.logger.info(
                f"ClassifierFallbackStrategy: Executing {self.fallback_name} for {node_name}"
            )

            if not available_children:
                self.logger.warning(
                    f"ClassifierFallbackStrategy: No available children for {node_name}"
                )
                return None

            # Try the fallback classifier
            context_dict: dict = {}
            if context:
                context_dict = {}

            chosen = self.fallback_classifier(
                user_input, available_children, context_dict
            )

            if not chosen:
                self.logger.warning(
                    f"ClassifierFallbackStrategy: Fallback classifier failed for {node_name}"
                )
                return None

            # Execute the chosen child
            child_result = chosen.execute(user_input, context)

            return ExecutionResult(
                success=True,
                node_name=self.fallback_name,
                node_path=[self.fallback_name],
                node_type=NodeType.CLASSIFIER,
                input=user_input,
                output=child_result.output,
                error=None,
                params={
                    "chosen_child": chosen.name,
                    "available_children": [child.name for child in available_children],
                    "remediation_strategy": self.name,
                },
                children_results=[child_result],
            )

        except Exception as e:
            self.logger.error(
                f"ClassifierFallbackStrategy: Fallback {self.fallback_name} failed for {node_name}: {type(e).__name__}: {str(e)}"
            )
            return None


class KeywordFallbackStrategy(RemediationStrategy):
    """Keyword-based fallback strategy for classifiers."""

    def __init__(self):
        super().__init__("keyword_fallback", "Keyword-based classification fallback")

    def execute(
        self,
        node_name: str,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        classifier_func: Optional[Callable] = None,
        available_children: Optional[List] = None,
        **kwargs,
    ) -> Optional[ExecutionResult]:
        """Use keyword matching as fallback classification."""
        try:
            self.logger.info(
                f"KeywordFallbackStrategy: Using keyword fallback for {node_name}"
            )

            if not available_children:
                self.logger.warning(
                    f"KeywordFallbackStrategy: No available children for {node_name}"
                )
                return None

            user_input_lower = user_input.lower()

            # Simple keyword matching based on handler names and descriptions
            for child in available_children:
                # Check handler name
                if child.name and child.name.lower() in user_input_lower:
                    self.logger.info(
                        f"KeywordFallbackStrategy: Matched '{child.name}' by name for {node_name}"
                    )
                    child_result = child.execute(user_input, context)
                    return ExecutionResult(
                        success=True,
                        node_name=node_name,
                        node_path=[node_name],
                        node_type=NodeType.CLASSIFIER,
                        input=user_input,
                        output=child_result.output,
                        error=None,
                        params={
                            "chosen_child": child.name,
                            "available_children": [c.name for c in available_children],
                            "remediation_strategy": self.name,
                            "match_type": "name",
                        },
                        children_results=[child_result],
                    )

                # Check description keywords
                if child.description:
                    desc_lower = child.description.lower()
                    # Extract meaningful words from description
                    desc_words = [
                        word
                        for word in desc_lower.split()
                        if len(word) > 3
                        and word not in ["the", "and", "for", "with", "this", "that"]
                    ]

                    for word in desc_words:
                        if word in user_input_lower:
                            self.logger.info(
                                f"KeywordFallbackStrategy: Matched '{child.name}' by description keyword '{word}' for {node_name}"
                            )
                            child_result = child.execute(user_input, context)
                            return ExecutionResult(
                                success=True,
                                node_name=node_name,
                                node_path=[node_name],
                                node_type=NodeType.CLASSIFIER,
                                input=user_input,
                                output=child_result.output,
                                error=None,
                                params={
                                    "chosen_child": child.name,
                                    "available_children": [
                                        c.name for c in available_children
                                    ],
                                    "remediation_strategy": self.name,
                                    "match_type": "description",
                                    "matched_keyword": word,
                                },
                                children_results=[child_result],
                            )

            self.logger.warning(
                f"KeywordFallbackStrategy: No keyword match found for {node_name}"
            )
            return None

        except Exception as e:
            self.logger.error(
                f"KeywordFallbackStrategy: Keyword fallback failed for {node_name}: {type(e).__name__}: {str(e)}"
            )
            return None


def create_classifier_fallback_strategy(
    fallback_classifier: Callable, fallback_name: str = "fallback_classifier"
) -> RemediationStrategy:
    """Create a classifier fallback strategy with specified classifier."""
    strategy = ClassifierFallbackStrategy(fallback_classifier, fallback_name)
    register_remediation_strategy("classifier_fallback", strategy)
    return strategy


def create_keyword_fallback_strategy() -> RemediationStrategy:
    """Create a keyword-based fallback strategy for classifiers."""
    strategy = KeywordFallbackStrategy()
    register_remediation_strategy("keyword_fallback", strategy)
    return strategy


# Initialize classifier-specific strategies
create_keyword_fallback_strategy()
