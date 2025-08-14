#!/usr/bin/env python3
"""
run_all_evals.py

Run evaluations on all datasets and generate comprehensive markdown reports.
"""

import argparse
from intent_kit.evals import load_dataset, run_eval_from_path, get_node_from_module
from intent_kit.evals.run_node_eval import generate_markdown_report
from intent_kit.services.yaml_service import yaml_service
from intent_kit.nodes import ActionNode, ClassifierNode
from typing import Dict, List, Any, Optional
from datetime import datetime
import pathlib
from dotenv import load_dotenv

load_dotenv()


def create_test_action(destination: str, date: str, booking_id: int) -> str:
    """Simple booking action function for testing."""
    return f"Flight booked to {destination} for {date} (Booking #{booking_id})"


def create_test_classifier(user_input: str, ctx) -> str:
    """Simple weather classifier function for testing."""
    weather_keywords = ["weather", "temperature", "forecast", "climate"]
    cancel_keywords = ["cancel", "cancellation", "canceled", "cancelled"]

    input_lower = user_input.lower()

    if any(keyword in input_lower for keyword in weather_keywords):
        return "weather"
    elif any(keyword in input_lower for keyword in cancel_keywords):
        return "cancel"
    else:
        return "unknown"


def create_node_for_dataset(dataset_name: str, node_type: str, node_name: str):
    """Create appropriate node instance based on dataset configuration."""
    if node_type == "action":
        return ActionNode(
            name=node_name,
            action=create_test_action,
            description=f"Test action for {dataset_name}",
            terminate_on_success=True,
            param_key="extracted_params",
        )
    elif node_type == "classifier":
        return ClassifierNode(
            name=node_name,
            output_labels=["weather", "cancel", "unknown"],
            description=f"Test classifier for {dataset_name}",
            classification_func=create_test_classifier,
        )
    else:
        # For other node types, try to load from module
        return get_node_from_module("intent_kit.nodes", node_name)


def run_all_evaluations():
    """Run all evaluations and generate reports."""
    parser = argparse.ArgumentParser(
        description="Run all evaluations and generate comprehensive report"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="intent_kit/evals/reports/latest/comprehensive_report.md",
        help="Output file for comprehensive report",
    )
    parser.add_argument(
        "--individual",
        action="store_true",
        help="Also generate individual reports for each dataset",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress output messages")
    parser.add_argument("--llm-config", help="Path to LLM configuration file")
    parser.add_argument(
        "--mock", action="store_true", help="Run in mock mode without real API calls"
    )

    # Parse args if called as script, otherwise use defaults
    try:
        args = parser.parse_args()
    except SystemExit:
        # Called as function, use defaults
        args = parser.parse_args([])

    # Create organized reports directory structure
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    today = datetime.now().strftime("%Y-%m-%d")
    reports_dir = pathlib.Path(__file__).parent / "reports" / "latest"
    reports_dir.mkdir(parents=True, exist_ok=True)
    date_reports_dir = pathlib.Path(__file__).parent / "reports" / today
    date_reports_dir.mkdir(parents=True, exist_ok=True)

    # Set output path
    output_path = pathlib.Path(args.output)
    if args.output == "intent_kit/evals/reports/latest/comprehensive_report.md":
        output_path = reports_dir / "comprehensive_report.md"

    if not args.quiet:
        mode = "MOCK" if args.mock else "LIVE"
        print(f"Running all evaluations in {mode} mode...")
    results = run_all_evaluations_internal(args.llm_config, mock_mode=args.mock)

    if not args.quiet:
        print("Generating comprehensive report...")
    generate_comprehensive_report(
        results, str(output_path), run_timestamp=run_timestamp, mock_mode=args.mock
    )

    # Also write timestamped copy to date-based archive directory
    date_comprehensive_report_path = (
        date_reports_dir / f"comprehensive_report_{run_timestamp}.md"
    )
    with (
        open(output_path, "r") as src,
        open(date_comprehensive_report_path, "w") as dst,
    ):
        dst.write(src.read())
    if not args.quiet:
        print(f"Comprehensive report archived as: {date_comprehensive_report_path}")

    if args.individual:
        if not args.quiet:
            print("Generating individual reports...")
        for result in results:
            dataset_name = result["dataset"]
            individual_report_path = reports_dir / f"{dataset_name}_report.md"
            # Write to latest
            generate_markdown_report(
                [result], individual_report_path, run_timestamp=run_timestamp
            )
            # Also write to date-based archive with timestamp in filename
            date_individual_report_path = (
                date_reports_dir / f"{dataset_name}_report_{run_timestamp}.md"
            )
            with (
                open(individual_report_path, "r") as src,
                open(date_individual_report_path, "w") as dst,
            ):
                dst.write(src.read())
            if not args.quiet:
                print(f"Individual report archived as: {date_individual_report_path}")

    if not args.quiet:
        print(f"Comprehensive report generated: {output_path}")

    return True


def run_all_evaluations_internal(
    llm_config_path: Optional[str] = None, mock_mode: bool = False
) -> List[Dict[str, Any]]:
    """Internal function to run all evaluations."""
    # Load LLM configuration if provided
    if llm_config_path:
        with open(llm_config_path, "r") as f:
            llm_config = yaml_service.safe_load(f)

        # Set environment variables for API keys
        for provider, config in llm_config.items():
            if "api_key" in config:
                import os

                env_var = f"{provider.upper()}_API_KEY"
                os.environ[env_var] = config["api_key"]
                print(f"Set {env_var} environment variable")

    # Find datasets
    datasets_dir = pathlib.Path(__file__).parent / "datasets"
    if not datasets_dir.exists():
        print(f"Datasets directory not found: {datasets_dir}")
        return []

    dataset_files = list(datasets_dir.glob("*.yaml"))
    if not dataset_files:
        print(f"No dataset files found in {datasets_dir}")
        return []

    results = []

    for dataset_file in dataset_files:
        print(f"\nEvaluating dataset: {dataset_file.name}")

        try:
            # Load dataset
            dataset = load_dataset(dataset_file)
            dataset_name = dataset.name
            node_type = dataset.node_type
            node_name = dataset.node_name

            # Create appropriate node
            node = create_node_for_dataset(dataset_name, node_type, node_name)
            if node is None:
                print(f"Failed to create node for {dataset_name}")
                continue

            # Run evaluation using the new API
            result = run_eval_from_path(dataset_file, node)

            # Convert to the format expected by the report generator
            converted_result = {
                "dataset": dataset_name,
                "total_cases": result.total_count(),
                "correct": result.passed_count(),
                "incorrect": result.failed_count(),
                "accuracy": result.accuracy(),
                "errors": [
                    {
                        "case": i + 1,
                        "input": error.input,
                        "expected": error.expected,
                        "actual": error.actual,
                        "error": error.error,
                        "type": "evaluation_error",
                    }
                    for i, error in enumerate(result.errors())
                ],
                "details": [
                    {
                        "case": i + 1,
                        "input": r.input,
                        "expected": r.expected,
                        "actual": r.actual,
                        "success": r.passed,
                        "error": r.error,
                        "metrics": r.metrics,
                    }
                    for i, r in enumerate(result.results)
                ],
                "raw_results_file": result.save_csv(),
            }

            results.append(converted_result)

            # Print results
            accuracy = result.accuracy()
            print(
                f"  Accuracy: {accuracy:.1%} ({result.passed_count()}/{result.total_count()})"
            )

            if result.errors():
                print(f"  Errors: {len(result.errors())}")
                for error in result.errors()[:3]:  # Show first 3 errors
                    print(f"    - Input: {error.input}")
                    print(f"      Expected: {error.expected}")
                    print(f"      Actual: {error.actual}")

        except Exception as e:
            print(f"Error evaluating {dataset_file.name}: {e}")
            import traceback

            traceback.print_exc()
            continue

    return results


def generate_comprehensive_report(
    results: List[Dict[str, Any]],
    output_path: str,
    run_timestamp: Optional[str] = None,
    mock_mode: bool = False,
):
    """Generate a comprehensive markdown report from all evaluation results."""
    import importlib

    # Generate the report content
    mock_indicator = " (MOCK MODE)" if mock_mode else ""
    report_content = f"# Comprehensive Node Evaluation Report{mock_indicator}\n\n"
    report_content += f"Generated on: {importlib.import_module('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_content += f"Mode: {'Mock (simulated responses)' if mock_mode else 'Live (real API calls)'}\n\n"

    # Summary
    report_content += "## Summary\n\n"
    total_cases = sum(r["total_cases"] for r in results)
    total_correct = sum(r["correct"] for r in results)
    overall_accuracy = total_correct / total_cases if total_cases > 0 else 0

    report_content += f"- **Total Test Cases**: {total_cases}\n"
    report_content += f"- **Total Correct**: {total_correct}\n"
    report_content += f"- **Overall Accuracy**: {overall_accuracy:.1%}\n"
    report_content += f"- **Datasets Evaluated**: {len(results)}\n\n"

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


if __name__ == "__main__":
    run_all_evaluations()
