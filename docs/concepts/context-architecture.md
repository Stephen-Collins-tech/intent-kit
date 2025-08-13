# Context Architecture

## Overview

Intent Kit provides a sophisticated context management system that enables stateful, multi-turn conversations and robust execution tracking. The context system is designed around a protocol-based architecture that supports flexible implementations while maintaining type safety and audit capabilities.

## Core Architecture

### ContextProtocol

The foundation of the context system is the `ContextProtocol`, which defines the interface that all context implementations must follow:

```python
from typing import Protocol, runtime_checkable, Any, Optional

@runtime_checkable
class ContextProtocol(Protocol):
    """Protocol for context implementations."""

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context."""
        ...

    def set(self, key: str, value: Any, modified_by: Optional[str] = None) -> None:
        """Set a value in context."""
        ...

    def has(self, key: str) -> bool:
        """Check if a key exists in context."""
        ...

    def delete(self, key: str) -> None:
        """Delete a key from context."""
        ...

    def keys(self) -> list[str]:
        """Get all keys in context."""
        ...

    def clear(self) -> None:
        """Clear all data from context."""
        ...

    def snapshot(self) -> dict[str, Any]:
        """Create an immutable snapshot of the context."""
        ...

    def apply_patch(self, patch: dict[str, Any]) -> None:
        """Apply a context patch."""
        ...
```

### DefaultContext

The primary context implementation is `DefaultContext`, which provides a reference implementation with deterministic merge policies, memoization, and comprehensive audit trails.

#### Key Features

- **Type Safety**: Validates and coerces data types
- **Audit Trails**: Tracks all modifications with metadata
- **Namespace Protection**: Protects system keys from conflicts
- **Deterministic Merging**: Predictable behavior for concurrent updates
- **Memoization**: Caches expensive operations
- **Error Tracking**: Comprehensive error logging and recovery

#### Data Structures

```python
@dataclass
class ContextPatch:
    """Represents a set of context changes."""
    data: dict[str, Any]
    provenance: Optional[str] = None
    tags: Optional[list[str]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContextOperation:
    """Tracks a context operation for audit purposes."""
    timestamp: datetime
    operation: str  # 'get', 'set', 'delete', 'clear'
    key: Optional[str]
    value: Any
    modified_by: Optional[str]
    success: bool
    error_message: Optional[str] = None
```

## Context Implementation

### DefaultContext Usage

#### Basic Operations

```python
from intent_kit.core.context import DefaultContext

# Create a new context
context = DefaultContext()

# Set values with metadata
context.set("user.name", "Alice", modified_by="greet_action")
context.set("user.preferences", {"theme": "dark", "language": "en"})

# Get values with defaults
name = context.get("user.name", "Unknown")
theme = context.get("user.preferences.theme", "light")

# Check existence
if context.has("user.name"):
    print("User name is set")

# Delete values
context.delete("temporary_data")

# Get all keys
all_keys = context.keys()

# Create snapshot
snapshot = context.snapshot()
```

#### Context Patches

```python
# Apply a patch of changes
patch = {
    "user.name": "Bob",
    "user.age": 30,
    "session.start_time": datetime.utcnow()
}

context.apply_patch(patch, provenance="user_registration")

# Create patches with metadata
from intent_kit.core.context import ContextPatch

patch = ContextPatch(
    data={"user.preferences": {"theme": "light"}},
    provenance="preference_update",
    tags=["user", "preferences"]
)

context.apply_patch(patch.data)
```

#### Error Handling

```python
# Context operations are safe and logged
try:
    context.set("invalid.key", "value")
except Exception as e:
    print(f"Error setting context: {e}")

# Check for errors
if context.has_errors():
    errors = context.get_errors()
    for error in errors:
        print(f"Error: {error}")
```

### Context in DAG Execution

#### Integration with DAGs

```python
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

# Create DAG
builder = DAGBuilder()
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "weather"],
                 description="Main classifier")
# ... add more nodes
dag = builder.build()

# Execute with context
context = DefaultContext()
result = run_dag(dag, "Hello Alice", context)

# Context persists across executions
result2 = run_dag(dag, "What's the weather?", context)
# Context still contains data from previous execution
```

#### Action Node Context Integration

```python
def greet(name: str, context=None) -> str:
    """Greet user and track greeting count."""
    if context:
        count = context.get("greet_count", 0) + 1
        context.set("greet_count", count, modified_by="greet_action")
        return f"Hello {name}! (greeting #{count})"
    return f"Hello {name}!"

# The action automatically receives context from the DAG execution
```

## Advanced Context Features

### Merge Policies

The context system supports different merge policies for handling conflicts:

```python
from intent_kit.core.context.policies import (
    last_write_wins,
    first_write_wins,
    append_list,
    merge_dict
)

# Policies can be applied when merging contexts
context1 = DefaultContext()
context1.set("data", {"a": 1, "b": 2})

context2 = DefaultContext()
context2.set("data", {"b": 3, "c": 4})

# Merge with different policies
merged = context1.snapshot()
merged["data"] = merge_dict(context1.get("data"), context2.get("data"))
```

### Fingerprinting

Generate deterministic fingerprints for context state:

```python
from intent_kit.core.context.fingerprint import generate_fingerprint

# Generate fingerprint from selected keys
fingerprint = generate_fingerprint(context.snapshot(),
                                 keys=["user.name", "user.preferences"])

# Use for caching or change detection
if fingerprint != last_fingerprint:
    # Context has changed
    update_cache(context.snapshot())
```

### Protected Namespaces

The context system protects certain namespaces:

```python
# System keys are protected
context.set("private.system_key", "value")  # Protected
context.set("tmp.temporary_data", "value")  # Protected

# User keys are allowed
context.set("user.data", "value")  # Allowed
context.set("app.config", "value")  # Allowed
```

## Context Patterns

### Stateful Conversations

```python
# Multi-turn conversation with context persistence
context = DefaultContext()

# Turn 1: User introduces themselves
result1 = run_dag(dag, "Hi, my name is Alice", context)
# Context now contains: user.name = "Alice"

# Turn 2: User asks about weather (bot remembers name)
result2 = run_dag(dag, "What's the weather like?", context)
# Action can access: context.get("user.name") = "Alice"
```

### Context Inheritance

```python
# Create context with initial data
initial_data = {
    "user.name": "Alice",
    "user.preferences": {"theme": "dark"}
}

context = DefaultContext()
context.apply_patch(initial_data, provenance="initialization")

# Context now has initial state
print(context.get("user.name"))  # "Alice"
```

### Context Validation

```python
def validate_user_context(context):
    """Validate required context keys."""
    required_keys = ["user.name", "user.id"]
    missing_keys = [key for key in required_keys if not context.has(key)]

    if missing_keys:
        raise ValueError(f"Missing required context keys: {missing_keys}")

    return True

# Use in actions
def process_user_request(context):
    validate_user_context(context)
    # Process request with validated context
```

## Performance Considerations

### Memory Management

```python
# Context grows with usage
context = DefaultContext()

# Monitor context size
print(f"Context keys: {len(context.keys())}")

# Clear when no longer needed
context.clear()

# Use snapshots for read-only access
snapshot = context.snapshot()  # Immutable copy
```

### Caching Strategies

```python
# Cache expensive computations
def expensive_calculation(context):
    cache_key = "expensive_result"

    if context.has(cache_key):
        return context.get(cache_key)

    # Perform expensive calculation
    result = perform_expensive_calculation()

    # Cache result
    context.set(cache_key, result, modified_by="expensive_calculation")
    return result
```

## Best Practices

### 1. **Context Design**

- Use descriptive key names with dot notation
- Group related data under common prefixes
- Document context key schemas
- Use consistent naming conventions

### 2. **State Management**

- Keep context focused on conversation state
- Avoid storing large objects in context
- Use context patches for bulk updates
- Clear temporary data when no longer needed

### 3. **Error Handling**

- Always check for context availability in actions
- Use default values for optional context keys
- Validate context state before critical operations
- Log context operations for debugging

### 4. **Performance**

- Use snapshots for read-only access
- Monitor context size in long-running applications
- Cache expensive computations in context
- Clear context periodically in batch processing

### 5. **Security**

- Never store sensitive data in context without encryption
- Use protected namespaces for system data
- Validate context data before use
- Implement context expiration for sensitive sessions

## Integration Examples

### Web Application Integration

```python
from flask import Flask, request, session
from intent_kit.core.context import DefaultContext

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']

    # Get or create context for user session
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

    # Create context with session data
    context = DefaultContext()
    context.set("session.id", session_id)
    context.set("user.id", session.get('user_id'))

    # Execute DAG
    result = run_dag(dag, user_input, context)

    # Store context state for next request
    session['context_state'] = context.snapshot()

    return {'response': result.data}
```

### Database Integration

```python
import json
from intent_kit.core.context import DefaultContext

def save_context_to_db(context, user_id):
    """Save context state to database."""
    context_data = context.snapshot()

    # Store in database
    db.execute("""
        INSERT INTO user_contexts (user_id, context_data, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
        context_data = ?, updated_at = ?
    """, (user_id, json.dumps(context_data), datetime.utcnow(),
          json.dumps(context_data), datetime.utcnow()))

def load_context_from_db(user_id):
    """Load context state from database."""
    result = db.execute("""
        SELECT context_data FROM user_contexts
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    if result:
        context = DefaultContext()
        context_data = json.loads(result[0])
        context.apply_patch(context_data, provenance="database_load")
        return context

    return DefaultContext()
```

## Troubleshooting

### Common Issues

1. **Context Not Persisting**
   - Ensure context is passed to `run_dag()`
   - Check that actions accept context parameter
   - Verify context is not being recreated

2. **Type Errors**
   - Use type hints in action functions
   - Provide default values for optional context keys
   - Validate context data before use

3. **Memory Issues**
   - Monitor context size with `len(context.keys())`
   - Clear temporary data with `context.delete()`
   - Use snapshots for read-only access

4. **Performance Problems**
   - Cache expensive computations in context
   - Use context patches for bulk updates
   - Monitor context operation frequency

## Future Enhancements

### Planned Features

- **Async Context**: Support for async/await patterns
- **Persistent Context**: Database-backed context storage
- **Distributed Context**: Multi-process context sharing
- **Context Validation**: Schema-based context validation
- **Context Migration**: Version-aware context upgrades

### Extension Points

The context system is designed for extensibility:

- Implement `ContextProtocol` for custom context types
- Extend `DefaultContext` for specialized use cases
- Create custom merge policies for domain-specific logic
- Add context middleware for cross-cutting concerns

## Conclusion

The context architecture in Intent Kit provides a robust foundation for stateful AI applications. By following the patterns and best practices outlined in this guide, you can:

- **Build conversational AI** with persistent memory
- **Create reliable applications** with comprehensive state management
- **Scale applications** with efficient context handling
- **Debug effectively** with detailed audit trails

The protocol-based design ensures flexibility while the `DefaultContext` implementation provides a solid foundation for most use cases. The context system integrates seamlessly with the DAG execution engine and supports the complex state management requirements of modern AI applications.
