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
