<p align="center">
  <img src="https://raw.githubusercontent.com/Stephen-Collins-tech/intent-kit/main/assets/logo.png" alt="Intent Kit Logo" height="100"/>
</p>

<h1 align="center">Intent Kit</h1>
<p align="center">Build reliable, auditable AI applications that understand user intent and take intelligent actions</p>

<p align="center" >
  <a style="text-decoration: none;" href="https://github.com/Stephen-Collins-tech/intent-kit/actions/workflows/ci.yml">
    <img src="https://github.com/Stephen-Collins-tech/intent-kit/actions/workflows/ci.yml/badge.svg" alt="CI"/>
  </a>
  <a style="text-decoration: none;" href="https://codecov.io/gh/Stephen-Collins-tech/intent-kit">
    <img src="https://codecov.io/gh/Stephen-Collins-tech/intent-kit/branch/main/graph/badge.svg" alt="Coverage Status"/>
  </a>
  <a style="text-decoration: none;" href="https://docs.intentkit.io">
    <img src="https://img.shields.io/badge/docs-online-blue" alt="Documentation"/>
  </a>
  <a style="text-decoration: none;" href="https://pypi.org/project/intentkit-py">
    <img src="https://img.shields.io/pypi/v/intentkit-py" alt="PyPI"/>
  </a>
  <a style="text-decoration: none;" href="https://pypi.org/project/intentkit-py">
    <img src="https://img.shields.io/pypi/dm/intentkit-py" alt="PyPI Downloads"/>
  </a>
</p>

<p align="center">
  <a href="https://docs.intentkit.io">Docs</a>
</p>

---

## What is Intent Kit?

Intent Kit helps you build AI-powered applications that understand what users want and take the right actions. Think of it as a smart router that can:

- **Understand user requests** using any AI model (OpenAI, Anthropic, Google, or your own)
- **Extract important details** like names, dates, and preferences automatically
- **Take actions** like sending messages, making calculations, or calling APIs
- **Handle complex requests** that involve multiple steps
- **Keep track of conversations** so your app remembers context

The best part? You stay in complete control. You define exactly what your app can do and how it should respond.

---

## Why Intent Kit?

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

### 2. Build Your First Workflow

```python
from intent_kit import IntentGraphBuilder, action, llm_classifier

# Define actions your app can take
greet = action(
    name="greet",
    description="Greet the user by name",
    action_func=lambda name: f"Hello {name}!",
    param_schema={"name": str}
)

# Create a classifier to understand requests
classifier = llm_classifier(
    name="main",
    description="Route to appropriate action",
    children=[greet],
    llm_config={"provider": "openai", "model": "gpt-3.5-turbo"}
)

# Build and test your workflow
graph = IntentGraphBuilder().root(classifier).build()
result = graph.route("Hello Alice")
print(result.output)  # → "Hello Alice!"
```

### 3. Using JSON Configuration

For more complex workflows, use JSON configuration:

```python
from intent_kit import IntentGraphBuilder

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

# Define your graph in JSON
graph_config = {
    "root": "main_classifier",
    "nodes": {
        "main_classifier": {
            "id": "main_classifier",
            "type": "classifier",
            "classifier_type": "llm",
            "name": "main_classifier",
            "description": "Main intent classifier",
            "llm_config": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
            },
            "children": ["greet_action", "calculate_action"],
        },
        "greet_action": {
            "id": "greet_action",
            "type": "action",
            "name": "greet_action",
            "description": "Greet the user",
            "function": "greet",
            "param_schema": {"name": "str"},
        },
        "calculate_action": {
            "id": "calculate_action",
            "type": "action",
            "name": "calculate_action",
            "description": "Perform a calculation",
            "function": "calculate",
            "param_schema": {"operation": "str", "a": "float", "b": "float"},
        },
    },
}

# Build your graph
graph = (
    IntentGraphBuilder()
    .with_json(graph_config)
    .with_functions(function_registry)
    .build()
)

# Test it!
result = graph.route("Hello Alice")
print(result.output)  # → "Hello Alice!"
```

---

## How It Works

Intent Kit uses a simple but powerful pattern:

1. **Actions** - Define what your app can do (send messages, make API calls, etc.)
2. **Classifiers** - Understand what the user wants using AI or rules
3. **Graphs** - Connect everything together into a workflow
4. **Context** - Remember conversations and user preferences

The magic happens when a user sends a message:
- The classifier figures out what they want
- Intent Kit extracts the important details (names, locations, etc.)
- The right action runs with those details
- You get back a response

---

## Reliable & Auditable AI

Most AI frameworks are black boxes that are hard to test and debug. Intent Kit is different - every decision is traceable and testable.

### Test Your Workflows Like Real Software

```python
from intent_kit.evals import run_eval, load_dataset

# Load test cases
dataset = load_dataset("tests/greeting_tests.yaml")

# Test your workflow
result = run_eval(dataset, graph)

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
- Chain actions together
- Handle "do X and Y" requests
- Remember context across conversations

### **Debugging & Transparency**
- Track how decisions are made
- Debug complex flows with full transparency
- Audit decision paths when needed

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
Build intelligent bots that understand natural language and take appropriate actions.

### **Task Automation**
Automate complex workflows that require understanding user intent.

### **Data Processing**
Route and process information based on what users are asking for.

### **Decision Systems**
Create systems that make smart decisions based on user requests.

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
