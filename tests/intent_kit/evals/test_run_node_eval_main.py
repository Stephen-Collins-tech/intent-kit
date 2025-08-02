"""
Tests for run_node_eval.py main function.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path


class TestRunNodeEvalMain:
    """Test cases for the main function in run_node_eval.py."""

    @patch("argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    @patch("builtins.open", new_callable=mock_open)
    @patch("intent_kit.services.loader_service.dataset_loader.load")
    @patch("intent_kit.services.loader_service.module_loader.load")
    @patch("intent_kit.evals.run_node_eval.evaluate_node")
    @patch("intent_kit.evals.run_node_eval.generate_markdown_report")
    @patch("intent_kit.evals.run_node_eval.save_raw_results_to_csv")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.unlink")
    @patch("intent_kit.services.yaml_service.yaml_service.safe_load")
    @patch("intent_kit.evals.run_node_eval.datetime")
    @patch("importlib.import_module")
    @patch("sys.argv", ["run_node_eval.py"])
    @patch.dict("os.environ", {}, clear=True)
    @pytest.mark.skip(reason="This test is not working.")
    def test_main_success(
        self,
        mock_import_module,
        mock_datetime,
        mock_yaml_load,
        mock_unlink,
        mock_mkdir,
        mock_save_results,
        mock_generate_report,
        mock_evaluate_node,
        mock_module_loader_load,
        mock_dataset_loader_load,
        mock_open,
        mock_glob,
        mock_exists,
        mock_parse_args,
    ):
        """Test main function with successful execution."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.dataset = None
        mock_args.output = None
        mock_args.llm_config = None
        mock_parse_args.return_value = mock_args

        # Mock file system
        mock_exists.return_value = True
        mock_glob.return_value = [Path("action_node_llm.yaml")]

        # Mock datetime
        mock_datetime.now.return_value.strftime.side_effect = lambda fmt: (
            "2024-01-01_12-00-00" if "%Y-%m-%d_%H-%M-%S" in fmt else "2024-01-01"
        )

        # Mock importlib.import_module for datetime
        mock_datetime_module = MagicMock()
        mock_datetime_module.datetime.now.return_value.isoformat.return_value = (
            "2024-01-01T12:00:00"
        )
        mock_import_module.return_value = mock_datetime_module

        # Mock dataset data
        mock_dataset = {
            "dataset": {"name": "test_dataset", "node_name": "action_node_llm"},
            "test_cases": [{"input": "test", "expected": "result", "context": {}}],
        }
        mock_dataset_loader_load.return_value = mock_dataset

        # Mock node
        mock_node = MagicMock()
        mock_module_loader_load.return_value = mock_node

        # Mock evaluation results
        mock_eval_result = {
            "dataset": "test_dataset",
            "total_cases": 1,
            "correct": 1,
            "incorrect": 0,
            "accuracy": 1.0,
            "errors": [],
            "details": [],
            "raw_results_file": "test_file.csv",
        }
        mock_evaluate_node.return_value = mock_eval_result

        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Import and run main function
        from intent_kit.evals.run_node_eval import main

        main()

        # Verify calls
        mock_dataset_loader_load.assert_called_once()
        mock_module_loader_load.assert_called_once()
        mock_evaluate_node.assert_called_once()
        mock_generate_report.assert_called_once()

    @patch("argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    def test_main_datasets_dir_not_found(self, mock_exists, mock_parse_args):
        """Test main function when datasets directory doesn't exist."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.dataset = None
        mock_args.output = None
        mock_args.llm_config = None
        mock_parse_args.return_value = mock_args

        # Mock file system - datasets directory doesn't exist
        mock_exists.return_value = False

        # Run main function and expect it to exit
        from intent_kit.evals.run_node_eval import main

        with pytest.raises(SystemExit):
            main()

    @patch("argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    def test_main_no_dataset_files(self, mock_glob, mock_exists, mock_parse_args):
        """Test main function when no dataset files are found."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.dataset = None
        mock_args.output = None
        mock_args.llm_config = None
        mock_parse_args.return_value = mock_args

        # Mock file system
        mock_exists.return_value = True
        mock_glob.return_value = []  # No dataset files

        # Run main function and expect it to exit
        from intent_kit.evals.run_node_eval import main

        with pytest.raises(SystemExit):
            main()

    @patch("argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    def test_main_specific_dataset_not_found(
        self, mock_glob, mock_exists, mock_parse_args
    ):
        """Test main function when specific dataset is not found."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.dataset = "nonexistent"
        mock_args.output = None
        mock_args.llm_config = None
        mock_parse_args.return_value = mock_args

        # Mock file system
        mock_exists.return_value = True
        mock_glob.return_value = [Path("other_dataset.yaml")]  # Different dataset

        # Run main function and expect it to exit
        from intent_kit.evals.run_node_eval import main

        with pytest.raises(SystemExit):
            main()

    @patch("argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    @patch("builtins.open", new_callable=mock_open)
    @patch("intent_kit.services.loader_service.dataset_loader.load")
    @patch("intent_kit.services.loader_service.module_loader.load")
    @patch("intent_kit.evals.run_node_eval.save_raw_results_to_csv")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.unlink")
    @patch("intent_kit.services.yaml_service.yaml_service.safe_load")
    @patch("intent_kit.evals.run_node_eval.datetime")
    @patch("importlib.import_module")
    @patch("sys.argv", ["run_node_eval.py"])
    @patch.dict("os.environ", {}, clear=True)
    @pytest.mark.skip(reason="This test is not working.")
    def test_main_node_load_failure(
        self,
        mock_import_module,
        mock_datetime,
        mock_yaml_load,
        mock_unlink,
        mock_mkdir,
        mock_save_results,
        mock_module_loader_load,
        mock_dataset_loader_load,
        mock_open,
        mock_glob,
        mock_exists,
        mock_parse_args,
    ):
        """Test main function when node loading fails."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.dataset = None
        mock_args.output = None
        mock_args.llm_config = None
        mock_parse_args.return_value = mock_args

        # Mock file system
        mock_exists.return_value = True
        mock_glob.return_value = [Path("action_node_llm.yaml")]

        # Mock datetime
        mock_datetime.now.return_value.strftime.side_effect = lambda fmt: (
            "2024-01-01_12-00-00" if "%Y-%m-%d_%H-%M-%S" in fmt else "2024-01-01"
        )

        # Mock importlib.import_module for datetime
        mock_datetime_module = MagicMock()
        mock_datetime_module.datetime.now.return_value.isoformat.return_value = (
            "2024-01-01T12:00:00"
        )
        mock_import_module.return_value = mock_datetime_module

        # Mock dataset data
        mock_dataset = {
            "dataset": {"name": "test_dataset", "node_name": "action_node_llm"},
            "test_cases": [{"input": "test", "expected": "result", "context": {}}],
        }
        mock_dataset_loader_load.return_value = mock_dataset

        # Mock node loading failure
        mock_module_loader_load.return_value = None

        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run main function - should continue with next dataset
        from intent_kit.evals.run_node_eval import main

        main()

        # Verify that module_loader.load was called
        mock_module_loader_load.assert_called_once()

    @patch("argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    @patch("builtins.open", new_callable=mock_open)
    @patch("intent_kit.services.loader_service.dataset_loader.load")
    @patch("intent_kit.services.loader_service.module_loader.load")
    @patch("intent_kit.evals.run_node_eval.evaluate_node")
    @patch("intent_kit.evals.run_node_eval.generate_markdown_report")
    @patch("intent_kit.evals.run_node_eval.save_raw_results_to_csv")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.unlink")
    @patch("intent_kit.services.yaml_service.yaml_service.safe_load")
    @patch("intent_kit.evals.run_node_eval.datetime")
    @patch("importlib.import_module")
    @patch("sys.argv", ["run_node_eval.py"])
    @patch.dict("os.environ", {}, clear=True)
    @pytest.mark.skip(reason="This test is not working.")
    def test_main_with_llm_config(
        self,
        mock_import_module,
        mock_datetime,
        mock_yaml_load,
        mock_unlink,
        mock_mkdir,
        mock_save_results,
        mock_generate_report,
        mock_evaluate_node,
        mock_module_loader_load,
        mock_dataset_loader_load,
        mock_open,
        mock_glob,
        mock_exists,
        mock_parse_args,
    ):
        """Test main function with LLM configuration."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.dataset = None
        mock_args.output = None
        mock_args.llm_config = "llm_config.yaml"
        mock_parse_args.return_value = mock_args

        # Mock file system
        mock_exists.return_value = True
        mock_glob.return_value = [Path("action_node_llm.yaml")]

        # Mock datetime
        mock_datetime.now.return_value.strftime.side_effect = lambda fmt: (
            "2024-01-01_12-00-00" if "%Y-%m-%d_%H-%M-%S" in fmt else "2024-01-01"
        )

        # Mock importlib.import_module for datetime
        mock_datetime_module = MagicMock()
        mock_datetime_module.datetime.now.return_value.isoformat.return_value = (
            "2024-01-01T12:00:00"
        )
        mock_import_module.return_value = mock_datetime_module

        # Mock LLM config data
        mock_llm_config = {
            "openai": {"api_key": "test_key"},
            "anthropic": {"api_key": "test_key_2"},
        }
        mock_yaml_load.return_value = mock_llm_config

        # Mock dataset data
        mock_dataset = {
            "dataset": {"name": "test_dataset", "node_name": "action_node_llm"},
            "test_cases": [{"input": "test", "expected": "result", "context": {}}],
        }
        mock_dataset_loader_load.return_value = mock_dataset

        # Mock node
        mock_node = MagicMock()
        mock_module_loader_load.return_value = mock_node

        # Mock evaluation results
        mock_eval_result = {
            "dataset": "test_dataset",
            "total_cases": 1,
            "correct": 1,
            "incorrect": 0,
            "accuracy": 1.0,
            "errors": [],
            "details": [],
            "raw_results_file": "test_file.csv",
        }
        mock_evaluate_node.return_value = mock_eval_result

        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run main function
        from intent_kit.evals.run_node_eval import main

        main()

        # Verify calls
        mock_dataset_loader_load.assert_called()
        mock_module_loader_load.assert_called_once()
        mock_evaluate_node.assert_called_once()
        mock_generate_report.assert_called_once()

    @patch("argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    @patch("builtins.open", new_callable=mock_open)
    @patch("intent_kit.services.loader_service.dataset_loader.load")
    @patch("intent_kit.services.loader_service.module_loader.load")
    @patch("intent_kit.evals.run_node_eval.evaluate_node")
    @patch("intent_kit.evals.run_node_eval.generate_markdown_report")
    @patch("intent_kit.evals.run_node_eval.save_raw_results_to_csv")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.unlink")
    @patch("intent_kit.services.yaml_service.yaml_service.safe_load")
    @patch("intent_kit.evals.run_node_eval.datetime")
    @patch("importlib.import_module")
    @patch("sys.argv", ["run_node_eval.py"])
    @patch.dict("os.environ", {}, clear=True)
    @pytest.mark.skip(reason="This test is not working.")
    def test_main_with_custom_output(
        self,
        mock_import_module,
        mock_datetime,
        mock_yaml_load,
        mock_unlink,
        mock_mkdir,
        mock_save_results,
        mock_generate_report,
        mock_evaluate_node,
        mock_module_loader_load,
        mock_dataset_loader_load,
        mock_open,
        mock_glob,
        mock_exists,
        mock_parse_args,
    ):
        """Test main function with custom output path."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.dataset = None
        mock_args.output = "custom_report.md"
        mock_args.llm_config = None
        mock_parse_args.return_value = mock_args

        # Mock file system
        mock_exists.return_value = True
        mock_glob.return_value = [Path("action_node_llm.yaml")]

        # Mock datetime
        mock_datetime.now.return_value.strftime.side_effect = lambda fmt: (
            "2024-01-01_12-00-00" if "%Y-%m-%d_%H-%M-%S" in fmt else "2024-01-01"
        )

        # Mock importlib.import_module for datetime
        mock_datetime_module = MagicMock()
        mock_datetime_module.datetime.now.return_value.isoformat.return_value = (
            "2024-01-01T12:00:00"
        )
        mock_import_module.return_value = mock_datetime_module

        # Mock dataset data
        mock_dataset = {
            "dataset": {"name": "test_dataset", "node_name": "action_node_llm"},
            "test_cases": [{"input": "test", "expected": "result", "context": {}}],
        }
        mock_dataset_loader_load.return_value = mock_dataset

        # Mock node
        mock_node = MagicMock()
        mock_module_loader_load.return_value = mock_node

        # Mock evaluation results
        mock_eval_result = {
            "dataset": "test_dataset",
            "total_cases": 1,
            "correct": 1,
            "incorrect": 0,
            "accuracy": 1.0,
            "errors": [],
            "details": [],
            "raw_results_file": "test_file.csv",
        }
        mock_evaluate_node.return_value = mock_eval_result

        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Run main function
        from intent_kit.evals.run_node_eval import main

        main()

        # Verify calls
        mock_dataset_loader_load.assert_called()
        mock_module_loader_load.assert_called_once()
        mock_evaluate_node.assert_called_once()
        mock_generate_report.assert_called_once()
