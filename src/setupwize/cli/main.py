"""Command-line interface for SetUpWize."""

from datetime import datetime
from pathlib import Path

import click
from rich.console import Console

from ..core.environment import Environment
from ..core.exceptions import PackageNotFoundError, SetUpWizeError
from ..core.package import create_package_from_yaml
from ..core.selector import select_packages_to_install
from ..core.shell import run_command
from ..parsers.yaml_parser import YamlParser
from ..tracers.log import LogConfig
from ..utils.system import (
    confirm_reboot,
    confirm_system_upgrade,
    is_running_gnome,
    is_running_on_kde_neon,
)

# Default packages to install
DEFAULT_PACKAGES = ["mise", "docker"]

console = Console()


@click.command()
@click.option(
    "--packages-dir",
    "-p",
    help="Directory containing package YAML files",
)
@click.option(
    "--install",
    "-i",
    help="Install packages (name of the package)",
)
@click.option(
    "--log-level",
    "-ll",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--log-path",
    "-lp",
    help="Path to the log file",
)
@click.option(
    "--list-packages",
    "-list",
    is_flag=True,
    help="List available packages and exit",
)
@click.option(
    "--select-packages",
    "-select",
    is_flag=True,
    help="Interactively select packages to install",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.argument("packages_to_install", nargs=-1)
def main(
    packages_dir: str | None,
    install: str | None,
    log_level: str | None,
    log_path: str | None,
    list_packages: bool,
    select_packages: bool,
    verbose: bool,
    packages_to_install: list[str],
) -> int:
    """SetUpWize: Your friendly tool installation wizard!"""
    # Load environment
    env = Environment.from_env()

    # Override environment with command-line options
    if packages_dir:
        env.packages_dir = Path(packages_dir)
    if log_level:
        env.log_level = log_level
    if log_path:
        env.log_path = Path(log_path)

    # Configure logging
    logger = LogConfig(
        log_path=env.log_path,
        logger_source=__file__,
        log_level=env.log_level,
    ).configure()

    # Check for desktop environment
    if not (is_running_gnome() or is_running_on_kde_neon()):
        logger.error(
            "This script is designed to run on GNOME or KDE Neon desktop environment only."
        )
        return 0

    # Create YAML parser
    yaml_parser = YamlParser(packages_dir=env.packages_dir)

    # List packages if requested
    if list_packages:
        available_packages = yaml_parser.get_available_packages()
        console.print("[bold]Available packages:[/]")
        for package in available_packages:
            console.print(f"  - {package}")
        return 0

    # Determine packages to install
    packages_to_install_list = list(packages_to_install)

    if not packages_to_install_list and not select_packages:
        # Use default packages
        packages_to_install_list = DEFAULT_PACKAGES

    if install:
        packages_to_install_list = [install]

    if select_packages:
        # Load all packages
        all_packages_data = yaml_parser.load_all_packages()

        # Select packages interactively
        selected_packages = select_packages_to_install(
            all_packages_data,
            packages_to_install_list or DEFAULT_PACKAGES,
        )

        if not selected_packages:
            logger.info("No packages selected for installation.")
            return 0

        packages_to_install_list = selected_packages

    # Update system if confirmed
    if confirm_system_upgrade():
        logger.info("Updating and upgrading system packages...")

        if is_running_on_kde_neon():
            # Use pkcon for KDE Neon
            logger.info("Using pkcon for KDE Neon system update...")
            run_command(["sudo", "pkcon", "update", "-y"], verbose=True)
        else:
            # Use apt-get for Ubuntu
            run_command(["sudo", "apt-get", "-y", "update"], verbose=True)
            run_command(["sudo", "apt-get", "-y", "upgrade"], verbose=True)

    # Install packages
    start_time = datetime.now()
    logger.info(
        f"Starting installation of {len(packages_to_install_list)} packages at {start_time}"
    )

    for package_name in packages_to_install_list:
        try:
            logger.info(f"Installing package: {package_name}")
            package_obj = create_package_from_yaml(package_name, yaml_parser, verbose)
            package_obj.install()
        except PackageNotFoundError:
            logger.exception(f"Package '{package_name}' not found.")
        except SetUpWizeError:
            logger.exception(f"Error installing package '{package_name}'")
        except Exception:
            logger.exception(f"Unexpected error installing package '{package_name}'")

    # Log completion
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Installation completed at {end_time} (duration: {duration})")

    # Ask for reboot if needed
    if confirm_reboot():
        logger.info("Rebooting system...")
        run_command(["sudo", "reboot"], verbose=True)

    return 0


if __name__ == "__main__":
    main()
