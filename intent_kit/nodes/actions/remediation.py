"""
Remediation strategies for intent-kit.

This module provides a pluggable remediation system for handling node execution failures.
Strategies can be registered by string ID or as custom callable functions.
"""

import time
from typing import Any, Callable, Dict, List, Optional
from ..types import ExecutionResult, ExecutionError
from ..enums import NodeType
from intent_kit.context import IntentContext
from intent_kit.utils.logger import Logger
from intent_kit.utils.text_utils import extract_json_from_text


class Strategy:
    """Base class for all strategies."""

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
        Execute the strategy.

        Args:
            node_name: Name of the node that failed
            user_input: Original user input
            context: Optional context object
            original_error: The original error that triggered remediation
            **kwargs: Additional strategy-specific parameters

        Returns:
            ExecutionResult if strategy succeeded, None if it failed
        """
        raise NotImplementedError("Subclasses must implement execute()")


class RemediationStrategy(Strategy):
    """Base class for remediation strategies."""

    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)

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
        print(f"[DEBUG] Entered RetryOnFailStrategy for node: {node_name}")
        if not handler_func or validated_params is None:
            self.logger.warning(
                f"RetryOnFailStrategy: Missing action_func or validated_params for {node_name}"
            )
            return None

        for attempt in range(1, self.max_attempts + 1):
            try:
                print(
                    f"[DEBUG] RetryOnFailStrategy: Attempt {attempt}/{self.max_attempts} for {node_name}"
                )
                self.logger.info(
                    f"RetryOnFailStrategy: Attempt {attempt}/{self.max_attempts} for {node_name}"
                )

                # Add context if available
                if context is not None:
                    output = handler_func(**validated_params, context=context)
                else:
                    output = handler_func(**validated_params)

                print(
                    f"[DEBUG] RetryOnFailStrategy: Success on attempt {attempt} for {node_name}"
                )
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
                    params=validated_params,
                )

            except Exception as e:
                print(
                    f"[DEBUG] RetryOnFailStrategy: Attempt {attempt} failed for {node_name}: {e}"
                )
                self.logger.warning(
                    f"RetryOnFailStrategy: Attempt {attempt} failed for {node_name}: {e}"
                )

                if attempt < self.max_attempts:
                    delay = max(0, self.base_delay * (2 ** (attempt - 1)))
                    print(
                        f"[DEBUG] RetryOnFailStrategy: Waiting {delay}s before retry for {node_name}"
                    )
                    time.sleep(delay)

        print(
            f"[DEBUG] RetryOnFailStrategy: All {self.max_attempts} attempts failed for {node_name}"
        )
        self.logger.error(
            f"RetryOnFailStrategy: All {self.max_attempts} attempts failed for {node_name}"
        )
        return None


class FallbackToAnotherNodeStrategy(RemediationStrategy):
    """Fallback to another node when the primary node fails."""

    def __init__(self, fallback_handler: Callable, fallback_name: str = "fallback"):
        super().__init__(
            "fallback_to_another_node",
            f"Fallback to {fallback_name} when primary node fails",
        )
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
        print(f"[DEBUG] Entered FallbackToAnotherNodeStrategy for node: {node_name}")
        if not validated_params:
            validated_params = {}

        try:
            print(
                f"[DEBUG] FallbackToAnotherNodeStrategy: Executing fallback {self.fallback_name}"
            )
            self.logger.info(
                f"FallbackToAnotherNodeStrategy: Executing fallback {self.fallback_name}"
            )

            # Add context if available
            if context is not None:
                output = self.fallback_handler(**validated_params, context=context)
            else:
                output = self.fallback_handler(**validated_params)

            print(
                f"[DEBUG] FallbackToAnotherNodeStrategy: Success with fallback {self.fallback_name}"
            )
            self.logger.info(
                f"FallbackToAnotherNodeStrategy: Success with fallback {self.fallback_name}"
            )

            return ExecutionResult(
                success=True,
                node_name=node_name,
                node_path=[node_name],
                node_type=NodeType.ACTION,
                input=user_input,
                output=output,
                params=validated_params,
            )

        except Exception as e:
            print(
                f"[DEBUG] FallbackToAnotherNodeStrategy: Fallback {self.fallback_name} failed: {e}"
            )
            self.logger.error(
                f"FallbackToAnotherNodeStrategy: Fallback {self.fallback_name} failed: {e}"
            )
            return None


class SelfReflectStrategy(RemediationStrategy):
    """Use LLM to reflect on the error and generate a corrected response."""

    def __init__(self, llm_config: Dict[str, Any], max_reflections: int = 2):
        super().__init__(
            "self_reflect",
            f"Use LLM to reflect on errors up to {max_reflections} times",
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
        print(f"[DEBUG] Entered SelfReflectStrategy for node: {node_name}")
        if not handler_func or validated_params is None:
            self.logger.warning(
                f"SelfReflectStrategy: Missing handler_func or validated_params for {node_name}"
            )
            return None

        from intent_kit.services.ai.llm_factory import LLMFactory

        llm = LLMFactory.create_client(self.llm_config)

        for reflection in range(self.max_reflections):
            try:
                print(
                    f"[DEBUG] SelfReflectStrategy: Reflection {reflection + 1}/{self.max_reflections} for {node_name}"
                )
                self.logger.info(
                    f"SelfReflectStrategy: Reflection {reflection + 1}/{self.max_reflections} for {node_name}"
                )

                # Create reflection prompt
                error_msg = str(original_error) if original_error else "Unknown error"
                reflection_prompt = f"""
                The following error occurred while processing user input: "{user_input}"

                Error: {error_msg}

                Please analyze the error and provide a corrected response. The response should be in JSON format with the following structure:
                {{
                    "corrected_params": {{
                        // corrected parameters here
                    }},
                    "explanation": "Brief explanation of what was wrong and how it was fixed"
                }}

                Original parameters were: {validated_params}
                """

                # Get LLM response
                response = llm.generate(reflection_prompt)
                print(f"[DEBUG] SelfReflectStrategy: LLM response: {response}")

                # Extract JSON from response
                json_data = extract_json_from_text(response)
                if not json_data:
                    print(
                        "[DEBUG] SelfReflectStrategy: Failed to extract JSON from response"
                    )
                    continue

                corrected_params = json_data.get("corrected_params", {})
                explanation = json_data.get("explanation", "No explanation provided")

                print(
                    f"[DEBUG] SelfReflectStrategy: Corrected params: {corrected_params}"
                )
                self.logger.info(
                    f"SelfReflectStrategy: Corrected params: {corrected_params}, Explanation: {explanation}"
                )

                # Try with corrected parameters
                if context is not None:
                    output = handler_func(**corrected_params, context=context)
                else:
                    output = handler_func(**corrected_params)

                print(
                    f"[DEBUG] SelfReflectStrategy: Success on reflection {reflection + 1} for {node_name}"
                )
                self.logger.info(
                    f"SelfReflectStrategy: Success on reflection {reflection + 1} for {node_name}"
                )

                return ExecutionResult(
                    success=True,
                    node_name=node_name,
                    node_path=[node_name],
                    node_type=NodeType.ACTION,
                    input=user_input,
                    output=output,
                    params=corrected_params,
                )

            except Exception as e:
                print(
                    f"[DEBUG] SelfReflectStrategy: Reflection {reflection + 1} failed for {node_name}: {e}"
                )
                self.logger.warning(
                    f"SelfReflectStrategy: Reflection {reflection + 1} failed for {node_name}: {e}"
                )

        print(
            f"[DEBUG] SelfReflectStrategy: All {self.max_reflections} reflections failed for {node_name}"
        )
        self.logger.error(
            f"SelfReflectStrategy: All {self.max_reflections} reflections failed for {node_name}"
        )
        return None


class ConsensusVoteStrategy(RemediationStrategy):
    """Use multiple LLMs to vote on the best response."""

    def __init__(self, llm_configs: List[Dict[str, Any]], vote_threshold: float = 0.6):
        super().__init__(
            "consensus_vote",
            f"Use {len(llm_configs)} LLMs to vote on response (threshold: {vote_threshold})",
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
        print(f"[DEBUG] Entered ConsensusVoteStrategy for node: {node_name}")
        if not handler_func or validated_params is None:
            self.logger.warning(
                f"ConsensusVoteStrategy: Missing handler_func or validated_params for {node_name}"
            )
            return None

        from intent_kit.services.ai.llm_factory import LLMFactory

        llms = [LLMFactory.create_client(config) for config in self.llm_configs]

        # Create voting prompt
        error_msg = str(original_error) if original_error else "Unknown error"
        voting_prompt = f"""
        The following error occurred while processing user input: "{user_input}"

        Error: {error_msg}

        Please analyze the error and provide a corrected response. The response should be in JSON format with the following structure:
        {{
            "corrected_params": {{
                // corrected parameters here
            }},
            "confidence": 0.85,
            "explanation": "Brief explanation of what was wrong and how it was fixed"
        }}

        Original parameters were: {validated_params}

        The confidence should be a float between 0.0 and 1.0 indicating how confident you are in this correction.
        """

        votes = []
        for i, llm in enumerate(llms):
            try:
                print(
                    f"[DEBUG] ConsensusVoteStrategy: Getting vote from LLM {i + 1}/{len(llms)}"
                )
                response = llm.generate(voting_prompt)
                print(
                    f"[DEBUG] ConsensusVoteStrategy: LLM {i + 1} response: {response}"
                )

                json_data = extract_json_from_text(response)
                if not json_data:
                    print(
                        f"[DEBUG] ConsensusVoteStrategy: Failed to extract JSON from LLM {i + 1} response"
                    )
                    continue

                corrected_params = json_data.get("corrected_params", {})
                confidence = json_data.get("confidence", 0.0)
                explanation = json_data.get("explanation", "No explanation provided")

                votes.append(
                    {
                        "params": corrected_params,
                        "confidence": confidence,
                        "explanation": explanation,
                        "llm_index": i,
                    }
                )

                print(
                    f"[DEBUG] ConsensusVoteStrategy: LLM {i + 1} vote - confidence: {confidence}, explanation: {explanation}"
                )

            except Exception as e:
                print(f"[DEBUG] ConsensusVoteStrategy: LLM {i + 1} failed: {e}")
                self.logger.warning(f"ConsensusVoteStrategy: LLM {i + 1} failed: {e}")

        if not votes:
            print(
                f"[DEBUG] ConsensusVoteStrategy: No valid votes received for {node_name}"
            )
            self.logger.error(
                f"ConsensusVoteStrategy: No valid votes received for {node_name}"
            )
            return None

        # Find the best vote based on confidence
        best_vote = max(votes, key=lambda v: v["confidence"])
        best_confidence = best_vote["confidence"]

        print(
            f"[DEBUG] ConsensusVoteStrategy: Best vote confidence: {best_confidence} (threshold: {self.vote_threshold})"
        )

        if best_confidence < self.vote_threshold:
            print(
                f"[DEBUG] ConsensusVoteStrategy: Best confidence {best_confidence} below threshold {self.vote_threshold} for {node_name}"
            )
            self.logger.warning(
                f"ConsensusVoteStrategy: Best confidence {best_confidence} below threshold {self.vote_threshold} for {node_name}"
            )
            return None

        # Try with the best voted parameters
        try:
            corrected_params = best_vote["params"]
            explanation = best_vote["explanation"]

            print(
                f"[DEBUG] ConsensusVoteStrategy: Trying with best voted params: {corrected_params}"
            )
            self.logger.info(
                f"ConsensusVoteStrategy: Trying with best voted params: {corrected_params}, Explanation: {explanation}"
            )

            if context is not None:
                output = handler_func(**corrected_params, context=context)
            else:
                output = handler_func(**corrected_params)

            print(
                f"[DEBUG] ConsensusVoteStrategy: Success with voted params for {node_name}"
            )
            self.logger.info(
                f"ConsensusVoteStrategy: Success with voted params for {node_name}"
            )

            return ExecutionResult(
                success=True,
                node_name=node_name,
                node_path=[node_name],
                node_type=NodeType.ACTION,
                input=user_input,
                output=output,
                params=corrected_params,
            )

        except Exception as e:
            print(
                f"[DEBUG] ConsensusVoteStrategy: Execution with voted params failed for {node_name}: {e}"
            )
            self.logger.error(
                f"ConsensusVoteStrategy: Execution with voted params failed for {node_name}: {e}"
            )
            return None


class RetryWithAlternatePromptStrategy(RemediationStrategy):
    """Retry with alternate prompts when the original fails."""

    def __init__(
        self, llm_config: Dict[str, Any], alternate_prompts: Optional[List[str]] = None
    ):
        super().__init__(
            "retry_with_alternate_prompt",
            f"Retry with {len(alternate_prompts) if alternate_prompts else 'default'} alternate prompts",
        )
        self.llm_config = llm_config
        self.alternate_prompts = alternate_prompts or [
            "Please try a different approach to solve this problem.",
            "Consider alternative methods to achieve the same goal.",
            "Think about this problem from a different perspective.",
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
        print(f"[DEBUG] Entered RetryWithAlternatePromptStrategy for node: {node_name}")
        if not handler_func or validated_params is None:
            self.logger.warning(
                f"RetryWithAlternatePromptStrategy: Missing handler_func or validated_params for {node_name}"
            )
            return None

        from intent_kit.services.ai.llm_factory import LLMFactory

        llm = LLMFactory.create_client(self.llm_config)

        error_msg = str(original_error) if original_error else "Unknown error"

        for i, alternate_prompt in enumerate(self.alternate_prompts):
            try:
                print(
                    f"[DEBUG] RetryWithAlternatePromptStrategy: Trying alternate prompt {i + 1}/{len(self.alternate_prompts)} for {node_name}"
                )
                self.logger.info(
                    f"RetryWithAlternatePromptStrategy: Trying alternate prompt {i + 1}/{len(self.alternate_prompts)} for {node_name}"
                )

                # Create prompt with alternate approach
                full_prompt = f"""
                The following error occurred while processing user input: "{user_input}"

                Error: {error_msg}

                {alternate_prompt}

                Please provide a corrected response in JSON format with the following structure:
                {{
                    "corrected_params": {{
                        // corrected parameters here
                    }},
                    "explanation": "Brief explanation of the alternate approach used"
                }}

                Original parameters were: {validated_params}
                """

                # Get LLM response
                response = llm.generate(full_prompt)
                print(
                    f"[DEBUG] RetryWithAlternatePromptStrategy: LLM response: {response}"
                )

                # Extract JSON from response
                json_data = extract_json_from_text(response)
                if not json_data:
                    print(
                        f"[DEBUG] RetryWithAlternatePromptStrategy: Failed to extract JSON from response for prompt {i + 1}"
                    )
                    continue

                corrected_params = json_data.get("corrected_params", {})
                explanation = json_data.get("explanation", "No explanation provided")

                print(
                    f"[DEBUG] RetryWithAlternatePromptStrategy: Corrected params: {corrected_params}"
                )
                self.logger.info(
                    f"RetryWithAlternatePromptStrategy: Corrected params: {corrected_params}, Explanation: {explanation}"
                )

                # Try with corrected parameters
                if context is not None:
                    output = handler_func(**corrected_params, context=context)
                else:
                    output = handler_func(**corrected_params)

                print(
                    f"[DEBUG] RetryWithAlternatePromptStrategy: Success with alternate prompt {i + 1} for {node_name}"
                )
                self.logger.info(
                    f"RetryWithAlternatePromptStrategy: Success with alternate prompt {i + 1} for {node_name}"
                )

                return ExecutionResult(
                    success=True,
                    node_name=node_name,
                    node_path=[node_name],
                    node_type=NodeType.ACTION,
                    input=user_input,
                    output=output,
                    params=corrected_params,
                )

            except Exception as e:
                print(
                    f"[DEBUG] RetryWithAlternatePromptStrategy: Alternate prompt {i + 1} failed for {node_name}: {e}"
                )
                self.logger.warning(
                    f"RetryWithAlternatePromptStrategy: Alternate prompt {i + 1} failed for {node_name}: {e}"
                )

        print(
            f"[DEBUG] RetryWithAlternatePromptStrategy: All {len(self.alternate_prompts)} alternate prompts failed for {node_name}"
        )
        self.logger.error(
            f"RetryWithAlternatePromptStrategy: All {len(self.alternate_prompts)} alternate prompts failed for {node_name}"
        )
        return None


class RemediationRegistry:
    """Registry for remediation strategies."""

    def __init__(self):
        self._strategies: Dict[str, RemediationStrategy] = {}
        self._register_builtin_strategies()

    def _register_builtin_strategies(self):
        """Register built-in remediation strategies."""
        self.register("retry_on_fail", RetryOnFailStrategy())
        self.register(
            "fallback_to_another_node", FallbackToAnotherNodeStrategy(lambda: None)
        )
        self.register("self_reflect", SelfReflectStrategy({}))
        self.register("consensus_vote", ConsensusVoteStrategy([{}]))
        self.register(
            "retry_with_alternate_prompt", RetryWithAlternatePromptStrategy({})
        )

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
_registry = RemediationRegistry()


def register_remediation_strategy(strategy_id: str, strategy: RemediationStrategy):
    """Register a remediation strategy globally."""
    _registry.register(strategy_id, strategy)


def get_remediation_strategy(strategy_id: str) -> Optional[RemediationStrategy]:
    """Get a remediation strategy by ID from the global registry."""
    return _registry.get(strategy_id)


def list_remediation_strategies() -> List[str]:
    """List all registered remediation strategy IDs."""
    return _registry.list_strategies()


# Factory functions for creating strategies
def create_retry_strategy(
    max_attempts: int = 3, base_delay: float = 1.0
) -> RemediationStrategy:
    """Create a retry strategy."""
    return RetryOnFailStrategy(max_attempts=max_attempts, base_delay=base_delay)


def create_fallback_strategy(
    fallback_handler: Callable, fallback_name: str = "fallback"
) -> RemediationStrategy:
    """Create a fallback strategy."""
    return FallbackToAnotherNodeStrategy(fallback_handler, fallback_name)


def create_self_reflect_strategy(
    llm_config: Dict[str, Any], max_reflections: int = 2
) -> RemediationStrategy:
    """Create a self-reflect strategy."""
    return SelfReflectStrategy(llm_config, max_reflections)


def create_consensus_vote_strategy(
    llm_configs: List[Dict[str, Any]], vote_threshold: float = 0.6
) -> RemediationStrategy:
    """Create a consensus vote strategy."""
    return ConsensusVoteStrategy(llm_configs, vote_threshold)


def create_alternate_prompt_strategy(
    llm_config: Dict[str, Any], alternate_prompts: Optional[List[str]] = None
) -> RemediationStrategy:
    """Create a retry with alternate prompt strategy."""
    return RetryWithAlternatePromptStrategy(llm_config, alternate_prompts)


class ClassifierFallbackStrategy(RemediationStrategy):
    """Fallback strategy for classifier nodes."""

    def __init__(
        self, fallback_classifier: Callable, fallback_name: str = "fallback_classifier"
    ):
        super().__init__(
            "classifier_fallback",
            f"Fallback to {fallback_name} when primary classifier fails",
        )
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
        print(f"[DEBUG] Entered ClassifierFallbackStrategy for node: {node_name}")
        if not available_children:
            self.logger.warning(
                f"ClassifierFallbackStrategy: No available children for {node_name}"
            )
            return None

        try:
            print(
                f"[DEBUG] ClassifierFallbackStrategy: Executing fallback {self.fallback_name}"
            )
            self.logger.info(
                f"ClassifierFallbackStrategy: Executing fallback {self.fallback_name}"
            )

            # Execute fallback classifier
            if context is not None:
                result = self.fallback_classifier(user_input, context=context)
            else:
                result = self.fallback_classifier(user_input)

            print(f"[DEBUG] ClassifierFallbackStrategy: Fallback result: {result}")

            # Find the child that matches the fallback classifier result
            best_child = None
            best_score = 0

            for child in available_children:
                if hasattr(child, "name") and child.name == result:
                    best_child = child
                    best_score = 1
                    break

            if best_child:
                print(
                    f"[DEBUG] ClassifierFallbackStrategy: Selected child '{best_child.name}' with score {best_score}"
                )
                self.logger.info(
                    f"ClassifierFallbackStrategy: Selected child '{best_child.name}' with score {best_score}"
                )

                return ExecutionResult(
                    success=True,
                    node_name=node_name,
                    node_path=[node_name],
                    node_type=NodeType.CLASSIFIER,
                    input=user_input,
                    output=best_child.name,
                    params={"selected_child": best_child.name, "score": best_score},
                )
            else:
                print(
                    f"[DEBUG] ClassifierFallbackStrategy: No suitable child found for {node_name}"
                )
                self.logger.warning(
                    f"ClassifierFallbackStrategy: No suitable child found for {node_name}"
                )
                return None

        except Exception as e:
            print(
                f"[DEBUG] ClassifierFallbackStrategy: Fallback {self.fallback_name} failed: {e}"
            )
            self.logger.error(
                f"ClassifierFallbackStrategy: Fallback {self.fallback_name} failed: {e}"
            )
            return None


class KeywordFallbackStrategy(RemediationStrategy):
    """Keyword-based fallback strategy for classifier nodes."""

    def __init__(self):
        super().__init__(
            "keyword_fallback",
            "Use keyword matching to select child node",
        )

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
        print(f"[DEBUG] Entered KeywordFallbackStrategy for node: {node_name}")
        if not available_children:
            self.logger.warning(
                f"KeywordFallbackStrategy: No available children for {node_name}"
            )
            return None

        try:
            print(
                f"[DEBUG] KeywordFallbackStrategy: Analyzing {len(available_children)} children for {node_name}"
            )
            self.logger.info(
                f"KeywordFallbackStrategy: Analyzing {len(available_children)} children for {node_name}"
            )

            # Find the best matching child using keyword matching
            best_child = None
            best_score = -1

            for child in available_children:
                if hasattr(child, "name") and hasattr(child, "description"):
                    # Create searchable text from child attributes
                    child_text = f"{child.name} {child.description}".lower()
                    input_lower = user_input.lower()

                    # Count exact word matches
                    input_words = set(input_lower.split())
                    child_words = set(child_text.split())
                    matches = len(input_words.intersection(child_words))

                    # Check if any input word is contained in the child name or vice versa
                    for input_word in input_words:
                        if len(input_word) > 3:
                            # Check if input word is in child name
                            if input_word in child.name.lower():
                                matches += 2
                            # Check if child name is in input word
                            elif child.name.lower() in input_word:
                                matches += 2
                            # Check for common prefixes (e.g., "calculate" and "calculator")
                            elif input_word.startswith(
                                child.name.lower()[:6]
                            ) or child.name.lower().startswith(input_word[:6]):
                                matches += 1

                    # Check if any input word is contained in the child description
                    for input_word in input_words:
                        if (
                            len(input_word) > 3
                            and input_word in child.description.lower()
                        ):
                            matches += 1

                    # Check if any child word is contained in the input
                    for child_word in child_words:
                        if len(child_word) > 3 and child_word in input_lower:
                            matches += 1

                    # Bonus for exact name matches
                    if child.name.lower() in input_lower:
                        matches += 2

                    # Bonus for description keywords
                    if child.description.lower() in input_lower:
                        matches += 1

                    print(
                        f"[DEBUG] KeywordFallbackStrategy: Child '{child.name}' score: {matches}"
                    )

                    if matches > best_score:
                        best_score = matches
                        best_child = child

            if best_child and best_score > 0:
                print(
                    f"[DEBUG] KeywordFallbackStrategy: Selected child '{best_child.name}' with score {best_score}"
                )
                self.logger.info(
                    f"KeywordFallbackStrategy: Selected child '{best_child.name}' with score {best_score}"
                )

                return ExecutionResult(
                    success=True,
                    node_name=node_name,
                    node_path=[node_name],
                    node_type=NodeType.CLASSIFIER,
                    input=user_input,
                    output=best_child.name,
                    params={"selected_child": best_child.name, "score": best_score},
                )
            else:
                print(
                    f"[DEBUG] KeywordFallbackStrategy: No suitable child found for {node_name}"
                )
                self.logger.warning(
                    f"KeywordFallbackStrategy: No suitable child found for {node_name}"
                )
                return None

        except Exception as e:
            print(f"[DEBUG] KeywordFallbackStrategy: Failed for {node_name}: {e}")
            self.logger.error(f"KeywordFallbackStrategy: Failed for {node_name}: {e}")
            return None


def create_classifier_fallback_strategy(
    fallback_classifier: Callable, fallback_name: str = "fallback_classifier"
) -> RemediationStrategy:
    """Create a classifier fallback strategy."""
    return ClassifierFallbackStrategy(fallback_classifier, fallback_name)


def create_keyword_fallback_strategy() -> RemediationStrategy:
    """Create a keyword fallback strategy."""
    return KeywordFallbackStrategy()
