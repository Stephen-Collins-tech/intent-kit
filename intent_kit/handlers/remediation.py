"""
Remediation strategies for intent-kit.

This module provides a pluggable remediation system for handling node execution failures.
Strategies can be registered by string ID or as custom callable functions.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from intent_kit.node.types import ExecutionResult, ExecutionError
from intent_kit.node.enums import NodeType
from intent_kit.context import IntentContext
from intent_kit.utils.logger import Logger


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
        **kwargs
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
        super().__init__("retry_on_fail",
                         f"Retry up to {max_attempts} times with exponential backoff")
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
        **kwargs
    ) -> Optional[ExecutionResult]:
        """Retry the handler function with the same parameters."""
        if not handler_func or validated_params is None:
            self.logger.warning(
                f"RetryOnFailStrategy: Missing handler_func or validated_params for {node_name}")
            return None

        for attempt in range(1, self.max_attempts + 1):
            try:
                self.logger.info(
                    f"RetryOnFailStrategy: Attempt {attempt}/{self.max_attempts} for {node_name}")

                if context is not None:
                    output = handler_func(**validated_params, context=context)
                else:
                    output = handler_func(**validated_params)

                # Success - return the result
                return ExecutionResult(
                    success=True,
                    node_name=node_name,
                    node_path=[node_name],  # Simplified path for retry
                    node_type=NodeType.HANDLER,  # Default to handler type
                    input=user_input,
                    output=output,
                    error=None,
                    params=validated_params,
                    children_results=[]
                )

            except Exception as e:
                self.logger.warning(
                    f"RetryOnFailStrategy: Attempt {attempt} failed for {node_name}: {type(e).__name__}: {str(e)}"
                )

                if attempt == self.max_attempts:
                    self.logger.error(
                        f"RetryOnFailStrategy: All {self.max_attempts} attempts failed for {node_name}")
                    return None

        return None


class FallbackToAnotherNodeStrategy(RemediationStrategy):
    """Fallback to a specified alternative handler."""

    def __init__(self, fallback_handler: Callable, fallback_name: str = "fallback"):
        super().__init__("fallback_to_another_node",
                         f"Fallback to {fallback_name}")
        self.fallback_handler = fallback_handler
        self.fallback_name = fallback_name

    def execute(
        self,
        node_name: str,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        validated_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[ExecutionResult]:
        """Execute the fallback handler."""
        try:
            self.logger.info(
                f"FallbackToAnotherNodeStrategy: Executing {self.fallback_name} for {node_name}")

            # Use the same parameters if possible, otherwise use minimal params
            if validated_params is not None:
                if context is not None:
                    output = self.fallback_handler(
                        **validated_params, context=context)
                else:
                    output = self.fallback_handler(**validated_params)
            else:
                # Minimal fallback with just the input
                if context is not None:
                    output = self.fallback_handler(
                        user_input=user_input, context=context)
                else:
                    output = self.fallback_handler(user_input=user_input)

            return ExecutionResult(
                success=True,
                node_name=self.fallback_name,
                node_path=[self.fallback_name],
                node_type=NodeType.HANDLER,  # Default to handler type
                input=user_input,
                output=output,
                error=None,
                params=validated_params or {},
                children_results=[]
            )

        except Exception as e:
            self.logger.error(
                f"FallbackToAnotherNodeStrategy: Fallback {self.fallback_name} failed for {node_name}: {type(e).__name__}: {str(e)}"
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


def create_retry_strategy(max_attempts: int = 3, base_delay: float = 1.0) -> RemediationStrategy:
    """Create a retry strategy with specified parameters."""
    strategy = RetryOnFailStrategy(
        max_attempts=max_attempts, base_delay=base_delay)
    register_remediation_strategy("retry_on_fail", strategy)
    return strategy


def create_fallback_strategy(fallback_handler: Callable, fallback_name: str = "fallback") -> RemediationStrategy:
    """Create a fallback strategy with specified handler."""
    strategy = FallbackToAnotherNodeStrategy(fallback_handler, fallback_name)
    register_remediation_strategy("fallback_to_another_node", strategy)
    return strategy


# Initialize built-in strategies
create_retry_strategy()
create_fallback_strategy(
    lambda **kwargs: "Fallback handler executed", "default_fallback")


class ClassifierFallbackStrategy(RemediationStrategy):
    """Fallback strategy for classifiers that tries alternative classification methods."""

    def __init__(self, fallback_classifier: Callable, fallback_name: str = "fallback_classifier"):
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
        **kwargs
    ) -> Optional[ExecutionResult]:
        """Execute the fallback classifier."""
        try:
            self.logger.info(
                f"ClassifierFallbackStrategy: Executing {self.fallback_name} for {node_name}")

            if not available_children:
                self.logger.warning(
                    f"ClassifierFallbackStrategy: No available children for {node_name}")
                return None

            # Try the fallback classifier
            context_dict = {}
            if context:
                context_dict = {}

            chosen = self.fallback_classifier(
                user_input, available_children, context_dict)

            if not chosen:
                self.logger.warning(
                    f"ClassifierFallbackStrategy: Fallback classifier failed for {node_name}")
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
                    "remediation_strategy": self.name
                },
                children_results=[child_result]
            )

        except Exception as e:
            self.logger.error(
                f"ClassifierFallbackStrategy: Fallback {self.fallback_name} failed for {node_name}: {type(e).__name__}: {str(e)}"
            )
            return None


class KeywordFallbackStrategy(RemediationStrategy):
    """Fallback to keyword-based classification when LLM classification fails."""

    def __init__(self):
        super().__init__("keyword_fallback", "Fallback to keyword-based classification")

    def execute(
        self,
        node_name: str,
        user_input: str,
        context: Optional[IntentContext] = None,
        original_error: Optional[ExecutionError] = None,
        classifier_func: Optional[Callable] = None,
        available_children: Optional[List] = None,
        **kwargs
    ) -> Optional[ExecutionResult]:
        """Use keyword matching as fallback classification."""
        try:
            self.logger.info(
                f"KeywordFallbackStrategy: Using keyword matching for {node_name}")

            if not available_children:
                self.logger.warning(
                    f"KeywordFallbackStrategy: No available children for {node_name}")
                return None

            # Simple keyword matching
            user_input_lower = user_input.lower()

            # Define keyword mappings for common intents
            keyword_mappings = {
                "greet": ["hello", "hi", "greet", "hey"],
                "calculate": ["calculate", "compute", "math", "add", "multiply", "plus", "times"],
                "weather": ["weather", "temperature", "forecast"],
                "help": ["help", "assist", "support"]
            }

            # Find the best match
            best_match = None
            best_score = 0

            for child in available_children:
                child_name_lower = child.name.lower()

                # Check direct name matching
                if child_name_lower in user_input_lower:
                    best_match = child
                    best_score = 1.0
                    break

                # Check keyword mappings
                if child_name_lower in keyword_mappings:
                    keywords = keyword_mappings[child_name_lower]
                    for keyword in keywords:
                        if keyword in user_input_lower:
                            # Simple scoring
                            score = len(keyword) / len(user_input_lower)
                            if score > best_score:
                                best_match = child
                                best_score = score

            if best_match and best_score > 0.1:  # Minimum threshold
                self.logger.info(
                    f"KeywordFallbackStrategy: Matched '{best_match.name}' with score {best_score}")

                # Execute the chosen child
                child_result = best_match.execute(user_input, context)

                return ExecutionResult(
                    success=True,
                    node_name=node_name,
                    node_path=[node_name],
                    node_type=NodeType.CLASSIFIER,
                    input=user_input,
                    output=child_result.output,
                    error=None,
                    params={
                        "chosen_child": best_match.name,
                        "available_children": [child.name for child in available_children],
                        "remediation_strategy": self.name,
                        "confidence_score": best_score
                    },
                    children_results=[child_result]
                )
            else:
                self.logger.warning(
                    f"KeywordFallbackStrategy: No keyword match found for {node_name}")
                return None

        except Exception as e:
            self.logger.error(
                f"KeywordFallbackStrategy: Keyword fallback failed for {node_name}: {type(e).__name__}: {str(e)}"
            )
            return None


def create_classifier_fallback_strategy(fallback_classifier: Callable, fallback_name: str = "fallback_classifier") -> RemediationStrategy:
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
