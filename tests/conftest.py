"""Test fixtures for SetUpWize."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def temp_env_file(temp_dir: Path) -> Path:
    """Create a temporary .env file for tests."""
    env_file = temp_dir / ".env"
    env_content = """
    DEFAULT_PACKAGES_DIR=packages
    DEFAULT_LOG_LEVEL=INFO
    DEFAULT_LOG_PATH=logs
    """
    env_file.write_text(env_content.strip())
    return env_file


@pytest.fixture
def temp_package_dir(temp_dir: Path) -> Path:
    """Create a temporary packages directory with a sample package."""
    package_dir = temp_dir / "packages"
    package_dir.mkdir(exist_ok=True)

    # Create a sample package file
    sample_package = package_dir / "sample.yaml"
    sample_content = """
    packages:
      - name: sample
        description: Sample package for testing
        category: Testing
        tasks:
          - type: shell
            command: echo "Hello, world!"
    """
    sample_package.write_text(sample_content.strip())

    return package_dir
