"""Tests for the yaml_parser module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from setupwize.core.exceptions import InvalidYamlFormatError, PackageNotFoundError
from setupwize.parsers.yaml_parser import YamlParser


class TestYamlParser:
    """Tests for the YamlParser class."""

    def test_init(self) -> None:
        """Test initialization."""
        parser = YamlParser(packages_dir=Path("/path/to/packages"))
        assert parser.packages_dir == Path("/path/to/packages")

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.open")
    @patch("yaml.safe_load")
    def test_load_package(self, mock_yaml_load, mock_open, _) -> None:
        """Test loading a package."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_yaml_load.return_value = {"name": "test", "description": "Test package"}
        parser = YamlParser(packages_dir=Path("/path/to/packages"))
        result = parser.load_package("test")
        assert result == {"name": "test", "description": "Test package"}
        mock_open.assert_called_once_with("r", encoding="utf-8")
        mock_yaml_load.assert_called_once_with(mock_file)

    @patch("pathlib.Path.exists", return_value=False)
    def test_load_package_not_found(self, _) -> None:
        """Test loading a package that doesn't exist."""
        parser = YamlParser(packages_dir=Path("/path/to/packages"))
        with pytest.raises(PackageNotFoundError, match="Package 'test' not found"):
            parser.load_package("test")

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.open")
    @patch("yaml.safe_load", side_effect=yaml.YAMLError())
    def test_load_package_invalid_yaml(self, _, mock_open, _unused) -> None:
        """Test loading a package with invalid YAML."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        parser = YamlParser(packages_dir=Path("/path/to/packages"))
        with pytest.raises(InvalidYamlFormatError, match="Invalid YAML format in package 'test'"):
            parser.load_package("test")

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.open")
    @patch("yaml.safe_load")
    def test_load_package_name_mismatch(self, mock_yaml_load, mock_open, _) -> None:
        """Test loading a package with a name mismatch."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_yaml_load.return_value = {"name": "other", "description": "Test package"}
        parser = YamlParser(packages_dir=Path("/path/to/packages"))
        with pytest.raises(
            InvalidYamlFormatError, match="Package name 'other' does not match filename 'test'"
        ):
            parser.load_package("test")

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.open")
    @patch("yaml.safe_load")
    def test_load_all_packages(self, mock_yaml_load, mock_open, _, mock_glob) -> None:
        """Test loading all packages."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Create mock Path objects for the glob results
        mock_path1 = MagicMock()
        mock_path1.stem = "test1"
        mock_path2 = MagicMock()
        mock_path2.stem = "test2"
        mock_glob.return_value = [mock_path1, mock_path2]

        mock_yaml_load.side_effect = [
            {"name": "test1", "description": "Test package 1"},
            {"name": "test2", "description": "Test package 2"},
        ]
        parser = YamlParser(packages_dir=Path("/path/to/packages"))
        result = parser.load_all_packages()
        assert len(result) == 2
        assert result[0] == {"name": "test1", "description": "Test package 1"}
        assert result[1] == {"name": "test2", "description": "Test package 2"}
        assert mock_open.call_count == 2

    @patch("pathlib.Path.glob")
    def test_load_all_packages_empty(self, mock_glob) -> None:
        """Test loading all packages when there are none."""
        mock_glob.return_value = []
        parser = YamlParser(packages_dir=Path("/path/to/packages"))
        result = parser.load_all_packages()
        assert result == []

    @patch("pathlib.Path.glob")
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.open")
    @patch("yaml.safe_load")
    def test_load_all_packages_with_errors(self, mock_yaml_load, mock_open, _, mock_glob) -> None:
        """Test loading all packages with some errors."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Create mock Path objects for the glob results
        mock_path1 = MagicMock()
        mock_path1.stem = "test1"
        mock_path2 = MagicMock()
        mock_path2.stem = "test2"
        mock_path3 = MagicMock()
        mock_path3.stem = "test3"
        mock_glob.return_value = [mock_path1, mock_path2, mock_path3]

        mock_yaml_load.side_effect = [
            {"name": "test1", "description": "Test package 1"},
            yaml.YAMLError(),
            {"name": "test3", "description": "Test package 3"},
        ]
        parser = YamlParser(packages_dir=Path("/path/to/packages"))
        result = parser.load_all_packages()
        assert len(result) == 2
        assert result[0] == {"name": "test1", "description": "Test package 1"}
        assert result[1] == {"name": "test3", "description": "Test package 3"}
        assert mock_open.call_count == 3
