"""Environment configuration module for SetUpWize."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class Environment:
    """Environment configuration for SetUpWize."""

    packages_dir: Path = field(default_factory=lambda: Path("packages"))
    log_level: str = "INFO"
    log_path: Path = field(default_factory=lambda: Path("logs"))

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "Environment":
        """Create an Environment instance from environment variables.

        Args:
            env_file: Path to the .env file. If None, uses the default .env file.

        Returns:
            An Environment instance with values from environment variables.
        """
        if env_file is None:
            env_file = Path(".env")

        # Load environment variables
        if env_file.exists():
            logger.info(f"Loading environment variables from {env_file}")
            load_dotenv(dotenv_path=env_file, override=False)
        else:
            logger.warning(f".env file not found at {env_file}")

        # Get environment variables with defaults
        import os

        packages_dir = Path(os.environ.get("DEFAULT_PACKAGES_DIR", "packages"))
        log_level = os.environ.get("DEFAULT_LOG_LEVEL", "INFO")
        log_path = Path(os.environ.get("DEFAULT_LOG_PATH", "logs"))

        return cls(
            packages_dir=packages_dir,
            log_level=log_level,
            log_path=log_path,
        )
