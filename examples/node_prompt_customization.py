"""
Example demonstrating node-level prompt customization.

This example shows how to use custom prompts for both handler nodes (argument extraction)
and classifier nodes (intent classification).

WARNING: This is an advanced feature. Use default prompts for most use cases.
"""

from intent_kit.builder import handler, llm_classifier
from intent_kit.builder import IntentGraphBuilder

# Example LLM configuration (replace with your actual config)
LLM_CONFIG = {
    "provider": "openai",
    "api_key": "your-api-key-here",
    "model": "gpt-4"
}


def basic_usage_example():
    """Demonstrate basic usage without custom prompts (recommended)."""
    print("=== Basic Usage Example (Recommended) ===")
    
    # Create handlers with default prompts
    greet_handler = handler(
        name="greet",
        description="Greet the user by name",
        handler_func=lambda name: f"Hello {name}!",
        param_schema={"name": str},
        llm_config=LLM_CONFIG
    )
    
    calc_handler = handler(
        name="calculate",
        description="Perform basic arithmetic",
        handler_func=lambda a, b, operation: f"Result: {eval(f'{a} {operation} {b}')}",
        param_schema={"a": int, "b": int, "operation": str},
        llm_config=LLM_CONFIG
    )
    
    # Create classifier with default prompts
    classifier = llm_classifier(
        name="root",
        children=[greet_handler, calc_handler],
        llm_config=LLM_CONFIG
    )
    
    print("✅ Basic usage created successfully")
    print("   - Uses default prompts (recommended)")
    print("   - Optimized for performance and reliability")
    print()


def advanced_usage_example():
    """Demonstrate advanced usage with custom prompts (expert only)."""
    print("=== Advanced Usage Example (Expert Only) ===")
    
    # Create handlers with custom extraction prompts
    greet_handler = handler(
        name="greet",
        description="Greet the user by name",
        handler_func=lambda name: f"Hello {name}!",
        param_schema={"name": str},
        llm_config=LLM_CONFIG,
        custom_prompts={
            "extraction": """
            You are a specialized name extractor for greeting users.
            
            User Input: {user_input}
            
            Required Parameters:
            {param_descriptions}
            
            {context_info}
            
            Instructions:
            - Extract the person's name from the user input
            - Look for names after words like "hello", "hi", "greet", "call me"
            - If no name is found, use "there" as default
            - Return the result as: "name: [extracted_name]"
            
            Extracted Parameters:
            """
        },
        suppress_warnings=True  # Acknowledge risks to silence warnings
    )
    
    calc_handler = handler(
        name="calculate",
        description="Perform basic arithmetic",
        handler_func=lambda a, b, operation: f"Result: {eval(f'{a} {operation} {b}')}",
        param_schema={"a": int, "b": int, "operation": str},
        llm_config=LLM_CONFIG,
        custom_prompts={
            "extraction": """
            You are a specialized arithmetic parameter extractor.
            
            User Input: {user_input}
            
            Required Parameters:
            {param_descriptions}
            
            {context_info}
            
            Instructions:
            - Extract two numbers and an operation from the user input
            - Supported operations: +, -, *, /, **
            - Look for patterns like "add 5 and 3" or "multiply 10 by 2"
            - Return in format: "a: [first_number]", "b: [second_number]", "operation: [op]"
            
            Extracted Parameters:
            """
        },
        suppress_warnings=True  # Acknowledge risks to silence warnings
    )
    
    # Create classifier with custom classification prompt
    classifier = llm_classifier(
        name="root",
        children=[greet_handler, calc_handler],
        llm_config=LLM_CONFIG,
        custom_prompts={
            "classification": """
            You are a specialized intent classifier for a math and greeting assistant.
            
            User Input: {user_input}
            
            Available Intents:
            {node_descriptions}
            
            {context_info}
            
            Instructions:
            - Classify the user's intent based on the available options
            - Greeting intent: Contains words like "hello", "hi", "greet", "hey"
            - Calculation intent: Contains numbers and math operations
            - Consider the context information when making your decision
            - Return only the number (1-{num_nodes}) corresponding to your choice
            - If no intent matches, return 0
            
            Your choice (number only):
            """
        },
        suppress_warnings=True  # Acknowledge risks to silence warnings
    )
    
    print("⚠️  Advanced usage created successfully")
    print("   - Uses custom prompts (expert only)")
    print("   - May affect performance and reliability")
    print("   - Requires thorough testing")
    print()


def troubleshooting_example():
    """Demonstrate how to troubleshoot custom prompt issues."""
    print("=== Troubleshooting Example ===")
    
    # Example of reverting to default prompts when issues occur
    print("If you experience issues with custom prompts:")
    print()
    print("1. Revert to default prompts:")
    print("   # Remove custom_prompts parameter")
    print("   handler = handler(")
    print("       name='test',")
    print("       description='Test handler',")
    print("       handler_func=lambda x: x,")
    print("       param_schema={'x': str},")
    print("       llm_config=LLM_CONFIG")
    print("       # No custom_prompts parameter")
    print("   )")
    print()
    print("2. Test with defaults to verify the issue persists")
    print("3. Report issues with context about prompt usage")
    print()


def main():
    """Run all examples."""
    print("Node-Level Prompt Customization Examples")
    print("=" * 50)
    print()
    
    basic_usage_example()
    advanced_usage_example()
    troubleshooting_example()
    
    print("For more information, see docs/node_prompt_customization.md")


if __name__ == "__main__":
    main()