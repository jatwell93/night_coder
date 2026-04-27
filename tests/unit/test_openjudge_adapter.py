"""Unit tests for OpenJudge adapter normalization (T084)."""

from __future__ import annotations

import pytest

from services.openjudge_adapter import OpenJudgeNormalizationError, normalize_openjudge_verdict


def test_normalize_openjudge_verdict_supports_reason_alias() -> None:
    raw = {
        "satisfied": True,
        "score": 0.91,
        "reason": "All expected outcomes were satisfied.",
    }

    verdict = normalize_openjudge_verdict(raw)

    assert verdict.satisfied is True
    assert verdict.score == pytest.approx(0.91)
    assert verdict.reasoning == "All expected outcomes were satisfied."


def test_normalize_openjudge_verdict_rejects_out_of_range_score() -> None:
    raw = {
        "satisfied": False,
        "score": 1.2,
        "reasoning": "Bad output.",
    }

    with pytest.raises(OpenJudgeNormalizationError, match="score"):
        normalize_openjudge_verdict(raw)
