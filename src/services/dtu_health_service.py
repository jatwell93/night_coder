"""DTU dependency readiness and startup failure classification (T037)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DtuStartupClassification:
    """Classification result for DTU startup failures."""

    dependency_name: str
    status: str
    reason_code: str
    detail: str


def classify_dtu_startup_failure(
    *, dependency_name: str, error_message: str
) -> DtuStartupClassification:
    """Classify DTU startup failures as infrastructure run failures."""
    return DtuStartupClassification(
        dependency_name=dependency_name,
        status="failed",
        reason_code="DTU.error.startup-failure",
        detail=error_message,
    )
