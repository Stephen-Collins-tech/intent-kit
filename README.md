<p align="center">
  <img src="assets/logo.png" alt="Intent Kit Logo" height="100" style="border-radius: 16px;"/>
</p>

<h1 align="center">intent-kit</h1>
<p align="center">A Python library for building intent-driven workflows with LLMs.</p>

<p align="center">
  <a href="https://github.com/Stephen-Collins-tech/intent-kit/actions/workflows/ci.yml">
    <img src="https://github.com/Stephen-Collins-tech/intent-kit/actions/workflows/ci.yml/badge.svg" alt="CI"/>
  </a>
  <a href="https://codecov.io/gh/Stephen-Collins-tech/intent-kit">
    <img src="https://codecov.io/gh/Stephen-Collins-tech/intent-kit/branch/main/graph/badge.svg" alt="Coverage Status"/>
  </a>
  <a href="https://docs.intentkit.io">
    <img src="https://img.shields.io/badge/docs-online-blue" alt="Documentation"/>
  </a>
  <a href="https://pypi.org/project/intentkit-py">
    <img src="https://img.shields.io/pypi/v/intentkit-py" alt="PyPI"/>
  </a>
</p>

---

## What is intent-kit?

**intent-kit** is a Python framework for building explicit, composable intent workflows.
Works with any classifier—LLMs, rule-based, or your own.
No forced dependencies. You define all possible intents and parameters up front, so you always stay in control.

* **Zero required dependencies**: Standard Python or plug in OpenAI, Anthropic, Google, Ollama, etc.
* **Explicit and safe**: No emergent "agent" magic.
* **Supports multi-intent, context tracking, validation, and visualization.**

---

## Features

* **Tree-based intent graphs**: Compose hierarchical workflows using classifiers and actions.
* **Any classifier**: Rule-based, ML, LLM, or custom logic.
* **Parameter extraction**: Automatic, with type validation and custom validators.
* **Context/state management**: Dependency tracking and audit trail.
* **Multi-intent**: Split and route complex requests like "Greet Bob and show weather."
* **Visualization**: Interactive graph output (optional).
* **Robust debugging**: JSON/console output and error tracing.

---

## Install

```bash
pip install intent-kit
# Or with extras:
pip install 'intent-kit[openai,anthropic,google,ollama,viz]'
# Or install all LLM providers plus visualization:
pip install 'intent-kit[all]'
# For visualization features only:
pip install 'intent-kit[viz]'
# For development (includes all providers + dev tools):
pip install 'intent-kit[dev]'
```

---

## Quick Start

```python
from intent_kit import IntentGraphBuilder, action, llm_classifier

greet = action(
    name="greet",
    description="Greet the user",
    action_func=lambda name, **_: f"Hello {name}!",
    param_schema={"name": str}
)
weather = action(
    name="weather",
    description="Get weather info",
    action_func=lambda city, **_: f"Weather in {city} is sunny.",
    param_schema={"city": str}
)

classifier = llm_classifier(
    name="root",
    children=[greet, weather],
    llm_config={}
)

graph = IntentGraphBuilder().root(classifier).build()
result = graph.route("Hello Alice")
print(result.output)  # → "Hello Alice!"
```

---

## How it Works

* **Define actions**: Functions for each intent, with schemas.
* **Build classifiers**: Route input with rule-based, LLM, or custom logic.
* **Build graphs**: Combine everything into a tree.
* **(Optional) Multi-intent**: Use splitter nodes for "do X and Y" inputs.
* **Context/state**: Track session or app state in workflows.

See [`examples/`](examples/) for more.

---

## Eval API: Real-World, Dataset-Driven Testing

**Test your intent graphs like real software, not just with unit tests.**

intent-kit includes a first-class **Eval API** for benchmarking your workflows against real datasets—YAML or programmatic. It's built for LLM and intent pipeline evaluation, not just toy examples.

* **Benchmark entire graphs or single nodes** with real data and reproducible reports.
* **Supports YAML or code datasets** (inputs, expected outputs, optional context).
* **Automatic reporting**: Markdown, CSV, and JSON output—easy to share or integrate into CI.
* **Mock mode** for API-free, cheap testing.
* **Tracks regressions over time** with date-based and "latest" result archives.

**Minimal eval example:**

```python
from intent_kit.evals import run_eval, load_dataset
from my_graph import my_node

dataset = load_dataset("intent_kit/evals/datasets/classifier_node_llm.yaml")
result = run_eval(dataset, my_node)

print(f"Accuracy: {result.accuracy():.1%}")
result.save_markdown("my_report.md")
```

**Why care?**
Most "agent" and LLM frameworks are untestable black boxes. **intent-kit** is designed for serious, auditable workflow engineering.

[Learn more in the docs →](https://docs.intentkit.io/evaluation/)

---

## API Highlights

* `action(...)`: Create a leaf node (executes your function, extracts arguments)
* `llm_classifier(...)`: Classifier node using LLM or fallback rule-based logic
* `IntentGraphBuilder()`: Fluent graph assembly
* `rule_splitter_node(...)`, `llm_splitter_node(...)`: Multi-intent input
* `IntentContext`: Track and manage session/context state
* `evals`: Run real dataset-driven benchmarks on your graph

---

## Project Structure

```
intent-kit/
├── intent_kit/        # Library code
├── examples/          # Example scripts
├── tests/             # Unit tests
└── pyproject.toml     # Build config
```

---

## Development

```bash
git clone git@github.com:Stephen-Collins-tech/intent-kit.git
cd intent-kit
# Using pip:
pip install -e ".[dev]"
# Or using uv (recommended):
uv pip install -e ".[dev]"
pytest tests/
```

---

## Documentation

* [Full documentation & guides](https://docs.intentkit.io)
* [API reference](https://docs.intentkit.io/reference/)
* [Evaluation docs](https://docs.intentkit.io/evaluation/)
---

## License

MIT License
