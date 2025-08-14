# Testing

Intent Kit provides comprehensive testing tools to ensure your DAGs work correctly and reliably.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=intent_kit

# Run specific test file
uv run pytest tests/test_dag.py

# Run with verbose output
uv run pytest -v
```

## Test Categories

### Unit Tests
- Node functionality (classifiers, extractors, actions)
- DAG building and execution
- Context management
- Parameter extraction and validation

### Integration Tests
- Complete workflow execution
- Intent routing
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
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

def test_simple_action():
    """Test basic action execution."""
    def greet(name: str, **kwargs) -> str:
        return f"Hello {name}!"

    # Create DAG
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
    context = DefaultContext()
    result, context = run_dag(dag, "Hello Alice")

    assert result.data == "Hello Alice!"
```

### Test Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Test both success and failure cases**
3. **Mock external dependencies** (LLM APIs, etc.)
4. **Use fixtures** for common setup
5. **Test edge cases** and error conditions

## Test Fixtures

### Common DAG Fixtures

```python
import pytest
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

@pytest.fixture
def simple_dag():
    """Create a simple DAG for testing."""
    def greet(name: str, **kwargs) -> str:
        return f"Hello {name}!"

    builder = DAGBuilder()
    builder.add_node("classifier", "classifier",
                     output_labels=["greet"],
                     description="Main classifier",
                     llm_config={
                         "provider": "openrouter",
                         "model": "google/gemma-2-9b-it"
                     })
    builder.add_node("extract_name", "extractor",
                     param_schema={"name": str},
                     description="Extract name")
    builder.add_node("greet_action", "action",
                     action=greet,
                     description="Greet user")
    builder.add_edge("classifier", "extract_name", "greet")
    builder.add_edge("extract_name", "greet_action", "success")
    builder.set_entrypoints(["classifier"])

    return builder.build()

@pytest.fixture
def test_context():
    """Create a test context."""
    return DefaultContext()

def test_greeting_workflow(simple_dag, test_context):
    """Test the complete greeting workflow."""
    result, test_context = run_dag(simple_dag, "Hello Alice")
    assert result.data == "Hello Alice!"
```

### Mock LLM Fixtures

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    mock_service = Mock()
    mock_service.generate_text.return_value = "greet"
    return mock_service

def test_classifier_with_mock(simple_dag, test_context, mock_llm_service):
    """Test classifier with mocked LLM service."""
    # Inject mock service into context
    test_context.set("llm_service", mock_llm_service)

    result, test_context = run_dag(simple_dag, "Hello Alice")
    assert result.data == "Hello Alice!"
```

## Testing Different Node Types

### Testing Classifier Nodes

```python
def test_classifier_node():
    """Test classifier node functionality."""
    def custom_classifier(input_text: str, **kwargs) -> str:
        if "hello" in input_text.lower():
            return "greet"
        return "unknown"

    builder = DAGBuilder()
    builder.add_node("classifier", "classifier",
                     output_labels=["greet", "unknown"],
                     description="Test classifier",
                     classification_func=custom_classifier)
    builder.add_node("greet_action", "action",
                     action=lambda: "Hello!",
                     description="Greet action")
    builder.add_edge("classifier", "greet_action", "greet")
    builder.set_entrypoints(["classifier"])

    dag = builder.build()
    context = DefaultContext()

    # Test greeting input
    result, context = run_dag(dag, "Hello there")
    assert result.data == "Hello!"

    # Test unknown input
    result, context = run_dag(dag, "Random text")
    assert result.data is None  # No action executed
```

### Testing Extractor Nodes

```python
def test_extractor_node():
    """Test extractor node functionality."""
    def test_action(name: str, age: int, **kwargs) -> str:
        return f"{name} is {age} years old"

    builder = DAGBuilder()
    builder.add_node("extractor", "extractor",
                     param_schema={"name": str, "age": int},
                     description="Extract name and age",
                     output_key="extracted_params")
    builder.add_node("action", "action",
                     action=test_action,
                     description="Test action")
    builder.add_edge("extractor", "action", "success")
    builder.set_entrypoints(["extractor"])

    dag = builder.build()
    context = DefaultContext()

    # Mock extracted parameters
    context.set("extracted_params", {"name": "Alice", "age": 25})

    result, context = run_dag(dag, "Test input")
    assert result.data == "Alice is 25 years old"
```

### Testing Action Nodes

```python
def test_action_node():
    """Test action node functionality."""
    def test_action(name: str, **kwargs) -> str:
        return f"Hello {name}!"

    builder = DAGBuilder()
    builder.add_node("action", "action",
                     action=test_action,
                     description="Test action")
    builder.set_entrypoints(["action"])

    dag = builder.build()
    context = DefaultContext()

    # Mock parameters
    context.set("extracted_params", {"name": "Bob"})

    result, context = run_dag(dag, "Test input")
    assert result.data == "Hello Bob!"
```

## Testing Error Conditions

### Testing Invalid Inputs

```python
def test_invalid_input_handling(simple_dag, test_context):
    """Test handling of invalid inputs."""
    # Test with empty input
    result, test_context = run_dag(simple_dag, "")
    assert result.data is None or "error" in str(result.data).lower()

    # Test with None input
    result, test_context = run_dag(simple_dag, None)
    assert result.data is None or "error" in str(result.data).lower()
```

### Testing Context Errors

```python
def test_context_error_handling():
    """Test context error handling."""
    def failing_action(**kwargs) -> str:
        raise ValueError("Test error")

    builder = DAGBuilder()
    builder.add_node("action", "action",
                     action=failing_action,
                     description="Failing action")
    builder.set_entrypoints(["action"])

    dag = builder.build()
    context = DefaultContext()

    # Test error handling
    result, context = run_dag(dag, "Test input")
    assert result.data is None or "error" in str(result.data).lower()
```

## Integration Testing

### Testing Complete Workflows

```python
def test_complete_workflow():
    """Test a complete workflow with multiple nodes."""
    def greet(name: str, **kwargs) -> str:
        return f"Hello {name}!"

    def get_weather(city: str, **kwargs) -> str:
        return f"Weather in {city} is sunny"

    # Create complex DAG
    builder = DAGBuilder()
    builder.add_node("classifier", "classifier",
                     output_labels=["greet", "weather"],
                     description="Main classifier")
    builder.add_node("extract_greet", "extractor",
                     param_schema={"name": str},
                     description="Extract name")
    builder.add_node("extract_weather", "extractor",
                     param_schema={"city": str},
                     description="Extract city")
    builder.add_node("greet_action", "action",
                     action=greet,
                     description="Greet action")
    builder.add_node("weather_action", "action",
                     action=get_weather,
                     description="Weather action")

    # Connect nodes
    builder.add_edge("classifier", "extract_greet", "greet")
    builder.add_edge("extract_greet", "greet_action", "success")
    builder.add_edge("classifier", "extract_weather", "weather")
    builder.add_edge("extract_weather", "weather_action", "success")
    builder.set_entrypoints(["classifier"])

    dag = builder.build()
    context = DefaultContext()

    # Test greeting workflow
    result, context = run_dag(dag, "Hello Alice")
    assert result.data == "Hello Alice!"

    # Test weather workflow
    result, context = run_dag(dag, "Weather in San Francisco")
    assert result.data == "Weather in San Francisco is sunny"
```

## Performance Testing

Use the evaluation framework for performance testing:

```python
from intent_kit.evals import run_eval, load_dataset

# Load performance test dataset
dataset = load_dataset("tests/performance_dataset.yaml")
result = run_eval(dataset, your_dag)

# Check performance metrics
print(f"Average response time: {result.avg_response_time()}ms")
print(f"Throughput: {result.throughput()} requests/second")
```

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Every push to main branch
- Coverage reports are generated and tracked

## Debugging Tests

```bash
# Run tests with debug output
uv run pytest -s

# Run specific test with debugger
uv run pytest tests/test_dag.py::test_specific_function -s

# Generate coverage report
uv run pytest --cov=intent_kit --cov-report=html
```

## Best Practices

### 1. **Test Structure**
- Organize tests by functionality
- Use descriptive test names
- Group related tests in classes

### 2. **Test Data**
- Use realistic test data
- Test edge cases and boundary conditions
- Include both valid and invalid inputs

### 3. **Mocking**
- Mock external dependencies
- Use fixtures for common setup
- Test error conditions explicitly

### 4. **Coverage**
- Aim for high test coverage
- Focus on critical paths
- Test error handling thoroughly

### 5. **Maintenance**
- Keep tests up to date with code changes
- Refactor tests when needed
- Use parameterized tests for similar scenarios
