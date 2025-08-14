"""
Tests for report utilities module.
"""

import pytest
from unittest.mock import Mock
from intent_kit.utils.report_utils import (
    ReportData,
    format_cost,
    format_tokens,
    generate_performance_report,
    generate_timing_table,
    generate_summary_statistics,
    generate_model_information,
    generate_cost_breakdown,
    generate_detailed_view,
    format_execution_results,
)


class TestReportData:
    """Test the ReportData dataclass."""

    def test_report_data_creation(self):
        """Test creating a ReportData instance."""
        data = ReportData(
            timings=[("test1", 1.0), ("test2", 2.0)],
            successes=[True, False],
            costs=[0.01, 0.02],
            outputs=["output1", "output2"],
            models_used=["gpt-4", "gpt-3.5"],
            providers_used=["openai", "openai"],
            input_tokens=[100, 200],
            output_tokens=[50, 100],
            llm_config={"model": "gpt-4", "provider": "openai"},
            test_inputs=["input1", "input2"],
        )
        
        assert len(data.timings) == 2
        assert len(data.successes) == 2
        assert len(data.costs) == 2
        assert data.llm_config["model"] == "gpt-4"


class TestFormatCost:
    """Test the format_cost function."""

    def test_format_cost_zero(self):
        """Test formatting zero cost."""
        assert format_cost(0.0) == "$0.00"

    def test_format_cost_very_small(self):
        """Test formatting very small costs."""
        assert format_cost(0.00000001) == "$0.00000001"

    def test_format_cost_small(self):
        """Test formatting small costs."""
        assert format_cost(0.001) == "$0.001000"

    def test_format_cost_medium(self):
        """Test formatting medium costs."""
        assert format_cost(0.5) == "$0.5000"

    def test_format_cost_large(self):
        """Test formatting large costs."""
        assert format_cost(1.5) == "$1.50"

    def test_format_cost_very_large(self):
        """Test formatting very large costs."""
        assert format_cost(100.123456) == "$100.12"


class TestFormatTokens:
    """Test the format_tokens function."""

    def test_format_tokens_small(self):
        """Test formatting small token counts."""
        assert format_tokens(100) == "100"

    def test_format_tokens_large(self):
        """Test formatting large token counts."""
        assert format_tokens(1000000) == "1,000,000"

    def test_format_tokens_zero(self):
        """Test formatting zero tokens."""
        assert format_tokens(0) == "0"


class TestGenerateTimingTable:
    """Test the generate_timing_table function."""

    def test_generate_timing_table_empty(self):
        """Test generating timing table with empty data."""
        data = ReportData(
            timings=[],
            successes=[],
            costs=[],
            outputs=[],
            models_used=[],
            providers_used=[],
            input_tokens=[],
            output_tokens=[],
            llm_config={"model": "test", "provider": "test"},
            test_inputs=[],
        )
        
        result = generate_timing_table(data)
        assert "Timing Summary:" in result
        assert "Input" in result
        assert "Elapsed (sec)" in result

    def test_generate_timing_table_with_data(self):
        """Test generating timing table with data."""
        data = ReportData(
            timings=[("test_input", 1.5)],
            successes=[True],
            costs=[0.01],
            outputs=["test_output"],
            models_used=["gpt-4"],
            providers_used=["openai"],
            input_tokens=[100],
            output_tokens=[50],
            llm_config={"model": "gpt-4", "provider": "openai"},
            test_inputs=["test_input"],
        )
        
        result = generate_timing_table(data)
        assert "test_input" in result
        assert "1.5000" in result
        assert "True" in result
        assert "$0.01" in result
        assert "gpt-4" in result
        assert "openai" in result
        assert "100/50" in result

    def test_generate_timing_table_long_values(self):
        """Test generating timing table with long values that need truncation."""
        data = ReportData(
            timings=[("very_long_input_name_that_needs_truncation", 1.5)],
            successes=[True],
            costs=[0.01],
            outputs=["very_long_output_that_needs_truncation"],
            models_used=["very_long_model_name_that_needs_truncation"],
            providers_used=["very_long_provider_name"],
            input_tokens=[100],
            output_tokens=[50],
            llm_config={"model": "gpt-4", "provider": "openai"},
            test_inputs=["very_long_input_name_that_needs_truncation"],
        )
        
        result = generate_timing_table(data)
        # Check that long values are truncated
        assert "very_long_input_name_that_needs_truncation" not in result
        assert "very_long_input_name_t..." in result


class TestGenerateSummaryStatistics:
    """Test the generate_summary_statistics function."""

    def test_generate_summary_statistics_basic(self):
        """Test generating basic summary statistics."""
        result = generate_summary_statistics(
            total_requests=10,
            successful_requests=8,
            total_cost=0.05,
            total_tokens=1000,
            total_input_tokens=600,
            total_output_tokens=400,
        )
        
        assert "Total Requests: 10" in result
        assert "Successful Requests: 8 (80.0%)" in result
        assert "Total Cost: $0.0500" in result
        assert "Average Cost per Request: $0.0050" in result
        assert "Total Tokens: 1,000 (600 in, 400 out)" in result
        assert "Cost per 1K Tokens: $0.0500" in result
        assert "Cost per Token: $0.000050" in result

    def test_generate_summary_statistics_zero_tokens(self):
        """Test generating summary statistics with zero tokens."""
        result = generate_summary_statistics(
            total_requests=5,
            successful_requests=3,
            total_cost=0.02,
            total_tokens=0,
            total_input_tokens=0,
            total_output_tokens=0,
        )
        
        assert "Total Requests: 5" in result
        assert "Successful Requests: 3 (60.0%)" in result
        assert "Total Cost: $0.0200" in result
        assert "Average Cost per Request: $0.0040" in result
        # Should not include token-related stats when tokens are 0
        assert "Total Tokens:" not in result
        assert "Cost per 1K Tokens:" not in result

    def test_generate_summary_statistics_zero_cost(self):
        """Test generating summary statistics with zero cost."""
        result = generate_summary_statistics(
            total_requests=5,
            successful_requests=5,
            total_cost=0.0,
            total_tokens=1000,
            total_input_tokens=600,
            total_output_tokens=400,
        )
        
        assert "Total Cost: $0.00" in result
        assert "Average Cost per Request: $0.00" in result
        # When cost is 0, the cost per successful request line is not included
        assert "Cost per Successful Request:" not in result

    def test_generate_summary_statistics_no_successful_requests(self):
        """Test generating summary statistics with no successful requests."""
        result = generate_summary_statistics(
            total_requests=5,
            successful_requests=0,
            total_cost=0.02,
            total_tokens=1000,
            total_input_tokens=600,
            total_output_tokens=400,
        )
        
        assert "Successful Requests: 0 (0.0%)" in result
        assert "Cost per Successful Request: $0.00" in result


class TestGenerateModelInformation:
    """Test the generate_model_information function."""

    def test_generate_model_information(self):
        """Test generating model information."""
        llm_config = {"model": "gpt-4", "provider": "openai"}
        result = generate_model_information(llm_config)
        
        assert "Primary Model: gpt-4" in result
        assert "Provider: openai" in result


class TestGenerateCostBreakdown:
    """Test the generate_cost_breakdown function."""

    def test_generate_cost_breakdown_with_tokens(self):
        """Test generating cost breakdown with token information."""
        result = generate_cost_breakdown(
            total_input_tokens=600,
            total_output_tokens=400,
            total_cost=0.05,
        )
        
        assert "Input Tokens: 600" in result
        assert "Output Tokens: 400" in result
        assert "Total Cost: $0.0500" in result

    def test_generate_cost_breakdown_no_tokens(self):
        """Test generating cost breakdown with no token information."""
        result = generate_cost_breakdown(
            total_input_tokens=0,
            total_output_tokens=0,
            total_cost=0.0,
        )
        
        # Should return empty string when no tokens
        assert result == ""


class TestGeneratePerformanceReport:
    """Test the generate_performance_report function."""

    def test_generate_performance_report(self):
        """Test generating a complete performance report."""
        data = ReportData(
            timings=[("test1", 1.0), ("test2", 2.0)],
            successes=[True, False],
            costs=[0.01, 0.02],
            outputs=["output1", "output2"],
            models_used=["gpt-4", "gpt-4"],
            providers_used=["openai", "openai"],
            input_tokens=[100, 200],
            output_tokens=[50, 100],
            llm_config={"model": "gpt-4", "provider": "openai"},
            test_inputs=["test1", "test2"],
        )
        
        result = generate_performance_report(data)
        
        # Check that all sections are present
        assert "Timing Summary:" in result
        assert "SUMMARY STATISTICS:" in result
        assert "MODEL INFORMATION:" in result
        assert "COST BREAKDOWN:" in result
        
        # Check specific content
        assert "test1" in result
        assert "test2" in result
        assert "Total Requests: 2" in result
        assert "Successful Requests: 1 (50.0%)" in result
        assert "Primary Model: gpt-4" in result
        assert "Provider: openai" in result


class TestGenerateDetailedView:
    """Test the generate_detailed_view function."""

    def test_generate_detailed_view(self):
        """Test generating a detailed view."""
        data = ReportData(
            timings=[("test1", 1.0)],
            successes=[True],
            costs=[0.01],
            outputs=["output1"],
            models_used=["gpt-4"],
            providers_used=["openai"],
            input_tokens=[100],
            output_tokens=[50],
            llm_config={"model": "gpt-4", "provider": "openai"},
            test_inputs=["test1"],
        )
        
        execution_results = [
            {
                "node_name": "test_node",
                "output": "test_output",
                "cost": 0.01,
                "input_tokens": 100,
                "output_tokens": 50,
            }
        ]
        
        result = generate_detailed_view(data, execution_results, "Performance info")
        
        assert "Performance Report:" in result
        assert "Intent: test_node" in result
        assert "Output: test_output" in result
        assert "Cost: $0.01" in result
        assert "Tokens: 100 in, 50 out" in result
        assert "Performance info" in result
        assert "test1: 1.000 seconds elapsed" in result

    def test_generate_detailed_view_no_perf_info(self):
        """Test generating detailed view without performance info."""
        data = ReportData(
            timings=[("test1", 1.0)],
            successes=[True],
            costs=[0.01],
            outputs=["output1"],
            models_used=["gpt-4"],
            providers_used=["openai"],
            input_tokens=[100],
            output_tokens=[50],
            llm_config={"model": "gpt-4", "provider": "openai"},
            test_inputs=["test1"],
        )
        
        execution_results = [
            {
                "node_name": "test_node",
                "output": "test_output",
                "cost": 0.01,
            }
        ]
        
        result = generate_detailed_view(data, execution_results)
        
        assert "Performance Report:" in result
        assert "Intent: test_node" in result
        assert "Output: test_output" in result
        assert "Cost: $0.01" in result


class TestFormatExecutionResults:
    """Test the format_execution_results function."""

    def test_format_execution_results_empty(self):
        """Test formatting empty execution results."""
        result = format_execution_results([], {"model": "test", "provider": "test"})
        assert result == "No execution results to report."

    def test_format_execution_results_with_data(self):
        """Test formatting execution results with data."""
        # Create mock execution result
        mock_result = Mock()
        mock_result.input = "test_input"
        mock_result.duration = 1.5
        mock_result.success = True
        mock_result.cost = 0.01
        mock_result.output = "test_output"
        mock_result.model = "gpt-4"
        mock_result.provider = "openai"
        mock_result.input_tokens = 100
        mock_result.output_tokens = 50
        mock_result.node_name = "test_node"
        mock_result.node_path = ["path1", "path2"]
        mock_result.node_type = "ACTION"
        mock_result.context_patch = {"key": "value"}
        mock_result.error = None
        
        llm_config = {"model": "gpt-4", "provider": "openai"}
        
        result = format_execution_results([mock_result], llm_config, "Performance info")
        
        assert "Performance Report:" in result
        assert "Intent: test_node" in result
        assert "Output: test_output" in result
        assert "Cost: $0.01" in result
        assert "Tokens: 100 in, 50 out" in result
        assert "Performance info" in result
        assert "test_input: 1.500 seconds elapsed" in result

    def test_format_execution_results_with_timings(self):
        """Test formatting execution results with custom timings."""
        mock_result = Mock()
        mock_result.input = "test_input"
        mock_result.duration = None  # Should use provided timing
        mock_result.success = True
        mock_result.cost = 0.01
        mock_result.output = "test_output"
        mock_result.model = "gpt-4"
        mock_result.provider = "openai"
        mock_result.input_tokens = 100
        mock_result.output_tokens = 50
        mock_result.node_name = "test_node"
        mock_result.node_path = None
        mock_result.node_type = None
        mock_result.context_patch = None
        mock_result.error = None
        
        llm_config = {"model": "gpt-4", "provider": "openai"}
        timings = [("test_input", 2.5)]  # Custom timing
        
        result = format_execution_results([mock_result], llm_config, "", timings)
        
        assert "test_input: 2.500 seconds elapsed" in result

    def test_format_execution_results_with_error(self):
        """Test formatting execution results with error."""
        mock_result = Mock()
        mock_result.input = "test_input"
        mock_result.duration = 1.0
        mock_result.success = False
        mock_result.cost = 0.0
        mock_result.output = None
        mock_result.model = None
        mock_result.provider = None
        mock_result.input_tokens = None
        mock_result.output_tokens = None
        mock_result.node_name = "test_node"
        mock_result.node_path = None
        mock_result.node_type = None
        mock_result.context_patch = None
        mock_result.error = "Test error"
        
        llm_config = {"model": "gpt-4", "provider": "openai"}
        
        result = format_execution_results([mock_result], llm_config)
        
        assert "Error: Test error" in result
        assert "False" in result  # Success status should be False