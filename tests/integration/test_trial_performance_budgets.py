"""T046 integration checks for pilot performance and review budgets."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from services.morning_review_service import assemble_morning_review_report


@pytest.mark.integration
def test_morning_review_report_assembly_stays_within_budget(tmp_path) -> None:
    telemetry = [{"event_type": "execution", "severity": "info"} for _ in range(200)]
    verdicts = [
        {"scenario_id": f"SCN-PILOT-00{i}", "satisfied": i % 2 == 0, "score": 0.7}
        for i in range(1, 6)
    ]
    started = datetime.now(tz=UTC)
    report = assemble_morning_review_report(
        run_id="run-20260427T223000Z-b16b00b5",
        telemetry_events=telemetry,
        verdicts=verdicts,
        output_dir=tmp_path,
    )
    elapsed = datetime.now(tz=UTC) - started

    assert report.total_scenarios == 5
    assert elapsed < timedelta(seconds=5)
