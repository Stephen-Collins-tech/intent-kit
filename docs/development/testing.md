# Testing

Intent Kit includes comprehensive testing infrastructure to ensure reliability and correctness.

## Test Structure

The test suite is organized in the `tests/` directory and covers:

- **Unit tests**: Individual component testing
- **Integration tests**: End-to-end workflow testing
- **Evaluation tests**: Performance and accuracy benchmarking

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=intent_kit

# Run specific test file
pytest tests/test_graph.py

# Run with verbose output
pytest -v
```

## Test Categories

### Unit Tests
- Node functionality (actions, classifiers, splitters)
- Graph building and routing
- Context management
- Parameter extraction and validation

### Integration Tests
- Complete workflow execution
- Multi-intent routing
- Error handling and recovery
- LLM integration

### Evaluation Tests
- Performance benchmarking
- Accuracy measurement
- Regression testing

## Writing Tests

### Example Test Structure

```python
import pytest
from intent_kit import IntentGraphBuilder, action

def test_simple_action():
    """Test basic action execution."""
    greet_action = action(
        name="greet",
        description="Greet user",
        action_func=lambda name: f"Hello {name}!",
        param_schema={"name": str}
    )
    
    graph = IntentGraphBuilder().root(greet_action).build()
    result = graph.route("Hello Alice")
    
    assert result.success
    assert result.output == "Hello Alice!"
```

### Test Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Test both success and failure cases**
3. **Mock external dependencies** (LLM APIs, etc.)
4. **Use fixtures** for common setup
5. **Test edge cases** and error conditions

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Every push to main branch
- Coverage reports are generated and tracked

## Debugging Tests

```bash
# Run tests with debug output
pytest -s

# Run specific test with debugger
pytest tests/test_graph.py::test_specific_function -s

# Generate coverage report
pytest --cov=intent_kit --cov-report=html
```

## Performance Testing

Use the evaluation framework for performance testing:

```python
from intent_kit.evals import run_eval, load_dataset

# Load performance test dataset
dataset = load_dataset("tests/performance_dataset.yaml")
result = run_eval(dataset, your_graph)

# Check performance metrics
print(f"Average response time: {result.avg_response_time()}ms")
print(f"Throughput: {result.throughput()} requests/second")
```