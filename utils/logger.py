import sys


class Logger:
    COLORS = {
        "blue": "\033[34m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "red": "\033[31m",
        "reset": "\033[0m"
    }

    def __init__(self, log_file=None):
        self.enable_colors = sys.stdout.isatty()
        self.log_file = log_file
        if log_file:
            # Create directory if it doesn't exist
            import os
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            # Create or clear the log file
            with open(log_file, 'w') as f:
                pass  # Just create/clear the file

    def _color(self, text, color):
        if self.enable_colors:
            return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
        return text

    def log(self, message):
        print(message)
        self._write_to_file(message)

    def highlight(self, message):
        colored_message = self._color(message, "blue")
        print(colored_message)
        self._write_to_file(message)  # Write uncolored text to file

    def success(self, message):
        colored_message = self._color(message, "green")
        print(colored_message)
        self._write_to_file(message)

    def warn(self, message):
        colored_message = self._color(message, "yellow")
        print(colored_message)
        self._write_to_file(message)

    def error(self, message):
        colored_message = self._color(message, "red")
        print(colored_message)
        self._write_to_file(message)

    def _write_to_file(self, message):
        """Write message to log file if one is specified"""
        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(f"{message}\n")
            except Exception as e:
                print(f"Error writing to log file: {e}")
                # Don't throw further exceptions if we can't log