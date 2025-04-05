"""Interactive package selector for SetUpWize."""

import logging
from dataclasses import dataclass, field
from typing import Any

import questionary
from questionary import Choice
from rich.console import Console

logger = logging.getLogger(__name__)


@dataclass
class PackageSelector:
    """Interactive package selector."""

    available_packages: list[dict[str, Any]]
    default_packages: list[str] = field(default_factory=list)
    console: Console | None = None

    def __post_init__(self) -> None:
        """Initialize the selector."""
        if self.console is None:
            self.console = Console()
        self.style = questionary.Style(
            [
                ("qmark", "#673ab7 bold"),  # Bold magenta question mark
                ("question", "bold"),  # Bold question text
                ("selected", "#cc5454"),  # Red color for selected choices
                ("pointer", "#673ab7 bold"),  # Bold magenta for the pointer
                ("answer", "#f44336 bold"),  # Bold red for the final answer
                ("instruction", ""),  # Hide the default instruction text
            ]
        )

    def _group_packages_by_category(self) -> dict[str, list[dict[str, Any]]]:
        """Group packages by category.

        Returns:
            A dictionary mapping categories to lists of package data.
        """
        packages_by_category: dict[str, list[dict[str, Any]]] = {}

        for package_data in self.available_packages:
            for package in package_data.get("packages", []):
                category = package.get("category", "Uncategorized")
                if category not in packages_by_category:
                    packages_by_category[category] = []
                packages_by_category[category].append(package)

        return packages_by_category

    def select_packages(self) -> list[str]:
        """Prompt the user to select packages to install.

        Returns:
            A list of selected package names.
        """
        if not self.available_packages:
            logger.warning("No packages available for installation.")
            return []

        # Group packages by category
        packages_by_category = self._group_packages_by_category()

        # Select packages from each category
        selected_packages: list[str] = []

        for category, package_list in packages_by_category.items():
            # We know console is not None because we initialize it in __post_init__
            if self.console is not None:  # for mypy
                self.console.print(f"[bold blue]Category:[/] [bold]{category}[/]")

            # Create choices for this category
            choices = [
                Choice(
                    title=f"{pkg.get('name')}: {pkg.get('description')}"
                    if pkg.get("description")
                    else pkg.get("name", ""),
                    value=pkg.get("name", ""),
                    checked=pkg.get("name", "") in self.default_packages,
                )
                for pkg in package_list
            ]

            # Prompt for package selection
            category_selected = questionary.checkbox(
                "Select packages from category:",
                choices=choices,
                style=self.style,
            ).ask()

            if category_selected:
                # Add packages that aren't already in the list
                for pkg in category_selected:
                    if pkg not in selected_packages:
                        selected_packages.append(pkg)

        return selected_packages


def select_packages_to_install(
    available_packages_data: list[dict[str, Any]],
    default_packages: list[str],
) -> list[str]:
    """Prompt the user to select packages to install.

    Args:
        available_packages_data: A list of dictionaries containing package data.
        default_packages: A list of default package names to be pre-selected.

    Returns:
        A list of selected package names.
    """
    selector = PackageSelector(
        available_packages=available_packages_data,
        default_packages=default_packages,
    )

    return selector.select_packages()
