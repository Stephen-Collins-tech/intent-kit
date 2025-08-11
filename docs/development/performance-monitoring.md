# Performance Monitoring

Intent Kit v0.5.0 introduces comprehensive performance monitoring capabilities to help you track and optimize your AI workflows.

## Overview

Performance monitoring in Intent Kit includes:

- **PerfUtil** - Utility for measuring execution time
- **ReportUtil** - Generate detailed performance reports
- **Token Usage Tracking** - Real-time token consumption and cost calculation
- **Execution Tracing** - Detailed logs of decision paths and performance

## PerfUtil

The `PerfUtil` class provides flexible timing utilities for measuring code execution time.

### Basic Usage

```python
from intent_kit.utils.perf_util import PerfUtil

# Manual timing
perf = PerfUtil("my task", auto_print=False)
perf.start()
# ... your code here ...
perf.stop()
print(perf.format())  # "my task: 1.234 seconds elapsed"
```

### Context Manager Usage

```python
from intent_kit.utils.perf_util import PerfUtil

# Automatic timing with context manager
with PerfUtil("my task") as perf:
    # ... your code here ...
    # Automatically prints timing on exit
```

### Collecting Multiple Timings

```python
from intent_kit.utils.perf_util import PerfUtil

timings = []

# Collect multiple timings
with PerfUtil.collect("task1", timings):
    # ... code for task1 ...

with PerfUtil.collect("task2", timings):
    # ... code for task2 ...

# Generate summary table
PerfUtil.report_table(timings, "My Performance Summary")
```

## ReportUtil

The `ReportUtil` class generates comprehensive performance reports for your intent graphs.

### Basic Performance Report

```python
from intent_kit.utils.report_utils import format_execution_results
from intent_kit.utils.perf_util import PerfUtil, collect

# Your graph and test inputs
graph = IntentGraphBuilder().root(classifier).build()
test_inputs = ["Hello Alice", "What's 2 + 3?", "Weather in NYC"]

results = []
timings = []

# Run tests with timing
with PerfUtil("full test run") as perf:
    for test_input in test_inputs:
        with collect(test_input, timings):
            result = graph.route(test_input)
            results.append(result)

# Generate report
report = format_execution_results(
    results=results,
    llm_config=llm_config,
    perf_info=perf.format(),
    timings=timings,
)

print(report)
```

### Report Features

The generated report includes:

- **Execution Summary** - Total time, average time per request
- **Individual Results** - Each input/output with timing
- **Token Usage** - Token consumption and estimated costs
- **Performance Breakdown** - Detailed timing for each step
- **Error Analysis** - Any failures or issues encountered

## Token Usage Tracking

Intent Kit automatically tracks token usage across all LLM operations.

### Cost Calculation

```python
from intent_kit.utils.report_utils import format_execution_results

# Get cost information from results
for result in results:
    if result.token_usage:
        print(f"Input tokens: {result.token_usage.input_tokens}")
        print(f"Output tokens: {result.token_usage.output_tokens}")
        print(f"Estimated cost: ${result.token_usage.estimated_cost:.4f}")
```

### Provider-Specific Tracking

Different AI providers have different pricing models:

- **OpenAI** - Per-token pricing with model-specific rates
- **Anthropic** - Per-token pricing with Claude model rates
- **Google AI** - Per-token pricing with Gemini model rates
- **Ollama** - Local models typically have no token costs

## Execution Tracing

Enable detailed execution tracing to understand performance bottlenecks.

### Enable Tracing

```python
from intent_kit import IntentGraphBuilder

graph = (
    IntentGraphBuilder()
    .with_json(graph_config)
    .with_functions(function_registry)
    .with_context_trace(True)  # Enable detailed tracing
    .with_debug_context(True)  # Enable debug information
    .build()
)
```

### Trace Information

Tracing provides:

- **Node Execution Times** - How long each classifier and action takes
- **Decision Paths** - Which nodes were visited and why
- **Parameter Extraction** - Time spent extracting parameters
- **LLM Calls** - Individual LLM request timing and token usage
- **Error Details** - Detailed error information with timing

## Performance Best Practices

### 1. Use Context Managers

```python
# Good: Automatic timing and cleanup
with PerfUtil("my operation") as perf:
    result = graph.route(input_text)

# Good: Collect multiple timings
timings = []
with PerfUtil.collect("operation", timings):
    result = graph.route(input_text)
```

### 2. Monitor Token Usage

```python
# Check token usage for cost optimization
for result in results:
    if result.token_usage:
        total_cost += result.token_usage.estimated_cost
        print(f"Total cost so far: ${total_cost:.4f}")
```

### 3. Profile Your Workflows

```python
# Profile different parts of your workflow
with PerfUtil.collect("classification", timings):
    # Classifier execution

with PerfUtil.collect("parameter_extraction", timings):
    # Parameter extraction

with PerfUtil.collect("action_execution", timings):
    # Action execution
```

### 4. Generate Regular Reports

```python
# Generate performance reports for monitoring
report = ReportUtil.format_execution_results(
    results=results,
    llm_config=llm_config,
    perf_info=perf.format(),
    timings=timings,
)

# Save reports for historical analysis
with open(f"performance_report_{date}.md", "w") as f:
    f.write(report)
```

## Integration with Evaluation

Performance monitoring integrates with the evaluation framework:

```python
from intent_kit.evals import run_eval, load_dataset

# Load test dataset
dataset = load_dataset("tests/my_tests.yaml")

# Run evaluation with performance tracking
results = run_eval(dataset, graph)

# Generate comprehensive report
report = ReportUtil.format_evaluation_results(
    results=results,
    dataset=dataset,
    llm_config=llm_config,
    include_performance=True
)
```

This provides both accuracy metrics and performance data in a single report.

## Example: Complete Performance Monitoring

```python
from intent_kit import IntentGraphBuilder
from intent_kit.utils.perf_util import PerfUtil
from intent_kit.utils.report_utils import ReportUtil

# Build your graph
graph = IntentGraphBuilder().root(classifier).build()

# Test inputs
test_inputs = [
    "Hello Alice",
    "What's 15 plus 7?",
    "Weather in San Francisco",
    "Help me",
    "Multiply 8 and 3",
]

results = []
timings = []

# Run tests with comprehensive monitoring
with PerfUtil("full test suite") as perf:
    for test_input in test_inputs:
        with PerfUtil.collect(test_input, timings):
            result = graph.route(test_input)
            results.append(result)

# Generate comprehensive report
report = ReportUtil.format_execution_results(
    results=results,
    llm_config=llm_config,
    perf_info=perf.format(),
    timings=timings,
)

print("Performance Report:")
print(report)

# Save for historical analysis
with open("performance_report.md", "w") as f:
    f.write(report)
```

This comprehensive monitoring approach helps you:

- **Optimize Performance** - Identify bottlenecks and slow operations
- **Control Costs** - Monitor token usage and estimated costs
- **Debug Issues** - Trace execution paths and identify problems
- **Track Improvements** - Compare performance over time
- **Validate Changes** - Ensure updates don't degrade performance
