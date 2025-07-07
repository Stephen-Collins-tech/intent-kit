#!/usr/bin/env python3
"""
eval_api_demo.py

Demonstration of the new intent-kit evaluation API.
"""

from intent_kit.evals import (
    load_dataset,
    run_eval,
    run_eval_from_path,
    run_eval_from_module,
    EvalTestCase,
    Dataset
)
from intent_kit.evals.sample_nodes.classifier_node_llm import classifier_node_llm


def demo_basic_usage():
    """Demonstrate basic usage with direct node instance."""
    print("=== Basic Usage Demo ===")

    # Load dataset
    dataset = load_dataset(
        "intent_kit/evals/datasets/classifier_node_llm.yaml")
    print(f"Loaded dataset: {dataset.name}")
    print(f"Test cases: {len(dataset.test_cases)}")

    # Run evaluation
    result = run_eval(dataset, classifier_node_llm)

    # Print results
    result.print_summary()

    # Save results (using default locations)
    csv_path = result.save_csv()
    json_path = result.save_json()
    md_path = result.save_markdown()

    print(f"Results saved to:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    return result


def demo_from_path():
    """Demonstrate usage with dataset path."""
    print("\n=== From Path Demo ===")

    result = run_eval_from_path(
        "intent_kit/evals/datasets/classifier_node_llm.yaml",
        classifier_node_llm
    )

    result.print_summary()
    return result


def demo_from_module():
    """Demonstrate usage with module loading."""
    print("\n=== From Module Demo ===")

    result = run_eval_from_module(
        "intent_kit/evals/datasets/classifier_node_llm.yaml",
        "intent_kit.evals.sample_nodes.classifier_node_llm",
        "classifier_node_llm"
    )

    result.print_summary()
    return result


def demo_custom_comparator():
    """Demonstrate usage with custom comparison logic."""
    print("\n=== Custom Comparator Demo ===")

    # Custom comparator for case-insensitive comparison
    def case_insensitive_comparator(expected, actual):
        if expected is None or actual is None:
            return expected == actual
        return str(expected).lower().strip() == str(actual).lower().strip()

    result = run_eval_from_path(
        "intent_kit/evals/datasets/classifier_node_llm.yaml",
        classifier_node_llm,
        comparator=case_insensitive_comparator
    )

    result.print_summary()
    return result


def demo_fail_fast():
    """Demonstrate fail-fast behavior."""
    print("\n=== Fail Fast Demo ===")

    result = run_eval_from_path(
        "intent_kit/evals/datasets/classifier_node_llm.yaml",
        classifier_node_llm,
        fail_fast=True
    )

    print(f"Fail-fast evaluation completed with {result.total_count()} tests")
    return result


def demo_programmatic_dataset():
    """Demonstrate creating a dataset programmatically."""
    print("\n=== Programmatic Dataset Demo ===")

    # Create test cases programmatically
    test_cases = [
        EvalTestCase(
            input="What's the weather like in Paris?",
            expected="Weather in Paris: Sunny with a chance of rain",
            context={"user_id": "demo_user"}
        ),
        EvalTestCase(
            input="Cancel my flight",
            expected="Successfully cancelled flight",
            context={"user_id": "demo_user"}
        )
    ]

    # Create dataset
    dataset = Dataset(
        name="demo_dataset",
        description="Programmatically created test dataset",
        node_type="classifier",
        node_name="classifier_node_llm",
        test_cases=test_cases
    )

    # Run evaluation
    result = run_eval(dataset, classifier_node_llm)
    result.print_summary()

    return result


def demo_error_handling():
    """Demonstrate error handling with a broken node."""
    print("\n=== Error Handling Demo ===")

    # Create a broken node that raises exceptions
    def broken_node(input_text, context=None):
        if "weather" in input_text.lower():
            raise ValueError("Weather service is down!")
        return "Default response"

    # Create a simple test case
    test_cases = [
        EvalTestCase(
            input="What's the weather like?",
            expected="Weather response",
            context={}
        ),
        EvalTestCase(
            input="Hello there",
            expected="Default response",
            context={}
        )
    ]

    dataset = Dataset(
        name="error_demo",
        description="Testing error handling",
        node_type="test",
        node_name="broken_node",
        test_cases=test_cases
    )

    result = run_eval(dataset, broken_node)
    result.print_summary()

    return result


def main():
    """Run all demos."""
    import os

    # Create results directory
    os.makedirs("results", exist_ok=True)

    # Run demos
    demos = [
        demo_basic_usage,
        demo_from_path,
        demo_from_module,
        demo_custom_comparator,
        demo_fail_fast,
        demo_programmatic_dataset,
        demo_error_handling
    ]

    results = []
    for demo in demos:
        try:
            result = demo()
            results.append(result)
        except Exception as e:
            print(f"Demo {demo.__name__} failed: {e}")

    # Summary
    print("\n=== Summary ===")
    for i, result in enumerate(results):
        print(f"Demo {i+1}: {result.accuracy():.1%} accuracy")

    print("\nAll demos completed! Check the results/ directory for output files.")


if __name__ == "__main__":
    main()
