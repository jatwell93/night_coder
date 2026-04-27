"""T053 [US3] integration test for morning review report assembly."""

from __future__ import annotations

import pytest

from services.morning_review_service import assemble_morning_review_report


@pytest.mark.integration
@pytest.mark.us3
def test_morning_review_report_assembles_telemetry_and_verdicts(tmp_path) -> None:
    report = assemble_morning_review_report(
        run_id="run-20260427T190000Z-1234abcd",
        telemetry_events=[
            {"event_type": "execution", "severity": "info"},
            {"event_type": "judge", "severity": "warn"},
        ],
        verdicts=[
            {"scenario_id": "SCN-PILOT-001", "satisfied": True, "score": 0.94},
            {"scenario_id": "SCN-PILOT-002", "satisfied": False, "score": 0.31},
        ],
        output_dir=tmp_path,
    )

    assert report.run_id == "run-20260427T190000Z-1234abcd"
    assert report.total_scenarios == 2
    assert report.unsatisfied_count == 1
