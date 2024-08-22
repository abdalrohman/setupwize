import logging
import os
import shlex
import subprocess
import sys
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


def run_command(
    args: list[str] | Callable[[], list[str]],
    env: dict[str, str] | None = None,
    verbose: bool = True,
    capture_output: bool = True,
    **kwargs: Any,  # noqa: ANN401
) -> tuple[str, int]:
    """
    Runs a command and captures its output.

    Args:
        args: A list of strings representing the command and its arguments, or a callable that returns such a list.
        env: An optional dictionary specifying environment variables.
        verbose: A boolean indicating whether to log command execution details.
        capture_output: A boolean indicating whether to capture the command's output.
        **kwargs: Additional keyword arguments to pass to subprocess.Popen.

    Returns:
        A tuple containing the captured output (if any) and the command's exit code.
    """
    if verbose:
        start_time = time.time()

    if callable(args):
        args = args()

    if env is not None:
        logger.info(f"Env: {env}")
        env_copy = os.environ.copy()
        env_copy.update(env)
        kwargs.setdefault("env", env_copy)

    if verbose:
        logger.info(f"Running: {shlex.join(args)}")

    if capture_output:
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.STDOUT)
        # Unbuffered output for maximum responsiveness
        # Use a smaller bufsize for more responsive output
        kwargs.setdefault("bufsize", 0)
        kwargs.setdefault("universal_newlines", True)

    try:
        with subprocess.Popen(args, **kwargs) as proc:  # noqa: S603
            # if proc.stdout and (verbose or "sudo" in args):
            if proc.stdout and (verbose):
                while True:
                    output = proc.stdout.read(1)  # Read one character at a time
                    if output == "" and proc.poll() is not None:
                        break
                    if output == "\r":  # Carriage return, likely an in-place update
                        sys.stdout.write("\r")  # Move cursor to beginning of line
                        sys.stdout.flush()
                    else:
                        sys.stdout.write(output)
                        sys.stdout.flush()

            if proc.stderr:
                while True:
                    error = proc.stderr.readline()
                    if error == "" and proc.poll() is not None:
                        break
                    if error:
                        sys.stderr.write(error)
                        sys.stderr.flush()

        returncode = proc.wait()

    except subprocess.CalledProcessError as exc:
        logger.exception(
            f"Failed to run command '{shlex.join(args)}' (exit code {exc.returncode}):\n{exc.output}",
        )
        raise
    ## Handle keyboard interrupt from outside run_command function
    # except KeyboardInterrupt as exc:
    #     logger.info("\nTerminating...")
    #     raise SystemExit(1) from exc
    except Exception as exc:
        logger.exception(f"Failed to run command '{shlex.join(args)}'")
        raise SystemExit(1) from exc

    if verbose:
        runtime = time.time() - start_time
        logger.info(f"Execution time: {runtime:.3f} seconds")

    return "", returncode
