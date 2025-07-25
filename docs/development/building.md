# Building

This guide covers how to build the intent-kit package using uv.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- Environment variables configured (see `.env.example`)

## Development Setup with uv

For development, sync the dev dependencies group:

```bash
uv sync --group dev
```

This will install all development tools and LLM providers as defined in the [dependency-groups] section of your `pyproject.toml`.

If you want an editable install of the library itself:

```bash
uv pip install -e .
```

### Optional Features

- **`[viz]`**: Interactive graph visualization with networkx and pyvis
- **`[all]`**: All LLM providers (OpenAI, Anthropic, Google, Ollama) plus visualization
- **`dev` group**: All providers plus development tools

### Syncing Dependencies

To update the lock file with any dependency changes:

```bash
uv lock
```

This ensures `uv.lock` is up-to-date with your `pyproject.toml` optional dependencies.

## Building

To build the package without including source files:

```bash
uv build --no-sources
```

This creates a distribution package that can be installed locally or used for testing.

## Installing from Wheel

After building, you can install the package directly from the generated wheel file:

```bash
# Find the wheel file in dist/ directory
ls dist/
# Install the wheel file
pip install dist/intentkit_py-<version>-py3-none-any.whl
```

Or install directly from the wheel without copying it:

```bash
# Install from wheel file
pip install --no-index --find-links dist/ intentkit-py
```

### Testing the Wheel

Before using, you can test the wheel installation:

```bash
# Build the wheel
uv build --no-sources

# Install from wheel
pip install dist/intentkit_py-<version>-py3-none-any.whl

# Test the installation
python -c "import intent_kit; print('Installation successful!')"
```

## Version Management

Before building, ensure you've updated the version in `pyproject.toml`:

```toml
[project]
name = "intentkit-py"
version = "0.2.1"  # Update this version
```

## CI/CD Integration

The project includes GitHub Actions workflows that automatically build and test on releases. See `.github/workflows/` for configuration details.
