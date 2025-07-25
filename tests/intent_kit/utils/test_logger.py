"""
Tests for logger utilities.
"""

import pytest
from unittest.mock import patch

from intent_kit.utils.logger import ColorManager, Logger


class TestColorManager:
    """Test ColorManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.color_manager = ColorManager()

    def test_get_color_basic_levels(self):
        """Test getting colors for basic log levels."""
        assert self.color_manager.get_color("info") == "\033[32m"
        assert self.color_manager.get_color("error") == "\033[31m"
        assert self.color_manager.get_color("debug") == "\033[34m"
        assert self.color_manager.get_color("warning") == "\033[33m"
        assert self.color_manager.get_color("critical") == "\033[35m"
        assert self.color_manager.get_color("fatal") == "\033[36m"
        assert self.color_manager.get_color("trace") == "\033[37m"
        assert self.color_manager.get_color("log") == "\033[90m"

    def test_get_color_extended_levels(self):
        """Test getting colors for extended log levels."""
        assert self.color_manager.get_color("section_title") == "\033[38;5;75m"
        assert self.color_manager.get_color("field_label") == "\033[38;5;146m"
        assert self.color_manager.get_color("field_value") == "\033[38;5;250m"
        assert self.color_manager.get_color("timestamp") == "\033[38;5;108m"
        assert self.color_manager.get_color("action") == "\033[38;5;180m"
        assert self.color_manager.get_color("error_soft") == "\033[38;5;210m"
        assert self.color_manager.get_color("separator") == "\033[38;5;241m"

    def test_get_color_bright_levels(self):
        """Test getting colors for bright levels."""
        assert self.color_manager.get_color("bright_blue") == "\033[94m"
        assert self.color_manager.get_color("bright_green") == "\033[92m"
        assert self.color_manager.get_color("bright_yellow") == "\033[93m"
        assert self.color_manager.get_color("bright_red") == "\033[91m"
        assert self.color_manager.get_color("bright_magenta") == "\033[95m"
        assert self.color_manager.get_color("bright_cyan") == "\033[96m"
        assert self.color_manager.get_color("bright_white") == "\033[97m"

    def test_get_color_unknown_level(self):
        """Test getting color for unknown level returns default."""
        assert self.color_manager.get_color("unknown") == "\033[37m"

    def test_clear_color(self):
        """Test clear color method."""
        assert self.color_manager.clear_color() == "\033[0m"

    @patch("intent_kit.utils.logger.ColorManager.supports_color")
    def test_colorize_with_color_support(self, mock_supports_color):
        """Test colorize method when color is supported."""
        mock_supports_color.return_value = True
        result = self.color_manager.colorize("test", "info")
        assert result == "\033[32mtest\033[0m"

    @patch("intent_kit.utils.logger.ColorManager.supports_color")
    def test_colorize_without_color_support(self, mock_supports_color):
        """Test colorize method when color is not supported."""
        mock_supports_color.return_value = False
        result = self.color_manager.colorize("test", "info")
        assert result == "test"

    @patch("intent_kit.utils.logger.ColorManager.supports_color")
    def test_colorize_key_value_with_color(self, mock_supports_color):
        """Test colorize_key_value method with color support."""
        mock_supports_color.return_value = True
        result = self.color_manager.colorize_key_value("key", "value")
        # The actual implementation uses white for both key and value
        assert "key" in result
        assert "value" in result
        assert "\033[37m" in result  # white for key
        assert "\033[0m" in result  # color reset

    @patch("intent_kit.utils.logger.ColorManager.supports_color")
    def test_colorize_key_value_without_color(self, mock_supports_color):
        """Test colorize_key_value method without color support."""
        mock_supports_color.return_value = False
        result = self.color_manager.colorize_key_value("key", "value")
        assert result == "key: value"

    def test_colorize_methods(self):
        """Test various colorize convenience methods."""
        with patch.object(self.color_manager, "colorize") as mock_colorize:
            self.color_manager.colorize_header("header")
            mock_colorize.assert_called_with("header", "debug")

            self.color_manager.colorize_success("success")
            mock_colorize.assert_called_with("success", "info")

            self.color_manager.colorize_warning("warning")
            mock_colorize.assert_called_with("warning", "warning")

            self.color_manager.colorize_error("error")
            mock_colorize.assert_called_with("error", "error")

            self.color_manager.colorize_metadata("metadata")
            mock_colorize.assert_called_with("metadata", "fatal")

    def test_colorize_bright_methods(self):
        """Test bright colorize methods."""
        with patch.object(self.color_manager, "colorize") as mock_colorize:
            self.color_manager.colorize_bright("text", "blue")
            mock_colorize.assert_called_with("text", "bright_blue")

            self.color_manager.colorize_bright("text", "unknown")
            mock_colorize.assert_called_with("text", "unknown")

    def test_colorize_type_methods(self):
        """Test type-specific colorize methods."""
        with patch.object(self.color_manager, "colorize") as mock_colorize:
            self.color_manager.colorize_key("key")
            mock_colorize.assert_called_with("key", "bright_blue")

            self.color_manager.colorize_value("value")
            mock_colorize.assert_called_with("value", "bright_yellow")

            self.color_manager.colorize_string("string")
            mock_colorize.assert_called_with("string", "bright_green")

            self.color_manager.colorize_number("123")
            mock_colorize.assert_called_with("123", "bright_yellow")

            self.color_manager.colorize_boolean("true")
            mock_colorize.assert_called_with("true", "bright_magenta")

            self.color_manager.colorize_null("null")
            mock_colorize.assert_called_with("null", "bright_red")

            self.color_manager.colorize_bracket("[]")
            mock_colorize.assert_called_with("[]", "bright_cyan")

    def test_colorize_special_methods(self):
        """Test special colorize methods."""
        with patch.object(self.color_manager, "colorize") as mock_colorize:
            self.color_manager.colorize_section_title("title")
            mock_colorize.assert_called_with("title", "section_title")

            self.color_manager.colorize_field_label("label")
            mock_colorize.assert_called_with("label", "field_label")

            self.color_manager.colorize_field_value("value")
            mock_colorize.assert_called_with("value", "field_value")

            self.color_manager.colorize_timestamp("2023-01-01")
            mock_colorize.assert_called_with("2023-01-01", "timestamp")

            self.color_manager.colorize_action("SET")
            mock_colorize.assert_called_with("SET", "action")

            self.color_manager.colorize_error_soft("error")
            mock_colorize.assert_called_with("error", "error_soft")

            self.color_manager.colorize_separator("---")
            mock_colorize.assert_called_with("---", "separator")

    def test_supports_color_basic(self):
        """Test supports_color basic functionality."""
        # This is a basic test that doesn't require complex mocking
        result = self.color_manager.supports_color()
        assert isinstance(result, bool)

    @patch("sys.stdout")
    @patch("os.environ")
    def test_supports_color_environment_variables(self, mock_environ, mock_stdout):
        """Test supports_color with different environment configurations."""
        # Mock stdout to be a terminal
        mock_stdout.isatty.return_value = True

        # Test with NO_COLOR set
        mock_environ.get.side_effect = lambda key, default=None: (
            "1" if key == "NO_COLOR" else default
        )
        assert not self.color_manager.supports_color()

        # Test with TERM=dumb
        mock_environ.get.side_effect = lambda key, default=None: (
            "dumb" if key == "TERM" else default
        )
        assert not self.color_manager.supports_color()

        # Test with normal terminal
        mock_environ.get.side_effect = lambda key, default=None: (
            "xterm" if key == "TERM" else None
        )
        assert self.color_manager.supports_color()


class TestLogger:
    """Test Logger class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.logger = Logger("test_logger")

    def test_init_with_name(self):
        """Test logger initialization with name."""
        logger = Logger("test_name")
        assert logger.name == "test_name"
        assert logger.level == "info"  # default level

    def test_init_with_level(self):
        """Test logger initialization with custom level."""
        logger = Logger("test_name", "debug")
        assert logger.name == "test_name"
        assert logger.level == "debug"

    def test_get_valid_log_levels(self):
        """Test getting valid log levels."""
        levels = self.logger.get_valid_log_levels()
        expected = [
            "trace",
            "debug",
            "info",
            "warning",
            "error",
            "critical",
            "fatal",
            "off",
        ]
        assert levels == expected

    def test_should_log(self):
        """Test should_log method with different levels."""
        # Test with info level logger
        logger = Logger("test", "info")
        assert logger.should_log("info")
        assert logger.should_log("warning")
        assert logger.should_log("error")
        assert not logger.should_log("debug")
        assert not logger.should_log("trace")

        # Test with debug level logger
        logger = Logger("test", "debug")
        assert logger.should_log("debug")
        assert logger.should_log("info")
        assert not logger.should_log("trace")

        # Test with trace level logger
        logger = Logger("test", "trace")
        assert logger.should_log("trace")
        assert logger.should_log("debug")

    def test_validate_log_level(self):
        """Test log level validation."""
        # Valid levels should not raise
        for level in [
            "trace",
            "debug",
            "info",
            "warning",
            "error",
            "critical",
            "fatal",
        ]:
            Logger("test", level)  # Should not raise exception

        # Invalid level should raise
        with pytest.raises(ValueError, match="Invalid log level"):
            Logger("test", "invalid_level")

    def test_log_methods(self):
        """Test all log methods."""
        # Test that the methods exist and are callable
        assert callable(self.logger.info)
        assert callable(self.logger.error)
        assert callable(self.logger.debug)
        assert callable(self.logger.warning)
        assert callable(self.logger.critical)
        assert callable(self.logger.fatal)
        assert callable(self.logger.trace)
        assert callable(self.logger.log)

    def test_getattr_fallback(self):
        """Test __getattr__ fallback for unknown methods."""
        # Test that color_manager methods are accessible through logger
        assert hasattr(self.logger, "colorize")
        assert hasattr(self.logger, "get_color")

        # Test that unknown methods raise AttributeError
        with pytest.raises(AttributeError):
            self.logger.unknown_method

    def test_log_output_format(self):
        """Test log output format."""
        with patch("intent_kit.utils.logger.print") as mock_print:
            self.logger.log("info", "test message")
            mock_print.assert_called_once()
            # Check that the output contains the expected format
            call_args = mock_print.call_args[0][0]
            assert "test_logger" in call_args
            assert "test message" in call_args

    def test_log_level_filtering(self):
        """Test that log messages are filtered by level."""
        logger = Logger("test", "warning")

        with patch("intent_kit.utils.logger.print") as mock_print:
            # Should not log debug message
            logger.log("debug", "debug message")
            mock_print.assert_not_called()

            # Should log warning message
            logger.log("warning", "warning message")
            mock_print.assert_called_once()

            # Should log error message
            logger.log("error", "error message")
            assert mock_print.call_count == 2

    def test_logger_with_different_names(self):
        """Test logger with different names."""
        logger1 = Logger("logger1")
        logger2 = Logger("logger2")

        with patch("intent_kit.utils.logger.print") as mock_print:
            logger1.log("info", "message1")
            logger2.log("info", "message2")

            calls = mock_print.call_args_list
            assert "logger1" in calls[0][0][0]
            assert "logger2" in calls[1][0][0]

    def test_individual_log_methods(self):
        """Test individual log methods (info, error, warning, etc.)."""
        # Use trace level logger to ensure all methods will be called
        logger = Logger("test", "trace")

        with patch("intent_kit.utils.logger.print") as mock_print:
            # Test info method
            logger.info("info message")
            call_args = mock_print.call_args[0][0]
            assert "[INFO]" in call_args
            assert "info message" in call_args

            # Test error method
            logger.error("error message")
            call_args = mock_print.call_args[0][0]
            assert "[ERROR]" in call_args
            assert "error message" in call_args

            # Test warning method
            logger.warning("warning message")
            call_args = mock_print.call_args[0][0]
            assert "[WARNING]" in call_args
            assert "warning message" in call_args

            # Test critical method
            logger.critical("critical message")
            call_args = mock_print.call_args[0][0]
            assert "[CRITICAL]" in call_args
            assert "critical message" in call_args

            # Test fatal method
            logger.fatal("fatal message")
            call_args = mock_print.call_args[0][0]
            assert "[FATAL]" in call_args
            assert "fatal message" in call_args

            # Test trace method
            logger.trace("trace message")
            call_args = mock_print.call_args[0][0]
            assert "[TRACE]" in call_args
            assert "trace message" in call_args

    def test_debug_method_with_colorize(self):
        """Test debug method with colorize_message parameter."""
        # Use debug level logger to ensure debug method will be called
        logger = Logger("test", "debug")

        with patch("intent_kit.utils.logger.print") as mock_print:
            # Test with colorize_message=True (default)
            logger.debug("key: value")
            call_args = mock_print.call_args[0][0]
            assert "[DEBUG]" in call_args
            assert "key: value" in call_args

            # Test with colorize_message=False
            logger.debug("simple message", colorize_message=False)
            call_args = mock_print.call_args[0][0]
            assert "[DEBUG]" in call_args
            assert "simple message" in call_args

    def test_debug_structured_method(self):
        """Test debug_structured method with different data types."""
        # Use debug level logger to ensure debug_structured method will be called
        logger = Logger("test", "debug")

        with patch("intent_kit.utils.logger.print") as mock_print:
            # Test with dictionary
            test_dict = {"key": "value", "number": 42}
            logger.debug_structured(test_dict, "Test Dict")
            call_args = mock_print.call_args[0][0]
            assert "[DEBUG]" in call_args
            assert "Test Dict" in call_args

            # Test with list
            test_list = [1, 2, 3, "string"]
            logger.debug_structured(test_list, "Test List")
            call_args = mock_print.call_args[0][0]
            assert "[DEBUG]" in call_args
            assert "Test List" in call_args

            # Test with string
            logger.debug_structured("simple string", "Test String")
            call_args = mock_print.call_args[0][0]
            assert "[DEBUG]" in call_args
            assert "Test String" in call_args

    def test_format_dict_method(self):
        """Test _format_dict method with various data types."""
        test_data = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "null": None,
            "nested": {"inner": "value"},
            "list": [1, 2, 3],
        }

        result = self.logger._format_dict(test_data)
        assert "string" in result
        assert "value" in result
        assert "42" in result
        assert "True" in result
        assert "null" in result
        assert "nested" in result
        assert "inner" in result

    def test_format_list_method(self):
        """Test _format_list method with various data types."""
        test_data = ["string", 42, True, None, {"key": "value"}, [1, 2, 3]]

        result = self.logger._format_list(test_data)
        assert "string" in result
        assert "42" in result
        assert "True" in result
        assert "null" in result
        assert "key" in result
        assert "value" in result

    def test_format_empty_containers(self):
        """Test formatting of empty dictionaries and lists."""
        # Test empty dict
        result_dict = self.logger._format_dict({})
        assert "{}" in result_dict

        # Test empty list
        result_list = self.logger._format_list([])
        assert "[]" in result_list

    def test_debug_structured_without_color_support(self):
        """Test debug_structured method when color is not supported."""
        # Use debug level logger to ensure debug_structured method will be called
        logger = Logger("test", "debug")

        with patch.object(logger, "supports_color", return_value=False):
            with patch("intent_kit.utils.logger.print") as mock_print:
                test_data = {"key": "value"}
                logger.debug_structured(test_data, "Test")
                call_args = mock_print.call_args[0][0]
                assert "[DEBUG]" in call_args
                assert "Test" in call_args
                assert "{'key': 'value'}" in call_args

    def test_log_method_level_filtering(self):
        """Test that individual log methods respect level filtering."""
        logger = Logger("test", "warning")

        with patch("intent_kit.utils.logger.print") as mock_print:
            # These should not log due to level filtering
            logger.info("info message")
            logger.debug("debug message")
            logger.trace("trace message")

            mock_print.assert_not_called()

            # These should log
            logger.warning("warning message")
            logger.error("error message")
            logger.critical("critical message")
            logger.fatal("fatal message")

            assert mock_print.call_count == 4

    def test_logger_with_off_level(self):
        """Test logger with 'off' level - should not log anything."""
        logger = Logger("test", "off")

        with patch("intent_kit.utils.logger.print") as mock_print:
            logger.info("info message")
            logger.error("error message")
            logger.debug("debug message")

            mock_print.assert_not_called()

    def test_color_manager_integration(self):
        """Test that logger properly uses color_manager."""
        with patch("intent_kit.utils.logger.print") as mock_print:
            self.logger.info("test message")
            call_args = mock_print.call_args[0][0]

            # Should contain color codes
            assert "\033[" in call_args
            assert "\033[0m" in call_args  # color reset

    def test_logger_edge_cases(self):
        """Test logger with edge cases."""
        # Test with empty message
        with patch("intent_kit.utils.logger.print") as mock_print:
            self.logger.info("")
            call_args = mock_print.call_args[0][0]
            assert "[INFO]" in call_args

        # Test with None message
        with patch("intent_kit.utils.logger.print") as mock_print:
            self.logger.info(None)
            call_args = mock_print.call_args[0][0]
            assert "[INFO]" in call_args
            assert "None" in call_args

        # Test with non-string message
        with patch("intent_kit.utils.logger.print") as mock_print:
            self.logger.info(123)
            call_args = mock_print.call_args[0][0]
            assert "[INFO]" in call_args
            assert "123" in call_args
