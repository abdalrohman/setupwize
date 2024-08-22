from pathlib import Path
from typing import Any

from core.exceptions import InvalidYamlFormatError, PackageNotFoundError

import yaml


class YamlParser:
    """
    Handles the reading and parsing of YAML files.
    """

    def __init__(self, packages_dir: str = "packages"):
        """
        Initializes the YamlParser.

        Args:
            packages_dir: The directory containing the YAML package files.
        """
        self.packages_dir = Path(packages_dir)

    def load_package(self, package_name: str) -> dict[str, Any]:
        """
        Loads and parses the YAML file for the specified package.
        """
        package_file = self.packages_dir / f"{package_name}.yaml"

        if not package_file.exists():
            raise PackageNotFoundError(f"Package '{package_name}' not found.")

        try:
            with package_file.open("r") as f:
                data: dict[str, Any] = yaml.safe_load(f)
                return data
        except yaml.YAMLError as e:
            raise InvalidYamlFormatError(f"Error parsing YAML for '{package_name}': {e}")

    def get_available_packages(self) -> list[str]:
        """
        Returns a list of available packages in the packages directory.

        Returns:
            A list of package names (without the .yaml extension).
        """
        return [f.stem for f in self.packages_dir.iterdir() if f.is_file() and f.suffix == ".yaml"]

    def load_all_packages(self) -> list[dict[str, Any]]:
        """
        Loads and parses all YAML files in the packages directory
        """
        all_packages = []
        for package_name in self.get_available_packages():
            try:
                package_data = self.load_package(package_name)
                all_packages.append(package_data)
            except (PackageNotFoundError, InvalidYamlFormatError) as e:
                print(str(e))
        return all_packages
