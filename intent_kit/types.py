"""
Core type definitions for intent-kit package.
"""

from typing import TypeVar, Union
from enum import Enum
from typing import TypedDict, Optional, Dict, Any, Callable

# Type aliases for basic types
TokenUsage = str
InputTokens = int
OutputTokens = int
TotalTokens = int
Cost = float
Provider = str
Model = str
Output = str
Duration = float  # in seconds

# Type variable for structured output

T = TypeVar("T")

# Structured output type - can be any structured data
StructuredOutput = Union[Dict[str, Any], list, Any]

# Type-safe output that can be either structured or string
TypedOutput = Union[StructuredOutput, str]


class TypedOutputType(str, Enum):
    """Types of output that can be cast."""

    JSON = "json"
    YAML = "yaml"
    STRING = "string"
    DICT = "dict"
    LIST = "list"
    CLASSIFIER = "classifier"  # Cast to ClassifierOutput type
    AUTO = "auto"  # Automatically detect type


class IntentClassification(str, Enum):
    """Classification types for intent chunks."""

    ATOMIC = "Atomic"
    COMPOSITE = "Composite"
    AMBIGUOUS = "Ambiguous"
    INVALID = "Invalid"


class IntentAction(str, Enum):
    """Actions that can be taken on intent chunks."""

    HANDLE = "handle"
    SPLIT = "split"
    CLARIFY = "clarify"
    REJECT = "reject"


class IntentChunkClassification(TypedDict, total=False):
    """Classification result for an intent chunk."""

    chunk_text: str
    classification: IntentClassification
    intent_type: Optional[str]
    action: IntentAction
    metadata: Dict[str, Any]


# The output of the classifier is:
ClassifierOutput = IntentChunkClassification

# Classifier function type
ClassifierFunction = Callable[[str], ClassifierOutput]
