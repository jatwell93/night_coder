"""US1 iteration loop controller."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoopOutcome:
    iterations: int
    satisfied: bool


def run_until_satisfied(
    *,
    max_iterations: int,
    satisfaction_probe: Callable[[int], bool],
) -> LoopOutcome:
    """Run probe from iteration 1..max until satisfied."""
    if max_iterations <= 0:
        msg = "max_iterations must be > 0"
        raise ValueError(msg)
    for i in range(1, max_iterations + 1):
        if satisfaction_probe(i):
            return LoopOutcome(iterations=i, satisfied=True)
    return LoopOutcome(iterations=max_iterations, satisfied=False)
