"""Integration tests for end-of-run finalization workflow (T042)."""

from __future__ import annotations

import pytest

from services.run_finalize_service import finalize_run


@pytest.mark.integration
@pytest.mark.us3
def test_finalize_run_links_telemetry_memory_and_manifest(tmp_path) -> None:
    result = finalize_run(
        artifacts_root=tmp_path,
        run_id="run-20260427T214000Z-feedbeef",
        git_sha="abc1234def",
        profile="offline",
        scenario_ids=["SCN-PILOT-001-configurable-upstream-happy-path"],
        verdict_refs=["runs/x/verdicts/SCN-PILOT-001.json"],
        telemetry_events=[{"event_type": "execution", "severity": "info"}],
        memory_candidates=[{"memory_id": "m1", "age_days": 2, "tags": ["pilot"]}],
    )

    assert result.manifest_path.exists()
    assert result.telemetry_bundle["partial"] is False
    assert len(result.selected_memories) == 1
