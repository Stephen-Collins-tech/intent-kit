import pathlib
import yaml
from node_eval.run_node_eval import run_tests, infer_node_spec_from_dataset, resolve_node_class

DATASET_DIR = pathlib.Path(__file__).parents[1] / "node_eval" / "datasets"


def _load_dataset(path: pathlib.Path):
    with open(path) as f:
        data = yaml.safe_load(f)
    threshold = data.get("threshold", 1.0)
    tests = data["tests"] if "tests" in data else data.get("cases", [])
    return threshold, tests


def pytest_generate_tests(metafunc):
    if "dataset_path" in metafunc.fixturenames:
        dataset_files = list(DATASET_DIR.glob("*.yaml"))
        metafunc.parametrize("dataset_path", dataset_files)


def test_node_accuracy(dataset_path):
    threshold, tests = _load_dataset(dataset_path)
    node_spec = infer_node_spec_from_dataset(dataset_path)
    node_cls = resolve_node_class(node_spec)

    passed, total, _ = run_tests(node_cls, tests)
    accuracy = passed / total if total else 0.0
    assert accuracy >= threshold, f"{node_cls.__name__} accuracy {accuracy:.2%} below threshold {threshold:.2%}"