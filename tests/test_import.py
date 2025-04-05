"""Test that the package can be imported."""


def test_import() -> None:
    """Test that the package can be imported."""
    import setupwize

    assert setupwize.__version__ is not None


def test_import_modules() -> None:
    """Test that the package modules can be imported."""
    from setupwize.cli import main
    from setupwize.core import environment, exceptions, package, selector, shell, task
    from setupwize.parsers import yaml_parser
    from setupwize.tracers import log
    from setupwize.utils import system

    assert environment
    assert exceptions
    assert package
    assert selector
    assert shell
    assert task
    assert yaml_parser
    assert log
    assert system
    assert main
