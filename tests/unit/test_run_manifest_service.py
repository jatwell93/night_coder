"""Unit tests for run manifest builder/writer (T041)."""

from __future__ import annotations

import json

from services.run_manifest_service import build_and_write_run_manifest


def test_build_and_write_run_manifest_persists_schema_compliant_payload(tmp_path) -> None:
    manifest_path = build_and_write_run_manifest(
        artifacts_root=tmp_path,
        run_id="run-20260427T213000Z-a1b2c3d4",
        git_sha="abc1234def",
        profile="offline",
        scenario_ids=["SCN-PILOT-001-configurable-upstream-happy-path"],
        verdict_refs=["runs/x/verdicts/SCN-PILOT-001.json"],
        artifact_refs=["runs/x/artifacts/summary.json"],
        trace_refs=["runs/x/traces/events.jsonl"],
        status="completed",
        notes="Pilot run summary",
    )

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == "run-20260427T213000Z-a1b2c3d4"
    assert payload["summary"]["status"] == "completed"
