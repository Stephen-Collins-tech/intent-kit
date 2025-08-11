# Intent Kit Examples

This directory contains focused examples demonstrating Intent Kit's features. Each example is self-contained and highlights specific aspects of the library.

## Getting Started

### 🚀 **[simple_demo.py](simple_demo.py)** - **START HERE** (103 lines)
The most basic Intent Kit example - perfect for beginners:
- Basic graph building with JSON configuration
- Simple action functions (greet, calculate, weather)
- LLM-based intent classification
- Built-in operation tracking via Context
- Clean, minimal implementation

**Run it:** `python examples/simple_demo.py`

## Focused Feature Demos

### 🧮 **[calculator_demo.py](calculator_demo.py)** - Comprehensive Calculator
A full-featured calculator showcasing:
- Basic arithmetic (+, -, *, /)
- Advanced math (sqrt, sin, cos, power, factorial, etc.)
- Memory functions (last result, history, clear)
- Parameter validation and error handling
- Interactive calculator mode
- Context-aware calculations

### 🔄 **[context_management_demo.py](context_management_demo.py)** - Context Deep Dive
Master Intent Kit's context system:
- Basic context operations (get, set, delete, keys)
- Session state management and persistence
- StackContext for function call tracking
- Interactive context exploration
- Context field lifecycle and history

### 📊 **[error_tracking_demo.py](error_tracking_demo.py)** - Operation Monitoring
Comprehensive error tracking and monitoring:
- Automatic operation success/failure tracking
- Built-in Context error collection
- Detailed error statistics and reporting
- Error type distribution analysis
- Operation performance metrics
- Intentionally error-prone scenarios for demonstration

## Legacy/Specialized Demos

These demos focus on specific features and may be longer/more complex:

- **[classifier_output_demo.py](classifier_output_demo.py)** - Type-safe LLM output handling
- **[typed_output_demo.py](typed_output_demo.py)** - Structured LLM response handling
- **[type_validation_demo.py](type_validation_demo.py)** - Runtime type checking
- **[context_demo.py](context_demo.py)** - Basic context operations
- **[context_with_graph_demo.py](context_with_graph_demo.py)** - Context integration
- **[stack_context_demo.py](stack_context_demo.py)** - Execution tracking
- **[performance_demo.py](performance_demo.py)** - Performance analysis

## Running the Examples

### Prerequisites

1. Install Intent Kit and dependencies:
   ```bash
   pip install -e .
   ```

2. Set up environment variables (copy `env.example` to `.env`):
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

### Running Individual Examples

Each example can be run independently:

```bash
# Start with the simple demo
python examples/simple_demo.py

# Explore specific features
python examples/context_demo.py
python examples/performance_demo.py
python examples/error_handling_demo.py
```

### Interactive vs Batch Mode

- **simple_demo.py** offers both batch demonstration and interactive chat mode
- Other examples run in batch mode showing specific feature demonstrations
- All examples include detailed console output explaining what's happening

## Example Progression

**Recommended learning path:**

1. **simple_demo.py** - Understand basic concepts
2. **context_demo.py** - Learn context system
3. **context_with_graph_demo.py** - See context in graphs
4. **error_handling_demo.py** - Handle errors gracefully
5. **performance_demo.py** - Monitor and optimize
6. **stack_context_demo.py** - Advanced debugging
7. **classifier_output_demo.py** - Type-safe outputs

## Key Concepts Demonstrated

### Graph Building
- JSON configuration approach
- Function registry pattern
- LLM configuration management
- Node types (classifiers, actions)

### Context Management
- Session-based isolation
- State persistence
- History tracking
- Error accumulation
- Debug information

### Error Handling
- Custom exception types
- Validation patterns
- Recovery strategies
- Error categorization

### Performance
- Timing and profiling
- Memory monitoring
- Load testing
- Benchmarking different configurations

### Type Safety
- Runtime type validation
- Structured output handling
- Parameter schema enforcement
- Enum validation

## Configuration

All examples use OpenRouter by default but can be configured for other providers:

```python
LLM_CONFIG = {
    "provider": "openrouter",  # or "openai", "anthropic", "google", "ollama"
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "mistralai/ministral-8b",
}
```

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure your `.env` file contains valid API keys
2. **Import Errors**: Run `pip install -e .` from the project root
3. **Model Not Found**: Check that your API key has access to the specified model

### Debug Mode

Most examples support debug mode for detailed execution information:

```python
# Enable debug context and tracing
graph = (
    IntentGraphBuilder()
    .with_json(config)
    .with_debug_context(True)
    .with_context_trace(True)
    .build()
)
```

## Contributing

When adding new examples:

1. Follow the existing naming convention: `feature_demo.py`
2. Include comprehensive docstrings explaining the purpose
3. Add the example to this README with proper categorization
4. Ensure examples are self-contained and runnable
5. Include both success and error scenarios where applicable

## Need Help?

- Check the [main documentation](../docs/) for detailed API reference
- Review existing examples for implementation patterns
- Look at the test suite for additional usage examples
