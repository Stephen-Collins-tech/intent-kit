# Intent Kit - Cursor Rules

## Project Overview

Intent Kit is a Python library for building hierarchical intent classification and execution systems. It provides a tree-based intent architecture with classifier and action nodes, supports multiple AI service backends, and enables context-aware execution.

## Code Style & Standards

### Python Code

* Use Python 3.11+ features and type hints throughout.
* Follow [PEP 8](https://peps.python.org/pep-0008/) with 4-space indentation.
* Use descriptive variable and function names.
* Prefer composition over inheritance.
* Use `dataclasses` for data structures.
* Add comprehensive docstrings for all public classes, methods, and functions (Google-style).
* Use type hints for all function parameters and return values.

### Import Organization

* Group imports in the following order: standard library, third-party, local imports.
* Example:

  ```python
  # Standard library imports
  import os
  import sys
  from typing import Dict, List, Optional

  # Third-party imports
  import yaml
  import anthropic

  # Local imports
  from intent_kit.nodes import TreeNode
  from intent_kit.graph import IntentGraphBuilder
  ```
* Consider using [isort](https://pycqa.github.io/isort/) for automatic import sorting.

### Error Handling

* Use custom exceptions from `intent_kit.exceptions`.
* Provide meaningful error messages in all exceptions.
* Log errors with relevant context.
* Use context managers for resource management.

## Architecture Patterns

### Node System

* All nodes inherit from `TreeNode` or appropriate base classes.
* Classifier nodes must implement `ClassifierNode`.
* Action nodes must implement `ActionNode`.
* Use builder patterns for complex node construction.
* Validate node configurations at creation time and raise on invalid configs.

### Graph Building

* Use `IntentGraphBuilder` for graph construction.
* Validate the entire graph structure before execution.
* Support both synchronous and asynchronous execution.
* Ensure proper context propagation throughout the graph.

### AI Service Integration

* Use the factory pattern for LLM client instantiation.
* Support multiple AI providers (OpenAI, Anthropic, Google, Ollama).
* Wrap all API calls with try/except and raise custom exceptions for provider-specific errors.
* Select AI providers via configuration, supporting environment variable overrides.

## Testing Requirements

### Test Structure

* Mirror the source code directory structure under `tests/`.
* Use clear, descriptive test function names (e.g., `test_[scenario]_[expected_result]`).
* Group related tests within `pytest` classes for organization.
* Use fixtures for common setup and teardown logic.

### Test Coverage

* Aim for 90%+ code coverage.
* Test both success and failure scenarios.
* Test edge cases and error conditions.
* Use parameterized tests for similar scenarios.

### Test Example

```python
import pytest
from intent_kit.nodes import TreeNode
from intent_kit.graph import IntentGraphBuilder

class TestIntentGraph:
    def test_basic_graph_construction(self):
        """Test that a basic graph can be constructed."""
        builder = IntentGraphBuilder()
        # Test implementation

    def test_graph_validation(self):
        """Test that invalid graphs are rejected."""
        # Test implementation
```

## Documentation Standards

### Code Documentation

* Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for all public classes, methods, and functions.
* Include type information and document all parameters and return values in docstrings.
* Document exceptions that may be raised.
* Provide usage examples in docstrings where helpful.

### API Documentation

* Document all public APIs in the `docs/` directory.
* Include code examples for each major feature.
* Keep documentation up to date with code changes.
* Use consistent formatting and structure across all docs.

## Development Workflow

### Code Quality

* Use `uv run pytest` for running tests.
* Use `ruff` for linting and formatting.
* Use `mypy` for type checking (with strict settings; see `mypy.ini` if present).
* Fix all linting, type checking, and test errors before committing.
* Use [pre-commit](https://pre-commit.com/) hooks for automating linting, formatting, and type checks if available.

### Git Workflow

* Use descriptive commit messages that explain *why*, not just *what*.
* Keep commits focused and atomic (one change per commit).
* Update `CHANGELOG.md` for all user-facing changes.
* Bump version numbers appropriately (per [semantic versioning](https://semver.org/) if possible).
* Follow PR checklist (if used): tests pass, lint passes, docs updated, changelog updated.

## File Organization

### Module Structure

* Keep related functionality together within modules.
* Use `__init__.py` files to expose public APIs.
* Separate concerns into clear, focused modules.
* Use relative imports within the package for internal code.

### Configuration

* Use YAML for configuration files.
* Validate configuration at load time and raise on invalid config.
* Provide sensible defaults for all config options.
* Support environment variable overrides for sensitive or environment-specific config.

## Performance Considerations

### Optimization

* Profile code to identify and address performance bottlenecks.
* Use async/await for I/O operations.
* Implement caching where beneficial.
* Monitor memory usage in long-running processes.

### Monitoring

* Use structured logging throughout the codebase.
* Track execution times for key operations.
* Monitor API call costs and usage.
* Implement robust error tracking.

## Security Guidelines

### Input Validation

* Validate all user inputs rigorously.
* Sanitize all data before processing.
* Use parameterized queries for database operations.
* Implement authentication and authorization where required.

### API Security

* Secure API keys and credentials using environment variables.
* Never commit secrets or credentials to version control.
* Implement rate limiting where appropriate.
* Log security-relevant events.

## Dependencies

### Package Management

* Use `uv` for dependency management.
* Pin dependency versions in `pyproject.toml`.
* Keep dependencies minimal and focused on project requirements.
* Regularly update dependencies for security; review third-party licenses for compatibility before adding.

### External Services

* Implement robust error handling for all external API calls.
* Use retry logic for transient failures.
* Monitor and respect API rate limits.
* Implement fallback mechanisms where feasible.

## Examples and Demos

### Code Examples

* Keep examples simple, realistic, and focused.
* Always include error handling in examples.
* Document all assumptions and prerequisites for running examples.

### Documentation Examples

* Ensure all code examples are tested and runnable.
* Keep examples updated with API changes.
* Provide expected outputs where it aids understanding.

## Context and Memory

### Project-Specific Rules

* This is a **pre-v1** codebase – no backward compatibility required (subject to change after v1).
* **Always use `uv run` for running Python commands** (e.g., `uv run pytest`, `uv run python script.py`).
* Refer to handlers as "actions" in all documentation.
* Focus on building reliable, auditable AI applications.

### AI Integration Patterns

* Use the factory pattern for LLM client instantiation.
* Support multiple AI providers.
* Implement context management for all LLM executions.
* Provide clear execution traces for all operations.

## Common Patterns

### Node Creation

```python
from intent_kit.nodes.actions import ActionNode
from intent_kit.nodes.classifiers import ClassifierNode

# Create action node
action = ActionNode(
    name="example_action",
    description="Example action description",
    action_func=lambda **kwargs: "result"
)

# Create classifier node
classifier = ClassifierNode(
    name="example_classifier",
    description="Example classifier description",
    children=[action]
)
```

### Graph Building

```python
from intent_kit.graph import IntentGraphBuilder

builder = IntentGraphBuilder()
graph = builder.add_node(classifier).build()
```

### Context Management

```python
from intent_kit.context import Context

context = Context()
result = graph.execute("user input", context)
```

## Pull Request Checklist (optional)

* [ ] All tests pass (`uv run pytest`)
* [ ] Code is linted and formatted (`ruff`)
* [ ] Type checks pass (`mypy`)
* [ ] Documentation is updated as needed
* [ ] CHANGELOG.md updated for user-facing changes
* [ ] No secrets or credentials in commits

---

**Remember:** This is an AI-focused library. Prioritize reliability, transparency, and user control in all implementations.
