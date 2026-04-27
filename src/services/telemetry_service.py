"""Telemetry publishing helpers for US3 workflows (T040)."""

from __future__ import annotations

from typing import Any


def capture_partial_failed_run_telemetry(
    *,
    run_id: str,
    emitted_events: list[dict[str, Any]],
    failure_reason: str,
) -> dict[str, Any]:
    """Capture partial telemetry when a run fails before full finalization."""
    return {
        "run_id": run_id,
        "partial": True,
        "events": emitted_events,
        "failure_reason": failure_reason,
    }
