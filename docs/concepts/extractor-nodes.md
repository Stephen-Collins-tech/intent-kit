# Extractor Nodes

Extractor nodes are powerful components in Intent Kit that use LLM services to extract structured parameters from user input. They provide intelligent parameter extraction with type validation and error handling.

## Overview

Extractor nodes:
- Use LLM services to understand and extract parameters from natural language
- Support type validation and coercion
- Provide structured output with extracted parameters
- Handle edge cases and missing parameters gracefully
- Track token usage and costs

## Basic Usage

```python
from intent_kit import DAGBuilder

# Add to DAG
builder = DAGBuilder()
builder.add_node("extract_booking", "extractor",
                 param_schema={
                     "date": str,
                     "time": str,
                     "guests": int,
                     "restaurant": str
                 },
                 description="Extract booking parameters",
                 output_key="booking_params")
```

## Parameter Schema

The `param_schema` defines the structure and types of parameters to extract:

```python
param_schema = {
    "name": str,           # String parameter
    "age": int,            # Integer parameter
    "price": float,        # Float parameter
    "is_active": bool,     # Boolean parameter
    "tags": list,          # List parameter
    "metadata": dict       # Dictionary parameter
}
```

### Type Validation

Extractor nodes automatically validate and coerce types:

```python
# Input: "I want to book for 5 people at 7:30 PM"
# Output: {"guests": 5, "time": "7:30 PM"}

param_schema = {
    "guests": int,    # Will extract "5" and convert to integer
    "time": str       # Will extract "7:30 PM" as string
}
```

## Advanced Configuration

### Custom Prompts

You can provide custom prompts for specific extraction scenarios:

```python
extractor = ExtractorNode(
    name="extract_address",
    param_schema={"street": str, "city": str, "zip": str},
    custom_prompt="""
    Extract address components from the user input.
    Focus on identifying street address, city, and zip code.
    If any component is missing, use null.
    """,
    output_key="address_params"
)
```

### LLM Configuration

Configure specific LLM settings for extraction:

```python
extractor = ExtractorNode(
    name="extract_complex_params",
    param_schema={"complex_field": str},
    llm_config={
        "provider": "openrouter",
        "model": "google/gemma-2-9b-it",
        "temperature": 0.1,  # Low temperature for consistent extraction
        "max_tokens": 500
    },
    output_key="complex_params"
)
```

## Error Handling

Extractor nodes handle various error scenarios:

### Missing Parameters

```python
# If a parameter is missing, it will be set to None or default value
# Input: "Book a table for 4 people" (missing time)
# Output: {"guests": 4, "time": None}
```

### Type Conversion Errors

```python
# If type conversion fails, the node will handle gracefully
# Input: "Book for abc people" (invalid number)
# Output: {"guests": None} with error in context
```

### LLM Service Errors

```python
# If LLM service is unavailable, the node will raise appropriate exceptions
# with detailed error information
```

## Context Integration

Extracted parameters are stored in the execution context:

```python
# After extraction, parameters are available in context
context = DefaultContext()
result = dag.execute("Book a table for 4 people at 7 PM", context)

# Access extracted parameters
booking_params = context.get("booking_params")
print(booking_params)  # {"guests": 4, "time": "7 PM"}
```

## Performance Monitoring

Extractor nodes track performance metrics:

```python
# Metrics are available in the execution result
result = extractor.execute("Book a table for 4 people", context)

print(result.metrics)
# {
#     "input_tokens": 15,
#     "output_tokens": 45,
#     "cost": 0.0023,
#     "duration": 1.2
# }
```

## Best Practices

### 1. Clear Parameter Names

```python
# Good: Clear, descriptive parameter names
param_schema = {
    "reservation_date": str,
    "party_size": int,
    "preferred_time": str
}

# Avoid: Vague parameter names
param_schema = {
    "date": str,
    "size": int,
    "time": str
}
```

### 2. Appropriate Type Definitions

```python
# Use specific types when possible
param_schema = {
    "price": float,        # Use float for monetary values
    "quantity": int,       # Use int for counts
    "is_confirmed": bool,  # Use bool for flags
    "notes": str          # Use str for text
}
```

### 3. Descriptive Prompts

```python
# Provide clear, specific prompts
custom_prompt = """
Extract booking information from the user's request.
- reservation_date: The date for the reservation (YYYY-MM-DD format)
- party_size: Number of people (integer)
- preferred_time: Preferred time (HH:MM format)
- special_requests: Any special requirements or requests
"""
```

### 4. Error Handling

```python
# Always handle missing or invalid parameters
def process_booking(context):
    params = context.get("booking_params", {})

    if not params.get("party_size"):
        return "How many people will be in your party?"

    if not params.get("reservation_date"):
        return "What date would you like to make the reservation for?"

    # Process valid booking
    return f"Booking confirmed for {params['party_size']} people on {params['reservation_date']}"
```

## Integration with Other Nodes

### With Classifier Nodes

```python
# Classifier routes to appropriate extractor
builder.add_edge("intent_classifier", "booking_extractor", "make_booking")
builder.add_edge("intent_classifier", "flight_extractor", "book_flight")
```

### With Action Nodes

```python
# Extractor provides parameters to action
builder.add_edge("booking_extractor", "create_booking_action", "success")
```

### With Clarification Nodes

```python
# Extractor can route to clarification if parameters are unclear
builder.add_edge("booking_extractor", "booking_clarification", "missing_params")
```

## Examples

### Restaurant Booking

```python
builder.add_node("extract_booking", "extractor",
                 param_schema={
                     "restaurant": str,
                     "date": str,
                     "time": str,
                     "party_size": int,
                     "special_requests": str
                 },
                 description="Extract restaurant booking parameters",
                 custom_prompt="""
                 Extract restaurant booking information:
                 - restaurant: Name of the restaurant
                 - date: Reservation date (YYYY-MM-DD)
                 - time: Preferred time (HH:MM)
                 - party_size: Number of people
                 - special_requests: Any special requirements
                 """,
                 output_key="booking_params")
```

### Flight Booking

```python
builder.add_node("extract_flight", "extractor",
                 param_schema={
                     "origin": str,
                     "destination": str,
                     "departure_date": str,
                     "return_date": str,
                     "passengers": int,
                     "class": str
                 },
                 description="Extract flight booking parameters",
                 output_key="flight_params")
```

### Product Search

```python
builder.add_node("extract_search", "extractor",
                 param_schema={
                     "product": str,
                     "category": str,
                     "min_price": float,
                     "max_price": float,
                     "brand": str
                 },
                 description="Extract product search parameters",
                 output_key="search_params")
```
