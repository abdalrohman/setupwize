"""Logging configuration for SetUpWize."""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

# Valid log levels
ALLOWED_LOG_LEVELS = ["INFO", "ERROR", "WARNING", "CRITICAL", "DEBUG"]


class ThemedRichHandler(RichHandler):
    """Rich handler with custom theme support."""

    def __init__(self, *args: Any, **kwargs: Any):  # noqa: ANN401
        """Initialize the handler."""
        super().__init__(*args, **kwargs)


@dataclass
class LogConfig:
    """Logging configuration for SetUpWize."""

    log_path: Path
    logger_source: str | None = None
    log_level: str = "INFO"
    filters: str | list[str] | None = None
    logfile_format: str = "%(asctime)s [%(levelname)s] %(name)s:%(module)s:%(lineno)d - %(message)s"
    logfile_datefmt: str = "%Y-%m-%d %H:%M:%S"
    console_format: str = "%(message)s"
    console_datefmt: str = "[%X]"
    rich_tracebacks: bool = True
    tracebacks_show_locals: bool = False
    rich_handler_show_time: bool = False
    rich_handler_show_level: bool = True
    rich_handler_show_path: bool = False

    def __post_init__(self) -> None:
        """Validate and initialize the configuration."""
        if not self.log_path or str(self.log_path).strip() == "":
            raise ValueError("log_path is required")

        # Validate log level
        if self.log_level not in ALLOWED_LOG_LEVELS:
            raise ValueError(
                f"Invalid log level: {self.log_level}. Allowed values: {ALLOWED_LOG_LEVELS}"
            )

        # Convert filters to list
        if isinstance(self.filters, str):
            self.filters = [self.filters]

    @property
    def console(self) -> Console:
        """Get a Rich console instance."""
        return Console(color_system="auto")

    @property
    def handler(self) -> RichHandler:
        """Get a Rich handler for logging."""
        return ThemedRichHandler(
            console=self.console,
            enable_link_path=False,
            rich_tracebacks=self.rich_tracebacks,
            tracebacks_show_locals=self.tracebacks_show_locals,
            show_time=self.rich_handler_show_time,
            show_level=self.rich_handler_show_level,
            show_path=self.rich_handler_show_path,
        )

    def _setup_file_handler(self, logger_name: str) -> logging.FileHandler:
        """Set up a file handler for logging.

        Args:
            logger_name: The name of the logger.

        Returns:
            A configured file handler.
        """
        # Create log directory if it doesn't exist
        self.log_path.mkdir(parents=True, exist_ok=True)

        # Create log file path
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = self.log_path / f"{logger_name}_{timestamp}.log"

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, self.log_level))

        # Set formatter
        formatter = logging.Formatter(self.logfile_format, datefmt=self.logfile_datefmt)
        file_handler.setFormatter(formatter)

        # Add filter if specified
        if self.filters:
            file_handler.addFilter(self._create_filter(self.filters))

        return file_handler

    def _create_filter(self, patterns: str | list[str]) -> logging.Filter:
        """Create a logging filter that excludes messages containing specified patterns.

        Args:
            patterns: A pattern or list of patterns to filter out.

        Returns:
            A logging filter.
        """

        # Convert string pattern to list
        pattern_list = [patterns] if isinstance(patterns, str) else patterns

        class PatternFilter(logging.Filter):
            def filter(self, record: logging.LogRecord) -> bool:
                message = record.getMessage()
                return not any(pattern in message for pattern in pattern_list)

        return PatternFilter()

    def configure(self) -> logging.Logger:
        """Configure and get a logger.

        Returns:
            A configured logger instance.
        """
        # Determine logger name
        logger_name = Path(self.logger_source).stem.upper() if self.logger_source else "MAIN"

        # Get logger
        logger = logging.getLogger(logger_name)

        # Clear existing handlers
        if logger.handlers:
            logger.handlers.clear()

        # Set log level
        logger.setLevel(getattr(logging, self.log_level))

        # Add console handler
        console_handler = self.handler
        console_handler.setLevel(getattr(logging, self.log_level))
        logger.addHandler(console_handler)

        # Add file handler
        file_handler = self._setup_file_handler(logger_name)
        logger.addHandler(file_handler)

        # Prevent propagation to root logger
        logger.propagate = False

        return logger
