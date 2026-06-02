from __future__ import annotations

import logging
import os
import subprocess
from collections.abc import Sequence

logger = logging.getLogger(__name__)


def run_subprocess_safely(
    args: Sequence[str],
    *,
    timeout_seconds: float = 30.0,
    cwd: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess with a timeout and clear, logged failure handling.

    Safety contract (SEC-4):

    - ``args`` must be a non-empty sequence; the first element is the executable.
      Quill never builds these from untrusted document content — callers pass a
      fixed tool name (e.g. a bundled binary) plus controlled arguments.
    - ``cwd``, when provided, must already exist and be a directory. The working
      directory is validated before launch so a caller cannot accidentally point
      the child process at a missing or non-directory path; callers are expected
      to pass a trusted, absolute directory they control.

    Raises:
        ValueError: if ``args`` is empty or ``cwd`` is not an existing directory.
        subprocess.TimeoutExpired: if the process exceeds ``timeout_seconds``.
        OSError: if the executable cannot be launched (surfaced after logging).
    """

    arg_list = list(args)
    if not arg_list:
        raise ValueError("run_subprocess_safely requires a non-empty args sequence")
    if cwd is not None and not os.path.isdir(cwd):
        raise ValueError(f"cwd must be an existing directory: {cwd!r}")
    logger.info("Running subprocess args=%r timeout=%s cwd=%r", arg_list, timeout_seconds, cwd)
    try:
        result = subprocess.run(
            arg_list,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        logger.info("Subprocess finished returncode=%s args=%r", result.returncode, arg_list)
        return result
    except subprocess.TimeoutExpired:
        logger.exception("Subprocess timed out args=%r timeout=%s", arg_list, timeout_seconds)
        raise
    except OSError as error:
        logger.exception("Subprocess failed to launch args=%r cwd=%r", arg_list, cwd)
        raise OSError(f"Could not run {arg_list[0]!r}: {error}") from error
