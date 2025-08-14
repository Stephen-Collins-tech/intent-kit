# Intent Kit

Build reliable, auditable AI applications that understand user intent and take intelligent actions

  [![CI](https://img.shields.io/github/actions/workflow/status/Stephen-Collins-tech/intent-kit/ci.yml?branch=main&logo=github&label=CI)](https://github.com/Stephen-Collins-tech/intent-kit/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)
  [![Coverage](https://codecov.io/gh/Stephen-Collins-tech/intent-kit/branch/main/graph/badge.svg)](https://codecov.io/gh/Stephen-Collins-tech/intent-kit)
  [![PyPI](https://img.shields.io/pypi/v/intentkit-py.svg)](https://pypi.python.org/pypi/intentkit-py)
  [![Downloads](https://static.pepy.tech/badge/intentkit-py/month)](https://pepy.tech/project/intentkit-py)
  [![Versions](https://img.shields.io/pypi/pyversions/intentkit-py.svg)](https://github.com/Stephen-Collins-tech/intent-kit)
  [![License](https://img.shields.io/github/license/Stephen-Collins-tech/intent-kit.svg)](https://github.com/Stephen-Collins-tech/intent-kit/blob/main/LICENSE)
  [![Documentation](https://img.shields.io/badge/docs-online-blue)](https://docs.intentkit.io)

<p align="center">
  <a href="https://docs.intentkit.io">Docs</a>
</p>

---

## What is Intent Kit?

Intent Kit helps you build AI-powered applications that understand what users want and take the right actions. Built on a flexible DAG (Directed Acyclic Graph) architecture, it provides:

- **Smart Intent Understanding** using any AI model (OpenAI, Anthropic, Google, or your own)
- **Automatic Parameter Extraction** for names, dates, preferences, and more
- **Flexible Action Execution** like sending messages, making calculations, or calling APIs
- **Complex Multi-Step Workflows** with reusable nodes and flexible routing
- **Context-Aware Conversations** that remember user preferences and conversation history
- **Node Reuse & Modularity** - share nodes across different execution paths

The best part? You stay in complete control. You define exactly what your app can do and how it should respond.

---

## Why Intent Kit?

### **Flexible & Scalable**
DAG-based architecture allows complex workflows with node reuse, fan-out/fan-in patterns, and multiple entry points.

### **Reliable & Auditable**
Every decision is traceable. Test your workflows thoroughly and deploy with confidence knowing exactly how your AI will behave.

### **You're in Control**
Define every possible action upfront. No black boxes, no unexpected behavior, no surprises.

### **Works with Any AI**
Use OpenAI, Anthropic, Google, Ollama, or even simple rules. Mix and match as needed.

### **Easy to Build**
Simple, clear API that feels natural to use. No complex abstractions to learn.

### **See What's Happening**
Track exactly how decisions are made and debug with full transparency.

---

## Quick Start

### 1. Install Intent Kit

```bash
pip install intentkit-py
```

For AI features, add your preferred provider:
```bash
pip install 'intentkit-py[openai]'    # OpenAI
pip install 'intentkit-py[anthropic]'  # Anthropic
pip install 'intentkit-py[all]'        # All providers
```

### 2. Build Your First DAG Workflow

```python
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

# Define actions your app can take
def greet(name: str) -> str:
    return f"Hello {name}!"

def get_weather(city: str) -> str:
    return f"Weather in {city} is sunny"

# Create DAG
builder = DAGBuilder()

# Set default LLM configuration
builder.with_default_llm_config({
    "provider": "openai",
    "model": "gpt-3.5-turbo"
})

# Add classifier node
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "weather"],
                 description="Route to appropriate action")

# Add extractors
builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name from greeting",
                 output_key="extracted_params")

builder.add_node("extract_city", "extractor",
                 param_schema={"city": str},
                 description="Extract city from weather request",
                 output_key="extracted_params")

# Add actions
builder.add_node("greet_action", "action",
                 function=greet,
                 param_schema={"name": str},
                 description="Greet the user")

builder.add_node("weather_action", "action",
                 function=get_weather,
                 param_schema={"city": str},
                 description="Get weather information")

# Add edges
builder.add_edge("classifier", "extract_name", "greet")
builder.add_edge("classifier", "extract_city", "weather")
builder.add_edge("extract_name", "greet_action")
builder.add_edge("extract_city", "weather_action")

# Build and test your DAG
dag = builder.build()
context = DefaultContext()

result, final_context = run_dag(dag, "Hello Alice", context)
print(result.data)  # → "Hello Alice!"
```

### 3. Using JSON Configuration

For more complex workflows, use JSON configuration:

```python
from intent_kit import DAGBuilder

# Define your functions
def greet(name, context=None):
    return f"Hello {name}!"

def calculate(operation, a, b, context=None):
    if operation == "add":
        return a + b
    return None

# Create function registry
function_registry = {
    "greet": greet,
    "calculate": calculate,
}

# Define your DAG in JSON
dag_config = {
    "entrypoints": ["main_classifier"],
    "nodes": {
        "main_classifier": {
            "type": "classifier",
            "config": {
                "description": "Main intent classifier",
                "llm_config": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                },
                "output_labels": ["greet", "calculate"]
            }
        },
        "greet_action": {
            "type": "action",
            "config": {
                "function": "greet",
                "param_schema": {"name": "str"},
                "description": "Greet the user"
            }
        },
        "calculate_action": {
            "type": "action",
            "config": {
                "function": "calculate",
                "param_schema": {"operation": "str", "a": "float", "b": "float"},
                "description": "Perform a calculation"
            }
        },
    },
    "edges": [
        {"from": "main_classifier", "to": "greet_action", "label": "greet"},
        {"from": "main_classifier", "to": "calculate_action", "label": "calculate"}
    ]
}

# Build your DAG
dag = (
    DAGBuilder()
    .with_json(dag_config)
    .with_functions(function_registry)
    .build()
)

# Test it!
context = DefaultContext()
result, final_context = run_dag(dag, "Hello Alice", context)
print(result.data)  # → "Hello Alice!"
```

---

## How It Works

Intent Kit uses a powerful DAG (Directed Acyclic Graph) pattern:

1. **Nodes** - Define decision points, extractors, or actions
2. **Edges** - Connect nodes with optional labels for flexible routing
3. **Entrypoints** - Starting nodes for user input
4. **Context** - Remember conversations and user preferences across nodes

The magic happens when a user sends a message:
- The classifier figures out what they want and routes to appropriate nodes
- Extractors pull out important details (names, locations, etc.)
- Actions execute with those details
- Context flows through the DAG, enabling complex multi-step workflows
- You get back a response with full execution trace

### DAG Benefits

- **Node Reuse** - Share nodes across different execution paths
- **Flexible Routing** - Support fan-out, fan-in, and complex patterns
- **Multiple Entry Points** - Handle different types of input
- **Deterministic Execution** - Predictable, testable behavior
- **Context Propagation** - State flows through the entire workflow

---

## Reliable & Auditable AI

Most AI frameworks are black boxes that are hard to test and debug. Intent Kit is different - every decision is traceable and testable.

### Test Your Workflows Like Real Software

```python
from intent_kit.evals import run_eval, load_dataset

# Load test cases
dataset = load_dataset("tests/greeting_tests.yaml")

# Test your workflow
result = run_eval(dataset, dag)

print(f"Accuracy: {result.accuracy():.1%}")
result.save_report("test_results.md")
```

### What You Can Test & Audit

- **Accuracy** - Does your workflow understand requests correctly?
- **Performance** - How fast does it respond?
- **Edge Cases** - What happens with unusual inputs?
- **Regressions** - Catch when changes break existing functionality
- **Decision Paths** - Trace exactly how each decision was made
- **Bias Detection** - Identify potential biases in your workflows

This means you can deploy with confidence, knowing your AI workflows work reliably and can be audited when needed.

---

## Key Features

### **Flexible DAG Architecture**
- Node reuse across different execution paths
- Support for fan-out, fan-in, and complex routing patterns
- Multiple entry points for different input types
- Deterministic execution with full traceability

### **Reliable & Auditable**
- Every decision is traceable and testable
- Comprehensive testing framework
- Full transparency into AI decision-making
- Bias detection and mitigation tools

### **Smart Understanding**
- Works with any AI model (OpenAI, Anthropic, Google, Ollama)
- Extracts parameters automatically (names, dates, preferences)
- Handles complex, multi-step requests

### **Multi-Step Workflows**
- Chain actions together with flexible routing
- Handle "do X and Y" requests
- Remember context across conversations
- Support for complex branching and merging

### **Debugging & Transparency**
- Track how decisions are made
- Debug complex flows with full transparency
- Audit decision paths when needed
- Context propagation tracking

### **Developer Friendly**
- Simple, clear API
- Comprehensive error handling
- Built-in debugging tools
- JSON configuration support

### **Testing & Evaluation**
- Test against real datasets
- Measure accuracy and performance
- Catch regressions automatically
- Validate reliability before deployment

### **Security**
- Automated security audits with pip-audit
- Vulnerability scanning in CI/CD pipeline
- Dependency security monitoring

---

## Common Use Cases

### **Chatbots & Virtual Assistants**
Build intelligent bots that understand natural language and take appropriate actions with context awareness.

### **Task Automation**
Automate complex workflows that require understanding user intent and multi-step processing.

### **Data Processing**
Route and process information based on what users are asking for with flexible DAG patterns.

### **Decision Systems**
Create systems that make smart decisions based on user requests with full audit trails.

### **Multi-Modal Workflows**
Handle complex scenarios requiring multiple classifiers, extractors, and actions working together.

---

## Installation Options

```bash
# Basic installation (Python only)
pip install intentkit-py

# With specific AI providers
pip install 'intentkit-py[openai]'      # OpenAI
pip install 'intentkit-py[anthropic]'    # Anthropic
pip install 'intentkit-py[google]'       # Google AI
pip install 'intentkit-py[ollama]'       # Ollama

# Everything (all providers + tools)
pip install 'intentkit-py[all]'

# Development (includes testing tools)
pip install 'intentkit-py[dev]'
```

---

## Project Structure

```
intent-kit/
├── intent_kit/           # Main library code
│   ├── core/            # DAG engine, traversal, validation
│   ├── nodes/           # Node implementations
│   ├── services/        # AI services and utilities
│   └── utils/           # Helper utilities
├── examples/             # Working examples
├── docs/                 # Documentation
├── tests/                # Test suite
├── scripts/              # Development utilities
├── tasks/                # Project roadmap and tasks
├── assets/               # Project assets (logo, etc.)
└── pyproject.toml        # Project configuration
```

---

## Getting Help

- **[Full Documentation](https://docs.intentkit.io)** - Guides, API reference, and examples
- **[Quickstart Guide](https://docs.intentkit.io/quickstart/)** - Get up and running fast
- **[Examples](https://docs.intentkit.io/examples/)** - See how others use Intent Kit
- **[GitHub Issues](https://github.com/Stephen-Collins-tech/intent-kit/issues)** - Report bugs or ask questions

---

## Development & Contribution

### Setup

```bash
git clone git@github.com:Stephen-Collins-tech/intent-kit.git
cd intent-kit
uv sync --group dev
uv run pre-commit install
```

### Development Commands

```bash
uv run pytest          # Run tests
uv run lint            # Lint code
uv run black --fix .   # Format and fix code
uv run typecheck       # Type checking
uv run security        # Security audit
uv build               # Build package
```

This project uses [`uv`](https://github.com/astral-sh/uv) for fast, reproducible Python workflows and pre-commit hooks for code quality.

---

## Contributing

We welcome contributions! See our [GitHub Issues](https://github.com/Stephen-Collins-tech/intent-kit/issues) for discussions and our [Development section](#development--contribution) for setup instructions.

---

## License

MIT License - feel free to use Intent Kit in your projects!
