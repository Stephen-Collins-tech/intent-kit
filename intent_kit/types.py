"""
Core types for intent-kit package.
"""

from dataclasses import dataclass
from typing import TypedDict, Optional, Dict, Any, Callable, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    pass


TokenUsage = str
InputTokens = int
OutputTokens = int
TotalTokens = int
Cost = float
Provider = str
Model = str
Output = str
Duration = float  # in seconds


@dataclass
class LLMResponse:
    """Response from an LLM."""

    output: Output
    model: Model
    input_tokens: InputTokens
    output_tokens: OutputTokens
    cost: Cost
    provider: Provider
    duration: Duration

    @property
    def total_tokens(self) -> TotalTokens:
        """Total tokens used in the response."""
        return self.input_tokens + self.output_tokens


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


# The output of the classifier is:
ClassifierOutput = IntentChunkClassification

# Classifier function type
ClassifierFunction = Callable[[str], ClassifierOutput]
