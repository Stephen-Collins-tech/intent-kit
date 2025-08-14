# Performance Monitoring

Intent Kit provides comprehensive performance monitoring tools to help you optimize your DAGs and track execution metrics.

## Performance Metrics

### Basic Performance Tracking

Track execution time and performance metrics:

```python
import time
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

def greet(name: str) -> str:
    return f"Hello {name}!"

# Create DAG
builder = DAGBuilder()
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

# Track execution time
start_time = time.time()
result = run_dag(dag, "Hello Alice", context)
end_time = time.time()

execution_time = end_time - start_time
print(f"Execution time: {execution_time:.3f}s")
print(f"Result: {result.data}")
```

### Performance Analysis

Analyze performance across multiple executions:

```python
import statistics
from intent_kit import run_dag

def benchmark_dag(dag, test_inputs, context):
    """Benchmark DAG performance with multiple inputs."""
    timings = []
    results = []

    for input_text in test_inputs:
        start_time = time.time()
        result = run_dag(dag, input_text, context)
        end_time = time.time()

        timings.append(end_time - start_time)
        results.append(result)

    # Calculate statistics
    avg_time = statistics.mean(timings)
    min_time = min(timings)
    max_time = max(timings)
    std_dev = statistics.stdev(timings) if len(timings) > 1 else 0

    print(f"Performance Summary:")
    print(f"  Average time: {avg_time:.3f}s")
    print(f"  Min time: {min_time:.3f}s")
    print(f"  Max time: {max_time:.3f}s")
    print(f"  Std deviation: {std_dev:.3f}s")
    print(f"  Total executions: {len(timings)}")

    return {
        "timings": timings,
        "results": results,
        "stats": {
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "std_dev": std_dev
        }
    }

# Use for benchmarking
test_inputs = ["Hello Alice", "Hi Bob", "Greet Charlie"]
context = DefaultContext()
performance_data = benchmark_dag(dag, test_inputs, context)
```

## ReportUtil

The `ReportUtil` class generates comprehensive performance reports for your DAGs.

### Basic Performance Report

```python
from intent_kit.utils.report_utils import format_execution_results
from intent_kit.utils.perf_util import PerfUtil, collect

# Your DAG and test inputs
dag = builder.build()
test_inputs = ["Hello Alice", "What's 2 + 3?", "Weather in NYC"]

results = []
timings = []

# Run tests with timing
with PerfUtil("full test run") as perf:
    for test_input in test_inputs:
        with collect(test_input, timings):
            result = run_dag(dag, test_input, context)
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
- **Performance Breakdown** - Detailed timing for each step
- **Error Analysis** - Any failures or issues encountered

## Execution Tracing

Enable detailed execution tracing to understand performance bottlenecks.

### Enable Tracing

```python
from intent_kit import DAGBuilder

dag = DAGBuilder.from_json(dag_config)
```

### Trace Information

Tracing provides:

- **Node Execution Times** - How long each classifier and action takes
- **Decision Paths** - Which nodes were visited and why
- **Parameter Extraction** - Time spent extracting parameters
- **LLM Calls** - Individual LLM request timing
- **Error Details** - Detailed error information with timing

## Performance Optimization

### 1. Node-Level Optimization

Optimize individual nodes for better performance:

```python
# Optimize action nodes
def optimized_greet(name: str) -> str:
    """Optimized greeting function."""
    # Use string formatting instead of concatenation
    return f"Hello {name}!"

# Optimize classifier nodes
def custom_classifier(input_text: str) -> str:
    """Custom classifier for better performance."""
    # Use simple pattern matching for common cases
    if "hello" in input_text.lower():
        return "greet"
    elif "weather" in input_text.lower():
        return "weather"
    return "unknown"
```

### 2. Caching Strategies

Implement caching for expensive operations:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_calculation(input_data: str) -> str:
    """Cache expensive calculations."""
    # Expensive computation here
    return f"Processed: {input_data}"

def cached_action(input_data: str, context=None) -> str:
    """Action with caching."""
    result = expensive_calculation(input_data)

    if context:
        context.set("cached_result", result, modified_by="cached_action")

    return result
```

### 3. Context Optimization

Optimize context usage for better performance:

```python
def optimized_context_usage(context):
    """Optimize context operations."""
    # Use snapshots for read-only access
    snapshot = context.snapshot()

    # Batch context updates
    updates = {
        "user.name": "Alice",
        "user.preferences": {"theme": "dark"},
        "session.start_time": time.time()
    }
    context.apply_patch(updates, provenance="batch_update")

    # Clear temporary data
    context.delete("temp_data")
```

## Monitoring Best Practices

### 1. **Set Performance Baselines**

```python
def establish_baseline(dag, test_inputs):
    """Establish performance baseline."""
    context = DefaultContext()
    baseline = benchmark_dag(dag, test_inputs, context)

    print(f"Performance Baseline:")
    print(f"  Target avg time: {baseline['stats']['avg_time']:.3f}s")
    print(f"  Target max time: {baseline['stats']['max_time']:.3f}s")

    return baseline
```

### 2. **Monitor Performance Trends**

```python
import json
from datetime import datetime

def log_performance_metrics(performance_data, test_name):
    """Log performance metrics for trend analysis."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "test_name": test_name,
        "avg_time": performance_data["stats"]["avg_time"],
        "max_time": performance_data["stats"]["max_time"],
        "execution_count": len(performance_data["timings"])
    }

    with open("performance_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

### 3. **Alert on Performance Degradation**

```python
def check_performance_degradation(current_stats, baseline_stats, threshold=0.2):
    """Check for performance degradation."""
    avg_degradation = (current_stats["avg_time"] - baseline_stats["avg_time"]) / baseline_stats["avg_time"]

    if avg_degradation > threshold:
        print(f"WARNING: Performance degraded by {avg_degradation:.1%}")
        print(f"  Baseline: {baseline_stats['avg_time']:.3f}s")
        print(f"  Current: {current_stats['avg_time']:.3f}s")
        return True

    return False
```

## Performance Testing

### Automated Performance Tests

```python
import pytest
import time

def test_dag_performance():
    """Test DAG performance meets requirements."""
    dag = create_test_dag()
    context = DefaultContext()

    test_inputs = ["Hello Alice", "Hi Bob", "Greet Charlie"]

    # Measure performance
    start_time = time.time()
    for input_text in test_inputs:
        result = run_dag(dag, input_text, context)
        assert result.data is not None

    total_time = time.time() - start_time
    avg_time = total_time / len(test_inputs)

    # Assert performance requirements
    assert avg_time < 1.0, f"Average execution time {avg_time:.3f}s exceeds 1.0s limit"
    assert total_time < 5.0, f"Total execution time {total_time:.3f}s exceeds 5.0s limit"
```

### Load Testing

```python
import concurrent.futures
import threading

def load_test_dag(dag, num_requests=100, max_workers=10):
    """Load test DAG with concurrent requests."""
    context = DefaultContext()
    test_input = "Hello Alice"

    def single_request():
        return run_dag(dag, test_input, context)

    # Run concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(single_request) for _ in range(num_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    print(f"Load test completed: {len(results)} requests")
    return results
```

## Performance Monitoring Tools

### Custom Performance Monitor

```python
class PerformanceMonitor:
    """Custom performance monitoring class."""

    def __init__(self):
        self.metrics = []

    def record_execution(self, input_text, execution_time, success):
        """Record execution metrics."""
        metric = {
            "timestamp": datetime.utcnow(),
            "input": input_text,
            "execution_time": execution_time,
            "success": success
        }
        self.metrics.append(metric)

    def get_summary(self):
        """Get performance summary."""
        if not self.metrics:
            return {}

        times = [m["execution_time"] for m in self.metrics]
        success_rate = sum(1 for m in self.metrics if m["success"]) / len(self.metrics)

        return {
            "total_executions": len(self.metrics),
            "avg_time": statistics.mean(times),
            "success_rate": success_rate,
            "min_time": min(times),
            "max_time": max(times)
        }

# Use the monitor
monitor = PerformanceMonitor()

def monitored_execution(dag, input_text, context):
    """Execute DAG with performance monitoring."""
    start_time = time.time()

    try:
        result = run_dag(dag, input_text, context)
        success = True
    except Exception as e:
        result = None
        success = False

    execution_time = time.time() - start_time
    monitor.record_execution(input_text, execution_time, success)

    return result
```

## Best Practices

### 1. **Regular Performance Testing**
- Run performance tests regularly
- Monitor for performance regressions
- Set up automated performance alerts

### 2. **Optimize Critical Paths**
- Identify and optimize slow nodes
- Use caching for expensive operations
- Optimize context operations

### 3. **Monitor Resource Usage**
- Track memory usage patterns
- Monitor context size growth
- Watch for memory leaks

### 4. **Profile and Optimize**
- Use profiling tools to identify bottlenecks
- Optimize the most frequently executed paths
- Consider async operations for I/O-bound tasks

### 5. **Set Performance Targets**
- Establish performance baselines
- Set realistic performance targets
- Monitor performance trends over time
