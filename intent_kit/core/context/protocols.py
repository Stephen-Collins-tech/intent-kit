from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional, Protocol, TypedDict, Literal


MergePolicyName = Literal[
    "last_write_wins",
    "first_write_wins",
    "append_list",
    "merge_dict",
    "reduce",
]


class ContextPatch(TypedDict, total=False):
    """
    Patch contract applied by traversal after node execution.

    data:      dotted-key map of values to set/merge
    policy:    per-key merge policies (optional; default policy applies otherwise)
    provenance: node id or source identifier for auditability
    tags:      optional set of tags (e.g., {"affects_memo"})
    """

    data: Mapping[str, Any]
    policy: Mapping[str, MergePolicyName]
    provenance: str
    tags: set[str]


class LoggerLike(Protocol):
    """Protocol for logger interface compatible with intent_kit.utils.logger.Logger."""

    def info(self, message: str) -> None: ...
    def warning(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...
    def debug(self, message: str, colorize_message: bool = True) -> None: ...
    def critical(self, message: str) -> None: ...
    def trace(self, message: str) -> None: ...


class ContextProtocol(Protocol):
    """
    Minimal, enforceable context surface used by traversal and nodes.

    Implementations should:
    - store values using dotted keys (recommended),
    - support deterministic merging (apply_patch),
    - provide stable memoization (fingerprint).
    """

    # Core KV
    def get(self, key: str, default: Any = None) -> Any: ...
    def set(self, key: str, value: Any, modified_by: Optional[str] = None) -> None: ...

    def has(self, key: str) -> bool: ...
    def keys(self) -> Iterable[str]: ...

    # Patching & snapshots
    def snapshot(self) -> Mapping[str, Any]: ...
    def apply_patch(self, patch: ContextPatch) -> None: ...
    def merge_from(self, other: Mapping[str, Any]) -> None: ...

    # Deterministic fingerprint for memoization
    def fingerprint(self, include: Optional[Iterable[str]] = None) -> str: ...

    # Telemetry (optional but expected)
    @property
    def logger(self) -> LoggerLike: ...

    # Hooks (no-op allowed)
    def add_error(
        self, *, where: str, err: str, meta: Optional[Mapping[str, Any]] = None
    ) -> None: ...

    def track_operation(
        self, *, name: str, status: str, meta: Optional[Mapping[str, Any]] = None
    ) -> None: ...
