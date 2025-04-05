"""Tests for the log module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.logging import RichHandler

from setupwize.tracers.log import LogConfig, ThemedRichHandler


class TestThemedRichHandler:
    """Tests for the ThemedRichHandler class."""

    def test_init(self) -> None:
        """Test initialization."""
        handler = ThemedRichHandler()
        assert isinstance(handler, RichHandler)


class TestLogConfig:
    """Tests for the LogConfig class."""

    def test_init(self) -> None:
        """Test initialization."""
        config = LogConfig(
            log_path=Path("/path/to/log"),
            log_level="INFO",
            logger_source="test_source",
            filters=["test_pattern"],
        )
        assert config.log_path == Path("/path/to/log")
        assert config.log_level == "INFO"
        assert config.logger_source == "test_source"
        assert config.filters == ["test_pattern"]

    def test_post_init_missing_log_path(self) -> None:
        """Test post initialization with missing log path."""
        with pytest.raises(ValueError, match="log_path is required"):
            LogConfig(log_path=Path(" "))

    @patch("setupwize.tracers.log.logging.getLogger")
    @patch("setupwize.tracers.log.ThemedRichHandler")
    @patch("pathlib.Path.mkdir")
    @patch("setupwize.tracers.log.logging.FileHandler")
    @patch("setupwize.tracers.log.datetime")
    def test_configure(
        self, mock_datetime, mock_file_handler, mock_mkdir, mock_rich_handler, mock_get_logger
    ) -> None:
        """Test configure method."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_rich_handler_instance = MagicMock()
        mock_rich_handler.return_value = mock_rich_handler_instance
        mock_file_handler_instance = MagicMock()
        mock_file_handler.return_value = mock_file_handler_instance
        mock_datetime.now.return_value.strftime.return_value = "20250405"

        config = LogConfig(
            log_path=Path("/path/to/log"),
            log_level="INFO",
        )
        logger = config.configure()

        mock_get_logger.assert_called_once()
        mock_logger.setLevel.assert_called_once()
        mock_rich_handler.assert_called_once()
        mock_rich_handler_instance.setLevel.assert_called_once()
        mock_logger.addHandler.assert_called()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        assert logger == mock_logger
