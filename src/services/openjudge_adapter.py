"""OpenJudge adapter with structured verdict normalization (T084)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class OpenJudgeNormalizationError(ValueError):
    """Raised when an OpenJudge verdict payload is missing required fields."""


@dataclass(frozen=True, slots=True)
class NormalizedJudgeVerdict:
    """Normalized verdict shape used by local judge services."""

    satisfied: bool
    score: float
    reasoning: str


def normalize_openjudge_verdict(raw_verdict: dict[str, Any]) -> NormalizedJudgeVerdict:
    """Normalize OpenJudge verdict payload into canonical local fields."""
    satisfied = raw_verdict.get("satisfied")
    if not isinstance(satisfied, bool):
        msg = "OpenJudge verdict must contain boolean field 'satisfied'"
        raise OpenJudgeNormalizationError(msg)

    raw_score = raw_verdict.get("score")
    if not isinstance(raw_score, (int, float)):
        msg = "OpenJudge verdict must contain numeric field 'score'"
        raise OpenJudgeNormalizationError(msg)
    score = float(raw_score)
    if score < 0.0 or score > 1.0:
        msg = f"OpenJudge verdict score must be within [0, 1], got {score!r}"
        raise OpenJudgeNormalizationError(msg)

    reasoning_raw = raw_verdict.get("reasoning", raw_verdict.get("reason"))
    if not isinstance(reasoning_raw, str) or not reasoning_raw.strip():
        msg = "OpenJudge verdict must contain non-empty field 'reasoning' (or alias 'reason')"
        raise OpenJudgeNormalizationError(msg)

    return NormalizedJudgeVerdict(
        satisfied=satisfied,
        score=score,
        reasoning=reasoning_raw.strip(),
    )
