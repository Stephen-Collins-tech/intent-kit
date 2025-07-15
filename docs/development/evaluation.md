# Evaluation

Intent Kit provides a comprehensive evaluation framework for testing and benchmarking your intent graphs.

## Overview

The evaluation system allows you to:
- Test your graphs against real datasets
- Measure accuracy and performance
- Track regressions over time
- Generate detailed reports

## Quick Start

```python
from intent_kit.evals import run_eval, load_dataset
from intent_kit import IntentGraphBuilder, action

# Create a simple graph
greet_action = action(
    name="greet",
    description="Greet user",
    action_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
)

graph = IntentGraphBuilder().root(greet_action).build()

# Load test dataset
dataset = load_dataset("tests/datasets/greeting.yaml")

# Run evaluation
result = run_eval(dataset, graph)

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

result = run_eval(dataset, graph)
```

### With Custom Metrics

```python
from intent_kit.evals import run_eval, EvaluationConfig

config = EvaluationConfig(
    include_timing=True,
    include_confidence=True,
    save_detailed_results=True
)

result = run_eval(dataset, graph, config=config)
```

### Batch Evaluation

```python
from intent_kit.evals import run_batch_eval

# Evaluate multiple graphs
graphs = [graph1, graph2, graph3]
results = run_batch_eval(dataset, graphs)

for name, result in results.items():
    print(f"{name}: {result.accuracy():.1%} accuracy")
```

## Results and Reports

### Available Metrics

- **Accuracy**: Percentage of correct predictions
- **Response Time**: Average processing time
- **Confidence**: Model confidence scores
- **Error Analysis**: Detailed error breakdown

### Saving Reports

```python
# Save as Markdown
result.save_markdown("evaluation_report.md")

# Save as JSON
result.save_json("evaluation_results.json")

# Save as CSV
result.save_csv("evaluation_data.csv")
```

### Report Formats

#### Markdown Report
```markdown
# Evaluation Report

## Summary
- Accuracy: 95.2%
- Average Response Time: 125ms
- Total Test Cases: 100

## Detailed Results
| Test Case | Expected | Actual | Status |
|-----------|----------|--------|--------|
| "Hello Alice" | "Hello Alice!" | "Hello Alice!" | ✅ |
```

#### JSON Report
```json
{
  "summary": {
    "accuracy": 0.952,
    "avg_response_time": 125,
    "total_cases": 100
  },
  "detailed_results": [...]
}
```

## Advanced Features

### Custom Metrics

```python
def custom_metric(expected, actual):
    """Custom similarity metric."""
    return similarity_score(expected, actual)

config = EvaluationConfig(
    custom_metrics={"similarity": custom_metric}
)
```

### Regression Testing

```python
from intent_kit.evals import compare_results

# Compare with previous results
previous_result = load_previous_results("baseline.json")
regression = compare_results(previous_result, current_result)

if regression.detected:
    print(f"Regression detected: {regression.details}")
```

### Mock Mode

For testing without API calls:

```python
config = EvaluationConfig(mock_mode=True)
result = run_eval(dataset, graph, config=config)
```

## Best Practices

1. **Use diverse datasets** that cover edge cases
2. **Test with real-world data** when possible
3. **Track metrics over time** to detect regressions
4. **Include timing benchmarks** for performance-critical applications
5. **Document your evaluation methodology**

## Integration with CI/CD

```yaml
# .github/workflows/eval.yml
name: Evaluation
on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v3
        with:
          python-version: '3.11'
      - run: pip install intentkit-py[dev]
      - run: python -m intent_kit.evals.run_all_evals
      - run: |
          # Check for regressions
          python -c "
          from intent_kit.evals import check_regressions
          check_regressions('baseline.json', 'results.json')
          "
```