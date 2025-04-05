"""Tests for the environment module."""

import os
from pathlib import Path
from unittest.mock import patch

from setupwize.core.environment import Environment


class TestEnvironment:
    """Tests for the Environment class."""

    def test_default_values(self) -> None:
        """Test default values."""
        env = Environment()

        assert env.packages_dir == Path("packages")
        assert env.log_level == "INFO"
        assert env.log_path == Path("logs")

    def test_custom_values(self) -> None:
        """Test custom values."""
        env = Environment(
            packages_dir=Path("custom_packages"),
            log_level="DEBUG",
            log_path=Path("custom_logs"),
        )

        assert env.packages_dir == Path("custom_packages")
        assert env.log_level == "DEBUG"
        assert env.log_path == Path("custom_logs")

    def test_from_env_file_not_found(self) -> None:
        """Test loading from a non-existent .env file."""
        with (
            patch("setupwize.core.environment.load_dotenv") as mock_load_dotenv,
            patch("setupwize.core.environment.Path.exists", return_value=False),
            patch.dict(os.environ, {}, clear=True),
        ):
            env = Environment.from_env(Path("non_existent.env"))

            # Check that load_dotenv was not called
            mock_load_dotenv.assert_not_called()

            # Check default values
            assert env.packages_dir == Path("packages")
            assert env.log_level == "INFO"
            assert env.log_path == Path("logs")

    def test_from_env_with_values(self, temp_env_file: Path) -> None:
        """Test loading from an .env file with values."""
        with patch.dict(
            os.environ,
            {
                "DEFAULT_PACKAGES_DIR": "custom_packages",
                "DEFAULT_LOG_LEVEL": "DEBUG",
                "DEFAULT_LOG_PATH": "custom_logs",
            },
            clear=True,
        ):
            env = Environment.from_env(temp_env_file)

            # Check values from environment
            assert env.packages_dir == Path("custom_packages")
            assert env.log_level == "DEBUG"
            assert env.log_path == Path("custom_logs")

    def test_from_env_partial_values(self, temp_env_file: Path) -> None:
        """Test loading from an .env file with partial values."""
        with patch.dict(
            os.environ,
            {
                "DEFAULT_PACKAGES_DIR": "custom_packages",
            },
            clear=True,
        ):
            env = Environment.from_env(temp_env_file)

            # Check values from environment and defaults
            assert env.packages_dir == Path("custom_packages")
            assert env.log_level == "INFO"
            assert env.log_path == Path("logs")
