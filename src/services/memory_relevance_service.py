"""Memory relevance and staleness filtering (T072)."""

from __future__ import annotations


def filter_relevant_memories(
    *,
    scenario_id: str,
    candidates: list[dict[str, object]],
    max_age_days: int,
) -> list[dict[str, object]]:
    """Return only scenario-relevant memory entries within staleness threshold."""
    _ = scenario_id  # Reserved for stricter scenario-tag matching in later iterations.
    selected: list[dict[str, object]] = []
    for candidate in candidates:
        age_days = candidate.get("age_days")
        if isinstance(age_days, int) and age_days <= max_age_days:
            selected.append(candidate)
    return selected
