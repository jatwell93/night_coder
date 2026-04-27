"""T034 [US3] contract tests for run manifest schema compliance."""

from __future__ import annotations

from typing import Any

import pytest

from lib.manifest_validation import ManifestValidationError, validate_manifest


def _manifest() -> dict[str, Any]:
    return {
        "run_id": "run-20260427T072500Z-9f0e1d2c",
        "git_sha": "abcdef1234567",
        "profile": "offline",
        "scenario_ids": ["SCN-PILOT-001-configurable-upstream-happy-path"],
        "verdict_refs": ["runs/abc/verdicts/SCN-PILOT-001.json"],
        "artifact_refs": ["runs/abc/artifacts/summary.json"],
        "trace_refs": ["runs/abc/traces/run.jsonl"],
        "summary": {
            "status": "completed",
            "started_at": "2026-04-27T19:00:00Z",
            "ended_at": "2026-04-27T19:10:00Z",
        },
    }


@pytest.mark.contract
@pytest.mark.us3
def test_run_manifest_contract_accepts_valid_payload() -> None:
    validate_manifest(_manifest())


@pytest.mark.contract
@pytest.mark.us3
def test_run_manifest_contract_rejects_invalid_summary_status() -> None:
    bad = _manifest()
    bad["summary"]["status"] = "running"
    with pytest.raises(ManifestValidationError):
        validate_manifest(bad)
