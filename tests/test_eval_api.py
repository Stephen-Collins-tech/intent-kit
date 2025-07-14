#!/usr/bin/env python3
"""
test_eval_api.py

Tests for the new evaluation API.
"""

import pytest
from pathlib import Path
from intent_kit.evals import (
    load_dataset,
    run_eval,
    run_eval_from_path,
    EvalTestCase,
    Dataset,
    EvalTestResult,
    EvalResult,
)
from intent_kit.services.yaml_service import yaml_service


def test_load_dataset():
    """Test loading a dataset from YAML."""
    dataset = load_dataset("intent_kit/evals/datasets/classifier_node_llm.yaml")

    assert dataset.name == "classifier_node_llm"
    assert dataset.node_type == "classifier"
    assert dataset.node_name == "classifier_node_llm"
    assert len(dataset.test_cases) > 0

    # Check first test case
    first_case = dataset.test_cases[0]
    assert first_case.input == "What's the weather like in New York?"
    assert first_case.expected == "Weather in New York: Sunny with a chance of rain"
    assert first_case.context == {"user_id": "user123"}


def test_load_dataset_missing_file():
    """Test loading a non-existent dataset."""
    with pytest.raises(FileNotFoundError):
        load_dataset("non_existent_file.yaml")


def test_load_dataset_malformed():
    """Test loading a malformed dataset."""
    # Create a temporary malformed YAML file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml_service.dump({"invalid": "data"}, f)
        temp_path = f.name

    try:
        with pytest.raises(ValueError):
            load_dataset(temp_path)
    finally:
        Path(temp_path).unlink()


def test_test_case_defaults():
    """Test EvalTestCase with default context."""
    test_case = EvalTestCase(input="test input", expected="test expected", context={})

    assert test_case.input == "test input"
    assert test_case.expected == "test expected"
    assert test_case.context == {}


def test_dataset_defaults():
    """Test Dataset with default description."""
    test_cases = [EvalTestCase("input", "expected", {})]
    dataset = Dataset(
        name="test",
        description="",
        node_type="test",
        node_name="test_node",
        test_cases=test_cases,
    )

    assert dataset.description == ""


def test_eval_result_methods():
    """Test EvalResult methods."""
    results = [
        EvalTestResult("input1", "expected1", "actual1", True, {}),
        EvalTestResult("input2", "expected2", "actual2", False, {}),
        EvalTestResult("input3", "expected3", "actual3", True, {}),
    ]

    eval_result = EvalResult(results, "test_dataset")

    assert eval_result.accuracy() == 2 / 3
    assert eval_result.passed_count() == 2
    assert eval_result.failed_count() == 1
    assert eval_result.total_count() == 3
    assert not eval_result.all_passed()
    assert len(eval_result.errors()) == 1


def test_eval_result_empty():
    """Test EvalResult with empty results."""
    eval_result = EvalResult([], "test_dataset")

    assert eval_result.accuracy() == 0.0
    assert eval_result.passed_count() == 0
    assert eval_result.failed_count() == 0
    assert eval_result.total_count() == 0
    assert eval_result.all_passed()  # Empty results are considered "all passed"
    assert len(eval_result.errors()) == 0


def test_run_eval_with_callable():
    """Test run_eval with a callable node."""

    def simple_node(input_text, context=None):
        return f"Processed: {input_text}"

    test_cases = [
        EvalTestCase("hello", "Processed: hello", {}),
        EvalTestCase("world", "Processed: world", {}),
    ]

    dataset = Dataset(
        name="test",
        description="Test dataset",
        node_type="test",
        node_name="simple_node",
        test_cases=test_cases,
    )

    result = run_eval(dataset, simple_node)

    assert result.accuracy() == 1.0
    assert result.all_passed()
    assert result.total_count() == 2


def test_run_eval_with_error():
    """Test run_eval with a node that raises exceptions."""

    def error_node(input_text, context=None):
        if "error" in input_text.lower():
            raise ValueError("Intentional error")
        return "success"

    test_cases = [
        EvalTestCase("hello", "success", {}),
        # This will fail due to exception
        EvalTestCase("error", "success", {}),
        EvalTestCase("world", "success", {}),
    ]

    dataset = Dataset(
        name="test",
        description="Test dataset",
        node_type="test",
        node_name="error_node",
        test_cases=test_cases,
    )

    result = run_eval(dataset, error_node)

    assert result.accuracy() == 2 / 3
    assert not result.all_passed()
    assert result.failed_count() == 1
    assert result.errors()[0].error == "Intentional error"


def test_run_eval_fail_fast():
    """Test run_eval with fail_fast=True."""

    def error_node(input_text, context=None):
        if "error" in input_text.lower():
            raise ValueError("Intentional error")
        return "success"

    test_cases = [
        EvalTestCase("hello", "success", {}),
        # This will fail and stop execution
        EvalTestCase("error", "success", {}),
        # This won't run due to fail_fast
        EvalTestCase("world", "success", {}),
    ]

    dataset = Dataset(
        name="test",
        description="Test dataset",
        node_type="test",
        node_name="error_node",
        test_cases=test_cases,
    )

    result = run_eval(dataset, error_node, fail_fast=True)

    assert result.total_count() == 2  # Only first two tests ran
    assert result.failed_count() == 1
    assert result.errors()[0].error == "Intentional error"


def test_run_eval_custom_comparator():
    """Test run_eval with custom comparator."""

    def simple_node(input_text, context=None):
        return input_text.upper()

    def case_insensitive_comparator(expected, actual):
        return str(expected).lower() == str(actual).lower()

    test_cases = [
        EvalTestCase("hello", "HELLO", {}),
        EvalTestCase("world", "WORLD", {}),
    ]

    dataset = Dataset(
        name="test",
        description="Test dataset",
        node_type="test",
        node_name="simple_node",
        test_cases=test_cases,
    )

    result = run_eval(dataset, simple_node, comparator=case_insensitive_comparator)

    assert result.accuracy() == 1.0
    assert result.all_passed()


def test_run_eval_from_path():
    """Test run_eval_from_path convenience function."""

    def simple_node(input_text, context=None):
        return f"Processed: {input_text}"

    # Create a temporary dataset file
    import tempfile

    test_data = {
        "dataset": {
            "name": "test_dataset",
            "description": "Test dataset",
            "node_type": "test",
            "node_name": "simple_node",
        },
        "test_cases": [
            {
                "input": "hello",
                "expected": "Processed: hello",
                "context": {"user_id": "test"},
            }
        ],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml_service.dump(test_data, f)
        temp_path = f.name

    try:
        result = run_eval_from_path(temp_path, simple_node)
        assert result.accuracy() == 1.0
        assert result.all_passed()
    finally:
        Path(temp_path).unlink()


def test_save_results():
    """Test saving results to different formats."""
    results = [
        EvalTestResult("input1", "expected1", "actual1", True, {}),
        EvalTestResult("input2", "expected2", "actual2", False, {}, "test error"),
    ]

    eval_result = EvalResult(results, "test_dataset")

    # Test CSV save
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        csv_path = f.name

    try:
        eval_result.save_csv(csv_path)
        assert Path(csv_path).exists()
    finally:
        Path(csv_path).unlink()

    # Test JSON save
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json_path = f.name

    try:
        eval_result.save_json(json_path)
        assert Path(json_path).exists()
    finally:
        Path(json_path).unlink()

    # Test Markdown save
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        md_path = f.name

    try:
        eval_result.save_markdown(md_path)
        assert Path(md_path).exists()
    finally:
        Path(md_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__])
