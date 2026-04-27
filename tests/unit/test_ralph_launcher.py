"""Tests for Ralph launcher integration (T081)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from services.ralph_launcher import build_ralph_run_command


def test_build_ralph_command_minimal() -> None:
    command = build_ralph_run_command(config_path=Path("ralph.yml"))
    assert command == ["ralph", "run", "-c", "ralph.yml"]


def test_build_ralph_command_with_overrides() -> None:
    command = build_ralph_run_command(
        config_path=Path("ralph.yml"),
        prompt_file=Path("PROMPT.md"),
        backend="gemini",
        max_iterations=12,
    )
    assert command == [
        "ralph",
        "run",
        "-c",
        "ralph.yml",
        "-P",
        "PROMPT.md",
        "--backend",
        "gemini",
        "--max-iterations",
        "12",
    ]


def test_launch_uses_ntm_gate() -> None:
    completed = Mock(returncode=0, stdout="ok", stderr="")
    with (
        patch("services.ralph_launcher.ntm_check_command_allowed", return_value=True),
        patch("services.ralph_launcher.subprocess.run", return_value=completed),
    ):
        from services.ralph_launcher import launch_ralph_run

        result = launch_ralph_run(config_path=Path("ralph.yml"))
        assert result.returncode == 0
