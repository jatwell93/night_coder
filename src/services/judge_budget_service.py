"""LLM budget/cost guard for judge calls (T086)."""

from __future__ import annotations

from dataclasses import dataclass


class JudgeBudgetExceededError(RuntimeError):
    """Raised when a judge call would exceed the approved budget cap."""


@dataclass(slots=True)
class JudgeBudgetGuard:
    """Tracks judge-call spend and prevents cap breaches."""

    judge_cap_usd: float
    spent_usd: float = 0.0

    def __post_init__(self) -> None:
        if self.judge_cap_usd <= 0:
            msg = f"judge_cap_usd must be > 0, got {self.judge_cap_usd!r}"
            raise ValueError(msg)
        if self.spent_usd < 0:
            msg = f"spent_usd must be >= 0, got {self.spent_usd!r}"
            raise ValueError(msg)

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.judge_cap_usd - self.spent_usd)

    def assert_within_budget(self, *, estimated_cost_usd: float) -> None:
        if estimated_cost_usd <= 0:
            msg = f"estimated_cost_usd must be > 0, got {estimated_cost_usd!r}"
            raise ValueError(msg)
        if estimated_cost_usd > self.remaining_usd:
            msg = (
                "Judge budget exceeded: estimated call cost "
                f"${estimated_cost_usd:.4f} > remaining ${self.remaining_usd:.4f}"
            )
            raise JudgeBudgetExceededError(msg)

    def commit_spend(self, *, actual_cost_usd: float) -> None:
        if actual_cost_usd < 0:
            msg = f"actual_cost_usd must be >= 0, got {actual_cost_usd!r}"
            raise ValueError(msg)
        self.spent_usd += actual_cost_usd
