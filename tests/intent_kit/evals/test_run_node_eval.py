"""Tests for run_node_eval module."""

import tempfile
import pathlib
from unittest.mock import patch, MagicMock, mock_open
from intent_kit.evals.run_node_eval import (
    evaluate_node,
    save_raw_results_to_csv,
    calculate_similarity,
    generate_markdown_report,
)
from intent_kit.core.types import ExecutionResult


class MockNode:
    """Mock node for testing."""

    def __init__(self, output="test output"):
        self.output = output

    def execute(self, user_input, context=None):
        return ExecutionResult(
            data=self.output,
            next_edges=None,
            terminate=True,
            metrics={},
            context_patch={},
        )


class TestRunNodeEval:
    """Test cases for run_node_eval module."""

    def test_calculate_similarity(self):
        """Test calculate_similarity function."""
        # Test exact match
        assert calculate_similarity("hello", "hello") == 1.0

        # Test similar strings
        similarity = calculate_similarity("hello world", "hello world!")
        assert 0.8 < similarity < 1.0

        # Test different strings
        similarity = calculate_similarity("hello", "goodbye")
        assert similarity < 0.5

        # Test empty strings
        assert calculate_similarity("", "") == 0.0
        assert calculate_similarity("hello", "") == 0.0
        assert calculate_similarity("", "hello") == 0.0

    def test_save_raw_results_to_csv(self):
        """Test saving raw results to CSV."""
        test_case = {"input": "test input", "expected": "test output", "context": {}}
        actual_output = "test result"
        success = True
        error = None
        similarity_score_val = 0.85

        with patch("intent_kit.evals.run_node_eval.Path") as mock_path:
            # Set up the mock to return a proper string path
            mock_csv_file = MagicMock()
            mock_csv_file.__str__.return_value = "test_dataset_results.csv"
            mock_path.return_value.parent.__truediv__.return_value = mock_csv_file
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False

            with patch("builtins.open", mock_open()):
                csv_file = save_raw_results_to_csv(
                    "test_dataset",
                    test_case,
                    actual_output,
                    success,
                    error,
                    similarity_score_val,
                )

        # Should return the CSV file path as a string
        assert isinstance(csv_file, str)

    def test_evaluate_node_success(self):
        """Test successful node evaluation."""
        mock_node = MagicMock()
        mock_node.execute.return_value = ExecutionResult(
            data="test output",
            next_edges=None,
            terminate=True,
            metrics={},
            context_patch={},
        )

        test_cases = [{"input": "test input", "expected": "test output", "context": {}}]

        with patch(
            "intent_kit.evals.run_node_eval.save_raw_results_to_csv"
        ) as mock_save_csv:
            mock_save_csv.return_value = "test_results.csv"

            result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["dataset"] == "test_dataset"
        assert result["total_cases"] == 1
        assert result["correct"] == 1
        assert result["incorrect"] == 0
        assert result["accuracy"] == 1.0
        assert len(result["errors"]) == 0

    def test_evaluate_node_with_list_output(self):
        """Test node evaluation with list output (splitter)."""
        mock_node = MagicMock()
        mock_node.execute.return_value = ExecutionResult(
            data=["hello", "world"],
            next_edges=None,
            terminate=True,
            metrics={},
            context_patch={},
        )

        test_cases = [
            {"input": "test input", "expected": ["hello", "world"], "context": {}}
        ]

        with patch(
            "intent_kit.evals.run_node_eval.save_raw_results_to_csv"
        ) as mock_save_csv:
            mock_save_csv.return_value = "test_results.csv"

            result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["correct"] == 1
        assert result["incorrect"] == 0
        assert result["accuracy"] == 1.0

    def test_evaluate_node_with_persistent_context(self):
        """Test node evaluation with persistent context."""
        mock_node = MagicMock()
        mock_node.name = "action_node_llm"
        mock_node.execute.return_value = ExecutionResult(
            data="test output",
            next_edges=None,
            terminate=True,
            metrics={},
            context_patch={},
        )

        test_cases = [
            {
                "input": "test input",
                "expected": "test output",
                "context": {"key": "value"},
            }
        ]

        with patch(
            "intent_kit.evals.run_node_eval.save_raw_results_to_csv"
        ) as mock_save_csv:
            mock_save_csv.return_value = "test_results.csv"

            result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["correct"] == 1
        assert result["incorrect"] == 0
        assert result["accuracy"] == 1.0

    def test_evaluate_node_with_incorrect_output(self):
        """Test node evaluation with incorrect output."""
        mock_node = MagicMock()
        mock_node.execute.return_value = ExecutionResult(
            data="wrong output",
            next_edges=None,
            terminate=True,
            metrics={},
            context_patch={},
        )

        test_cases = [
            {"input": "test input", "expected": "correct output", "context": {}}
        ]

        with patch(
            "intent_kit.evals.run_node_eval.save_raw_results_to_csv"
        ) as mock_save_csv:
            mock_save_csv.return_value = "test_results.csv"

            result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["correct"] == 0
        assert result["incorrect"] == 1
        assert result["accuracy"] == 0.0
        assert len(result["errors"]) == 1
        assert result["errors"][0]["type"] == "incorrect_output"

    def test_evaluate_node_with_exception(self):
        """Test node evaluation with exception."""
        mock_node = MagicMock()
        mock_node.execute.side_effect = Exception("Test error")

        test_cases = [{"input": "test input", "expected": "test output", "context": {}}]

        with patch(
            "intent_kit.evals.run_node_eval.save_raw_results_to_csv"
        ) as mock_save_csv:
            mock_save_csv.return_value = "test_results.csv"

            result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["correct"] == 0
        assert result["incorrect"] == 1
        assert result["accuracy"] == 0.0
        assert len(result["errors"]) == 1
        assert result["errors"][0]["type"] == "exception"
        assert "Test error" in result["errors"][0]["error"]

    def test_evaluate_node_with_no_output(self):
        """Test node evaluation with no output."""
        mock_node = MagicMock()
        mock_node.execute.return_value = ExecutionResult(
            data=None, next_edges=None, terminate=True, metrics={}, context_patch={}
        )

        test_cases = [{"input": "test input", "expected": "test output", "context": {}}]

        with patch(
            "intent_kit.evals.run_node_eval.save_raw_results_to_csv"
        ) as mock_save_csv:
            mock_save_csv.return_value = "test_results.csv"

            result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["correct"] == 0
        assert result["incorrect"] == 1
        assert result["accuracy"] == 0.0
        assert len(result["errors"]) == 1
        assert result["errors"][0]["type"] == "no_output"

    def test_evaluate_node_with_numeric_comparison(self):
        """Test node evaluation with numeric values."""
        mock_node = MagicMock()
        mock_node.execute.return_value = ExecutionResult(
            data=42.0, next_edges=None, terminate=True, metrics={}, context_patch={}
        )

        test_cases = [{"input": "test input", "expected": 42, "context": {}}]

        with patch(
            "intent_kit.evals.run_node_eval.save_raw_results_to_csv"
        ) as mock_save_csv:
            mock_save_csv.return_value = "test_results.csv"

            result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["correct"] == 1
        assert result["incorrect"] == 0
        assert result["accuracy"] == 1.0

    def test_evaluate_node_with_callable_node(self):
        """Test node evaluation with callable node."""

        def callable_node(user_input, context=None):
            return ExecutionResult(
                data="callable output",
                next_edges=None,
                terminate=True,
                metrics={},
                context_patch={},
            )

        test_cases = [
            {"input": "test input", "expected": "callable output", "context": {}}
        ]

        with patch(
            "intent_kit.evals.run_node_eval.save_raw_results_to_csv"
        ) as mock_save_csv:
            mock_save_csv.return_value = "test_results.csv"

            result = evaluate_node(callable_node, test_cases, "test_dataset")

        assert result["correct"] == 1
        assert result["incorrect"] == 0
        assert result["accuracy"] == 1.0

    def test_evaluate_node_with_invalid_node(self):
        """Test node evaluation with invalid node."""
        invalid_node = "not a node"

        test_cases = [{"input": "test input", "expected": "test output", "context": {}}]

        with patch(
            "intent_kit.evals.run_node_eval.save_raw_results_to_csv"
        ) as mock_save_csv:
            mock_save_csv.return_value = "test_results.csv"

            result = evaluate_node(invalid_node, test_cases, "test_dataset")

        assert result["correct"] == 0
        assert result["incorrect"] == 1
        assert result["accuracy"] == 0.0
        assert len(result["errors"]) == 1
        assert result["errors"][0]["type"] == "exception"

    def test_generate_markdown_report(self):
        """Test generate_markdown_report function."""
        results = [
            {
                "dataset": "test_dataset",
                "total_cases": 10,
                "correct": 8,
                "incorrect": 2,
                "accuracy": 0.8,
                "errors": [
                    {
                        "case": 1,
                        "input": "test input",
                        "expected": "expected output",
                        "actual": "actual output",
                        "type": "incorrect_output",
                    }
                ],
                "raw_results_file": "test_results.csv",
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as tmp_file:
            output_file = tmp_file.name

        try:
            generate_markdown_report(
                results,
                pathlib.Path(output_file),
                run_timestamp="2024-01-01_12-00-00",
                mock_mode=False,
            )

            # Check that file was created
            assert pathlib.Path(output_file).exists()

            # Read the content to verify it's correct
            with open(output_file, "r") as f:
                content = f.read()
                assert "test_dataset" in content
                assert "80.0%" in content
                assert "**Total Test Cases**: 10" in content

        finally:
            pathlib.Path(output_file).unlink(missing_ok=True)

    def test_generate_markdown_report_mock_mode(self):
        """Test generate_markdown_report in mock mode."""
        results = [
            {
                "dataset": "test_dataset",
                "total_cases": 5,
                "correct": 5,
                "incorrect": 0,
                "accuracy": 1.0,
                "errors": [],
                "raw_results_file": "test_results.csv",
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as tmp_file:
            output_file = tmp_file.name

        try:
            generate_markdown_report(
                results,
                pathlib.Path(output_file),
                run_timestamp="2024-01-01_12-00-00",
                mock_mode=True,
            )

            # Check that file was created
            assert pathlib.Path(output_file).exists()

            # Read the content to verify mock mode indicator is present
            with open(output_file, "r") as f:
                content = f.read()
                assert "(MOCK MODE)" in content
                assert "Mock (simulated responses)" in content

        finally:
            pathlib.Path(output_file).unlink(missing_ok=True)
