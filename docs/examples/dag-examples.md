# DAG Examples

This guide provides comprehensive examples of DAG patterns, including node reuse, complex routing, and advanced use cases.

## Overview

DAGs in Intent Kit support:
- **Node Reuse** - Share nodes across multiple execution paths
- **Complex Routing** - Conditional logic and branching
- **Parallel Execution** - Multiple paths executed simultaneously
- **Context Propagation** - Rich context flows through all paths

## Basic DAG Patterns

### Simple Linear Flow

```python
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

def greet(name: str, **kwargs) -> str:
    return f"Hello {name}!"

def get_weather(city: str, **kwargs) -> str:
    return f"Weather in {city} is sunny"

# Create DAG
builder = DAGBuilder()
builder.with_default_llm_config({
    "provider": "openrouter",
    "model": "google/gemma-2-9b-it"
})

# Add nodes
builder.add_node("classifier", "classifier",
                 output_labels=["greet", "weather"],
                 description="Route to appropriate action")

builder.add_node("extract_name", "extractor",
                 param_schema={"name": str},
                 description="Extract name from greeting")

builder.add_node("extract_city", "extractor",
                 param_schema={"city": str},
                 description="Extract city from weather request")

builder.add_node("greet_action", "action",
                 action=greet,
                 description="Greet the user")

builder.add_node("weather_action", "action",
                 action=get_weather,
                 description="Get weather information")

# Connect nodes
builder.add_edge("classifier", "extract_name", "greet")
builder.add_edge("extract_name", "greet_action", "success")
builder.add_edge("classifier", "extract_city", "weather")
builder.add_edge("extract_city", "weather_action", "success")

builder.set_entrypoints(["classifier"])

# Build and execute
dag = builder.build()
context = DefaultContext()

result, context = run_dag(dag, "Hello Alice")
print(result.data)  # "Hello Alice!"

result, context = run_dag(dag, "What's the weather in New York?", context)
print(result.data)  # "Weather in New York is sunny"
```

## Node Reuse Patterns

### Shared Extractor

```python
from intent_kit import DAGBuilder

def book_flight(origin: str, destination: str, date: str) -> str:
    return f"Flight booked from {origin} to {destination} on {date}"

def book_hotel(city: str, check_in: str, check_out: str) -> str:
    return f"Hotel booked in {city} from {check_in} to {check_out}"

# Create DAG with shared extractor
builder = DAGBuilder()

# Shared location extractor used by multiple paths
builder.add_node("extract_location", "extractor",
                 param_schema={"location": str},
                 description="Extract location information",
                 output_key="location_params")

# Flight booking path
builder.add_node("flight_classifier", "classifier",
                 output_labels=["book_flight"],
                 description="Classify flight booking requests")

builder.add_node("extract_flight_details", "extractor",
                 param_schema={"origin": str, "destination": str, "date": str},
                 description="Extract flight details")

builder.add_node("flight_action", "action",
                 action=book_flight,
                 description="Book flight")

# Hotel booking path
builder.add_node("hotel_classifier", "classifier",
                 output_labels=["book_hotel"],
                 description="Classify hotel booking requests")

builder.add_node("extract_hotel_details", "extractor",
                 param_schema={"city": str, "check_in": str, "check_out": str},
                 description="Extract hotel details")

builder.add_node("hotel_action", "action",
                 action=book_hotel,
                 description="Book hotel")

# Connect with shared extractor
builder.add_edge("flight_classifier", "extract_location", "book_flight")
builder.add_edge("extract_location", "extract_flight_details", "success")
builder.add_edge("extract_flight_details", "flight_action", "success")

builder.add_edge("hotel_classifier", "extract_location", "book_hotel")
builder.add_edge("extract_location", "extract_hotel_details", "success")
builder.add_edge("extract_hotel_details", "hotel_action", "success")

builder.set_entrypoints(["flight_classifier", "hotel_classifier"])
```

### Shared Classifier

```python
from intent_kit import DAGBuilder

def process_order(product: str, quantity: int) -> str:
    return f"Order processed: {quantity} x {product}"

def check_inventory(product: str) -> str:
    return f"Inventory check for {product}: In stock"

def calculate_price(product: str, quantity: int) -> str:
    return f"Price for {quantity} x {product}: $99.99"

# Create DAG with shared classifier
builder = DAGBuilder()

# Shared classifier for product-related requests
builder.add_node("product_classifier", "classifier",
                 output_labels=["order", "inventory", "price"],
                 description="Classify product-related requests")

# Shared product extractor
builder.add_node("extract_product", "extractor",
                 param_schema={"product": str},
                 description="Extract product information")

# Order processing path
builder.add_node("extract_order_details", "extractor",
                 param_schema={"product": str, "quantity": int},
                 description="Extract order details")

builder.add_node("order_action", "action",
                 action=process_order,
                 description="Process order")

# Inventory check path
builder.add_node("inventory_action", "action",
                 action=check_inventory,
                 description="Check inventory")

# Price calculation path
builder.add_node("extract_price_details", "extractor",
                 param_schema={"product": str, "quantity": int},
                 description="Extract price calculation details")

builder.add_node("price_action", "action",
                 action=calculate_price,
                 description="Calculate price")

# Connect with shared classifier and extractor
builder.add_edge("product_classifier", "extract_product", "order")
builder.add_edge("extract_product", "extract_order_details", "success")
builder.add_edge("extract_order_details", "order_action", "success")

builder.add_edge("product_classifier", "extract_product", "inventory")
builder.add_edge("extract_product", "inventory_action", "success")

builder.add_edge("product_classifier", "extract_product", "price")
builder.add_edge("extract_product", "extract_price_details", "success")
builder.add_edge("extract_price_details", "price_action", "success")

builder.set_entrypoints(["product_classifier"])
```

## Complex Routing Patterns

### Conditional Branching

```python
from intent_kit import DAGBuilder

def process_urgent_request(details: str) -> str:
    return f"URGENT: {details} - Escalated to priority queue"

def process_normal_request(details: str) -> str:
    return f"Normal: {details} - Added to standard queue"

def process_low_priority_request(details: str) -> str:
    return f"Low priority: {details} - Added to background queue"

# Create DAG with conditional branching
builder = DAGBuilder()

# Main classifier
builder.add_node("request_classifier", "classifier",
                 output_labels=["urgent", "normal", "low"],
                 description="Classify request priority")

# Priority-specific extractors
builder.add_node("extract_urgent_details", "extractor",
                 param_schema={"details": str, "priority": str},
                 description="Extract urgent request details")

builder.add_node("extract_normal_details", "extractor",
                 param_schema={"details": str},
                 description="Extract normal request details")

builder.add_node("extract_low_details", "extractor",
                 param_schema={"details": str},
                 description="Extract low priority request details")

# Priority-specific actions
builder.add_node("urgent_action", "action",
                 action=process_urgent_request,
                 description="Process urgent request")

builder.add_node("normal_action", "action",
                 action=process_normal_request,
                 description="Process normal request")

builder.add_node("low_action", "action",
                 action=process_low_priority_request,
                 description="Process low priority request")

# Connect with conditional branching
builder.add_edge("request_classifier", "extract_urgent_details", "urgent")
builder.add_edge("extract_urgent_details", "urgent_action", "success")

builder.add_edge("request_classifier", "extract_normal_details", "normal")
builder.add_edge("extract_normal_details", "normal_action", "success")

builder.add_edge("request_classifier", "extract_low_details", "low")
builder.add_edge("extract_low_details", "low_action", "success")

builder.set_entrypoints(["request_classifier"])
```

### Multi-Step Validation

```python
from intent_kit import DAGBuilder

def validate_user(user_id: str) -> str:
    return f"User {user_id} validated"

def validate_payment(payment_info: str) -> str:
    return f"Payment {payment_info} validated"

def process_purchase(user_id: str, product: str, payment_info: str) -> str:
    return f"Purchase completed: {product} for user {user_id}"

def request_authentication() -> str:
    return "Please authenticate to continue"

def request_payment_info() -> str:
    return "Please provide payment information"

# Create DAG with multi-step validation
builder = DAGBuilder()

# Initial classifier
builder.add_node("purchase_classifier", "classifier",
                 output_labels=["purchase"],
                 description="Classify purchase requests")

# Extract purchase details
builder.add_node("extract_purchase_details", "extractor",
                 param_schema={"user_id": str, "product": str, "payment_info": str},
                 description="Extract purchase details")

# Validation nodes
builder.add_node("user_validator", "classifier",
                 output_labels=["valid", "invalid"],
                 description="Validate user")

builder.add_node("payment_validator", "classifier",
                 output_labels=["valid", "invalid"],
                 description="Validate payment")

# Actions
builder.add_node("user_validation_action", "action",
                 action=validate_user,
                 description="Validate user")

builder.add_node("payment_validation_action", "action",
                 action=validate_payment,
                 description="Validate payment")

builder.add_node("purchase_action", "action",
                 action=process_purchase,
                 description="Process purchase")

builder.add_node("auth_clarification", "clarification",
                 clarification_message="Please authenticate to continue",
                 available_options=["Login", "Register", "Cancel"],
                 output_key="auth_response")

builder.add_node("payment_clarification", "clarification",
                 clarification_message="Please provide payment information",
                 available_options=["Credit Card", "PayPal", "Cancel"],
                 output_key="payment_response")

# Connect multi-step validation
builder.add_edge("purchase_classifier", "extract_purchase_details", "purchase")
builder.add_edge("extract_purchase_details", "user_validator", "success")
builder.add_edge("user_validator", "user_validation_action", "valid")
builder.add_edge("user_validator", "auth_clarification", "invalid")
builder.add_edge("auth_clarification", "user_validator", "Login")

builder.add_edge("user_validation_action", "payment_validator", "success")
builder.add_edge("payment_validator", "payment_validation_action", "valid")
builder.add_edge("payment_validator", "payment_clarification", "invalid")
builder.add_edge("payment_clarification", "payment_validator", "Credit Card")

builder.add_edge("payment_validation_action", "purchase_action", "success")

builder.set_entrypoints(["purchase_classifier"])
```

## Advanced Patterns

### Parallel Processing

```python
from intent_kit import DAGBuilder

def analyze_sentiment(text: str) -> str:
    return f"Sentiment analysis: {text} is positive"

def extract_keywords(text: str) -> str:
    return f"Keywords extracted: {text}"

def summarize_text(text: str) -> str:
    return f"Summary: {text[:50]}..."

def combine_analysis(sentiment: str, keywords: str, summary: str) -> str:
    return f"Combined analysis: {sentiment}, {keywords}, {summary}"

# Create DAG with parallel processing
builder = DAGBuilder()

# Main classifier
builder.add_node("text_classifier", "classifier",
                 output_labels=["analyze"],
                 description="Classify text analysis requests")

# Extract text
builder.add_node("extract_text", "extractor",
                 param_schema={"text": str},
                 description="Extract text for analysis")

# Parallel analysis nodes
builder.add_node("sentiment_analyzer", "action",
                 action=analyze_sentiment,
                 description="Analyze sentiment")

builder.add_node("keyword_extractor", "action",
                 action=extract_keywords,
                 description="Extract keywords")

builder.add_node("text_summarizer", "action",
                 action=summarize_text,
                 description="Summarize text")

# Combine results
builder.add_node("analysis_combiner", "action",
                 action=combine_analysis,
                 description="Combine analysis results")

# Connect parallel processing
builder.add_edge("text_classifier", "extract_text", "analyze")
builder.add_edge("extract_text", "sentiment_analyzer", "success")
builder.add_edge("extract_text", "keyword_extractor", "success")
builder.add_edge("extract_text", "text_summarizer", "success")

# All parallel nodes feed into combiner
builder.add_edge("sentiment_analyzer", "analysis_combiner", "success")
builder.add_edge("keyword_extractor", "analysis_combiner", "success")
builder.add_edge("text_summarizer", "analysis_combiner", "success")

builder.set_entrypoints(["text_classifier"])
```

### Error Handling and Recovery

```python
from intent_kit import DAGBuilder

def process_data(data: str) -> str:
    return f"Data processed: {data}"

def fallback_processing(data: str) -> str:
    return f"Fallback processing: {data}"

def log_error(error: str) -> str:
    return f"Error logged: {error}"

def retry_processing(data: str) -> str:
    return f"Retry processing: {data}"

# Create DAG with error handling
builder = DAGBuilder()

# Main classifier
builder.add_node("data_classifier", "classifier",
                 output_labels=["process"],
                 description="Classify data processing requests")

# Extract data
builder.add_node("extract_data", "extractor",
                 param_schema={"data": str},
                 description="Extract data for processing")

# Processing nodes
builder.add_node("data_processor", "classifier",
                 output_labels=["success", "error", "retry"],
                 description="Process data with error handling")

builder.add_node("main_processor", "action",
                 action=process_data,
                 description="Main data processor")

builder.add_node("fallback_processor", "action",
                 action=fallback_processing,
                 description="Fallback processor")

builder.add_node("error_logger", "action",
                 action=log_error,
                 description="Log errors")

builder.add_node("retry_processor", "action",
                 action=retry_processing,
                 description="Retry processing")

# Connect with error handling
builder.add_edge("data_classifier", "extract_data", "process")
builder.add_edge("extract_data", "data_processor", "success")
builder.add_edge("data_processor", "main_processor", "success")
builder.add_edge("data_processor", "fallback_processor", "error")
builder.add_edge("data_processor", "retry_processor", "retry")

# Error logging
builder.add_edge("main_processor", "error_logger", "error")
builder.add_edge("fallback_processor", "error_logger", "error")
builder.add_edge("retry_processor", "error_logger", "error")

builder.set_entrypoints(["data_classifier"])
```

## Real-World Examples

### Customer Support System

```python
from intent_kit import DAGBuilder

def route_ticket(category: str, priority: str) -> str:
    return f"Ticket routed to {category} team with {priority} priority"

def create_ticket(user_id: str, issue: str) -> str:
    return f"Support ticket created for user {user_id}: {issue}"

def escalate_ticket(ticket_id: str, reason: str) -> str:
    return f"Ticket {ticket_id} escalated: {reason}"

def resolve_ticket(ticket_id: str, solution: str) -> str:
    return f"Ticket {ticket_id} resolved: {solution}"

# Create customer support DAG
builder = DAGBuilder()

# Main classifier
builder.add_node("support_classifier", "classifier",
                 output_labels=["create", "escalate", "resolve", "status"],
                 description="Classify support requests")

# Shared extractors
builder.add_node("extract_user_info", "extractor",
                 param_schema={"user_id": str},
                 description="Extract user information")

builder.add_node("extract_ticket_info", "extractor",
                 param_schema={"ticket_id": str},
                 description="Extract ticket information")

# Specific extractors
builder.add_node("extract_issue_details", "extractor",
                 param_schema={"issue": str, "category": str, "priority": str},
                 description="Extract issue details")

builder.add_node("extract_escalation_details", "extractor",
                 param_schema={"ticket_id": str, "reason": str},
                 description="Extract escalation details")

builder.add_node("extract_resolution_details", "extractor",
                 param_schema={"ticket_id": str, "solution": str},
                 description="Extract resolution details")

# Actions
builder.add_node("ticket_creator", "action",
                 action=create_ticket,
                 description="Create support ticket")

builder.add_node("ticket_router", "action",
                 action=route_ticket,
                 description="Route ticket to appropriate team")

builder.add_node("ticket_escalator", "action",
                 action=escalate_ticket,
                 description="Escalate ticket")

builder.add_node("ticket_resolver", "action",
                 action=resolve_ticket,
                 description="Resolve ticket")

# Connect customer support flow
builder.add_edge("support_classifier", "extract_user_info", "create")
builder.add_edge("extract_user_info", "extract_issue_details", "success")
builder.add_edge("extract_issue_details", "ticket_creator", "success")
builder.add_edge("ticket_creator", "ticket_router", "success")

builder.add_edge("support_classifier", "extract_ticket_info", "escalate")
builder.add_edge("extract_ticket_info", "extract_escalation_details", "success")
builder.add_edge("extract_escalation_details", "ticket_escalator", "success")

builder.add_edge("support_classifier", "extract_ticket_info", "resolve")
builder.add_edge("extract_ticket_info", "extract_resolution_details", "success")
builder.add_edge("extract_resolution_details", "ticket_resolver", "success")

builder.set_entrypoints(["support_classifier"])
```

### E-commerce Recommendation System

```python
from intent_kit import DAGBuilder

def get_product_recommendations(category: str, user_preferences: str) -> str:
    return f"Recommendations for {category}: {user_preferences}"

def get_personalized_offers(user_id: str, purchase_history: str) -> str:
    return f"Personalized offers for user {user_id}: {purchase_history}"

def analyze_user_behavior(user_id: str, behavior_data: str) -> str:
    return f"Behavior analysis for user {user_id}: {behavior_data}"

def combine_recommendations(products: str, offers: str, insights: str) -> str:
    return f"Combined recommendations: {products}, {offers}, {insights}"

# Create recommendation DAG
builder = DAGBuilder()

# Main classifier
builder.add_node("recommendation_classifier", "classifier",
                 output_labels=["products", "offers", "insights", "combined"],
                 description="Classify recommendation requests")

# Shared user extractor
builder.add_node("extract_user", "extractor",
                 param_schema={"user_id": str},
                 description="Extract user information")

# Specific extractors
builder.add_node("extract_preferences", "extractor",
                 param_schema={"category": str, "user_preferences": str},
                 description="Extract user preferences")

builder.add_node("extract_purchase_history", "extractor",
                 param_schema={"user_id": str, "purchase_history": str},
                 description="Extract purchase history")

builder.add_node("extract_behavior", "extractor",
                 param_schema={"user_id": str, "behavior_data": str},
                 description="Extract behavior data")

# Actions
builder.add_node("product_recommender", "action",
                 action=get_product_recommendations,
                 description="Get product recommendations")

builder.add_node("offer_generator", "action",
                 action=get_personalized_offers,
                 description="Generate personalized offers")

builder.add_node("behavior_analyzer", "action",
                 action=analyze_user_behavior,
                 description="Analyze user behavior")

builder.add_node("recommendation_combiner", "action",
                 action=combine_recommendations,
                 description="Combine all recommendations")

# Connect recommendation flow
builder.add_edge("recommendation_classifier", "extract_user", "products")
builder.add_edge("extract_user", "extract_preferences", "success")
builder.add_edge("extract_preferences", "product_recommender", "success")

builder.add_edge("recommendation_classifier", "extract_user", "offers")
builder.add_edge("extract_user", "extract_purchase_history", "success")
builder.add_edge("extract_purchase_history", "offer_generator", "success")

builder.add_edge("recommendation_classifier", "extract_user", "insights")
builder.add_edge("extract_user", "extract_behavior", "success")
builder.add_edge("extract_behavior", "behavior_analyzer", "success")

# Combined recommendations
builder.add_edge("recommendation_classifier", "extract_user", "combined")
builder.add_edge("extract_user", "extract_preferences", "success")
builder.add_edge("extract_preferences", "product_recommender", "success")
builder.add_edge("product_recommender", "recommendation_combiner", "success")

builder.add_edge("extract_user", "extract_purchase_history", "success")
builder.add_edge("extract_purchase_history", "offer_generator", "success")
builder.add_edge("offer_generator", "recommendation_combiner", "success")

builder.add_edge("extract_user", "extract_behavior", "success")
builder.add_edge("extract_behavior", "behavior_analyzer", "success")
builder.add_edge("behavior_analyzer", "recommendation_combiner", "success")

builder.set_entrypoints(["recommendation_classifier"])
```

## Best Practices

### 1. Node Naming

```python
# Use descriptive, consistent naming
builder.add_node("user_authentication_classifier", "classifier", ...)
builder.add_node("extract_user_credentials", "extractor", ...)
builder.add_node("validate_user_credentials", "action", ...)
```

### 2. Error Handling

```python
# Always include error handling paths
builder.add_node("data_processor", "classifier",
                 output_labels=["success", "error", "retry"],
                 description="Process data with error handling")
```

### 3. Context Management

```python
# Use context to pass data between nodes
context = DefaultContext()
context.set("user_id", "user123")
context.set("session_id", "session456")

result = dag.execute("Process my request", context)
```

### 4. Performance Optimization

```python
# Use shared nodes for common operations
builder.add_node("shared_text_processor", "extractor",
                 param_schema={"text": str},
                 description="Shared text processing")
```

### 5. Testing

```python
# Test each path in your DAG
test_cases = [
    ("Hello Alice", "greet"),
    ("What's the weather in New York?", "weather"),
    ("Book a flight to Paris", "booking")
]

for input_text, expected_intent in test_cases:
    result = dag.execute(input_text, context)
    assert result.data is not None
```
