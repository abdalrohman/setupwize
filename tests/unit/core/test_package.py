"""Tests for the package module."""

from unittest.mock import MagicMock, patch

import pytest

from setupwize.core.exceptions import PackageNameMismatchError, PackageNotFoundError
from setupwize.core.package import Package, create_package_from_yaml
from setupwize.parsers.yaml_parser import YamlParser


class TestPackage:
    """Tests for the Package class."""

    def test_from_dict_minimal(self) -> None:
        """Test creating a package from a minimal dictionary."""
        data = {"name": "test"}
        package = Package.from_dict(data)

        assert package.name == "test"
        assert package.description == ""
        assert package.category == "Uncategorized"
        assert package.tasks == []
        assert package.dependencies == []
        assert package.verbose is False

    def test_from_dict_complete(self) -> None:
        """Test creating a package from a complete dictionary."""
        data = {
            "name": "test",
            "description": "Test package",
            "category": "Testing",
            "tasks": [
                {"type": "shell", "command": "echo 'Hello, world!'"},
            ],
            "dependencies": ["dep1", "dep2"],
        }

        with patch("setupwize.core.package.create_task_from_config") as mock_create_task:
            mock_task = MagicMock()
            mock_create_task.return_value = mock_task

            package = Package.from_dict(data, verbose=True)

            assert package.name == "test"
            assert package.description == "Test package"
            assert package.category == "Testing"
            assert package.tasks == [mock_task]
            assert package.dependencies == ["dep1", "dep2"]
            assert package.verbose is True

            mock_create_task.assert_called_once_with(
                {"type": "shell", "command": "echo 'Hello, world!'"},
                True,
            )

    def test_from_dict_invalid(self) -> None:
        """Test creating a package from an invalid dictionary."""
        # Missing name
        with pytest.raises(ValueError, match="must contain a 'name' key"):
            Package.from_dict({})

        # Invalid tasks
        with pytest.raises(ValueError, match="'tasks' must be a list"):
            Package.from_dict({"name": "test", "tasks": "not a list"})

        # Invalid dependencies
        with pytest.raises(ValueError, match="'dependencies' must be a list"):
            Package.from_dict({"name": "test", "dependencies": "not a list"})

        # Invalid dependency type
        with pytest.raises(TypeError, match="dependencies must be strings"):
            Package.from_dict({"name": "test", "dependencies": [1, 2, 3]})

    def test_install(self) -> None:
        """Test installing a package."""
        # Create mock tasks
        mock_task1 = MagicMock()
        mock_task2 = MagicMock()

        # Create the package with mock tasks
        package = Package(
            name="test",
            description="Test package",
            category="Testing",
            tasks=[mock_task1, mock_task2],
            dependencies=["dep1", "dep2"],
            verbose=True,
        )

        # Install the package
        with patch("setupwize.core.task.AptExecutor"):
            package.install()

            # Check that the tasks were executed
            mock_task1.execute.assert_called_once()
            mock_task2.execute.assert_called_once()


class TestCreatePackageFromYaml:
    """Tests for the create_package_from_yaml function."""

    def test_create_package_from_yaml(self) -> None:
        """Test creating a package from a YAML file."""
        # Mock YamlParser
        mock_yaml_parser = MagicMock(spec=YamlParser)
        mock_yaml_parser.load_package.return_value = {
            "packages": [
                {
                    "name": "test",
                    "description": "Test package",
                    "category": "Testing",
                    "tasks": [
                        {"type": "shell", "command": "echo 'Hello, world!'"},
                    ],
                    "dependencies": ["dep1", "dep2"],
                }
            ]
        }

        # Mock Package.from_dict
        with patch("setupwize.core.package.Package.from_dict") as mock_from_dict:
            mock_package = MagicMock(spec=Package)
            mock_from_dict.return_value = mock_package

            # Create package from YAML
            package = create_package_from_yaml("test", mock_yaml_parser, verbose=True)

            # Check that the YAML parser was called
            mock_yaml_parser.load_package.assert_called_once_with("test")

            # Check that Package.from_dict was called
            mock_from_dict.assert_called_once_with(
                {
                    "name": "test",
                    "description": "Test package",
                    "category": "Testing",
                    "tasks": [
                        {"type": "shell", "command": "echo 'Hello, world!'"},
                    ],
                    "dependencies": ["dep1", "dep2"],
                },
                True,
            )

            # Check that the package was returned
            assert package == mock_package

    def test_create_package_from_yaml_not_found(self) -> None:
        """Test creating a package from a YAML file that doesn't exist."""
        # Mock YamlParser
        mock_yaml_parser = MagicMock(spec=YamlParser)
        mock_yaml_parser.load_package.side_effect = PackageNotFoundError("test")

        # Create package from YAML
        with pytest.raises(PackageNotFoundError):
            create_package_from_yaml("test", mock_yaml_parser)

    def test_create_package_from_yaml_name_mismatch(self) -> None:
        """Test creating a package from a YAML file with a name mismatch."""
        # Mock YamlParser
        mock_yaml_parser = MagicMock(spec=YamlParser)
        mock_yaml_parser.load_package.return_value = {
            "packages": [
                {
                    "name": "wrong",
                    "description": "Test package",
                    "category": "Testing",
                    "tasks": [
                        {"type": "shell", "command": "echo 'Hello, world!'"},
                    ],
                    "dependencies": ["dep1", "dep2"],
                }
            ]
        }

        # Create package from YAML
        with pytest.raises(PackageNameMismatchError):
            create_package_from_yaml("test", mock_yaml_parser)

    def test_create_package_from_yaml_empty_packages(self) -> None:
        """Test creating a package from a YAML file with no packages."""
        # Mock YamlParser
        mock_yaml_parser = MagicMock(spec=YamlParser)
        mock_yaml_parser.load_package.return_value = {"packages": []}

        # Create package from YAML
        with pytest.raises(PackageNotFoundError):
            create_package_from_yaml("test", mock_yaml_parser)
