"""Tests for src/lib/verdict_validation.py."""

from __future__ import annotations

from typing import Any

import pytest

from lib import verdict_validation
from lib.verdict_validation import VerdictValidationError


def valid_verdict() -> dict[str, Any]:
    return {
        "verdict_id": "vdt-20260423T134200Z-a1b2c3d4",
        "run_id": "run-20260423T130000Z-deadbeef",
        "scenario_id": "SCN-PILOT-001-upstream-ok",
        "satisfied": True,
        "score": 0.95,
        "reasoning": "Agent made one call and received 200 with status ok.",
        "evidence_refs": [
            "runs/run-20260423T130000Z-deadbeef/evidence/SCN-PILOT-001-upstream-ok/stdout.txt",
        ],
        "issued_at": "2026-04-23T13:42:00Z",
    }


class TestValidateVerdict:
    def test_valid_verdict_passes(self) -> None:
        verdict_validation.validate_verdict(valid_verdict())

    def test_score_above_one_rejected(self) -> None:
        bad = valid_verdict()
        bad["score"] = 1.5
        with pytest.raises(VerdictValidationError, match="score"):
            verdict_validation.validate_verdict(bad)

    def test_score_below_zero_rejected(self) -> None:
        bad = valid_verdict()
        bad["score"] = -0.1
        with pytest.raises(VerdictValidationError, match="score"):
            verdict_validation.validate_verdict(bad)

    def test_empty_reasoning_rejected(self) -> None:
        bad = valid_verdict()
        bad["reasoning"] = ""
        with pytest.raises(VerdictValidationError, match="reasoning"):
            verdict_validation.validate_verdict(bad)

    def test_missing_evidence_refs_rejected(self) -> None:
        bad = valid_verdict()
        bad["evidence_refs"] = []
        with pytest.raises(VerdictValidationError, match="evidence_refs"):
            verdict_validation.validate_verdict(bad)

    def test_bad_issued_at_rejected(self) -> None:
        bad = valid_verdict()
        bad["issued_at"] = "yesterday"
        with pytest.raises(VerdictValidationError, match="issued_at"):
            verdict_validation.validate_verdict(bad)

    def test_extra_property_rejected(self) -> None:
        bad = valid_verdict()
        bad["unexpected"] = True
        with pytest.raises(VerdictValidationError):
            verdict_validation.validate_verdict(bad)

    def test_satisfied_false_is_valid(self) -> None:
        v = valid_verdict()
        v["satisfied"] = False
        v["score"] = 0.3
        verdict_validation.validate_verdict(v)


class TestIsValidVerdict:
    def test_returns_true_for_valid(self) -> None:
        assert verdict_validation.is_valid_verdict(valid_verdict()) is True

    def test_returns_false_for_invalid(self) -> None:
        bad = valid_verdict()
        del bad["reasoning"]
        assert verdict_validation.is_valid_verdict(bad) is False
