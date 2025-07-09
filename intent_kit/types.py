"""
Core types for intent-kit package.
"""

from typing import TypedDict, Optional, Dict, Any, Sequence, Union, Callable
from enum import Enum


class IntentClassification(str, Enum):
    ATOMIC = "Atomic"
    COMPOSITE = "Composite"
    AMBIGUOUS = "Ambiguous"
    INVALID = "Invalid"


class IntentAction(str, Enum):
    HANDLE = "handle"
    SPLIT = "split"
    CLARIFY = "clarify"
    REJECT = "reject"


class IntentChunkClassification(TypedDict, total=False):
    chunk_text: str
    classification: IntentClassification
    intent_type: Optional[str]
    action: IntentAction
    metadata: Dict[str, Any]


# The output of the splitter is still:
IntentChunk = Union[str, Dict[str, Any]]

# The output of the classifier is:
ClassifierOutput = IntentChunkClassification

# Single splitter function type - can accept additional kwargs like context
SplitterFunction = Callable[..., Sequence[IntentChunk]]

# Classifier function type
ClassifierFunction = Callable[[IntentChunk], ClassifierOutput]
