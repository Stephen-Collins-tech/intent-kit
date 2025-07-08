# intent-kit

<!-- Badges -->

[![CI](https://github.com/Stephen-Collins-tech/intent-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/Stephen-Collins-tech/intent-kit/actions/workflows/ci.yml)
[![Coverage Status](https://codecov.io/gh/Stephen-Collins-tech/intent-kit/branch/main/graph/badge.svg)](https://codecov.io/gh/Stephen-Collins-tech/intent-kit)
[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://docs.intentkit.io)
[![PyPI](https://img.shields.io/pypi/v/intentkit-py)](https://pypi.org/project/intentkit-py)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Stephen-Collins-tech/intent-kit/HEAD?filepath=examples%2Fsimple_demo.ipynb)

A Python library for building intent-driven workflows with LLMs.

## Features

* **Tree-based Intent Architecture**: Build hierarchical intent trees with classifier and intent nodes.
* **IntentGraph Multi-Intent Routing**: Route to multiple intent trees and handle complex multi-intent inputs.
* **Context-Aware Execution**: Full context support with dependency tracking and state management.
* **Multiple Classifier Backends**: Support for keyword-based classification and AI service integration.
* **Parameter Extraction & Validation**: Automatic parameter extraction with type validation and custom validators.
* **AI Service Integration**: Optional integration with OpenAI, Anthropic, Google AI, and Ollama services.
* **Flexible Node System**: Mix classifier nodes and intent nodes to create complex decision trees.
* **Error Handling**: Comprehensive error handling with detailed logging and execution tracing.
* **Type Safety**: Full type hints and validation throughout the system.
* **Interactive Visualization**: Generate interactive HTML graphs of execution paths (optional).
* **Debug Output**: JSON and console output formats for debugging.

---

## Core Thesis

**intent-kit is a universal intent framework with zero core dependencies that works with any classification method.**

**intent-kit is built on the principle that the developer is responsible for defining the complete set of capabilities, constraints, and dependencies within their workflow domain.**

All possible workflows—whether independent or dependent, serial or parallel—**must be explicitly described and known ahead of time**. This means:

* **Every intent and parameter is known up front.**
* **All context dependencies (inputs/outputs) are declared for each intent.**
* **No "emergent" or open-ended LLM-driven behaviors outside the defined workflow graph.**

> **Note:** If you're looking for "sentient" agents that magically invent new capabilities and workflow logic out of thin air, you're in the wrong place. intent-kit doesn't believe in spontaneous digital enlightenment—just reliable, deterministic software.

This explicitness is *required* for:

* Correctness and safety (no surprises at runtime)
* Parallel/concurrent execution (fine-grained dependency tracking)
* Auditability and testability (every workflow is analyzable and visualizable)
* Business reliability (no "unknown unknowns")

**Universal Framework Benefits:**
* **Zero Core Dependencies**: Works anywhere with just Python standard library
* **Any Classification Method**: Rule-based, ML models, external APIs, or LLMs
* **Optional AI Enhancement**: Add AI capabilities when needed
* **Works Everywhere**: From embedded systems to enterprise applications

If you want deterministic, composable, and debuggable intent classification—where you, the developer, define and constrain the domain—**intent-kit is for you**.

---

## Universal Framework Approach

intent-kit is designed as a **universal intent framework** that works with any classification method:

### **Start Simple (Zero Dependencies)**
```python
from intent_kit import handler, keyword_classifier, ClassifierNode

# Pure rule-based classification - no external dependencies
intent_handlers = [
    handler(
        name="greet",
        description="Greet user",
        handler_func=lambda name: f"Hello {name}!",
        param_schema={"name": str}
        # No llm_config = uses rule-based extraction
    )
]

classifier = ClassifierNode(
    name="root",
    classifier=keyword_classifier,  # Built-in rule-based classifier
    children=intent_handlers
)
```

### **Scale Up (Add Your Own Classification)**
```python
# Custom classification method
def my_classifier(user_input: str, children: List[TreeNode]) -> Optional[TreeNode]:
    # Your custom logic: database lookup, ML model, API call, etc.
    intent = my_custom_classification_logic(user_input)
    return find_handler_by_name(intent, children)

classifier = ClassifierNode(
    name="root",
    classifier=my_classifier,
    children=intent_handlers
)
```

### **Go AI (Optional Enhancement)**
```python
# Add AI capabilities when needed
from intent_kit import llm_classifier

classifier = llm_classifier(
    name="root",
    children=intent_handlers,
    llm_config=LLM_CONFIG  # Optional AI enhancement
)
```

### **Mix & Match (Hybrid Approaches)**
```python
# Combine multiple classification methods
def hybrid_classifier(user_input: str, children: List[TreeNode]) -> Optional[TreeNode]:
    # Try rule-based first
    result = keyword_classifier(user_input, children)
    if result:
        return result
    
    # Fall back to ML model
    result = ml_classifier(user_input, children)
    if result:
        return result
    
    # Finally try LLM (if available)
    return llm_classifier(user_input, children)
```

**This universal approach means intent-kit works for:**
- **Embedded systems** (rule-based only)
- **Enterprise applications** (database-driven classification)
- **Web applications** (API-based classification)
- **AI applications** (LLM-powered classification)
- **Hybrid systems** (multiple classification methods)

---

## Installation

```bash
# Basic installation (zero core dependencies - truly universal!)
uv pip install intent-kit

# With specific AI provider support
uv pip install 'intent-kit[openai]'      # OpenAI (GPT models)
uv pip install 'intent-kit[anthropic]'   # Anthropic (Claude models)
uv pip install 'intent-kit[google]'      # Google (Gemini models)
uv pip install 'intent-kit[ollama]'      # Ollama (local models)

# With visualization support
uv pip install 'intent-kit[viz]'

# With multiple providers
uv pip install 'intent-kit[openai,anthropic]'
uv pip install 'intent-kit[openai,google,viz]'

# With all optional features
uv pip install 'intent-kit[openai,anthropic,google,ollama,viz]'
```

Or, with plain pip:

```bash
# Core framework (zero dependencies)
pip install intent-kit

# With specific AI provider support
pip install 'intent-kit[openai]'      # OpenAI (GPT models)
pip install 'intent-kit[anthropic]'   # Anthropic (Claude models)
pip install 'intent-kit[google]'      # Google (Gemini models)
pip install 'intent-kit[ollama]'      # Ollama (local models)

# With visualization support
pip install 'intent-kit[viz]'

# With multiple providers
pip install 'intent-kit[openai,anthropic]'
pip install 'intent-kit[openai,google,viz]'
```

---

## Quick Start

The API provides a simplified, declarative way to build intent graphs with automatic argument extraction and LLM integration:

```python
from intent_kit import IntentGraphBuilder, handler, llm_classifier
from intent_kit.context import IntentContext

# Create intent handlers with automatic argument extraction
greet_handler = handler(
    name="greet",
    description="Greet the user",
    handler_func=lambda name, **kwargs: f"Hello {name}!",
    param_schema={"name": str}
    # No llm_config = uses rule-based extraction
)

weather_handler = handler(
    name="weather",
    description="Get weather information for a location",
    handler_func=lambda location, **kwargs: f"The weather in {location} is sunny.",
    param_schema={"location": str}
)

# Create classifier with auto-wired children descriptions
classifier = llm_classifier(
    name="root",
    children=[greet_handler, weather_handler],
    llm_config=LLM_CONFIG,  # Optional: enables LLM-powered classification
    description="Main intent classifier"
)

# Build the graph using the builder pattern
graph = (
    IntentGraphBuilder()
    .root(classifier)
    .build()
)

# Use the graph
context = IntentContext(session_id="user_123")
result = graph.route("Hello Alice", context=context)
print(result.output)  # "Hello Alice!"
```

### Advanced Example with IntentGraph

```python
from intent_kit import IntentGraphBuilder, handler, llm_classifier, rule_splitter_node
from intent_kit.context import IntentContext

# Create handlers with automatic argument extraction
greet_handler = handler(
    name="greet",
    description="Greet the user",
    handler_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
)

weather_handler = handler(
    name="weather",
    description="Get weather information for a location",
    handler_func=lambda location: f"The weather in {location} is sunny.",
    param_schema={"location": str}
)

# Create classifier with auto-wired children descriptions
classifier = llm_classifier(
    name="main_classifier",
    children=[greet_handler, weather_handler],
    llm_config=LLM_CONFIG,
    description="Main intent classifier"
)

# Create splitter for multi-intent handling
splitter = rule_splitter_node(
    name="main_splitter",
    children=[classifier],
    description="Split multi-intent inputs using rule-based logic"
)

# Build the graph using the builder pattern
graph = (
    IntentGraphBuilder()
    .root(splitter)
    .build()
)

# Handle multi-intent input
context = IntentContext(session_id="user_123")
result = graph.route("Hello Alice and what's the weather for Paris?", context=context)

if result.success:
    print(f"Results: {result.output}")
else:
    print(f"Errors: {result.error}")
```

### LLM-Powered Classification Example

```python
from intent_kit import handler, llm_classifier, IntentGraphBuilder
from intent_kit.services.llm_factory import LLMFactory

# Configure LLM
llm_config = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-api-key"
}

# Create handlers with automatic LLM-powered argument extraction
weather_handler = handler(
    name="weather",
    description="Get weather information for a location",
    handler_func=lambda city, **kwargs: f"The weather in {city} is sunny.",
    param_schema={"city": str},
    llm_config=llm_config  # Enables LLM-based argument extraction
)

greet_handler = handler(
    name="greet",
    description="Send a greeting to someone",
    handler_func=lambda name, **kwargs: f"Hello {name}!",
    param_schema={"name": str},
    llm_config=llm_config
)

# Create LLM-powered classifier with auto-wired children descriptions
root_node = llm_classifier(
    name="Root",
    children=[weather_handler, greet_handler],
    llm_config=llm_config,
    description="LLM-powered intent classifier"
)

# Build the graph
graph = (
    IntentGraphBuilder()
    .root(root_node)
    .build()
)
```

---

## Core Concepts

### Nodes

* **ClassifierNode**: Routes input to child nodes using a classifier function.
* **HandlerNode**: Leaf nodes that execute specific actions with parameter extraction and validation.

### Trees (Emergent)

Trees emerge naturally from the parent-child relationships between nodes. Any node can be a "root" of a tree simply by being the entry point. The tree structure is defined by the `children` parameter when creating nodes.

### Context System

The `IntentContext` provides state management and dependency tracking:

```python
from intent_kit.context import IntentContext

context = IntentContext(session_id="user_123")

# Set values with audit trail
context.set("user_name", "Alice", modified_by="greet")
context.set("greeting_count", 1, modified_by="greet")

# Get values with defaults
name = context.get("user_name", "Unknown")
count = context.get("greeting_count", 0)

# Track dependencies in intent nodes
weather_node = handler(
    name="Weather",
    param_schema={"city": str},
    handler=handle_weather,
    arg_extractor=extract_weather_args,
    context_inputs={"user_preferences"},  # Read from context
    context_outputs={"last_weather_query"},  # Write to context
    description="Get weather with user preferences"
)
```

### Builder API

The API provides a simplified, declarative way to build intent graphs:

#### handler()

Creates a handler node with automatic argument extraction:

```python
from intent_kit import handler

greet_handler = handler(
        name="greet",
        description="Greet the user",
        handler_func=lambda name, **kwargs: f"Hello {name}!",
        param_schema={"name": str},
        llm_config=LLM_CONFIG  # Optional: enables LLM-based argument extraction
    )
```

#### llm_classifier()

Creates an LLM-powered classifier node with auto-wired children descriptions:

```python
from intent_kit import llm_classifier

classifier = llm_classifier(
    name="root",
    children=[greet_handler, calc_handler, weather_handler],
    llm_config=LLM_CONFIG,
    description="Main intent classifier"
)
```

#### IntentGraphBuilder

A fluent builder for creating IntentGraph instances:

```python
from intent_kit import IntentGraphBuilder

graph = (
    IntentGraphBuilder()
    .root(classifier)
    .build()
)
```

#### Splitter Nodes

For multi-intent handling:

```python
from intent_kit import llm_splitter_node, rule_splitter_node

# LLM-powered splitter
llm_splitter = llm_splitter_node(
    name="smart_splitter",
    children=[classifier],
    llm_config=LLM_CONFIG
)

# Rule-based splitter
rule_splitter = rule_splitter_node(
    name="rule_splitter",
    children=[classifier]
)
```

### Legacy TreeBuilder API

Utility class for creating nodes (legacy approach):

```python
from intent_kit.classifiers import ClassifierNode
from intent_kit.handlers import HandlerNode

# Create handler node
handler_node = HandlerNode(
    name="HandlerName",
    param_schema={"param1": str, "param2": int},
    handler=your_handler_function,
    arg_extractor=your_extractor_function,
    input_validator=your_validator_function,  # Optional
    output_validator=your_output_validator,   # Optional
    context_inputs={"field1", "field2"},      # Optional
    context_outputs={"field3", "field4"},     # Optional
    description="Handler description"
)

# Create classifier node
classifier_node = ClassifierNode(
    name="ClassifierName",
    classifier=your_classifier_function,
    children=[child_node1, child_node2],
    description="Classifier description"
)
```

### Argument Extraction

The API provides automatic argument extraction with two modes:

#### LLM-based Extraction

When `llm_config` is provided to `handler()`, it uses LLM-powered argument extraction:

```python
handler(
    name="greet",
    description="Greet the user",
    handler_func=lambda name: f"Hello {name}!",
    param_schema={"name": str},
    llm_config=LLM_CONFIG  # Enables LLM-based extraction
)
```

#### Rule-based Extraction

When no `llm_config` is provided, it uses simple rule-based extraction:

```python
handler(
    name="greet",
    description="Greet the user",
    handler_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
    # No llm_config = uses rule-based extraction
)
```

The rule-based extractor uses simple heuristics:
- For string parameters: extracts the last word or entire text
- For numeric parameters: finds numbers in the text or uses defaults
- For boolean parameters: defaults to True

### Multi-Intent Handling

For multi-intent scenarios, use splitter nodes:

```python
# Create a classifier for the splitter's children
classifier = llm_classifier(
    name="splitter_classifier",
    children=[greet_handler, calc_handler, weather_handler],
    llm_config=LLM_CONFIG
)

# Create LLM-powered splitter
splitter = llm_splitter_node(
    name="multi_intent_splitter",
    children=[classifier],
    llm_config=LLM_CONFIG
)

# Build the graph
graph = (
    IntentGraphBuilder()
    .root(splitter)
    .build()
)

# Test multi-intent input
result = graph.route("Hello Alice and what's the weather in San Francisco")
```

### Classifiers

Built-in classifiers:

```python
from intent_kit.classifiers import keyword_classifier

# Simple keyword-based classification
# Returns first child whose name appears in the input
```

### AI Service Integration

```python
from intent_kit.services.llm_factory import LLMFactory

# Create AI service client
llm_client = LLMFactory.create_client({
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "api_key": "your-key"
})

# Available providers: openai, anthropic, google, ollama
```

### Benefits of the API

1. **Simplified Syntax**: Less boilerplate code required
2. **Automatic Argument Extraction**: No need to manually create argument extractors
3. **Auto-wired Classifiers**: Children descriptions are automatically included in classifier prompts
4. **Fluent Builder Pattern**: More readable graph construction
5. **Fallback Support**: Rule-based extraction when LLM config is not available
6. **Backwards Compatibility**: Original API still works for advanced use cases



### IntentGraph - Multi-Intent Routing

IntentGraph enables routing to multiple intent trees and handling multi-intent user inputs. Trees are registered as root nodes, and the tree structure emerges from their parent-child relationships:

```python
from intent_kit.graph import IntentGraph
from intent_kit.splitters import rule_splitter, llm_splitter

# Create IntentGraph with rule-based splitting
graph = IntentGraph(splitter=rule_splitter, visualize=True)
graph.add_root_node(root_node)

# Handle multi-intent input
result = graph.route("Cancel my flight and update my email", context=context)

# Use LLM-based splitting for complex inputs
graph_llm = IntentGraph(
    splitter=llm_splitter, 
    visualize=True, 
    llm_config=llm_config
)
```

**Key Features:**

* **Intent Splitting**: Decompose multi-intent inputs into sub-intents.
* **Flexible Routing**: Dispatch to one or more intent trees.
* **Multiple Splitters**: Rule-based and LLM-based splitting strategies.
* **Consistent API**: Unified `ExecutionResult` return format
* **Interactive Visualization**: Generate interactive HTML graphs of execution paths (optional)

### Interactive Graph Visualization

IntentGraph can generate interactive HTML visualizations of execution paths. This feature requires optional dependencies:

```bash
# Install with visualization support
uv pip install 'intent-kit[viz]'
```

**Usage:**

```python
from intent_kit.graph import IntentGraph

# Create IntentGraph with visualization enabled
graph = IntentGraph(splitter=rule_splitter, visualize=True)
graph.add_root_node(root_node)

# Execute and get visualization
result = graph.route("Book a flight to Paris", context=context)
if result.output and isinstance(result.output, dict) and "visualization_html" in result.output:
    print(f"Interactive graph saved to: {result.output['visualization_html']}")
    # Open the HTML file in your browser to see the interactive graph
```

The visualization shows:
- **Node types**: Classifier nodes (blue), Intent nodes (green), Error nodes (red)
- **Execution flow**: Directed edges showing the path through the tree
- **Node details**: Input, output, errors, and parameters for each node
- **Interactive features**: Zoom, pan, hover for details, and node dragging

Graphs are saved to `intentkit_graphs/` directory with unique filenames based on the input hash.

---

## Examples

The `examples/` directory contains comprehensive demonstrations of IntentKit functionality. Each example is designed to be minimal and focused on specific features.

### Available Examples

#### Simple Demo (`simple_demo.py`)
A basic demonstration of IntentKit with LLM-powered intent classification and argument extraction. Shows the core IntentGraph functionality with a **pass-through splitter** (default behavior).

#### Multi-Intent Demo (`multi_intent_demo.py`)
A demonstration of multi-intent handling using the rule-based splitter. Shows how to handle complex inputs like "Hello Alice and what's the weather in San Francisco".

#### Error Demo (`error_demo.py`)
A demonstration of error handling and debugging features. Shows how to handle various error scenarios and debug intent routing issues.

#### Context Demo (`context_demo.py`)
A demonstration of context and dependency management. Shows how handlers can read from and write to shared context.

#### Context Debugging Demo (`context_debug_demo.py`)
A comprehensive demonstration of context debugging features including:
- `debug_context` and `context_trace` parameters
- Dependency mapping and analysis with `get_context_dependencies()`
- Context flow validation with `validate_context_flow()`
- Debug output formats (console, JSON) with `trace_context_execution()`

#### Ollama Demo (`ollama_demo.py`)
A demonstration of using IntentKit with local Ollama models. Shows how to configure and use local LLM models.

### Default Behavior

By default, IntentKit uses a **pass-through splitter** that doesn't split user input. This is the safest approach for most use cases, as it avoids accidentally splitting inputs like "What's 15 plus 7?" on mathematical operators.

If you need multi-intent handling, explicitly configure the rule-based splitter:

```python
from intent_kit.splitters import rule_splitter

return IntentGraphBuilder().root(classifier).splitter(rule_splitter).build()
```

### Running Examples

```bash
# Simple Demo (requires OpenAI API key)
python examples/simple_demo.py

# Ollama Demo (requires Ollama installed)
python examples/ollama_demo.py

# Context Demo
python examples/context_demo.py

# Error Demo
python examples/error_demo.py

# Multi-Intent Demo
python examples/multi_intent_demo.py

# Context Debug Demo
python examples/context_debug_demo.py
```

### Setup Requirements

#### API Keys for LLM Services (Optional)

For LLM-powered features, you can set up API keys:

**Option 1: Environment Variables**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

**Option 2: .env File**
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

**Note:** Many demos work without any API keys using fallback classification!

### Key Features Demonstrated

- **Intent Classification**: LLM-powered intent routing
- **Argument Extraction**: Automatic parameter extraction from user input
- **Context Management**: Shared state across handlers
- **Error Handling**: Robust error handling and debugging
- **Multi-Intent**: Handling complex, multi-part requests
- **Local Models**: Using Ollama for local LLM processing

### Example Inputs

**Simple Demo Inputs:**
- "Hello, my name is Alice"
- "What's 15 plus 7?"
- "Weather in San Francisco"
- "Help me"
- "Multiply 8 and 3"

**Multi-Intent Demo Inputs:**
- "Hello Alice and what's the weather in San Francisco"
- "Calculate 5 plus 3 and also greet Bob"
- "Help me and get weather for New York"

### Minimal Example

Here's the absolute minimum code needed to get started:

```python
from intent_kit import IntentGraphBuilder, handler, llm_classifier

def create_intent_graph():
    handlers = [
        handler(
            name="greet",
            description="Greet the user",
            handler_func=lambda name, **kwargs: f"Hello {name}!",
            param_schema={"name": str}
        ),
        handler(
            name="calculate",
            description="Perform a calculation",
            handler_func=lambda operation, a, b, **kwargs: f"{a} {operation} {b} = {eval(f'{a} {operation} {b}')}",
            param_schema={"operation": str, "a": float, "b": float}
        )
    ]
    
    classifier = llm_classifier(
        name="root",
        children=handlers,
        llm_config={},  # Empty config uses fallback classification
        description="Main intent classifier"
    )
    
    return IntentGraphBuilder().root(classifier).build()

# Use the graph
graph = create_intent_graph()
result = graph.route("Hello, my name is Alice")
print(result.output)  # "Hello Alice!"
```

---

## Development

```bash
# Clone the repository
git clone git@github.com:Stephen-Collins-tech/intent-kit.git
cd intent-kit

# Install in development mode (recommended: uv)
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
uv pip install pytest   # if not already present
pytest tests/
```

Or with pip:

```bash
pip install -e .
pip install -e ".[dev]"
pytest tests/
```

---

## Evaluation & Benchmarking

intent-kit provides a built-in evaluation framework for benchmarking intent graphs and nodes against real datasets. This is separate from unit/integration tests and is designed for large-scale, reproducible evaluation.

The evaluation framework is now part of the main `intent_kit` package and can be imported as:

```python
from intent_kit.evals import run_all_evaluations, evaluate_node, generate_markdown_report
```

**Organized Structure:**
- **Latest results**: Always available in `intent_kit/evals/results/latest/` and `intent_kit/evals/reports/latest/`
- **Date-based archives**: Historical runs are automatically archived in date-based directories
- **Clean separation**: Reports and raw results are organized separately for easy access

### Running All Evals

To run all evaluations and generate comprehensive markdown reports:

```bash
# Run with real API calls (requires API keys)
uv run run-evals

# Run in mock mode (no API keys required)
uv run run-evals --mock
```

- Generates a comprehensive report at `reports/comprehensive_report.md`
- Generates individual reports for each dataset in `reports/`
- Mock mode uses simulated responses for testing without API costs

### Running a Specific Eval

To run a specific node evaluation (with markdown output):

```bash
uv run eval-node --dataset handler_node_llm --output reports/my_eval_report.md
```

- Replace `handler_node_llm` with any dataset name (without .yaml extension)
- Add `--output <file.md>` to save the report to a specific file
- Reports are automatically saved to `reports/` directory

### Adding New Evals
- Add new YAML datasets to `intent_kit/evals/datasets/`
- Add corresponding node implementations to `intent_kit/evals/sample_nodes/`
- The framework will automatically discover and evaluate them

### Where are the results?
- **Latest reports**: `intent_kit/evals/reports/latest/`
- **Latest results**: `intent_kit/evals/results/latest/`
- **Date-based archives**: `intent_kit/evals/reports/YYYY-MM-DD/` and `intent_kit/evals/results/YYYY-MM-DD/`
- Reports are in markdown format for easy sharing and review
- Raw results are in CSV format for detailed analysis

### When to use evals vs. tests?
- **Unit/Integration tests** (in `tests/`): For correctness, fast feedback, and CI
- **Evals** (in `intent_kit/evals/`): For benchmarking, regression, and real-world performance

---

## Project Structure

```
intent-kit/
├── intent_kit/
│   ├── __init__.py          # Main exports
│   ├── node.py              # Node classes (TreeNode)
│   ├── builder.py           # Builder API utility
│   │   └── intent_graph.py  # Main IntentGraph class
│   ├── graph/               # IntentGraph multi-intent routing
│   │   └── intent_graph.py  # Main IntentGraph class
│   ├── splitters/           # Intent splitting strategies
│   │   ├── node.py          # SplitterNode class
│   │   ├── functions.py     # Splitter functions
│   │   ├── rule_splitter.py # Rule-based splitting
│   │   ├── llm_splitter.py  # LLM-powered splitting
│   │   └── types.py         # Splitter types
│   ├── classifiers/         # Classification backends
│   │   ├── node.py          # ClassifierNode class
│   │   ├── keyword.py       # Keyword-based classifier
│   │   ├── llm_classifier.py # LLM-powered classifier
│   │   ├── chunk_classifier.py # Chunk classification
│   │   └── __init__.py
│   ├── handlers/            # Action execution
│   │   ├── node.py          # HandlerNode class
│   │   └── __init__.py
│   ├── context/             # Context and state management
│   │   ├── dependencies.py  # Context dependency tracking
│   │   └── __init__.py
│   ├── services/            # AI service integrations
│   │   ├── llm_factory.py   # LLM client factory
│   │   ├── openai_client.py
│   │   ├── anthropic_client.py
│   │   ├── google_client.py
│   │   ├── ollama_client.py
│   │   └── __init__.py
│   ├── evals/               # Evaluation framework
│   │   ├── __init__.py      # Evaluation exports
│   │   ├── run_all_evals.py # Run all evaluations
│   │   ├── run_node_eval.py # Individual node evaluation
│   │   ├── datasets/        # Evaluation datasets
│   │   ├── sample_nodes/    # Sample nodes for evaluation
│   │   └── reports/         # Generated evaluation reports
│   ├── types.py             # Type definitions
│   ├── exceptions/          # Custom exceptions
│   └── utils/               # Utilities
│       └── logger.py
├── examples/                # Usage examples
│   ├── simple_demo.py       # Basic IntentGraph demo
│   ├── context_demo.py      # Context-aware workflow demo
│   ├── ollama_demo.py       # Local LLM demo
│   ├── error_demo.py        # Error handling demo
│   └── README.md
├── tests/                   # Test suite
└── pyproject.toml           # Project configuration
```

---

## License

MIT License

## Evaluation API

The evaluation API provides a clean Python interface for testing your nodes against YAML datasets.

### Basic Usage

```python
from intent_kit.evals import load_dataset, run_eval
from intent_kit.evals.sample_nodes.classifier_node_llm import classifier_node_llm

# Load a dataset
dataset = load_dataset("intent_kit/evals/datasets/classifier_node_llm.yaml")

# Run evaluation
result = run_eval(dataset, classifier_node_llm)

# Check results
print(f"Accuracy: {result.accuracy():.1%}")
print(f"Passed: {result.passed_count()}/{result.total_count()}")

# Save results (using default locations)
csv_path = result.save_csv()
json_path = result.save_json()
md_path = result.save_markdown()

# Or specify custom paths
result.save_csv("my_results.csv")
result.save_json("my_results.json")
result.save_markdown("my_report.md")
```

### Convenience Functions

```python
from intent_kit.evals import run_eval_from_path, run_eval_from_module

# Evaluate from file path
result = run_eval_from_path(
    "intent_kit/evals/datasets/classifier_node_llm.yaml",
    classifier_node_llm
)

# Evaluate with module loading
result = run_eval_from_module(
    "intent_kit/evals/datasets/classifier_node_llm.yaml",
    "intent_kit.evals.sample_nodes.classifier_node_llm",
    "classifier_node_llm"
)
```

### Custom Comparison

```python
# Case-insensitive comparison
def case_insensitive_comparator(expected, actual):
    return str(expected).lower().strip() == str(actual).lower().strip()

result = run_eval(dataset, node, comparator=case_insensitive_comparator)
```

### Programmatic Datasets

```python
from intent_kit.evals import EvalTestCase, Dataset

# Create test cases programmatically
test_cases = [
    EvalTestCase(
        input="What's the weather like?",
        expected="Weather response",
        context={"user_id": "test"}
    )
]

dataset = Dataset(
    name="my_dataset",
    description="Custom test dataset",
    node_type="classifier",
    node_name="my_node",
    test_cases=test_cases
)

result = run_eval(dataset, my_node)
```

### Dataset Format

YAML datasets should follow this format:

```yaml
dataset:
  name: "my_dataset"
  description: "Test dataset for my node"
  node_type: "classifier"
  node_name: "my_node"

test_cases:
  - input: "What's the weather like in New York?"
    expected: "Weather in New York: Sunny with a chance of rain"
    context:
      user_id: "user123"
  
  - input: "Cancel my flight"
    expected: "Successfully cancelled flight"
    context:
      user_id: "user123"
```

### Error Handling

The API handles errors gracefully:

- **Node exceptions**: Caught and recorded in results
- **Missing files**: Clear error messages
- **Malformed datasets**: Validation with helpful error messages
- **Fail-fast option**: Stop evaluation on first failure

```python
# Fail-fast evaluation
result = run_eval(dataset, node, fail_fast=True)
```

### Output Locations

By default, results are saved to the existing intent-kit directory structure:

- **CSV/JSON results**: `intent_kit/evals/results/latest/`
- **Markdown reports**: `intent_kit/evals/reports/latest/`

Files are automatically timestamped to avoid conflicts. You can also specify custom paths if needed.