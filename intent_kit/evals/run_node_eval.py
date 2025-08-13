#!/usr/bin/env python3
"""
run_node_eval.py

Run evaluations on sample nodes using datasets.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import os
import importlib
import argparse
import csv
from datetime import datetime

# Add text similarity imports
from difflib import SequenceMatcher
from dotenv import load_dotenv
from intent_kit.core.context import DefaultContext as Context
from intent_kit.services.yaml_service import yaml_service
from intent_kit.services.loader_service import dataset_loader, module_loader
from intent_kit.core.types import ExecutionResult
from intent_kit.nodes import ActionNode, ClassifierNode

load_dotenv()

_first_test_case: dict = {}


def load_dataset(dataset_path: Path) -> Dict[str, Any]:
    """Load a dataset from YAML file."""
    return dataset_loader.load(dataset_path)


def get_node_from_module(module_name: str, node_name: str):
    """Get a node instance from a module."""
    return module_loader.load(module_name, node_name)


def save_raw_results_to_csv(
    dataset_name: str,
    test_case: Dict[str, Any],
    actual_output: Any,
    success: bool,
    error: Optional[str] = None,
    similarity_score: Optional[float] = None,
    run_timestamp: Optional[str] = None,
    metrics: Optional[Dict[str, Any]] = None,
):
    """Save raw evaluation results to CSV files."""
    # Create organized results directory structure
    today = datetime.now().strftime("%Y-%m-%d")
    if run_timestamp is None:
        run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create results directory structure
    results_dir = Path(__file__).parent / "results" / "latest"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Also create date-based directory for archiving
    date_dir = Path(__file__).parent / "results" / today
    date_dir.mkdir(parents=True, exist_ok=True)

    # Create CSV files for this dataset
    csv_file = results_dir / f"{dataset_name}_results.csv"
    date_csv_file = date_dir / f"{dataset_name}_results_{run_timestamp}.csv"

    # Prepare row data
    row_data = {
        "timestamp": importlib.import_module("datetime").datetime.now().isoformat(),
        "input": test_case["input"],
        "expected": test_case["expected"],
        "actual": actual_output,
        "success": success,
        "similarity_score": similarity_score or "",
        "error": error or "",
        "context": str(test_case.get("context", {})),
        "metrics": str(metrics or {}),
    }

    # Check if this is the first test case (to write header)
    global _first_test_case
    is_first = dataset_name not in _first_test_case
    if is_first:
        _first_test_case[dataset_name] = True
        # Clear both files for new evaluation run
        if csv_file.exists():
            csv_file.unlink()
        if date_csv_file.exists():
            date_csv_file.unlink()

    # Write to latest directory
    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row_data.keys())
        if is_first:
            writer.writeheader()
        writer.writerow(row_data)

    # Write to date-based directory for archiving (always write header for new file)
    write_header = not date_csv_file.exists()
    with open(date_csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row_data.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row_data)

    return str(csv_file)


def calculate_similarity(expected: str, actual: str) -> float:
    """Calculate similarity between expected and actual outputs."""
    if not expected or not actual:
        return 0.0
    return SequenceMatcher(None, expected.lower(), actual.lower()).ratio()


def evaluate_node(
    node: Any,
    test_cases: List[Dict[str, Any]],
    dataset_name: str,
    run_timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate a node against test cases."""
    results: Dict[str, Any] = {
        "dataset": dataset_name,
        "total_cases": len(test_cases),
        "correct": 0,
        "incorrect": 0,
        "errors": [],
        "details": [],
        "raw_results_file": "",
    }

    for i, test_case in enumerate(test_cases):
        user_input = test_case["input"]
        expected = test_case["expected"]

        try:
            # Create context with test case context
            context = Context()
            if "context" in test_case:
                for key, value in test_case["context"].items():
                    context.set(key, value, modified_by="eval")

            # Execute node
            if hasattr(node, "execute"):
                result = node.execute(user_input, context)
            elif callable(node):
                result = node(user_input, context=context)
            else:
                raise ValueError("Node must be callable or have .execute method")

            # Extract result data
            if isinstance(result, ExecutionResult):
                actual_output = result.data
                metrics = result.metrics
            else:
                actual_output = result
                metrics = {}

            # Check if execution was successful
            if actual_output is not None:
                # Calculate similarity for string comparisons
                similarity_score_val = calculate_similarity(
                    str(expected), str(actual_output)
                )

                # Determine correctness
                if isinstance(expected, (int, float)) and isinstance(
                    actual_output, (int, float)
                ):
                    # For numeric values, allow small tolerance
                    tolerance = 1e-6
                    correct = abs(expected - actual_output) < tolerance
                else:
                    # For actions and classifiers, compare strings
                    correct = (
                        str(actual_output).strip().lower()
                        == str(expected).strip().lower()
                    )

                if correct:
                    results["correct"] += 1
                else:
                    results["incorrect"] += 1
                    results["errors"].append(
                        {
                            "case": i + 1,
                            "input": user_input,
                            "expected": expected,
                            "actual": actual_output,
                            "similarity_score": similarity_score_val,
                            "type": "incorrect_output",
                        }
                    )

                # Save raw result to CSV
                save_raw_results_to_csv(
                    dataset_name,
                    test_case,
                    actual_output,
                    correct,
                    similarity_score=similarity_score_val,
                    run_timestamp=run_timestamp,
                    metrics=metrics,
                )
            else:
                results["incorrect"] += 1
                error_msg = "No output produced"
                results["errors"].append(
                    {
                        "case": i + 1,
                        "input": user_input,
                        "expected": expected,
                        "actual": None,
                        "type": "no_output",
                        "error": error_msg,
                    }
                )

                # Save raw result to CSV
                save_raw_results_to_csv(
                    dataset_name,
                    test_case,
                    None,
                    False,
                    error_msg,
                    run_timestamp=run_timestamp,
                    metrics=metrics,
                )

        except Exception as e:
            results["incorrect"] += 1
            error_msg = str(e)
            results["errors"].append(
                {
                    "case": i + 1,
                    "input": user_input,
                    "expected": expected,
                    "actual": None,
                    "type": "exception",
                    "error": error_msg,
                }
            )

            # Save raw result to CSV
            save_raw_results_to_csv(
                dataset_name,
                test_case,
                None,
                False,
                error_msg,
                run_timestamp=run_timestamp,
            )

        # Store detailed results
        results["details"].append(
            {
                "case": i + 1,
                "input": user_input,
                "expected": expected,
                "actual": actual_output if "actual_output" in locals() else None,
                "success": "actual_output" in locals() and actual_output is not None,
                "error": error_msg if "error_msg" in locals() else None,
                "metrics": metrics if "metrics" in locals() else {},
            }
        )

    results["accuracy"] = (
        results["correct"] / results["total_cases"] if results["total_cases"] > 0 else 0
    )
    return results


def generate_markdown_report(
    results: List[Dict[str, Any]],
    output_path: Path,
    run_timestamp: Optional[str] = None,
    mock_mode: bool = False,
):
    """Generate a markdown report from evaluation results."""
    # Generate the report content
    mock_indicator = " (MOCK MODE)" if mock_mode else ""
    report_content = f"# Node Evaluation Report{mock_indicator}\n\n"
    report_content += f"Generated on: {importlib.import_module('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_content += f"Mode: {'Mock (simulated responses)' if mock_mode else 'Live (real API calls)'}\n\n"

    # Summary
    report_content += "## Summary\n\n"
    total_cases = sum(r["total_cases"] for r in results)
    total_correct = sum(r["correct"] for r in results)
    overall_accuracy = total_correct / total_cases if total_cases > 0 else 0

    report_content += f"- **Total Test Cases**: {total_cases}\n"
    report_content += f"- **Total Correct**: {total_correct}\n"
    report_content += f"- **Overall Accuracy**: {overall_accuracy:.1%}\n\n"

    # Individual dataset results
    report_content += "## Dataset Results\n\n"
    for result in results:
        report_content += f"### {result['dataset']}\n"
        report_content += f"- **Accuracy**: {result['accuracy']:.1%} ({result['correct']}/{result['total_cases']})\n"
        report_content += f"- **Correct**: {result['correct']}\n"
        report_content += f"- **Incorrect**: {result['incorrect']}\n"
        report_content += f"- **Raw Results**: `{result['raw_results_file']}`\n\n"

        # Show errors if any
        if result["errors"]:
            report_content += "#### Errors\n"
            for error in result["errors"][:5]:  # Show first 5 errors
                report_content += f"- **Case {error['case']}**: {error['input']}\n"
                report_content += f"  - Expected: `{error['expected']}`\n"
                report_content += f"  - Actual: `{error['actual']}`\n"
                if error.get("error"):
                    report_content += f"  - Error: {error['error']}\n"
                report_content += "\n"
            if len(result["errors"]) > 5:
                report_content += (
                    f"- ... and {len(result['errors']) - 5} more errors\n\n"
                )

    # Detailed results table
    report_content += "## Detailed Results\n\n"
    report_content += "| Dataset | Accuracy | Correct | Total | Raw Results |\n"
    report_content += "|---------|----------|---------|-------|-------------|\n"
    for result in results:
        report_content += f"| {result['dataset']} | {result['accuracy']:.1%} | {result['correct']} | {result['total_cases']} | `{result['raw_results_file']}` |\n"

    # Write to the specified output path
    with open(output_path, "w") as f:
        f.write(report_content)

    today = datetime.now().strftime("%Y-%m-%d")
    if run_timestamp is None:
        run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_reports_dir = Path(__file__).parent / "reports" / today
    date_reports_dir.mkdir(parents=True, exist_ok=True)

    # Create date-based filename
    date_output_path = (
        date_reports_dir / f"{output_path.stem}_{run_timestamp}{output_path.suffix}"
    )
    with open(date_output_path, "w") as f:
        f.write(report_content)


def main():
    parser = argparse.ArgumentParser(description="Run node evaluations")
    parser.add_argument("--dataset", help="Specific dataset to run")
    parser.add_argument("--output", help="Output file for markdown report")
    parser.add_argument("--llm-config", help="Path to LLM configuration file")

    args = parser.parse_args()

    # Load LLM configuration if provided
    llm_config = {}
    if args.llm_config:
        with open(args.llm_config, "r") as f:
            llm_config = yaml_service.safe_load(f)

        # Set environment variables for API keys
        for provider, config in llm_config.items():
            if "api_key" in config:
                env_var = f"{provider.upper()}_API_KEY"
                os.environ[env_var] = config["api_key"]
                print(f"Set {env_var} environment variable")

    # Find datasets
    datasets_dir = Path(__file__).parent / "datasets"
    if not datasets_dir.exists():
        print(f"Datasets directory not found: {datasets_dir}")
        sys.exit(1)

    dataset_files = list(datasets_dir.glob("*.yaml"))
    if not dataset_files:
        print(f"No dataset files found in {datasets_dir}")
        sys.exit(1)

    # Filter to specific dataset if requested
    if args.dataset:
        dataset_files = [f for f in dataset_files if args.dataset in f.name]
        if not dataset_files:
            print(f"No dataset files found matching '{args.dataset}'")
            sys.exit(1)

    results = []
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for dataset_file in dataset_files:
        print(f"\nEvaluating dataset: {dataset_file.name}")

        try:
            # Load dataset
            dataset = load_dataset(dataset_file)
            dataset_name = dataset["dataset"]["name"]
            node_type = dataset["dataset"]["node_type"]
            node_name = dataset["dataset"]["node_name"]

            # Create appropriate node based on type
            if node_type == "action":
                # Create a simple test action function
                def test_action(**kwargs):
                    destination = kwargs.get("destination", "Unknown")
                    date = kwargs.get("date", "ASAP")
                    booking_id = kwargs.get("booking_id", 1)
                    return f"Flight booked to {destination} for {date} (Booking #{booking_id})"

                node = ActionNode(
                    name=node_name,
                    action=test_action,
                    description=f"Test action for {dataset_name}",
                    terminate_on_success=True,
                    param_key="extracted_params",
                )
            elif node_type == "classifier":
                # Create a simple test classifier function
                def test_classifier(user_input: str, ctx) -> str:
                    weather_keywords = ["weather", "temperature", "forecast", "climate"]
                    cancel_keywords = [
                        "cancel",
                        "cancellation",
                        "canceled",
                        "cancelled",
                    ]

                    input_lower = user_input.lower()

                    if any(keyword in input_lower for keyword in weather_keywords):
                        return "weather"
                    elif any(keyword in input_lower for keyword in cancel_keywords):
                        return "cancel"
                    else:
                        return "unknown"

                node = ClassifierNode(
                    name=node_name,
                    output_labels=["weather", "cancel", "unknown"],
                    description=f"Test classifier for {dataset_name}",
                    classification_func=test_classifier,
                )
            else:
                print(f"Unsupported node type: {node_type}")
                continue

            # Run evaluation
            test_cases = dataset["test_cases"]
            result = evaluate_node(node, test_cases, dataset_name, run_timestamp)
            results.append(result)

            # Print results
            accuracy = result["accuracy"]
            print(
                f"  Accuracy: {accuracy:.1%} ({result['correct']}/{result['total_cases']})"
            )
            print(f"  Raw results saved to: {result['raw_results_file']}")

            if result["errors"]:
                print(f"  Errors: {len(result['errors'])}")
                for error in result["errors"][:3]:  # Show first 3 errors
                    print(f"    - Case {error['case']}: {error['input']}")
                    print(f"      Expected: {error['expected']}")
                    print(f"      Actual: {error['actual']}")

        except Exception as e:
            print(f"Error evaluating {dataset_file.name}: {e}")
            import traceback

            traceback.print_exc()
            continue

    # Generate report
    if results:
        if args.output:
            output_path = Path(args.output)
        else:
            # Create organized reports directory structure
            today = datetime.now().strftime("%Y-%m-%d")

            # Create reports directory structure
            reports_dir = Path(__file__).parent / "reports" / "latest"
            reports_dir.mkdir(parents=True, exist_ok=True)

            # Also create date-based directory for archiving
            date_reports_dir = Path(__file__).parent / "reports" / today
            date_reports_dir.mkdir(parents=True, exist_ok=True)

            output_path = reports_dir / "evaluation_report.md"

        generate_markdown_report(results, output_path, run_timestamp=run_timestamp)
        print(f"\nReport generated: {output_path}")

        # Print summary
        total_cases = sum(r["total_cases"] for r in results)
        total_correct = sum(r["correct"] for r in results)
        overall_accuracy = total_correct / total_cases if total_cases > 0 else 0
        print(
            f"\nOverall Accuracy: {overall_accuracy:.1%} ({total_correct}/{total_cases})"
        )


if __name__ == "__main__":
    main()
