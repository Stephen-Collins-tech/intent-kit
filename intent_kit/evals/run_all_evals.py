#!/usr/bin/env python3
"""
run_all_evals.py

Run evaluations on all datasets and generate comprehensive markdown reports.
"""

import argparse
from intent_kit.evals import load_dataset
from intent_kit.evals.run_node_eval import (
    get_node_from_module,
    evaluate_node,
    generate_markdown_report,
)
from intent_kit.services.yaml_service import yaml_service
from typing import Dict, List, Any, Optional
from datetime import datetime
import pathlib
from dotenv import load_dotenv

load_dotenv()


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
                print(
                    f"Individual report written to: {individual_report_path} and archived as {date_individual_report_path}"
                )

    if not args.quiet:
        print("Evaluation complete!")

    return True


def run_all_evaluations_internal(
    llm_config_path: Optional[str] = None, mock_mode: bool = False
) -> List[Dict[str, Any]]:
    """Run evaluations on all datasets and return results."""
    dataset_dir = pathlib.Path(__file__).parent / "datasets"
    results = []

    # Load LLM configuration if provided
    if llm_config_path:
        import os

        with open(llm_config_path, "r") as f:
            llm_config = yaml_service.safe_load(f)

        # Set environment variables for API keys
        for provider, config in llm_config.items():
            if "api_key" in config:
                env_var = f"{provider.upper()}_API_KEY"
                os.environ[env_var] = config["api_key"]
                print(f"Set {env_var} environment variable (key obfuscated)")

    # Set mock mode environment variable
    if mock_mode:
        import os

        os.environ["INTENT_KIT_MOCK_MODE"] = "1"
        print("Running in MOCK mode - using simulated responses")

    for dataset_file in dataset_dir.glob("*.yaml"):
        print(f"Evaluating {dataset_file.name}...")

        # Load dataset
        dataset = load_dataset(dataset_file)
        dataset_name = dataset.name
        node_name = dataset.node_name

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
        test_cases = [
            {"input": tc.input, "expected": tc.expected, "context": tc.context}
            for tc in dataset.test_cases
        ]
        result = evaluate_node(node, test_cases, dataset_name)
        results.append(result)

        # Print results
        accuracy = result["accuracy"]
        mode_indicator = "[MOCK]" if mock_mode else ""
        print(
            f"  Accuracy: {accuracy:.1%} ({result['correct']}/{result['total_cases']}) {mode_indicator}"
        )

    return results


def generate_comprehensive_report(
    results: List[Dict[str, Any]],
    output_file: Optional[str] = None,
    run_timestamp: str = "",
    mock_mode: bool = False,
) -> str:
    """Generate a comprehensive markdown report for all evaluations."""

    total_datasets = len(results)
    total_tests = sum(r["total_cases"] for r in results)
    total_passed = sum(r["correct"] for r in results)
    overall_accuracy = total_passed / total_tests if total_tests > 0 else 0.0

    # Count statuses
    passed_datasets = sum(1 for r in results if r["accuracy"] >= 0.8)  # 80% threshold
    failed_datasets = total_datasets - passed_datasets

    # Add mock mode indicator
    mock_indicator = " (MOCK MODE)" if mock_mode else ""

    report = f"""# Comprehensive Evaluation Report{mock_indicator}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Mode:** {'Mock (simulated responses)' if mock_mode else 'Live (real API calls)'}
**Total Datasets:** {total_datasets}
**Total Tests:** {total_tests}
**Overall Accuracy:** {overall_accuracy:.1%}

## Executive Summary

| Metric | Value |
|--------|-------|
| **Datasets Evaluated** | {total_datasets} |
| **Datasets Passed** | {passed_datasets} |
| **Datasets Failed** | {failed_datasets} |
| **Total Tests** | {total_tests} |
| **Tests Passed** | {total_passed} |
| **Tests Failed** | {total_tests - total_passed} |
| **Overall Accuracy** | {overall_accuracy:.1%} |

## Dataset Results

| Dataset | Accuracy | Status | Tests |
|---------|----------|--------|-------|
"""

    for result in results:
        status = "PASSED" if result["accuracy"] >= 0.8 else "FAILED"
        status_icon = "✅" if status == "PASSED" else "❌"

        report += f"| `{result['dataset']}` | {result['accuracy']:.1%} | {status_icon} {status} | {result['correct']}/{result['total_cases']} |\n"

    # Detailed results for each dataset
    report += "\n## Detailed Results\n\n"

    for result in results:
        report += f"### {result['dataset']}\n\n"
        report += f"**Accuracy:** {result['accuracy']:.1%} ({result['correct']}/{result['total_cases']})  \n"
        report += (
            f"**Status:** {'PASSED' if result['accuracy'] >= 0.8 else 'FAILED'}\n\n"
        )

        # Show errors if any
        if result["errors"]:
            report += "#### Errors\n"
            for error in result["errors"][:5]:  # Show first 5 errors
                report += f"- **Case {error['case']}**: {error['input']}\n"
                report += f"  - Expected: `{error['expected']}`\n"
                report += f"  - Actual: `{error['actual']}`\n"
                if error.get("error"):
                    report += f"  - Error: {error['error']}\n"
                report += "\n"
            if len(result["errors"]) > 5:
                report += f"- ... and {len(result['errors']) - 5} more errors\n\n"

    # Write to file if specified
    if output_file:
        with open(output_file, "w") as f:
            f.write(report)
        print(f"Comprehensive report written to: {output_file}")
        return output_file

    return report


if __name__ == "__main__":
    run_all_evaluations()
