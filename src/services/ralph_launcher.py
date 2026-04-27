"""Ralph orchestrator launch integration (T081)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from services.ntm_adapter import ntm_check_command_allowed

__all__ = ["RalphLaunchResult", "build_ralph_run_command", "launch_ralph_run"]


@dataclass(frozen=True, slots=True)
class RalphLaunchResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def build_ralph_run_command(
    *,
    config_path: Path,
    prompt_file: Path | None = None,
    backend: str | None = None,
    max_iterations: int | None = None,
) -> list[str]:
    """Build a deterministic `ralph run` command line."""
    command: list[str] = ["ralph", "run", "-c", str(config_path)]
    if prompt_file is not None:
        command.extend(["-P", str(prompt_file)])
    if backend is not None:
        command.extend(["--backend", backend])
    if max_iterations is not None:
        command.extend(["--max-iterations", str(max_iterations)])
    return command


def launch_ralph_run(
    *,
    config_path: Path,
    prompt_file: Path | None = None,
    backend: str | None = None,
    max_iterations: int | None = None,
    working_directory: Path | None = None,
    enforce_ntm: bool = True,
) -> RalphLaunchResult:
    """Launch Ralph orchestration loop and capture output."""
    command = build_ralph_run_command(
        config_path=config_path,
        prompt_file=prompt_file,
        backend=backend,
        max_iterations=max_iterations,
    )
    if enforce_ntm:
        joined = " ".join(command)
        if not ntm_check_command_allowed(joined):
            msg = f"NTM denied Ralph command: {joined}"
            raise RuntimeError(msg)
    completed = subprocess.run(  # noqa: S603 - command list is constructed by trusted launcher inputs.
        command,
        cwd=str(working_directory) if working_directory is not None else None,
        capture_output=True,
        text=True,
        check=False,
    )
    return RalphLaunchResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
