#!/usr/bin/env python3
"""
test_eval_api.py

Test script to demonstrate the updated evals functionality with DAG-based nodes.
"""

import sys
from pathlib import Path
from intent_kit.evals import run_eval_from_path
from intent_kit.nodes import ActionNode, ClassifierNode
from intent_kit.core.context import DefaultContext as Context


def create_booking_action(destination: str, date: str, booking_id: int) -> str:
    """Simple booking action function for testing."""
    return f"Flight booked to {destination} for {date} (Booking #{booking_id})"


def create_weather_classifier(user_input: str, ctx) -> str:
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


def test_action_node_eval():
    """Test ActionNode evaluation."""
    print("Testing ActionNode evaluation...")

    # Create ActionNode
    action_node = ActionNode(
        name="booking_action",
        action=create_booking_action,
        description="Book flights based on extracted parameters",
        terminate_on_success=True,
        param_key="extracted_params",
    )

    # Load dataset
    dataset_path = Path(__file__).parent / "datasets" / "action_node_llm.yaml"

    # Run evaluation
    result = run_eval_from_path(dataset_path, action_node)

    # Print results
    result.print_summary()

    # Save results
    csv_path = result.save_csv()
    json_path = result.save_json()
    md_path = result.save_markdown()

    print("Results saved to:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")


def test_classifier_node_eval():
    """Test ClassifierNode evaluation."""
    print("\nTesting ClassifierNode evaluation...")

    # Create ClassifierNode
    classifier_node = ClassifierNode(
        name="intent_classifier",
        output_labels=["weather", "cancel", "unknown"],
        description="Classify user intent",
        classification_func=create_weather_classifier,
    )

    # Load dataset
    dataset_path = Path(__file__).parent / "datasets" / "classifier_node_llm.yaml"

    # Run evaluation
    result = run_eval_from_path(dataset_path, classifier_node)

    # Print results
    result.print_summary()

    # Save results
    csv_path = result.save_csv()
    json_path = result.save_json()
    md_path = result.save_markdown()

    print("Results saved to:")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")


def test_custom_comparator():
    """Test evaluation with custom comparator."""
    print("\nTesting custom comparator...")

    def case_insensitive_comparator(expected, actual):
        """Case-insensitive string comparison."""
        if isinstance(expected, str) and isinstance(actual, str):
            return expected.lower() == actual.lower()
        return expected == actual

    # Create ActionNode
    action_node = ActionNode(
        name="booking_action",
        action=create_booking_action,
        description="Book flights based on extracted parameters",
        terminate_on_success=True,
        param_key="extracted_params",
    )

    # Load dataset
    dataset_path = Path(__file__).parent / "datasets" / "action_node_llm.yaml"

    # Run evaluation with custom comparator
    result = run_eval_from_path(
        dataset_path, action_node, comparator=case_insensitive_comparator
    )

    print(f"Custom comparator accuracy: {result.accuracy():.1%}")


def test_context_factory():
    """Test evaluation with custom context factory."""
    print("\nTesting custom context factory...")

    def create_context_with_metadata():
        """Create context with additional metadata."""
        ctx = Context()
        ctx.set("eval_mode", True, modified_by="test")
        ctx.set("test_timestamp", "2024-01-01", modified_by="test")
        return ctx

    # Create ActionNode
    action_node = ActionNode(
        name="booking_action",
        action=create_booking_action,
        description="Book flights based on extracted parameters",
        terminate_on_success=True,
        param_key="extracted_params",
    )

    # Load dataset
    dataset_path = Path(__file__).parent / "datasets" / "action_node_llm.yaml"

    # Run evaluation with custom context factory
    result = run_eval_from_path(
        dataset_path, action_node, context_factory=create_context_with_metadata
    )

    print(f"Custom context factory accuracy: {result.accuracy():.1%}")


def main():
    """Run all tests."""
    print("Testing Updated Evals API with DAG-based Nodes")
    print("=" * 50)

    try:
        # Test ActionNode
        test_action_node_eval()

        # Test ClassifierNode
        test_classifier_node_eval()

        # Test custom comparator
        test_custom_comparator()

        # Test context factory
        test_context_factory()

        # Summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        # The original code had print statements for accuracy here,
        # but the test functions no longer return results.
        # This section will need to be updated if accuracy reporting is desired.
        print(
            "Accuracy reporting is currently disabled as test functions no longer return results."
        )

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
