"""T036 [US3] integration test for memory feedback loop improvement."""

from __future__ import annotations

import pytest

from services.memory_feedback_service import run_memory_feedback_cycle


@pytest.mark.integration
@pytest.mark.us3
def test_memory_retrieval_reduces_repeated_failures() -> None:
    first = run_memory_feedback_cycle(
        scenario_id="SCN-PILOT-002-timeout-retry-exhaustion",
        prior_memory=[],
        current_failure="timeout-retry-exhausted",
    )
    second = run_memory_feedback_cycle(
        scenario_id="SCN-PILOT-002-timeout-retry-exhaustion",
        prior_memory=first.written_memories,
        current_failure="timeout-retry-exhausted",
    )

    assert second.retry_count < first.retry_count
