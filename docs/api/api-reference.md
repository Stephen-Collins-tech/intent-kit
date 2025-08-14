# API Reference

This document provides a comprehensive reference for the Intent Kit API.

## Table of Contents

- [Core Classes](#core-classes)
- [Node Types](#node-types)
- [Context Management](#context-management)
- [LLM Integration](#llm-integration)
- [Configuration](#configuration)
- [Utilities](#utilities)

## Core Classes

### DAGBuilder

The main builder class for creating intent DAGs.

```python
from intent_kit import DAGBuilder
```

#### Constructor

```python
DAGBuilder()
```

Creates a new DAG builder instance.

#### Methods

##### `add_node(node_id, node_type, **config)`
Add a node to the DAG.

**Parameters:**
- `node_id` (str): Unique identifier for the node
- `node_type` (str): Type of node ("classifier", "extractor", "action", "clarification")
- `**config`: Node-specific configuration

**Examples:**

```python
builder = DAGBuilder()

# Add classifier node
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "weather"],
                 description="Main intent classifier")

# Add extractor node
builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name from greeting",
                 output_key="extracted_params")

# Add action node
builder.add_node("greet_action", "action",
                 action=greet_function,
                 description="Greet the user")

# Add clarification node
builder.add_node("clarification", "clarification",
                 clarification_message="I'm not sure what you'd like me to do.",
                 available_options=["Say hello", "Ask about weather"],
                 description="Handle unclear requests")
```

##### `add_edge(from_node, to_node, label=None)`
Add an edge between nodes.

**Parameters:**
- `from_node` (str): Source node ID
- `to_node` (str): Target node ID
- `label` (str, optional): Edge label for conditional routing

**Examples:**

```python
# Connect classifier to extractor
builder.add_edge("classifier", "extract_name", "greet")

# Connect extractor to action
builder.add_edge("extract_name", "greet_action", "success")

# Add error handling edge
builder.add_edge("extract_name", "clarification", "error")

# Add clarification to retry
builder.add_edge("clarification", "classifier", "retry")
```

##### `set_entrypoints(entrypoints)`
Set the entry points for the DAG.

**Parameters:**
- `entrypoints` (List[str]): List of node IDs that can receive initial input

**Example:**

```python
builder.set_entrypoints(["classifier"])
```

##### `with_default_llm_config(config)`
Set default LLM configuration for the DAG.

**Parameters:**
- `config` (dict): LLM configuration dictionary

**Example:**

```python
llm_config = {
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "api_key": "your-openrouter-api-key",
    "temperature": 0.1
}

builder.with_default_llm_config(llm_config)
```

##### `from_json(config)`
Create a DAGBuilder from JSON configuration.

**Parameters:**
- `config` (dict): DAG configuration dictionary

**Example:**

```python
dag_config = {
    "nodes": {
        "classifier": {
            "type": "classifier",
            "output_labels": ["greet", "weather"],
            "description": "Main intent classifier",
            "llm_config": {
                "provider": "openrouter",
                "model": "google/gemma-2-9b-it"
            }
        },
        "greet_action": {
            "type": "action",
            "action": greet_function,
            "description": "Greet the user"
        }
    },
    "edges": [
        {"from": "classifier", "to": "greet_action", "label": "greet"}
    ],
    "entrypoints": ["classifier"]
}

dag = DAGBuilder.from_json(dag_config)
```

##### `build(validate_structure=True, producer_labels=None)`
Build and return the final DAG instance.

**Parameters:**
- `validate_structure` (bool): Whether to validate the DAG structure before returning
- `producer_labels` (Dict[str, Set[str]], optional): Dictionary mapping node_id to set of labels it can produce

**Returns:**
- `IntentDAG`: Configured DAG instance

**Raises:**
- `ValueError`: If validation fails and validate_structure is True
- `CycleError`: If a cycle is detected and validate_structure is True

**Example:**

```python
dag = builder.build()
```

##### `freeze()`
Make the DAG immutable to catch mutation bugs.

**Returns:**
- `DAGBuilder`: Self for method chaining

**Example:**

```python
builder.freeze()  # DAG becomes immutable
```

##### `remove_node(node_id)`
Remove a node and all its edges.

**Parameters:**
- `node_id` (str): The node ID to remove

**Returns:**
- `DAGBuilder`: Self for method chaining

**Raises:**
- `RuntimeError`: If DAG is frozen
- `ValueError`: If node doesn't exist

**Example:**

```python
builder.remove_node("unused_node")
```

##### `get_outgoing_edges(node_id)`
Get outgoing edges from a node.

**Parameters:**
- `node_id` (str): The node ID

**Returns:**
- `Dict[EdgeLabel, Set[str]]`: Dictionary mapping edge labels to sets of destination node IDs

**Example:**

```python
edges = builder.get_outgoing_edges("classifier")
print(edges)  # → {"greet": {"extractor"}, "weather": {"weather_action"}}
```

##### `get_incoming_edges(node_id)`
Get incoming edges to a node.

**Parameters:**
- `node_id` (str): The node ID

**Returns:**
- `Set[str]`: Set of source node IDs

**Example:**

```python
sources = builder.get_incoming_edges("action")
print(sources)  # → {"extractor"}
```

##### `has_edge(src, dst, label=None)`
Check if an edge exists.

**Parameters:**
- `src` (str): Source node ID
- `dst` (str): Destination node ID
- `label` (EdgeLabel, optional): Optional edge label

**Returns:**
- `bool`: True if the edge exists, False otherwise

**Example:**

```python
if builder.has_edge("classifier", "extractor", "greet"):
    print("Edge exists")
```

### IntentDAG

The main DAG class for executing intent workflows.

```python
from intent_kit import IntentDAG
```

#### Methods

##### `execute(input_text, context=None)`
Execute the DAG with the given input.

**Parameters:**
- `input_text` (str): User input to process
- `context` (Context, optional): Context instance for state management

**Returns:**
- `ExecutionResult`: Result of the execution

**Example:**

```python
from intent_kit.core.context import DefaultContext

context = DefaultContext()
result = dag.execute("Hello Alice", context)
print(result.data)  # → "Hello Alice!"
```

##### `validate()`
Validate the DAG structure.

**Returns:**
- `bool`: True if valid, raises exception if invalid

**Example:**

```python
try:
    dag.validate()
    print("DAG is valid")
except Exception as e:
    print(f"DAG validation failed: {e}")
```

## Node Types

### ClassifierNode

Classifies user intent and routes to appropriate paths.

```python
from intent_kit.nodes.classifier import ClassifierNode
```

#### Constructor

```python
ClassifierNode(
    name: str,
    output_labels: List[str],
    description: str = "",
    llm_config: Optional[Dict[str, Any]] = None,
    classification_func: Optional[Callable[[str, Any], str]] = None,
    custom_prompt: Optional[str] = None,
    context_read: Optional[List[str]] = None,
    context_write: Optional[List[str]] = None
)
```

**Parameters:**
- `name` (str): Node name
- `output_labels` (List[str]): Possible output labels
- `description` (str, optional): Description of the classifier's purpose
- `llm_config` (Dict[str, Any], optional): LLM configuration
- `classification_func` (Callable[[str, Any], str], optional): Custom classification function
- `custom_prompt` (str, optional): Custom prompt for classification
- `context_read` (List[str], optional): List of context keys to read before execution
- `context_write` (List[str], optional): List of context keys to write after execution

**Example:**

```python
classifier = ClassifierNode(
    name="main_classifier",
    output_labels=["greet", "calculate", "weather"],
    description="Route user requests to appropriate actions",
    llm_config={"provider": "openai", "model": "gpt-4"}
)
```

#### Execute Method

```python
def execute(self, user_input: str, ctx: ContextProtocol) -> ExecutionResult:
    """Execute the classifier node.

    Args:
        user_input: User input string to classify
        ctx: Execution context containing LLM service and other state

    Returns:
        ExecutionResult with classification label and routing information
    """
```

**Important:** All nodes receive the context as the second parameter in their `execute` method, allowing them to access shared state, LLM services, and other execution context.

### ExtractorNode

Extracts parameters from natural language using LLM.

```python
from intent_kit.nodes.extractor import ExtractorNode
```

#### Constructor

```python
ExtractorNode(
    name: str,
    param_schema: Dict[str, Union[Type[Any], str]],
    description: str = "",
    llm_config: Optional[Dict[str, Any]] = None,
    custom_prompt: Optional[str] = None,
    output_key: str = "extracted_params",
    context_read: Optional[List[str]] = None,
    context_write: Optional[List[str]] = None
)
```

**Parameters:**
- `name` (str): Node name
- `param_schema` (Dict[str, Union[Type[Any], str]]): Schema defining parameters to extract
- `description` (str, optional): Description of what to extract
- `llm_config` (Dict[str, Any], optional): LLM configuration
- `custom_prompt` (str, optional): Custom prompt for parameter extraction
- `output_key` (str, optional): Key for storing extracted parameters in context
- `context_read` (List[str], optional): List of context keys to read before execution
- `context_write` (List[str], optional): List of context keys to write after execution

**Example:**

```python
extractor = ExtractorNode(
    name="name_extractor",
    param_schema={"name": str},
    description="Extract person's name from greeting",
    output_key="extracted_params"
)
```

#### Execute Method

```python
def execute(self, user_input: str, ctx: ContextProtocol) -> ExecutionResult:
    """Execute the extractor node.

    Args:
        user_input: User input string to extract parameters from
        ctx: Execution context containing LLM service and other state

    Returns:
        ExecutionResult with extracted parameters and routing information
    """
```

### ActionNode

Executes specific actions and produces outputs.

```python
from intent_kit.nodes.action import ActionNode
```

#### Constructor

```python
ActionNode(
    name: str,
    action: Callable[..., Any],
    description: str = "",
    terminate_on_success: bool = True,
    param_key: str = "extracted_params",
    context_read: Optional[List[str]] = None,
    context_write: Optional[List[str]] = None,
    param_keys: Optional[List[str]] = None
)
```

**Parameters:**
- `name` (str): Node name
- `action` (Callable[..., Any]): Function to execute
- `description` (str, optional): Description of the action
- `terminate_on_success` (bool, optional): Whether to terminate after successful execution
- `param_key` (str, optional): Key in context to get parameters from
- `context_read` (List[str], optional): List of context keys to read and pass to the action function
- `context_write` (List[str], optional): List of context keys to write after execution
- `param_keys` (List[str], optional): List of parameter keys to check for parameters (defaults to [param_key])

**Example:**

```python
def greet_action(name: str, user_name: Optional[str] = None, **kwargs) -> str:
    # Check for user.name from context first, then name parameter
    context_user_name = kwargs.get('user.name')
    if context_user_name:
        return f"Hello {context_user_name}!"
    elif name:
        return f"Hello {name}!"
    else:
        return "Hello there!"

action = ActionNode(
    name="greet_action",
    action=greet_action,
    description="Greet the user by name",
    terminate_on_success=True,
    param_keys=["name_params", "extracted_params"],  # Look for name parameters
    context_read=["user.name"],  # Read user name from context
    context_write=["greeting_count"]  # Write greeting count to context
)
```

#### Execute Method

```python
def execute(self, user_input: str, ctx: ContextProtocol) -> ExecutionResult:
    """Execute the action node.

    Args:
        user_input: User input string (not used, parameters come from context)
        ctx: Execution context containing extracted parameters

    Returns:
        ExecutionResult with action results and termination flag
    """
```

### ClarificationNode

Handles unclear intent by asking for clarification.

```python
from intent_kit.nodes.clarification import ClarificationNode
```

#### Constructor

```python
ClarificationNode(
    name: str,
    clarification_message: Optional[str] = None,
    available_options: Optional[list[str]] = None,
    description: Optional[str] = None,
    llm_config: Optional[Dict[str, Any]] = None,
    custom_prompt: Optional[str] = None,
    context_read: Optional[list[str]] = None,
    context_write: Optional[list[str]] = None
)
```

**Parameters:**
- `name` (str): Node name
- `clarification_message` (str, optional): Custom message to ask for clarification
- `available_options` (list[str], optional): List of available options to suggest to the user
- `description` (str, optional): Description of the node's purpose
- `llm_config` (Dict[str, Any], optional): LLM configuration for generating contextual clarification messages
- `custom_prompt` (str, optional): Custom prompt for generating clarification messages
- `context_read` (list[str], optional): List of context keys to read before execution
- `context_write` (list[str], optional): List of context keys to write after execution

**Example:**

```python
clarification = ClarificationNode(
    name="clarification",
    clarification_message="I'm not sure what you'd like me to do. Please try saying hello!",
    available_options=["Say hello to someone"],
    description="Ask for clarification when intent is unclear"
)
```

## Context Management

### DefaultContext

Default context implementation for state management.

```python
from intent_kit.core.context import DefaultContext
```

#### Constructor

```python
DefaultContext()
```

#### Methods

##### `set(key, value)`
Set a value in the context.

**Parameters:**
- `key` (str): Context key
- `value` (Any): Value to store

**Example:**

```python
context = DefaultContext()
context.set("user_name", "Alice")
context.set("conversation_count", 5)
```

##### `get(key, default=None)`
Get a value from the context.

**Parameters:**
- `key` (str): Context key
- `default` (Any, optional): Default value if key not found

**Returns:**
- `Any`: Stored value or default

**Example:**

```python
user_name = context.get("user_name", "Unknown")
count = context.get("conversation_count", 0)
```

##### `has(key)`
Check if a key exists in the context.

**Parameters:**
- `key` (str): Context key

**Returns:**
- `bool`: True if key exists

**Example:**

```python
if context.has("user_name"):
    print(f"User: {context.get('user_name')}")
```

##### `clear()`
Clear all context data.

**Example:**

```python
context.clear()
```

### Context Read/Write Configuration

Nodes can specify which context keys they read from and write to, enabling declarative context management.

#### Context Read Configuration

Nodes can declare which context keys they need to read before execution:

```python
# Action node that reads user name from context
action_node = ActionNode(
    name="weather_action",
    action=get_weather,
    context_read=["user.name", "user.preferences"],  # Read these keys from context
    description="Get weather with user preferences"
)
```

#### Context Write Configuration

Nodes can declare which context keys they will write after execution:

```python
# Action node that writes to context
action_node = ActionNode(
    name="remember_name_action",
    action=remember_name,
    context_write=["user.name", "user.first_seen"],  # Write these keys to context
    description="Remember user's name"
)
```

#### Parameter Key Configuration

Action nodes can specify which parameter keys to check for parameters:

```python
# Action node with custom parameter keys
action_node = ActionNode(
    name="weather_action",
    action=get_weather,
    param_keys=["location_params", "extracted_params"],  # Check these keys for parameters
    context_read=["user.name"],
    description="Get weather for location"
)
```

#### Context-Aware Action Functions

Action functions can access context data through the `**kwargs` parameter:

```python
def get_weather(location: str, **kwargs) -> str:
    """Get weather with context awareness."""
    # Access context data
    user_name = kwargs.get('user.name')
    preferences = kwargs.get('user.preferences', {})

    if user_name:
        return f"Hey {user_name}! The weather in {location} is sunny."
    else:
        return f"The weather in {location} is sunny."
```

#### Context Persistence Example

```python
# Create a DAG with context persistence
builder = DAGBuilder()

# Add extractor that writes to specific key
builder.add_node(
    "extract_name",
    "extractor",
    param_schema={"name": str},
    output_key="name_params",  # Use specific key to avoid conflicts
    description="Extract name from greeting"
)

# Add action that reads and writes context
builder.add_node(
    "remember_name_action",
    "action",
    action=remember_name,
    param_keys=["name_params"],  # Read from specific parameter key
    context_write=["user.name", "user.first_seen"],  # Write to context
    description="Remember user's name"
)

# Add action that reads from context
builder.add_node(
    "weather_action",
    "action",
    action=get_weather,
    param_keys=["location_params"],  # Read from specific parameter key
    context_read=["user.name"],  # Read from context
    context_write=["weather.requests", "weather.last_location"],  # Write to context
    description="Get weather with user name"
)
```

## LLM Integration

### Supported Providers

Intent Kit supports multiple LLM providers:

#### OpenAI

```python
llm_config = {
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "your-openai-api-key",
    "temperature": 0.1
}
```

#### Anthropic

```python
llm_config = {
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "api_key": "your-openrouter-api-key",
    "temperature": 0.1
}
```

#### Google

```python
llm_config = {
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "api_key": "your-openrouter-api-key",
    "temperature": 0.1
}
```

#### Ollama

```python
llm_config = {
    "provider": "ollama",
    "model": "llama2",
    "base_url": "http://localhost:11434",
    "temperature": 0.1
}
```

### LLM Configuration Options

Common configuration options:

- `provider` (str): LLM provider name
- `model` (str): Model name
- `api_key` (str): API key for the provider
- `temperature` (float): Sampling temperature (0.0-2.0)
- `max_tokens` (int): Maximum tokens to generate
- `base_url` (str): Custom base URL (for Ollama)

## Configuration

### Environment Variables

Set these environment variables for API keys:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

### JSON Configuration Schema

Complete JSON configuration schema:

```json
{
  "nodes": {
    "node_id": {
      "type": "classifier|extractor|action|clarification",
      "description": "Node description",
      "llm_config": {
        "provider": "openai|anthropic|google|ollama",
        "model": "model-name",
        "api_key": "api-key",
        "temperature": 0.1
      },
      "param_schema": {
        "param_name": "param_type"
      },
      "output_key": "context_key",
      "action": "function_reference"
    }
  },
  "edges": [
    {
      "from": "source_node_id",
      "to": "target_node_id",
      "label": "edge_label"
    }
  ],
  "entrypoints": ["node_id1", "node_id2"],
      "default_llm_config": {
      "provider": "openrouter",
      "model": "google/gemma-2-9b-it"
    }
}
```

## Utilities

### run_dag

Convenience function for executing DAGs.

```python
from intent_kit import run_dag
```

#### Usage

```python
from intent_kit import run_dag
from intent_kit.core.context import DefaultContext

context = DefaultContext()
result, final_context = run_dag(dag, "Hello Alice", context)
print(result.data)  # → "Hello Alice!"
```

### DAGBuilder.from_json

Convenience method for creating DAGs from JSON configuration.

```python
from intent_kit import DAGBuilder

dag = DAGBuilder.from_json(dag_config)
```

### DAGBuilder.with_default_llm_config

Set default LLM configuration for all nodes in the DAG.

```python
from intent_kit import DAGBuilder

builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "api_key": "your-api-key"
})
```

## Error Handling

### Common Exceptions

#### DAGValidationError
Raised when DAG structure is invalid.

```python
from intent_kit.core.exceptions import DAGValidationError

try:
    dag.validate()
except DAGValidationError as e:
    print(f"DAG validation failed: {e}")
```

#### NodeExecutionError
Raised when node execution fails.

```python
from intent_kit.core.exceptions import NodeExecutionError

try:
    result = dag.execute("Hello Alice", context)
except NodeExecutionError as e:
    print(f"Node execution failed: {e}")
```

#### ContextError
Raised when context operations fail.

```python
from intent_kit.core.exceptions import ContextError

try:
    context.set("key", value)
except ContextError as e:
    print(f"Context operation failed: {e}")
```

## Best Practices

### DAG Design

1. **Start with a classifier** - Always begin with a classifier node
2. **Use extractors** - Extract parameters before actions
3. **Handle errors** - Add clarification nodes for error handling
4. **Keep it simple** - Start with simple workflows and add complexity

### Context Management

1. **Use meaningful keys** - Use descriptive context key names
2. **Validate data** - Always validate data before using it
3. **Clear when needed** - Clear context when starting new sessions
4. **Protect system keys** - Avoid using reserved system key names

### LLM Configuration

1. **Use appropriate models** - Choose models based on your needs
2. **Set temperature** - Use lower temperature for classification
3. **Handle rate limits** - Implement retry logic for API calls
4. **Monitor costs** - Track API usage and costs

### Testing

1. **Test each node** - Test individual nodes in isolation
2. **Test workflows** - Test complete workflows end-to-end
3. **Test edge cases** - Test error conditions and edge cases
4. **Use evaluation tools** - Use built-in evaluation framework

## Advanced API Reference

### DAG Validation

#### validate_dag_structure

Validate the structure of a DAG for correctness and completeness.

```python
from intent_kit.core.validation import validate_dag_structure

# Validate DAG structure
issues = validate_dag_structure(dag)

if issues:
    print("Validation issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("DAG structure is valid")
```

**Parameters:**
- `dag` (IntentDAG): The DAG to validate
- `producer_labels` (Dict[str, Set[str]], optional): Dictionary mapping node_id to set of labels it can produce

**Returns:**
- `List[str]`: List of validation issues (empty if all valid)

**Raises:**
- `CycleError`: If a cycle is detected in the DAG
- `ValueError`: If basic structure is invalid

**Validation Checks:**
- **ID Consistency** - All referenced node IDs exist
- **Entrypoint Validation** - Entrypoints exist and are reachable
- **Cycle Detection** - No cycles in the DAG structure
- **Reachability** - All nodes are reachable from entrypoints
- **Label Validation** - Edge labels match producer capabilities (if provided)

### Context Management

#### ContextProtocol

Protocol defining the interface for context implementations.

```python
from intent_kit.core.context import ContextProtocol

class CustomContext(ContextProtocol):
    def get(self, key: str, default: Any = None) -> Any:
        # Implementation
        pass

    def set(self, key: str, value: Any, modified_by: Optional[str] = None) -> None:
        # Implementation
        pass

    def has(self, key: str) -> bool:
        # Implementation
        pass

    def keys(self) -> Iterable[str]:
        # Implementation
        pass

    def snapshot(self) -> Mapping[str, Any]:
        # Implementation
        pass

    def apply_patch(self, patch: ContextPatch) -> None:
        # Implementation
        pass

    def merge_from(self, other: Mapping[str, Any]) -> None:
        # Implementation
        pass

    def fingerprint(self, include: Optional[Iterable[str]] = None) -> str:
        # Implementation
        pass

    @property
    def logger(self) -> LoggerLike:
        # Implementation
        pass

    def add_error(self, *, where: str, err: str, meta: Optional[Mapping[str, Any]] = None) -> None:
        # Implementation
        pass

    def track_operation(self, *, name: str, status: str, meta: Optional[Mapping[str, Any]] = None) -> None:
        # Implementation
        pass
```

#### ContextPatch

Patch contract applied by traversal after node execution.

```python
from intent_kit.core.context import ContextPatch, MergePolicyName

patch: ContextPatch = {
    "data": {
        "user.name": "Alice",
        "session.id": "session_123",
        "preferences.language": "en"
    },
    "policy": {
        "user.name": "last_write_wins",
        "preferences.language": "first_write_wins"
    },
    "provenance": "extract_user_info",
    "tags": {"affects_memo"}
}
```

**Fields:**
- `data` (Mapping[str, Any]): Dotted-key map of values to set/merge
- `policy` (Mapping[str, MergePolicyName], optional): Per-key merge policies
- `provenance` (str): Node id or source identifier for auditability
- `tags` (set[str], optional): Optional set of tags (e.g., {"affects_memo"})

#### MergePolicyName

Available merge policies for context patches.

```python
from intent_kit.core.context import MergePolicyName

# Available policies:
# - "last_write_wins" - Latest value overwrites previous
# - "first_write_wins" - First value is preserved
# - "append_list" - Values are appended to a list
# - "merge_dict" - Dictionaries are merged recursively
# - "reduce" - Custom reduction function is applied
```

#### LoggerLike

Protocol for logger interface compatible with intent_kit.utils.logger.Logger.

```python
from intent_kit.core.context import LoggerLike

class CustomLogger(LoggerLike):
    def info(self, message: str) -> None:
        # Implementation
        pass

    def warning(self, message: str) -> None:
        # Implementation
        pass

    def error(self, message: str) -> None:
        # Implementation
        pass

    def debug(self, message: str, colorize_message: bool = True) -> None:
        # Implementation
        pass

    def critical(self, message: str) -> None:
        # Implementation
        pass

    def trace(self, message: str) -> None:
        # Implementation
        pass
```

### Evaluation Framework

#### EvalResult

Results from evaluating a node against a dataset.

```python
from intent_kit.evals import EvalResult

# Create evaluation result
result = EvalResult(test_results, dataset_name="Intent Classification")

# Check overall performance
print(f"Accuracy: {result.accuracy():.1%}")
print(f"Passed: {result.passed_count()}/{result.total_count()}")

# Get failed cases
failed_cases = result.errors()

# Print summary
result.print_summary()
```

**Methods:**
- `all_passed() -> bool`: Check if all test cases passed
- `accuracy() -> float`: Calculate accuracy percentage
- `passed_count() -> int`: Count of passed test cases
- `failed_count() -> int`: Count of failed test cases
- `total_count() -> int`: Total number of test cases
- `errors() -> List[EvalTestResult]`: Get failed test cases
- `print_summary() -> None`: Print formatted summary

#### EvalTestCase

A single test case with input, expected output, and optional context.

```python
from intent_kit.evals import EvalTestCase

test_case = EvalTestCase(
    input="Hello, how are you?",
    expected="greet",
    context={"user_id": "test_user_1"}
)
```

**Fields:**
- `input` (str): The input text to test
- `expected` (Any): Expected output or result
- `context` (Optional[Dict[str, Any]]): Optional context data

#### Dataset

A dataset containing test cases for evaluating a node.

```python
from intent_kit.evals import Dataset

dataset = Dataset(
    name="Intent Classification Dataset",
    description="Test cases for intent classification",
    node_type="classifier",
    node_name="intent_classifier",
    test_cases=[test_case1, test_case2, ...]
)
```

**Fields:**
- `name` (str): Dataset name
- `description` (Optional[str]): Dataset description
- `node_type` (str): Type of node being tested
- `node_name` (str): Name of the node being tested
- `test_cases` (List[EvalTestCase]): List of test cases

#### evaluate_node

Evaluate a node against a dataset.

```python
from intent_kit.evals import evaluate_node, load_dataset

# Load dataset
dataset = load_dataset("path/to/dataset.yaml")

# Evaluate node
result = evaluate_node(dataset, node_instance)

# Print results
result.print_summary()
```

**Parameters:**
- `dataset` (Dataset): Dataset to evaluate against
- `node` (NodeProtocol): Node instance to evaluate

**Returns:**
- `EvalResult`: Evaluation results

#### load_dataset

Load a dataset from a YAML file.

```python
from intent_kit.evals import load_dataset

dataset = load_dataset("datasets/classifier_node_llm.yaml")
```

**Parameters:**
- `file_path` (str): Path to YAML dataset file

**Returns:**
- `Dataset`: Loaded dataset

### Performance Utilities

#### PerfUtil

Performance monitoring and timing utilities.

```python
from intent_kit.utils import PerfUtil

# Create performance monitor
perf = PerfUtil()

# Time an operation
with perf.timer("api_call"):
    result = api_client.call()

# Get timing statistics
stats = perf.get_stats()
print(f"Average API call time: {stats['api_call']['avg']:.2f}ms")

# Generate report
report = perf.generate_report()
```

**Methods:**
- `timer(name: str)`: Context manager for timing operations
- `get_stats() -> Dict[str, Dict]`: Get timing statistics
- `generate_report() -> str`: Generate formatted report
- `reset()`: Reset all timing data

#### ReportData

Data structure for performance reporting.

```python
from intent_kit.utils import ReportData

report_data = ReportData(
    total_tokens=1500,
    total_cost=0.0025,
    model_usage={"gpt-4": 1000, "gpt-3.5-turbo": 500},
    timing_data={"api_call": 1.2, "processing": 0.5}
)
```

**Fields:**
- `total_tokens` (int): Total tokens used
- `total_cost` (float): Total cost in USD
- `model_usage` (Dict[str, int]): Usage per model
- `timing_data` (Dict[str, float]): Timing data per operation

### Type Validation Utilities

#### TypeValidationError

Exception raised during type validation.

```python
from intent_kit.utils import TypeValidationError, validate_type

try:
    validate_type("age", 25, int)
except TypeValidationError as e:
    print(f"Type validation failed: {e}")
```

#### validate_type

Validate that a value matches the expected type.

```python
from intent_kit.utils import validate_type, TYPE_MAP

# Basic type validation
validate_type("name", "Alice", str)
validate_type("age", 25, int)
validate_type("active", True, bool)

# List validation
validate_type("tags", ["tag1", "tag2"], list)

# Dict validation
validate_type("config", {"key": "value"}, dict)

# Custom type validation
validate_type("user_id", "user_123", lambda x: x.startswith("user_"))
```

**Parameters:**
- `name` (str): Name of the field being validated
- `value` (Any): Value to validate
- `expected_type` (Union[type, Callable]): Expected type or validation function

**Raises:**
- `TypeValidationError`: If validation fails

#### TYPE_MAP

Predefined type mapping for common validations.

```python
from intent_kit.utils import TYPE_MAP

# Available types:
# - "int": Integer validation
# - "str": String validation
# - "bool": Boolean validation
# - "list": List validation
# - "dict": Dictionary validation
# - "float": Float validation
# - "email": Email validation
# - "url": URL validation
# - "uuid": UUID validation
```
