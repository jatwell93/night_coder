"""T051 [US1] integration test for satisfaction-based loop termination."""

from __future__ import annotations

import pytest

from services.orchestrator_loop_service import run_until_satisfied


@pytest.mark.integration
@pytest.mark.us1
def test_orchestrator_stops_when_scenario_satisfied() -> None:
    outcome = run_until_satisfied(
        max_iterations=10,
        satisfaction_probe=lambda i: i >= 3,
    )
    assert outcome.iterations == 3
    assert outcome.satisfied is True


@pytest.mark.integration
@pytest.mark.us1
def test_orchestrator_rejects_non_positive_iteration_cap() -> None:
    with pytest.raises(ValueError, match="max_iterations"):
        run_until_satisfied(
            max_iterations=0,
            satisfaction_probe=lambda _: False,
        )
