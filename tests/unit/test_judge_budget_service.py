"""Unit tests for judge budget guard (T086)."""

from __future__ import annotations

import pytest

from services.judge_budget_service import JudgeBudgetExceededError, JudgeBudgetGuard


def test_guard_allows_calls_within_cap_and_tracks_spend() -> None:
    guard = JudgeBudgetGuard(judge_cap_usd=1.0)

    guard.assert_within_budget(estimated_cost_usd=0.25)
    guard.commit_spend(actual_cost_usd=0.20)

    assert guard.spent_usd == pytest.approx(0.20)
    assert guard.remaining_usd == pytest.approx(0.80)


def test_guard_rejects_call_when_estimate_exceeds_remaining_budget() -> None:
    guard = JudgeBudgetGuard(judge_cap_usd=0.50)
    guard.commit_spend(actual_cost_usd=0.40)

    with pytest.raises(JudgeBudgetExceededError, match="budget"):
        guard.assert_within_budget(estimated_cost_usd=0.15)
