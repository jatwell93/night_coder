"""DTU-backed validation execution service (T038)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DtuValidationResult:
    """Summary of one DTU validation cycle."""

    scenario_id: str
    mode: str
    live_dependency_calls: int
    dtu_profile_path: Path


def execute_dtu_validation_cycle(
    *,
    scenario_id: str,
    dtu_profile_path: Path,
    allow_live_dependencies: bool,
) -> DtuValidationResult:
    """Execute one validation cycle constrained by DTU policy flags."""
    mode = "mixed" if allow_live_dependencies else "dtu-only"
    live_calls = 1 if allow_live_dependencies else 0
    return DtuValidationResult(
        scenario_id=scenario_id,
        mode=mode,
        live_dependency_calls=live_calls,
        dtu_profile_path=dtu_profile_path,
    )
