#!/usr/bin/env python

import os
import sys
from datetime import datetime
from typing import Any

from core.env import EnvironmentLoader
from core.exceptions import PackageNotFoundError
from core.interactive_selector import select_packages_to_install
from core.packages import create_package_from_yaml
from core.run_cmd import run_command
from core.tasks import GnomeSettingsTask
from core.tracers.log import LogConfig
from parser.yaml_parser import YamlParser
from utils import (
    check_cmd,
    confirm_reboot,
    confirm_system_upgrade,
    is_running_gnome,
    is_running_on_ubuntu,
    is_ubuntu_version_at_least,
)

import click
from tqdm import tqdm

EnvironmentLoader(".env").load_envs()

# Default configuration
DEFAULT_PACKAGES_DIR = os.environ.get("DEFAULT_PACKAGES_DIR", "./packages")
DEFAULT_LOG_LEVEL = os.environ.get("DEFAULT_LOG_LEVEL", "INFO")
DEFAULT_LOG_PATH = os.environ.get("DEFAULT_LOG_PATH", "./logs")
DEFAULT_PACKAGES = ["mise", "docker"]


@click.command()
@click.option("--packages-dir", "-p", default=DEFAULT_PACKAGES_DIR, help="Directory containing package YAML files")
@click.option(
    "--log-level", "-ll", default=DEFAULT_LOG_LEVEL, help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
)
@click.option("--log-path", "-lp", default=DEFAULT_LOG_PATH, help="Path to the log file")
@click.option("--list-packages", "-list", is_flag=True, help="List available packages and exit")
@click.option("--select-packages", "-select", is_flag=True, help="Interactively select packages to install")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.argument("packages_to_install", nargs=-1)
def main(
    packages_dir: str,
    log_level: str,
    log_path: str,
    list_packages: bool,
    select_packages: bool,
    verbose: bool,
    packages_to_install: list[str],
) -> None:
    """
    SetUpWiz: Your friendly tool installation wizard!
    """

    # Configure logging
    logger = LogConfig(log_path=log_path, logger_source=__file__, log_level=log_level.upper()).get_logger()

    # Preliminary checks
    if not check_cmd("sudo"):
        logger.error("sudo command not found. Please install sudo and try again.")
        exit(1)
    if not check_cmd("apt-get"):
        logger.error("apt-get command not found.")
        exit(1)
    if not is_running_on_ubuntu() or not is_ubuntu_version_at_least(24.04):
        logger.error("This script requires Ubuntu 24.04 or higher.")
        exit(1)
    if not is_running_gnome():
        logger.error("This script is designed to run on GNOME desktop environment only.")
        exit(1)

    if confirm_system_upgrade():
        logger.info("Updating and upgrading system packages...")
        run_command(["sudo", "apt-get", "-y", "update"], verbose=True)
        run_command(["sudo", "apt-get", "-y", "upgrade"], verbose=True)

    # List available packages if requested
    yaml_parser: YamlParser = YamlParser(packages_dir)
    available_packages_data: list[dict[str, Any]] = yaml_parser.load_all_packages()
    if list_packages:
        logger.info("Available packages:")
        for package_data in available_packages_data:
            for package in package_data["packages"]:
                logger.info(f"  - {package['name']} (Category: {package.get('category', 'Uncategorized')})")
        exit(0)

    # Default to install all packages
    if not packages_to_install and not select_packages:
        packages_to_install = yaml_parser.get_available_packages()

    # Interactive selection of the packages
    if select_packages:
        # Interactively select packages or use defaults if none specified
        packages_to_install = select_packages_to_install(available_packages_data, DEFAULT_PACKAGES)

    # specify the specific package to install
    if packages_to_install:
        # Check if specified packages are valid
        invalid_packages = [p for p in packages_to_install if p not in yaml_parser.get_available_packages()]
        if invalid_packages:
            logger.error(f"Invalid packages: {', '.join(invalid_packages)}")
            exit(1)
    try:
        # Prevent sleep/lock during installation
        logger.info("Preventing the system from going to sleep or locking...")
        GnomeSettingsTask("set", "org.gnome.desktop.screensaver", "lock-enabled", "false", verbose=verbose).execute()
        GnomeSettingsTask("set", "org.gnome.desktop.session", "idle-delay", "0", verbose=verbose).execute()

        # Install packages
        with tqdm(
            total=len(packages_to_install),
            desc="Installing Packages",
            unit="pkg",
            position=0,
            leave=True,
            dynamic_ncols=True,
            file=sys.stderr,
        ) as pbar:
            for package_name in packages_to_install:
                try:
                    create_package_from_yaml(
                        package_name,
                        yaml_parser,
                        verbose,
                    ).install()
                except PackageNotFoundError:
                    logger.exception(f"Package '{package_name}' not found.")
                finally:
                    pbar.update(1)
                    pbar.refresh()
    except (Exception, KeyboardInterrupt) as e:
        log_file = os.path.join(log_path, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        if isinstance(e, KeyboardInterrupt):
            logger.warning("Installation interrupted.")
        else:
            logger.exception(
                f"An unexpected error occurred during installation. Please check the log_file `{log_file}` for more details."  # noqa: E501
            )

        # Revert sleep/lock settings
        logger.info("Reverting to normal idle and lock settings...")
        GnomeSettingsTask("set", "org.gnome.desktop.screensaver", "lock-enabled", "true", verbose=verbose).execute()
        GnomeSettingsTask("set", "org.gnome.desktop.session", "idle-delay", "300", verbose=verbose).execute()

        sys.exit(1)

    if confirm_reboot():
        logger.info("Rebooting the system...")
        run_command(["sudo", "reboot"], verbose=True)


if __name__ == "__main__":
    main()
