# ruff: noqa: ANN201
import filecmp
import logging
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from core.exceptions import TaskExecutionFailedError
from core.run_cmd import run_command

logger = logging.getLogger(__name__)


class Task(ABC):
    def __init__(self, task_name: str) -> None:
        self.task_name: str = task_name

    @abstractmethod
    def execute(self):
        pass


class AptTask(Task):
    def __init__(
        self, action: str, package: str | list[str] | None = None, repo: str | None = None, verbose: bool = False
    ) -> None:
        """
        action: accept (update, install, add_repo)
        """
        super().__init__("apt_interface")
        if not action:
            raise ValueError("Action cannot be empty")
        accepted_actions = ["update", "install", "add_repo"]
        if action not in accepted_actions:
            raise ValueError(f"Invalid action: {action}")

        if isinstance(package, str):
            package = [package]

        if action == "add_repo" and not repo:
            raise ValueError("Repo cannot be empty")

        if action == "install" and not package:
            raise ValueError("Package cannot be empty")

        self.action: str = action
        self.verbose: bool = verbose
        if package:
            self.package: list[str] = package
        if repo:
            self.repo: str = repo

    @staticmethod
    def __update_cmd() -> list[str]:
        """
        Update the system.

        Returns:
            A list of strings representing the command to execute.
        """
        return ["sudo", "-S", "apt-get", "update", "-y"]

    @staticmethod
    def __install_cmd(packages: list[str]) -> list[str]:
        """
        Install packages using apt-get.

        Args:
            packages: The package name(s) to install (str or list of str).

        Returns:
            A list of strings representing the command to execute.

        Examples:
            - install_cmd(["git", "curl"])
        """
        cmd = ["sudo", "-S", "apt-get", "install", "-y"]
        cmd.extend(packages)

        return cmd

    @staticmethod
    def __add_repository_cmd(repo: str) -> list[str]:
        """
        Add a repository using apt-add-repository.

        Args:
            repo: The repository to add.

        Returns:
            A list of strings representing the command to execute.

        Example:
            add_repository_cmd("ppa:git-core/ppa")
        """
        return ["sudo", "-S", "apt-add-repository", "-y", repo]

    def execute(self):
        if self.action == "update":
            run_command(self.__update_cmd(), verbose=self.verbose)
        elif self.action == "install":
            run_command(self.__install_cmd(self.package), verbose=self.verbose)
        elif self.action == "add_repo":
            run_command(self.__add_repository_cmd(self.repo), verbose=self.verbose)
        elif self.action == "add_repo":
            run_command(self.__add_repository_cmd(self.repo), verbose=self.verbose)
            run_command(self.__update_cmd(), verbose=self.verbose)


class CommandTask(Task):
    def __init__(self, command: str, verbose: bool = False) -> None:
        super().__init__("shell_interface")
        if not command:
            raise ValueError("Command cannot be empty")

        self.command: str = command
        self.verbose: bool = verbose

    @staticmethod
    def __run_shell_cmd(cmd: str) -> list[str]:
        """
        Run a shell command like command with | or &&.

        Returns:
            A list of strings representing the command to execute.

        Example:
            cat file.txt | grep 'pattern' && echo 'found' || echo 'not found'
        """
        return ["/bin/sh", "-c", rf"{cmd}"]  # ensure pass the cmd as raw text

    def execute(self):
        try:
            run_command(self.__run_shell_cmd(self.command), verbose=self.verbose)
        except Exception as e:
            raise TaskExecutionFailedError(f"'{self.task_name}' failed: {e}")


class GnomeSettingsTask(Task):
    """
    Represents a task for setting or getting Gnome settings.
    """

    def __init__(self, action: str, schema: str, key: str, value: str = "", verbose: bool = False) -> None:
        """
        Initializes a GnomeSettingsTask.

        Args:
            action: The action to perform ("set" or "get").
            schema: The Gnome schema (e.g., "org.gnome.desktop.screensaver").
            key: The setting key (e.g., "lock-enabled").
            value: The value to set (only for "set" action).
            verbose: Whether to display verbose output during execution.
        """
        super().__init__("gnome_settings_task")
        self.action = action
        self.schema = schema
        self.key = key
        self.value = value
        self.verbose = verbose

        if self.action not in ("set", "get"):
            raise ValueError("Invalid action for GnomeSettingsTask. Must be 'set' or 'get'.")
        if self.action == "set" and self.value is None:
            raise ValueError("Value must be provided for 'set' action.")

    @staticmethod
    def __set_gnome_settings(schema: str, key: str, value: str) -> list[str]:
        """
        Set Gnome settings using gsettings.

        Returns:
            A list of strings representing the command to execute.
        """
        return ["gsettings", "set", schema, key, value]

    @staticmethod
    def __get_gnome_settings(schema: str, key: str) -> list[str]:
        """
        Get Gnome settings using gsettings.

        Returns:
            A list of strings representing the command to execute.
        """
        if not key:
            raise ValueError("Key must be provided for 'get' action.")
        return ["gsettings", "get", schema, key]

    def execute(self):
        if self.action == "set":
            run_command(self.__set_gnome_settings(self.schema, self.key, self.value), verbose=self.verbose)
        elif self.action == "get":
            run_command(self.__get_gnome_settings(self.schema, self.key), verbose=self.verbose)


class ConfigurationTask(Task):
    """
    Represents a task for copying configuration files and optionally executing commands.
    """

    def __init__(
        self,
        config_paths: list[str],
        destinations: list[str],
        command: str | None = None,
        clean_up_cmd: str | None = None,
        verbose: bool = False,
    ) -> None:
        """
        Initializes a ConfigurationTask

        Args:
            config_paths: A list of paths to configuration files/directories.
            destinations: A list of corresponding destination paths.
            command: (Optional) A shell command to execute after copying.
            verbose: Whether to display verbose output.
        """
        super().__init__("configuration_task")
        self.config_paths = config_paths
        self.destinations = destinations
        self.command = command
        self.verbose = verbose
        self.clean_up_cmd = clean_up_cmd

        if not self.config_paths or not self.destinations:
            logger.warning("No configuration paths or destinations provided. Skipping task.")
            return

        if len(self.config_paths) != len(self.destinations):
            raise ValueError("Number of config_paths and destinations must match.")

    def execute(self):
        if self.command:
            # logger.info(f"Executing post-configuration command: {self.command}")
            try:
                run_command(["/bin/sh", "-c", self.command], verbose=self.verbose)
            except Exception as e:
                raise TaskExecutionFailedError(f"'{self.task_name}' failed: {e}")

        for config_path, dest in zip(self.config_paths, self.destinations, strict=False):
            config_source: Path = Path(config_path).expanduser()
            config_dest = Path(dest).expanduser()

            if not config_source.exists():
                logger.error(f"Configuration not found: {config_source}")
                raise TaskExecutionFailedError(
                    f"Configuration task '{self.task_name}' failed: {config_source} not found"
                )

            try:
                if config_dest.exists():
                    if config_source.is_file() and filecmp.cmp(config_source, config_dest):
                        logger.info(f"Files are identical, skipping copy for '{config_path}' to '{dest}'")
                        continue  # Skip if files are the same

                    # Backup the existing file or directory at the destination
                    backup_dest = config_dest.with_suffix(".bak")

                    # Remove existing backup if it exists
                    if backup_dest.exists():
                        if backup_dest.is_dir():
                            shutil.rmtree(backup_dest)
                        else:
                            backup_dest.unlink()
                        logger.info(f"Removed existing backup at '{backup_dest}'")

                    if config_source.is_file() and config_dest.is_dir():
                        # Backup the existing file within the destination directory
                        existing_file = config_dest / config_source.name
                        if existing_file.exists():
                            backup_dest = existing_file.with_suffix(".bak")
                            logger.info(f"Backing up existing file to '{backup_dest}'")
                            shutil.move(existing_file, backup_dest)
                    else:
                        # Backup the existing file or directory at the destination
                        backup_dest = config_dest.with_suffix(".bak")
                        logger.info(f"Backing up existing configuration to '{backup_dest}'")
                        if config_dest.is_dir():
                            shutil.move(config_dest, backup_dest)
                        else:
                            shutil.copy2(config_dest, backup_dest)

                config_dest.parent.mkdir(parents=True, exist_ok=True)
                if config_source.is_dir():
                    shutil.copytree(config_source, config_dest)
                else:
                    shutil.copy2(config_source, config_dest)

                logger.info(f"Configuration copied from '{config_source}' to '{config_dest}'")
            except Exception as e:
                raise TaskExecutionFailedError(f"Configuration task '{self.task_name}' failed: {e}")

        if self.clean_up_cmd:
            try:
                logger.info("Preform cleanup...")
                run_command(["/bin/sh", "-c", self.clean_up_cmd], verbose=self.verbose)
            except Exception as e:
                raise TaskExecutionFailedError(f"'{self.task_name}' failed: {e}")


def create_task_from_config(task_data: dict[str, Any], verbose: bool = False) -> Task:
    """
    Creates a Task object based on the provided YAML configuration.

    Args:
        task_data: A dictionary containing the task's type and configuration.

    Returns:
        A Task object of the appropriate type.

    Raises:
        ValueError: If the task type is not recognized.
    """
    task_type = task_data["type"]

    if task_type == "apt":
        return AptTask(
            action=task_data["action"],
            package=task_data.get("packages", []),
            repo=task_data.get("repo", ""),
            verbose=verbose,
        )
    elif task_type == "shell":
        return CommandTask(
            command=task_data["command"],
            verbose=verbose,
        )
    elif task_type == "gnome_settings":
        return GnomeSettingsTask(
            action=task_data["action"],
            schema=task_data["schema"],
            key=task_data["key"],
            value=task_data.get("value", ""),
            verbose=verbose,
        )
    elif task_type == "configuration":
        return ConfigurationTask(
            config_paths=task_data.get("config_path", ""),
            destinations=task_data.get("destination", ""),
            command=task_data.get("command", []),
            clean_up_cmd=task_data.get("clean_up_cmd", ""),
            verbose=verbose,
        )
    else:
        raise ValueError(f"Unrecognized task type: {task_type}")
