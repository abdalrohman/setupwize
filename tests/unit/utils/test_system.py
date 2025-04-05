"""Tests for the system module."""

import subprocess
from unittest.mock import MagicMock, mock_open, patch

from setupwize.utils.system import confirm_reboot, confirm_system_upgrade, is_running_on_kde_neon


@patch("setupwize.utils.system.subprocess.run")
def test_is_running_on_kde_neon_true(mock_run) -> None:
    """Test is_running_on_kde_neon when running on KDE Neon."""
    mock_process = MagicMock()
    mock_process.stdout = "KDE neon User Edition 5.27"
    mock_run.return_value = mock_process

    result = is_running_on_kde_neon()
    assert result is True
    mock_run.assert_called_once_with(
        ["lsb_release", "-d"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("setupwize.utils.system.subprocess.run")
def test_is_running_on_kde_neon_false(mock_run) -> None:
    """Test is_running_on_kde_neon when not running on KDE Neon."""
    mock_process = MagicMock()
    mock_process.stdout = "Ubuntu 22.04.3 LTS"
    mock_run.return_value = mock_process

    result = is_running_on_kde_neon()
    assert result is False
    mock_run.assert_called_once_with(
        ["lsb_release", "-d"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("setupwize.utils.system.subprocess.run")
@patch("setupwize.utils.system.os.environ.get", return_value="KDE")
@patch("pathlib.Path.is_file", return_value=True)
@patch("pathlib.Path.open", new_callable=mock_open, read_data="neon")
def test_is_running_on_kde_neon_error(mock_open, mock_is_file, mock_env_get, mock_run) -> None:
    """Test is_running_on_kde_neon when an error occurs."""
    mock_run.side_effect = subprocess.SubprocessError()

    result = is_running_on_kde_neon()
    assert result is True
    mock_run.assert_called_once_with(
        ["lsb_release", "-d"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("setupwize.utils.system.questionary.confirm")
def test_confirm_system_upgrade_yes(mock_confirm) -> None:
    """Test confirm_system_upgrade when user confirms."""
    mock_confirm_instance = MagicMock()
    mock_confirm.return_value = mock_confirm_instance
    mock_confirm_instance.ask.return_value = True

    result = confirm_system_upgrade()
    assert result is True
    mock_confirm.assert_called_once_with(
        "Do you want to update and upgrade system packages?",
        default=True,
    )
    mock_confirm_instance.ask.assert_called_once()


@patch("setupwize.utils.system.questionary.confirm")
def test_confirm_system_upgrade_no(mock_confirm) -> None:
    """Test confirm_system_upgrade when user declines."""
    mock_confirm_instance = MagicMock()
    mock_confirm.return_value = mock_confirm_instance
    mock_confirm_instance.ask.return_value = False

    result = confirm_system_upgrade()
    assert result is False
    mock_confirm.assert_called_once_with(
        "Do you want to update and upgrade system packages?",
        default=True,
    )
    mock_confirm_instance.ask.assert_called_once()


@patch("setupwize.utils.system.questionary.confirm")
def test_confirm_reboot_yes(mock_confirm) -> None:
    """Test confirm_reboot when user confirms."""
    mock_confirm_instance = MagicMock()
    mock_confirm.return_value = mock_confirm_instance
    mock_confirm_instance.ask.return_value = True

    result = confirm_reboot()
    assert result is True
    mock_confirm.assert_called_once_with(
        "Some changes may require a system reboot. Do you want to reboot now?",
        default=False,
    )
    mock_confirm_instance.ask.assert_called_once()


@patch("setupwize.utils.system.questionary.confirm")
def test_confirm_reboot_no(mock_confirm) -> None:
    """Test confirm_reboot when user declines."""
    mock_confirm_instance = MagicMock()
    mock_confirm.return_value = mock_confirm_instance
    mock_confirm_instance.ask.return_value = False

    result = confirm_reboot()
    assert result is False
    mock_confirm.assert_called_once_with(
        "Some changes may require a system reboot. Do you want to reboot now?",
        default=False,
    )
    mock_confirm_instance.ask.assert_called_once()
