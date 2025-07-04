#!/usr/bin/env python3
"""
run_eval.py

Expands pattern definitions into individual test cases, executes them
against a stub system-under-test, and stores both the expanded dataset
and raw outputs on disk.
"""
# ... existing code ...
import csv
import itertools
import json
import os
import pathlib
import re
from typing import Dict, List

import yaml
from tqdm import tqdm

# File locations -------------------------------------------------------------
SCRIPT_DIR = pathlib.Path(__file__).parent
PATTERNS_FILE = SCRIPT_DIR / "patterns.yaml"
GENERATED_DIR = SCRIPT_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

EVAL_SET_CSV = GENERATED_DIR / "eval_set.csv"
RAW_OUTPUTS_JSON = GENERATED_DIR / "raw_outputs.json"

# ---------------------------------------------------------------------------
# Stub system under test – replace with your real API call
# ---------------------------------------------------------------------------

def ask_system(text: str) -> str:
    """Demonstration function. Mimics what a real assistant might return."""
    tl = text.lower()
    m = re.match(r"how do i (close|delete|cancel) my account\?", tl)
    if m:
        action = m.group(1)
        return (
            f"To {action} your account, go to Settings > Account and select {action}."
        )

    m = re.match(r"i forgot my (password|pin)\. what do i do\?", tl)
    if m:
        cred = m.group(1)
        return (
            f"You can reset your {cred} by clicking 'Forgot {cred}' on the sign-in page."
        )

    return "Sorry, I don't know."


# ---------------------------------------------------------------------------
# Pattern expansion
# ---------------------------------------------------------------------------

def expand_patterns(pattern_defs: List[Dict]) -> List[Dict]:
    """Expand pattern definitions to a flat list of concrete test cases."""
    cases = []
    idx = 1
    for definition in pattern_defs:
        template = definition["pattern"]
        variables = definition.get("variables", {})
        expected_template = definition.get("expected", "")

        var_names = list(variables.keys())
        value_lists = [variables[name] for name in var_names]

        for combination in itertools.product(*value_lists):
            subs = dict(zip(var_names, combination))
            input_text = template.format(**subs)
            expected = expected_template.format(**subs) if expected_template else ""

            cases.append({
                "id": idx,
                "input": input_text,
                "expected": expected,
            })
            idx += 1
    return cases


# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def main():
    pattern_defs = yaml.safe_load(open(PATTERNS_FILE))['patterns']
    cases = expand_patterns(pattern_defs)

    # Write expanded dataset
    with open(EVAL_SET_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "input", "expected"])
        writer.writeheader()
        writer.writerows(cases)

    # Run cases through the system
    results = []
    for case in tqdm(cases, desc="Running cases"):
        output = ask_system(case["input"])
        results.append({"id": case["id"], "output": output})

    json.dump(results, open(RAW_OUTPUTS_JSON, "w"), indent=2)

    print(f"Wrote {len(cases)} cases to {EVAL_SET_CSV}")
    print(f"Wrote outputs to {RAW_OUTPUTS_JSON}")


if __name__ == "__main__":
    main()