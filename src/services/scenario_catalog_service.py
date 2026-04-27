"""Read-only scenario catalog loader with boundary enforcement (T071)."""

from __future__ import annotations

import re
import stat
from pathlib import Path

_SCENARIO_HEADER_RE = re.compile(r"^#\s+(SCN-[A-Z0-9-]+)\s*:")


def load_scenario_catalog(*, catalog_path: Path) -> dict[str, str]:
    """Load scenario markdown files from a read-only catalog path."""
    mode = catalog_path.stat().st_mode
    if mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
        msg = (
            f"Scenario catalog at {catalog_path!r} has write bits set. "
            "Lock the catalog before starting a run: chmod -R a-w <path>"
        )
        raise PermissionError(msg)

    scenarios: dict[str, str] = {}
    for scenario_file in sorted(catalog_path.glob("*.md")):
        content = scenario_file.read_text(encoding="utf-8")
        first_line = content.splitlines()[0] if content.splitlines() else ""
        match = _SCENARIO_HEADER_RE.match(first_line)
        scenario_id = match.group(1) if match else scenario_file.stem
        scenarios[scenario_id] = content
    return scenarios
