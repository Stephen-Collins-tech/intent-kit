"""
Tests for logger utilities.
"""

import pytest





class TestColorManager:
    """Test ColorManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.color_manager = ColorManager()

    def test_def test_get_color_basic_levels(self): -> None:
        """Test getting colors for basic log levels."""
        assert self.color_manager.get_color("info") == "\033[32m"
        assert self.color_manager.get_color("error") == "\033[31m"
        assert self.color_manager.get_color("debug") == "\033[34m"
        assert self.color_manager.get_color("warning") == "\033[33m"
        assert self.color_manager.get_color("critical") == "\033[35m"
        assert self.color_manager.get_color("fatal") == "\033[36m"
        assert self.color_manager.get_color("trace") == "\033[37m"
        assert self.color_manager.get_color("log") == "\033[90m"

    def test_def test_get_color_extended_levels(self): -> None:
        """Test getting colors for extended log levels."""
        assert self.color_manager.get_color("section_title") == "\033[38;5;75m"
        assert self.color_manager.get_color("field_label") == "\033[38;5;146m"
        assert self.color_manager.get_color("field_value") == "\033[38;5;250m"
        assert self.color_manager.get_color("timestamp") == "\033[38;5;108m"
        assert self.color_manager.get_color("action") == "\033[38;5;180m"
        assert self.color_manager.get_color("error_soft") == "\033[38;5;210m"
        assert self.color_manager.get_color("separator") == "\033[38;5;241m"

    def test_def test_get_color_bright_levels(self): -> None:
        """Test getting colors for bright levels."""
        assert self.color_manager.get_color("bright_blue") == "\033[94m"
        assert self.color_manager.get_color("bright_green") == "\033[92m"
        assert self.color_manager.get_color("bright_yellow") == "\033[93m"
        assert self.color_manager.get_color("bright_red") == "\033[91m"
        assert self.color_manager.get_color("bright_magenta") == "\033[95m"
        assert self.color_manager.get_color("bright_cyan") == "\033[96m"
        assert self.color_manager.get_color("bright_white") == "\033[97m"

    def test_def test_get_color_unknown_level(self): -> None:
        """Test getting color for unknown level returns default."""
        assert self.color_manager.get_color("unknown") == "\033[37m"

    def test_def test_clear_color(self): -> None:
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

    def test_def test_colorize_methods(self): -> None:
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

    def test_def test_colorize_bright_methods(self): -> None:
        """Test bright colorize methods."""
        with patch.object(self.color_manager, "colorize") as mock_colorize:
            self.color_manager.colorize_bright("text", "blue")
            mock_colorize.assert_called_with("text", "bright_blue")

            self.color_manager.colorize_bright("text", "unknown")
            mock_colorize.assert_called_with("text", "unknown")

    def test_def test_colorize_type_methods(self): -> None:
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

    def test_def test_colorize_special_methods(self): -> None:
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

    def test_def test_supports_color_basic(self): -> None:
        """Test supports_color basic functionality."""
        # This is a basic test that doesn't require complex mocking
        result = self.color_manager.supports_color()
        assert isinstance(result, bool)


class TestLogger:
    """Test Logger class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.logger = Logger("test_logger")

    def test_def test_init_with_name(self): -> None:
        """Test logger initialization with name."""
        logger = Logger("test_name")
        assert logger.name == "test_name"
        assert logger.level == "info"  # default level

    def test_def test_init_with_level(self): -> None:
        """Test logger initialization with custom level."""
        logger = Logger("test_name", "debug")
        assert logger.name == "test_name"
        assert logger.level == "debug"

    def test_def test_get_valid_log_levels(self): -> None:
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

    def test_def test_should_log(self): -> None:
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

    def test_def test_validate_log_level(self): -> None:
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

    def test_def test_log_methods(self): -> None:
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

    def test_def test_getattr_fallback(self): -> None:
        """Test __getattr__ fallback for unknown methods."""
        # Test that color_manager methods are accessible through logger
        assert hasattr(self.logger, "colorize")
        assert hasattr(self.logger, "get_color")

        # Test that unknown methods raise AttributeError
        with pytest.raises(AttributeError):
            self.logger.unknown_method

    def test_def test_log_output_format(self): -> None:
        """Test log output format."""
        with patch("intent_kit.utils.logger.print") as mock_print:
            self.logger.log("info", "test message")
            mock_print.assert_called_once()
            # Check that the output contains the expected format
            call_args = mock_print.call_args[0][0]
            assert "test_logger" in call_args
            assert "test message" in call_args

    def test_def test_log_level_filtering(self): -> None:
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

    def test_def test_logger_with_different_names(self): -> None:
        """Test logger with different names."""
        logger1 = Logger("logger1")
        logger2 = Logger("logger2")

        with patch("intent_kit.utils.logger.print") as mock_print:
            logger1.log("info", "message1")
            logger2.log("info", "message2")

            calls = mock_print.call_args_list
            assert "logger1" in calls[0][0][0]
            assert "logger2" in calls[1][0][0]
