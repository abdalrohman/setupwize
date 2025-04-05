"""Tests for the task module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from setupwize.core.exceptions import TaskExecutionFailedError
from setupwize.core.task import (
    AptExecutor,
    ConfigurationExecutor,
    GnomeSettingsExecutor,
    ShellExecutor,
    Task,
    create_task_from_config,
)


class TestTask:
    """Tests for the Task class."""

    def test_init(self) -> None:
        """Test initialization."""
        executor = MagicMock()
        task = Task(name="test", executor=executor, verbose=True)
        assert task.name == "test"
        assert task.executor == executor
        assert task.verbose is True

    def test_execute_success(self) -> None:
        """Test successful execution."""
        executor = MagicMock()
        task = Task(name="test", executor=executor, verbose=True)
        task.execute()
        executor.execute.assert_called_once()

    def test_execute_failure(self) -> None:
        """Test execution failure."""
        executor = MagicMock()
        executor.execute.side_effect = Exception("Test error")
        task = Task(name="test", executor=executor, verbose=True)
        with pytest.raises(TaskExecutionFailedError):
            task.execute()


class TestAptExecutor:
    """Tests for the AptExecutor class."""

    def test_init(self) -> None:
        """Test initialization."""
        executor = AptExecutor(
            action="install",
            packages=["package1", "package2"],
            repo="ppa:test/repo",
            verbose=True,
        )
        assert executor.action == "install"
        assert executor.packages == ["package1", "package2"]
        assert executor.repo == "ppa:test/repo"
        assert executor.verbose is True

    @patch("setupwize.core.task.run_command")
    @patch("setupwize.core.task.is_running_on_kde_neon")
    def test_execute_install_kde_neon(self, mock_is_kde_neon, mock_run_command) -> None:
        """Test execute install on KDE Neon."""
        mock_is_kde_neon.return_value = True
        mock_run_command.return_value = MagicMock(success=True)

        executor = AptExecutor(
            action="install",
            packages=["package1", "package2"],
            verbose=True,
        )
        executor.execute()

        # Check that run_command was called for each package
        assert mock_run_command.call_count == 2
        mock_run_command.assert_any_call(
            ["sudo", "pkcon", "install", "-y", "package1"],
            verbose=True,
            check=True,
        )
        mock_run_command.assert_any_call(
            ["sudo", "pkcon", "install", "-y", "package2"],
            verbose=True,
            check=True,
        )

    @patch("setupwize.core.task.run_command")
    @patch("setupwize.core.task.is_running_on_kde_neon")
    def test_execute_install_ubuntu(self, mock_is_kde_neon, mock_run_command) -> None:
        """Test execute install on Ubuntu."""
        mock_is_kde_neon.return_value = False
        mock_run_command.return_value = MagicMock(success=True)

        executor = AptExecutor(
            action="install",
            packages=["package1", "package2"],
            verbose=True,
        )
        executor.execute()

        # Check that run_command was called for each package
        assert mock_run_command.call_count == 2
        mock_run_command.assert_any_call(
            ["sudo", "apt-get", "install", "-y", "package1"],
            verbose=True,
            check=True,
        )
        mock_run_command.assert_any_call(
            ["sudo", "apt-get", "install", "-y", "package2"],
            verbose=True,
            check=True,
        )

    @patch(
        "setupwize.core.task.AptExecutor._add_repository_cmd",
        return_value=["sudo", "add-apt-repository", "-y", "ppa:test/repo"],
    )
    @patch(
        "setupwize.core.task.AptExecutor._update_cmd", return_value=["sudo", "apt-get", "update"]
    )
    @patch("setupwize.core.task.run_command")
    def test_execute_add_repo(self, mock_run_command, mock_update_cmd, mock_add_repo_cmd) -> None:
        """Test execute add repository."""
        mock_run_command.return_value = MagicMock(success=True)

        executor = AptExecutor(
            action="add_repo",
            repo="ppa:test/repo",
            verbose=True,
        )
        executor.execute()

        assert mock_run_command.call_count == 2
        mock_add_repo_cmd.assert_called_once_with("ppa:test/repo")
        mock_update_cmd.assert_called_once()

    @patch(
        "setupwize.core.task.AptExecutor._update_cmd", return_value=["sudo", "apt-get", "update"]
    )
    @patch("setupwize.core.task.run_command")
    def test_execute_update(self, mock_run_command, mock_update_cmd) -> None:
        """Test execute update."""
        mock_run_command.return_value = MagicMock(success=True)

        executor = AptExecutor(
            action="update",
            verbose=True,
        )
        executor.execute()

        mock_run_command.assert_called_once()
        mock_update_cmd.assert_called_once()

    def test_execute_invalid_action(self) -> None:
        """Test execute with invalid action."""
        with pytest.raises(ValueError, match="Invalid action: invalid"):
            AptExecutor(
                action="invalid",
                verbose=True,
            )


class TestShellExecutor:
    """Tests for the ShellExecutor class."""

    def test_init(self) -> None:
        """Test initialization."""
        executor = ShellExecutor(
            command="echo 'test'",
            verbose=True,
        )
        assert executor.command == "echo 'test'"
        assert executor.verbose is True

    @patch("setupwize.core.task.run_command")
    def test_execute(self, mock_run_command) -> None:
        """Test execute."""
        mock_run_command.return_value = MagicMock(success=True)

        executor = ShellExecutor(
            command="echo 'test'",
            verbose=True,
        )
        executor.execute()

        mock_run_command.assert_called_once_with(
            ["bash", "-c", "echo 'test'"],
            verbose=True,
            check=True,
        )


class TestConfigurationExecutor:
    """Tests for the ConfigurationExecutor class."""

    def test_init(self) -> None:
        """Test initialization."""
        executor = ConfigurationExecutor(
            config_paths=[Path("/path/to/config1"), Path("/path/to/config2")],
            destinations=[Path("/path/to/dest1"), Path("/path/to/dest2")],
            verbose=True,
        )
        assert executor.config_paths == [Path("/path/to/config1"), Path("/path/to/config2")]
        assert executor.destinations == [Path("/path/to/dest1"), Path("/path/to/dest2")]
        assert executor.verbose is True

    @patch("setupwize.core.task.shutil.copy2")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_execute(self, mock_mkdir, mock_exists, mock_copy2) -> None:
        """Test execute."""

        # Mock Path.exists to return True for config paths
        mock_exists.return_value = True

        executor = ConfigurationExecutor(
            config_paths=[Path("/path/to/config1"), Path("/path/to/config2")],
            destinations=[Path("/path/to/dest1"), Path("/path/to/dest2")],
            verbose=True,
        )
        executor.execute()

        assert mock_mkdir.call_count == 2
        assert mock_copy2.call_count == 2
        mock_exists.assert_any_call()
        mock_copy2.assert_any_call(Path("/path/to/config1"), Path("/path/to/dest1"))
        mock_copy2.assert_any_call(Path("/path/to/config2"), Path("/path/to/dest2"))

    def test_execute_mismatched_lengths(self) -> None:
        """Test execute with mismatched lengths."""
        executor = ConfigurationExecutor(
            config_paths=[Path("/path/to/config1"), Path("/path/to/config2")],
            destinations=[Path("/path/to/dest1")],
            verbose=True,
        )
        with pytest.raises(ValueError, match="Mismatched lengths"):
            executor.execute()


class TestGnomeSettingsExecutor:
    """Tests for the GnomeSettingsExecutor class."""

    def test_init(self) -> None:
        """Test initialization."""
        executor = GnomeSettingsExecutor(
            settings={"org.gnome.desktop.interface": {"gtk-theme": "Adwaita-dark"}},
            verbose=True,
        )
        assert executor.settings == {"org.gnome.desktop.interface": {"gtk-theme": "Adwaita-dark"}}
        assert executor.verbose is True

    @patch("setupwize.core.task.run_command")
    def test_execute(self, mock_run_command) -> None:
        """Test execute."""
        mock_run_command.return_value = MagicMock(success=True)

        executor = GnomeSettingsExecutor(
            settings={"org.gnome.desktop.interface": {"gtk-theme": "Adwaita-dark"}},
            verbose=True,
        )
        executor.execute()

        mock_run_command.assert_called_once_with(
            ["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Adwaita-dark"],
            verbose=True,
            check=True,
        )

    @patch("setupwize.core.task.run_command")
    def test_execute_multiple_settings(self, mock_run_command) -> None:
        """Test execute with multiple settings."""
        mock_run_command.return_value = MagicMock(success=True)

        executor = GnomeSettingsExecutor(
            settings={
                "org.gnome.desktop.interface": {
                    "gtk-theme": "Adwaita-dark",
                    "icon-theme": "Adwaita",
                }
            },
            verbose=True,
        )
        executor.execute()

        assert mock_run_command.call_count == 2
        mock_run_command.assert_any_call(
            ["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Adwaita-dark"],
            verbose=True,
            check=True,
        )
        mock_run_command.assert_any_call(
            ["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", "Adwaita"],
            verbose=True,
            check=True,
        )


class TestCreateTaskFromConfig:
    """Tests for the create_task_from_config function."""

    def test_create_apt_task(self) -> None:
        """Test creating an apt task."""
        task_config = {
            "type": "apt",
            "action": "install",
            "packages": ["package1", "package2"],
            "repo": "ppa:test/repo",
        }
        task = create_task_from_config(task_config, verbose=True)
        assert task.name == "apt_install"
        assert isinstance(task.executor, AptExecutor)
        assert task.executor.action == "install"
        assert task.executor.packages == ["package1", "package2"]
        assert task.executor.repo == "ppa:test/repo"
        assert task.verbose is True

    def test_create_shell_task(self) -> None:
        """Test creating a shell task."""
        task_config = {
            "type": "shell",
            "command": "echo 'test'",
        }
        task = create_task_from_config(task_config, verbose=True)
        assert task.name == "shell_command"
        assert isinstance(task.executor, ShellExecutor)
        assert task.executor.command == "echo 'test'"
        assert task.verbose is True

    def test_create_configuration_task(self) -> None:
        """Test creating a configuration task."""
        task_config = {
            "type": "configuration",
            "config_path": ["/path/to/config1", "/path/to/config2"],
            "destination": ["/path/to/dest1", "/path/to/dest2"],
        }
        task = create_task_from_config(task_config, verbose=True)
        assert task.name == "configuration"
        assert isinstance(task.executor, ConfigurationExecutor)
        assert task.executor.config_paths == [Path("/path/to/config1"), Path("/path/to/config2")]
        assert task.executor.destinations == [Path("/path/to/dest1"), Path("/path/to/dest2")]
        assert task.verbose is True

    def test_create_gnome_settings_task(self) -> None:
        """Test creating a gnome_settings task."""
        task_config = {
            "type": "gnome_settings",
            "settings": {"org.gnome.desktop.interface": {"gtk-theme": "Adwaita-dark"}},
        }
        task = create_task_from_config(task_config, verbose=True)
        assert task.name == "gnome_settings"
        assert isinstance(task.executor, GnomeSettingsExecutor)
        assert task.executor.settings == {
            "org.gnome.desktop.interface": {"gtk-theme": "Adwaita-dark"}
        }
        assert task.verbose is True

    def test_create_invalid_task(self) -> None:
        """Test creating an invalid task."""
        task_config = {
            "type": "invalid",
        }
        with pytest.raises(ValueError, match="Unknown task type: invalid"):
            create_task_from_config(task_config, verbose=True)
