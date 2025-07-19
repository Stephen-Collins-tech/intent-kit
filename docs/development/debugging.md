# Debugging

Intent Kit provides comprehensive debugging tools to help you troubleshoot and optimize your intent graphs.

## Debug Output

### Basic Debugging

Enable debug output to see detailed execution information:

```python
from intent_kit import IntentGraphBuilder, action
from intent_kit.context import IntentContext

# Create a graph with debug enabled
graph = IntentGraphBuilder().root(action(...)).build()
context = IntentContext(session_id="debug_session", debug=True)

result = graph.route("Hello Alice", context=context)
print(context.debug_log)  # View detailed execution log
```

### Debug Log Format

The debug log shows:
- Node execution order
- Parameter extraction results
- Context updates
- Error details

```python
# Example debug output
{
  "session_id": "debug_session",
  "execution_path": [
    {"node": "root_classifier", "input": "Hello Alice", "output": "greet"},
    {"node": "greet_action", "params": {"name": "Alice"}, "output": "Hello Alice!"}
  ],
  "context_updates": [...],
  "timing": {"total_ms": 45, "classifier_ms": 12, "action_ms": 33}
}
```

## Context Debugging

### Context Dependencies

Track how context flows through your graph:

```python
from intent_kit.context.debug import get_context_dependencies

# Analyze context dependencies
dependencies = get_context_dependencies(graph)
print("Context dependencies:", dependencies)
```

### Context Validation

Validate that context is properly managed:

```python
from intent_kit.context.debug import validate_context_flow

# Check for context issues
issues = validate_context_flow(graph, context)
if issues:
    print("Context issues found:", issues)
```

### Context Tracing

Trace context execution step by step:

```python
from intent_kit.context.debug import trace_context_execution

# Get detailed context trace
trace = trace_context_execution(graph, "Hello Alice", context)
for step in trace:
    print(f"Step {step.step}: {step.node} -> {step.context_changes}")
```

## Node-Level Debugging

### Action Node Debugging

```python
# Enable parameter extraction debugging
action_node = action(
    name="debug_action",
    description="Debug action",
    action_func=lambda **kwargs: str(kwargs),
    param_schema={"name": str},
    debug=True
)

result = action_node.execute("Hello Alice")
print(f"Extracted params: {result.extracted_params}")
print(f"Validation errors: {result.validation_errors}")
```

### Classifier Node Debugging

```python
# Enable classifier debugging
classifier = llm_classifier(
    name="debug_classifier",
    children=[action1, action2],
    debug=True
)

result = classifier.classify("Hello Alice")
print(f"Classification confidence: {result.confidence}")
print(f"Alternative intents: {result.alternatives}")
```

## Visualization Debugging

### Graph Visualization

Visualize your graph structure for debugging:

```python
from intent_kit.utils.visualization import visualize_graph

# Generate interactive graph visualization
visualize_graph(graph, output_file="debug_graph.html")
```

### Execution Path Visualization

Visualize the execution path for a specific input:

```python
from intent_kit.utils.visualization import visualize_execution_path

# Show execution path
visualize_execution_path(graph, "Hello Alice", output_file="execution_path.html")
```

## Performance Debugging

### Timing Analysis

```python
import time
from intent_kit.context import IntentContext

context = IntentContext(session_id="perf_debug", timing=True)
result = graph.route("Hello Alice", context=context)

print(f"Total execution time: {context.timing.total_ms}ms")
print(f"Classifier time: {context.timing.classifier_ms}ms")
print(f"Action time: {context.timing.action_ms}ms")
```

### Memory Usage

```python
import psutil
import os

process = psutil.Process(os.getpid())
before_memory = process.memory_info().rss

result = graph.route("Hello Alice")

after_memory = process.memory_info().rss
print(f"Memory used: {(after_memory - before_memory) / 1024 / 1024:.2f} MB")
```

## Error Debugging

### Error Tracing

```python
try:
    result = graph.route("Invalid input")
except Exception as e:
    print(f"Error: {e}")
    print(f"Error context: {e.context}")
    print(f"Error node: {e.node}")
```

### Validation Errors

```python
# Check parameter validation
action_node = action(
    name="test",
    action_func=lambda x: x,
    param_schema={"x": int}
)

result = action_node.execute("not a number")
if not result.success:
    print(f"Validation errors: {result.validation_errors}")
```

## Logging

### Configure Logging

```python
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("intent_kit")

# Enable specific component logging
logging.getLogger("intent_kit.graph").setLevel(logging.DEBUG)
logging.getLogger("intent_kit.context").setLevel(logging.DEBUG)
```

### Custom Logging

```python
from intent_kit.context import IntentContext

class DebugContext(IntentContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug_log = []
    
    def log(self, message, level="INFO"):
        self.debug_log.append({"message": message, "level": level, "timestamp": time.time()})

context = DebugContext(session_id="custom_debug")
result = graph.route("Hello Alice", context=context)
print(context.debug_log)
```

## Best Practices

1. **Use debug mode** during development
2. **Enable timing** for performance-critical applications
3. **Validate context flow** for complex graphs
4. **Use visualization** for graph structure debugging
5. **Log errors** with sufficient context
6. **Test with edge cases** to catch issues early

## Common Issues

### Parameter Extraction Failures

```python
# Debug parameter extraction
action_node = action(
    name="debug",
    action_func=lambda name, age: f"{name} is {age}",
    param_schema={"name": str, "age": int}
)

result = action_node.execute("Alice is 25")
print(f"Raw extraction: {result.raw_extraction}")
print(f"Validated params: {result.extracted_params}")
```

### Context State Issues

```python
# Check context state
print(f"Context keys: {list(context.keys())}")
print(f"Context values: {dict(context)}")

# Validate context updates
for key, value in context.items():
    print(f"{key}: {value} (type: {type(value)})")
```

### LLM Integration Issues

```python
# Test LLM configuration
from intent_kit.services.llm_factory import LLMFactory

factory = LLMFactory()
client = factory.create_client({
    "provider": "openai",
    "api_key": "your-key",
    "model": "gemma3:27b"
})

# Test basic LLM call
try:
    response = client.chat.completions.create(
        model="gemma3:27b",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("LLM connection successful")
except Exception as e:
    print(f"LLM connection failed: {e}")
```