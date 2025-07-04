#!/usr/bin/env python3
"""run_node_eval.py

Standalone harness for running node-level micro-datasets.

Usage:
  python3 node_eval/run_node_eval.py --node node_eval.sample_nodes.uppercase_node:UppercaseNode \
                                     --dataset node_eval/datasets/uppercase_node.yaml

If --node is omitted, the script infers the node class from the dataset
filename (e.g. uppercase_node.yaml → UppercaseNode in
node_eval.sample_nodes.uppercase_node).
"""
import argparse
import importlib
import inspect
import pathlib
import sys
import yaml
from typing import Any, Dict, List, Tuple

from intent_kit.node.types import ExecutionResult


DEFAULT_DATASET_DIR = pathlib.Path(__file__).parent / "datasets"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_node_class(node_spec: str):
    """Import and return the node class object from a spec string.

    Spec format: "package.module:ClassName".
    """
    if ":" not in node_spec:
        raise ValueError("node spec must be in module:Class format")
    module_path, class_name = node_spec.split(":", 1)
    module = importlib.import_module(module_path)
    node_cls = getattr(module, class_name)
    return node_cls


def infer_node_spec_from_dataset(dataset_path: pathlib.Path) -> str:
    """Guess module and class from dataset filename 'xyz_node.yaml'."""
    stem = dataset_path.stem  # e.g. uppercase_node
    class_name = "".join(part.capitalize() for part in stem.split("_"))  # UppercaseNode
    module_path = f"node_eval.sample_nodes.{stem}"
    return f"{module_path}:{class_name}"


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def run_tests(node_cls, tests: List[Dict[str, Any]]) -> Tuple[int, int, List[Dict[str, Any]]]:
    node_instance = node_cls()
    passed = 0
    total = len(tests)
    detailed_results: List[Dict[str, Any]] = []
    for idx, case in enumerate(tests, 1):
        inp = case["input"]
        expected = case["expected"]
        result: ExecutionResult = node_instance.execute(inp)
        output = result.output
        success = output == expected and result.success
        if success:
            passed += 1
        detailed_results.append({
            "index": idx,
            "input": inp,
            "expected": expected,
            "output": output,
            "node_success": result.success,
            "test_pass": success,
            "error": None if result.error is None else result.error.to_dict(),
        })
    return passed, total, detailed_results


def main():
    parser = argparse.ArgumentParser(description="Node-level evaluation harness")
    parser.add_argument("--dataset", type=str, default=str(DEFAULT_DATASET_DIR / "uppercase_node.yaml"),
                        help="Path to YAML dataset file")
    parser.add_argument("--node", type=str, default=None,
                        help="Node spec in module:Class format (if omitted, inferred from dataset filename)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    dataset_path = pathlib.Path(args.dataset)
    if not dataset_path.exists():
        sys.exit(f"Dataset file not found: {dataset_path}")

    with open(dataset_path) as f:
        data = yaml.safe_load(f)
    tests = data.get("tests") or data.get("cases")
    if not tests:
        sys.exit("Dataset YAML must have 'tests' key with list of cases")

    node_spec = args.node or infer_node_spec_from_dataset(dataset_path)
    node_cls = resolve_node_class(node_spec)

    passed, total, details = run_tests(node_cls, tests)

    accuracy = passed / total if total else 0.0
    print(f"Node {node_cls.__name__}: {passed}/{total} passed (accuracy {accuracy:.1%})")

    if args.verbose or passed != total:
        import json
        print(json.dumps(details, indent=2))


if __name__ == "__main__":
    main()