"""T070 [US3] integration test for partial telemetry on failed runs."""

from __future__ import annotations

import pytest

from services.telemetry_service import capture_partial_failed_run_telemetry


@pytest.mark.integration
@pytest.mark.us3
def test_failed_run_still_emits_partial_telemetry_bundle() -> None:
    telemetry = capture_partial_failed_run_telemetry(
        run_id="run-20260427T201500Z-12ab34cd",
        emitted_events=[
            {"event_type": "execution", "severity": "info"},
            {"event_type": "guardrail", "severity": "error"},
        ],
        failure_reason="orchestrator crashed before finalize",
    )

    assert telemetry["run_id"] == "run-20260427T201500Z-12ab34cd"
    assert telemetry["partial"] is True
    assert len(telemetry["events"]) == 2
