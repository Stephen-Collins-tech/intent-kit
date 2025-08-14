# Utilities

Intent Kit provides a comprehensive set of utility modules that support core functionality, including type validation, text processing, performance monitoring, logging, and reporting.

## Overview

The utilities module includes:
- **Type Coercion** - Advanced type validation and conversion
- **Text Utils** - Text processing and manipulation
- **Performance Utils** - Performance monitoring and cost tracking
- **Logger** - Structured logging system
- **Report Utils** - Report generation and formatting
- **Typed Output** - Type-safe output handling

## Type Coercion

The `type_coercion` module provides robust type validation and conversion capabilities.

### Basic Type Validation

```python
from intent_kit.utils.type_coercion import validate_type, resolve_type

# Validate basic types
result = validate_type("42", int)
print(result)  # 42

result = validate_type("3.14", float)
print(result)  # 3.14

result = validate_type("true", bool)
print(result)  # True

# Handle invalid types
try:
    result = validate_type("not_a_number", int)
except TypeValidationError as e:
    print(f"Validation error: {e}")
```

### Complex Type Validation

```python
from intent_kit.utils.type_coercion import validate_raw_content

# Validate complex structures
data = {
    "name": "John",
    "age": "25",
    "scores": ["85", "92", "78"],
    "active": "true"
}

schema = {
    "name": str,
    "age": int,
    "scores": list,
    "active": bool
}

validated_data = validate_raw_content(data, dict)
print(validated_data)
# {
#     "name": "John",
#     "age": 25,
#     "scores": ["85", "92", "78"],
#     "active": True
# }
```

### Custom Type Validation

```python
from typing import Union, List
from intent_kit.utils.type_coercion import TypeValidationError

# Define custom validation rules
def validate_email(value: str) -> str:
    if "@" not in value:
        raise TypeValidationError(f"Invalid email format: {value}")
    return value

def validate_age(value: Union[int, str]) -> int:
    age = validate_type(value, int)
    if age < 0 or age > 150:
        raise TypeValidationError(f"Age must be between 0 and 150: {age}")
    return age

# Use custom validators
schema = {
    "email": validate_email,
    "age": validate_age,
    "tags": List[str]
}

data = {
    "email": "user@example.com",
    "age": "25",
    "tags": ["python", "ai", "ml"]
}

validated = validate_raw_content(data, dict)
```

## Text Utils

The `text_utils` module provides comprehensive text processing capabilities.

### Text Cleaning and Normalization

```python
from intent_kit.utils.text_utils import (
    clean_text, normalize_text, extract_keywords,
    calculate_similarity, split_text
)

# Clean and normalize text
text = "  Hello, World!  How are you?  "
cleaned = clean_text(text)
print(cleaned)  # "Hello, World! How are you?"

normalized = normalize_text(text)
print(normalized)  # "hello world how are you"

# Extract keywords
keywords = extract_keywords("Machine learning is a subset of artificial intelligence")
print(keywords)  # ["machine", "learning", "subset", "artificial", "intelligence"]
```

### Text Similarity

```python
from intent_kit.utils.text_utils import calculate_similarity

# Calculate similarity between texts
text1 = "Hello, how are you?"
text2 = "Hi, how are you doing?"
text3 = "What's the weather like?"

similarity_1_2 = calculate_similarity(text1, text2)
similarity_1_3 = calculate_similarity(text1, text3)

print(f"Similarity 1-2: {similarity_1_2:.2f}")  # Higher similarity
print(f"Similarity 1-3: {similarity_1_3:.2f}")  # Lower similarity
```

### Text Splitting and Chunking

```python
from intent_kit.utils.text_utils import split_text, chunk_text

# Split text into sentences
text = "Hello there. How are you? I'm doing well. Thanks for asking."
sentences = split_text(text)
print(sentences)
# ["Hello there.", "How are you?", "I'm doing well.", "Thanks for asking."]

# Chunk text for processing
long_text = "This is a very long text that needs to be chunked..."
chunks = chunk_text(long_text, max_chunk_size=100, overlap=20)
print(f"Created {len(chunks)} chunks")
```

### Advanced Text Processing

```python
from intent_kit.utils.text_utils import (
    extract_entities, detect_language, translate_text,
    summarize_text, extract_sentiment
)

# Extract named entities
text = "John Smith works at Google in San Francisco"
entities = extract_entities(text)
print(entities)  # {"PERSON": ["John Smith"], "ORG": ["Google"], "LOC": ["San Francisco"]}

# Detect language
language = detect_language("Bonjour, comment allez-vous?")
print(language)  # "fr"

# Extract sentiment
sentiment = extract_sentiment("I love this product! It's amazing.")
print(sentiment)  # {"positive": 0.9, "negative": 0.1}
```

## Performance Utils

The `perf_util` module provides comprehensive performance monitoring and cost tracking.

### Basic Performance Tracking

```python
from intent_kit.utils.perf_util import PerfUtil

# Initialize performance utility
perf = PerfUtil()

# Track execution time
with perf.timer("data_processing"):
    # Your code here
    import time
    time.sleep(1)

# Get timing information
timings = perf.get_timings()
print(timings)  # {"data_processing": 1.002}
```

### Cost Tracking

```python
from intent_kit.utils.perf_util import PerfUtil

perf = PerfUtil()

# Track token usage and costs
perf.record_tokens(
    provider="openrouter",
    model="google/gemma-2-9b-it",
    input_tokens=100,
    output_tokens=50
)

# Get cost information
costs = perf.get_costs()
print(costs)  # {"openrouter": {"google/gemma-2-9b-it": 0.0023}}

# Get total cost
total_cost = perf.get_total_cost()
print(f"Total cost: ${total_cost:.4f}")
```

### Performance Monitoring

```python
from intent_kit.utils.perf_util import PerfUtil

perf = PerfUtil()

# Monitor multiple operations
with perf.timer("classification"):
    # Classification logic
    pass

with perf.timer("extraction"):
    # Extraction logic
    pass

with perf.timer("action_execution"):
    # Action execution
    pass

# Get detailed performance report
report = perf.generate_report()
print(report)
# {
#     "timings": {
#         "classification": 0.5,
#         "extraction": 1.2,
#         "action_execution": 0.3
#     },
#     "costs": {...},
#     "summary": {
#         "total_time": 2.0,
#         "total_cost": 0.005
#     }
# }
```

### Memory Usage Tracking

```python
from intent_kit.utils.perf_util import PerfUtil
import psutil

perf = PerfUtil()

# Track memory usage
initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
perf.record_memory_usage("start", initial_memory)

# After processing
final_memory = psutil.Process().memory_info().rss / 1024 / 1024
perf.record_memory_usage("end", final_memory)

memory_usage = perf.get_memory_usage()
print(f"Memory used: {memory_usage['end'] - memory_usage['start']:.2f} MB")
```

## Logger

The `logger` module provides structured logging capabilities.

### Basic Logging

```python
from intent_kit.utils.logger import Logger

# Create logger instance
logger = Logger("my_component")

# Basic logging
logger.info("Component initialized")
logger.warning("Deprecated feature used")
logger.error("An error occurred", exc_info=True)
logger.debug("Debug information")
```

### Structured Logging

```python
from intent_kit.utils.logger import Logger

logger = Logger("dag_execution")

# Log with structured data
logger.info("DAG execution started", extra={
    "dag_id": "booking_flow",
    "user_id": "user123",
    "input_length": 50
})

logger.info("Node executed", extra={
    "node_id": "classifier",
    "execution_time": 0.5,
    "result": "weather"
})
```

### Log Configuration

```python
from intent_kit.utils.logger import Logger, configure_logging

# Configure logging
configure_logging(
    level="INFO",
    format="json",
    output_file="logs/app.log"
)

# Create logger with specific configuration
logger = Logger("custom_logger", level="DEBUG")
```

### Performance Logging

```python
from intent_kit.utils.logger import Logger

logger = Logger("performance")

# Log performance metrics
def log_performance_metrics(operation, duration, tokens=None, cost=None):
    logger.info("Performance metrics", extra={
        "operation": operation,
        "duration_seconds": duration,
        "tokens_used": tokens,
        "cost_usd": cost
    })

# Usage
log_performance_metrics("llm_generation", 1.5, tokens=150, cost=0.003)
```

## Report Utils

The `report_utils` module provides comprehensive reporting capabilities.

### Basic Report Generation

```python
from intent_kit.utils.report_utils import ReportGenerator

# Create report generator
reporter = ReportGenerator()

# Add data to report
reporter.add_section("execution_summary", {
    "total_requests": 100,
    "successful_requests": 95,
    "failed_requests": 5,
    "average_response_time": 1.2
})

reporter.add_section("cost_analysis", {
    "total_cost": 0.25,
    "cost_per_request": 0.0025,
    "provider_breakdown": {
        "openai": 0.15,
        "anthropic": 0.10
    }
})

# Generate report
report = reporter.generate_report()
print(report)
```

### Performance Reports

```python
from intent_kit.utils.report_utils import PerformanceReport

# Create performance report
perf_report = PerformanceReport()

# Add performance data
perf_report.add_execution_data({
    "node_id": "classifier",
    "execution_time": 0.5,
    "tokens_used": 100,
    "cost": 0.002
})

perf_report.add_execution_data({
    "node_id": "extractor",
    "execution_time": 1.2,
    "tokens_used": 200,
    "cost": 0.004
})

# Generate performance summary
summary = perf_report.generate_summary()
print(summary)
# {
#     "total_executions": 2,
#     "total_time": 1.7,
#     "total_cost": 0.006,
#     "average_time": 0.85,
#     "node_breakdown": {...}
# }
```

### HTML Report Generation

```python
from intent_kit.utils.report_utils import HTMLReportGenerator

# Create HTML report
html_reporter = HTMLReportGenerator()

# Add sections
html_reporter.add_section("Overview", {
    "title": "Execution Summary",
    "content": "This report summarizes the DAG execution performance."
})

html_reporter.add_metrics("Performance Metrics", {
    "Response Time": "1.2s",
    "Cost": "$0.25",
    "Accuracy": "95%"
})

# Generate HTML report
html_content = html_reporter.generate_html()
with open("report.html", "w") as f:
    f.write(html_content)
```

### JSON Report Export

```python
from intent_kit.utils.report_utils import JSONReportExporter

# Create JSON exporter
exporter = JSONReportExporter()

# Add report data
exporter.add_data("execution_results", {
    "total_requests": 100,
    "success_rate": 0.95,
    "average_latency": 1.2
})

# Export to JSON
json_data = exporter.export()
with open("report.json", "w") as f:
    json.dump(json_data, f, indent=2)
```

## Typed Output

The `typed_output` module provides type-safe output handling.

### Basic Typed Output

```python
from intent_kit.utils.typed_output import TypedOutput, OutputType

# Create typed output
output = TypedOutput(
    content="Hello, world!",
    output_type=OutputType.TEXT,
    metadata={"confidence": 0.95}
)

# Access typed content
print(output.content)  # "Hello, world!"
print(output.output_type)  # OutputType.TEXT
print(output.metadata)  # {"confidence": 0.95}
```

### Structured Output

```python
from intent_kit.utils.typed_output import TypedOutput, OutputType

# Create structured output
structured_output = TypedOutput(
    content={
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    },
    output_type=OutputType.JSON,
    metadata={
        "schema_version": "1.0",
        "validation_passed": True
    }
)

# Validate structured content
if structured_output.output_type == OutputType.JSON:
    data = structured_output.content
    print(f"Name: {data['name']}")
    print(f"Age: {data['age']}")
```

### Output Validation

```python
from intent_kit.utils.typed_output import TypedOutput, OutputType, validate_output

# Create output with validation
output = TypedOutput(
    content={"temperature": 25, "humidity": 60},
    output_type=OutputType.JSON
)

# Validate output
is_valid = validate_output(output, {
    "temperature": (int, lambda x: 0 <= x <= 50),
    "humidity": (int, lambda x: 0 <= x <= 100)
})

print(f"Output is valid: {is_valid}")
```

### Output Transformation

```python
from intent_kit.utils.typed_output import TypedOutput, OutputType

# Create output
output = TypedOutput(
    content="The temperature is 25°C",
    output_type=OutputType.TEXT
)

# Transform output
def extract_temperature(text):
    import re
    match = re.search(r'(\d+)°C', text)
    return int(match.group(1)) if match else None

transformed = output.transform(
    extract_temperature,
    OutputType.NUMBER,
    metadata={"extraction_method": "regex"}
)

print(transformed.content)  # 25
print(transformed.output_type)  # OutputType.NUMBER
```

## Best Practices

### 1. Type Safety

```python
# Always use type validation for external data
from intent_kit.utils.type_coercion import validate_raw_content

def process_user_input(data):
    schema = {
        "name": str,
        "age": int,
        "email": str
    }

    try:
        validated_data = validate_raw_content(data, dict)
        return validated_data
    except TypeValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise
```

### 2. Performance Monitoring

```python
# Use performance utilities consistently
from intent_kit.utils.perf_util import PerfUtil

perf = PerfUtil()

def expensive_operation():
    with perf.timer("expensive_operation"):
        # Your code here
        result = complex_calculation()

        # Record costs if applicable
        perf.record_tokens("openrouter", "google/gemma-2-9b-it", 100, 50)

        return result
```

### 3. Structured Logging

```python
# Use structured logging for better observability
from intent_kit.utils.logger import Logger

logger = Logger("dag_execution")

def execute_dag(dag_id, user_input):
    logger.info("DAG execution started", extra={
        "dag_id": dag_id,
        "input_length": len(user_input),
        "timestamp": datetime.now().isoformat()
    })

    try:
        result = dag.execute(user_input)
        logger.info("DAG execution completed", extra={
            "dag_id": dag_id,
            "success": True,
            "execution_time": result.execution_time
        })
        return result
    except Exception as e:
        logger.error("DAG execution failed", extra={
            "dag_id": dag_id,
            "error": str(e),
            "success": False
        }, exc_info=True)
        raise
```

### 4. Error Handling

```python
# Use utilities for robust error handling
from intent_kit.utils.type_coercion import TypeValidationError
from intent_kit.utils.logger import Logger

logger = Logger("data_processing")

def safe_data_processing(data):
    try:
        # Process data with type validation
        validated_data = validate_raw_content(data, dict)
        return process_validated_data(validated_data)
    except TypeValidationError as e:
        logger.warning("Data validation failed", extra={
            "error": str(e),
            "data_type": type(data).__name__
        })
        return None
    except Exception as e:
        logger.error("Unexpected error in data processing", exc_info=True)
        raise
```
