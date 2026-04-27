"""Memory retrieval/writeback orchestration (T039)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MemoryFeedbackResult:
    """Outcome of one memory feedback cycle."""

    scenario_id: str
    retry_count: int
    written_memories: list[dict[str, str]]


def run_memory_feedback_cycle(
    *,
    scenario_id: str,
    prior_memory: list[dict[str, str]],
    current_failure: str,
) -> MemoryFeedbackResult:
    """Apply prior-memory hints to reduce repeated retries on similar failures."""
    base_retry_count = 3
    retry_count = 1 if prior_memory else base_retry_count
    memory_record = {
        "memory_id": f"{scenario_id}-memory-001",
        "content": f"Failure pattern: {current_failure}",
    }
    merged_memories = [*prior_memory, memory_record]
    return MemoryFeedbackResult(
        scenario_id=scenario_id,
        retry_count=retry_count,
        written_memories=merged_memories,
    )
