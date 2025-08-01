"""
Fluent builder for creating ActionNode instances.
Supports both stateless functions and stateful callable objects as actions.
"""

from intent_kit.nodes.base_builder import BaseBuilder
from typing import Any, Callable, Dict, Type, Set, List, Optional, Union
from intent_kit.nodes.actions.node import ActionNode, RemediationStrategy
from intent_kit.nodes.actions.param_extraction import (
    create_arg_extractor,
    parse_param_schema,
)
from intent_kit.services.ai.base_client import BaseLLMClient
from intent_kit.utils.logger import get_logger

LLMConfig = Union[Dict[str, Any], BaseLLMClient]


class ActionBuilder(BaseBuilder[ActionNode]):
    """
    Builder for ActionNode supporting both stateless and stateful callables.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.logger = get_logger("ActionBuilder")
        # Can be function or instance
        self.action_func: Optional[Callable[..., Any]] = None
        self.param_schema: Optional[Dict[str, Type]] = None
        self.llm_config: Optional[LLMConfig] = None
        self.extraction_prompt: Optional[str] = None
        self.context_inputs: Optional[Set[str]] = None
        self.context_outputs: Optional[Set[str]] = None
        self.input_validator: Optional[Callable[[Dict[str, Any]], bool]] = None
        self.output_validator: Optional[Callable[[Any], bool]] = None
        self.remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = (
            None
        )

    @staticmethod
    def from_json(
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
        llm_config: Optional[LLMConfig] = None,
    ) -> "ActionBuilder":
        """
        Create an ActionNode from JSON spec.
        Supports function names (resolved via function_registry) or full callable objects (for stateful actions).
        """
        node_id = node_spec.get("id") or node_spec.get("name")
        if not node_id:
            raise ValueError(f"Node spec must have 'id' or 'name': {node_spec}")

        name = node_spec.get("name", node_id)
        description = node_spec.get("description", "")

        # Resolve action (function or stateful callable)
        action = node_spec.get("function")
        action_obj = None
        if isinstance(action, str):
            if action not in function_registry:
                raise ValueError(f"Function '{action}' not found for node '{node_id}'")
            action_obj = function_registry[action]
        elif callable(action):
            action_obj = action
        else:
            raise ValueError(
                f"Action for node '{node_id}' must be a function name or callable object"
            )

        builder = ActionBuilder(name)
        builder.description = description
        builder.action_func = action_obj
        builder.logger.info(f"ActionBuilder param_schema: {builder.param_schema}")
        builder.param_schema = parse_param_schema(node_spec.get("param_schema", {}))

        # Use node-specific llm_config if present, otherwise use default
        if "llm_config" in node_spec:
            builder.llm_config = node_spec["llm_config"]
        else:
            builder.llm_config = llm_config

        # Optionals: allow set/list in JSON
        for k, m in [
            ("context_inputs", builder.with_context_inputs),
            ("context_outputs", builder.with_context_outputs),
            ("remediation_strategies", builder.with_remediation_strategies),
        ]:
            v = node_spec.get(k)
            if v:
                m(v)

        return builder

    def with_action(self, func: Callable[..., Any]) -> "ActionBuilder":
        """
        Accepts any callable—plain function, lambda, or class instance with __call__ (stateful).
        """
        self.action_func = func
        return self

    def with_param_schema(self, schema: Dict[str, Type]) -> "ActionBuilder":
        self.param_schema = schema
        return self

    def with_llm_config(self, config: Optional[LLMConfig]) -> "ActionBuilder":
        self.llm_config = config
        return self

    def with_extraction_prompt(self, prompt: str) -> "ActionBuilder":
        self.extraction_prompt = prompt
        return self

    def with_context_inputs(self, inputs: Any) -> "ActionBuilder":
        self.context_inputs = set(inputs)
        return self

    def with_context_outputs(self, outputs: Any) -> "ActionBuilder":
        self.context_outputs = set(outputs)
        return self

    def with_input_validator(
        self, fn: Callable[[Dict[str, Any]], bool]
    ) -> "ActionBuilder":
        self.input_validator = fn
        return self

    def with_output_validator(self, fn: Callable[[Any], bool]) -> "ActionBuilder":
        self.output_validator = fn
        return self

    def with_remediation_strategies(self, strategies: Any) -> "ActionBuilder":
        self.remediation_strategies = list(strategies)
        return self

    def build(self) -> ActionNode:
        """Build and return the ActionNode instance.

        Returns:
            Configured ActionNode instance

        Raises:
            ValueError: If required fields are missing
        """
        self._validate_required_fields(
            [
                ("action function", self.action_func, "with_action"),
                ("parameter schema", self.param_schema, "with_param_schema"),
            ]
        )

        # Type assertions after validation
        assert self.action_func is not None
        assert self.param_schema is not None

        arg_extractor = create_arg_extractor(
            param_schema=self.param_schema,
            llm_config=self.llm_config,
            extraction_prompt=self.extraction_prompt,
            node_name=self.name,
        )

        return ActionNode(
            name=self.name,
            param_schema=self.param_schema,
            action=self.action_func,  # <-- can be function or stateful object!
            arg_extractor=arg_extractor,
            context_inputs=self.context_inputs,
            context_outputs=self.context_outputs,
            input_validator=self.input_validator,
            output_validator=self.output_validator,
            description=self.description,
            remediation_strategies=self.remediation_strategies,
        )
