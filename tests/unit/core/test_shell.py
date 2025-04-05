"""Tests for the shell module."""

import os
from unittest.mock import MagicMock, patch

import pytest

from setupwize.core.exceptions import TaskExecutionFailedError
from setupwize.core.shell import CommandResult, run_command


class TestCommandResult:
    """Tests for the CommandResult class."""

    def test_success_property(self) -> None:
        """Test the success property."""
        # Success
        result = CommandResult(
            output="output",
            exit_code=0,
            execution_time=1.0,
            command=["echo", "hello"],
        )
        assert result.success is True

        # Failure
        result = CommandResult(
            output="output",
            exit_code=1,
            execution_time=1.0,
            command=["echo", "hello"],
        )
        assert result.success is False


class TestRunCommand:
    """Tests for the run_command function."""

    def test_run_command_success(self) -> None:
        """Test running a command successfully."""
        with patch("subprocess.Popen") as mock_popen:
            # Mock process
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["line1\n", "line2\n", ""]
            mock_process.stdout.read.return_value = ""
            mock_process.wait.return_value = 0
            mock_popen.return_value = mock_process

            # Run command
            result = run_command(["echo", "hello"], verbose=False)

            # Check result
            assert result.output == "line1\nline2\n"
            assert result.exit_code == 0
            assert result.command == ["echo", "hello"]
            assert result.execution_time > 0

    def test_run_command_failure(self) -> None:
        """Test running a command that fails."""
        with patch("subprocess.Popen") as mock_popen:
            # Mock process
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["error\n", ""]
            mock_process.stdout.read.return_value = ""
            mock_process.wait.return_value = 1
            mock_popen.return_value = mock_process

            # Run command
            result = run_command(["false"], verbose=False)

            # Check result
            assert result.output == "error\n"
            assert result.exit_code == 1
            assert result.command == ["false"]
            assert result.execution_time > 0

    def test_run_command_check_success(self) -> None:
        """Test running a command with check=True that succeeds."""
        with patch("subprocess.Popen") as mock_popen:
            # Mock process
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["line1\n", "line2\n", ""]
            mock_process.stdout.read.return_value = ""
            mock_process.wait.return_value = 0
            mock_popen.return_value = mock_process

            # Run command
            result = run_command(["echo", "hello"], verbose=False, check=True)

            # Check result
            assert result.output == "line1\nline2\n"
            assert result.exit_code == 0
            assert result.command == ["echo", "hello"]
            assert result.execution_time > 0

    def test_run_command_check_failure(self) -> None:
        """Test running a command with check=True that fails."""
        with patch("subprocess.Popen") as mock_popen:
            # Mock process
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["error\n", ""]
            mock_process.stdout.read.return_value = ""
            mock_process.wait.return_value = 1
            mock_popen.return_value = mock_process

            # Run command
            with pytest.raises(TaskExecutionFailedError) as excinfo:
                run_command(["false"], verbose=False, check=True)

            # Check exception
            assert "shell_command" in str(excinfo.value)
            assert "false" in str(excinfo.value)
            assert "1" in str(excinfo.value)

    def test_run_command_callable_args(self) -> None:
        """Test running a command with callable args."""
        with patch("subprocess.Popen") as mock_popen:
            # Mock process
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["line1\n", ""]
            mock_process.stdout.read.return_value = ""
            mock_process.wait.return_value = 0
            mock_popen.return_value = mock_process

            # Run command
            result = run_command(lambda: ["echo", "hello"], verbose=False)

            # Check result
            assert result.output == "line1\n"
            assert result.exit_code == 0
            assert result.command == ["echo", "hello"]
            assert result.execution_time > 0

    def test_run_command_with_env(self) -> None:
        """Test running a command with environment variables."""
        with (
            patch("subprocess.Popen") as mock_popen,
            patch.dict(os.environ, {"EXISTING": "value"}, clear=True),
        ):
            # Mock process
            mock_process = MagicMock()
            mock_process.stdout.readline.side_effect = ["line1\n", ""]
            mock_process.stdout.read.return_value = ""
            mock_process.wait.return_value = 0
            mock_popen.return_value = mock_process

            # Run command
            result = run_command(
                ["echo", "hello"],
                env={"TEST": "value"},
                verbose=False,
            )

            # Check result
            assert result.output == "line1\n"
            assert result.exit_code == 0

            # Check that Popen was called with the correct environment
            _, kwargs = mock_popen.call_args
            assert kwargs["env"] == {"EXISTING": "value", "TEST": "value"}

    def test_run_command_exception(self) -> None:
        """Test running a command that raises an exception."""
        with patch("subprocess.Popen") as mock_popen:
            # Mock Popen to raise an exception
            mock_popen.side_effect = Exception("Test exception")

            # Run command
            result = run_command(["echo", "hello"], verbose=False)

            # Check result
            assert "Test exception" in result.output
            assert result.exit_code == -1
            assert result.command == ["echo", "hello"]
            assert result.execution_time > 0

    def test_run_command_exception_check(self) -> None:
        """Test running a command that raises an exception with check=True."""
        with patch("subprocess.Popen") as mock_popen:
            # Mock Popen to raise an exception
            mock_popen.side_effect = Exception("Test exception")

            # Run command
            with pytest.raises(TaskExecutionFailedError) as excinfo:
                run_command(["echo", "hello"], verbose=False, check=True)

            # Check exception
            assert "shell_command" in str(excinfo.value)
            assert "echo hello" in str(excinfo.value)
