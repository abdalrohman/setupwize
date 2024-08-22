import logging
from typing import Any

import questionary

logger = logging.getLogger(__name__)


questionary_style = questionary.Style(
    [
        ("qmark", "#673ab7 bold"),  # Bold magenta question mark
        ("question", ""),  # Default color for the question
        ("selected", "#cc5454"),  # Red color for selected choices
        ("pointer", "#673ab7 bold"),  # Bold magenta for the pointer
        ("answer", "#f44336 bold"),  # Bold red for the final answer
        ("instruction", ""),  # Hide the default instruction text
    ]
)


def select_packages_to_install(available_packages_data: list[dict[str, Any]], default_packages: list[str]) -> list[str]:
    """
    Prompts the user to select packages to install interactively, grouped by category.

    Args:
        available_packages_data: A list of dictionaries containing package data (including 'name' and 'category').
        default_packages: A list of default package names to be pre-selected.

    Returns:
        A list of selected package names to install.
    """
    if not available_packages_data:
        logger.warning("No packages available for installation.")
        return []

    # Group packages by category
    packages_by_category: dict[str, list[str]] = {}
    for package_data in available_packages_data:
        for package in package_data["packages"]:
            category: str = package.get("category", "Uncategorized")
            packages_by_category.setdefault(category, []).append(package)

    selected_packages: list[str] = []
    for category, package_data_list in packages_by_category.items():
        logger.info(f"Selecting packages from category: {category}")

        # Create choices for this category with default packages pre-selected
        choices = [
            questionary.Choice(
                title=f"{pd['name']}: {pd['description']}" if pd.get("description") else pd["name"],  # type: ignore
                value=pd["name"],  # type: ignore
                checked=pd["name"] in default_packages,  # type: ignore
            )
            for pd in package_data_list
        ]

        # Prompt for package selection within this category
        category_selected = questionary.checkbox(
            f"Select packages from '{category}':",  # noqa: S608
            choices=choices,
            style=questionary_style,
        ).ask()

        selected_packages.extend(category_selected or [])

    return selected_packages
