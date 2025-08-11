"""
Report utilities for generating formatted performance and cost reports.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
from intent_kit.nodes.types import ExecutionResult


@dataclass
class ReportData:
    """Data structure for report generation."""

    timings: List[Tuple[str, float]]
    successes: List[bool]
    costs: List[float]
    outputs: List[str]
    models_used: List[str]
    providers_used: List[str]
    input_tokens: List[int]
    output_tokens: List[int]
    llm_config: dict
    test_inputs: List[str]


def format_cost(cost: float) -> str:
    """Format cost with appropriate precision and currency symbol."""
    if cost == 0.0:
        return "$0.00"
    elif cost < 0.000001:
        return f"${cost:.8f}"
    elif cost < 0.01:
        return f"${cost:.6f}"
    elif cost < 1.0:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"


def format_tokens(tokens: int) -> str:
    """Format token count with commas for readability."""
    return f"{tokens:,}"


def generate_performance_report(data: ReportData) -> str:
    """
    Generate a formatted performance report from the provided data.

    Args:
        data: ReportData object containing all the metrics and data

    Returns:
        Formatted report string
    """
    # Calculate summary statistics
    total_cost = sum(data.costs)
    total_input_tokens = sum(data.input_tokens)
    # Fixed: was using input_tokens
    total_output_tokens = sum(data.output_tokens)
    total_tokens = total_input_tokens + total_output_tokens
    successful_requests = sum(data.successes)
    total_requests = len(data.test_inputs)

    # Generate timing summary table
    timing_table = generate_timing_table(data)

    # Generate summary statistics
    summary_stats = generate_summary_statistics(
        total_requests,
        successful_requests,
        total_cost,
        total_tokens,
        total_input_tokens,
        total_output_tokens,
    )

    # Generate model information
    model_info = generate_model_information(data.llm_config)

    # Generate cost breakdown
    cost_breakdown = generate_cost_breakdown(
        total_input_tokens, total_output_tokens, total_cost
    )

    # Combine all sections
    report = f"""{timing_table}

{summary_stats}

{model_info}

{cost_breakdown}"""

    return report


def generate_timing_table(data: ReportData) -> str:
    """Generate the timing summary table."""
    lines = []
    lines.append("Timing Summary:")
    lines.append(
        f"  {'Input':<25} | {'Elapsed (sec)':>12} | {'Success':>7} | {'Cost':>10} | {'Model':<35} | {'Provider':<10} | {'Tokens (in/out)':<15} | {'Output':<20}"
    )
    lines.append("  " + "-" * 150)

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
        data.timings,
        data.successes,
        data.costs,
        data.outputs,
        data.models_used,
        data.providers_used,
        data.input_tokens,
        data.output_tokens,
    ):
        elapsed_str = f"{elapsed:11.4f}" if elapsed is not None else "     N/A   "
        cost_str = format_cost(cost)
        model_str = model[:35] if len(model) <= 35 else model[:32] + "..."
        provider_str = provider[:10] if len(provider) <= 10 else provider[:7] + "..."
        tokens_str = f"{format_tokens(in_toks)}/{format_tokens(out_toks)}"

        # Truncate input and output if too long
        input_str = label[:25] if len(label) <= 25 else label[:22] + "..."
        output_str = (
            str(output)[:20] if len(str(output)) <= 20 else str(output)[:17] + "..."
        )

        lines.append(
            f"  {input_str:<25} | {elapsed_str:>12} | {str(success):>7} | {cost_str:>10} | {model_str:<35} | {provider_str:<10} | {tokens_str:<15} | {output_str:<20}"
        )

    return "\n".join(lines)


def generate_summary_statistics(
    total_requests: int,
    successful_requests: int,
    total_cost: float,
    total_tokens: int,
    total_input_tokens: int,
    total_output_tokens: int,
) -> str:
    """Generate summary statistics section."""
    lines = []
    lines.append("=" * 150)
    lines.append("SUMMARY STATISTICS:")
    lines.append(f"  Total Requests: {total_requests}")
    lines.append(
        f"  Successful Requests: {successful_requests} ({successful_requests/total_requests*100:.1f}%)"
    )
    lines.append(f"  Total Cost: {format_cost(total_cost)}")
    lines.append(
        f"  Average Cost per Request: {format_cost(total_cost/total_requests)}"
    )

    if total_tokens > 0:
        lines.append(
            f"  Total Tokens: {format_tokens(total_tokens)} ({format_tokens(total_input_tokens)} in, {format_tokens(total_output_tokens)} out)"
        )
        lines.append(
            f"  Cost per 1K Tokens: {format_cost(total_cost/(total_tokens/1000))}"
        )
        lines.append(f"  Cost per Token: {format_cost(total_cost/total_tokens)}")

    if total_cost > 0:
        lines.append(
            f"  Cost per Successful Request: {format_cost(total_cost/successful_requests) if successful_requests > 0 else '$0.00'}"
        )
        if total_tokens > 0:
            efficiency = (total_tokens / total_requests) / (
                total_cost * 1000
            )  # tokens per dollar per request
            lines.append(
                f"  Efficiency: {efficiency:.1f} tokens per dollar per request"
            )

    return "\n".join(lines)


def generate_model_information(llm_config: dict) -> str:
    """Generate model information section."""
    lines = []
    lines.append("MODEL INFORMATION:")
    lines.append(f"  Primary Model: {llm_config['model']}")
    lines.append(f"  Provider: {llm_config['provider']}")
    return "\n".join(lines)


def generate_cost_breakdown(
    total_input_tokens: int, total_output_tokens: int, total_cost: float
) -> str:
    """Generate cost breakdown section."""
    lines = []

    # Display cost breakdown if we have token information
    if total_input_tokens > 0 or total_output_tokens > 0:
        lines.append("COST BREAKDOWN:")
        lines.append(f"  Input Tokens: {format_tokens(total_input_tokens)}")
        lines.append(f"  Output Tokens: {format_tokens(total_output_tokens)}")
        lines.append(f"  Total Cost: {format_cost(total_cost)}")

    return "\n".join(lines)


def generate_detailed_view(
    data: ReportData, execution_results: list, perf_info: str = ""
) -> str:
    """
    Generate a detailed view showing execution results first, followed by summary.

    Args:
        data: ReportData object containing all the metrics and data
        execution_results: List of execution result details to display
        perf_info: Performance information string (e.g., "simple_demo.py run time: 14.189 seconds elapsed")

    Returns:
        Formatted detailed view string
    """
    lines = ["Performance Report:"]

    # Add execution results first
    for i, result in enumerate(execution_results):
        if i > 0:
            lines.append("")  # Add spacing between results

        # Add intent and output info
        if result.get("node_name"):
            lines.append(f"Intent: {result['node_name']}")
        if result.get("output") is not None:
            lines.append(f"Output: {result['output']}")
        if result.get("cost") is not None:
            lines.append(f"Cost: {format_cost(result['cost'])}")

        # Add token information if available
        input_tokens = result.get("input_tokens", 0)
        output_tokens = result.get("output_tokens", 0)
        if input_tokens > 0 or output_tokens > 0:
            lines.append(
                f"Tokens: {format_tokens(input_tokens)} in, {format_tokens(output_tokens)} out"
            )

    # Add performance information
    if perf_info:
        lines.append(perf_info)

    # Add timing information for each input
    for label, elapsed in data.timings:
        if elapsed is not None:
            lines.append(f"{label}: {elapsed:.3f} seconds elapsed")

    lines.append("")  # Add spacing before summary

    # Generate the full performance report
    report = generate_performance_report(data)
    lines.append(report)

    return "\n".join(lines)


def format_execution_results(
    results: List[ExecutionResult],
    llm_config: dict,
    perf_info: str = "",
    timings: Optional[List[Tuple[str, float]]] = None,
) -> str:
    """
    Generate a formatted report from a list of ExecutionResult objects.

    Args:
        results: List of ExecutionResult objects
        llm_config: LLM configuration dictionary
        perf_info: Performance information string (e.g., "simple_demo.py run time: 14.189 seconds elapsed")
        timings: Optional list of (input, elapsed_time) tuples. If not provided, will use result.duration

    Returns:
        Formatted report string
    """
    if not results:
        return "No execution results to report."

    # Extract data from ExecutionResult objects
    timing_data = []
    successes = []
    costs = []
    outputs = []
    models_used = []
    providers_used = []
    input_tokens = []
    output_tokens = []
    test_inputs = []
    execution_results = []

    for i, result in enumerate(results):
        # Extract timing info (use provided timings if available, otherwise use duration)
        if timings and i < len(timings):
            elapsed = timings[i][1]
        else:
            elapsed = result.duration or 0.0
        timing_data.append((result.input, elapsed))

        # Extract success status
        successes.append(result.success)

        # Extract cost
        cost = result.cost or 0.0
        costs.append(cost)

        # Extract output
        output = result.output if result.success else f"Error: {result.error}"
        outputs.append(str(output) if output is not None else "")

        # Extract model and provider info
        model_used = result.model or llm_config.get("model", "unknown")
        provider_used = result.provider or llm_config.get("provider", "unknown")
        models_used.append(model_used)
        providers_used.append(provider_used)

        # Extract token counts
        in_tokens = result.input_tokens or 0
        out_tokens = result.output_tokens or 0
        input_tokens.append(in_tokens)
        output_tokens.append(out_tokens)

        # Store test input
        test_inputs.append(result.input)

        # Build execution result dict for detailed view
        execution_result = {
            "success": result.success,
            "node_name": result.node_name,
            "node_path": result.node_path or ["unknown"],
            "node_type": result.node_type.name if result.node_type else "ACTION",
            "input": result.input,
            "output": result.output,
            "total_tokens": (result.input_tokens or 0) + (result.output_tokens or 0),
            "input_tokens": result.input_tokens or 0,
            "output_tokens": result.output_tokens or 0,
            "cost": result.cost or 0.0,
            "provider": result.provider,
            "model": result.model,
            "error": result.error,
            "params": result.params or {},
            "children_results": result.children_results or [],
            "duration": result.duration or 0.0,
        }
        execution_results.append(execution_result)

    # Create ReportData
    data = ReportData(
        timings=timing_data,
        successes=successes,
        costs=costs,
        outputs=outputs,
        models_used=models_used,
        providers_used=providers_used,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        llm_config=llm_config,
        test_inputs=test_inputs,
    )

    # Generate the detailed view with execution results
    return generate_detailed_view(data, execution_results, perf_info)
