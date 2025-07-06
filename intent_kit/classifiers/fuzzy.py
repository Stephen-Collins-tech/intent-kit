"""
Fuzzy / typo-tolerant classifier.

This classifier chooses the child node whose *keyword* is the closest match to
``user_input`` even when the input contains minor typos.  It is deliberately
simple and dependency-free – it relies on ``difflib.SequenceMatcher`` from the
standard library so that intent-kit keeps *zero core dependencies*.

Usage parallels the other lightweight classifiers:
    from intent_kit.classifiers.fuzzy import fuzzy_classifier
    node = ClassifierNode(name="root", classifier=fuzzy_classifier, children=[...])

Each child node can expose a ``fuzzy_keywords`` attribute – a list/tuple/string
of keywords to compare against.  If absent, the child's ``name`` is used.  The
match with the highest similarity ratio above ``threshold`` (default 0.6) is
returned; if no keyword crosses the threshold, the classifier yields ``None``.
"""

from difflib import SequenceMatcher
from typing import Optional, Dict, Any, Iterable, List, Tuple
import math

from intent_kit.node import TreeNode  # type: ignore
from intent_kit.utils.logger import Logger

logger = Logger(__name__)

DEFAULT_THRESHOLD = 0.6  # similarity score 0-1


def _norm_keywords(keywords) -> List[str]:
    """Normalise the *keywords* attribute into a list of lower-cased strings."""
    if keywords is None:
        return []
    if isinstance(keywords, str):
        return [keywords.lower()]
    # Assume iterable
    return [str(k).lower() for k in keywords if isinstance(k, str)]


def _best_keyword_score(user_text: str, keywords: Iterable[str]) -> float:
    """Return best similarity score between *user_text* and iterable keywords."""
    if not user_text or not keywords:
        return 0.0
    user_lower = user_text.lower()
    return max(SequenceMatcher(None, user_lower, kw).ratio() for kw in keywords)


def fuzzy_classifier(
    user_input: str,
    children: List[TreeNode],
    context: Optional[Dict[str, Any]] = None,
    *,
    threshold: float = DEFAULT_THRESHOLD,
) -> Optional[TreeNode]:
    """Return the child whose keyword is the best fuzzy match >= *threshold*."""

    if not user_input or not user_input.strip():
        logger.debug("fuzzy_classifier received empty input; returning None")
        return None

    best_child: Optional[TreeNode] = None
    best_score = -math.inf

    for child in children:
        keywords = _norm_keywords(getattr(child, "fuzzy_keywords", None))
        if not keywords:
            # default to child name
            keywords = _norm_keywords(child.name)
        score = _best_keyword_score(user_input, keywords)
        logger.debug(f"Fuzzy score for child '{child.name}': {score:.3f}")
        if score > best_score and score >= threshold:
            best_score = score
            best_child = child

    if best_child:
        logger.debug(
            f"fuzzy_classifier selected '{best_child.name}' with score {best_score:.3f}"
        )
    else:
        logger.debug("fuzzy_classifier found no match exceeding threshold")
    return best_child