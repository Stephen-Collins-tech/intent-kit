#!/usr/bin/env python3
"""
intent_kit.evals

A clean Python API for evaluating intent-kit nodes against YAML datasets.
"""

import csv
import importlib
from typing import Any, Dict, List, Optional, Callable, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from intent_kit.services.yaml_service import yaml_service


@dataclass
class EvalTestCase:
    """A single test case with input, expected output, and optional context."""

    input: str
    expected: Any
    context: Optional[Dict[str, Any]]

    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class Dataset:
    """A dataset containing test cases for evaluating a node."""

    name: str
    description: Optional[str]
    node_type: str
    node_name: str
    test_cases: List[EvalTestCase]

    def __post_init__(self):
        if self.description is None:
            self.description = ""


@dataclass
class EvalTestResult:
    """Result of a single test case evaluation."""

    input: str
    expected: Any
    actual: Any
    passed: bool
    context: Optional[Dict[str, Any]]
    error: Optional[str] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}


class EvalResult:
    """Results from evaluating a node against a dataset."""

    def __init__(self, results: List[EvalTestResult], dataset_name: str = ""):
        self.results = results
        self.dataset_name = dataset_name

    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)

    def accuracy(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)

    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    def total_count(self) -> int:
        return len(self.results)

    def errors(self) -> List[EvalTestResult]:
        return [r for r in self.results if not r.passed]

    def print_summary(self) -> None:
        print(f"\nEvaluation Results for {self.dataset_name or 'Dataset'}:")
        print(
            f"  Accuracy: {self.accuracy():.1%} ({self.passed_count()}/{self.total_count()})"
        )
        print(f"  Passed: {self.passed_count()}")
        print(f"  Failed: {self.failed_count()}")
        if self.errors():
            print("\nFailed Tests:")
            for i, error in enumerate(self.errors()[:5]):
                print(f"  {i+1}. Input: '{error.input}'")
                print(f"     Expected: '{error.expected}'")
                print(f"     Actual: '{error.actual}'")
                if error.error:
                    print(f"     Error: {error.error}")
                print()
            if len(self.errors()) > 5:
                print(f"  ... and {len(self.errors()) - 5} more failed tests")

    def save_csv(self, path: Optional[str] = None) -> str:
        if path is None:
            results_dir = Path(__file__).parent / "results" / "latest"
            results_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = str(
                results_dir / f"{self.dataset_name}_eval_results_{timestamp}.csv"
            )
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["input", "expected", "actual", "passed", "error", "context"]
            )
            for result in self.results:
                writer.writerow(
                    [
                        result.input,
                        result.expected,
                        result.actual,
                        result.passed,
                        result.error or "",
                        str(result.context),
                    ]
                )
        return str(path)

    def save_json(self, path: Optional[str] = None) -> str:
        if path is None:
            results_dir = Path(__file__).parent / "results" / "latest"
            results_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = str(
                results_dir / f"{self.dataset_name}_eval_results_{timestamp}.json"
            )
        import json

        data = {
            "dataset_name": self.dataset_name,
            "summary": {
                "accuracy": self.accuracy(),
                "passed_count": self.passed_count(),
                "failed_count": self.failed_count(),
                "total_count": self.total_count(),
            },
            "results": [
                {
                    "input": r.input,
                    "expected": r.expected,
                    "actual": r.actual,
                    "passed": r.passed,
                    "error": r.error,
                    "context": r.context,
                }
                for r in self.results
            ],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return str(path)

    def save_markdown(self, path: Optional[str] = None) -> str:
        if path is None:
            reports_dir = Path(__file__).parent / "reports" / "latest"
            reports_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = str(reports_dir / f"{self.dataset_name}_eval_report_{timestamp}.md")
        report = f"""# Evaluation Report: {self.dataset_name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Accuracy:** {self.accuracy():.1%} ({self.passed_count()}/{self.total_count()})
- **Passed:** {self.passed_count()}
- **Failed:** {self.failed_count()}

## Results

| # | Input | Expected | Actual | Status |
|---|-------|----------|--------|--------|
"""
        for i, result in enumerate(self.results, 1):
            status = "✅ PASS" if result.passed else "❌ FAIL"
            report += f"| {i} | `{result.input}` | `{result.expected}` | `{result.actual}` | {status} |\n"
        if self.errors():
            report += "\n## Failed Tests\n\n"
            for i, error in enumerate(self.errors(), 1):
                report += f"### Failed Test {i}\n\n"
                report += f"- **Input:** `{error.input}`\n"
                report += f"- **Expected:** `{error.expected}`\n"
                report += f"- **Actual:** `{error.actual}`\n"
                if error.error:
                    report += f"- **Error:** {error.error}\n"
                report += "\n"
        with open(path, "w") as f:
            f.write(report)
        return str(path)


def load_dataset(path: Union[str, Path]) -> Dataset:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    with open(path, "r") as f:
        data = yaml_service.safe_load(f)
    if "dataset" not in data:
        raise ValueError(f"Dataset file missing 'dataset' section: {path}")
    dataset_info = data["dataset"]
    required_fields = ["name", "node_type", "node_name"]
    for field in required_fields:
        if field not in dataset_info:
            raise ValueError(f"Dataset missing required field '{field}': {path}")
    if "test_cases" not in data:
        raise ValueError(f"Dataset file missing 'test_cases' section: {path}")
    test_cases = []
    for i, tc_data in enumerate(data["test_cases"]):
        if "input" not in tc_data:
            raise ValueError(f"Test case {i+1} missing 'input' field: {path}")
        if "expected" not in tc_data:
            raise ValueError(f"Test case {i+1} missing 'expected' field: {path}")
        test_case = EvalTestCase(
            input=tc_data["input"],
            expected=tc_data["expected"],
            context=tc_data.get("context", {}),
        )
        test_cases.append(test_case)
    return Dataset(
        name=dataset_info["name"],
        description=dataset_info.get("description", ""),
        node_type=dataset_info["node_type"],
        node_name=dataset_info["node_name"],
        test_cases=test_cases,
    )


def get_node_from_module(module_name: str, node_name: str):
    try:
        module = importlib.import_module(module_name)
        return getattr(module, node_name)
    except (ImportError, AttributeError) as e:
        print(f"Error loading node {node_name} from {module_name}: {e}")
        return None


def run_eval(
    dataset: Dataset,
    node: Any,
    comparator: Optional[Callable[[Any, Any], bool]] = None,
    fail_fast: bool = False,
) -> EvalResult:
    if comparator is None:

        def default_comparator(expected, actual):
            return expected == actual

        comparator = default_comparator
    results = []
    for test_case in dataset.test_cases:
        try:
            if callable(node):
                actual = node(test_case.input, context=test_case.context)
            elif hasattr(node, "execute"):
                from intent_kit.context import IntentContext

                context = IntentContext()
                if test_case.context:
                    for key, value in test_case.context.items():
                        context.set(key, value, modified_by="eval")
                result = node.execute(test_case.input, context)
                actual = result.output if result.success else None
                if not result.success and result.error:
                    raise Exception(result.error.message)
            else:
                raise ValueError("Node must be callable or have an .execute() method")
            passed = comparator(test_case.expected, actual)
            result = EvalTestResult(
                input=test_case.input,
                expected=test_case.expected,
                actual=actual,
                passed=passed,
                context=test_case.context,
            )
        except Exception as e:
            result = EvalTestResult(
                input=test_case.input,
                expected=test_case.expected,
                actual=None,
                passed=False,
                context=test_case.context,
                error=str(e),
            )
            if fail_fast:
                results.append(result)
                return EvalResult(results, dataset.name)
        results.append(result)
    return EvalResult(results, dataset.name)


def run_eval_from_path(
    dataset_path: Union[str, Path],
    node: Any,
    comparator: Optional[Callable[[Any, Any], bool]] = None,
    fail_fast: bool = False,
) -> EvalResult:
    dataset = load_dataset(dataset_path)
    return run_eval(dataset, node, comparator, fail_fast)


def run_eval_from_module(
    dataset_path: Union[str, Path],
    module_name: str,
    node_name: str,
    comparator: Optional[Callable[[Any, Any], bool]] = None,
    fail_fast: bool = False,
) -> EvalResult:
    dataset = load_dataset(dataset_path)
    node = get_node_from_module(module_name, node_name)
    if node is None:
        raise ValueError(f"Failed to load node {node_name} from {module_name}")
    return run_eval(dataset, node, comparator, fail_fast)


# Control what gets imported when using "from intent_kit.evals import *"
__all__ = [
    "EvalTestCase",
    "Dataset",
    "EvalTestResult",
    "EvalResult",
    "load_dataset",
    "get_node_from_module",
    "run_eval",
    "run_eval_from_path",
    "run_eval_from_module",
]
