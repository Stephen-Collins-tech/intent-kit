Here's a **TASKS.md** that blends the Context refactor/move plan with the merge-policy + patch protocol feedback we discussed.
It's structured with markdown checkboxes so you can drop it directly into your repo and feed it to an LLM coding assistant.

---

# Context Refactor & Relocation Tasks

## Overview

This document outlines the refactor to move the context system into `intent_kit/core/context/` with a new protocol-based architecture that supports deterministic merging, stable fingerprinting, and backwards compatibility.

---

# Answers (decisions)

1. **Implementation order**

* **Stage 0 (must first):** `protocols.py` (ContextProtocol/ContextPatch/MergePolicyName), `default.py` with **KV only** (get/set/keys/snapshot) + stubbed `apply_patch`/`fingerprint`, `__init__.py`, deprecated re-export.
* **Stage 1:** Wire traversal to type `ctx: ContextProtocol` (no behavior change), keep existing ctx usage working.
* **Stage 2:** Implement merge policies (`policies.py`) + real `apply_patch` in `DefaultContext` (LWW default).
* **Stage 3:** Implement `fingerprint` + glob include (basic `*`), exclude `tmp.*` and `private.*` by default.
* **Stage 4 (incremental):** Convert 1–2 core nodes to emit `ctx_patch`; keep direct `ctx.set` allowed.
* **Stage 5:** Tests (policies, conflicts, fingerprint, fan-in determinism, adapter).

2. **Current context usage**

* **Yes**—do a *quick* usage scan first (30–60 min scope): where `ctx.set`, `ctx.keys`, `ctx.logger`, and any `ctx.get_history`/ops/errors are used. This ensures the Stage 0 interface doesn't break anything and tells you which namespaces to reserve.

3. **Reduce policy / registry**

* **Defer.** Ship with `last_write_wins`, `first_write_wins`, `append_list`, `merge_dict`. Implement `reduce` as a **NotImplemented** path that raises a clear error with guidance ("register a reducer in v2"). Add the registry hook later.

4. **Glob patterns for fingerprint**

* **Support simple shell-style globs** in Stage 3: `*` and `?` with `fnmatch`. That covers `user.*`, `shared.*`, and `node.<id>.*`. No need for brace sets or character classes yet.
* Default `include` if `None`: `["user.*", "shared.*"]`.
* Always exclude prefixes: `tmp.*`, `private.*`.

5. **Error handling**

* **Use existing `ContextConflictError` if present;** otherwise define it in `core.exceptions` or locally as a fallback in `policies.py/default.py` (as in the skeleton). When you wire traversal, import from the shared exceptions module to keep one canonical type.

6. **Testing strategy**

* **Add the scaffold in the same PR** (light but real).

  * Unit tests for `policies.py` and `DefaultContext.apply_patch`
  * Fingerprint stability tests
  * Fan-in merge determinism test (simulate two patches, stable order)
  * Adapter hydration test
* Don't block on integration tests for nodes yet—add those when you convert the first node to patches.

---

# Execution Plan (checklist)

## Stage 0 — Protocol + Minimal DefaultContext

* [x] Add `core/context/protocols.py` (exact skeleton already provided).
* [x] Add `core/context/default.py` with KV + `snapshot` + stub `apply_patch`/`fingerprint`.
* [x] Add `core/context/__init__.py` and `adapters.py` (DictBackedContext).
* [x] ~~Add deprecation re-export `intent_kit/context/__init__.py`.~~ (Removed old context entirely - no backwards compatibility)
* [x] Quick repo scan to confirm only `get/set/keys/logger` are needed immediately.

**DoD:** Project imports resolve; traversal still runs with old behavior. ✅ **COMPLETED**

## Stage 1 — Type Traversal Against Protocol

* [x] Change traversal signature/uses to `ctx: ContextProtocol`.
* [x] Keep existing memoization and `ctx.set` calls intact (no behavior change).
* [x] CI green.

**DoD:** No runtime behavior changes; types enforce the new surface. ✅ **COMPLETED**

## Stage 2 — Merge Policies + Patch Application

* [x] Implement `policies.py`: `last_write_wins`, `first_write_wins`, `append_list`, `merge_dict`.
* [x] In `default.apply_patch`:

  * [x] Enforce `private.*` write protection.
  * [x] Per-key policy map; default to LWW.
  * [x] Deterministic loop over keys; wrap unexpected errors as `ContextConflictError`.
  * [ ] (Optional) record per-key provenance in a private metadata map for future observability.

**DoD:** Patches merge deterministically; conflicts raise `ContextConflictError`. ✅ **COMPLETED**

## Stage 3 — Fingerprint

* [x] Implement `_select_keys_for_fingerprint` with `fnmatch` globs.
* [x] Default includes: `["user.*", "shared.*"]`.
* [x] Exclude `tmp.*`, `private.*`.
* [x] `canonical_fingerprint` returns canonical JSON; leave hashing for later.
* [x] **BONUS:** Implemented glob pattern matching with `fnmatch` for flexible key selection.

**DoD:** Fingerprint stable across key order; unaffected by `tmp.*`/`private.*`. ✅ **COMPLETED**

## Stage 4 — Node Pilot to Patches

* [x] Update `classifier` and `extractor` to return `ctx_patch` (keep existing direct `set` as fallback).
* [x] In traversal: if `result.ctx_patch`, set `provenance` if missing, then `ctx.apply_patch`.

**DoD:** Mixed mode works; patches preferred. ✅ **COMPLETED**

## Stage 5 — Tests

* [x] `tests/context/test_policies.py`
    * [x] LWW/FWW basic
    * [x] append_list (list vs non-list)
    * [x] merge_dict (dict vs non-dict → conflict)
* [x] `tests/context/test_default_context.py`
    * [x] apply_patch write protect `private.*`
    * [x] per-key policy overrides
    * [x] deterministic application order
* [x] `tests/context/test_fingerprint.py`
    * [x] glob include works (`user.*`, `shared.*`)
    * [x] `tmp.*` changes don't affect fingerprint
* [x] `tests/context/test_adapters.py`
    * [x] DictBackedContext hydrates existing mapping

**DoD:** All tests pass locally and in CI; coverage for policies + fingerprint. ✅ **COMPLETED**

---

# Non-goals (explicit)

* No reducer registry in this PR (raise with helpful message).
* No deep-merge semantics for nested dicts (shallow `merge_dict` only).
* No strict enforcement of ContextDependencies yet (warning-level only later).

---

# Acceptance Criteria (engineer-facing)

* ✅ `intent_kit.core.context` is the **only** import path used by traversal and nodes.
* ✅ Traversal compiles against `ContextProtocol` and applies patches if present.
* ✅ Fan-in merges are deterministic and policy-driven; unreconcilable merges raise `ContextConflictError`.
* ✅ Fingerprint is stable and excludes ephemeral/private keys.
* ~~Back-compat re-export exists and warns.~~ (Removed - no backwards compatibility)

---

# Ready-to-Drop-In File Skeletons

Here are **ready-to-drop-in file skeletons** for `core/context/` (plus the deprecation shim). They compile, have clear TODOs, and keep imports clean so your LLM assistant can fill in logic without guessing.

---

# 📁 Proposed File Tree

```
intent_kit/
  core/
    context/
      __init__.py
      protocols.py
      default.py
      policies.py
      fingerprint.py
      adapters.py
  context/
    __init__.py  # (deprecated re-export)
```

---

# intent\_kit/core/context/**init**.py

```python
"""
Core Context public API.

Re-export the protocol, default implementation, and key types from submodules.
"""

from .protocols import (
    ContextProtocol,
    ContextPatch,
    MergePolicyName,
    LoggerLike,
)

from .default import DefaultContext
from .adapters import DictBackedContext

__all__ = [
    "ContextProtocol",
    "ContextPatch",
    "MergePolicyName",
    "LoggerLike",
    "DefaultContext",
    "DictBackedContext",
]
```

---

# intent\_kit/core/context/protocols.py

```python
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
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...


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
    def add_error(self, *, where: str, err: str, meta: Optional[Mapping[str, Any]] = None) -> None: ...
    def track_operation(self, *, name: str, status: str, meta: Optional[Mapping[str, Any]] = None) -> None: ...
```

---

# intent\_kit/core/context/default.py

```python
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, Mapping, Optional

from .protocols import ContextProtocol, ContextPatch, MergePolicyName, LoggerLike
from .fingerprint import canonical_fingerprint  # TODO: implement in fingerprint.py
from .policies import apply_merge  # TODO: implement in policies.py

# Try to use the shared exceptions if present.
try:
    from intent_kit.core.exceptions import ContextConflictError
except Exception:  # pragma: no cover
    class ContextConflictError(RuntimeError):
        """Fallback if shared exception isn't available during early refactor."""


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
        self._logger: LoggerLike = logger or logging.getLogger("intent_kit")

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

        TODO:
          - Respect per-key policies (patch.get("policy", {}))
          - Default policy: last_write_wins
          - Disallow writes to "private.*"
          - Raise ContextConflictError on irreconcilable merges
          - Track provenance on write
        """
        data = patch.get("data", {})
        policies = patch.get("policy", {})
        provenance = patch.get("provenance", "unknown")

        for key, incoming in data.items():
            if key.startswith("private."):
                raise ContextConflictError(f"Write to protected namespace: {key}")

            policy: MergePolicyName = policies.get(key, "last_write_wins")
            existing = self._data.get(key, None)

            try:
                merged = apply_merge(policy=policy, existing=existing, incoming=incoming, key=key)
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

        TODO:
          - Expand glob patterns in `include` (e.g., "user.*", "shared.*")
          - Exclude DEFAULT_EXCLUDED_FP_PREFIXES by default
          - Canonicalize via `canonical_fingerprint`
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

    def add_error(self, *, where: str, err: str, meta: Optional[Mapping[str, Any]] = None) -> None:
        # TODO: integrate with error tracking (StackContext/Langfuse/etc.)
        self._logger.error("CTX error at %s: %s | meta=%s", where, err, meta)

    def track_operation(self, *, name: str, status: str, meta: Optional[Mapping[str, Any]] = None) -> None:
        # TODO: integrate with operation tracking
        self._logger.debug("CTX op %s status=%s meta=%s", name, status, meta)


def _select_keys_for_fingerprint(
    data: Mapping[str, Any],
    include: Optional[Iterable[str]],
    exclude_prefixes: Iterable[str],
) -> Dict[str, Any]:
    """
    Build a dict of keys → values to feed into the fingerprint.

    TODO:
      - Implement glob expansion for `include`
      - If include is None, use a conservative default (e.g., only 'user.*' & 'shared.*')
    """
    if include:
        # TODO: glob match keys against patterns in include
        # Placeholder: naive exact match
        keys = sorted({k for k in data.keys() if k in include})
    else:
        # Default conservative subset
        keys = sorted([k for k in data.keys() if k.startswith(("user.", "shared."))])

    # Exclude protected/ephemeral prefixes
    filtered = [k for k in keys if not k.startswith(tuple(exclude_prefixes))]
    return {k: data[k] for k in filtered}
```

---

# intent\_kit/core/context/policies.py

```python
from __future__ import annotations
from typing import Any

# Try to use the shared exceptions if present.
try:
    from intent_kit.core.exceptions import ContextConflictError
except Exception:  # pragma: no cover
    class ContextConflictError(RuntimeError):
        """Fallback if shared exception isn't available during early refactor."""


def apply_merge(*, policy: str, existing: Any, incoming: Any, key: str) -> Any:
    """
    Route to a concrete merge policy implementation.

    Supported (initial set):
      - last_write_wins (default)
      - first_write_wins
      - append_list
      - merge_dict (shallow)
      - reduce (requires registered reducer)
    """
    if policy == "last_write_wins":
        return _last_write_wins(existing, incoming)
    if policy == "first_write_wins":
        return _first_write_wins(existing, incoming)
    if policy == "append_list":
        return _append_list(existing, incoming, key)
    if policy == "merge_dict":
        return _merge_dict(existing, incoming, key)
    if policy == "reduce":
        # TODO: wire a reducer registry; for now fail explicitly
        raise ContextConflictError(f"Reducer not registered for key: {key}")

    raise ContextConflictError(f"Unknown merge policy: {policy}")


def _last_write_wins(existing: Any, incoming: Any) -> Any:
    return incoming


def _first_write_wins(existing: Any, incoming: Any) -> Any:
    return existing if existing is not None else incoming


def _append_list(existing: Any, incoming: Any, key: str) -> Any:
    if existing is None:
        existing = []
    if not isinstance(existing, list):
        raise ContextConflictError(f"append_list expects list at {key}; got {type(existing).__name__}")
    return [*existing, incoming] if not isinstance(incoming, list) else [*existing, *incoming]


def _merge_dict(existing: Any, incoming: Any, key: str) -> Any:
    if existing is None:
        existing = {}
    if not isinstance(existing, dict) or not isinstance(incoming, dict):
        raise ContextConflictError(f"merge_dict expects dicts at {key}")
    out = dict(existing)
    out.update(incoming)
    return out
```

---

# intent\_kit/core/context/fingerprint.py

```python
from __future__ import annotations
import json
from typing import Any, Mapping


def canonical_fingerprint(selected: Mapping[str, Any]) -> str:
    """
    Produce a deterministic fingerprint string from selected key/values.

    TODO:
      - Consider stable float formatting if needed
      - Consider hashing (e.g., blake2b) over the JSON string if shorter keys are desired
    """
    # Canonical JSON: sort keys, no whitespace churn
    return json.dumps(selected, sort_keys=True, separators=(",", ":"))
```

---

# intent\_kit/core/context/adapters.py

```python
from __future__ import annotations

import logging
from typing import Any, Mapping, Optional

from .default import DefaultContext
from .protocols import LoggerLike


class DictBackedContext(DefaultContext):
    """
    Adapter that hydrates from an existing dict-like context once,
    then behaves like DefaultContext.

    This is intended as a back-compat shim during migration.
    """

    def __init__(self, backing: Mapping[str, Any], *, logger: Optional[LoggerLike] = None) -> None:
        super().__init__(logger=logger or logging.getLogger("intent_kit"))
        # Single hydration step
        for k, v in backing.items():
            if isinstance(k, str):
                self._data[k] = v
```

---

# intent\_kit/context/**init**.py (Deprecated Re-Export)

```python
"""
DEPRECATED: intent_kit.context

Use: `from intent_kit.core.context import ...`

This module re-exports the core.context API for a transition period.
"""

from warnings import warn

warn(
    "intent_kit.context is deprecated; use intent_kit.core.context",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from the new location
from intent_kit.core.context import (
    ContextProtocol,
    ContextPatch,
    MergePolicyName,
    LoggerLike,
    DefaultContext,
    DictBackedContext,
)

__all__ = [
    "ContextProtocol",
    "ContextPatch",
    "MergePolicyName",
    "LoggerLike",
    "DefaultContext",
    "DictBackedContext",
]
```

---

## Notes for your LLM Coding Assistant

* **Open TODOs:**

  * Implement glob expansion + exclusions in `_select_keys_for_fingerprint` (default.py).
  * Flesh out `canonical_fingerprint` if you want a hashed output.
  * Add a reducer registry for `reduce` in `policies.py` when needed.
  * Optional provenance/meta tracking on writes in `DefaultContext.apply_patch`.

* **Strict Mode (optional next PR):**

  * Block writes outside node-declared `ContextDependencies.outputs`.
  * Record per-key provenance to aid audit trails.

* **Traversal touch points (separate PR):**

  * Type `ctx: ContextProtocol`.
  * Use `ctx.apply_patch(result.ctx_patch)` if present.
  * Swap memoization to `ctx.fingerprint(include=dag.stable_context_keys)`.

If you want, I can also generate a tiny **unit test scaffold** (pytest) for merge policies and fingerprint stability to go with this.
