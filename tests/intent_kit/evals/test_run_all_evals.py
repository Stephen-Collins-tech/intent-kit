"""
Tests for run_all_evals module.
"""

import pytest
import tempfile
import pathlib
from unittest.mock import patch, MagicMock, mock_open
from intent_kit.evals.run_all_evals import (
    run_all_evaluations,
    run_all_evaluations_internal,
    generate_comprehensive_report,
)


class TestRunAllEvals:
    """Test cases for run_all_evals module."""

    @patch("intent_kit.evals.run_all_evals.argparse.ArgumentParser")
    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    @patch("intent_kit.evals.run_all_evals.run_all_evaluations_internal")
    @patch("intent_kit.evals.run_all_evals.generate_comprehensive_report")
    def test_run_all_evaluations_success(self, mock_generate_report, mock_run_internal, mock_path, mock_parser):
        """Test successful execution of run_all_evaluations."""
        # Mock argument parser
        mock_args = MagicMock()
        mock_args.output = "test_output.md"
        mock_args.individual = True
        mock_args.quiet = False
        mock_args.llm_config = None
        mock_args.mock = False
        mock_parser.return_value.parse_args.return_value = mock_args

        # Mock path operations
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.parent = MagicMock()
        mock_path_instance.parent.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_instance.mkdir.return_value = None

        # Mock internal function
        mock_run_internal.return_value = [
            {"dataset": "test_dataset", "accuracy": 0.85, "correct": 17, "total_cases": 20}
        ]

        # Mock generate report
        mock_generate_report.return_value = "test_report.md"

        # Mock file operations
        with patch("builtins.open", mock_open()) as mock_file:
            result = run_all_evaluations()

        assert result is True
        mock_run_internal.assert_called_once_with(None, mock_mode=False)
        mock_generate_report.assert_called_once()

    @patch("intent_kit.evals.run_all_evals.argparse.ArgumentParser")
    def test_run_all_evaluations_system_exit(self, mock_parser):
        """Test run_all_evaluations when called as function (SystemExit)."""
        # Mock SystemExit to simulate function call
        mock_parser.return_value.parse_args.side_effect = SystemExit()

        with patch("intent_kit.evals.run_all_evals.run_all_evaluations_internal") as mock_internal:
            with patch("intent_kit.evals.run_all_evals.generate_comprehensive_report"):
                with patch("intent_kit.evals.run_all_evals.pathlib.Path"):
                    with patch("builtins.open", mock_open()):
                        result = run_all_evaluations()

        assert result is True
        mock_internal.assert_called_once()

    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    @patch("intent_kit.evals.run_all_evals.load_dataset")
    @patch("intent_kit.evals.run_all_evals.get_node_from_module")
    @patch("intent_kit.evals.run_all_evals.evaluate_node")
    def test_run_all_evaluations_internal_success(self, mock_evaluate, mock_get_node, mock_load_dataset, mock_path):
        """Test successful execution of run_all_evaluations_internal."""
        # Mock dataset directory
        mock_dataset_dir = MagicMock()
        mock_dataset_dir.glob.return_value = [
            pathlib.Path("test_dataset.yaml")
        ]
        mock_path.return_value.parent.__truediv__.return_value = mock_dataset_dir

        # Mock dataset loading
        mock_dataset = MagicMock()
        mock_dataset.name = "test_dataset"
        mock_dataset.node_name = "action_node_llm"
        mock_dataset.test_cases = [
            MagicMock(input="test input", expected="test output", context={})
        ]
        mock_load_dataset.return_value = mock_dataset

        # Mock node loading
        mock_node = MagicMock()
        mock_get_node.return_value = mock_node

        # Mock evaluation
        mock_evaluate.return_value = {
            "dataset": "test_dataset",
            "accuracy": 0.85,
            "correct": 17,
            "total_cases": 20
        }

        # Mock environment
        with patch.dict("os.environ", {}, clear=True):
            results = run_all_evaluations_internal()

        assert len(results) == 1
        assert results[0]["dataset"] == "test_dataset"
        assert results[0]["accuracy"] == 0.85

    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    @patch("intent_kit.evals.run_all_evals.load_dataset")
    @patch("intent_kit.evals.run_all_evals.get_node_from_module")
    def test_run_all_evaluations_internal_with_llm_config(self, mock_get_node, mock_load_dataset, mock_path):
        """Test run_all_evaluations_internal with LLM configuration."""
        # Mock dataset directory
        mock_dataset_dir = MagicMock()
        mock_dataset_dir.glob.return_value = []
        mock_path.return_value.parent.__truediv__.return_value = mock_dataset_dir

        # Mock LLM config file
        llm_config = {
            "openai": {"api_key": "test_key"},
            "anthropic": {"api_key": "test_key_2"}
        }

        with patch("builtins.open", mock_open(read_data="openai:\n  api_key: test_key\nanthropic:\n  api_key: test_key_2")):
            with patch("yaml.safe_load", return_value=llm_config):
                with patch("os.environ", {}) as mock_env:
                    results = run_all_evaluations_internal("test_config.yaml")

        assert len(results) == 0
        assert mock_env["OPENAI_API_KEY"] == "test_key"
        assert mock_env["ANTHROPIC_API_KEY"] == "test_key_2"

    @patch("intent_kit.evals.run_all_evals.pathlib.Path")
    def test_run_all_evaluations_internal_mock_mode(self, mock_path):
        """Test run_all_evaluations_internal in mock mode."""
        # Mock dataset directory
        mock_dataset_dir = MagicMock()
        mock_dataset_dir.glob.return_value = []
        mock_path.return_value.parent.__truediv__.return_value = mock_dataset_dir

        with patch("os.environ", {}) as mock_env:
            results = run_all_evaluations_internal(mock_mode=True)

        assert len(results) == 0
        assert mock_env["INTENT_KIT_MOCK_MODE"] == "1"

    def test_generate_comprehensive_report(self):
        """Test generate_comprehensive_report function."""
        results = [
            {"dataset": "test1", "accuracy": 0.85, "correct": 17, "total_cases": 20},
            {"dataset": "test2", "accuracy": 0.90, "correct": 18, "total_cases": 20}
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp_file:
            output_file = tmp_file.name

        try:
            report_path = generate_comprehensive_report(
                results, output_file, run_timestamp="2024-01-01_12-00-00", mock_mode=False
            )

            # Check that file was created
            assert pathlib.Path(output_file).exists()
            assert report_path == output_file

            # Check file contents
            with open(output_file, "r") as f:
                content = f.read()
                assert "Comprehensive Evaluation Report" in content
                assert "test1" in content
                assert "test2" in content
                assert "85.0%" in content
                assert "90.0%" in content

        finally:
            pathlib.Path(output_file).unlink(missing_ok=True)

    def test_generate_comprehensive_report_mock_mode(self):
        """Test generate_comprehensive_report in mock mode."""
        results = [
            {"dataset": "test1", "accuracy": 0.85, "correct": 17, "total_cases": 20}
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp_file:
            output_file = tmp_file.name

        try:
            report_path = generate_comprehensive_report(
                results, output_file, run_timestamp="2024-01-01_12-00-00", mock_mode=True
            )

            # Check file contents for mock mode indicator
            with open(output_file, "r") as f:
                content = f.read()
                assert "MOCK MODE" in content

        finally:
            pathlib.Path(output_file).unlink(missing_ok=True)

    def test_generate_comprehensive_report_no_results(self):
        """Test generate_comprehensive_report with no results."""
        results = []

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp_file:
            output_file = tmp_file.name

        try:
            report_path = generate_comprehensive_report(results, output_file)

            # Check that file was created even with no results
            assert pathlib.Path(output_file).exists()
            assert report_path == output_file

        finally:
            pathlib.Path(output_file).unlink(missing_ok=True)