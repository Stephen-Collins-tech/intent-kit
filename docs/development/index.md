# Development

Welcome to the Development section of the Intent Kit documentation. Here you'll find guides and resources for building, testing, evaluating, and debugging your Intent Kit projects.

## Topics

- **[Building](building.md)** - How to build the package
- **[Testing](testing.md)** - Unit tests and integration testing
- **[Evaluation](evaluation.md)** - Performance evaluation and benchmarking
- **[Debugging](debugging.md)** - Debugging tools and techniques
- **[Performance Monitoring](performance-monitoring.md)** - Performance tracking and reporting
- **[Documentation Management](documentation-management.md)** - Managing and maintaining documentation

## Development Workflow

### Getting Started

1. **Install Dependencies** - Use `uv` for dependency management
2. **Run Tests** - Use `uv run pytest` for testing
3. **Code Quality** - Use `ruff` for linting and formatting
4. **Type Checking** - Use `mypy` for type validation

### Key Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Lint and format code
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy

# Build package
uv run python -m build
```

## Architecture Overview

Intent Kit uses a DAG-based architecture with:

- **Core DAG Types** - `IntentDAG`, `GraphNode`, `ExecutionResult`
- **Node Protocol** - Standard interface for all executable nodes
- **Context System** - State management with type safety and audit trails
- **Traversal Engine** - BFS-based execution with memoization and limits

## Contributing

For additional information, see the [project README on GitHub](https://github.com/Stephen-Collins-tech/intent-kit#readme) or explore other sections of the documentation.
