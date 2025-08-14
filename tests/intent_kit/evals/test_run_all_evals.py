"""Tests for run_all_evals module."""

import tempfile
import pathlib
from unittest.mock import patch, MagicMock, mock_open
from intent_kit.evals.run_all_evals import (
    run_all_evaluations_internal,
    generate_comprehensive_report,
    create_node_for_dataset,
    run_all_evaluations,
    create_test_action,
    create_test_classifier,
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

    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_internal_with_llm_config(self, mock_path):
        """Test run_all_evaluations_internal with LLM configuration."""
        # Mock dataset directory
        mock_dataset_dir = MagicMock()
        mock_dataset_dir.glob.return_value = []
        mock_path.return_value.parent.__truediv__.return_value = mock_dataset_dir

        # Create a temporary LLM config file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as tmp_file:
            tmp_file.write("openai:\n  api_key: test_key\n")
            llm_config_path = tmp_file.name

        try:
            with patch("os.environ", {}):
                results = run_all_evaluations_internal(
                    llm_config_path=llm_config_path, mock_mode=True
                )

            assert len(results) == 0
        finally:
            pathlib.Path(llm_config_path).unlink(missing_ok=True)

    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_internal_datasets_not_found(self, mock_path):
        """Test run_all_evaluations_internal when datasets directory doesn't exist."""
        # Mock dataset directory to not exist
        mock_dataset_dir = MagicMock()
        mock_dataset_dir.exists.return_value = False
        mock_path.return_value.parent.__truediv__.return_value = mock_dataset_dir

        with patch("builtins.print") as mock_print:
            results = run_all_evaluations_internal(mock_mode=True)

        assert len(results) == 0
        mock_print.assert_called_once()
        assert "Datasets directory not found" in mock_print.call_args[0][0]

    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_internal_no_dataset_files(self, mock_path):
        """Test run_all_evaluations_internal when no dataset files are found."""
        # Mock dataset directory with no files
        mock_dataset_dir = MagicMock()
        mock_dataset_dir.exists.return_value = True
        mock_dataset_dir.glob.return_value = []
        mock_path.return_value.parent.__truediv__.return_value = mock_dataset_dir

        with patch("builtins.print") as mock_print:
            results = run_all_evaluations_internal(mock_mode=True)

        assert len(results) == 0
        mock_print.assert_called_once()
        assert "No dataset files found" in mock_print.call_args[0][0]

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

    def test_generate_comprehensive_report_with_multiple_errors(self):
        """Test generate_comprehensive_report with multiple errors."""
        results = [
            {
                "dataset": "test_with_multiple_errors",
                "accuracy": 0.30,
                "correct": 3,
                "total_cases": 10,
                "incorrect": 7,
                "errors": [
                    {
                        "case": 1,
                        "input": "test input 1",
                        "expected": "expected output 1",
                        "actual": "actual output 1",
                        "error": "Test error message 1",
                        "type": "evaluation_error",
                    },
                    {
                        "case": 2,
                        "input": "test input 2",
                        "expected": "expected output 2",
                        "actual": "actual output 2",
                        "error": "Test error message 2",
                        "type": "evaluation_error",
                    },
                    {
                        "case": 3,
                        "input": "test input 3",
                        "expected": "expected output 3",
                        "actual": "actual output 3",
                        "error": "Test error message 3",
                        "type": "evaluation_error",
                    },
                    {
                        "case": 4,
                        "input": "test input 4",
                        "expected": "expected output 4",
                        "actual": "actual output 4",
                        "error": "Test error message 4",
                        "type": "evaluation_error",
                    },
                    {
                        "case": 5,
                        "input": "test input 5",
                        "expected": "expected output 5",
                        "actual": "actual output 5",
                        "error": "Test error message 5",
                        "type": "evaluation_error",
                    },
                    {
                        "case": 6,
                        "input": "test input 6",
                        "expected": "expected output 6",
                        "actual": "actual output 6",
                        "error": "Test error message 6",
                        "type": "evaluation_error",
                    },
                ],
                "raw_results_file": "test_with_multiple_errors_results.csv",
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
                assert "test_with_multiple_errors" in content
                assert "30.0%" in content
                assert "Test error message 1" in content
                assert "Test error message 2" in content
                assert "Test error message 3" in content
                assert "Test error message 4" in content
                assert "Test error message 5" in content
                assert "and 1 more errors" in content

        finally:
            pathlib.Path(output_file).unlink(missing_ok=True)

    def test_generate_comprehensive_report_with_timestamp(self):
        """Test generate_comprehensive_report with timestamp."""
        results = [
            {
                "dataset": "test_timestamp",
                "accuracy": 0.75,
                "correct": 15,
                "total_cases": 20,
                "incorrect": 5,
                "errors": [],
                "raw_results_file": "test_timestamp_results.csv",
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

            # Read the content to verify report was generated
            with open(output_file, "r") as f:
                content = f.read()
                assert "Comprehensive Node Evaluation Report" in content
                assert "test_timestamp" in content

        finally:
            pathlib.Path(output_file).unlink(missing_ok=True)


class TestTestFunctions:
    """Test cases for test helper functions."""

    def test_create_test_action(self):
        """Test create_test_action function."""
        result = create_test_action("Paris", "2024-01-15", 12345)
        assert result == "Flight booked to Paris for 2024-01-15 (Booking #12345)"

    def test_create_test_action_different_parameters(self):
        """Test create_test_action with different parameters."""
        result = create_test_action("Tokyo", "2024-12-31", 99999)
        assert result == "Flight booked to Tokyo for 2024-12-31 (Booking #99999)"

    def test_create_test_classifier_weather(self):
        """Test create_test_classifier with weather keywords."""
        ctx = {}  # Mock context
        result = create_test_classifier("What's the weather like today?", ctx)
        assert result == "weather"

    def test_create_test_classifier_temperature(self):
        """Test create_test_classifier with temperature keyword."""
        ctx = {}
        result = create_test_classifier("What's the temperature?", ctx)
        assert result == "weather"

    def test_create_test_classifier_forecast(self):
        """Test create_test_classifier with forecast keyword."""
        ctx = {}
        result = create_test_classifier("Show me the forecast", ctx)
        assert result == "weather"

    def test_create_test_classifier_cancel(self):
        """Test create_test_classifier with cancel keywords."""
        ctx = {}
        result = create_test_classifier("I want to cancel my booking", ctx)
        assert result == "cancel"

    def test_create_test_classifier_cancellation(self):
        """Test create_test_classifier with cancellation keyword."""
        ctx = {}
        result = create_test_classifier("How do I request a cancellation?", ctx)
        assert result == "cancel"

    def test_create_test_classifier_canceled(self):
        """Test create_test_classifier with canceled keyword."""
        ctx = {}
        result = create_test_classifier("My flight was canceled", ctx)
        assert result == "cancel"

    def test_create_test_classifier_cancelled(self):
        """Test create_test_classifier with cancelled keyword."""
        ctx = {}
        result = create_test_classifier("My flight was cancelled", ctx)
        assert result == "cancel"

    def test_create_test_classifier_unknown(self):
        """Test create_test_classifier with unknown input."""
        ctx = {}
        result = create_test_classifier("Hello, how are you?", ctx)
        assert result == "unknown"

    def test_create_test_classifier_case_insensitive(self):
        """Test create_test_classifier is case insensitive."""
        ctx = {}
        result = create_test_classifier("WEATHER today", ctx)
        assert result == "weather"

        result = create_test_classifier("CANCEL booking", ctx)
        assert result == "cancel"


class TestRunAllEvaluations:
    """Test cases for the main run_all_evaluations function."""

    @patch("intent_kit.evals.run_all_evals.run_all_evaluations_internal")
    @patch("intent_kit.evals.run_all_evals.generate_comprehensive_report")
    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_success(
        self, mock_path, mock_generate_report, mock_run_internal
    ):
        """Test run_all_evaluations with successful execution."""
        # Mock the internal function
        mock_run_internal.return_value = [
            {
                "dataset": "test1",
                "accuracy": 0.85,
                "correct": 17,
                "total_cases": 20,
                "incorrect": 3,
                "errors": [],
                "raw_results_file": "test1_results.csv",
            }
        ]

        # Mock path operations
        mock_reports_dir = MagicMock()
        mock_date_reports_dir = MagicMock()
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = (
            mock_reports_dir
        )
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = (
            mock_date_reports_dir
        )

        # Mock argument parser
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.output = "intent_kit/evals/reports/latest/comprehensive_report.md"
            mock_args.individual = False
            mock_args.quiet = False
            mock_args.llm_config = None
            mock_args.mock = False
            mock_parse_args.return_value = mock_args

            # Mock file operations
            with patch("builtins.open", mock_open()):
                with patch("builtins.print") as mock_print:
                    result = run_all_evaluations()

                    assert result is True
                    mock_run_internal.assert_called_once_with(None, mock_mode=False)
                    mock_generate_report.assert_called()
                    mock_print.assert_called()

    @patch("intent_kit.evals.run_all_evals.run_all_evaluations_internal")
    @patch("intent_kit.evals.run_all_evals.generate_comprehensive_report")
    @patch("intent_kit.evals.run_all_evals.generate_markdown_report")
    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_with_individual_reports(
        self, mock_path, mock_generate_markdown, mock_generate_report, mock_run_internal
    ):
        """Test run_all_evaluations with individual reports enabled."""
        # Mock the internal function
        mock_run_internal.return_value = [
            {
                "dataset": "test1",
                "accuracy": 0.85,
                "correct": 17,
                "total_cases": 20,
                "incorrect": 3,
                "errors": [],
                "raw_results_file": "test1_results.csv",
            }
        ]

        # Mock path operations
        mock_reports_dir = MagicMock()
        mock_date_reports_dir = MagicMock()
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = (
            mock_reports_dir
        )
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = (
            mock_date_reports_dir
        )

        # Mock argument parser
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.output = "intent_kit/evals/reports/latest/comprehensive_report.md"
            mock_args.individual = True
            mock_args.quiet = False
            mock_args.llm_config = None
            mock_args.mock = False
            mock_parse_args.return_value = mock_args

            # Mock file operations
            with patch("builtins.open", mock_open()):
                with patch("builtins.print") as mock_print:
                    result = run_all_evaluations()

                    assert result is True
                    mock_run_internal.assert_called_once_with(None, mock_mode=False)
                    mock_generate_report.assert_called()
                    mock_generate_markdown.assert_called()
                    mock_print.assert_called()

    @patch("intent_kit.evals.run_all_evals.run_all_evaluations_internal")
    @patch("intent_kit.evals.run_all_evals.generate_comprehensive_report")
    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_quiet_mode(
        self, mock_path, mock_generate_report, mock_run_internal
    ):
        """Test run_all_evaluations in quiet mode."""
        # Mock the internal function
        mock_run_internal.return_value = []

        # Mock path operations
        mock_reports_dir = MagicMock()
        mock_date_reports_dir = MagicMock()
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = (
            mock_reports_dir
        )
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = (
            mock_date_reports_dir
        )

        # Mock argument parser
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.output = "intent_kit/evals/reports/latest/comprehensive_report.md"
            mock_args.individual = False
            mock_args.quiet = True
            mock_args.llm_config = None
            mock_args.mock = False
            mock_parse_args.return_value = mock_args

            # Mock file operations
            with patch("builtins.open", mock_open()):
                with patch("builtins.print") as mock_print:
                    result = run_all_evaluations()

                    assert result is True
                    mock_run_internal.assert_called_once_with(None, mock_mode=False)
                    mock_generate_report.assert_called()
                    # Should not print in quiet mode
                    mock_print.assert_not_called()

    @patch("intent_kit.evals.run_all_evals.run_all_evaluations_internal")
    @patch("intent_kit.evals.run_all_evals.generate_comprehensive_report")
    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_mock_mode(
        self, mock_path, mock_generate_report, mock_run_internal
    ):
        """Test run_all_evaluations in mock mode."""
        # Mock the internal function
        mock_run_internal.return_value = []

        # Mock path operations
        mock_reports_dir = MagicMock()
        mock_date_reports_dir = MagicMock()
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = (
            mock_reports_dir
        )
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = (
            mock_date_reports_dir
        )

        # Mock argument parser
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.output = "intent_kit/evals/reports/latest/comprehensive_report.md"
            mock_args.individual = False
            mock_args.quiet = False
            mock_args.llm_config = None
            mock_args.mock = True
            mock_parse_args.return_value = mock_args

            # Mock file operations
            with patch("builtins.open", mock_open()):
                with patch("builtins.print") as mock_print:
                    result = run_all_evaluations()

                    assert result is True
                    mock_run_internal.assert_called_once_with(None, mock_mode=True)
                    mock_generate_report.assert_called()
                    mock_print.assert_called()
                    # Check that mock mode was mentioned in print calls
                    mock_print.assert_any_call(
                        "Running all evaluations in MOCK mode..."
                    )

    @patch("intent_kit.evals.run_all_evals.run_all_evaluations_internal")
    @patch("intent_kit.evals.run_all_evals.generate_comprehensive_report")
    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_with_llm_config(
        self, mock_path, mock_generate_report, mock_run_internal
    ):
        """Test run_all_evaluations with LLM configuration."""
        # Mock the internal function
        mock_run_internal.return_value = []

        # Mock path operations
        mock_reports_dir = MagicMock()
        mock_date_reports_dir = MagicMock()
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = (
            mock_reports_dir
        )
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = (
            mock_date_reports_dir
        )

        # Mock argument parser
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.output = "intent_kit/evals/reports/latest/comprehensive_report.md"
            mock_args.individual = False
            mock_args.quiet = False
            mock_args.llm_config = "config.yaml"
            mock_args.mock = False
            mock_parse_args.return_value = mock_args

            # Mock file operations
            with patch("builtins.open", mock_open()):
                with patch("builtins.print") as mock_print:
                    result = run_all_evaluations()

                    assert result is True
                    mock_run_internal.assert_called_once_with(
                        "config.yaml", mock_mode=False
                    )
                    mock_generate_report.assert_called()
                    mock_print.assert_called()

    @patch("intent_kit.evals.run_all_evals.run_all_evaluations_internal")
    @patch("intent_kit.evals.run_all_evals.generate_comprehensive_report")
    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_custom_output_path(
        self, mock_path, mock_generate_report, mock_run_internal
    ):
        """Test run_all_evaluations with custom output path."""
        # Mock the internal function
        mock_run_internal.return_value = []

        # Mock path operations
        mock_reports_dir = MagicMock()
        mock_date_reports_dir = MagicMock()
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = (
            mock_reports_dir
        )
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = (
            mock_date_reports_dir
        )

        # Mock argument parser
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.output = "custom_report.md"
            mock_args.individual = False
            mock_args.quiet = False
            mock_args.llm_config = None
            mock_args.mock = False
            mock_parse_args.return_value = mock_args

            # Mock file operations
            with patch("builtins.open", mock_open()):
                with patch("builtins.print") as mock_print:
                    result = run_all_evaluations()

                    assert result is True
                    mock_run_internal.assert_called_once_with(None, mock_mode=False)
                    mock_generate_report.assert_called()
                    mock_print.assert_called()
