"""Custom exceptions for SetUpWize."""


class SetUpWizeError(Exception):
    """Base exception class for all SetUpWize-related errors."""

    pass


class PackageNotFoundError(SetUpWizeError):
    """Raised when a specified package YAML file is not found."""

    pass


class InvalidYamlFormatError(SetUpWizeError):
    """Raised when a YAML file has an invalid format or structure."""

    pass


class TaskExecutionFailedError(SetUpWizeError):
    """Raised when a task fails to execute successfully."""

    pass


class PackageNameMismatchError(SetUpWizeError):
    """Raised when the package name in the YAML file does not match the filename."""

    pass
