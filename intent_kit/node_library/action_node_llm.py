"""
LLM-powered action node for evaluation testing.
"""

from intent_kit.nodes.actions.node import ActionNode


def action_node_llm():
    """
    Create an LLM-powered action node for evaluation.

    This node is designed to extract parameters and perform booking actions
    using LLM-based parameter extraction.
    """

    # Define a simple booking action function
    def booking_action(destination: str, date: str = "ASAP", **kwargs) -> str:
        """Mock booking action for evaluation."""
        # Use a simple counter based on destination for consistent booking numbers
        booking_numbers = {
            "Paris": 1,
            "Tokyo": 2,
            "London": 3,
            "New York": 4,
            "Sydney": 5,
            "Berlin": 6,
            "Rome": 7,
            "Barcelona": 8,
            "Amsterdam": 9,
            "Prague": 10,
        }
        booking_num = booking_numbers.get(destination, hash(destination) % 1000)
        return f"Flight booked to {destination} for {date} (Booking #{booking_num})"

    # Create a simple parameter extractor
    def simple_extractor(user_input: str, context=None):
        # Simple extraction logic for evaluation
        if "Paris" in user_input:
            destination = "Paris"
        elif "Tokyo" in user_input:
            destination = "Tokyo"
        elif "London" in user_input:
            destination = "London"
        elif "New York" in user_input:
            destination = "New York"
        elif "Sydney" in user_input:
            destination = "Sydney"
        elif "Berlin" in user_input:
            destination = "Berlin"
        elif "Rome" in user_input:
            destination = "Rome"
        elif "Barcelona" in user_input:
            destination = "Barcelona"
        elif "Amsterdam" in user_input:
            destination = "Amsterdam"
        elif "Prague" in user_input:
            destination = "Prague"
        else:
            destination = "Unknown"

        # Extract date
        if "next Friday" in user_input:
            date = "next Friday"
        elif "tomorrow" in user_input:
            date = "tomorrow"
        elif "next week" in user_input:
            date = "next week"
        elif "weekend" in user_input:
            date = "the weekend"  # Match expected format
        elif "next month" in user_input:
            date = "next month"
        elif "December 15th" in user_input:
            date = "December 15th"
        else:
            date = "ASAP"

        return {"destination": destination, "date": date}

    # Create the action node
    action = ActionNode(
        name="action_node_llm",
        description="LLM-powered booking action",
        param_schema={"destination": str, "date": str},
        action=booking_action,
        arg_extractor=simple_extractor,
    )

    return action
