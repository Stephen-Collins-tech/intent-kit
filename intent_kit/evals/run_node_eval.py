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
import re
from dotenv import load_dotenv
from intent_kit.context import IntentContext
from intent_kit.services.yaml_service import yaml_service

load_dotenv()

_first_test_case: dict = {}


def load_dataset(dataset_path: Path) -> Dict[str, Any]:
    """Load a dataset from YAML file."""
    with open(dataset_path, "r") as f:
        return yaml_service.safe_load(f)


def get_node_from_module(module_name: str, node_name: str):
    """Get a node instance from a module."""
    try:
        module = importlib.import_module(module_name)
        return getattr(module, node_name)
    except (ImportError, AttributeError) as e:
        print(f"Error loading node {node_name} from {module_name}: {e}")
        return None


def save_raw_results_to_csv(
    dataset_name: str,
    test_case: Dict[str, Any],
    actual_output: Any,
    success: bool,
    error: Optional[str] = None,
    similarity_score: Optional[float] = None,
    run_timestamp: Optional[str] = None,
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

    return csv_file, date_csv_file


def similarity_score(text1: str, text2: str) -> float:
    """Calculate similarity score between two texts."""

    # Normalize texts for comparison
    def normalize(text):
        return re.sub(r"\s+", " ", text.lower().strip())

    norm1 = normalize(text1)
    norm2 = normalize(text2)

    # Use sequence matcher for similarity
    return SequenceMatcher(None, norm1, norm2).ratio()


def chunks_similarity_score(
    expected_chunks: List[str], actual_chunks: List[str], threshold: float = 0.8
) -> tuple[bool, float]:
    """Calculate similarity score between expected and actual chunks."""
    if len(expected_chunks) != len(actual_chunks):
        return False, 0.0

    total_score = 0.0
    for expected, actual in zip(expected_chunks, actual_chunks):
        score = similarity_score(expected, actual)
        total_score += score

    avg_score = total_score / len(expected_chunks)
    return avg_score >= threshold, avg_score


def evaluate_node(
    node, test_cases: List[Dict[str, Any]], dataset_name: str
) -> Dict[str, Any]:
    """Evaluate a node against test cases."""
    results: Dict[str, Any] = {
        "dataset": dataset_name,
        "total_cases": len(test_cases),
        "correct": 0,
        "incorrect": 0,
        "errors": [],
        "details": [],
        "raw_results_file": f"intent_kit/evals/results/latest/{dataset_name}_results.csv",
    }

    # Generate a unique run timestamp for this evaluation
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Check if this node needs persistent context (like action_node_llm)
    needs_persistent_context = hasattr(node, "name") and "action_node_llm" in node.name

    # Create persistent context if needed
    persistent_context = None
    if needs_persistent_context:
        persistent_context = IntentContext()
        # Initialize booking count for action_node_llm
        persistent_context.set("booking_count", 0, modified_by="evaluation_init")

    for i, test_case in enumerate(test_cases):
        user_input = test_case["input"]
        expected = test_case["expected"]
        context_data = test_case.get("context", {})

        # Use persistent context if available, otherwise create new one
        if persistent_context is not None:
            context = persistent_context
            # Update context with test case data
            for key, value in context_data.items():
                context.set(key, value, modified_by="test_case")
        else:
            # Create new context for each test case
            context = IntentContext()
            for key, value in context_data.items():
                context.set(key, value, modified_by="test_case")

        try:
            # Execute the node
            result = node.execute(user_input, context)

            if result.success:
                actual_output = result.output
                similarity_score_val = None

                if isinstance(actual_output, list):
                    # For splitters, compare lists using similarity
                    if isinstance(expected, list):
                        correct, similarity_score_val = chunks_similarity_score(
                            expected, actual_output
                        )
                    else:
                        correct = False
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
                )
            else:
                results["incorrect"] += 1
                error_msg = result.error.message if result.error else "Unknown error"
                results["errors"].append(
                    {
                        "case": i + 1,
                        "input": user_input,
                        "expected": expected,
                        "actual": None,
                        "type": "execution_failed",
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
                "actual": result.output if "result" in locals() else None,
                "success": result.success if "result" in locals() else False,
                "error": (
                    result.error.message
                    if "result" in locals() and result.error
                    else None
                ),
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

        # Load dataset
        dataset = load_dataset(dataset_file)
        dataset_name = dataset["dataset"]["name"]
        node_name = dataset["dataset"]["node_name"]

        # Determine module name based on node name
        if "llm" in node_name:
            module_name = (
                f"intent_kit.evals.sample_nodes.{node_name.split('_')[0]}_node_llm"
            )
        else:
            module_name = (
                f"intent_kit.evals.sample_nodes.{node_name.split('_')[0]}_node"
            )

        # Load node
        node = get_node_from_module(module_name, node_name)
        if node is None:
            print(f"Failed to load node {node_name} from {module_name}")
            continue

        # Run evaluation
        test_cases = dataset["test_cases"]
        result = evaluate_node(node, test_cases, dataset_name)
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
