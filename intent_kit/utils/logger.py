import os


class ColorManager:
    """Handles all color-related logic for terminal output."""

    def __init__(self):
        pass

    def get_color(self, level):
        if level == "info":
            return "\033[32m"  # green
        elif level == "error":
            return "\033[31m"  # red
        elif level == "debug":
            return "\033[34m"  # blue
        elif level == "warning":
            return "\033[33m"  # yellow
        elif level == "critical":
            return "\033[35m"  # magenta
        elif level == "fatal":
            return "\033[36m"  # cyan
        elif level == "trace":
            return "\033[37m"  # white
        elif level == "log":
            return "\033[90m"  # gray
        # New soft color palette using 256-color ANSI codes
        elif level == "section_title":
            return "\033[38;5;75m"  # Soft blue/cyan for main section titles
        elif level == "field_label":
            # Muted light purple for field names/labels
            return "\033[38;5;146m"
        elif level == "field_value":
            return "\033[38;5;250m"  # Soft white/grey for field values
        elif level == "timestamp":
            return "\033[38;5;108m"  # Muted green for timestamps/numbers
        elif level == "action":
            return "\033[38;5;180m"  # Muted yellow/gold for actions (SET/GET)
        elif level == "error_soft":
            return "\033[38;5;210m"  # Soft red for errors (not aggressive)
        elif level == "separator":
            return "\033[38;5;241m"  # Dim grey for section separators
        # Extended color codes for new methods (keeping for backward compatibility)
        elif level == "bright_blue":
            return "\033[94m"  # bright blue
        elif level == "bright_green":
            return "\033[92m"  # bright green
        elif level == "bright_yellow":
            return "\033[93m"  # bright yellow
        elif level == "bright_red":
            return "\033[91m"  # bright red
        elif level == "bright_magenta":
            return "\033[95m"  # bright magenta
        elif level == "bright_cyan":
            return "\033[96m"  # bright cyan
        elif level == "bright_white":
            return "\033[97m"  # bright white
        elif level == "black":
            return "\033[30m"  # black
        elif level == "gray":
            return "\033[90m"  # gray (same as log)
        elif level == "light_gray":
            return "\033[37m"  # light gray (same as white)
        else:
            return "\033[37m"  # white (default)

    def clear_color(self):
        return "\033[0m"  # reset/clear color

    def supports_color(self):
        """Check if the terminal supports ANSI color codes."""
        import os
        import sys

        # Check if we're in a terminal
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False

        # Check environment variables
        if os.environ.get("NO_COLOR"):
            return False

        # Check if we're in a dumb terminal
        term = os.environ.get("TERM", "")
        if term == "dumb":
            return False

        return True

    def colorize(self, text, color_name):
        """Colorize text with a specific color if supported."""
        if not self.supports_color():
            return text
        return f"{self.get_color(color_name)}{text}{self.clear_color()}"

    def colorize_key_value(self, key, value, key_color="white", value_color="yellow"):
        """Colorize a key-value pair."""
        if not self.supports_color():
            return f"{key}: {value}"

        key_colored = self.colorize(key, key_color)
        value_colored = self.colorize(str(value), value_color)
        return f"{key_colored}: {value_colored}"

    def colorize_header(self, text):
        """Colorize a header/section title."""
        return self.colorize(text, "debug")  # blue

    def colorize_success(self, text):
        """Colorize success/info text."""
        return self.colorize(text, "info")  # green

    def colorize_warning(self, text):
        """Colorize warning text."""
        return self.colorize(text, "warning")  # yellow

    def colorize_error(self, text):
        """Colorize error text."""
        return self.colorize(text, "error")  # red

    def colorize_metadata(self, text):
        """Colorize metadata/secondary information."""
        return self.colorize(text, "fatal")  # cyan

    def colorize_bright(self, text, color_name):
        """Colorize text with bright colors."""
        bright_colors = {
            "blue": "bright_blue",
            "green": "bright_green",
            "yellow": "bright_yellow",
            "red": "bright_red",
            "magenta": "bright_magenta",
            "cyan": "bright_cyan",
            "white": "bright_white",
        }
        color = bright_colors.get(color_name, color_name)
        return self.colorize(text, color)

    def colorize_key(self, text):
        """Colorize keys/labels."""
        return self.colorize(text, "bright_blue")

    def colorize_value(self, text):
        """Colorize values/data."""
        return self.colorize(text, "bright_yellow")

    def colorize_string(self, text):
        """Colorize string values."""
        return self.colorize(text, "bright_green")

    def colorize_number(self, text):
        """Colorize numeric values."""
        return self.colorize(text, "bright_yellow")

    def colorize_boolean(self, text):
        """Colorize boolean values."""
        return self.colorize(text, "bright_magenta")

    def colorize_null(self, text):
        """Colorize null/empty values."""
        return self.colorize(text, "bright_red")

    def colorize_bracket(self, text):
        """Colorize brackets/punctuation."""
        return self.colorize(text, "bright_cyan")

    def colorize_section_title(self, text):
        """Colorize main section titles with soft blue/cyan."""
        return self.colorize(text, "section_title")

    def colorize_field_label(self, text):
        """Colorize field names/labels with muted light purple."""
        return self.colorize(text, "field_label")

    def colorize_field_value(self, text):
        """Colorize field values with soft white/grey."""
        return self.colorize(text, "field_value")

    def colorize_timestamp(self, text):
        """Colorize timestamps/numbers with muted green."""
        return self.colorize(text, "timestamp")

    def colorize_action(self, text):
        """Colorize actions (SET/GET) with muted yellow/gold."""
        return self.colorize(text, "action")

    def colorize_error_soft(self, text):
        """Colorize errors with soft red (not aggressive)."""
        return self.colorize(text, "error_soft")

    def colorize_separator(self, text):
        """Colorize section separators with dim grey."""
        return self.colorize(text, "separator")


class Logger:
    # Valid log levels in logical order (from most verbose to least)
    VALID_LOG_LEVELS = [
        "trace",  # Most verbose - detailed execution flow
        "debug",  # Debug information for development
        "info",  # General information
        "warning",  # Warnings that don't stop execution
        "error",  # Errors that affect functionality
        "critical",  # Critical errors that may cause failure
        "fatal",  # Fatal errors that will cause termination
        "off",  # No logging
    ]

    def __init__(self, name, level=""):
        self.name = name
        self.level = level or os.getenv("LOG_LEVEL", "info")
        self._validate_log_level()
        self.color_manager = ColorManager()

    def _validate_log_level(self):
        """Validate the log level and throw exception if invalid."""
        if self.level not in self.VALID_LOG_LEVELS:
            valid_levels = ", ".join(self.VALID_LOG_LEVELS)
            raise ValueError(
                f"Invalid log level '{self.level}'. "
                f"Valid levels are: {valid_levels}"
            )

    def get_valid_log_levels(self):
        """Return valid log levels in logical order."""
        return self.VALID_LOG_LEVELS.copy()

    def should_log(self, message_level):
        """Check if a message at the given level should be logged."""
        if self.level == "off":
            return False

        # Get the index of current level and message level
        try:
            current_index = self.VALID_LOG_LEVELS.index(self.level)
            message_index = self.VALID_LOG_LEVELS.index(message_level)
            # Log if message level is at or above current level (lower index = more verbose)
            return message_index >= current_index
        except ValueError:
            # If message_level is not in VALID_LOG_LEVELS, don't log it
            return False

    # Delegate color methods directly to color_manager
    def __getattr__(self, name):
        """Delegate color-related methods to color_manager."""
        if hasattr(self.color_manager, name):
            return getattr(self.color_manager, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def info(self, message):
        if not self.should_log("info"):
            return
        color = self.get_color("info")
        clear = self.clear_color()
        print(f"{color}[INFO]{clear} [{self.name}] {message}")

    def error(self, message):
        if not self.should_log("error"):
            return
        color = self.get_color("error")
        clear = self.clear_color()
        print(f"{color}[ERROR]{clear} [{self.name}] {message}")

    def debug(self, message):
        if not self.should_log("debug"):
            return
        color = self.get_color("debug")
        clear = self.clear_color()
        print(f"{color}[DEBUG]{clear} [{self.name}] {message}")

    def warning(self, message):
        if not self.should_log("warning"):
            return
        color = self.get_color("warning")
        clear = self.clear_color()
        print(f"{color}[WARNING]{clear} [{self.name}] {message}")

    def critical(self, message):
        if not self.should_log("critical"):
            return
        color = self.get_color("critical")
        clear = self.clear_color()
        print(f"{color}[CRITICAL]{clear} [{self.name}] {message}")

    def fatal(self, message):
        if not self.should_log("fatal"):
            return
        color = self.get_color("fatal")
        clear = self.clear_color()
        print(f"{color}[FATAL]{clear} [{self.name}] {message}")

    def trace(self, message):
        if not self.should_log("trace"):
            return
        color = self.get_color("trace")
        clear = self.clear_color()
        print(f"{color}[TRACE]{clear} [{self.name}] {message}")

    def log(self, level, message):
        if not self.should_log(level):
            return
        color = self.get_color(level)
        clear = self.clear_color()
        print(f"{color}[{level}]{clear} [{self.name}] {message}")
