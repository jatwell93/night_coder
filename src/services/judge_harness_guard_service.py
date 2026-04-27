"""Immutable harness path guard (T031)."""

from __future__ import annotations

from pathlib import Path


def assert_harness_path_is_immutable(*, harness_path: Path, repo_root: Path) -> None:
    """Ensure judge harness path is outside agent-writable repo root."""
    harness_resolved = harness_path.resolve()
    repo_resolved = repo_root.resolve()
    if harness_resolved == repo_resolved or harness_resolved.is_relative_to(repo_resolved):
        msg = (
            "Judge harness path must be outside the repository root "
            f"(harness={harness_resolved}, repo={repo_resolved})"
        )
        raise ValueError(msg)
