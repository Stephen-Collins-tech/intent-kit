from __future__ import annotations
from typing import Any

from intent_kit.core.exceptions import ContextConflictError


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
        raise ContextConflictError(
            f"append_list expects list at {key}; got {type(existing).__name__}"
        )
    if not isinstance(incoming, list):
        raise ContextConflictError(
            f"append_list expects list for incoming value at {key}; got {type(incoming).__name__}"
        )
    return [*existing, *incoming]


def _merge_dict(existing: Any, incoming: Any, key: str) -> Any:
    if existing is None:
        existing = {}
    if not isinstance(existing, dict) or not isinstance(incoming, dict):
        raise ContextConflictError(f"merge_dict expects dicts at {key}")
    out = dict(existing)
    out.update(incoming)
    return out
