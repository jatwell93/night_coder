"""T025 [US2] contract test for judge verdict schema compliance."""

from __future__ import annotations

import json

import pytest

from lib.verdict_validation import validate_verdict
from services.judge_verdict_service import build_and_persist_verdict


@pytest.mark.contract
@pytest.mark.us2
def test_persisted_verdict_matches_contract(tmp_path) -> None:
    verdict_path = build_and_persist_verdict(
        output_dir=tmp_path,
        run_id="run-20260423T130000Z-deadbeef",
        scenario_id="SCN-PILOT-001-outcome",
        satisfied=False,
        score=0.2,
        reasoning="Process completed but expected user-visible output mismatch.",
        evidence_refs=["runs/x/evidence/SCN-PILOT-001-outcome/stdout.txt"],
    )

    payload = json.loads(verdict_path.read_text(encoding="utf-8"))
    validate_verdict(payload)
    assert payload["scenario_id"] == "SCN-PILOT-001-outcome"
    assert payload["satisfied"] is False
