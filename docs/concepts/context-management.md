# Context Management

Intent Kit provides a sophisticated context management system that enables stateful execution, dependency tracking, and deterministic behavior across DAG traversals.

## Overview

The context system consists of several key components:

- **ContextProtocol** - Interface for context implementations
- **DefaultContext** - Standard context implementation
- **ContextPatch** - Mechanism for applying changes during traversal
- **Merge Policies** - Rules for combining context data
- **Fingerprinting** - Deterministic context identification for memoization

## Core Concepts

### Context Protocol

The `ContextProtocol` defines the interface that all context implementations must follow:

```python
from intent_kit.core.context import ContextProtocol

class ContextProtocol(Protocol):
    # Core key-value operations
    def get(self, key: str, default: Any = None) -> Any: ...
    def set(self, key: str, value: Any, modified_by: Optional[str] = None) -> None: ...
    def has(self, key: str) -> bool: ...
    def keys(self) -> Iterable[str]: ...

    # Patching and snapshots
    def snapshot(self) -> Mapping[str, Any]: ...
    def apply_patch(self, patch: ContextPatch) -> None: ...
    def merge_from(self, other: Mapping[str, Any]) -> None: ...

    # Deterministic fingerprinting
    def fingerprint(self, include: Optional[Iterable[str]] = None) -> str: ...

    # Telemetry and logging
    @property
    def logger(self) -> LoggerLike: ...

    # Error and operation tracking
    def add_error(self, *, where: str, err: str, meta: Optional[Mapping[str, Any]] = None) -> None: ...
    def track_operation(self, *, name: str, status: str, meta: Optional[Mapping[str, Any]] = None) -> None: ...
```

### Default Context

The `DefaultContext` provides a complete implementation of the context protocol:

```python
from intent_kit.core.context import DefaultContext

# Create a new context
context = DefaultContext()

# Set values
context.set("user.name", "Alice")
context.set("session.id", "session_123")
context.set("preferences.language", "en")

# Get values
name = context.get("user.name")  # "Alice"
language = context.get("preferences.language", "en")  # "en"

# Check existence
if context.has("user.name"):
    print("User name is set")

# Get all keys
all_keys = list(context.keys())  # ["user.name", "session.id", "preferences.language"]
```

## Context Patches

Context patches are the mechanism by which nodes can modify context during DAG traversal. They provide:

- **Atomic updates** - All changes are applied together
- **Audit trail** - Provenance tracking for changes
- **Merge policies** - Configurable rules for combining data
- **Memoization control** - Tags to control caching behavior

### Creating Patches

```python
from intent_kit.core.context import ContextPatch, MergePolicyName

# Basic patch
patch: ContextPatch = {
    "data": {
        "user.name": "Alice",
        "session.id": "session_123"
    },
    "provenance": "extract_user_info"
}

# Patch with merge policies
patch_with_policies: ContextPatch = {
    "data": {
        "user.name": "Alice",
        "preferences.language": "en",
        "conversation.history": ["Hello", "How are you?"]
    },
    "policy": {
        "user.name": "last_write_wins",
        "preferences.language": "first_write_wins",
        "conversation.history": "append_list"
    },
    "provenance": "greeting_node",
    "tags": {"affects_memo"}
}
```

### Applying Patches

```python
from intent_kit.core.context import DefaultContext, ContextPatch

context = DefaultContext()

# Create and apply patch
patch: ContextPatch = {
    "data": {"user.name": "Alice"},
    "provenance": "user_extraction"
}

context.apply_patch(patch)
print(context.get("user.name"))  # "Alice"
```

## Merge Policies

Merge policies define how context values are combined when conflicts occur:

### Available Policies

```python
from intent_kit.core.context import MergePolicyName

# last_write_wins - Latest value overwrites previous
policy1: MergePolicyName = "last_write_wins"

# first_write_wins - First value is preserved
policy2: MergePolicyName = "first_write_wins"

# append_list - Values are appended to a list
policy3: MergePolicyName = "append_list"

# merge_dict - Dictionaries are merged recursively
policy4: MergePolicyName = "merge_dict"

# reduce - Custom reduction function is applied
policy5: MergePolicyName = "reduce"
```

### Policy Examples

```python
from intent_kit.core.context import DefaultContext, ContextPatch

context = DefaultContext()

# Example 1: last_write_wins
context.set("user.name", "Bob")
patch1: ContextPatch = {
    "data": {"user.name": "Alice"},
    "policy": {"user.name": "last_write_wins"},
    "provenance": "update_user"
}
context.apply_patch(patch1)
print(context.get("user.name"))  # "Alice"

# Example 2: append_list
context.set("conversation.history", ["Hello"])
patch2: ContextPatch = {
    "data": {"conversation.history": ["How are you?"]},
    "policy": {"conversation.history": "append_list"},
    "provenance": "greeting"
}
context.apply_patch(patch2)
print(context.get("conversation.history"))  # ["Hello", "How are you?"]

# Example 3: merge_dict
context.set("user.preferences", {"language": "en", "theme": "dark"})
patch3: ContextPatch = {
    "data": {"user.preferences": {"theme": "light", "notifications": True}},
    "policy": {"user.preferences": "merge_dict"},
    "provenance": "update_preferences"
}
context.apply_patch(patch3)
print(context.get("user.preferences"))  # {"language": "en", "theme": "light", "notifications": True}
```

## Context Fingerprinting

Fingerprinting provides deterministic identification of context state for memoization:

```python
from intent_kit.core.context import DefaultContext

context = DefaultContext()

# Set some values
context.set("user.name", "Alice")
context.set("session.id", "session_123")

# Get fingerprint of entire context
full_fingerprint = context.fingerprint()
print(full_fingerprint)  # Deterministic hash

# Get fingerprint of specific keys only
user_fingerprint = context.fingerprint(include=["user.name"])
print(user_fingerprint)  # Hash based only on user.name
```

## Advanced Usage Patterns

### Custom Context Implementation

```python
from intent_kit.core.context import ContextProtocol, ContextPatch, LoggerLike
from typing import Any, Iterable, Mapping, Optional
import json

class DatabaseContext(ContextProtocol):
    def __init__(self, db_connection):
        self.db = db_connection
        self._cache = {}
        self._logger = CustomLogger()

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._cache:
            return self._cache[key]

        # Query database
        value = self.db.query(f"SELECT value FROM context WHERE key = ?", (key,))
        if value:
            self._cache[key] = value
            return value
        return default

    def set(self, key: str, value: Any, modified_by: Optional[str] = None) -> None:
        self._cache[key] = value
        self.db.execute(
            "INSERT OR REPLACE INTO context (key, value, modified_by) VALUES (?, ?, ?)",
            (key, json.dumps(value), modified_by)
        )

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def keys(self) -> Iterable[str]:
        return [row[0] for row in self.db.query("SELECT key FROM context")]

    def snapshot(self) -> Mapping[str, Any]:
        return {key: self.get(key) for key in self.keys()}

    def apply_patch(self, patch: ContextPatch) -> None:
        for key, value in patch["data"].items():
            self.set(key, value, patch["provenance"])

    def merge_from(self, other: Mapping[str, Any]) -> None:
        for key, value in other.items():
            self.set(key, value)

    def fingerprint(self, include: Optional[Iterable[str]] = None) -> str:
        if include:
            data = {key: self.get(key) for key in include if self.has(key)}
        else:
            data = self.snapshot()
        return json.dumps(data, sort_keys=True)

    @property
    def logger(self) -> LoggerLike:
        return self._logger

    def add_error(self, *, where: str, err: str, meta: Optional[Mapping[str, Any]] = None) -> None:
        self.logger.error(f"Error in {where}: {err}")

    def track_operation(self, *, name: str, status: str, meta: Optional[Mapping[str, Any]] = None) -> None:
        self.logger.info(f"Operation {name}: {status}")

class CustomLogger(LoggerLike):
    def info(self, message: str) -> None:
        print(f"[INFO] {message}")

    def warning(self, message: str) -> None:
        print(f"[WARN] {message}")

    def error(self, message: str) -> None:
        print(f"[ERROR] {message}")

    def debug(self, message: str, colorize_message: bool = True) -> None:
        print(f"[DEBUG] {message}")

    def critical(self, message: str) -> None:
        print(f"[CRITICAL] {message}")

    def trace(self, message: str) -> None:
        print(f"[TRACE] {message}")
```

### Context Adapters

Intent Kit provides context adapters for common data structures:

```python
from intent_kit.core.context import DictBackedContext

# Create context backed by a dictionary
data = {"user.name": "Alice", "session.id": "session_123"}
context = DictBackedContext(data)

# Context operations work normally
context.set("preferences.language", "en")
print(context.get("user.name"))  # "Alice"
```

### Custom Nodes with Context Access

When creating custom nodes, you can access the context directly in the `execute` method:

```python
from intent_kit.core.types import NodeProtocol, ExecutionResult
from intent_kit.core.context import ContextProtocol

class CustomMemoryNode(NodeProtocol):
    def __init__(self, name: str):
        self.name = name

    def execute(self, user_input: str, ctx: ContextProtocol) -> ExecutionResult:
        """Execute with direct context access."""

        # Access context directly
        user_name = ctx.get("user.name")
        conversation_count = ctx.get("conversation.count", 0)

        # Update context
        ctx.set("conversation.count", conversation_count + 1)

        # Create response using context
        if user_name:
            response = f"Hello {user_name}! This is conversation #{conversation_count + 1}"
        else:
            response = f"Hello! This is conversation #{conversation_count + 1}"

        return ExecutionResult(
            data=response,
            next_edges=["success"],
            terminate=False,
            context_patch={
                "last_greeting": response,
                "greeting_count": conversation_count + 1
            }
        )

# Usage in DAG
builder = DAGBuilder()
builder.add_node("memory_greeter", CustomMemoryNode("memory_greeter"))
```

### Action Functions with Context

For action nodes, you can create functions that receive context through the node's execute method:

```python
from intent_kit.core.context import ContextProtocol

def remember_user_action(name: str, ctx: ContextProtocol) -> str:
    """Action function that can access context."""
    # Store in context
    ctx.set("user.name", name)
    ctx.set("user.first_seen", time.time())

    return f"Nice to meet you, {name}! I'll remember you."

def weather_with_context_action(location: str, ctx: ContextProtocol) -> str:
    """Action function that uses context for personalization."""
    user_name = ctx.get("user.name", "there")
    weather_count = ctx.get("weather.requests", 0) + 1

    # Update context
    ctx.set("weather.requests", weather_count)
    ctx.set("weather.last_location", location)

    return f"Hey {user_name}! The weather in {location} is sunny. (Request #{weather_count})"

## Current Limitations and Workarounds

### Action Function Context Access

In the current implementation, action functions receive parameters but not the context directly:

```python
def weather_action(location: str, **kwargs) -> str:
    """Action function - receives parameters but not context."""
    # This function cannot access context directly
    return f"The weather in {location} is sunny."
```

The context is managed by the traversal engine and accessed through context patches returned by the node's execute method.

### Context Persistence Challenges

The current system has some limitations for true context persistence:

1. **Extractor Overwriting**: Each extractor node overwrites the `extracted_params` key
2. **Action Function Isolation**: Action functions don't have direct context access
3. **Context Patch Management**: Data must be explicitly stored via context patches

### Workarounds for Context Persistence

To achieve true context persistence, you can:

1. **Use Custom Nodes**: Create custom node implementations that have direct context access
2. **Leverage Context Patches**: Use context patches to store persistent data
3. **Use Different Context Keys**: Store persistent data in different context keys than `extracted_params`

### Example: Custom Node with Context Access

```python
from intent_kit.core.types import NodeProtocol, ExecutionResult
from intent_kit.core.context import ContextProtocol

class PersistentMemoryNode(NodeProtocol):
    def __init__(self, name: str):
        self.name = name

    def execute(self, user_input: str, ctx: ContextProtocol) -> ExecutionResult:
        """Execute with direct context access."""

        # Get current parameters
        params = ctx.get("extracted_params", {})

        # Store name persistently if extracted
        if "name" in params:
            ctx.set("user.name", params["name"])
            ctx.set("user.first_seen", time.time())

        # Get remembered name for response
        user_name = ctx.get("user.name", "there")

        result = f"Hello {user_name}! Nice to meet you."

        return ExecutionResult(
            data=result,
            next_edges=["success"],
            terminate=True,
            context_patch={
                "action_result": result,
                "user.name": params.get("name"),  # Store in context patch
                "user.first_seen": time.time()
            }
        )
```

**Note**: Custom nodes require modifications to the traversal system to be supported.
```

### Error Handling and Tracking

```python
from intent_kit.core.context import DefaultContext

context = DefaultContext()

# Track operations
context.track_operation(name="api_call", status="started", meta={"endpoint": "/users"})

try:
    # Simulate API call
    result = api_client.get_user("alice")
    context.set("user.data", result)
    context.track_operation(name="api_call", status="completed")
except Exception as e:
    # Track errors
    context.add_error(
        where="api_call",
        err=str(e),
        meta={"endpoint": "/users", "user_id": "alice"}
    )
    context.track_operation(name="api_call", status="failed")
```

## Best Practices

### 1. Use Descriptive Keys

```python
# Good - descriptive and hierarchical
context.set("user.profile.name", "Alice")
context.set("user.profile.email", "alice@example.com")
context.set("session.current.id", "session_123")

# Avoid - flat and unclear
context.set("name", "Alice")
context.set("email", "alice@example.com")
context.set("session", "session_123")
```

### 2. Leverage Merge Policies

```python
# Use appropriate policies for different data types
patch: ContextPatch = {
    "data": {
        "user.name": "Alice",  # Use last_write_wins for single values
        "conversation.history": ["New message"],  # Use append_list for lists
        "user.preferences": {"theme": "dark"}  # Use merge_dict for objects
    },
    "policy": {
        "user.name": "last_write_wins",
        "conversation.history": "append_list",
        "user.preferences": "merge_dict"
    },
    "provenance": "user_interaction"
}
```

### 3. Control Memoization

```python
# Use tags to control memoization behavior
patch: ContextPatch = {
    "data": {"user.name": "Alice"},
    "provenance": "user_extraction",
    "tags": {"affects_memo"}  # This change affects memoization
}

# Changes without this tag won't affect memoization
patch2: ContextPatch = {
    "data": {"debug.enabled": True},
    "provenance": "debug_setting"
    # No tags - won't affect memoization
}
```

### 4. Track Provenance

```python
# Always include provenance for auditability
context.set("user.name", "Alice", modified_by="user_extraction_node")
context.set("session.id", "session_123", modified_by="session_manager")

# Or use patches with provenance
patch: ContextPatch = {
    "data": {"user.name": "Alice"},
    "provenance": "user_extraction_node"
}
```

### 5. Use Fingerprinting for Caching

```python
# Create cache key based on relevant context
cache_key = context.fingerprint(include=["user.name", "session.id"])

# Use in memoization
if cache_key in memo_cache:
    return memo_cache[cache_key]
```

## Integration with DAG Traversal

The context system integrates seamlessly with DAG traversal:

```python
from intent_kit import DAGBuilder, DefaultContext

# Create DAG with context-aware nodes
builder = DAGBuilder()
builder.add_node("extract_user", "extractor", ...)
builder.add_node("greet_user", "action", ...)

dag = builder.build()

# Execute with context
context = DefaultContext()
context.set("session.id", "session_123")

result, final_context = dag.execute("Hello Alice", context)

# Context is automatically updated during traversal
print(final_context.get("user.name"))  # "Alice"
print(final_context.get("greeting.count"))  # 1
```

## Performance Considerations

### 1. Efficient Fingerprinting

```python
# Only fingerprint relevant keys for memoization
relevant_keys = ["user.name", "session.id", "preferences.language"]
fingerprint = context.fingerprint(include=relevant_keys)
```

### 2. Batch Operations

```python
# Use patches for multiple changes
patch: ContextPatch = {
    "data": {
        "user.name": "Alice",
        "user.email": "alice@example.com",
        "user.preferences": {"language": "en"}
    },
    "provenance": "user_registration"
}
context.apply_patch(patch)
```

### 3. Caching Strategies

```python
# Cache frequently accessed values
class CachedContext(DefaultContext):
    def __init__(self):
        super().__init__()
        self._cache = {}

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._cache:
            return self._cache[key]

        value = super().get(key, default)
        self._cache[key] = value
        return value
```

## Context Read/Write Configuration

Intent Kit provides a declarative approach to context management through node-level configuration. Nodes can specify which context keys they read from and write to, enabling clear data flow and preventing unintended context modifications.

### Node-Level Context Declaration

All node types support context read/write configuration:

```python
from intent_kit.nodes import ActionNode, ClassifierNode, ExtractorNode

# Action node with context read/write
action_node = ActionNode(
    name="weather_action",
    action=get_weather,
    context_read=["user.name", "user.preferences"],  # Read these keys
    context_write=["weather.requests", "weather.last_location"],  # Write these keys
    description="Get weather with user context"
)

# Classifier node with context awareness
classifier_node = ClassifierNode(
    name="intent_classifier",
    output_labels=["greet", "weather", "help"],
    context_read=["user.name", "conversation.history"],  # Read context for classification
    context_write=["intent.confidence"],  # Write classification confidence
    description="Classify intent with user context"
)

# Extractor node with context persistence
extractor_node = ExtractorNode(
    name="name_extractor",
    param_schema={"name": str},
    context_read=["conversation.context"],  # Read conversation context
    context_write=["extraction.confidence"],  # Write extraction confidence
    description="Extract name with context"
)
```

### Parameter Key Configuration

Action nodes can specify which parameter keys to check for parameters, enabling flexible parameter sourcing:

```python
# Action node with custom parameter keys
action_node = ActionNode(
    name="weather_action",
    action=get_weather,
    param_keys=["location_params", "extracted_params"],  # Check these keys for parameters
    context_read=["user.name"],  # Read user name from context
    context_write=["weather.requests"],  # Write request count
    description="Get weather for location"
)
```

### Context-Aware Action Functions

Action functions receive context data through the `**kwargs` parameter:

```python
def get_weather(location: str, **kwargs) -> str:
    """Get weather with context awareness."""
    # Access context data
    user_name = kwargs.get('user.name')
    preferences = kwargs.get('user.preferences', {})
    temperature_unit = preferences.get('temperature_unit', 'fahrenheit')

    if user_name:
        return f"Hey {user_name}! The weather in {location} is sunny and 72°{temperature_unit[0].upper()}."
    else:
        return f"The weather in {location} is sunny and 72°{temperature_unit[0].upper()}."

def remember_name(name: str, **kwargs) -> str:
    """Remember user name with context."""
    # Context data is automatically available
    user_name = kwargs.get('user.name')
    if user_name:
        return f"Nice to see you again, {user_name}!"
    else:
        return f"Nice to meet you, {name}! I'll remember your name."
```

### Context Persistence Patterns

#### 1. User Information Persistence

```python
# Extract and store user information
builder.add_node(
    "extract_name",
    "extractor",
    param_schema={"name": str},
    output_key="name_params",  # Use specific key to avoid conflicts
    context_write=["user.name", "user.first_seen"],  # Write to persistent context
    description="Extract and store user name"
)

# Use stored user information
builder.add_node(
    "greet_user",
    "action",
    action=greet_user,
    context_read=["user.name"],  # Read stored user name
    context_write=["greeting.count"],  # Track greeting count
    description="Greet user with stored name"
)
```

#### 2. Conversation State Tracking

```python
# Track conversation state
builder.add_node(
    "classify_intent",
    "classifier",
    output_labels=["greet", "weather", "help"],
    context_read=["conversation.turn_count", "user.name"],  # Read conversation state
    context_write=["intent.confidence", "conversation.turn_count"],  # Update state
    description="Classify intent with conversation context"
)
```

#### 3. Request Counting and Analytics

```python
# Track request patterns
builder.add_node(
    "weather_action",
    "action",
    action=get_weather,
    context_read=["user.name", "weather.requests"],  # Read user and request count
    context_write=["weather.requests", "weather.last_location", "weather.last_request_time"],  # Update analytics
    description="Get weather with analytics tracking"
)
```

### Benefits of Declarative Context Management

1. **Clear Data Flow**: Explicit declaration of what data nodes read and write
2. **Prevent Conflicts**: Avoid accidental overwrites of important context data
3. **Audit Trail**: Clear tracking of context modifications
4. **Performance**: Optimized context access patterns
5. **Maintainability**: Self-documenting context usage

### Best Practices

1. **Use Descriptive Key Names**: Use hierarchical keys like `user.name`, `weather.requests`
2. **Minimize Context Reads**: Only read the context keys you actually need
3. **Be Specific with Writes**: Only write to context keys that are part of your node's responsibility
4. **Use Parameter Keys**: Use specific parameter keys to avoid conflicts between extractors
5. **Document Context Usage**: Include context read/write in node descriptions

The context management system provides a robust foundation for building stateful, auditable, and performant intent classification systems with clear data flow and declarative context management.
