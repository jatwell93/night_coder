"""Run completion pipeline with verdict generation (T032)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from services.judge_fallback_service import persist_evaluation_pending_record
from services.judge_runner_service import run_external_judge
from services.judge_verdict_service import build_and_persist_verdict
from services.scenario_evidence_service import assemble_scenario_evidence


@dataclass(frozen=True, slots=True)
class CompletionResult:
    run_status: str
    verdict: dict[str, Any]
    verdict_path: Path


def complete_run_with_outcome_judging(
    *,
    run_id: str,
    scenario_id: str,
    expected_outcome: str,
    observed_outcome: str,
    evidence_refs: list[str],
    verdict_output_dir: Path,
) -> CompletionResult:
    evidence = assemble_scenario_evidence(
        scenario_id=scenario_id,
        expected_outcome=expected_outcome,
        observed_outcome=observed_outcome,
        evidence_refs=evidence_refs,
    )
    try:
        decision = run_external_judge(evidence)
    except RuntimeError as error:
        verdict_path = persist_evaluation_pending_record(
            output_dir=verdict_output_dir,
            run_id=run_id,
            scenario_id=scenario_id,
            error=error,
            evidence_refs=list(evidence.evidence_refs),
        )
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        return CompletionResult(
            run_status="evaluation-pending",
            verdict=verdict,
            verdict_path=verdict_path,
        )

    verdict_path = build_and_persist_verdict(
        output_dir=verdict_output_dir,
        run_id=run_id,
        scenario_id=scenario_id,
        satisfied=decision.satisfied,
        score=decision.score,
        reasoning=decision.reasoning,
        evidence_refs=list(evidence.evidence_refs),
    )
    verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    return CompletionResult(
        run_status="completed",
        verdict=verdict,
        verdict_path=verdict_path,
    )
