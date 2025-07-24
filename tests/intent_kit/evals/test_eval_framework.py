"""
Tests for the evaluation framework in intent_kit.evals.

This tests the evaluation framework itself, not the sample nodes.
"""

from intent_kit.evals import (
    load_dataset,
    run_eval,
    run_eval_from_path,
    EvalTestCase,
    Dataset,
)


class MockNode:
    def execute(self, user_input, context=None):
        # Simple echo node for testing
        class Result:
            def __init__(self, output):
                self.success = True
                self.output = output
                self.error = None

        return Result(user_input.upper())


def test_load_dataset(tmp_path):
    # Create a sample YAML dataset
    yaml_content = """
dataset:
  name: test_dataset
  node_type: action
  node_name: mock_node
test_cases:
  - input: hello
    expected: HELLO
  - input: world
    expected: WORLD
"""
    dataset_file = tmp_path / "sample.yaml"
    dataset_file.write_text(yaml_content)
    dataset = load_dataset(dataset_file)
    assert dataset.name == "test_dataset"
    assert len(dataset.test_cases) == 2
    assert dataset.test_cases[0].input == "hello"
    assert dataset.test_cases[0].expected == "HELLO"


def test_run_eval_with_mock_node():
    # Create a dataset object
    test_cases = [
        EvalTestCase(input="foo", expected="FOO", context={}),
        EvalTestCase(input="bar", expected="BAR", context={}),
    ]
    dataset = Dataset(
        name="mock_eval",
        description="",
        node_type="action",
        node_name="mock_node",
        test_cases=test_cases,
    )
    node = MockNode()
    result = run_eval(dataset, node)
    assert result.all_passed()
    assert result.passed_count() == 2
    assert result.failed_count() == 0
    assert result.total_count() == 2


def test_run_eval_from_path(tmp_path):
    # Create a sample YAML dataset
    yaml_content = """
dataset:
  name: test_dataset_path
  node_type: action
  node_name: mock_node
test_cases:
  - input: test
    expected: TEST
"""
    dataset_file = tmp_path / "sample2.yaml"
    dataset_file.write_text(yaml_content)
    node = MockNode()
    result = run_eval_from_path(dataset_file, node)
    assert result.all_passed()
    assert result.passed_count() == 1
    assert result.failed_count() == 0
    assert result.total_count() == 1
