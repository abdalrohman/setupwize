"""Shell command execution utilities."""

import logging
import os
import shlex
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..core.exceptions import TaskExecutionFailedError

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a command execution."""

    output: str
    exit_code: int
    execution_time: float
    command: list[str]
    success_code: list[int] = field(default_factory=lambda: [0])

    @property
    def success(self) -> bool:
        """Check if the command was successful."""
        return self.exit_code in self.success_code


def run_command(
    args: list[str] | Callable[[], list[str]],
    env: dict[str, str] | None = None,
    verbose: bool = False,
    capture_output: bool = True,
    check: bool = False,
    success_code: list[int] | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> CommandResult:
    """Run a command and capture its output.

    Args:
        args: A list of strings representing the command and its arguments,
            or a callable that returns such a list.
        env: An optional dictionary specifying environment variables.
        verbose: A boolean indicating whether to log command execution details.
        capture_output: A boolean indicating whether to capture the command's output.
        check: A boolean indicating whether to raise an exception if the command fails.
        success_code: A list of integers representing the expected success codes.
        **kwargs: Additional keyword arguments to pass to subprocess.Popen.

    Returns:
        A CommandResult object containing the command's output and exit code.

    Raises:
        TaskExecutionFailedError: If the command fails and check is True.
    """
    success_code = [0] if success_code is None else success_code
    start_time = time.time()

    # Get the command arguments
    cmd_args = args() if callable(args) else args

    # Set up environment variables
    if env is not None:
        env_copy = os.environ.copy()
        env_copy.update(env)
        kwargs.setdefault("env", env_copy)

    # Log the command if verbose
    if verbose:
        print(f"\033[1;34mVERBOSE: Running command: {shlex.join(cmd_args)}\033[0m")
        if env is not None:
            print(f"\033[1;34mVERBOSE: Environment variables: {env}\033[0m")

    # Set up subprocess options
    if capture_output:
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.STDOUT)
        kwargs.setdefault("bufsize", 0)  # Unbuffered output
        kwargs.setdefault("universal_newlines", True)  # Text mode

    # Run the command
    try:
        # nosec B603 - We're using a controlled command
        process = subprocess.Popen(cmd_args, **kwargs)  # noqa: S603

        output = ""
        if capture_output:
            # Read output line by line for real-time logging
            for line in iter(process.stdout.readline, ""):  # type: ignore
                if verbose:
                    print(f"\033[1;32mVERBOSE: Command output: {line.rstrip()}\033[0m")
                output += line

            # Make sure we've read all output
            remaining_output = process.stdout.read()  # type: ignore
            if remaining_output:
                if verbose:
                    print(f"\033[1;32mVERBOSE: Command output: {remaining_output.rstrip()}\033[0m")
                output += remaining_output

        # Wait for the process to complete
        exit_code = process.wait()

        # Calculate execution time
        execution_time = time.time() - start_time

        # Log completion if verbose
        if verbose:
            print(
                f"\033[1;34mVERBOSE: Command completed in {execution_time:.2f}s with exit code {exit_code}\033[0m"
            )

        # Create result
        result = CommandResult(
            output=output,
            exit_code=exit_code,
            execution_time=execution_time,
            command=cmd_args,
            success_code=success_code,
        )

        # Check for errors if requested
        if check and exit_code not in success_code:
            raise TaskExecutionFailedError(  # noqa: TRY301
                task_name="shell_command",
                command=shlex.join(cmd_args),
                exit_code=exit_code,
            )
        return result  # noqa: TRY300

    except Exception as e:
        # Log error if verbose
        if verbose:
            print(f"\033[1;31mVERBOSE: Command failed: {e}\033[0m")

        # Calculate execution time
        execution_time = time.time() - start_time

        # Raise exception if check is True
        if check:
            raise TaskExecutionFailedError(
                task_name="shell_command",
                command=shlex.join(cmd_args),
                exit_code=-1,
            ) from e

        # Return error result
        return CommandResult(
            output=str(e),
            exit_code=-1,
            execution_time=execution_time,
            command=cmd_args,
            success_code=success_code,
        )
