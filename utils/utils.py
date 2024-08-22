import logging
import os
import shutil
from pathlib import Path

import questionary

logger = logging.getLogger(__name__)


def check_cmd(cmd: str) -> bool:
    """
    Check if the command exists.

    Args:
        cmd: The command to check.

    Returns:
        True if the command exists, False otherwise.
    """
    if not cmd:
        raise ValueError("Command cannot be empty")
    return shutil.which(cmd) is not None


def is_running_gnome() -> bool:
    """
    Checks if the script is running on the GNOME desktop environment.

    Returns:
        True if running on GNOME, False otherwise.
    """
    return "GNOME" in os.environ.get("XDG_CURRENT_DESKTOP", "")


def is_running_on_ubuntu() -> bool:
    """
    Checks if the script is running on an Ubuntu system.

    Returns:
        True if running on Ubuntu, False otherwise.
    """
    os_release_path = Path("/etc/os-release")
    if not os_release_path.is_file():
        return False

    with os_release_path.open() as f:
        for line in f:
            if line.startswith("ID="):
                distro_id = line.split("=")[1].strip().lower()
                return distro_id == "ubuntu"
    return False


def is_ubuntu_version_at_least(min_version: float) -> bool:
    """
    Checks if the Ubuntu version is at least the specified minimum version.

    Args:
        min_version: The minimum required Ubuntu version.

    Returns:
        True if the Ubuntu version is at least min_version, False otherwise.
    """
    os_release_path = Path("/etc/os-release")
    if not os_release_path.is_file():
        return False

    with os_release_path.open() as f:
        for line in f:
            if line.startswith("VERSION_ID="):
                distro_version = line.split("=")[1].strip().split('"')[1]
                try:
                    return float(distro_version) >= min_version
                except ValueError:
                    logger.warning(f"Could not parse Ubuntu version: {distro_version}")
                    return False
    return False


def confirm_reboot() -> bool:
    """
    Prompts the user to confirm a reboot.
    """
    print("\nImportant: You need to reboot your system to apply the recent changes.")
    confirm: bool = questionary.confirm("Would you like to reboot now?", default=False).ask()

    return confirm


def confirm_system_upgrade() -> bool:
    """
    Performs a system upgrade.
    """
    print("\nRecommendation: It's recommended to keep your system up-to-date.")
    print("Upgrading ensures you have the latest features and security patches.")
    confirm: bool = questionary.confirm("Would you like to upgrade your system now?", default=False).ask()

    return confirm
