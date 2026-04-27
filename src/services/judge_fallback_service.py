"""Judge-unavailable fallback handling (T067)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lib.run_identity import to_iso8601, utc_now

JUDGE_FALLBACK_REASON_CODE = "JDG.fallback.evaluation-pending"


def persist_evaluation_pending_record(
    *,
    output_dir: Path,
    run_id: str,
    scenario_id: str,
    error: Exception,
    evidence_refs: list[str],
) -> Path:
    """Persist fallback record when the external judge is unavailable."""
    output_dir.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "run_id": run_id,
        "scenario_id": scenario_id,
        "status": "evaluation-pending",
        "reason_code": JUDGE_FALLBACK_REASON_CODE,
        "error": str(error),
        "evidence_refs": evidence_refs,
        "issued_at": to_iso8601(utc_now()),
    }
    target = output_dir / f"{scenario_id}.evaluation-pending.json"
    target.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return target
