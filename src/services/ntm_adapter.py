"""NTM adapter wiring for command interception (T080)."""

from __future__ import annotations

import shutil
import subprocess

__all__ = [
    "NtmAdapterError",
    "assert_ntm_available",
    "ntm_check_command_allowed",
]


class NtmAdapterError(RuntimeError):
    """Raised when NTM is unavailable or policy check fails."""


def assert_ntm_available() -> None:
    """Raise if the `ntm` binary is not on PATH."""
    if shutil.which("ntm") is None:
        msg = "ntm is not available on PATH"
        raise NtmAdapterError(msg)


def ntm_check_command_allowed(command: str) -> bool:
    """Check command against NTM policy engine.

    Uses:
      ntm safety check "<command>"

    Returns True when NTM exits 0 for this command.
    """
    assert_ntm_available()
    ntm_path = shutil.which("ntm")
    if ntm_path is None:
        msg = "ntm is not available on PATH"
        raise NtmAdapterError(msg)
    result = subprocess.run(  # noqa: S603 - intentional guarded subprocess invocation for policy check.
        [ntm_path, "safety", "check", command],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0
