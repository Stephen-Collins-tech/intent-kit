# Building and Publishing

This guide covers how to build and publish the intent-kit package using uv.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- Access to PyPI (for publishing)
- Environment variables configured (see `.env.example`)

## Development Setup with uv

For development, install with all dependencies:

```bash
uv pip install -e ".[dev]"
```

This installs the package in editable mode with all development tools and LLM providers.

### Optional Features

- **`[viz]`**: Interactive graph visualization with networkx and pyvis
- **`[all]`**: All LLM providers (OpenAI, Anthropic, Google, Ollama) plus visualization
- **`[dev]`**: All providers plus development tools

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

This creates a distribution package that can be published to PyPI.

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

Before publishing, you can test the wheel installation:

```bash
# Build the wheel
uv build --no-sources

# Install from wheel
pip install dist/intentkit_py-<version>-py3-none-any.whl

# Test the installation
python -c "import intent_kit; print('Installation successful!')"
```

## Publishing

To publish the package to PyPI:

```bash
UV_PUBLISH_TOKEN=$UV_PUBLISH_TOKEN uv publish
```

### Environment Setup

Make sure your environment variables are set:

```bash
# Copy from .env.example and fill in your values
UV_PUBLISH_TOKEN=your_pypi_token_here
```

### Publishing Process

1. **Build the package**: `uv build --no-sources`
2. **Test the wheel**: `pip install dist/intentkit_py-<version>-py3-none-any.whl`
3. **Set token**: `export UV_PUBLISH_TOKEN=your_pypi_token_here`
4. **Publish**: `UV_PUBLISH_TOKEN=$UV_PUBLISH_TOKEN uv publish`

## Version Management

Before publishing, ensure you've updated the version in `pyproject.toml`:

```toml
[project]
name = "intentkit-py"
version = "0.2.1"  # Update this version
```

## CI/CD Integration

The project includes GitHub Actions workflows that automatically build and publish on releases. See `.github/workflows/` for configuration details.

## Troubleshooting

### Common Issues

- **Authentication errors**: Ensure `UV_PUBLISH_TOKEN` is set correctly
- **Version conflicts**: Make sure the version in `pyproject.toml` is higher than the current PyPI version
- **Build failures**: Check that all dependencies are properly specified in `pyproject.toml`

### Verification

After publishing, verify the package is available:

```bash
pip install intentkit-py==<version>
```

## Related Documentation

- [Development Setup](index.md)
- [Testing](testing.md)
- [Evaluation](evaluation.md)
