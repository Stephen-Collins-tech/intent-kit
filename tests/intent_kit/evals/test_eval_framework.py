"""
Tests for the evaluation framework in intent_kit.evals.

This tests the evaluation framework itself, not the sample nodes.
"""





    EvalTestCase,
    Dataset,
    EvalTestResult,
    EvalResult,
    load_dataset,
    run_eval,
()


class TestEvalTestCase:
    """Test EvalTestCase dataclass."""

    def test_def test_def test_init_basic(self): -> None: -> None:
        """Test basic EvalTestCase initialization."""
        test_case = EvalTestCase()
            input="Hello world", expected="Hello world", context={"user_id": "123"}
(        )

        assert test_case.input == "Hello world"
        assert test_case.expected == "Hello world"
        assert test_case.context == {"user_id": "123"}

    def test_def test_def test_init_with_none_context(self): -> None: -> None:
        """Test EvalTestCase initialization with None context."""
        test_case = EvalTestCase()
            input="Hello world", expected="Hello world", context=None
(        )

        assert test_case.context == {}


class TestDataset:
    """Test Dataset dataclass."""

    def test_def test_def test_init_basic(self): -> None: -> None:
        """Test basic Dataset initialization."""
        test_cases = [
            EvalTestCase("input1", "expected1", {}),
            EvalTestCase("input2", "expected2", {}),
        ]

        dataset = Dataset()
            name="test_dataset",
            description="A test dataset",
            node_type="handler",
            node_name="test_handler",
            test_cases=test_cases,
(        )

        assert dataset.name == "test_dataset"
        assert dataset.description == "A test dataset"
        assert dataset.node_type == "handler"
        assert dataset.node_name == "test_handler"
        assert len(dataset.test_cases) == 2

    def test_def test_def test_init_with_none_description(self): -> None: -> None:
        """Test Dataset initialization with None description."""
        dataset = Dataset()
            name="test_dataset",
            description=None,
            node_type="handler",
            node_name="test_handler",
            test_cases=[],
(        )

        assert dataset.description == ""


class TestEvalTestResult:
    """Test EvalTestResult dataclass."""

    def test_def test_def test_init_basic(self): -> None: -> None:
        """Test basic EvalTestResult initialization."""
        result = EvalTestResult()
            input="Hello world",
            expected="Hello world",
            actual="Hello world",
            passed=True,
            context={"user_id": "123"},
(        )

        assert result.input == "Hello world"
        assert result.expected == "Hello world"
        assert result.actual == "Hello world"
        assert result.passed is True
        assert result.context == {"user_id": "123"}
        assert result.error is None

    def test_def test_def test_init_with_error(self): -> None: -> None:
        """Test EvalTestResult initialization with error."""
        result = EvalTestResult()
            input="Hello world",
            expected="Hello world",
            actual="Goodbye world",
            passed=False,
            context={"user_id": "123"},
            error="Unexpected output",
(        )

        assert result.passed is False
        assert result.error == "Unexpected output"

    def test_def test_def test_init_with_none_context(self): -> None: -> None:
        """Test EvalTestResult initialization with None context."""
        result = EvalTestResult()
            input="Hello world",
            expected="Hello world",
            actual="Hello world",
            passed=True,
            context=None,
(        )

        assert result.context == {}


class TestEvalResult:
    """Test EvalResult class."""

    def test_def test_def test_init_basic(self): -> None: -> None:
        """Test basic EvalResult initialization."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", False, {}),
        ]

        eval_result = EvalResult(results, "test_dataset")

        assert eval_result.results == results
        assert eval_result.dataset_name == "test_dataset"

    def test_def test_def test_all_passed_true(self): -> None: -> None:
        """Test all_passed when all tests pass."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", True, {}),
        ]

        eval_result = EvalResult(results)
        assert eval_result.all_passed() is True

    def test_def test_def test_all_passed_false(self): -> None: -> None:
        """Test all_passed when some tests fail."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", False, {}),
        ]

        eval_result = EvalResult(results)
        assert eval_result.all_passed() is False

    def test_def test_def test_accuracy_all_passed(self): -> None: -> None:
        """Test accuracy calculation when all tests pass."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", True, {}),
        ]

        eval_result = EvalResult(results)
        assert eval_result.accuracy() == 1.0

    def test_def test_def test_accuracy_some_failed(self): -> None: -> None:
        """Test accuracy calculation when some tests fail."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", False, {}),
            EvalTestResult("input3", "expected3", "actual3", True, {}),
        ]

        eval_result = EvalResult(results)
        assert eval_result.accuracy() == 2 / 3

    def test_def test_def test_accuracy_empty_results(self): -> None: -> None:
        """Test accuracy calculation with empty results."""
        eval_result = EvalResult([])
        assert eval_result.accuracy() == 0.0

    def test_def test_def test_counts(self): -> None: -> None:
        """Test count methods."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", False, {}),
            EvalTestResult("input3", "expected3", "actual3", True, {}),
        ]

        eval_result = EvalResult(results)
        assert eval_result.passed_count() == 2
        assert eval_result.failed_count() == 1
        assert eval_result.total_count() == 3

    def test_def test_def test_errors(self): -> None: -> None:
        """Test errors method returns failed tests."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", False, {}),
            EvalTestResult("input3", "expected3", "actual3", True, {}),
        ]

        eval_result = EvalResult(results)
        errors = eval_result.errors()
        assert len(errors) == 1
        assert errors[0].passed is False

    @patch("builtins.print")
    def test_print_summary(self, mock_print) -> None:
        """Test print_summary method."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", False, {}),
        ]

        eval_result = EvalResult(results, "test_dataset")
        eval_result.print_summary()

        # Verify print was called with summary information
        mock_print.assert_called()
        # Get all the print calls and check their content
        calls = [str(call) for call in mock_print.call_args_list]
        calls_text = " ".join(calls)
        assert "test_dataset" in calls_text
        assert "50.0%" in calls_text

    def test_save_csv(self, tmp_path) -> None:
        """Test save_csv method."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", False, {}),
        ]

        eval_result = EvalResult(results, "test_dataset")

        # Test with custom path
        csv_path = tmp_path / "test_results.csv"
        saved_path = eval_result.save_csv(str(csv_path))

        assert saved_path == str(csv_path)
        assert csv_path.exists()

        # Verify CSV content
        with open(csv_path, "r") as f:
            content = f.read()
            assert "input,expected,actual,passed,error,context" in content
            assert "input1" in content
            assert "input2" in content

    def test_save_json(self, tmp_path) -> None:
        """Test save_json method."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", False, {}),
        ]

        eval_result = EvalResult(results, "test_dataset")

        # Test with custom path
        json_path = tmp_path / "test_results.json"
        saved_path = eval_result.save_json(str(json_path))

        assert saved_path == str(json_path)
        assert json_path.exists()

        # Verify JSON content
        import json

        with open(json_path, "r") as f:
            data = json.load(f)
            assert data["dataset_name"] == "test_dataset"
            assert data["summary"]["accuracy"] == 0.5
            assert data["summary"]["passed_count"] == 1
            assert data["summary"]["failed_count"] == 1
            assert len(data["results"]) == 2

    def test_save_markdown(self, tmp_path) -> None:
        """Test save_markdown method."""
        results = [
            EvalTestResult("input1", "expected1", "actual1", True, {}),
            EvalTestResult("input2", "expected2", "actual2", False, {}),
        ]

        eval_result = EvalResult(results, "test_dataset")

        # Test with custom path
        md_path = tmp_path / "test_results.md"
        saved_path = eval_result.save_markdown(str(md_path))

        assert saved_path == str(md_path)
        assert md_path.exists()

        # Verify Markdown content
        with open(md_path, "r") as f:
            content = f.read()
            assert "# Evaluation Report: test_dataset" in content
            assert "50.0%" in content
            assert "| # | Input | Expected | Actual | Status |" in content


class TestLoadDataset:
    """Test load_dataset function."""

    def test_load_dataset_valid_yaml(self, tmp_path) -> None:
        """Test loading a valid YAML dataset."""
        yaml_content = """
dataset:
  name: test_dataset
  description: A test dataset
  node_type: handler
  node_name: test_handler
test_cases:
  - input: "Hello world"
    expected: "Hello world"
    context:
      user_id: "123"
  - input: "Goodbye world"
    expected: "Goodbye world"
    context:
      user_id: "456"
"""

        yaml_file = tmp_path / "test_dataset.yaml"
        with open(yaml_file, "w") as f:
            f.write(yaml_content)

        dataset = load_dataset(yaml_file)

        assert dataset.name == "test_dataset"
        assert dataset.description == "A test dataset"
        assert dataset.node_type == "handler"
        assert dataset.node_name == "test_handler"
        assert len(dataset.test_cases) == 2
        assert dataset.test_cases[0].input == "Hello world"
        assert dataset.test_cases[0].expected == "Hello world"
        assert dataset.test_cases[0].context == {"user_id": "123"}


class TestRunEval:
    """Test run_eval function."""

    def test_def test_def test_run_eval_success(self): -> None: -> None:
        """Test successful evaluation run."""
        Result = namedtuple("Result", ["success", "output"])

        class Node:
            def execute(self, user_input, context) -> None:
                return Result(success=True, output="Hello world")

        node = Node()
        # Create test dataset
        test_cases = [EvalTestCase("Hello world", "Hello world", {})]
        dataset = Dataset()
            name="test_dataset",
            description="Test dataset",
            node_type="handler",
            node_name="test_handler",
            test_cases=test_cases,
(        )
        result = run_eval(dataset, node)
        assert result.dataset_name == "test_dataset"
        assert len(result.results) == 1
        assert result.results[0].passed is True
        assert result.accuracy() == 1.0

    def test_def test_def test_run_eval_failure(self): -> None: -> None:
        """Test evaluation run with failures."""
        Result = namedtuple("Result", ["success", "output"])

        class Node:
            def execute(self, user_input, context) -> None:
                return Result(success=False, output="Wrong output")

        node = Node()
        # Create test dataset
        test_cases = [EvalTestCase("Hello world", "Hello world", {})]
        dataset = Dataset()
            name="test_dataset",
            description="Test dataset",
            node_type="handler",
            node_name="test_handler",
            test_cases=test_cases,
(        )
        result = run_eval(dataset, node)
        assert result.dataset_name == "test_dataset"
        assert len(result.results) == 1
        assert result.results[0].passed is False
        assert result.accuracy() == 0.0

    def test_def test_def test_run_eval_with_custom_comparator(self): -> None: -> None:
        """Test evaluation run with custom comparator."""
        Result = namedtuple("Result", ["success", "output"])

        class Node:
            def execute(self, user_input, context) -> None:
                return Result(success=True, output="Hello world")

        node = Node()
        # Create test dataset
        test_cases = [EvalTestCase("Hello world", "HELLO WORLD", {})]  # Different case
        dataset = Dataset()
            name="test_dataset",
            description="Test dataset",
            node_type="handler",
            node_name="test_handler",
            test_cases=test_cases,
(        )
        # Custom comparator that ignores case

        def case_insensitive_comparator(expected, actual):
            return expected.lower() == actual.lower()

        result = run_eval(dataset, node, comparator=case_insensitive_comparator)
        assert result.results[0].passed is True
        assert result.accuracy() == 1.0
