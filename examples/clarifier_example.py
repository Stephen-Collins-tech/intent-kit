"""
Example demonstrating the use of Clarifier nodes in a booking system.

This example shows how Clarifier nodes can be used to handle ambiguous
user input and request clarification when needed.
"""







def book_flight(destination: str, date: str, time: str = "any") -> str:
    """Book a flight with the given parameters."""
    return f"Flight booked to {destination} on {date} at {time}"


def book_hotel(
    location: str, check_in: str, check_out: str, room_type: str = "standard"
) -> str:
    """Book a hotel with the given parameters."""
    return (
        f"Hotel booked in {location} from {check_in} to {check_out}, {room_type} room"
    )


def book_restaurant(name: str, date: str, time: str, party_size: int = 2) -> str:
    """Book a restaurant reservation."""
    return (
        f"Restaurant reservation at {name} on {date} at {time} for {party_size} people"
    )


def create_booking_graph():
    """Create an intent graph with Clarifier nodes for a booking system."""

    # Create action nodes
    flight_action = action(
        name="book_flight",
        description="Books flights",
        action_func=book_flight,
        param_schema={"destination": str, "date": str, "time": str},
    )

    hotel_action = action(
        name="book_hotel",
        description="Books hotels",
        action_func=book_hotel,
        param_schema={
            "location": str,
            "check_in": str,
            "check_out": str,
            "room_type": str,
        },
    )

    restaurant_action = action(
        name="book_restaurant",
        description="Books restaurant reservations",
        action_func=book_restaurant,
        param_schema={"name": str, "date": str, "time": str, "party_size": int},
    )

    # Create regular Clarifier nodes for different booking types
    flight_clarifier = clarifier(
        name="flight_clarifier",
        clarification_prompt="I need more details about your flight booking. Your request '{input}' is unclear.",
        expected_response_format="Please specify: [destination] [date] [time (optional)]",
        max_clarification_attempts=3,
        description="Clarifies flight booking requests",
    )

    hotel_clarifier = clarifier(
        name="hotel_clarifier",
        clarification_prompt="I need more details about your hotel booking. Your request '{input}' is unclear.",
        expected_response_format="Please specify: [location] [check-in date] [check-out date] [room type (optional)]",
        max_clarification_attempts=3,
        description="Clarifies hotel booking requests",
    )

    restaurant_clarifier = clarifier(
        name="restaurant_clarifier",
        clarification_prompt="I need more details about your restaurant reservation. Your request '{input}' is unclear.",
        expected_response_format="Please specify: [restaurant name] [date] [time] [party size (optional)]",
        max_clarification_attempts=3,
        description="Clarifies restaurant reservation requests",
    )

    # Create LLM-powered Clarifier nodes for smart clarification
    smart_booking_clarifier = llm_clarifier(
        name="smart_booking_clarifier",
        llm_config={"provider": "openrouter", "model": "google/gemma-3-27b-it"},
        expected_response_format="Please specify: [type] [details] [date] [time]",
        max_clarification_attempts=3,
        description="Smart LLM-powered clarifier for booking requests",
    )

    smart_flight_clarifier = llm_clarifier(
        name="smart_flight_clarifier",
        llm_config={"provider": "openrouter", "model": "google/gemma-3-27b-it"},
        clarification_prompt_template="""You are a travel booking assistant. The user wants to book a flight but their request is unclear.

User Input: {user_input}
{context_info}

Generate a helpful clarification prompt that:
1. Acknowledges their intent to book a flight
2. Identifies what specific information is missing (destination, date, time, etc.)
3. Asks for the missing details in a friendly way
4. Provides guidance on the expected format

Expected Response Format: {expected_format}
Maximum Clarification Attempts: {max_attempts}

Clarification Prompt:""",
        expected_response_format="Please specify: [destination] [date] [time] [preferences]",
        max_clarification_attempts=3,
        description="Smart LLM-powered clarifier for flight bookings",
    )

    # Create a simple classifier function
    def booking_classifier(user_input: str, children, context=None):
        """Simple classifier that routes to appropriate nodes based on keywords."""
        input_lower = user_input.lower()

        if "flight" in input_lower or "fly" in input_lower:
            return flight_action
        elif "hotel" in input_lower or "accommodation" in input_lower:
            return hotel_action
        elif (
            "restaurant" in input_lower
            or "dinner" in input_lower
            or "lunch" in input_lower
        ):
            return restaurant_action
        else:
            # If unclear, return the appropriate clarifier based on context
            # For this example, we'll use a simple heuristic
            if any(word in input_lower for word in ["book", "reserve", "make"]):
                return flight_clarifier  # Default to flight clarifier
            return flight_clarifier

    # Create the graph


    graph = IntentGraph(
        root_nodes=[
            flight_action,
            hotel_action,
            restaurant_action,
            flight_clarifier,
            hotel_clarifier,
            restaurant_clarifier,
            smart_booking_clarifier,
            smart_flight_clarifier,
        ]
    )

    return graph


def demonstrate_clarifier_usage():
    """Demonstrate how Clarifier nodes work in practice."""

    print("=== Clarifier Node Example ===\n")

    # Create the booking graph
    graph = create_booking_graph()

    # Test cases with ambiguous input
    test_cases = [
        "book something",
        "I want to book",
        "make a reservation",
        "book a flight",  # Still ambiguous - needs destination and date
        "book a hotel",  # Still ambiguous - needs location and dates
    ]

    for i, user_input in enumerate(test_cases, 1):
        print(f"Test {i}: User says: '{user_input}'")

        # Route the input through the graph
        result = graph.route(user_input, debug=True)

        # Check if clarification is needed
        if result.success is False and result.children_results:
            clarifier_result = result.children_results[0]
            if clarifier_result.node_type == NodeType.CLARIFY:
                print("  → Clarification needed!")
                print(f"  → Clarifier node: {clarifier_result.node_name}")
                print(
                    f"  → Message: {clarifier_result.output['clarification_message']}"
                )

                # Simulate user providing clarification
                clarification_response = "book a flight to Paris on March 15th"
                print(f"  → User clarifies: '{clarification_response}'")

                # Handle the clarification response
                context = IntentContext()
                clarifier_node = graph.root_nodes[3]  # flight_clarifier
                response = clarifier_node.handle_clarification_response(
                    clarification_response, context
                )

                if response["success"]:
                    print("  → Clarification successful!")
                    print(f"  → Clarified input: '{response['clarified_input']}'")
                    print(f"  → Attempts: {response['attempts']}")

                    # Now route the clarified input
                    clarified_result = graph.route(
                        response["clarified_input"], debug=True
                    )
                    if clarified_result.success:
                        print(f"  → Final result: {clarified_result.output}")
                    else:
                        print(
                            f"  → Still needs processing: {clarified_result.error.message if clarified_result.error else 'Unknown error'}"
                        )
                else:
                    print(f"  → Clarification failed: {response['error']}")
            else:
                print(
                    f"  → No clarification needed, but execution failed: {clarifier_result.error.message if clarifier_result.error else 'Unknown error'}"
                )
        else:
            print(f"  → Direct execution successful: {result.output}")

        print()


def demonstrate_clarifier_with_context():
    """Demonstrate Clarifier nodes with context management."""

    print("=== Clarifier Node with Context Example ===\n")

    # Create a clarifier node
    clarifier_node = clarifier(
        name="booking_clarifier",
        clarification_prompt="Your booking request '{input}' is unclear. Please provide more details.",
        expected_response_format="Please specify: [type] [details]",
        max_clarification_attempts=2,
    )

    # Create context
    context = IntentContext()

    # Execute clarifier with ambiguous input
    print("1. User provides ambiguous input: 'book something'")
    result = clarifier_node.execute("book something", context=context)

    print(f"   Clarification message: {result.output['clarification_message']}")

    # Check context
    clarification_context = context.get("clarification_context")
    print(f"   Context stored: {clarification_context}")

    # Handle first clarification response
    print("\n2. User provides first clarification: 'book a flight'")
    response1 = clarifier_node.handle_clarification_response("book a flight", context)
    print(f"   Response: {response1}")

    # Handle second clarification response
    print("\n3. User provides second clarification: 'book a flight to Paris'")
    response2 = clarifier_node.handle_clarification_response(
        "book a flight to Paris", context
    )
    print(f"   Response: {response2}")

    # Try third clarification (should fail due to max attempts)
    print("\n4. User provides third clarification: 'book a flight to Paris tomorrow'")
    response3 = clarifier_node.handle_clarification_response(
        "book a flight to Paris tomorrow", context
    )
    print(f"   Response: {response3}")

    print()


def demonstrate_llm_clarifier():
    """Demonstrate LLM-powered Clarifier nodes."""

    print("=== LLM Clarifier Node Example ===\n")

    # Create an LLM clarifier with custom prompt
    smart_clarifier = llm_clarifier(
        name="smart_booking_clarifier",
        llm_config={"provider": "openrouter", "model": "google/gemma-3-27b-it"},
        clarification_prompt_template="""You are a helpful travel booking assistant. The user's request is unclear and needs clarification.

User Input: {user_input}
{context_info}

Generate a helpful clarification prompt that:
1. Acknowledges their intent to make a booking
2. Identifies what specific information is missing
3. Asks for the missing details in a friendly, helpful way
4. Provides guidance on the expected format

Expected Response Format: {expected_format}
Maximum Clarification Attempts: {max_attempts}

Clarification Prompt:""",
        expected_response_format="Please specify: [type] [destination] [date] [time] [preferences]",
        max_clarification_attempts=3,
        description="Smart LLM-powered clarifier for travel bookings",
    )

    print("LLM Clarifier created:")
    print(f"  Node name: {smart_clarifier.name}")
    print(f"  Node type: {smart_clarifier.node_type}")
    print(f"  Expected format: {smart_clarifier.expected_response_format}")
    print(f"  Max attempts: {smart_clarifier.max_clarification_attempts}")

    # Test with context
    context = IntentContext()
    context.set("user_preferences", "window seat, vegetarian meal")
    context.set("previous_bookings", "Paris, London")

    print("\nTesting LLM clarifier with context:")
    print(f"  User preferences: {context.get('user_preferences')}")
    print(f"  Previous bookings: {context.get('previous_bookings')}")

    # Note: In a real scenario, this would call the actual LLM
    # For this example, we'll just show the structure
    print("\nLLM clarifier would generate contextual clarification based on:")
    print("  - User's unclear input")
    print("  - User preferences and history")
    print("  - Expected response format")
    print("  - Maximum attempts limit")


def demonstrate_json_based_clarifier():
    """Demonstrate creating Clarifier nodes from JSON configuration."""

    print("=== JSON-based Clarifier Node Example ===\n")

    # Define the graph in JSON
    json_graph = {
        "root": "booking_clarifier",
        "intents": {
            "booking_clarifier": {
                "type": "clarifier",
                "name": "booking_clarifier",
                "description": "Clarifies booking requests",
                "clarification_prompt": "Your booking request '{input}' is unclear. Please provide more details.",
                "expected_response_format": "Please specify: [type] [destination] [date] [time]",
                "max_clarification_attempts": 3,
            }
        },
    }

    # Create function registry (empty for clarifier nodes)
    function_registry = {}

    # Build the graph
    builder = IntentGraphBuilder()
    graph = builder.with_json(json_graph).with_functions(function_registry).build()

    print("Graph created from JSON configuration:")
    print(f"  Root nodes: {[node.name for node in graph.root_nodes]}")

    clarifier_node = graph.root_nodes[0]
    print(f"  Clarifier node type: {clarifier_node.node_type}")
    print(f"  Clarification prompt: {clarifier_node.clarification_prompt}")
    print(f"  Expected format: {clarifier_node.expected_response_format}")
    print(f"  Max attempts: {clarifier_node.max_clarification_attempts}")

    # Test the clarifier
    print("\nTesting clarifier with ambiguous input: 'book'")
    result = clarifier_node.execute("book")
    print(f"  Clarification message: {result.output['clarification_message']}")


def demonstrate_json_based_llm_clarifier():
    """Demonstrate creating LLM Clarifier nodes from JSON configuration."""

    print("=== JSON-based LLM Clarifier Node Example ===\n")

    # Define the graph in JSON with LLM clarifier
    json_graph = {
        "root": "smart_booking_clarifier",
        "intents": {
            "smart_booking_clarifier": {
                "type": "llm_clarifier",
                "name": "smart_booking_clarifier",
                "description": "Smart LLM-powered clarifier for booking requests",
                "llm_config": {
                    "provider": "openrouter",
                    "model": "google/gemma-3-27b-it",
                },
                "clarification_prompt_template": "Generate a helpful clarification for: {user_input}",
                "expected_response_format": "Please specify: [type] [details] [date] [time]",
                "max_clarification_attempts": 3,
            }
        },
    }

    # Create function registry (empty for clarifier nodes)
    function_registry = {}

    # Build the graph
    builder = IntentGraphBuilder()
    graph = builder.with_json(json_graph).with_functions(function_registry).build()

    print("Graph created from JSON configuration with LLM clarifier:")
    print(f"  Root nodes: {[node.name for node in graph.root_nodes]}")

    clarifier_node = graph.root_nodes[0]
    print(f"  Clarifier node type: {clarifier_node.node_type}")
    print(f"  Expected format: {clarifier_node.expected_response_format}")
    print(f"  Max attempts: {clarifier_node.max_clarification_attempts}")

    # Test the LLM clarifier
    print("\nTesting LLM clarifier with ambiguous input: 'book'")
    result = clarifier_node.execute("book")
    print(f"  Clarification message: {result.output['clarification_message']}")


if __name__ == "__main__":
    demonstrate_clarifier_usage()
    demonstrate_clarifier_with_context()
    demonstrate_llm_clarifier()
    demonstrate_json_based_clarifier()
    demonstrate_json_based_llm_clarifier()
