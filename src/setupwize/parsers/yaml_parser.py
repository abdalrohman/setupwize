"""YAML parser for SetUpWize."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from ..core.exceptions import InvalidYamlFormatError, PackageNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class YamlParser:
    """Parser for YAML package files."""

    packages_dir: Path

    def __init__(self, packages_dir: str | Path = "packages"):
        """Initialize the parser.

        Args:
            packages_dir: The directory containing package YAML files.
        """
        self.packages_dir = Path(packages_dir)

    def load_package(self, package_name: str) -> dict[str, Any]:
        """Load and parse a package YAML file.

        Args:
            package_name: The name of the package (without .yaml extension).

        Returns:
            A dictionary containing the parsed YAML data.

        Raises:
            PackageNotFoundError: If the package file is not found.
            InvalidYamlFormatError: If the YAML file has an invalid format.
        """
        package_file = self.packages_dir / f"{package_name}.yaml"

        if not package_file.exists():
            raise PackageNotFoundError(package_name)

        try:
            with package_file.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

                if not isinstance(data, dict):
                    raise InvalidYamlFormatError(
                        f"Invalid YAML format in '{package_name}.yaml': not a dictionary"
                    )

                # Check if the package name matches the filename
                if "name" in data and data["name"] != package_name:
                    raise InvalidYamlFormatError(
                        f"Package name '{data['name']}' does not match filename '{package_name}'"
                    )

                return data
        except yaml.YAMLError as e:
            raise InvalidYamlFormatError(f"Invalid YAML format in package '{package_name}': {e}")

    def get_available_packages(self) -> list[str]:
        """Get a list of available package names.

        Returns:
            A list of package names (without .yaml extension).
        """
        try:
            return [f.stem for f in self.packages_dir.glob("*.yaml")]
        except Exception as e:
            logger.warning(f"Error getting available packages: {e}")
            return []

    def load_all_packages(self) -> list[dict[str, Any]]:
        """Load and parse all package YAML files.

        Returns:
            A list of dictionaries containing the parsed YAML data.
        """
        all_packages: list[dict[str, list[dict[str, str]]]] = []
        available_packages = self.get_available_packages()

        if not available_packages:
            logger.warning("No package files found in directory: %s", self.packages_dir)
            return all_packages

        for package_name in available_packages:
            try:
                package_data = self.load_package(package_name)
                all_packages.append(package_data)
            except PackageNotFoundError:
                logger.warning(f"Package file for '{package_name}' not found")
            except InvalidYamlFormatError as e:
                logger.warning(f"Error loading package '{package_name}': {e}")
            except Exception as e:
                logger.exception(f"Unexpected error loading package '{package_name}': {e}")

        return all_packages
