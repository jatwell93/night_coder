"""Tests for src/lib/manifest_validation.py."""

from __future__ import annotations

from typing import Any

import pytest

from lib import manifest_validation
from lib.manifest_validation import ManifestValidationError


def valid_manifest() -> dict[str, Any]:
    return {
        "run_id": "run-20260423T143005Z-a1b2c3d4",
        "git_sha": "abc1234def5678",
        "profile": "offline",
        "scenario_ids": ["SCN-PILOT-001-upstream-ok"],
        "verdict_refs": ["runs/run-xyz/verdicts/SCN-PILOT-001-upstream-ok.json"],
        "artifact_refs": [],
        "trace_refs": [],
        "summary": {
            "status": "completed",
            "started_at": "2026-04-23T13:00:00Z",
            "ended_at": "2026-04-23T13:42:00Z",
        },
    }


class TestValidateManifest:
    def test_valid_manifest_passes(self) -> None:
        manifest_validation.validate_manifest(valid_manifest())

    def test_missing_required_field_raises(self) -> None:
        bad = valid_manifest()
        del bad["run_id"]
        with pytest.raises(ManifestValidationError, match="run_id"):
            manifest_validation.validate_manifest(bad)

    def test_short_git_sha_rejected(self) -> None:
        bad = valid_manifest()
        bad["git_sha"] = "abc"
        with pytest.raises(ManifestValidationError, match="git_sha"):
            manifest_validation.validate_manifest(bad)

    def test_invalid_profile_rejected(self) -> None:
        bad = valid_manifest()
        bad["profile"] = "staging"
        with pytest.raises(ManifestValidationError):
            manifest_validation.validate_manifest(bad)

    def test_empty_scenario_ids_rejected(self) -> None:
        bad = valid_manifest()
        bad["scenario_ids"] = []
        with pytest.raises(ManifestValidationError, match="scenario_ids"):
            manifest_validation.validate_manifest(bad)

    def test_unknown_top_level_property_rejected(self) -> None:
        bad = valid_manifest()
        bad["extra"] = "not allowed"
        with pytest.raises(ManifestValidationError):
            manifest_validation.validate_manifest(bad)

    def test_evaluation_pending_status_accepted(self) -> None:
        m = valid_manifest()
        m["summary"]["status"] = "evaluation-pending"
        manifest_validation.validate_manifest(m)

    def test_invalid_summary_status_rejected(self) -> None:
        bad = valid_manifest()
        bad["summary"]["status"] = "weird"
        with pytest.raises(ManifestValidationError):
            manifest_validation.validate_manifest(bad)

    def test_summary_notes_accepted(self) -> None:
        m = valid_manifest()
        m["summary"]["notes"] = "Re-ran after DTU restart."
        manifest_validation.validate_manifest(m)

    def test_extra_summary_property_allowed(self) -> None:
        # Schema declares summary.additionalProperties=true.
        m = valid_manifest()
        m["summary"]["custom_metric"] = 42
        manifest_validation.validate_manifest(m)


class TestIsValidManifest:
    def test_returns_true_for_valid(self) -> None:
        assert manifest_validation.is_valid_manifest(valid_manifest()) is True

    def test_returns_false_for_invalid(self) -> None:
        bad = valid_manifest()
        del bad["summary"]
        assert manifest_validation.is_valid_manifest(bad) is False


class TestErrorDetails:
    def test_error_includes_path(self) -> None:
        bad = valid_manifest()
        bad["summary"]["started_at"] = "not-a-datetime"
        with pytest.raises(ManifestValidationError) as exc_info:
            manifest_validation.validate_manifest(bad)
        assert "summary" in str(exc_info.value)
        assert "started_at" in str(exc_info.value)
