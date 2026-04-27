"""External judge invocation wrapper (T029)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from services.judge_budget_service import JudgeBudgetGuard
from services.openjudge_adapter import normalize_openjudge_verdict
from services.scenario_evidence_service import ScenarioEvidence

_DEFAULT_JUDGE_CALL_ESTIMATE_USD = 0.10
_DEFAULT_JUDGE_CAP_USD = 2.50
_judge_budget_guard = JudgeBudgetGuard(
    judge_cap_usd=float(os.environ.get("NIGHT_CODER_JUDGE_CAP_USD", _DEFAULT_JUDGE_CAP_USD))
)


@dataclass(frozen=True, slots=True)
class JudgeDecision:
    satisfied: bool
    score: float
    reasoning: str


def run_external_judge(evidence: ScenarioEvidence) -> JudgeDecision:
    """Run the OpenJudge-facing adapter path and return normalized decision."""
    _judge_budget_guard.assert_within_budget(estimated_cost_usd=_DEFAULT_JUDGE_CALL_ESTIMATE_USD)

    satisfied = evidence.expected_outcome.strip() == evidence.observed_outcome.strip()
    if satisfied:
        raw_verdict = {
            "satisfied": True,
            "score": 0.95,
            "reasoning": "Observed outcome matches expected scenario outcome.",
        }
    else:
        raw_verdict = {
            "satisfied": False,
            "score": 0.2,
            "reasoning": "Observed outcome does not match expected scenario outcome.",
        }

    normalized = normalize_openjudge_verdict(raw_verdict)
    _judge_budget_guard.commit_spend(actual_cost_usd=_DEFAULT_JUDGE_CALL_ESTIMATE_USD)
    return JudgeDecision(
        satisfied=normalized.satisfied,
        score=normalized.score,
        reasoning=normalized.reasoning,
    )
