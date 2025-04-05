"""Custom exceptions for SetUpWize."""


class SetUpWizeError(Exception):
    """Base exception class for all SetUpWize-related errors."""

    def __init__(self, message: str, details: dict | list | str | None = None) -> None:
        """Initialize the exception.

        Args:
            message: The error message.
            details: Additional details about the error.
        """
        self.message = message
        self.details = details
        super().__init__(message)


class PackageError(SetUpWizeError):
    """Base class for package-related errors."""

    pass


class PackageNotFoundError(PackageError):
    """Raised when a specified package YAML file is not found."""

    def __init__(self, package_name: str) -> None:
        """Initialize the exception.

        Args:
            package_name: The name of the package that was not found.
        """
        super().__init__(f"Package '{package_name}' not found.")
        self.package_name = package_name


class PackageNameMismatchError(PackageError):
    """Raised when the package name in the YAML file does not match the filename."""

    def __init__(self, expected: str, actual: str) -> None:
        """Initialize the exception.

        Args:
            expected: The expected package name.
            actual: The actual package name found in the YAML file.
        """
        super().__init__(f"Package name mismatch: Expected '{expected}', got '{actual}'")
        self.expected = expected
        self.actual = actual


class ParserError(SetUpWizeError):
    """Base class for parser-related errors."""

    pass


class InvalidYamlFormatError(ParserError):
    """Raised when a YAML file has an invalid format or structure."""

    pass


class TaskError(SetUpWizeError):
    """Base class for task-related errors."""

    pass


class TaskExecutionFailedError(TaskError):
    """Raised when a task fails to execute successfully."""

    def __init__(
        self, task_name: str, command: str | None = None, exit_code: int | None = None
    ) -> None:
        """Initialize the exception.

        Args:
            task_name: The name of the task that failed.
            command: The command that failed, if applicable.
            exit_code: The exit code of the failed command, if applicable.
        """
        message = f"Task '{task_name}' failed"
        if command:
            message += f" while executing '{command}'"
        if exit_code is not None:
            message += f" with exit code {exit_code}"

        super().__init__(message)
        self.task_name = task_name
        self.command = command
        self.exit_code = exit_code
