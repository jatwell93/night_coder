"""Verdict persistence workflow (T030)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from lib.run_identity import to_iso8601, utc_now
from lib.verdict_validation import validate_verdict


def build_and_persist_verdict(
    *,
    output_dir: Path,
    run_id: str,
    scenario_id: str,
    satisfied: bool,
    score: float,
    reasoning: str,
    evidence_refs: list[str],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    verdict = {
        "verdict_id": f"vdt-{uuid4().hex[:12]}",
        "run_id": run_id,
        "scenario_id": scenario_id,
        "satisfied": satisfied,
        "score": score,
        "reasoning": reasoning,
        "evidence_refs": evidence_refs,
        "issued_at": to_iso8601(utc_now()),
    }
    validate_verdict(verdict)
    target = output_dir / f"{scenario_id}.json"
    target.write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    return target
