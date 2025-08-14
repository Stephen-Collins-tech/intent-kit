"""
Core Context public API.

Re-export the protocol, default implementation, and key types from submodules.
"""

from intent_kit.core.context.protocols import (
    ContextProtocol,
    ContextPatch,
    MergePolicyName,
    LoggerLike,
)

from intent_kit.core.context.default import DefaultContext
from intent_kit.core.context.adapters import DictBackedContext

__all__ = [
    "ContextProtocol",
    "ContextPatch",
    "MergePolicyName",
    "LoggerLike",
    "DefaultContext",
    "DictBackedContext",
]
