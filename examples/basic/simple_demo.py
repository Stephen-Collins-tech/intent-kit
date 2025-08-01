"""
Simple IntentGraph Demo

A minimal demonstration showing how to configure an intent graph with actions and classifiers.
"""

import os
import json
from dotenv import load_dotenv
from intent_kit import IntentGraphBuilder

load_dotenv()

LLM_CONFIG = {
    "provider": "openrouter",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": "moonshotai/kimi-k2",
}


def greet(name, context=None):
    return f"Hello {name}!"


def calculate(operation, a, b, context=None):
    # Simple operation mapping
    if operation == "plus":
        return a + b
    if operation == "minus":
        return a - b
    if operation == "times":
        return a * b
    if operation == "divided":
        return a / b
    if operation == "add":
        return a + b
    if operation == "multiply":
        return a * b
    return None


def weather(location, context=None):
    return f"Weather in {location}: 72°F, Sunny (simulated)"


def help_action(context=None):
    return "I can help with greetings, calculations, and weather!"


function_registry = {
    "greet": greet,
    "calculate": calculate,
    "weather": weather,
    "help_action": help_action,
}


def create_intent_graph():
    # Load the graph definition from local JSON (same directory as script)
    json_path = os.path.join(os.path.dirname(__file__), "simple_demo.json")
    with open(json_path, "r") as f:
        json_graph = json.load(f)

    return (
        IntentGraphBuilder()
        .with_json(json_graph)
        .with_functions(function_registry)
        .with_default_llm_config(LLM_CONFIG)
        .build()
    )


def format_cost(cost: float) -> str:
    """Format cost with appropriate precision and currency symbol."""
    if cost == 0.0:
        return "$0.00"
    elif cost < 0.01:
        return f"${cost:.6f}"
    elif cost < 1.0:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"


def format_tokens(tokens: int) -> str:
    """Format token count with commas for readability."""
    return f"{tokens:,}"


if __name__ == "__main__":
    from intent_kit.context import IntentContext
    from intent_kit.utils.perf_util import PerfUtil

    with PerfUtil("simple_demo.py run time") as perf:
        graph = create_intent_graph()
        context = IntentContext(session_id="simple_demo")

        test_inputs = [
            # "Hello, my name is Alice",
            "What's 15 plus 7?",
            # "Weather in San Francisco",
            # "Help me",
            "Multiply 8 and 3",
        ]

        timings: list[tuple[str, float]] = []
        successes = []
        costs: list[float] = []
        outputs = []
        models_used = []
        providers_used = []
        input_tokens = []
        output_tokens = []

        for user_input in test_inputs:
            with PerfUtil.collect(user_input, timings) as perf:
                result = graph.route(user_input, context=context)
                success = bool(result.success)
                cost = result.cost or 0.0
                costs.append(cost)
                output = result.output if result.success else f"Error: {result.error}"
                outputs.append(output)

                # Extract model and token information
                model_used = result.model or LLM_CONFIG["model"]
                provider_used = result.provider or LLM_CONFIG["provider"]
                models_used.append(model_used)
                providers_used.append(provider_used)

                # Get token counts if available
                in_tokens = result.input_tokens or 0
                out_tokens = result.output_tokens or 0
                input_tokens.append(in_tokens)
                output_tokens.append(out_tokens)

                if result.success:
                    print(f"Intent: {result.node_name}")
                    print(f"Output: {result.output}")
                    print(f"Cost: {format_cost(cost)}")
                    if in_tokens > 0 or out_tokens > 0:
                        print(
                            f"Tokens: {format_tokens(in_tokens)} in, {format_tokens(out_tokens)} out"
                        )
                else:
                    print(f"Error: {result.error}")
                successes.append(success)

    print(perf.format())

    # Print detailed table with enhanced information
    print("\nTiming Summary:")
    print(
        f"  {'Input':<25} | {'Elapsed (sec)':>12} | {'Success':>7} | {'Cost':>10} | {'Model':<35} | {'Provider':<10} | {'Tokens (in/out)':<15} | {'Output':<20}"
    )
    print("  " + "-" * 150)

    for (
        (label, elapsed),
        success,
        cost,
        output,
        model,
        provider,
        in_toks,
        out_toks,
    ) in zip(
        timings,
        successes,
        costs,
        outputs,
        models_used,
        providers_used,
        input_tokens,
        output_tokens,
    ):
        elapsed_str = f" {elapsed:12.4f}" if elapsed is not None else "     N/A   "
        cost_str = format_cost(cost)
        model_str = model[:35] if len(model) <= 35 else model[:32] + "..."
        provider_str = provider[:10] if len(provider) <= 10 else provider[:7] + "..."
        tokens_str = f"{format_tokens(in_toks)}/{format_tokens(out_toks)}"

        # Truncate input and output if too long
        input_str = label[:25] if len(label) <= 25 else label[:22] + "..."
        output_str = (
            str(output)[:20] if len(str(output)) <= 20 else str(output)[:17] + "..."
        )

        print(
            f"  {input_str:<25} | {elapsed_str:>12} | {str(success):>7} | {cost_str:>10} | {model_str:<35} | {provider_str:<10} | {tokens_str:<15} | {output_str:<20}"
        )

    # Print summary statistics
    total_cost = sum(costs)
    total_input_tokens = sum(input_tokens)
    total_output_tokens = sum(output_tokens)
    total_tokens = total_input_tokens + total_output_tokens
    successful_requests = sum(successes)
    total_requests = len(test_inputs)

    print("\n" + "=" * 150)
    print("SUMMARY STATISTICS:")
    print(f"  Total Requests: {total_requests}")
    print(
        f"  Successful Requests: {successful_requests} ({successful_requests/total_requests*100:.1f}%)"
    )
    print(f"  Total Cost: {format_cost(total_cost)}")
    print(f"  Average Cost per Request: {format_cost(total_cost/total_requests)}")

    if total_tokens > 0:
        print(
            f"  Total Tokens: {format_tokens(total_tokens)} ({format_tokens(total_input_tokens)} in, {format_tokens(total_output_tokens)} out)"
        )
        print(f"  Cost per 1K Tokens: {format_cost(total_cost/(total_tokens/1000))}")
        print(f"  Cost per Token: {format_cost(total_cost/total_tokens)}")

    if total_cost > 0:
        print(
            f"  Cost per Successful Request: {format_cost(total_cost/successful_requests) if successful_requests > 0 else '$0.00'}"
        )
        if total_tokens > 0:
            efficiency = (total_tokens / total_requests) / (
                total_cost * 1000
            )  # tokens per dollar per request
            print(f"  Efficiency: {efficiency:.1f} tokens per dollar per request")

    # Show model pricing information
    print("\nMODEL INFORMATION:")
    print(f"  Primary Model: {LLM_CONFIG['model']}")
    print(f"  Provider: {LLM_CONFIG['provider']}")

    # Display cost breakdown if we have token information
    if total_input_tokens > 0 or total_output_tokens > 0:
        print("\nCOST BREAKDOWN:")
        print(f"  Input Tokens: {format_tokens(total_input_tokens)}")
        print(f"  Output Tokens: {format_tokens(total_output_tokens)}")
        print(f"  Total Cost: {format_cost(total_cost)}")
