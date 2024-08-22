import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Logging
ALLOWED_LOG_LEVELS: list[str] = [
    "INFO",
    "ERROR",
    "WARNING",
    "CRITICAL",
    "DEBUG",
]


class ThemedRichHandler(RichHandler):
    def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
        super().__init__(*args, **kwargs)
        self.console_theme = Theme(
            {
                "logging.level.info": "bold cyan",
                "logging.level.warning": "yellow",
                "logging.level.error": "bold red",
                "logging.level.critical": "bold red reverse",
            }
        )

    def emit(self, record: logging.LogRecord) -> None:
        # Apply theme before rendering
        self.console.push_theme(self.console_theme)

        # Call the original emit method to handle rendering
        super().emit(record)

        # Pop the theme after rendering
        self.console.pop_theme()


class CustomFilters(logging.Filter):
    """
    A custom logging filter that filters log records based on specified substrings.
    Accepts None to disable filtering.

    Args:
        filters: A string, a list of strings, or None.
                 If a string or list, log records containing any of these substrings will be filtered out.
                 If None, no filtering will be applied.
    """

    def __init__(
        self,
        filters: str | list[str] | None,
    ):
        super().__init__()
        self.filters: list[str] = []  # Empty list effectively disables filtering
        if filters is None:
            pass
        else:
            self.filters = [filters] if isinstance(filters, str) else filters

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filters a log record based on the defined filter criteria.

        Args:
            record: The log record to be filtered.

        Returns:
            True if the log record should be kept (not filtered out), False otherwise.
        """
        if not self.filters:  # No filters, allow all records
            return True

        message = record.getMessage().lower()  # Case-insensitive filtering
        return not any(f.lower() in message for f in self.filters)


class LogConfig:
    """
    Configures and provides a logger instance with rich formatting, file handling, and filtering capabilities.

    Args:
        log_path: The path to the directory where log files will be stored. (required)
        logger_source: The source or name of the logger. If not provided, it defaults to the module name where `get_logger` is called.
        log_level: The desired logging level (e.g., "INFO", "DEBUG"). Defaults to "INFO".
        filters: A string, a list of strings, or None representing filter criteria.
                 Log records containing any of these substrings will be filtered out.
                 Defaults to None (no filtering).
        logfile_format: The log record format string for the log file.
        logfile_datefmt: The date/time format for log records in the log file.
        console_format: The log record format string for console output.
        console_datefmt: The date/time format for log records in the console output.
        rich_tracebacks: Whether to enable rich tracebacks for exceptions (using the `rich` library).
        tracebacks_show_locals: Whether to show local variables in rich tracebacks.
        rich_handler_show_time: Whether to show the timestamp in the rich console handler.
        rich_handler_show_level: Whether to show the log level in the rich console handler.
        rich_handler_show_path: Whether to show the file path and line number in the rich console handler.

    Example:
        ```python
        from core.tracers import LogConfig

        logger = LogConfig(log_path="./logs").get_logger()
        logger.info("This is an informational message.")
        ```
    """  # noqa: E501

    def __init__(
        self,
        *,
        log_path: str | Path,
        logger_source: str | None = None,
        log_level: str = "INFO",
        filters: str | list[str] | None = None,
        logfile_format: str = "%(asctime)s [%(levelname)s] %(name)s:%(module)s:%(lineno)d - %(message)s",
        logfile_datefmt: str = "%Y-%m-%d %H:%M:%S",
        console_format: str = "%(message)s",
        console_datefmt: str = "[%X]",
        rich_tracebacks: bool = True,
        tracebacks_show_locals: bool = False,
        rich_handler_show_time: bool = False,
        rich_handler_show_level: bool = True,
        rich_handler_show_path: bool = False,
    ):
        if not log_path:
            raise ValueError("log_path is required")

        if isinstance(log_path, str):
            self.log_path = Path(log_path)

        self.log_path.mkdir(exist_ok=True)  # create log directory if not exist

        # define the log file name
        self.log_file_path: Path = self.log_path / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        self.logger_source = logger_source
        self.log_level = log_level.upper() if log_level.upper() in ALLOWED_LOG_LEVELS else "INFO"

        self.filters: str | list[str] | None = filters

        # Customize rich handler
        self.rich_tracebacks = rich_tracebacks
        self.tracebacks_show_locals = tracebacks_show_locals
        self.rich_handler_show_time = rich_handler_show_time
        self.rich_handler_show_level = rich_handler_show_level
        self.rich_handler_show_path = rich_handler_show_path

        self.logfile_format: str = logfile_format
        self.logfile_datefmt: str = logfile_datefmt
        self.console_format: str = console_format
        self.console_datefmt: str = console_datefmt

    @property
    def console(self) -> Console:
        """
        Creates a Rich Console instance based on the execution environment.
        """
        return Console(
            color_system="auto",
        )

    @property
    def handler(self) -> RichHandler:
        """
        Creates a RichHandler for logging with enhanced formatting and tracebacks
        """
        return ThemedRichHandler(
            console=self.console,
            enable_link_path=False,
            rich_tracebacks=self.rich_tracebacks,
            tracebacks_show_locals=self.tracebacks_show_locals,
            show_time=self.rich_handler_show_time,
            show_level=self.rich_handler_show_level,
            show_path=self.rich_handler_show_path,
        )

    def get_logger(self) -> logging.Logger:
        """
        Configures and returns a logger instance with file handling and custom filtering

        Returns:
            A configured logger instance
        """
        # set file formatter
        file_formatter = logging.Formatter(
            self.logfile_format,
            datefmt=self.logfile_datefmt,
        )
        # create file handler to store the log into file
        file_handler = logging.FileHandler(filename=str(self.log_file_path))
        file_handler.setFormatter(file_formatter)

        # set the formatter for rich handler to format the console logging format
        self.handler.setFormatter(
            logging.Formatter(
                self.console_format,
                datefmt=self.console_datefmt,
            ),
        )

        # Get the root logger
        logger = logging.getLogger()
        logger.setLevel(self.log_level)

        # Remove existing handlers (if necessary)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Add handlers to root logger
        logger.addHandler(self.handler)
        logger.addHandler(file_handler)

        # Get or create the logger for the specific source
        logger = logging.getLogger(self.logger_source)

        # if there is filter add it to the logger
        if self.filters:
            logger.addFilter(CustomFilters(self.filters))

        return logger


# # Example usage

# # Default configuration (INFO level, MAIN logger)
# logger = LogConfig(log_path="./logs").get_logger()
# logger.info("This is an informational message.")

# # Filter out logs containing "sensitive_data"
# logger = LogConfig(log_path="./logs", filters="sensitive_data").get_logger()
# logger.info("This message contains sensitive_data and will be filtered out.")
# logger.info("This message is safe and will be logged.")

# # Disable filtering
# logger = LogConfig(log_path="./logs", filters=None).get_logger()
# logger.info("All messages will be logged, no filtering applied.")

# # Custom format
# custom_format = "%(levelname)s: %(message)s"
# custom_datefmt = "%Y-%m-%d %H:%M:%S"
# logger = LogConfig(log_path="./logs", format=custom_format, datefmt=custom_datefmt).get_logger()
# logger.info("This message will use the custom format and date format.")
