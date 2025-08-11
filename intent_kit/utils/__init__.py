"""
Utility modules for intent-kit.
"""

from .logger import Logger
from .text_utils import (
    extract_json_from_text,
    extract_json_array_from_text,
    extract_key_value_pairs,
    is_deserializable_json,
    clean_for_deserialization,
    extract_structured_data,
    validate_json_structure,
)
from .perf_util import PerfUtil, report_table, collect
from .report_utils import (
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
from .type_validator import (
    validate_type,
    validate_dict,
    TypeValidationError,
    validate_int,
    validate_str,
    validate_bool,
    validate_list,
    validate_dict_simple,
    resolve_type,
    TYPE_MAP,
)

__all__ = [
    "Logger",
    "ReportData",
    # Text utilities
    "extract_json_from_text",
    "extract_json_array_from_text",
    "extract_key_value_pairs",
    "is_deserializable_json",
    "clean_for_deserialization",
    "extract_structured_data",
    "validate_json_structure",
    # Performance utilities
    "PerfUtil",
    "report_table",
    "collect",
    # Report utilities
    "format_cost",
    "format_tokens",
    "generate_performance_report",
    "generate_timing_table",
    "generate_summary_statistics",
    "generate_model_information",
    "generate_cost_breakdown",
    "generate_detailed_view",
    "format_execution_results",
    # Type validation utilities
    "validate_type",
    "validate_dict",
    "TypeValidationError",
    "validate_int",
    "validate_str",
    "validate_bool",
    "validate_list",
    "validate_dict_simple",
    "resolve_type",
    "TYPE_MAP",
]
