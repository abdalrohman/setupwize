import logging
from pathlib import Path

from dotenv import load_dotenv

# define logger
logger = logging.getLogger(__name__)


# Env loader class (Must be at the first to load the .env file)
class EnvironmentLoader:
    """
    A class to load and verify environment variables from a .env file.
    """

    def __init__(self, env_file_path: str | Path = ".env"):
        """
        Initializes the EnvironmentLoader.

        Args:
            env_file_path: Path to the .env file relative to the project root. Defaults to "PROJECT_ROOT/.env".
            required_vars: List of required environment variables.
        """
        if isinstance(env_file_path, str):
            env_file_path = Path(env_file_path)
        self.env_file_path = env_file_path.resolve()

    def load_envs(self) -> None:
        """
        Loads environment variables from the .env file and verifies required variables.
        """
        logger.info(f"Loading environment variables from {self.env_file_path}...")

        if not self.env_file_path.is_file():
            logger.warning(f".env file not found at {self.env_file_path}")
            return

        load_dotenv(dotenv_path=self.env_file_path, override=False)
