import logging
from typing import Any

from core.exceptions import PackageNameMismatchError, PackageNotFoundError
from core.tasks import AptTask, Task, create_task_from_config
from parser import YamlParser

logger = logging.getLogger(__name__)


# TODO add validation to package
class Package:
    """
    Represents a software package to be installed,
    holding its metadata and installation tasks.
    """

    def __init__(self, package_data: dict[str, Any], verbose: bool = False):
        """
        Initializes a Package object from parsed YAML data.

        Args:
            package_data: A dictionary containing the package's metadata and tasks.
        """
        self.name: str = package_data["name"]
        self.description: str = package_data.get("description", "")
        self.verbose: bool = verbose
        self.tasks: list[Task] = self._create_tasks(package_data["tasks"])
        self.dependencies: list[str] = package_data.get("dependencies", [])

    def _create_tasks(self, tasks_data: list[dict[str, Any]]) -> list[Task]:
        """
        Creates Task objects from the YAML task definitions.

        Args:
            tasks_data: A list of dictionaries representing the tasks.

        Returns:
            A list of Task objects.
        """
        return [create_task_from_config(task_data, self.verbose) for task_data in tasks_data]

    def install(self) -> None:
        """
        Executes the installation tasks for this package.
        """
        logger.info(f"Starting installation of package '{self.name}'...")
        if self.dependencies:
            # assume all dependencies are installed using apt
            AptTask(
                action="install",
                package=self.dependencies,
                verbose=self.verbose,
            ).execute()

        for task in self.tasks:
            task.execute()
            logger.info(f"Task: '{task.task_name}' completed successfully for package '{self.name}'")

        logger.info(f"Package '{self.name}' installed successfully!")


def create_package_from_yaml(
    package_name: str,
    yaml_parser: YamlParser,
    verbose: bool = False,
) -> Package:
    """
    Creates a Package object by loading and parsing the YAML file.

    Args:
        package_name: The name of the package (without the .yaml extension).
        yaml_parser: An instance of YamlParser for loading YAML data.

    Returns:
        A Package object representing the parsed package.
    """
    all_packages_data: dict[str, Any] = yaml_parser.load_package(package_name)

    # Find the specific package data from the list
    for package_data in all_packages_data["packages"]:
        if package_data["name"] != package_name:
            raise PackageNameMismatchError(
                f"Package name mismatch: Expected '{package_name}', got '{package_data['name']}'"
            )
        return Package(package_data, verbose)

    raise PackageNotFoundError(f"Package '{package_name}' not found in the YAML data.")
