"""T027 [US2] integration test for unsatisfactory verdict path."""

from __future__ import annotations

import pytest

from services.run_completion_service import complete_run_with_outcome_judging


@pytest.mark.integration
@pytest.mark.us2
def test_run_completes_with_unsatisfactory_verdict_when_outcome_mismatch(tmp_path) -> None:
    result = complete_run_with_outcome_judging(
        run_id="run-20260423T130000Z-deadbeef",
        scenario_id="SCN-PILOT-001-outcome",
        expected_outcome="response contains status=ok",
        observed_outcome="response contains status=error",
        evidence_refs=["runs/x/evidence/SCN-PILOT-001-outcome/stdout.txt"],
        verdict_output_dir=tmp_path,
    )

    assert result.run_status == "completed"
    assert result.verdict["satisfied"] is False
    assert result.verdict["score"] < 0.5
