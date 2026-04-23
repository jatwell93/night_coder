"""Canonical layout for a run's output artifacts.

Every overnight run writes artifacts under a single root directory (typically
``/home/deploy/night_coder/artifacts/`` on the VPS). This module centralises
the path layout so services never hand-compose paths and never accidentally
escape the root.

Layout::

    <root>/
      runs/
        <run_id>/
          manifest.json
          events.jsonl
          traces/
          logs/
          verdicts/
            <scenario_id>.json
          evidence/
            <scenario_id>/

Identifier validation rejects path separators and traversal sequences so
``evidence_for("../../etc")`` always raises rather than silently escaping.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

__all__ = ["ArtifactPaths", "for_run"]

_SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _require_safe_id(value: str, *, field: str) -> None:
    if not value:
        msg = f"{field} must be non-empty"
        raise ValueError(msg)
    if not _SAFE_ID_PATTERN.match(value):
        msg = (
            f"{field} {value!r} is not a safe identifier; allowed characters: "
            "alphanumerics, dot, underscore, hyphen (must not start with '.', '-', or '_')"
        )
        raise ValueError(msg)


@dataclass(frozen=True)
class ArtifactPaths:
    """Path resolver for a single run's artifact tree.

    Construct with the artifact root and a validated ``run_id``. All resolver
    methods return :class:`pathlib.Path` instances strictly under ``root``.
    """

    root: Path
    run_id: str

    def __post_init__(self) -> None:
        _require_safe_id(self.run_id, field="run_id")

    @property
    def run_root(self) -> Path:
        return self.root / "runs" / self.run_id

    @property
    def manifest(self) -> Path:
        return self.run_root / "manifest.json"

    @property
    def events_log(self) -> Path:
        return self.run_root / "events.jsonl"

    @property
    def traces_dir(self) -> Path:
        return self.run_root / "traces"

    @property
    def logs_dir(self) -> Path:
        return self.run_root / "logs"

    @property
    def verdicts_dir(self) -> Path:
        return self.run_root / "verdicts"

    @property
    def evidence_root(self) -> Path:
        return self.run_root / "evidence"

    def verdict_for(self, scenario_id: str) -> Path:
        _require_safe_id(scenario_id, field="scenario_id")
        return self.verdicts_dir / f"{scenario_id}.json"

    def evidence_for(self, scenario_id: str) -> Path:
        _require_safe_id(scenario_id, field="scenario_id")
        return self.evidence_root / scenario_id

    def ensure_run_tree(self) -> None:
        """Create the run root and its standard subdirectories (idempotent)."""
        for directory in (
            self.run_root,
            self.traces_dir,
            self.logs_dir,
            self.verdicts_dir,
            self.evidence_root,
        ):
            directory.mkdir(parents=True, exist_ok=True)


def for_run(root: Path, run_id: str) -> ArtifactPaths:
    """Convenience constructor."""
    return ArtifactPaths(root=root, run_id=run_id)
