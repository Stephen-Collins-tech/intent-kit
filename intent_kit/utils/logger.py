class Logger:
    def __init__(self, name, level=""):
        self.name = name
        self.level = level

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
        else:
            return "\033[37m"  # white

    def clear_color(self):
        return "\033[0m"  # reset/clear color

    def info(self, message):
        color = self.get_color("info")
        clear = self.clear_color()
        print(f"{color}[INFO]{clear} [{self.name}] {message}")

    def error(self, message):
        color = self.get_color("error")
        clear = self.clear_color()
        print(f"{color}[ERROR]{clear} [{self.name}] {message}")

    def debug(self, message):
        color = self.get_color("debug")
        clear = self.clear_color()
        print(f"{color}[DEBUG]{clear} [{self.name}] {message}")

    def warning(self, message):
        color = self.get_color("warning")
        clear = self.clear_color()
        print(f"{color}[WARNING]{clear} [{self.name}] {message}")

    def critical(self, message):
        color = self.get_color("critical")
        clear = self.clear_color()
        print(f"{color}[CRITICAL]{clear} [{self.name}] {message}")

    def fatal(self, message):
        color = self.get_color("fatal")
        clear = self.clear_color()
        print(f"{color}[FATAL]{clear} [{self.name}] {message}")

    def trace(self, message):
        color = self.get_color("trace")
        clear = self.clear_color()
        print(f"{color}[TRACE]{clear} [{self.name}] {message}")

    def log(self, level, message):
        color = self.get_color(level)
        clear = self.clear_color()
        print(f"{color}[{level}]{clear} [{self.name}] {message}")
