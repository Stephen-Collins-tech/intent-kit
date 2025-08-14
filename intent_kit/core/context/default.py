from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional
from time import perf_counter

from intent_kit.core.context.protocols import (
    ContextProtocol,
    ContextPatch,
    MergePolicyName,
    LoggerLike,
)
from intent_kit.core.context.fingerprint import canonical_fingerprint
from intent_kit.core.context.policies import apply_merge
from intent_kit.core.exceptions import ContextConflictError
from intent_kit.utils.logger import Logger


DEFAULT_EXCLUDED_FP_PREFIXES = ("tmp.", "private.")


class DefaultContext(ContextProtocol):
    """
    Reference dotted-key context with deterministic merge + memoization.

    Storage model:
      - _data: Dict[str, Any] with dotted keys
      - _logger: LoggerLike
    """

    def __init__(self, *, logger: Optional[LoggerLike] = None) -> None:
        self._data: Dict[str, Any] = {}
        self._logger: LoggerLike = logger or Logger("intent_kit.context")

    # ---------- Core KV ----------
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any, modified_by: Optional[str] = None) -> None:
        # TODO: optionally record provenance/modified_by
        self._data[key] = value

    def has(self, key: str) -> bool:
        return key in self._data

    def keys(self) -> Iterable[str]:
        # Returning a stable view helps reproducibility
        return sorted(self._data.keys())

    # ---------- Patching & snapshots ----------
    def snapshot(self) -> Mapping[str, Any]:
        # Shallow copy is enough for deterministic reads/merges
        return dict(self._data)

    def apply_patch(self, patch: ContextPatch) -> None:
        """
        Deterministically apply a patch according to per-key or default policy.

        Features:
          - Respect per-key policies (patch.get("policy", {}))
          - Default policy: last_write_wins
          - Disallow writes to "private.*"
          - Raise ContextConflictError on irreconcilable merges
          - Track provenance on write (optional)
        """
        data = patch.get("data", {})
        policies = patch.get("policy", {})
        # TODO: use provenance for tracking
        _ = patch.get("provenance", "unknown")

        for key, incoming in data.items():
            if key.startswith("private."):
                raise ContextConflictError(f"Write to protected namespace: {key}")

            policy: MergePolicyName = policies.get(key, "last_write_wins")
            existing = self._data.get(key, None)

            try:
                merged = apply_merge(
                    policy=policy, existing=existing, incoming=incoming, key=key
                )
            except ContextConflictError:
                raise
            except Exception as e:  # wrap unexpected policy errors
                raise ContextConflictError(f"Merge failed for {key}: {e}") from e

            self._data[key] = merged
            # TODO: optionally track provenance per key, e.g., self._meta[key] = provenance

        # TODO: handle patch.tags (e.g., mark keys affecting memoization)

    def merge_from(self, other: Mapping[str, Any]) -> None:
        """
        Merge values from another mapping using last_write_wins semantics.

        NOTE: This is a coarse merge; use apply_patch for policy-aware merging.
        """
        for k, v in other.items():
            if k.startswith("private."):
                continue
            self._data[k] = v

    # ---------- Fingerprint ----------
    def fingerprint(self, include: Optional[Iterable[str]] = None) -> str:
        """
        Return a stable, canonical fingerprint string for memoization.

        Supports glob patterns in `include` (e.g., "user.*", "shared.*").
        Excludes DEFAULT_EXCLUDED_FP_PREFIXES by default.
        Uses canonical_fingerprint for deterministic output.
        """
        selected = _select_keys_for_fingerprint(
            data=self._data,
            include=include,
            exclude_prefixes=DEFAULT_EXCLUDED_FP_PREFIXES,
        )
        return canonical_fingerprint(selected)

    # ---------- Telemetry ----------
    @property
    def logger(self) -> LoggerLike:
        return self._logger

    def add_error(
        self, *, where: str, err: str, meta: Optional[Mapping[str, Any]] = None
    ) -> None:
        """Add an error to the context with structured logging.

        Args:
            where: Location/context where the error occurred
            err: Error message
            meta: Additional metadata about the error
        """
        # TODO: integrate with error tracking (StackContext/Langfuse/etc.)
        error_data = {
            "where": where,
            "error": err,
            "timestamp": perf_counter(),
            "meta": meta or {},
        }

        # Store error in context for potential recovery/debugging
        self._data[f"errors.{where}"] = error_data

        # Simple error log without verbose metadata
        self._logger.error(f"CTX error at {where}: {err}")

    def track_operation(
        self, *, name: str, status: str, meta: Optional[Mapping[str, Any]] = None
    ) -> None:
        """Track an operation with structured logging.

        Args:
            name: Name of the operation
            status: Status of the operation (started, completed, failed, etc.)
            meta: Additional metadata about the operation
        """
        # TODO: integrate with operation tracking
        operation_data = {
            "name": name,
            "status": status,
            "timestamp": perf_counter(),
            "meta": meta or {},
        }

        # Store operation in context for potential analysis
        operation_key = f"operations.{name}.{status}"
        self._data[operation_key] = operation_data

        # Simple operation log without verbose metadata
        if status == "started":
            self._logger.debug(f"CTX op {name} started")
        elif status == "completed":
            self._logger.info(f"CTX op {name} completed")
        else:
            self._logger.debug(f"CTX op {name} {status}")


def _select_keys_for_fingerprint(
    data: Mapping[str, Any],
    include: Optional[Iterable[str]],
    exclude_prefixes: Iterable[str],
) -> Dict[str, Any]:
    """
    Build a dict of keys → values to feed into the fingerprint.

    Supports glob patterns in `include` (e.g., "user.*", "shared.*").
    If include is None, uses conservative default (only 'user.*' & 'shared.*').
    """
    import fnmatch

    if include:
        # Use glob matching for include patterns
        keys_set = set()
        for pattern in include:
            keys_set.update(fnmatch.filter(data.keys(), pattern))
        keys = sorted(keys_set)
    else:
        # Default conservative subset
        keys = sorted([k for k in data.keys() if k.startswith(("user.", "shared."))])

    # Exclude protected/ephemeral prefixes
    filtered = [k for k in keys if not k.startswith(tuple(exclude_prefixes))]
    return {k: data[k] for k in filtered}
