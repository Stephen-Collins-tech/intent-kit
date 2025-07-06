"""
Regex-based classifier module.

This module provides a simple classifier function, `regex_classifier`, that
selects the first child node whose associated regular-expression pattern matches
(the first match wins).  Patterns can be attached to each child node via a
`regex_patterns` attribute (either a single pattern string or an iterable of
patterns).  If a child has no explicit patterns, the classifier falls back to a
case-insensitive search for the child's ``name``.

The function complies with the signature expected by ``ClassifierNode``:
    (user_input: str, children: list[TreeNode], context: Optional[dict]) -> Optional[TreeNode]

This keeps it interchangeable with existing keyword and LLM classifiers.
"""

import re
from typing import Optional, Dict, Any, Iterable, List
from intent_kit.node import TreeNode  # type: ignore  (import time resolution)
from intent_kit.utils.logger import Logger

logger = Logger(__name__)


def _get_patterns_for_child(child: TreeNode) -> List[str]:
    """Return a list of regex patterns to test for *child*.

    If the node exposes a ``regex_patterns`` attribute (either a ``str`` or an
    iterable of strings), that value is used; otherwise the child's ``name`` is
    escaped and used as a literal match.  ``None`` patterns are ignored.
    """
    patterns_attr = getattr(child, "regex_patterns", None)

    if patterns_attr is None:
        # No explicit patterns – default to literal escape of the child's name.
        if child.name:
            return [re.escape(str(child.name))]
        return []

    # Normalise – accept str or Iterable[str]
    if isinstance(patterns_attr, str):
        return [patterns_attr]

    # Filter any non-string entries defensively
    return [p for p in patterns_attr if isinstance(p, str)]


def regex_classifier(
    user_input: str,
    children: list[TreeNode],
    context: Optional[Dict[str, Any]] = None,
) -> Optional[TreeNode]:
    """Select the first child whose regex pattern matches *user_input*.

    The search is performed in the order the children are provided.  Matching is
    case-insensitive and uses ``re.search``.
    """

    if not user_input or not user_input.strip():
        logger.debug("regex_classifier given empty user_input; returning None")
        return None

    for child in children:
        patterns = _get_patterns_for_child(child)
        for pattern in patterns:
            try:
                if re.search(pattern, user_input, flags=re.IGNORECASE):
                    logger.debug(
                        f"regex_classifier matched pattern '{pattern}' for child '{child.name}'"
                    )
                    return child
            except re.error as exc:
                logger.warning(
                    f"Invalid regex pattern '{pattern}' on child '{child.name}': {exc}"
                )
                continue  # skip invalid pattern and keep evaluating

    logger.debug("regex_classifier found no match")
    return None