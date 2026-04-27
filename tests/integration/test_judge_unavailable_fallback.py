"""T066 [US2] integration test for judge-unavailable fallback handling."""

from __future__ import annotations

import pytest

from services.run_completion_service import complete_run_with_outcome_judging


@pytest.mark.integration
@pytest.mark.us2
def test_judge_unavailable_sets_evaluation_pending(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _raise_unavailable(*_args, **_kwargs) -> None:
        raise RuntimeError("judge harness unavailable")

    monkeypatch.setattr(
        "services.run_completion_service.run_external_judge",
        _raise_unavailable,
    )

    result = complete_run_with_outcome_judging(
        run_id="run-20260427T080000Z-cafefeed",
        scenario_id="SCN-PILOT-002-fallback",
        expected_outcome="response contains status=ok",
        observed_outcome="response contains status=error",
        evidence_refs=["runs/x/evidence/SCN-PILOT-002-fallback/stdout.txt"],
        verdict_output_dir=tmp_path,
    )

    assert result.run_status == "evaluation-pending"
    assert result.verdict["reason_code"] == "JDG.fallback.evaluation-pending"
    assert result.verdict["error"] == "judge harness unavailable"
