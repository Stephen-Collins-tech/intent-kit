# Evaluation

Intent Kit provides a comprehensive evaluation framework to measure the performance and accuracy of your DAGs.

## Overview

The evaluation framework helps you:
- Measure accuracy and performance
- Compare different DAG configurations
- Track regressions over time
- Generate detailed reports

## Quick Start

```python
from intent_kit.evals import run_eval, load_dataset
from intent_kit import DAGBuilder, run_dag

# Create a simple DAG
def greet(name: str, **kwargs) -> str:
    return f"Hello {name}!"

builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it"
})
builder.add_node("classifier", "classifier",
                 output_labels=["greet"],
                 description="Main classifier")
builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name")
builder.add_node("greet_action", "action",
                 action=greet,
                 description="Greet user")
builder.add_edge("classifier", "extract_name", "greet")
builder.add_edge("extract_name", "greet_action", "success")
builder.set_entrypoints(["classifier"])

dag = builder.build()

# Load test dataset
dataset = load_dataset("tests/datasets/greeting.yaml")

# Run evaluation
result = run_eval(dataset, dag)

# View results
print(f"Accuracy: {result.accuracy():.1%}")
print(f"Average response time: {result.avg_response_time()}ms")
```

## Dataset Format

### YAML Format

```yaml
# tests/datasets/greeting.yaml
test_cases:
  - input: "Hello Alice"
    expected_output: "Hello Alice!"
    expected_intent: "greet"
    expected_params:
      name: "Alice"

  - input: "Hi Bob"
    expected_output: "Hello Bob!"
    expected_intent: "greet"
    expected_params:
      name: "Bob"
```

### Programmatic Format

```python
dataset = {
    "test_cases": [
        {
            "input": "Hello Alice",
            "expected_output": "Hello Alice!",
            "expected_intent": "greet",
            "expected_params": {"name": "Alice"}
        }
    ]
}
```

## Running Evaluations

### Basic Evaluation

```python
from intent_kit.evals import run_eval

result = run_eval(dataset, dag)
```

### With Custom Metrics

```python
from intent_kit.evals import run_eval, EvaluationConfig

config = EvaluationConfig(
    include_timing=True,
    include_confidence=True,
    save_detailed_results=True
)

result = run_eval(dataset, dag, config=config)
```

### Batch Evaluation

```python
from intent_kit.evals import run_batch_eval

# Evaluate multiple DAGs
dags = [dag1, dag2, dag3]
results = run_batch_eval(dataset, dags)

for name, result in results.items():
    print(f"{name}: {result.accuracy():.1%} accuracy")
```

## Evaluation Metrics

### Accuracy Metrics

```python
# Basic accuracy
accuracy = result.accuracy()
print(f"Overall accuracy: {accuracy:.1%}")

# Per-intent accuracy
intent_accuracy = result.intent_accuracy()
for intent, acc in intent_accuracy.items():
    print(f"{intent}: {acc:.1%}")

# Parameter extraction accuracy
param_accuracy = result.parameter_accuracy()
print(f"Parameter accuracy: {param_accuracy:.1%}")
```

### Performance Metrics

```python
# Timing metrics
avg_time = result.avg_response_time()
max_time = result.max_response_time()
min_time = result.min_response_time()

print(f"Average response time: {avg_time}ms")
print(f"Response time range: {min_time}ms - {max_time}ms")

# Throughput
throughput = result.throughput()
print(f"Throughput: {throughput} requests/second")
```

### Error Analysis

```python
# Error breakdown
errors = result.errors()
for error in errors:
    print(f"Error: {error.input} -> {error.expected} (got: {error.actual})")

# Error types
error_types = result.error_types()
for error_type, count in error_types.items():
    print(f"{error_type}: {count} errors")
```

## Creating Test Datasets

### Manual Dataset Creation

```python
def create_greeting_dataset():
    """Create a test dataset for greeting functionality."""
    return {
        "test_cases": [
            {
                "input": "Hello Alice",
                "expected_output": "Hello Alice!",
                "expected_intent": "greet",
                "expected_params": {"name": "Alice"}
            },
            {
                "input": "Hi Bob",
                "expected_output": "Hello Bob!",
                "expected_intent": "greet",
                "expected_params": {"name": "Bob"}
            },
            {
                "input": "Greet Charlie",
                "expected_output": "Hello Charlie!",
                "expected_intent": "greet",
                "expected_params": {"name": "Charlie"}
            }
        ]
    }

# Use the dataset
dataset = create_greeting_dataset()
result = run_eval(dataset, dag)
```

### Automated Dataset Generation

```python
def generate_test_cases(base_inputs, variations):
    """Generate test cases with variations."""
    test_cases = []

    for base_input in base_inputs:
        for variation in variations:
            test_input = base_input.format(**variation)
            expected_output = f"Hello {variation['name']}!"

            test_cases.append({
                "input": test_input,
                "expected_output": expected_output,
                "expected_intent": "greet",
                "expected_params": {"name": variation["name"]}
            })

    return {"test_cases": test_cases}

# Generate test cases
base_inputs = ["Hello {name}", "Hi {name}", "Greet {name}"]
variations = [
    {"name": "Alice"},
    {"name": "Bob"},
    {"name": "Charlie"},
    {"name": "David"}
]

dataset = generate_test_cases(base_inputs, variations)
```

## Advanced Evaluation

### Custom Evaluation Metrics

```python
from intent_kit.evals import EvaluationResult

class CustomEvaluationResult(EvaluationResult):
    def custom_metric(self):
        """Calculate a custom metric."""
        correct = sum(1 for case in self.results if case.correct)
        total = len(self.results)
        return correct / total if total > 0 else 0

def custom_evaluation(dataset, dag):
    """Run evaluation with custom metrics."""
    # Run standard evaluation
    result = run_eval(dataset, dag)

    # Add custom metrics
    custom_metric = result.custom_metric()
    print(f"Custom metric: {custom_metric:.1%}")

    return result
```

### Cross-Validation

```python
from sklearn.model_selection import KFold
import numpy as np

def cross_validate_dag(dataset, dag, n_splits=5):
    """Perform cross-validation on DAG."""
    test_cases = dataset["test_cases"]
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    accuracies = []

    for train_idx, test_idx in kf.split(test_cases):
        # Split dataset
        train_cases = [test_cases[i] for i in train_idx]
        test_cases_split = [test_cases[i] for i in test_idx]

        train_dataset = {"test_cases": train_cases}
        test_dataset = {"test_cases": test_cases_split}

        # Evaluate on test set
        result = run_eval(test_dataset, dag)
        accuracies.append(result.accuracy())

    mean_accuracy = np.mean(accuracies)
    std_accuracy = np.std(accuracies)

    print(f"Cross-validation accuracy: {mean_accuracy:.1%} ± {std_accuracy:.1%}")
    return accuracies
```

## Regression Testing

### Automated Regression Detection

```python
import json
from datetime import datetime

def save_baseline_results(result, baseline_file="baseline_results.json"):
    """Save baseline results for regression testing."""
    baseline = {
        "timestamp": datetime.utcnow().isoformat(),
        "accuracy": result.accuracy(),
        "avg_response_time": result.avg_response_time(),
        "total_tests": len(result.results)
    }

    with open(baseline_file, "w") as f:
        json.dump(baseline, f, indent=2)

def check_regression(result, baseline_file="baseline_results.json", threshold=0.05):
    """Check for performance regression."""
    with open(baseline_file, "r") as f:
        baseline = json.load(f)

    current_accuracy = result.accuracy()
    baseline_accuracy = baseline["accuracy"]

    regression = baseline_accuracy - current_accuracy

    if regression > threshold:
        print(f"REGRESSION DETECTED: Accuracy dropped by {regression:.1%}")
        print(f"  Baseline: {baseline_accuracy:.1%}")
        print(f"  Current: {current_accuracy:.1%}")
        return True

    print(f"No regression detected. Accuracy: {current_accuracy:.1%}")
    return False

# Use for regression testing
result = run_eval(dataset, dag)
check_regression(result)
```

## Continuous Evaluation

### Integration with CI/CD

```python
# evaluation_script.py
from intent_kit.evals import run_eval, load_dataset
import sys

def main():
    # Load dataset and DAG
    dataset = load_dataset("tests/datasets/main.yaml")
    dag = create_production_dag()

    # Run evaluation
    result = run_eval(dataset, dag)

    # Check for regressions
    if result.accuracy() < 0.95:  # 95% accuracy threshold
        print("ERROR: Accuracy below threshold")
        sys.exit(1)

    if result.avg_response_time() > 1000:  # 1 second threshold
        print("ERROR: Response time above threshold")
        sys.exit(1)

    print("Evaluation passed!")
    print(f"Accuracy: {result.accuracy():.1%}")
    print(f"Avg response time: {result.avg_response_time()}ms")

if __name__ == "__main__":
    main()
```

### Scheduled Evaluation

```python
import schedule
import time

def scheduled_evaluation():
    """Run evaluation on schedule."""
    dataset = load_dataset("tests/datasets/main.yaml")
    dag = create_production_dag()

    result = run_eval(dataset, dag)

    # Log results
    with open("evaluation_log.json", "a") as f:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "accuracy": result.accuracy(),
            "avg_response_time": result.avg_response_time()
        }
        f.write(json.dumps(log_entry) + "\n")

# Schedule daily evaluation
schedule.every().day.at("02:00").do(scheduled_evaluation)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Best Practices

### 1. **Comprehensive Test Coverage**
- Test all intents and edge cases
- Include negative test cases
- Test parameter extraction accuracy

### 2. **Realistic Test Data**
- Use real-world input examples
- Include variations in input format
- Test with different user personas

### 3. **Performance Monitoring**
- Set performance baselines
- Monitor for regressions
- Track performance trends

### 4. **Automated Testing**
- Integrate evaluation into CI/CD
- Run evaluations regularly
- Alert on performance degradation

### 5. **Result Analysis**
- Analyze error patterns
- Identify common failure modes
- Use results to improve DAGs
