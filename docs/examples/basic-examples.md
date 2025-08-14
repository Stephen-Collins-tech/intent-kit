# Basic Examples

This guide provides basic examples of common Intent Kit patterns and use cases. These examples demonstrate fundamental concepts and can be used as building blocks for more complex applications.

## Table of Contents

- [Simple Greeting Bot](#simple-greeting-bot)
- [Calculator with Multiple Operations](#calculator-with-multiple-operations)
- [Weather Information Bot](#weather-information-bot)
- [Task Management System](#task-management-system)
- [Customer Support Router](#customer-support-router)
- [Data Query System](#data-query-system)

## Simple Greeting Bot

A basic example that demonstrates intent classification and parameter extraction.

```python
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

# Define the greeting action
def greet_action(name: str, **kwargs) -> str:
    return f"Hello {name}! Nice to meet you."

# Create the DAG
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "temperature": 0.1
})

# Add classifier to understand user intent
builder.add_node("classifier", "classifier",
                 output_labels=["greet"],
                 description="Determine if user wants to be greeted")

# Add extractor to get the person's name
builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract the person's name from the greeting",
                 output_key="extracted_params")

# Add action to perform the greeting
builder.add_node("greet_action", "action",
                 action=greet_action,
                 description="Greet the person by name")

# Connect the nodes
builder.add_edge("classifier", "extract_name", "greet")
builder.add_edge("extract_name", "greet_action", "success")
builder.set_entrypoints(["classifier"])

# Build and test
dag = builder.build()

# Test with different inputs
test_inputs = [
    "Hello Alice",
    "Hi Bob, how are you?",
    "Greet Sarah",
    "Good morning John"
]

for input_text in test_inputs:
    result, context = run_dag(dag, input_text)
    print(f"Input: {input_text}")
    print(f"Output: {result.data}")
    print("---")
```

**Expected Output:**
```
Input: Hello Alice
Output: Hello Alice! Nice to meet you.
---
Input: Hi Bob, how are you?
Output: Hello Bob! Nice to meet you.
---
```

## Calculator with Multiple Operations

A more complex example that handles multiple intents and operations.

```python
from intent_kit import DAGBuilder
from intent_kit.core.context import DefaultContext

# Define calculator actions
def add_action(a: float, b: float, **kwargs) -> str:
    return f"{a} + {b} = {a + b}"

def subtract_action(a: float, b: float, **kwargs) -> str:
    return f"{a} - {b} = {a - b}"

def multiply_action(a: float, b: float, **kwargs) -> str:
    return f"{a} × {b} = {a * b}"

def divide_action(a: float, b: float, **kwargs) -> str:
    if b == 0:
        return "Error: Cannot divide by zero"
    return f"{a} ÷ {b} = {a / b}"

# Create the DAG
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "temperature": 0.1
})

# Add main classifier
builder.add_node("classifier", "classifier",
                 output_labels=["add", "subtract", "multiply", "divide"],
                 description="Determine the mathematical operation")

# Add extractors for each operation
builder.add_node("extract_add", "extractor",
                 param_schema={"a": float, "b": float},
                 description="Extract two numbers for addition",
                 output_key="extracted_params")

builder.add_node("extract_subtract", "extractor",
                 param_schema={"a": float, "b": float},
                 description="Extract two numbers for subtraction",
                 output_key="extracted_params")

builder.add_node("extract_multiply", "extractor",
                 param_schema={"a": float, "b": float},
                 description="Extract two numbers for multiplication",
                 output_key="extracted_params")

builder.add_node("extract_divide", "extractor",
                 param_schema={"a": float, "b": float},
                 description="Extract two numbers for division",
                 output_key="extracted_params")

# Add action nodes
builder.add_node("add_action", "action",
                 action=add_action,
                 description="Perform addition")

builder.add_node("subtract_action", "action",
                 action=subtract_action,
                 description="Perform subtraction")

builder.add_node("multiply_action", "action",
                 action=multiply_action,
                 description="Perform multiplication")

builder.add_node("divide_action", "action",
                 action=divide_action,
                 description="Perform division")

# Connect nodes
builder.add_edge("classifier", "extract_add", "add")
builder.add_edge("extract_add", "add_action", "success")

builder.add_edge("classifier", "extract_subtract", "subtract")
builder.add_edge("extract_subtract", "subtract_action", "success")

builder.add_edge("classifier", "extract_multiply", "multiply")
builder.add_edge("extract_multiply", "multiply_action", "success")

builder.add_edge("classifier", "extract_divide", "divide")
builder.add_edge("extract_divide", "divide_action", "success")

builder.set_entrypoints(["classifier"])

# Build and test
dag = builder.build()

# Test with different operations
test_inputs = [
    "Add 5 and 3",
    "Subtract 10 from 15",
    "Multiply 4 by 7",
    "Divide 20 by 4",
    "What is 8 plus 12?"
]

for input_text in test_inputs:
    result, context = run_dag(dag, input_text)
    print(f"Input: {input_text}")
    print(f"Output: {result.data}")
    print("---")
```

## Weather Information Bot

An example that demonstrates handling complex parameter extraction and external API calls.

```python
from intent_kit import DAGBuilder
from intent_kit.core.context import DefaultContext
from datetime import datetime

# Simulate weather API call
def get_weather_action(city: str, date: str = None, **kwargs) -> str:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    # Simulate weather data
    weather_data = {
        "New York": {"temperature": "22°C", "condition": "sunny"},
        "London": {"temperature": "15°C", "condition": "rainy"},
        "Tokyo": {"temperature": "25°C", "condition": "cloudy"},
        "Sydney": {"temperature": "28°C", "condition": "clear"}
    }

    if city in weather_data:
        weather = weather_data[city]
        return f"Weather in {city} on {date}: {weather['temperature']}, {weather['condition']}"
    else:
        return f"Weather data not available for {city}"

# Create the DAG
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "temperature": 0.1
})

# Add classifier
builder.add_node("classifier", "classifier",
                 output_labels=["weather"],
                 description="Determine if user wants weather information")

# Add extractor for weather parameters
builder.add_node("extract_weather", "extractor",
                 param_schema={"city": str, "date": str},
                 description="Extract city name and optional date for weather query",
                 output_key="extracted_params")

# Add weather action
builder.add_node("weather_action", "action",
                 action=get_weather_action,
                 description="Get weather information for the specified city")

# Connect nodes
builder.add_edge("classifier", "extract_weather", "weather")
builder.add_edge("extract_weather", "weather_action", "success")
builder.set_entrypoints(["classifier"])

# Build and test
dag = builder.build()

# Test with different weather queries
test_inputs = [
    "What's the weather in New York?",
    "How's the weather in London today?",
    "Weather forecast for Tokyo tomorrow",
    "Tell me about the weather in Sydney"
]

for input_text in test_inputs:
    result, context = run_dag(dag, input_text)
    print(f"Input: {input_text}")
    print(f"Output: {result.data}")
    print("---")
```

## Task Management System

An example that demonstrates context management and state persistence.

```python
from intent_kit import DAGBuilder
from intent_kit.core.context import DefaultContext

# Task storage (in a real app, this would be a database)
tasks = []

def add_task_action(title: str, priority: str = "medium", **kwargs) -> str:
    task_id = len(tasks) + 1
    task = {"id": task_id, "title": title, "priority": priority, "completed": False}
    tasks.append(task)
    return f"Task added: {title} (Priority: {priority}, ID: {task_id})"

def list_tasks_action(**kwargs) -> str:
    if not tasks:
        return "No tasks found."

    task_list = []
    for task in tasks:
        status = "✓" if task["completed"] else "□"
        task_list.append(f"{status} {task['id']}. {task['title']} ({task['priority']})")

    return "Tasks:\n" + "\n".join(task_list)

def complete_task_action(task_id: int, **kwargs) -> str:
    if 1 <= task_id <= len(tasks):
        tasks[task_id - 1]["completed"] = True
        return f"Task {task_id} marked as completed."
    else:
        return f"Task {task_id} not found."

# Create the DAG
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "temperature": 0.1
})

# Add classifier
builder.add_node("classifier", "classifier",
                 output_labels=["add_task", "list_tasks", "complete_task"],
                 description="Determine the task management action")

# Add extractors
builder.add_node("extract_add_task", "extractor",
                 param_schema={"title": str, "priority": str},
                 description="Extract task title and priority",
                 output_key="extracted_params")

builder.add_node("extract_complete_task", "extractor",
                 param_schema={"task_id": int},
                 description="Extract task ID to complete",
                 output_key="extracted_params")

# Add actions
builder.add_node("add_task_action", "action",
                 action=add_task_action,
                 description="Add a new task")

builder.add_node("list_tasks_action", "action",
                 action=list_tasks_action,
                 description="List all tasks")

builder.add_node("complete_task_action", "action",
                 action=complete_task_action,
                 description="Mark a task as completed")

# Connect nodes
builder.add_edge("classifier", "extract_add_task", "add_task")
builder.add_edge("extract_add_task", "add_task_action", "success")

builder.add_edge("classifier", "list_tasks_action", "list_tasks")

builder.add_edge("classifier", "extract_complete_task", "complete_task")
builder.add_edge("extract_complete_task", "complete_task_action", "success")

builder.set_entrypoints(["classifier"])

# Build and test
dag = builder.build()

# Test task management
test_inputs = [
    "Add a task to buy groceries",
    "Add a high priority task to call the doctor",
    "List all tasks",
    "Complete task 1",
    "List all tasks"
]

for input_text in test_inputs:
    result, context = run_dag(dag, input_text)
    print(f"Input: {input_text}")
    print(f"Output: {result.data}")
    print("---")
```

## Customer Support Router

An example that demonstrates complex routing and error handling.

```python
from intent_kit import DAGBuilder
from intent_kit.core.context import DefaultContext

# Support actions
def billing_support_action(issue: str, **kwargs) -> str:
    return f"Billing support ticket created: {issue}. A representative will contact you within 24 hours."

def technical_support_action(issue: str, **kwargs) -> str:
    return f"Technical support ticket created: {issue}. Our engineers will investigate and respond within 2 hours."

def general_inquiry_action(question: str, **kwargs) -> str:
    return f"General inquiry received: {question}. We'll get back to you with an answer soon."

def escalation_action(issue: str, **kwargs) -> str:
    return f"Your issue has been escalated to senior support: {issue}. You'll receive a call within 1 hour."

# Create the DAG
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "temperature": 0.1
})

# Add main classifier
builder.add_node("classifier", "classifier",
                 output_labels=["billing", "technical", "general", "escalation"],
                 description="Classify customer support requests")

# Add extractors
builder.add_node("extract_billing", "extractor",
                 param_schema={"issue": str},
                 description="Extract billing issue details",
                 output_key="extracted_params")

builder.add_node("extract_technical", "extractor",
                 param_schema={"issue": str},
                 description="Extract technical issue details",
                 output_key="extracted_params")

builder.add_node("extract_general", "extractor",
                 param_schema={"question": str},
                 description="Extract general inquiry question",
                 output_key="extracted_params")

builder.add_node("extract_escalation", "extractor",
                 param_schema={"issue": str},
                 description="Extract escalation issue details",
                 output_key="extracted_params")

# Add actions
builder.add_node("billing_action", "action",
                 action=billing_support_action,
                 description="Handle billing support request")

builder.add_node("technical_action", "action",
                 action=technical_support_action,
                 description="Handle technical support request")

builder.add_node("general_action", "action",
                 action=general_inquiry_action,
                 description="Handle general inquiry")

builder.add_node("escalation_action", "action",
                 action=escalation_action,
                 description="Handle escalated support request")

# Connect nodes
builder.add_edge("classifier", "extract_billing", "billing")
builder.add_edge("extract_billing", "billing_action", "success")

builder.add_edge("classifier", "extract_technical", "technical")
builder.add_edge("extract_technical", "technical_action", "success")

builder.add_edge("classifier", "extract_general", "general")
builder.add_edge("extract_general", "general_action", "success")

builder.add_edge("classifier", "extract_escalation", "escalation")
builder.add_edge("extract_escalation", "escalation_action", "success")

builder.set_entrypoints(["classifier"])

# Build and test
dag = builder.build()

# Test customer support routing
test_inputs = [
    "I have a billing issue with my subscription",
    "The app is crashing when I try to upload files",
    "What are your business hours?",
    "This is urgent and I need immediate assistance"
]

for input_text in test_inputs:
    result, context = run_dag(dag, input_text)
    print(f"Input: {input_text}")
    print(f"Output: {result.data}")
    print("---")
```

## Data Query System

An example that demonstrates complex data processing and multiple parameter types.

```python
from intent_kit import DAGBuilder
from intent_kit.core.context import DefaultContext
from datetime import datetime, timedelta

# Simulate database
sales_data = [
    {"date": "2024-01-01", "product": "Widget A", "amount": 1000, "region": "North"},
    {"date": "2024-01-02", "product": "Widget B", "amount": 1500, "region": "South"},
    {"date": "2024-01-03", "product": "Widget A", "amount": 800, "region": "North"},
    {"date": "2024-01-04", "product": "Widget C", "amount": 2000, "region": "East"},
]

def sales_report_action(product: str = None, region: str = None, start_date: str = None, end_date: str = None, **kwargs) -> str:
    filtered_data = sales_data.copy()

    if product:
        filtered_data = [d for d in filtered_data if d["product"] == product]
    if region:
        filtered_data = [d for d in filtered_data if d["region"] == region]
    if start_date:
        filtered_data = [d for d in filtered_data if d["date"] >= start_date]
    if end_date:
        filtered_data = [d for d in filtered_data if d["date"] <= end_date]

    if not filtered_data:
        return "No sales data found for the specified criteria."

    total_amount = sum(d["amount"] for d in filtered_data)
    count = len(filtered_data)

    filters = []
    if product: filters.append(f"Product: {product}")
    if region: filters.append(f"Region: {region}")
    if start_date: filters.append(f"Start Date: {start_date}")
    if end_date: filters.append(f"End Date: {end_date}")

    filter_text = ", ".join(filters) if filters else "All data"

    return f"Sales Report ({filter_text}):\nTotal Sales: ${total_amount:,}\nNumber of Transactions: {count}"

def inventory_check_action(product: str, **kwargs) -> str:
    # Simulate inventory data
    inventory = {
        "Widget A": {"quantity": 150, "location": "Warehouse 1"},
        "Widget B": {"quantity": 75, "location": "Warehouse 2"},
        "Widget C": {"quantity": 200, "location": "Warehouse 1"},
    }

    if product in inventory:
        item = inventory[product]
        return f"Inventory for {product}: {item['quantity']} units at {item['location']}"
    else:
        return f"Product {product} not found in inventory."

# Create the DAG
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it",
    "temperature": 0.1
})

# Add classifier
builder.add_node("classifier", "classifier",
                 output_labels=["sales_report", "inventory_check"],
                 description="Determine the type of data query")

# Add extractors
builder.add_node("extract_sales", "extractor",
                 param_schema={"product": str, "region": str, "start_date": str, "end_date": str},
                 description="Extract sales report parameters",
                 output_key="extracted_params")

builder.add_node("extract_inventory", "extractor",
                 param_schema={"product": str},
                 description="Extract product name for inventory check",
                 output_key="extracted_params")

# Add actions
builder.add_node("sales_action", "action",
                 action=sales_report_action,
                 description="Generate sales report")

builder.add_node("inventory_action", "action",
                 action=inventory_check_action,
                 description="Check inventory levels")

# Connect nodes
builder.add_edge("classifier", "extract_sales", "sales_report")
builder.add_edge("extract_sales", "sales_action", "success")

builder.add_edge("classifier", "extract_inventory", "inventory_check")
builder.add_edge("extract_inventory", "inventory_action", "success")

builder.set_entrypoints(["classifier"])

# Build and test
dag = builder.build()

# Test data queries
test_inputs = [
    "Show me sales for Widget A",
    "What's the inventory for Widget B?",
    "Sales report for North region",
    "Check inventory for Widget C"
]

for input_text in test_inputs:
    result, context = run_dag(dag, input_text)
    print(f"Input: {input_text}")
    print(f"Output: {result.data}")
    print("---")
```

## Best Practices

### 1. Start Simple
Begin with basic workflows and gradually add complexity. Each example above builds on the previous concepts.

### 2. Use Descriptive Names
Choose clear, descriptive names for your nodes and actions:
```python
# Good
builder.add_node("extract_user_name", "extractor", ...)
builder.add_node("send_greeting", "action", ...)

# Avoid
builder.add_node("extract", "extractor", ...)
builder.add_node("action1", "action", ...)
```

### 3. Handle Edge Cases
Always consider what happens when:
- Required parameters are missing
- Invalid data is provided
- External services are unavailable

### 4. Test Thoroughly
Test your workflows with various inputs:
```python
test_cases = [
    "Normal case",
    "Edge case",
    "Error case",
    "Empty input",
    "Very long input"
]
```

### 5. Use Context Effectively
Leverage context to maintain state across interactions:
```python
# Store user preferences
context.set("user_preferences", {"language": "en", "timezone": "UTC"})

# Retrieve in later interactions
prefs = context.get("user_preferences", {})
```

### 6. Monitor Performance
Track execution times and success rates:
```python
import time

start_time = time.time()
result = dag.execute(input_text, context)
execution_time = time.time() - start_time

print(f"Execution time: {execution_time:.2f} seconds")
```

## Next Steps

- Explore [DAG Examples](dag-examples.md) for more complex patterns
- Learn about [Context Management](../concepts/context-architecture.md) for stateful applications
- Check out [JSON Configuration](../configuration/json-serialization.md) for declarative workflows
- Review [Testing Strategies](../development/testing.md) for robust applications
