"""Task management for SetUpWize."""

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from ..core.exceptions import TaskExecutionFailedError
from ..core.shell import run_command
from ..utils.system import is_running_on_kde_neon

logger = logging.getLogger(__name__)


class TaskExecutor(Protocol):
    """Protocol for task executors."""

    def execute(self) -> None:
        """Execute the task."""
        ...


@dataclass
class Task:
    """Base task class using composition over inheritance."""

    name: str
    executor: TaskExecutor
    verbose: bool = False

    def execute(self) -> None:
        """Execute the task."""
        logger.info(f"Executing task: {self.name}")
        try:
            self.executor.execute()
            logger.info(f"Task '{self.name}' completed successfully")
        except Exception as e:
            logger.exception(f"Task '{self.name}' failed")
            raise TaskExecutionFailedError(task_name=self.name) from e


@dataclass
class AptExecutor:
    """Executor for APT package management tasks."""

    action: str
    packages: list[str] = field(default_factory=list)
    repo: str | None = None
    verbose: bool = False

    def __post_init__(self) -> None:
        """Validate the task configuration."""
        if not self.action:
            raise ValueError("Action cannot be empty")

        accepted_actions = ["update", "install", "add_repo"]
        if self.action not in accepted_actions:
            raise ValueError(f"Invalid action: {self.action}")

        if self.action == "add_repo" and not self.repo:
            raise ValueError("Repo cannot be empty")

        if self.action == "install" and not self.packages:
            raise ValueError("Packages cannot be empty")

    def _update_cmd(self) -> list[str]:
        """Get the command for updating package lists."""
        if is_running_on_kde_neon():
            return ["sudo", "pkcon", "update", "-y"]
        return ["sudo", "apt-get", "-y", "update"]

    def _install_cmd(self, packages: list[str]) -> list[str]:
        """Get the command for installing packages."""
        if is_running_on_kde_neon():
            return ["sudo", "pkcon", "install", "-y", *packages]
        return ["sudo", "apt-get", "install", "-y", *packages]

    def _add_repository_cmd(self, repo: str) -> list[str]:
        """Get the command for adding a repository."""
        return ["sudo", "add-apt-repository", "-y", repo]

    def execute(self) -> None:
        """Execute the APT task."""
        if self.action == "update":
            result = run_command(
                self._update_cmd(), success_code=[0, 5], verbose=self.verbose, check=True
            )
            if not result.success:
                raise TaskExecutionFailedError(
                    task_name="apt_update",
                    command=" ".join(result.command),
                    exit_code=result.exit_code,
                )

        elif self.action == "install":
            if is_running_on_kde_neon() and len(self.packages) > 1:
                # For KDE Neon, install packages one by one
                for pkg in self.packages:
                    logger.info(f"Installing package: {pkg}")
                    result = run_command(
                        ["sudo", "pkcon", "install", "-y", pkg],
                        verbose=self.verbose,
                        check=True,
                        success_code=[0, 5],
                    )
                    if not result.success:
                        raise TaskExecutionFailedError(
                            task_name=f"apt_install_{pkg}",
                            command=" ".join(result.command),
                            exit_code=result.exit_code,
                        )
            else:
                # For Ubuntu or single package on KDE Neon
                for pkg in self.packages:
                    logger.info(f"Installing package: {pkg}")
                    result = run_command(
                        self._install_cmd([pkg]),
                        verbose=self.verbose,
                        check=True,
                        success_code=[0, 5],
                    )
                    if not result.success:
                        raise TaskExecutionFailedError(
                            task_name=f"apt_install_{pkg}",
                            command=" ".join(result.command),
                            exit_code=result.exit_code,
                        )

        elif self.action == "add_repo":
            if not self.repo:
                raise ValueError("Repo cannot be empty")

            # Add repository
            result = run_command(
                self._add_repository_cmd(self.repo),
                verbose=self.verbose,
                check=True,
            )
            if not result.success:
                raise TaskExecutionFailedError(
                    task_name="apt_add_repo",
                    command=" ".join(result.command),
                    exit_code=result.exit_code,
                )

            # Update after adding repo
            update_result = run_command(
                self._update_cmd(),
                success_code=[0, 5],
                verbose=self.verbose,
                check=True,
            )
            if not update_result.success:
                raise TaskExecutionFailedError(
                    task_name="apt_update_after_repo",
                    command=" ".join(update_result.command),
                    exit_code=update_result.exit_code,
                )


@dataclass
class ShellExecutor:
    """Executor for shell command tasks."""

    command: str
    verbose: bool = False

    def execute(self) -> None:
        """Execute the shell command."""
        cmd = ["bash", "-c", self.command]
        result = run_command(
            cmd,
            verbose=self.verbose,
            check=True,
        )
        if not result.success:
            raise TaskExecutionFailedError(
                task_name="shell_command",
                command=self.command,
                exit_code=result.exit_code,
            )


@dataclass
class ConfigurationExecutor:
    """Executor for configuration file tasks."""

    config_paths: list[Path]
    destinations: list[Path]
    verbose: bool = False

    def execute(self) -> None:
        """Copy configuration files to their destinations."""
        if len(self.config_paths) != len(self.destinations):
            raise ValueError(
                f"Mismatched lengths: Number of config paths ({len(self.config_paths)}) "
                f"must match number of destinations ({len(self.destinations)})"
            )

        for src, dst in zip(self.config_paths, self.destinations, strict=False):
            src_path = Path(src)
            dst_path = Path(dst)

            if not src_path.exists():
                raise FileNotFoundError(f"Configuration source not found: {src_path}")

            # Create destination directory if it doesn't exist
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file or directory
            if src_path.is_dir():
                if self.verbose:
                    logger.info(f"Copying directory {src_path} to {dst_path}")
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                if self.verbose:
                    logger.info(f"Copying file {src_path} to {dst_path}")
                shutil.copy2(src_path, dst_path)


@dataclass
class GnomeSettingsExecutor:
    """Executor for GNOME settings tasks."""

    settings: dict[str, Any]
    verbose: bool = False

    def execute(self) -> None:
        """Apply GNOME settings."""
        for schema, values in self.settings.items():
            for key, value in values.items():
                cmd = ["gsettings", "set", schema, key]

                # Convert value to string based on type
                if isinstance(value, bool):
                    cmd.append("true" if value else "false")
                elif isinstance(value, int | float):
                    cmd.append(str(value))
                elif isinstance(value, list):
                    # Convert list to string representation for gsettings
                    list_str = str(value).replace("'", '"')
                    cmd.append(list_str)
                else:
                    cmd.append(str(value))

                result = run_command(cmd, verbose=self.verbose, check=True)
                if not result.success:
                    raise TaskExecutionFailedError(
                        task_name=f"gnome_settings_{schema}_{key}",
                        command=" ".join(result.command),
                        exit_code=result.exit_code,
                    )


def create_task_from_config(task_data: dict[str, Any], verbose: bool = False) -> Task:
    """Create a Task object from a configuration dictionary.

    Args:
        task_data: A dictionary containing the task configuration.
        verbose: Whether to enable verbose output.

    Returns:
        A Task object configured according to the task_data.

    Raises:
        ValueError: If the task type is not recognized.
    """
    task_type = task_data["type"]

    if task_type == "apt":
        apt_executor = AptExecutor(
            action=task_data["action"],
            packages=task_data.get("packages", []),
            repo=task_data.get("repo"),
            verbose=verbose,
        )
        return Task(name=f"apt_{task_data['action']}", executor=apt_executor, verbose=verbose)

    elif task_type == "shell":
        shell_executor = ShellExecutor(
            command=task_data["command"],
            verbose=verbose,
        )
        return Task(name="shell_command", executor=shell_executor, verbose=verbose)

    elif task_type == "configuration":
        # Convert string paths to Path objects
        config_paths = [Path(p) for p in task_data["config_path"]]
        destinations = [Path(p) for p in task_data["destination"]]

        config_executor = ConfigurationExecutor(
            config_paths=config_paths,
            destinations=destinations,
            verbose=verbose,
        )
        return Task(name="configuration", executor=config_executor, verbose=verbose)

    elif task_type == "gnome_settings":
        gnome_executor = GnomeSettingsExecutor(
            settings=task_data["settings"],
            verbose=verbose,
        )
        return Task(name="gnome_settings", executor=gnome_executor, verbose=verbose)

    else:
        raise ValueError(f"Unknown task type: {task_type}")
