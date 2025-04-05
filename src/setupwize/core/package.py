"""Package management for SetUpWize."""

import logging
from dataclasses import dataclass, field
from typing import Any

from ..core.exceptions import PackageNameMismatchError, PackageNotFoundError
from ..core.task import Task, create_task_from_config
from ..parsers.yaml_parser import YamlParser

logger = logging.getLogger(__name__)


@dataclass
class Package:
    """A software package to be installed."""

    name: str
    description: str = ""
    category: str = "Uncategorized"
    tasks: list[Task] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    verbose: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any], verbose: bool = False) -> "Package":
        """Create a Package from a dictionary.

        Args:
            data: A dictionary containing package data.
            verbose: Whether to enable verbose output.

        Returns:
            A Package object.

        Raises:
            ValueError: If the package data is invalid.
        """
        # Validate required fields
        if "name" not in data:
            raise ValueError("Package data must contain a 'name' key.")

        # Create tasks
        tasks = []
        if "tasks" in data:
            if not isinstance(data["tasks"], list):
                raise ValueError("Package 'tasks' must be a list.")

            tasks = [create_task_from_config(task_data, verbose) for task_data in data["tasks"]]

        # Get dependencies
        dependencies = []
        if "dependencies" in data:
            if not isinstance(data["dependencies"], list):
                raise ValueError("Package 'dependencies' must be a list.")

            for dep in data["dependencies"]:
                if not isinstance(dep, str):
                    raise TypeError("Package dependencies must be strings.")

            dependencies = data["dependencies"]

        # Create package
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", "Uncategorized"),
            tasks=tasks,
            dependencies=dependencies,
            verbose=verbose,
        )

    def install(self) -> None:
        """Install the package."""
        logger.info(f"Starting installation of package '{self.name}'...")

        # Install dependencies if any
        if self.dependencies:
            # Import here to avoid circular imports
            from ..core.task import AptExecutor

            logger.info(
                f"Installing dependencies for '{self.name}': {', '.join(self.dependencies)}"
            )

            # Create and execute a task for installing dependencies
            executor = AptExecutor(
                action="install",
                packages=self.dependencies,
                verbose=self.verbose,
            )

            dependency_task = Task(
                name=f"install_dependencies_{self.name}",
                executor=executor,
                verbose=self.verbose,
            )

            dependency_task.execute()

        # Execute tasks
        for task in self.tasks:
            task.execute()

        logger.info(f"Package '{self.name}' installed successfully!")


def create_package_from_yaml(
    package_name: str,
    yaml_parser: YamlParser,
    verbose: bool = False,
) -> Package:
    """Create a Package object from a YAML file.

    Args:
        package_name: The name of the package.
        yaml_parser: A YamlParser instance.
        verbose: Whether to enable verbose output.

    Returns:
        A Package object.

    Raises:
        PackageNotFoundError: If the package YAML file is not found.
        PackageNameMismatchError: If the package name in the YAML file does not match the filename.
    """
    # Load package data
    all_packages_data = yaml_parser.load_package(package_name)

    # Find the specific package data
    for package_data in all_packages_data.get("packages", []):
        if package_data.get("name") != package_name:
            raise PackageNameMismatchError(
                expected=package_name, actual=package_data.get("name", "")
            )

        return Package.from_dict(package_data, verbose)

    # If we get here, the package was not found
    raise PackageNotFoundError(package_name)
