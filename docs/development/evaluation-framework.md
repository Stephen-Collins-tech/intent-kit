# Evaluation Framework

Intent Kit provides a comprehensive evaluation framework for testing and benchmarking nodes against structured datasets. This framework enables systematic testing of node performance, accuracy, and reliability.

## Overview

The evaluation framework includes:
- **Structured Datasets** - YAML-based test case definitions
- **Comprehensive Metrics** - Accuracy, performance, and cost tracking
- **Automated Testing** - Batch evaluation of multiple test cases
- **Report Generation** - Detailed performance reports and analysis
- **Regression Testing** - Track performance changes over time

## Basic Usage

### Running Evaluations

```python
from intent_kit.evals import evaluate_node, load_dataset

# Load a dataset
dataset = load_dataset("path/to/dataset.yaml")

# Evaluate a node
result = evaluate_node(dataset, node_instance)

# Print results
result.print_summary()
print(f"Accuracy: {result.accuracy():.1%}")
```

### Command Line Interface

```bash
# Run all evaluations
uv run python -m intent_kit.evals.run_all_evals

# Run specific node evaluation
uv run python -m intent_kit.evals.run_node_eval --dataset classifier_node_llm.yaml

# Run with specific configuration
uv run python -m intent_kit.evals.run_node_eval --dataset extractor_node.yaml --config production.yaml
```

## Dataset Format

### YAML Dataset Structure

```yaml
name: "Classifier Node Evaluation"
description: "Test cases for intent classification"
node_type: "classifier"
node_name: "intent_classifier"

test_cases:
  - input: "Hello, how are you?"
    expected: "greet"
    context:
      user_id: "test_user_1"

  - input: "What's the weather like?"
    expected: "weather"
    context:
      user_id: "test_user_2"

  - input: "Book a table for 4 people"
    expected: "booking"
    context:
      user_id: "test_user_3"
```

### Test Case Structure

```yaml
test_cases:
  - input: "User input string"
    expected: "Expected output or result"
    context:
      # Optional context data
      user_id: "user123"
      session_id: "session456"
      metadata:
        category: "greeting"
        difficulty: "easy"
```

## Creating Datasets

### Classifier Node Dataset

```yaml
name: "Intent Classification Dataset"
description: "Test cases for intent classification"
node_type: "classifier"
node_name: "intent_classifier"

test_cases:
  # Greeting intents
  - input: "Hello there"
    expected: "greet"

  - input: "Good morning"
    expected: "greet"

  - input: "Hi, how are you doing?"
    expected: "greet"

  # Weather intents
  - input: "What's the weather like?"
    expected: "weather"

  - input: "Is it going to rain today?"
    expected: "weather"

  - input: "Weather forecast for tomorrow"
    expected: "weather"

  # Booking intents
  - input: "I want to book a table"
    expected: "booking"

  - input: "Reserve a flight to New York"
    expected: "booking"

  - input: "Book a hotel room"
    expected: "booking"
```

### Extractor Node Dataset

```yaml
name: "Parameter Extraction Dataset"
description: "Test cases for parameter extraction"
node_type: "extractor"
node_name: "booking_extractor"

test_cases:
  - input: "Book a table for 4 people at 7 PM"
    expected:
      party_size: 4
      time: "7 PM"
    context:
      required_params: ["party_size", "time"]

  - input: "Reserve a flight from LA to NYC on March 15"
    expected:
      origin: "LA"
      destination: "NYC"
      date: "March 15"
    context:
      required_params: ["origin", "destination", "date"]

  - input: "I need a hotel room for 2 nights starting tomorrow"
    expected:
      duration: 2
      start_date: "tomorrow"
    context:
      required_params: ["duration", "start_date"]
```

### Action Node Dataset

```yaml
name: "Action Execution Dataset"
description: "Test cases for action execution"
node_type: "action"
node_name: "greet_action"

test_cases:
  - input: "Hello"
    expected: "Hello! How can I help you today?"
    context:
      user_name: "John"

  - input: "Hi there"
    expected: "Hi there! How can I help you today?"
    context:
      user_name: "Jane"
```

## Advanced Dataset Features

### Context-Aware Testing

```yaml
test_cases:
  - input: "What's my balance?"
    expected: "Your current balance is $1,250.00"
    context:
      user_id: "user123"
      account_balance: 1250.00

  - input: "Transfer $100 to savings"
    expected: "Transferred $100.00 to your savings account"
    context:
      user_id: "user123"
      checking_balance: 500.00
      savings_balance: 2000.00
```

### Edge Case Testing

```yaml
test_cases:
  # Empty input
  - input: ""
    expected: "clarification"

  # Very long input
  - input: "This is a very long input that tests how the system handles extremely long user inputs that might exceed normal length limits and could potentially cause issues with processing or response generation"
    expected: "booking"

  # Special characters
  - input: "Book a table for 2 @ 7:30 PM"
    expected: "booking"

  # Unicode characters
  - input: "Réserver une table pour 4 personnes"
    expected: "booking"
```

### Performance Testing

```yaml
test_cases:
  # Simple queries
  - input: "Hello"
    expected: "greet"
    context:
      max_response_time: 1.0

  # Complex queries
  - input: "I need to book a flight from San Francisco to New York for next Tuesday, preferably in the morning, for 2 people, economy class, and I'd like to know about baggage allowance"
    expected: "booking"
    context:
      max_response_time: 5.0
```

## Running Evaluations

### Programmatic Evaluation

```python
from intent_kit.evals import evaluate_node, load_dataset
from intent_kit import DAGBuilder

# Load dataset
dataset = load_dataset("datasets/classifier_node_llm.yaml")

# Create DAG with classifier
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it"
})
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "weather", "booking"],
                 description="Test classifier")
builder.set_entrypoints(["classifier"])

dag = builder.build()

# Run evaluation
result = evaluate_node(dataset, dag)

# Analyze results
print(f"Total tests: {result.total_count()}")
print(f"Passed: {result.passed_count()}")
print(f"Failed: {result.failed_count()}")
print(f"Accuracy: {result.accuracy():.1%}")

# Get failed tests
failed_tests = result.errors()
for test in failed_tests:
    print(f"Failed: '{test.input}' -> Expected: {test.expected}, Got: {test.actual}")
```

### Batch Evaluation

```python
from intent_kit.evals import run_all_evals
from pathlib import Path

# Run all evaluations in a directory
datasets_dir = Path("intent_kit/evals/datasets")
results = run_all_evals(datasets_dir)

# Print summary
for dataset_name, result in results.items():
    print(f"{dataset_name}: {result.accuracy():.1%} accuracy")
```

### Configuration-Based Evaluation

```python
# evaluation_config.yaml
evaluation:
  datasets:
    - path: "datasets/classifier_node_llm.yaml"
      enabled: true
    - path: "datasets/extractor_node.yaml"
      enabled: true
    - path: "datasets/action_node.yaml"
      enabled: false

  settings:
    max_workers: 4
    timeout: 30
    retry_attempts: 3

  reporting:
    output_dir: "results"
    format: "json"
    include_metrics: true
```

## Metrics and Analysis

### Performance Metrics

```python
# Get detailed metrics
result = evaluate_node(dataset, node)

# Timing metrics
for test_result in result.results:
    if test_result.elapsed_time:
        print(f"Response time: {test_result.elapsed_time:.2f}s")

    if test_result.metrics:
        print(f"Tokens used: {test_result.metrics.get('tokens', 'N/A')}")
        print(f"Cost: ${test_result.metrics.get('cost', 0):.4f}")
```

### Accuracy Analysis

```python
# Analyze accuracy by category
def analyze_accuracy_by_category(result):
    categories = {}

    for test_result in result.results:
        category = test_result.context.get('category', 'unknown')
        if category not in categories:
            categories[category] = {'passed': 0, 'total': 0}

        categories[category]['total'] += 1
        if test_result.passed:
            categories[category]['passed'] += 1

    for category, stats in categories.items():
        accuracy = stats['passed'] / stats['total']
        print(f"{category}: {accuracy:.1%} ({stats['passed']}/{stats['total']})")
```

### Error Analysis

```python
# Analyze common failure patterns
def analyze_errors(result):
    error_patterns = {}

    for test_result in result.errors():
        error_type = type(test_result.actual).__name__
        if error_type not in error_patterns:
            error_patterns[error_type] = []
        error_patterns[error_type].append(test_result.input)

    for error_type, inputs in error_patterns.items():
        print(f"{error_type}: {len(inputs)} occurrences")
        for input_text in inputs[:3]:  # Show first 3 examples
            print(f"  - {input_text}")
```

## Report Generation

### JSON Reports

```python
import json
from datetime import datetime

def generate_report(result, dataset_name):
    report = {
        "dataset": dataset_name,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": result.total_count(),
            "passed": result.passed_count(),
            "failed": result.failed_count(),
            "accuracy": result.accuracy()
        },
        "details": []
    }

    for test_result in result.results:
        report["details"].append({
            "input": test_result.input,
            "expected": test_result.expected,
            "actual": test_result.actual,
            "passed": test_result.passed,
            "elapsed_time": test_result.elapsed_time,
            "metrics": test_result.metrics
        })

    return report

# Save report
report = generate_report(result, "classifier_evaluation")
with open("results/classifier_report.json", "w") as f:
    json.dump(report, f, indent=2)
```

### HTML Reports

```python
def generate_html_report(results):
    html = """
    <html>
    <head>
        <title>Evaluation Results</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; }
            .test-case { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
            .passed { background: #d4edda; }
            .failed { background: #f8d7da; }
        </style>
    </head>
    <body>
        <h1>Evaluation Results</h1>
    """

    for dataset_name, result in results.items():
        html += f"""
        <div class="summary">
            <h2>{dataset_name}</h2>
            <p>Accuracy: {result.accuracy():.1%} ({result.passed_count()}/{result.total_count()})</p>
        </div>
        """

        for test_result in result.results:
            status_class = "passed" if test_result.passed else "failed"
            html += f"""
            <div class="test-case {status_class}">
                <strong>Input:</strong> {test_result.input}<br>
                <strong>Expected:</strong> {test_result.expected}<br>
                <strong>Actual:</strong> {test_result.actual}<br>
                <strong>Time:</strong> {test_result.elapsed_time:.2f}s
            </div>
            """

    html += "</body></html>"
    return html
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/evaluation.yml
name: Run Evaluations

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install uv
        uv sync

    - name: Run evaluations
      run: |
        uv run python -m intent_kit.evals.run_all_evals
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: evaluation-results
        path: results/
```

### Regression Testing

```python
def check_regression(current_result, baseline_result, threshold=0.05):
    """Check if performance has regressed significantly."""
    current_accuracy = current_result.accuracy()
    baseline_accuracy = baseline_result.accuracy()

    if current_accuracy < baseline_accuracy - threshold:
        print(f"⚠️  Performance regression detected!")
        print(f"Baseline: {baseline_accuracy:.1%}")
        print(f"Current: {current_accuracy:.1%}")
        print(f"Regression: {baseline_accuracy - current_accuracy:.1%}")
        return False

    print(f"✅ No significant regression detected")
    return True
```

## Best Practices

### 1. Comprehensive Test Coverage

```yaml
# Include various input types
test_cases:
  # Normal cases
  - input: "Hello"
    expected: "greet"

  # Edge cases
  - input: ""
    expected: "clarification"

  # Boundary cases
  - input: "A" * 1000  # Very long input
    expected: "greet"

  # Special characters
  - input: "Hello! How are you? 😊"
    expected: "greet"
```

### 2. Realistic Test Data

```yaml
# Use realistic, diverse test data
test_cases:
  - input: "Hi there, how's it going?"
    expected: "greet"
    context:
      user_demographic: "casual"

  - input: "Good morning, sir. How may I assist you today?"
    expected: "greet"
    context:
      user_demographic: "formal"
```

### 3. Performance Benchmarks

```yaml
# Include performance expectations
test_cases:
  - input: "Simple greeting"
    expected: "greet"
    context:
      max_response_time: 1.0
      max_tokens: 100

  - input: "Complex multi-intent request"
    expected: "multi_intent"
    context:
      max_response_time: 5.0
      max_tokens: 500
```

### 4. Regular Evaluation

```bash
# Set up automated evaluation
# Add to your CI/CD pipeline
uv run python -m intent_kit.evals.run_all_evals --output-dir results --format json

# Check for regressions
python scripts/check_regression.py results/current.json results/baseline.json
```
