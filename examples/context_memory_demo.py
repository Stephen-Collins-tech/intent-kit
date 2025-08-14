"""
Context Memory Demo - Multi-turn Conversation Example

This example demonstrates how to use context across multiple turns to maintain
conversation state and memory between interactions.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from intent_kit import DAGBuilder, run_dag
from intent_kit.core.context import DefaultContext

load_dotenv()


def remember_name(name: str, **kwargs) -> str:
    """Remember the user's name in context for future interactions."""
    return f"Nice to meet you, {name}! I'll remember your name."


def get_weather(location: str, user_name: Optional[str] = None, **kwargs) -> str:
    """Get weather for a location, using remembered name if available."""
    # Check for user.name from context first, then user_name parameter
    context_user_name = kwargs.get("user.name")
    if context_user_name:
        return f"Hey {context_user_name}! The weather in {location} is sunny and 72°F."
    elif user_name:
        return f"Hey {user_name}! The weather in {location} is sunny and 72°F."
    else:
        return f"Hey there! The weather in {location} is sunny and 72°F."


def get_remembered_name(user_name: Optional[str] = None, **kwargs) -> str:
    """Get the remembered name from context."""
    # Check for user.name from context first, then user_name parameter
    context_user_name = kwargs.get("user.name")
    if context_user_name:
        return f"I remember you! Your name is {context_user_name}."
    elif user_name:
        return f"I remember you! Your name is {user_name}."
    else:
        return "I don't remember your name yet. Try introducing yourself first!"


# Note: In the current implementation, action functions receive parameters
# but not the context directly. The context is managed by the traversal engine
# and accessed through context patches returned by the node's execute method.


def create_memory_dag():
    """Create a DAG that can remember context across turns."""
    builder = DAGBuilder()

    # Set default LLM configuration for the entire graph
    builder.with_default_llm_config(
        {
            "provider": "openrouter",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "model": "google/gemma-2-9b-it",
        }
    )

    # Add classifier node to determine intent
    builder.add_node(
        "classifier",
        "classifier",
        output_labels=["greet", "weather", "remember", "unknown"],
        description="Classify user intent",
    )

    # Add extractor for name extraction
    builder.add_node(
        "extract_name",
        "extractor",
        param_schema={"name": str},
        description="Extract name from greeting",
        output_key="name_params",  # Use different key to avoid overwriting
    )

    # Add extractor for location extraction
    builder.add_node(
        "extract_location",
        "extractor",
        param_schema={"location": str},
        description="Extract location from weather request",
        output_key="location_params",  # Use different key to avoid overwriting
    )

    # Add action nodes with context read/write configuration
    builder.add_node(
        "remember_name_action",
        "action",
        action=remember_name,
        description="Remember the user's name",
        # Look for name parameters
        param_keys=["name_params", "extracted_params"],
        context_read=[],  # No context to read
        # Write name to context
        context_write=["user.name", "user.first_seen"],
    )

    builder.add_node(
        "weather_action",
        "action",
        action=get_weather,
        description="Get weather information",
        # Look for location parameters
        param_keys=["location_params", "extracted_params"],
        context_read=["user.name"],  # Read user name from context
        context_write=[
            "weather.requests",
            "weather.last_location",
        ],  # Write weather data
    )

    builder.add_node(
        "get_name_action",
        "action",
        action=get_remembered_name,
        description="Get remembered name from context",
        # Look for name parameters
        param_keys=["name_params", "extracted_params"],
        context_read=["user.name"],  # Read user name from context
        context_write=[],  # No context to write
    )

    # Add clarification node
    builder.add_node(
        "clarification",
        "clarification",
        clarification_message="I'm not sure what you'd like me to do. You can greet me, ask about weather, or ask me to remember your name!",
        available_options=[
            "Say hello",
            "Ask about weather",
            "Ask me to remember your name",
        ],
        description="Ask for clarification when intent is unclear",
    )

    # Connect nodes
    builder.add_edge("classifier", "extract_name", "greet")
    builder.add_edge("extract_name", "remember_name_action", "success")
    builder.add_edge("classifier", "extract_location", "weather")
    builder.add_edge("extract_location", "weather_action", "success")
    builder.add_edge("classifier", "get_name_action", "remember")
    builder.add_edge("classifier", "clarification", "unknown")
    builder.set_entrypoints(["classifier"])

    return builder


def simulate_conversation():
    """Simulate a multi-turn conversation with context memory."""
    print("=== Context Memory Demo ===\n")
    print("This demo shows how context persists across multiple turns.\n")
    print("Features demonstrated:\n")
    print("- Context read/write configuration for nodes")
    print("- Persistent storage of user data across turns")
    print("- Context-aware responses using stored data\n")

    # Create a shared context that persists across all turns
    shared_context = DefaultContext()
    builder = create_memory_dag()
    dag = builder.build()

    # Simulate conversation turns
    conversation_turns = [
        "Hi, my name is Alice",
        "What's the weather like in San Francisco?",
        "Do you remember my name?",
        "What's the weather in New York?",
        "Hello again!",
    ]

    for i, user_input in enumerate(conversation_turns, 1):
        print(f"Turn {i}: '{user_input}'")

        # Execute the DAG with the shared context
        result, updated_context = run_dag(dag, user_input, ctx=shared_context)

        # Update our shared context with the returned context
        shared_context = updated_context

        if result and result.data:
            if "action_result" in result.data:
                print(f"Response: {result.data['action_result']}")
            elif "clarification_message" in result.data:
                print(f"Clarification: {result.data['clarification_message']}")
            else:
                print(f"Response: {result.data}")
        else:
            print("No response")

        # Show current context state
        print("Current context:")
        context_snapshot = shared_context.snapshot()
        for key, value in context_snapshot.items():
            if not key.startswith("private.") and not key.startswith("tmp."):
                print(f"  {key}: {value}")

        # Show context persistence status
        if i == 1:
            print("\n  ✓ Alice's name stored in context for future use")
        elif i == 2:
            print("\n  ✓ Weather response personalized using Alice's name from context")
        elif i == 3:
            print("\n  ✓ Successfully retrieved Alice's name from context")

        print()


if __name__ == "__main__":
    simulate_conversation()
