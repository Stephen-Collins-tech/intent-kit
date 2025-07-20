"""
Tests for run_node_eval module.
"""

import tempfile
import pathlib


    load_dataset,
    get_node_from_module,
    save_raw_results_to_csv,
    similarity_score,
    chunks_similarity_score,
    evaluate_node,
    generate_markdown_report,
()


class TestRunNodeEval:
    """Test cases for run_node_eval module."""

    def test_def test_def test_load_dataset_success(self): -> None: -> None:
        """Test successful dataset loading."""
        test_data = {
            "name": "test_dataset",
            "node_name": "test_node",
            "test_cases": [
                {"input": "test input", "expected": "test output", "context": {}}
            ],
        }

        with patch()
            "builtins.open",
            mock_open(read_data="name: test_dataset\nnode_name: test_node"),
(        ):
            with patch("yaml.safe_load", return_value=test_data):
                result = load_dataset(pathlib.Path("test.yaml"))

        assert result == test_data

    def test_def test_def test_get_node_from_module_success(self): -> None: -> None:
        """Test successful node loading from module."""
        mock_node = MagicMock()
        mock_module = MagicMock()
        mock_module.test_node = mock_node

        with patch("importlib.import_module", return_value=mock_module):
            result = get_node_from_module("test.module", "test_node")

        assert result == mock_node

    def test_def test_def test_get_node_from_module_import_error(self): -> None: -> None:
        """Test node loading with import error."""
        with patch()
            "importlib.import_module", side_effect=ImportError("Module not found")
(        ):
            result = get_node_from_module("test.module", "test_node")

        assert result is None

    def test_def test_def test_get_node_from_module_attribute_error(self): -> None: -> None:
        """Test node loading with attribute error."""

        class MinimalModule:
            pass

        mock_module = MinimalModule()
        # Do not define test_node attribute, so getattr will raise AttributeError

        with patch("importlib.import_module", return_value=mock_module):
            result = get_node_from_module("test.module", "test_node")

        assert result is None

    def test_def test_def test_save_raw_results_to_csv(self): -> None: -> None:
        """Test saving raw results to CSV."""
        test_case = {"input": "test input", "expected": "test output", "context": {}}
        actual_output = "test result"
        success = True
        error = None
        similarity_score_val = 0.85

        with patch("intent_kit.evals.run_node_eval.Path") as mock_path:
            mock_path.return_value.parent.__truediv__.return_value = ()
                mock_path.return_value
(            )
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False

            with patch("builtins.open", mock_open()):
                csv_file, date_csv_file = save_raw_results_to_csv()
                    "test_dataset",
                    test_case,
                    actual_output,
                    success,
                    error,
                    similarity_score_val,
(                )

        # Verify files were created
        assert csv_file is not None
        assert date_csv_file is not None

    def test_def test_def test_similarity_score_identical(self): -> None: -> None:
        """Test similarity score with identical texts."""
        score = similarity_score("hello world", "hello world")
        assert score == 1.0

    def test_def test_def test_similarity_score_different(self): -> None: -> None:
        """Test similarity score with different texts."""
        score = similarity_score("hello world", "goodbye world")
        assert 0.0 <= score <= 1.0
        assert score < 1.0

    def test_def test_def test_similarity_score_normalized(self): -> None: -> None:
        """Test similarity score with whitespace normalization."""
        score1 = similarity_score("hello  world", "hello world")
        score2 = similarity_score("HELLO WORLD", "hello world")
        assert score1 > 0.8  # Should be high after normalization
        assert score2 > 0.8  # Should be high after normalization

    def test_def test_def test_chunks_similarity_score_identical(self): -> None: -> None:
        """Test chunks similarity with identical chunks."""
        expected = ["hello", "world"]
        actual = ["hello", "world"]
        correct, score = chunks_similarity_score(expected, actual)
        assert correct is True
        assert score == 1.0

    def test_def test_def test_chunks_similarity_score_different_lengths(self): -> None: -> None:
        """Test chunks similarity with different lengths."""
        expected = ["hello", "world"]
        actual = ["hello"]
        correct, score = chunks_similarity_score(expected, actual)
        assert correct is False
        assert score == 0.0

    def test_def test_def test_chunks_similarity_score_threshold(self): -> None: -> None:
        """Test chunks similarity with threshold."""
        expected = ["hello world"]
        actual = ["hello world!"]
        correct, score = chunks_similarity_score(expected, actual, threshold=0.9)
        assert correct is True
        assert score > 0.8

    @patch("intent_kit.evals.run_node_eval.save_raw_results_to_csv")
    def test_evaluate_node_success(self, mock_save_csv) -> None:
        """Test successful node evaluation."""
        mock_node = MagicMock()
        mock_node.execute.return_value = MagicMock(success=True, output="test output")

        test_cases = [{"input": "test input", "expected": "test output", "context": {}}]

        result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["dataset"] == "test_dataset"
        assert result["total_cases"] == 1
        assert result["correct"] == 1
        assert result["incorrect"] == 0
        assert len(result["errors"]) == 0

    @patch("intent_kit.evals.run_node_eval.save_raw_results_to_csv")
    def test_evaluate_node_with_error(self, mock_save_csv) -> None:
        """Test node evaluation with execution error."""
        mock_node = MagicMock()
        mock_node.execute.side_effect = Exception("Test error")

        test_cases = [{"input": "test input", "expected": "test output", "context": {}}]

        result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["dataset"] == "test_dataset"
        assert result["total_cases"] == 1
        assert result["correct"] == 0
        assert result["incorrect"] == 1
        assert len(result["errors"]) == 1

    @patch("intent_kit.evals.run_node_eval.save_raw_results_to_csv")
    def test_evaluate_node_with_list_output(self, mock_save_csv) -> None:
        """Test node evaluation with list output (splitter)."""
        mock_node = MagicMock()
        mock_node.execute.return_value = MagicMock()
            success=True, output=["hello", "world"]
(        )

        test_cases = [
            {"input": "test input", "expected": ["hello", "world"], "context": {}}
        ]

        result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["correct"] == 1
        assert result["incorrect"] == 0

    @patch("intent_kit.evals.run_node_eval.save_raw_results_to_csv")
    def test_evaluate_node_with_persistent_context(self, mock_save_csv) -> None:
        """Test node evaluation with persistent context."""
        mock_node = MagicMock()
        mock_node.name = "action_node_llm"
        mock_node.execute.return_value = MagicMock(success=True, output="test output")

        test_cases = [
            {
                "input": "test input",
                "expected": "test output",
                "context": {"key": "value"},
            }
        ]

        result = evaluate_node(mock_node, test_cases, "test_dataset")

        assert result["correct"] == 1
        assert result["incorrect"] == 0

    def test_def test_def test_generate_markdown_report(self): -> None: -> None:
        """Test markdown report generation."""
        results = [
            {
                "dataset": "test_dataset",
                "accuracy": 0.85,
                "correct": 17,
                "incorrect": 3,
                "total_cases": 20,
                "errors": [],
                "details": [],
                "raw_results_file": "test_results.csv",
            }
        ]

        with tempfile.NamedTemporaryFile()
            mode="w", suffix=".md", delete=False
(        ) as tmp_file:
            output_path = pathlib.Path(tmp_file.name)

        try:
            generate_markdown_report()
                results, output_path, run_timestamp="2024-01-01_12-00-00"
(            )

            # Check that file was created
            assert output_path.exists()

            # Check file contents
            with open(output_path, "r") as f:
                content = f.read()
                assert "test_dataset" in content
                assert "85.0%" in content
                assert "17/20" in content

        finally:
            output_path.unlink(missing_ok=True)

    def test_def test_def test_generate_markdown_report_with_errors(self): -> None: -> None:
        """Test markdown report generation with errors."""
        results = [
            {
                "dataset": "test_dataset",
                "accuracy": 0.5,
                "correct": 10,
                "incorrect": 10,
                "total_cases": 20,
                "errors": [
                    {
                        "case": 1,
                        "input": "test input",
                        "expected": "expected output",
                        "actual": "actual output",
                        "error": "Test error",
                    }
                ],
                "details": [{"input": "test", "error": "Test error"}],
                "raw_results_file": "test_results.csv",
            }
        ]

        with tempfile.NamedTemporaryFile()
            mode="w", suffix=".md", delete=False
(        ) as tmp_file:
            output_path = pathlib.Path(tmp_file.name)

        try:
            generate_markdown_report(results, output_path)

            # Check file contents for error information
            with open(output_path, "r") as f:
                content = f.read()
                assert "Test error" in content
                assert "50.0%" in content

        finally:
            output_path.unlink(missing_ok=True)
