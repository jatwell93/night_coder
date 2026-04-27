"""Morning review report assembly from telemetry and verdicts (T054)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class MorningReviewReport:
    """Operator-facing summary for morning run review."""

    run_id: str
    total_scenarios: int
    unsatisfied_count: int
    report_path: Path


def assemble_morning_review_report(
    *,
    run_id: str,
    telemetry_events: list[dict[str, Any]],
    verdicts: list[dict[str, Any]],
    output_dir: Path,
) -> MorningReviewReport:
    """Build and persist a compact report from telemetry and verdict outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    unsatisfied_count = sum(1 for verdict in verdicts if not bool(verdict.get("satisfied")))
    payload = {
        "run_id": run_id,
        "total_scenarios": len(verdicts),
        "unsatisfied_count": unsatisfied_count,
        "telemetry_event_count": len(telemetry_events),
    }
    target = output_dir / f"{run_id}.morning-review.json"
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return MorningReviewReport(
        run_id=run_id,
        total_scenarios=len(verdicts),
        unsatisfied_count=unsatisfied_count,
        report_path=target,
    )
