"""
Fluent builder for creating ClassifierNode instances.
Supports both rule-based and LLM-powered classifiers.
"""

import json

from intent_kit.nodes.base_builder import BaseBuilder
from intent_kit.services.ai.base_client import BaseLLMClient
from typing import Any, Dict, Union
from typing import Callable, List, Optional
from intent_kit.nodes import TreeNode
from intent_kit.nodes.classifiers.node import ClassifierNode
from intent_kit.services.ai.llm_factory import LLMFactory
from intent_kit.utils.logger import Logger
from intent_kit.nodes.actions.remediation import RemediationStrategy
from intent_kit.types import LLMResponse

logger = Logger(__name__)

# Type alias for llm_config to support both dict and BaseLLMClient
LLMConfig = Union[Dict[str, Any], BaseLLMClient]


def get_default_classification_prompt() -> str:
    """Get the default classification prompt template."""
    return """You are an intent classifier. Given a user input, select the most appropriate intent from the available options.

User Input: {user_input}

Available Intents:
{node_descriptions}

{context_info}

Instructions:
- Analyze the user input carefully
- Consider the available context information when making your decision
- Select the intent that best matches the user's request
- Return only the number (1-{num_nodes}) corresponding to your choice
- If no intent matches, return 0

Your choice (number only):"""


def create_default_classifier() -> Callable:
    """Create a default classifier that returns the first child."""

    def default_classifier(
        user_input: str,
        children: List[TreeNode],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[TreeNode]:
        return children[0] if children else None

    return default_classifier


class ClassifierBuilder(BaseBuilder[ClassifierNode]):
    """Builder for ClassifierNode supporting both rule-based and LLM classifiers."""

    def __init__(self, name: str):
        super().__init__(name)
        self.classifier_func: Optional[Callable] = None
        self.children: List[TreeNode] = []
        self.remediation_strategies: Optional[List[Union[str, RemediationStrategy]]] = (
            None
        )

    @staticmethod
    def from_json(
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
        llm_config: Optional[LLMConfig] = None,
    ) -> "ClassifierBuilder":
        """
        Create a ClassifierNode from JSON spec.
        Supports both rule-based classifiers (function names) and LLM classifiers.
        """
        node_id = node_spec.get("id") or node_spec.get("name")
        if not node_id:
            raise ValueError(f"Node spec must have 'id' or 'name': {node_spec}")

        name = node_spec.get("name", node_id)
        description = node_spec.get("description", "")
        classifier_type = node_spec.get("classifier_type", "rule")
        llm_config = node_spec.get("llm_config") or llm_config
        logger.debug(
            f"AFTER DEFAULT FALLBACK CHECK LLM classifier config: {llm_config}"
        )

        # Resolve classifier function
        classifier_func = None
        if classifier_type == "llm":
            # LLM classifier - will be configured later with children
            # Use the processed llm_config that was passed in (already processed by NodeFactory)
            if not llm_config:
                raise ValueError(f"LLM classifier '{node_id}' requires llm_config")
            classification_prompt = node_spec.get(
                "classification_prompt", get_default_classification_prompt()
            )

            # Create LLM classifier function that returns both node and response info
            def llm_classifier(
                user_input: str,
                children: List[TreeNode],
                context: Optional[Dict[str, Any]] = None,
            ) -> tuple[Optional[TreeNode], Optional[LLMResponse]]:

                logger = Logger(__name__)  # Added missing import
                logger.debug(f"LLM classifier input: {user_input}")
                if llm_config is None:
                    logger.error(
                        "No llm_config provided to LLM classifier. Please set a default on the graph or provide one at the node level."
                    )
                    return None, None

                try:
                    # Build the classification prompt with available children
                    child_descriptions = []
                    for child in children:
                        child_descriptions.append(
                            f"- {child.name}: {child.description}"
                        )

                    prompt = classification_prompt.format(
                        user_input=user_input,
                        node_descriptions="\n".join(child_descriptions),
                    )

                    # Get LLM response
                    if isinstance(llm_config, dict):
                        # Obfuscate API key in debug log
                        logger.debug(f"LLM classifier config IS A DICT: {llm_config}")
                        safe_config = llm_config.copy()
                        if "api_key" in safe_config:
                            safe_config["api_key"] = "***OBFUSCATED***"
                        logger.debug(f"LLM classifier config: {safe_config}")
                        logger.debug(f"LLM classifier prompt: {prompt}")
                        response = LLMFactory.generate_with_config(llm_config, prompt)
                    else:
                        # Use BaseLLMClient instance directly
                        logger.debug(
                            f"LLM classifier using client: {type(llm_config).__name__}"
                        )
                        logger.debug(f"LLM classifier prompt: {prompt}")
                        response = llm_config.generate(prompt)

                    # Parse the response to get the selected node name
                    selected_node_name = response.output.strip()

                    # Clean up JSON formatting if present
                    if selected_node_name.startswith("```json"):
                        selected_node_name = selected_node_name[7:]
                    if selected_node_name.endswith("```"):
                        selected_node_name = selected_node_name[:-3]
                    selected_node_name = selected_node_name.strip()

                    # Try to parse as JSON object first

                    try:
                        parsed_json = json.loads(selected_node_name)
                        if isinstance(parsed_json, dict) and "intent" in parsed_json:
                            selected_node_name = parsed_json["intent"]
                        elif isinstance(parsed_json, str):
                            selected_node_name = parsed_json
                    except json.JSONDecodeError:
                        # Not valid JSON, treat as plain string
                        pass

                    # Remove quotes if present
                    if selected_node_name.startswith(
                        '"'
                    ) and selected_node_name.endswith('"'):
                        selected_node_name = selected_node_name[1:-1]
                    elif selected_node_name.startswith(
                        "'"
                    ) and selected_node_name.endswith("'"):
                        selected_node_name = selected_node_name[1:-1]

                    logger.debug(f"LLM raw output: {response}")
                    logger.debug(f"LLM classifier selected node: {selected_node_name}")
                    logger.debug(f"LLM classifier children: {children}")

                    # Find the child node with the matching name
                    chosen_child = None
                    for child in children:
                        logger.debug(f"LLM classifier child in for loop: {child.name}")
                        if child.name == selected_node_name:
                            logger.debug(
                                f"LLM classifier child in for loop found: {child.name}"
                            )
                            chosen_child = child
                            break

                    # If no exact match, try partial matching
                    if chosen_child is None:
                        for child in children:
                            if selected_node_name.lower() in child.name.lower():
                                logger.debug(
                                    f"LLM classifier partial match found: {child.name}"
                                )
                                chosen_child = child
                                break

                    if chosen_child is None:
                        logger.warning(
                            f"LLM classifier could not find child '{selected_node_name}'. Available children: {[c.name for c in children]}"
                        )
                        # Return first child as fallback
                        chosen_child = children[0] if children else None

                    # Return both the chosen child and LLM response info

                    return chosen_child, response

                except Exception as e:
                    logger.error(f"LLM classifier error: {e}")
                    return None, None

            classifier_func = llm_classifier
        else:
            # Rule-based classifier
            classifier_name = node_spec.get("classifier")
            if classifier_name:
                if classifier_name not in function_registry:
                    raise ValueError(
                        f"Classifier function '{classifier_name}' not found for node '{node_id}'"
                    )
                classifier_func = function_registry[classifier_name]

        if classifier_func is None:
            raise ValueError(
                f"Classifier function '{classifier_name}' not found for node '{node_id}'"
            )

        builder = ClassifierBuilder(name)
        builder.description = description
        builder.classifier_func = classifier_func

        # Optionals: allow set/list in JSON
        for k, m in [("remediation_strategies", builder.with_remediation_strategies)]:
            v = node_spec.get(k)
            if v:
                m(v)

        return builder

    @staticmethod
    def create_from_spec(
        node_id: str,
        name: str,
        description: str,
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
    ) -> TreeNode:
        """Create a classifier node from specification."""
        classifier_type = node_spec.get("classifier_type", "rule")

        if classifier_type == "llm":
            return ClassifierBuilder._create_llm_classifier_node(
                node_id, name, description, node_spec, function_registry
            )
        else:
            if "classifier_function" not in node_spec:
                raise ValueError(
                    f"Classifier node '{node_id}' must have a 'classifier_function' field"
                )

            function_name = node_spec["classifier_function"]
            if function_name not in function_registry:
                raise ValueError(
                    f"Function '{function_name}' not found in function registry"
                )

            builder = ClassifierBuilder(name)
            builder.with_classifier(function_registry[function_name])
            builder.with_description(description)

            return builder.build()

    @staticmethod
    def _create_llm_classifier_node(
        node_id: str,
        name: str,
        description: str,
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
    ) -> TreeNode:
        """Create an LLM classifier node from specification."""
        if "llm_config" not in node_spec:
            raise ValueError(
                f"LLM classifier node '{node_id}' must have an 'llm_config' field"
            )

        llm_config = node_spec["llm_config"]
        classification_prompt = node_spec.get(
            "classification_prompt",
            ClassifierBuilder._get_default_classification_prompt(),
        )

        # Create LLM classifier function directly
        def llm_classifier(
            user_input: str,
            children: List[TreeNode],
            context: Optional[Dict[str, Any]] = None,
        ) -> tuple[Optional[TreeNode], Optional[Dict[str, Any]]]:

            logger = Logger(__name__)
            logger.debug(f"LLM classifier input: {user_input}")

            if llm_config is None:
                logger.error(
                    "No llm_config provided to LLM classifier. Please set a default on the graph or provide one at the node level."
                )
                return None, None

            try:
                # Build the classification prompt with available children
                child_descriptions = []
                for child in children:
                    child_descriptions.append(f"- {child.name}: {child.description}")

                prompt = classification_prompt.format(
                    user_input=user_input,
                    node_descriptions="\n".join(child_descriptions),
                )

                # Get LLM response
                if isinstance(llm_config, dict):
                    # Obfuscate API key in debug log
                    safe_config = llm_config.copy()
                    if "api_key" in safe_config:
                        safe_config["api_key"] = "***OBFUSCATED***"
                    logger.debug(f"LLM classifier config: {safe_config}")
                    logger.debug(f"LLM classifier prompt: {prompt}")
                    response = LLMFactory.generate_with_config(llm_config, prompt)
                else:
                    # Use BaseLLMClient instance directly
                    logger.debug(
                        f"LLM classifier using client: {type(llm_config).__name__}"
                    )
                    logger.debug(f"LLM classifier prompt: {prompt}")
                    response = llm_config.generate(prompt)

                # Parse the response to get the selected node name
                selected_node_name = response.output.strip()

                # Clean up JSON formatting if present
                if selected_node_name.startswith("```json"):
                    selected_node_name = selected_node_name[7:]
                if selected_node_name.endswith("```"):
                    selected_node_name = selected_node_name[:-3]
                selected_node_name = selected_node_name.strip()

                # Try to parse as JSON object first
                import json

                try:
                    parsed_json = json.loads(selected_node_name)
                    if isinstance(parsed_json, dict) and "intent" in parsed_json:
                        selected_node_name = parsed_json["intent"]
                    elif isinstance(parsed_json, str):
                        selected_node_name = parsed_json
                except json.JSONDecodeError:
                    # Not valid JSON, treat as plain string
                    pass

                # Remove quotes if present
                if selected_node_name.startswith('"') and selected_node_name.endswith(
                    '"'
                ):
                    selected_node_name = selected_node_name[1:-1]
                elif selected_node_name.startswith("'") and selected_node_name.endswith(
                    "'"
                ):
                    selected_node_name = selected_node_name[1:-1]

                logger.debug(f"LLM raw output: {response}")
                logger.debug(f"LLM classifier selected node: {selected_node_name}")
                logger.debug(f"LLM classifier children: {children}")

                # Find the child node with the matching name
                chosen_child = None
                for child in children:
                    logger.debug(f"LLM classifier child in for loop: {child.name}")
                    if child.name == selected_node_name:
                        logger.debug(
                            f"LLM classifier child in for loop found: {child.name}"
                        )
                        chosen_child = child
                        break

                # If no exact match, try partial matching
                if chosen_child is None:
                    for child in children:
                        if selected_node_name.lower() in child.name.lower():
                            logger.debug(
                                f"LLM classifier partial match found: {child.name}"
                            )
                            chosen_child = child
                            break

                if chosen_child is None:
                    logger.warning(
                        f"LLM classifier could not find child '{selected_node_name}'. Available children: {[c.name for c in children]}"
                    )
                    # Return first child as fallback
                    chosen_child = children[0] if children else None

                return chosen_child, {"llm_response": response}

            except Exception as e:
                logger.error(f"Error in LLM classifier: {e}")
                # Return first child as fallback
                return children[0] if children else None, {"error": str(e)}

        # Use ClassifierBuilder to create the node (proper abstraction)
        builder = ClassifierBuilder(name)
        builder.with_classifier(llm_classifier)
        builder.with_description(description)

        return builder.build()

    @staticmethod
    def _get_default_classification_prompt() -> str:
        """Get the default classification prompt template."""
        return """You are an intent classifier. Given a user input, select the most appropriate intent from the available options.

User Input: {user_input}

Available Intents:
{node_descriptions}

Instructions:
- Analyze the user input carefully
- Consider the available context information when making your decision
- Select the intent that best matches the user's request
- Return only the number (1-{num_nodes}) corresponding to your choice
- If no intent matches, return 0

Your choice (number only):"""

    def with_classifier(self, classifier_func: Callable) -> "ClassifierBuilder":
        self.classifier_func = classifier_func
        return self

    def with_children(self, children: List[TreeNode]) -> "ClassifierBuilder":
        self.children = children
        return self

    def add_child(self, child: TreeNode) -> "ClassifierBuilder":
        self.children.append(child)
        return self

    def with_remediation_strategies(self, strategies: Any) -> "ClassifierBuilder":
        self.remediation_strategies = list(strategies)
        return self

    def build(self) -> ClassifierNode:
        """Build and return the ClassifierNode instance.

        Returns:
            Configured ClassifierNode instance

        Raises:
            ValueError: If required fields are missing
        """
        self._validate_required_field(
            "classifier function", self.classifier_func, "with_classifier"
        )

        # Type assertion after validation
        assert self.classifier_func is not None

        return ClassifierNode(
            name=self.name,
            description=self.description,
            classifier=self.classifier_func,
            children=self.children,
            remediation_strategies=self.remediation_strategies,
        )
