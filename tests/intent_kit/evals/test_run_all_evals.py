"""Tests for run_all_evals module."""

import tempfile
import pathlib
from unittest.mock import patch, MagicMock
from intent_kit.evals.run_all_evals import (
    run_all_evaluations_internal,
    generate_comprehensive_report,
    create_node_for_dataset,
)


class TestRunAllEvals:
    """Test cases for run_all_evals module."""

    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_internal_success(self, mock_path):
        """Test run_all_evaluations_internal with successful evaluations."""
        # Mock dataset directory
        mock_dataset_dir = MagicMock()
        mock_dataset_dir.glob.return_value = []
        mock_path.return_value.parent.__truediv__.return_value = mock_dataset_dir

        results = run_all_evaluations_internal(mock_mode=True)

        assert len(results) == 0  # No dataset files found

    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_internal_mock_mode(self, mock_path):
        """Test run_all_evaluations_internal in mock mode."""
        # Mock dataset directory
        mock_dataset_dir = MagicMock()
        mock_dataset_dir.glob.return_value = []
        mock_path.return_value.parent.__truediv__.return_value = mock_dataset_dir

        with patch("os.environ", {}):
            results = run_all_evaluations_internal(mock_mode=True)

        assert len(results) == 0
        # Note: The function doesn't actually set INTENT_KIT_MOCK_MODE in the environment
        # It just runs in mock mode internally

    def test_generate_comprehensive_report(self):
        """Test generate_comprehensive_report function."""
        results = [
            {
                "dataset": "test1",
                "accuracy": 0.85,
                "correct": 17,
                "total_cases": 20,
                "incorrect": 3,  # Add the missing field
                "errors": [],
                "raw_results_file": "test1_results.csv",
            },
            {
                "dataset": "test2",
                "accuracy": 0.90,
                "correct": 18,
                "total_cases": 20,
                "incorrect": 2,  # Add the missing field
                "errors": [],
                "raw_results_file": "test2_results.csv",
            },
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as tmp_file:
            output_file = tmp_file.name

        try:
            generate_comprehensive_report(
                results,
                output_file,
                run_timestamp="2024-01-01_12-00-00",
                mock_mode=False,
            )

            # Check that file was created
            assert pathlib.Path(output_file).exists()

            # Read the content to verify it's correct
            with open(output_file, "r") as f:
                content = f.read()
                assert "test1" in content
                assert "test2" in content
                assert "85.0%" in content
                assert "90.0%" in content

        finally:
            pathlib.Path(output_file).unlink(missing_ok=True)

    def test_generate_comprehensive_report_mock_mode(self):
        """Test generate_comprehensive_report in mock mode."""
        results = [
            {
                "dataset": "test1",
                "accuracy": 0.85,
                "correct": 17,
                "total_cases": 20,
                "incorrect": 3,  # Add the missing field
                "errors": [],
                "raw_results_file": "test1_results.csv",
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as tmp_file:
            output_file = tmp_file.name

        try:
            generate_comprehensive_report(
                results,
                output_file,
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

    def test_generate_comprehensive_report_no_results(self):
        """Test generate_comprehensive_report with no results."""
        results = []

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as tmp_file:
            output_file = tmp_file.name

        try:
            generate_comprehensive_report(results, output_file)

            # Check that file was created even with no results
            assert pathlib.Path(output_file).exists()

            # Read the content to verify it handles empty results
            with open(output_file, "r") as f:
                content = f.read()
                assert "**Total Test Cases**: 0" in content
                assert "Overall Accuracy**: 0.0%" in content

        finally:
            pathlib.Path(output_file).unlink(missing_ok=True)

    def test_create_node_for_dataset_action(self):
        """Test create_node_for_dataset with action node type."""
        node = create_node_for_dataset("test_dataset", "action", "test_action")
        assert node is not None
        assert hasattr(node, "execute")
        assert node.name == "test_action"

    def test_create_node_for_dataset_classifier(self):
        """Test create_node_for_dataset with classifier node type."""
        node = create_node_for_dataset("test_dataset", "classifier", "test_classifier")
        assert node is not None
        assert hasattr(node, "execute")
        assert node.name == "test_classifier"

    def test_create_node_for_dataset_unknown_type(self):
        """Test create_node_for_dataset with unknown node type."""
        node = create_node_for_dataset("test_dataset", "unknown", "test_node")
        # Should return None for unknown types
        assert node is None

    def test_generate_comprehensive_report_with_errors(self):
        """Test generate_comprehensive_report with error results."""
        results = [
            {
                "dataset": "test_with_errors",
                "accuracy": 0.50,
                "correct": 5,
                "total_cases": 10,
                "incorrect": 5,  # Add the missing field
                "errors": [
                    {
                        "case": 1,
                        "input": "test input",
                        "expected": "expected output",
                        "actual": "actual output",
                        "error": "Test error message",
                        "type": "evaluation_error",
                    }
                ],
                "raw_results_file": "test_with_errors_results.csv",
            }
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as tmp_file:
            output_file = tmp_file.name

        try:
            generate_comprehensive_report(
                results,
                output_file,
                run_timestamp="2024-01-01_12-00-00",
                mock_mode=False,
            )

            # Check that file was created
            assert pathlib.Path(output_file).exists()

            # Read the content to verify error information is included
            with open(output_file, "r") as f:
                content = f.read()
                assert "test_with_errors" in content
                assert "50.0%" in content
                assert "Test error message" in content

        finally:
            pathlib.Path(output_file).unlink(missing_ok=True)
