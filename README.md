# intent-kit

A Python library for building hierarchical intent classification and execution systems with support for multiple AI service backends.

## Features

* **Tree-based Intent Architecture**: Build hierarchical intent taxonomies with classifier and intent nodes.
* **IntentGraph Multi-Intent Routing**: Route to multiple taxonomies and handle complex multi-intent inputs.
* **Multiple Classifier Backends**: Support for keyword-based classification and AI service integration.
* **Parameter Extraction & Validation**: Automatic parameter extraction with type validation and custom validators.
* **AI Service Integration**: Optional integration with OpenAI, Anthropic, and Google AI services.
* **Flexible Node System**: Mix classifier nodes and intent nodes to create complex decision trees.
* **Error Handling**: Comprehensive error handling with detailed logging.
* **Type Safety**: Full type hints and validation throughout the system.

---

## Core Thesis

**intent-kit is built on the principle that the developer is responsible for defining the complete set of capabilities, constraints, and dependencies within their workflow domain.**

All possible workflows—whether independent or dependent, serial or parallel—**must be explicitly described and known ahead of time**. This means:

* **Every intent and parameter is known up front.**
* **All context dependencies (inputs/outputs) are declared for each intent.**
* **No “emergent” or open-ended LLM-driven behaviors outside the defined workflow graph.**

> **Note:** If you’re looking for “sentient” agents that magically invent new capabilities and workflow logic out of thin air, you’re in the wrong place. intent-kit doesn’t believe in spontaneous digital enlightenment—just reliable, deterministic software.


This explicitness is *required* for:

* Correctness and safety (no surprises at runtime)
* Parallel/concurrent execution (fine-grained dependency tracking)
* Auditability and testability (every workflow is analyzable and visualizable)
* Business reliability (no “unknown unknowns”)

If you want deterministic, composable, and debuggable AI-assisted automation—where you, the developer, define and constrain the domain—**intent-kit is for you**.

---

## Installation

```bash
# Basic installation (recommended: uv)
uv pip install intent-kit

# With AI service support
uv pip install 'intent-kit[openai]'
```

Or, with plain pip:

```bash
pip install intent-kit
pip install 'intent-kit[openai]'
```

---

## Quick Start

### Basic Example

```python
from intent_kit.tree import TreeBuilder
from intent_kit.classifiers import keyword_classifier
from intent_kit.engine import execute_taxonomy
import re

# Define argument extractors
def extract_weather_args(user_input: str) -> dict:
    """Extract city from user input."""
    match = re.search(r'weather (?:for|in) (\w+)', user_input, re.IGNORECASE)
    return {"city": match.group(1) if match else "Unknown"}

def extract_greeting_args(user_input: str) -> dict:
    """Extract person name from user input."""
    match = re.search(r'hello (\w+)', user_input, re.IGNORECASE)
    return {"person": match.group(1) if match else "there"}

# Define handlers
def handle_weather(city: str) -> str:
    return f"The weather in {city} is sunny."

def handle_greeting(person: str) -> str:
    return f"Hello, {person}!"

# Build the taxonomy tree
weather_node = TreeBuilder.intent_node(
    name="Weather",
    param_schema={"city": str},
    handler=handle_weather,
    arg_extractor=extract_weather_args,
    description="Get weather information for a city"
)

greeting_node = TreeBuilder.intent_node(
    name="Greeting", 
    param_schema={"person": str},
    handler=handle_greeting,
    arg_extractor=extract_greeting_args,
    description="Send a greeting to someone"
)

root_taxonomy = TreeBuilder.classifier_node(
    name="Root",
    classifier=keyword_classifier,
    children=[weather_node, greeting_node],
    description="Main intent classifier"
)

# Execute intents
result = execute_taxonomy(
    user_input="What's the weather for Paris?",
    node=root_taxonomy
)
print(result["output"])  # "The weather in Paris is sunny."
```

### Advanced Example with Hierarchical Structure

```python
# Banking domain
def extract_account_args(user_input: str) -> dict:
    match = re.search(r'account(\w+)', user_input)
    return {"account_id": match.group(1) if match else "default"}

def handle_get_balance(account_id: str) -> str:
    return f"Balance for {account_id}: $1,000"

banking_node = TreeBuilder.classifier_node(
    name="Banking",
    classifier=keyword_classifier,
    children=[
        TreeBuilder.intent_node(
            name="GetBalance",
            param_schema={"account_id": str},
            handler=handle_get_balance,
            arg_extractor=extract_account_args,
            description="Get account balance"
        )
    ],
    description="Banking operations"
)

# HR domain  
def extract_employee_args(user_input: str) -> dict:
    words = user_input.split()
    return {"name": words[-2] if len(words) >= 2 else "Unknown", 
            "role": words[-1] if len(words) >= 1 else "Employee"}

def handle_add_employee(name: str, role: str) -> str:
    return f"Added employee {name} as {role}"

hr_node = TreeBuilder.classifier_node(
    name="HR",
    classifier=keyword_classifier,
    children=[
        TreeBuilder.intent_node(
            name="AddEmployee",
            param_schema={"name": str, "role": str},
            handler=handle_add_employee,
            arg_extractor=extract_employee_args,
            description="Add new employee"
        )
    ],
    description="HR operations"
)

# Root taxonomy
root = TreeBuilder.classifier_node(
    name="Root",
    classifier=keyword_classifier,
    children=[banking_node, hr_node],
    description="Business operations"
)

# Usage
result = execute_taxonomy(
    user_input="banking:GetBalance account123",
    node=root,
    debug=True
)
```

---

## Core Concepts

### Nodes

* **ClassifierNode**: Routes input to child nodes using a classifier function.
* **IntentNode**: Leaf nodes that execute specific intents with parameter extraction and validation.

### TreeBuilder

Utility class for creating nodes:

```python
# Create intent node
intent_node = TreeBuilder.intent_node(
    name="IntentName",
    param_schema={"param1": str, "param2": int},
    handler=your_handler_function,
    arg_extractor=your_extractor_function,
    input_validator=your_validator_function,  # Optional
    output_validator=your_output_validator,   # Optional
    description="Intent description"
)

# Create classifier node
classifier_node = TreeBuilder.classifier_node(
    name="ClassifierName",
    classifier=your_classifier_function,
    children=[child_node1, child_node2],
    description="Classifier description"
)
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
from intent_kit.services import create_service, get_available_services

# Check available services
print(get_available_services())

# Create AI service client
openai_client = create_service("openai", api_key="your-key")
anthropic_client = create_service("anthropic", api_key="your-key")
google_client = create_service("google", api_key="your-key")
```

### IntentGraph - Multi-Intent Routing

IntentGraph enables routing to multiple intent taxonomies and handling multi-intent user inputs:

```python
from intent_kit.graph import IntentGraph
from intent_kit.graph.splitters import rule_splitter, llm_splitter

# Create IntentGraph with rule-based splitting
graph = IntentGraph(splitter=rule_splitter)
graph.register_taxonomy("travel", TravelTaxonomy())
graph.register_taxonomy("account", AccountTaxonomy())

# Handle multi-intent input
result = graph.route("Cancel my flight and update my email")
# Returns: {"results": [...], "errors": [...]}

# Use LLM-based splitting for complex inputs
graph_llm = IntentGraph(splitter=lambda user_input, taxonomies, debug, **kwargs:
                        llm_splitter(user_input, taxonomies, debug, llm_client))
```

**Key Features:**

* **Intent Splitting**: Decompose multi-intent inputs into sub-intents.
* **Flexible Routing**: Dispatch to one or more taxonomy trees.
* **Multiple Splitters**: Rule-based and LLM-based splitting strategies.
* **Consistent API**: Unified `{"results": [...], "errors": [...]}` return format

See `examples/simple_demo.py` for a complete IntentGraph demonstration with LLM integration.

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

## Project Structure

```
intent-kit/
├── intent_kit/
│   ├── __init__.py          # Main exports
│   ├── node.py              # Node classes (ClassifierNode, IntentNode)
│   ├── tree.py              # TreeBuilder utility
│   ├── engine.py            # Execution engine
│   ├── taxonomy.py          # Intent taxonomy base classes
│   ├── graph/               # IntentGraph multi-intent routing
│   │   ├── intent_graph.py  # Main IntentGraph class
│   │   ├── aggregation.py   # Result aggregation utilities
│   │   └── splitters/       # Intent splitting strategies
│   │       ├── rule_splitter.py
│   │       ├── llm_splitter.py
│   │       └── splitter_types.py
│   ├── classifiers/         # Classification backends
│   │   ├── keyword.py       # Keyword-based classifier
│   │   └── __init__.py
│   ├── services/            # AI service integrations
│   │   ├── openai_service.py
│   │   ├── anthropic_service.py
│   │   ├── google_client.py
│   │   └── __init__.py
│   └── utils/               # Utilities
│       └── logger.py
├── examples/                # Usage examples
│   ├── simple_demo.py       # IntentGraph LLM integration demo
│   └── README.md
├── tests/                   # Test suite
└── pyproject.toml           # Project configuration
```

---

## License

MIT License