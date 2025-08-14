# Clarification Nodes

Clarification nodes handle ambiguous or incomplete user input by asking for additional information. They enable multi-turn conversations and improve user experience by gathering missing details.

## Overview

Clarification nodes:
- Detect when user input is unclear or incomplete
- Present structured options for user selection
- Support multi-turn conversation flows
- Provide context-aware clarification messages
- Handle user responses and route appropriately

## Basic Usage

```python
from intent_kit import DAGBuilder

# Create a clarification node
builder.add_node("booking_clarification", "clarification",
                 clarification_message="I need more information to help you with your booking.",
                 available_options=[
                     "Make a restaurant reservation",
                     "Book a flight",
                     "Reserve a hotel room"
                 ],
                 output_key="clarification_response")
```

## Configuration Options

### Clarification Message

The message presented to the user when clarification is needed:

```python
builder.add_node("clarification", "clarification",
                 clarification_message="""
                 I'm not sure what type of booking you'd like to make.
                 Please select from the options below:
                 """,
                 available_options=["Restaurant", "Flight", "Hotel"])
```

### Available Options

Provide structured options for user selection:

```python
# Simple text options
available_options = [
    "Book a restaurant table",
    "Reserve a flight",
    "Book a hotel room"
]

# Or with more descriptive options
available_options = [
    "🍽️ Restaurant - Make a dining reservation",
    "✈️ Flight - Book air travel",
    "🏨 Hotel - Reserve accommodation"
]
```

### Output Key

Specify where the user's response should be stored:

```python
builder.add_node("clarification", "clarification",
                 clarification_message="What would you like to do?",
                 available_options=["Option A", "Option B"],
                 output_key="user_selection")  # Response stored in context under this key
```

## Advanced Configuration

### Custom Response Handling

```python
builder.add_node("smart_clarification", "clarification",
                 clarification_message="Please specify your preference:",
                 available_options=["Budget", "Luxury", "Mid-range"],
                 output_key="preference",
                 custom_response_handler=lambda response: {
                     "preference": response.lower(),
                     "confidence": 0.9
                 })
```

### Context-Aware Messages

```python
# Use context to personalize clarification messages
def get_clarification_message(context):
    user_name = context.get("user_name", "there")
    return f"Hi {user_name}, I need a bit more information to help you."

builder.add_node("personalized_clarification", "clarification",
                 clarification_message=get_clarification_message,
                 available_options=["Option 1", "Option 2"])
```

## Multi-Turn Conversations

Clarification nodes enable sophisticated multi-turn conversations:

```python
# First clarification - determine intent
builder.add_node("intent_clarification", "clarification",
                 clarification_message="What would you like to do?",
                 available_options=["Book travel", "Make reservation", "Get information"],
                 output_key="intent")

# Second clarification - based on first response
builder.add_node("travel_clarification", "clarification",
                 clarification_message="What type of travel?",
                 available_options=["Flight", "Train", "Bus", "Car rental"],
                 output_key="travel_type")

# Connect the flow
builder.add_edge("intent_clarification", "travel_clarification", "Book travel")
```

## Integration Patterns

### With Classifier Nodes

```python
# Classifier routes to clarification when intent is unclear
builder.add_edge("intent_classifier", "clarification", "unclear_intent")
builder.add_edge("clarification", "intent_classifier", "clarified")
```

### With Extractor Nodes

```python
# Clarification can provide missing parameters for extraction
builder.add_edge("extractor", "clarification", "missing_params")
builder.add_edge("clarification", "extractor", "params_provided")
```

### With Action Nodes

```python
# Clarification can route to different actions based on user choice
builder.add_edge("clarification", "restaurant_action", "restaurant_selected")
builder.add_edge("clarification", "flight_action", "flight_selected")
```

## Error Handling

### Invalid Responses

```python
# Handle cases where user provides unexpected input
builder.add_node("robust_clarification", "clarification",
                 clarification_message="Please select from the options:",
                 available_options=["A", "B", "C"],
                 fallback_message="I didn't understand. Please choose A, B, or C.")
```

### Timeout Handling

```python
# Handle cases where user doesn't respond
builder.add_node("timeout_clarification", "clarification",
                 clarification_message="Please respond within 30 seconds:",
                 available_options=["Yes", "No"],
                 timeout_seconds=30,
                 timeout_message="No response received. Please try again.")
```

## Best Practices

### 1. Clear and Specific Options

```python
# Good: Clear, specific options
available_options = [
    "Book a table for 2 people",
    "Book a table for 4+ people",
    "Check restaurant availability",
    "Cancel existing reservation"
]

# Avoid: Vague options
available_options = [
    "Book",
    "Check",
    "Cancel"
]
```

### 2. Progressive Disclosure

```python
# Start with broad categories, then get specific
# First clarification
builder.add_node("category_clarification", "clarification",
                 clarification_message="What type of service do you need?",
                 available_options=["Travel", "Dining", "Entertainment"])

# Second clarification (after travel selected)
builder.add_node("travel_type_clarification", "clarification",
                 clarification_message="What type of travel?",
                 available_options=["Flight", "Hotel", "Car rental", "Package deal"])
```

### 3. Context Preservation

```python
# Preserve context across clarification turns
def handle_clarification_response(context, response):
    # Store the clarification response
    context.set("clarification_response", response)

    # Preserve original user input
    original_input = context.get("original_input")
    context.set("full_conversation", f"{original_input} -> {response}")

    return response
```

### 4. Graceful Degradation

```python
# Provide fallback options when clarification fails
builder.add_node("fallback_clarification", "clarification",
                 clarification_message="I'm having trouble understanding. Please try again:",
                 available_options=["Option A", "Option B", "Start over"],
                 max_attempts=3)
```

## Examples

### Restaurant Booking Flow

```python
# Determine booking type
builder.add_node("booking_type_clarification", "clarification",
                 clarification_message="What type of booking would you like to make?",
                 available_options=[
                     "Dinner reservation",
                     "Lunch reservation",
                     "Private event",
                     "Catering order"
                 ],
                 output_key="booking_type")

# Determine party size
builder.add_node("party_size_clarification", "clarification",
                 clarification_message="How many people will be in your party?",
                 available_options=[
                     "1-2 people",
                     "3-4 people",
                     "5-8 people",
                     "9+ people"
                 ],
                 output_key="party_size")
```

### Travel Planning Flow

```python
# Determine travel purpose
builder.add_node("travel_purpose_clarification", "clarification",
                 clarification_message="What's the purpose of your trip?",
                 available_options=[
                     "Business travel",
                     "Vacation/leisure",
                     "Family visit",
                     "Other"
                 ],
                 output_key="travel_purpose")

# Determine budget range
builder.add_node("budget_clarification", "clarification",
                 clarification_message="What's your budget range?",
                 available_options=[
                     "Budget-friendly ($)",
                     "Mid-range ($$)",
                     "Luxury ($$$)"
                 ],
                 output_key="budget_range")
```

### Customer Support Flow

```python
# Determine issue category
builder.add_node("issue_category_clarification", "clarification",
                 clarification_message="What type of issue are you experiencing?",
                 available_options=[
                     "Technical problem",
                     "Billing question",
                     "Account access",
                     "General inquiry"
                 ],
                 output_key="issue_category")

# Determine urgency
builder.add_node("urgency_clarification", "clarification",
                 clarification_message="How urgent is this issue?",
                 available_options=[
                     "Critical - Service completely down",
                     "High - Major functionality affected",
                     "Medium - Minor inconvenience",
                     "Low - General question"
                 ],
                 output_key="urgency_level")
```

## Performance Considerations

### Response Time

```python
# Set appropriate timeouts for different contexts
builder.add_node("quick_clarification", "clarification",
                 clarification_message="Quick question:",
                 available_options=["Yes", "No"],
                 timeout_seconds=10)  # Short timeout for simple questions

builder.add_node("detailed_clarification", "clarification",
                 clarification_message="Please provide detailed information:",
                 available_options=["Option A", "Option B", "Option C"],
                 timeout_seconds=60)  # Longer timeout for complex decisions
```

### Memory Management

```python
# Clear old clarification context to prevent memory bloat
def cleanup_clarification_context(context):
    # Keep only recent clarification history
    clarification_history = context.get("clarification_history", [])
    if len(clarification_history) > 5:
        context.set("clarification_history", clarification_history[-5:])
```
