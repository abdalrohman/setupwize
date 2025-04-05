"""System utilities for SetUpWize."""

import os
import shutil
import subprocess
from pathlib import Path

import questionary
from rich.console import Console

console = Console()


def check_cmd(cmd: str) -> bool:
    """Check if a command is available in the system.

    Args:
        cmd: The command to check.

    Returns:
        True if the command is available, False otherwise.
    """
    return shutil.which(cmd) is not None


def is_running_gnome() -> bool:
    """Check if the script is running on GNOME.

    Returns:
        True if running on GNOME, False otherwise.
    """
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
    return "GNOME" in desktop


def is_running_on_kde_neon() -> bool:
    """Check if the script is running on KDE Neon.

    Returns:
        True if running on KDE Neon, False otherwise.
    """
    try:
        result = subprocess.run(
            ["lsb_release", "-d"],
            capture_output=True,
            text=True,
            check=True,
        )
        return (
            "KDE" in os.environ.get("XDG_CURRENT_DESKTOP", "") and "neon" in result.stdout.lower()
        )
    except subprocess.SubprocessError:
        # If lsb_release command fails, fall back to checking os-release file
        os_release_path = Path("/etc/os-release")
        if not os_release_path.is_file():
            return False

        is_kde = "KDE" in os.environ.get("XDG_CURRENT_DESKTOP", "")

        with os_release_path.open() as f:
            content = f.read().lower()
            return is_kde and ("neon" in content)


def is_running_on_ubuntu() -> bool:
    """Check if the script is running on Ubuntu.

    Returns:
        True if running on Ubuntu, False otherwise.
    """
    os_release_path = Path("/etc/os-release")
    if not os_release_path.is_file():
        return False

    with os_release_path.open() as f:
        content = f.read().lower()
        return "ubuntu" in content


def get_ubuntu_version() -> tuple[int, int] | None:
    """Get the Ubuntu version.

    Returns:
        A tuple containing the major and minor version numbers, or None if not running on Ubuntu.
    """
    if not is_running_on_ubuntu():
        return None

    try:
        # nosec B603 B607 - This is a safe command with fixed arguments
        result = subprocess.run(  # noqa: S603
            ["lsb_release", "-rs"],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
        )

        version_str = result.stdout.strip()
        major, minor = map(int, version_str.split("."))
    except (subprocess.SubprocessError, ValueError):
        return None
    else:
        return major, minor


def is_ubuntu_version_at_least(major: int, minor: int = 0) -> bool:
    """Check if the Ubuntu version is at least the specified version.

    Args:
        major: The major version number.
        minor: The minor version number.

    Returns:
        True if the Ubuntu version is at least the specified version, False otherwise.
    """
    version = get_ubuntu_version()
    if not version:
        return False

    current_major, current_minor = version
    return (current_major > major) or (current_major == major and current_minor >= minor)


def confirm_system_upgrade() -> bool:
    """Ask the user to confirm system upgrade.

    Returns:
        True if the user confirms, False otherwise.
    """
    result = questionary.confirm(
        "Do you want to update and upgrade system packages?",
        default=True,
    ).ask()
    return bool(result)


def confirm_reboot() -> bool:
    """Ask the user to confirm system reboot.

    Returns:
        True if the user confirms, False otherwise.
    """
    result = questionary.confirm(
        "Some changes may require a system reboot. Do you want to reboot now?",
        default=False,
    ).ask()
    return bool(result)
