"""
Node factory utilities for creating common node types.
"""

from typing import Any, Callable, Dict, List
from intent_kit.nodes.actions.builder import ActionBuilder
from intent_kit.nodes.classifiers.builder import ClassifierBuilder
from intent_kit.nodes import TreeNode


def action(
    name: str,
    description: str,
    action_func: Callable,
    param_schema: Dict[str, Any],
) -> TreeNode:
    """Create an action node."""
    builder = ActionBuilder(name)
    builder.description = description
    builder.action_func = action_func
    builder.param_schema = param_schema
    return builder.build()


def llm_classifier(
    name: str,
    description: str,
    children: List[TreeNode],
    llm_config: Dict[str, Any],
) -> TreeNode:
    """Create an LLM classifier node."""
    # Create a node spec that the from_json method can handle
    node_spec = {
        "id": name,
        "name": name,
        "description": description,
        "type": "llm_classifier",
        "llm_config": llm_config,
    }

    # Create a dummy function registry
    function_registry: Dict[str, Callable] = {}

    builder = ClassifierBuilder.from_json(node_spec, function_registry, llm_config)
    builder.with_children(children)
    return builder.build()
