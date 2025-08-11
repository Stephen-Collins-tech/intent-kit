"""
Classifier node implementation.

This module provides the ClassifierNode class which is an intermediate node
that uses a classifier to select child nodes.
"""

import json
import re
from typing import Any, Callable, List, Optional, Dict
from ..base_node import TreeNode
from ..enums import NodeType
from ..types import ExecutionResult, ExecutionError
from intent_kit.context import Context


class ClassifierNode(TreeNode):
    """Intermediate node that uses a classifier to select child nodes."""

    def __init__(
        self,
        name: Optional[str],
        children: List["TreeNode"],
        description: str = "",
        parent: Optional["TreeNode"] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        custom_prompt: Optional[str] = None,
        prompt_template: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            description=description,
            children=children,
            parent=parent,
            llm_config=llm_config,
        )
        self._llm_config = llm_config or {}

        # Prompt configuration
        self.custom_prompt = custom_prompt
        self.prompt_template = prompt_template or self._get_default_prompt_template()

    def _get_default_prompt_template(self) -> str:
        """Get the default classification prompt template."""
        return """You are an intent classifier. Given a user input, select the most appropriate intent from the available options.

User Input: {user_input}

Available Intents:
{node_descriptions}

{context_info}

Instructions:
- Analyze the user input carefully for keywords and intent
- Look for mathematical terms (calculate, times, plus, minus, multiply, divide, etc.) → choose calculation intent
- Look for greeting terms (hello, hi, greet, etc.) → choose greeting intent
- Look for weather terms (weather, temperature, forecast, etc.) → choose weather intent
- Consider the available context information when making your decision
- Select the intent that best matches the user's request
- Return a JSON object with a "choice" field containing the number (1-{num_nodes}) corresponding to your choice
- If no intent matches, use choice: 0

Return only the JSON object: {{"choice": <number>}}"""

    def _build_prompt(self, user_input: str, context: Optional[Context] = None) -> str:
        """Build the classification prompt."""
        # Build node descriptions
        node_descriptions = []
        for i, child in enumerate(self.children, 1):
            desc = f"{i}. {child.name}"
            if child.description:
                desc += f": {child.description}"
            node_descriptions.append(desc)

        # Build context info
        context_info = ""
        if context:
            self.logger.debug_structured(
                {
                    "context": context,
                },
                "Context Information BEFORE export",
            )
            context_dict = context.export_to_dict()
            self.logger.debug_structured(
                {
                    "context_dict": context_dict,
                },
                "Context Information AFTER export",
            )
            if context_dict:
                context_info = "\n\nAvailable Context Information:\n"
                for key, value in context_dict.items():
                    context_info += f"- {key}: {value}\n"
                context_info += (
                    "\nUse this context information to help with classification."
                )

        return self.prompt_template.format(
            user_input=user_input,
            node_descriptions="\n".join(node_descriptions),
            context_info=context_info,
            num_nodes=len(self.children),
        )

    def _parse_response(self, response: Any) -> Dict[str, int]:
        """Parse the classification response to extract the choice."""
        try:
            # Clean up the response
            self.logger.debug_structured(
                {
                    "response": response,
                    "response_type": type(response).__name__,
                },
                "Classification Response _parse_response",
            )

            if isinstance(response, dict):
                # Check if response has raw_content field (LLM client wrapper)
                if "raw_content" in response:
                    raw_content = response["raw_content"]
                    if isinstance(raw_content, dict) and "choice" in raw_content:
                        return raw_content
                    elif isinstance(raw_content, str):
                        return self._extract_choice_from_text(raw_content)

                # Direct dict response
                if "choice" in response:
                    return response

                # Fallback: try to extract choice from any nested structure
                return self._extract_choice_from_dict(response)

            elif isinstance(response, str):
                # Try to extract JSON from the response
                return self._extract_choice_from_text(response)
            else:
                self.logger.warning(f"Unexpected response type: {type(response)}")
                return {"choice": 0}

        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return {"choice": 0}

    def _extract_choice_from_text(self, text: str) -> Dict[str, int]:
        """Extract choice from text using regex patterns."""
        # Try to find JSON object
        json_match = re.search(r"\{[^{}]*\}", text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Fallback to regex extraction
        # Pattern for "choice": number or choice: number
        pattern = r'["\']?choice["\']?\s*:\s*(\d+)'
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            try:
                choice = int(match.group(1))
                return {"choice": choice}
            except ValueError:
                pass

        # If no choice found, default to 0
        return {"choice": 0}

    def _extract_choice_from_dict(self, data: Any) -> Dict[str, int]:
        """Recursively extract choice from nested dictionary structures."""
        if isinstance(data, dict):
            # Check if this dict has a choice field
            if "choice" in data:
                try:
                    choice = int(data["choice"])
                    return {"choice": choice}
                except (ValueError, TypeError):
                    pass

            # Recursively search nested structures
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    result = self._extract_choice_from_dict(value)
                    if result and result.get("choice") is not None:
                        return result

        elif isinstance(data, list):
            # Search through list items
            for item in data:
                result = self._extract_choice_from_dict(item)
                if result and result.get("choice") is not None:
                    return result

        # No choice found
        return {"choice": 0}

    def _validate_and_cast_data(self, parsed_data: Any) -> Optional["TreeNode"]:
        """Validate and cast the parsed data to select a child node."""
        try:
            if not isinstance(parsed_data, dict):
                return None

            choice = parsed_data.get("choice")
            if choice is None:
                return None

            # Validate choice is an integer
            try:
                choice = int(choice)
            except (ValueError, TypeError):
                return None

            # Check if choice is valid
            if choice == 0:
                return None  # No choice
            elif 1 <= choice <= len(self.children):
                return self.children[choice - 1]
            else:
                self.logger.warning(
                    f"Invalid choice {choice}, expected 0-{len(self.children)}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error validating choice: {e}")
            return None

    def _execute_classification_with_llm(
        self, user_input: str, context: Optional[Context] = None
    ) -> ExecutionResult:
        """Execute the classification using LLM."""
        try:
            # Build prompt
            prompt = self.custom_prompt or self._build_prompt(user_input, context)

            # Generate response using LLM
            if self.llm_client:
                # Get model from config or use default
                model = self._llm_config.get("model", "default")
                llm_response = self.llm_client.generate(
                    prompt, model=model, expected_type=dict
                )

                # Parse the response
                parsed_data = self._parse_response(llm_response.output)

                # Validate and get chosen child
                chosen_child = self._validate_and_cast_data(parsed_data)

                # Build result
                result = ExecutionResult(
                    success=True,
                    node_name=self.name,
                    node_path=[self.name],
                    node_type=NodeType.CLASSIFIER,
                    input=user_input,
                    output=None,
                    input_tokens=llm_response.input_tokens,
                    output_tokens=llm_response.output_tokens,
                    cost=llm_response.cost,
                    provider=llm_response.provider,
                    model=llm_response.model,
                    params={
                        "chosen_child": chosen_child.name if chosen_child else None
                    },
                    children_results=[],
                    duration=llm_response.duration,
                )

                # If we have a chosen child, execute it
                if chosen_child:
                    child_result = chosen_child.execute(user_input, context)
                    result.children_results.append(child_result)
                    result.output = child_result.output
                    # Aggregate metrics
                    result.input_tokens = (result.input_tokens or 0) + (
                        child_result.input_tokens or 0
                    )
                    result.output_tokens = (result.output_tokens or 0) + (
                        child_result.output_tokens or 0
                    )
                    result.cost = (result.cost or 0.0) + (child_result.cost or 0.0)
                    result.duration = (result.duration or 0.0) + (
                        child_result.duration or 0.0
                    )

                return result
            else:
                raise ValueError("No LLM client available for classification")

        except Exception as e:
            self.logger.error(f"Classification execution failed: {e}")
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=[self.name],
                node_type=NodeType.CLASSIFIER,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type="ClassificationError",
                    message=f"Classification execution failed: {e}",
                    node_name=self.name,
                    node_path=[self.name],
                    original_exception=e,
                ),
                children_results=[],
            )

    def _update_executor_children(self):
        """Update children in the classification executor."""
        # This method is no longer needed since we removed the executor
        pass

    def __setattr__(self, name: str, value: Any) -> None:
        """Override to update executor children when children are set."""
        super().__setattr__(name, value)
        if name == "children":
            self._update_executor_children()

    @property
    def node_type(self) -> NodeType:
        """Get the node type."""
        return NodeType.CLASSIFIER

    def execute(
        self, user_input: str, context: Optional[Context] = None
    ) -> ExecutionResult:
        """Execute the classifier node."""
        try:
            # Log structured diagnostic info for classifier execution
            self.logger.debug_structured(
                {
                    "node_name": self.name,
                    "node_path": self.get_path(),
                    "input": user_input,
                    "num_children": len(self.children),
                    "has_llm_client": self.llm_client is not None,
                },
                "Classifier Execution START",
            )

            # Execute classification using LLM
            result = self._execute_classification_with_llm(user_input, context)

            # Check if no child was chosen and we have remediation strategies
            if (
                result.success
                and result.params
                and result.params.get("chosen_child") is None
            ):
                raise ExecutionError(
                    error_type="ClassificationError",
                    message="No child was chosen",
                    node_name=self.name,
                    node_path=self.get_path(),
                    original_exception=None,
                )

                # Log the result
            if result.success:
                self.logger.debug_structured(
                    {
                        "node_name": self.name,
                        "node_path": self.get_path(),
                        "classification_success": True,
                        "chosen_child": (
                            result.params.get("chosen_child") if result.params else None
                        ),
                        "cost": result.cost,
                        "tokens": {
                            "input": result.input_tokens,
                            "output": result.output_tokens,
                        },
                    },
                    "Classifier Complete",
                )
            else:
                self.logger.error(f"Classification failed: {result.error}")

            return result

        except Exception as e:
            self.logger.error(f"Unexpected error in classifier execution: {str(e)}")
            return ExecutionResult(
                success=False,
                node_name=self.name,
                node_path=self.get_path(),
                node_type=NodeType.CLASSIFIER,
                input=user_input,
                output=None,
                error=ExecutionError(
                    error_type=type(e).__name__,
                    message=str(e),
                    node_name=self.name,
                    node_path=self.get_path(),
                    original_exception=e,
                ),
                children_results=[],
            )

    @staticmethod
    def from_json(
        node_spec: Dict[str, Any],
        function_registry: Dict[str, Callable],
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> "ClassifierNode":
        """
        Create a ClassifierNode from JSON spec.
        Supports LLM-based classification with custom prompts.
        """
        # Extract common node information (same logic as base class)
        node_id = node_spec.get("id") or node_spec.get("name")
        if not node_id:
            raise ValueError(f"Node spec must have 'id' or 'name': {node_spec}")

        name = node_spec.get("name", node_id)
        description = node_spec.get("description", "")
        node_llm_config = node_spec.get("llm_config", {})

        # Merge LLM configs
        if llm_config:
            node_llm_config = {**llm_config, **node_llm_config}

        # Get custom prompt from node spec
        custom_prompt = node_spec.get("custom_prompt")
        prompt_template = node_spec.get("prompt_template")

        # Create the node directly
        node = ClassifierNode(
            name=name,
            description=description,
            children=node_spec.get("children", []),
            llm_config=node_llm_config,
            custom_prompt=custom_prompt,
            prompt_template=prompt_template,
        )

        return node
