"""Tests for the selector module."""

from unittest.mock import MagicMock, patch

from rich.console import Console

from setupwize.core.selector import PackageSelector, select_packages_to_install


class TestPackageSelector:
    """Tests for the PackageSelector class."""

    def test_init(self) -> None:
        """Test initialization."""
        console = Console()
        selector = PackageSelector(
            available_packages=[{"packages": [{"name": "test"}]}],
            default_packages=["default"],
            console=console,
        )
        assert selector.available_packages == [{"packages": [{"name": "test"}]}]
        assert selector.default_packages == ["default"]
        assert selector.console == console

    def test_post_init(self) -> None:
        """Test post initialization."""
        selector = PackageSelector(
            available_packages=[{"packages": [{"name": "test"}]}],
            default_packages=["default"],
        )
        assert selector.console is not None
        assert selector.style is not None

    def test_group_packages_by_category(self) -> None:
        """Test grouping packages by category."""
        selector = PackageSelector(
            available_packages=[
                {
                    "packages": [
                        {"name": "test1", "category": "Category1"},
                        {"name": "test2", "category": "Category2"},
                        {"name": "test3"},  # No category, should use "Uncategorized"
                    ]
                }
            ],
            default_packages=["default"],
        )
        result = selector._group_packages_by_category()
        assert "Category1" in result
        assert "Category2" in result
        assert "Uncategorized" in result
        assert len(result["Category1"]) == 1
        assert len(result["Category2"]) == 1
        assert len(result["Uncategorized"]) == 1
        assert result["Category1"][0]["name"] == "test1"
        assert result["Category2"][0]["name"] == "test2"
        assert result["Uncategorized"][0]["name"] == "test3"

    @patch("setupwize.core.selector.questionary.checkbox")
    def test_select_packages(self, mock_checkbox) -> None:
        """Test selecting packages."""
        mock_checkbox_instance = MagicMock()
        mock_checkbox.return_value = mock_checkbox_instance
        mock_checkbox_instance.ask.return_value = ["test1", "test3"]

        selector = PackageSelector(
            available_packages=[
                {
                    "packages": [
                        {"name": "test1", "category": "Category1", "description": "Test 1"},
                        {"name": "test2", "category": "Category1", "description": "Test 2"},
                        {"name": "test3", "category": "Category2", "description": "Test 3"},
                    ]
                }
            ],
            default_packages=["test1"],
        )

        # Mock the _group_packages_by_category method to return a controlled result
        selector._group_packages_by_category = MagicMock(
            return_value={
                "Category1": [
                    {"name": "test1", "category": "Category1", "description": "Test 1"},
                    {"name": "test2", "category": "Category1", "description": "Test 2"},
                ],
                "Category2": [
                    {"name": "test3", "category": "Category2", "description": "Test 3"},
                ],
            }
        )

        result = selector.select_packages()
        assert result == ["test1", "test3"]
        assert mock_checkbox.call_count == 2  # One for each category

    @patch("setupwize.core.selector.questionary.checkbox")
    def test_select_packages_empty_category(self, mock_checkbox) -> None:
        """Test selecting packages with an empty category."""
        mock_checkbox_instance = MagicMock()
        mock_checkbox.return_value = mock_checkbox_instance
        mock_checkbox_instance.ask.return_value = []

        selector = PackageSelector(
            available_packages=[
                {
                    "packages": [
                        {"name": "test1", "category": "Category1", "description": "Test 1"},
                    ]
                }
            ],
            default_packages=[],
        )

        # Mock the _group_packages_by_category method to return a controlled result
        selector._group_packages_by_category = MagicMock(
            return_value={
                "Category1": [
                    {"name": "test1", "category": "Category1", "description": "Test 1"},
                ],
            }
        )

        result = selector.select_packages()
        assert result == []
        assert mock_checkbox.call_count == 1

    @patch("setupwize.core.selector.questionary.checkbox")
    def test_select_packages_no_packages(self, mock_checkbox) -> None:
        """Test selecting packages with no packages."""
        selector = PackageSelector(
            available_packages=[],
            default_packages=[],
        )

        # Mock the _group_packages_by_category method to return an empty dict
        selector._group_packages_by_category = MagicMock(return_value={})

        result = selector.select_packages()
        assert result == []
        assert mock_checkbox.call_count == 0


def test_select_packages_to_install() -> None:
    """Test select_packages_to_install function."""
    with patch("setupwize.core.selector.PackageSelector") as mock_selector_class:
        mock_selector = MagicMock()
        mock_selector_class.return_value = mock_selector
        mock_selector.select_packages.return_value = ["test1", "test3"]

        result = select_packages_to_install(
            available_packages_data=[{"packages": [{"name": "test"}]}],
            default_packages=["default"],
        )

        assert result == ["test1", "test3"]
        mock_selector_class.assert_called_once_with(
            available_packages=[{"packages": [{"name": "test"}]}],
            default_packages=["default"],
        )
        mock_selector.select_packages.assert_called_once()
