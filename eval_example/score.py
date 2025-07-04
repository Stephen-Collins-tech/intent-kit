#!/usr/bin/env python3
"""
score.py

Reads the generated evaluation set and system outputs, then computes an
exact-match accuracy metric.  Mis-predictions are written to
./generated/errors.csv for quick inspection.
"""
import csv
import json
import pathlib
import sys

import pandas as pd

SCRIPT_DIR = pathlib.Path(__file__).parent
EVAL_SET_CSV = SCRIPT_DIR / "generated" / "eval_set.csv"
RAW_OUTPUTS_JSON = SCRIPT_DIR / "generated" / "raw_outputs.json"


def main():
    if not EVAL_SET_CSV.exists() or not RAW_OUTPUTS_JSON.exists():
        sys.exit("Required files not found. Run run_eval.py first.")

    # Ground-truth answers
    gt = {
        int(r["id"]): r["expected"].strip().lower()
        for r in csv.DictReader(open(EVAL_SET_CSV))
    }

    # System predictions
    preds = {
        int(r["id"]): r["output"].strip().lower()
        for r in json.load(open(RAW_OUTPUTS_JSON))
    }

    rows = []
    for i in gt:
        pred = preds.get(i, "")
        correct = gt[i] == pred
        rows.append({"id": i, "gold": gt[i], "pred": pred, "correct": correct})

    df = pd.DataFrame(rows)
    accuracy = df.correct.mean()
    total = len(df)
    print(f"Exact-match accuracy: {accuracy:.3%} ({df.correct.sum()}/{total})")

    errors = df[~df.correct]
    if not errors.empty:
        error_path = SCRIPT_DIR / "generated" / "errors.csv"
        errors.to_csv(error_path, index=False)
        print(f"Wrote {len(errors)} errors to {error_path}")


if __name__ == "__main__":
    main()