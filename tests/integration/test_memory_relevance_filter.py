"""T069 [US3] integration test for stale-memory relevance filtering."""

from __future__ import annotations

import pytest

from services.memory_relevance_service import filter_relevant_memories


@pytest.mark.integration
@pytest.mark.us3
def test_stale_memory_entries_are_filtered_before_reuse() -> None:
    selected = filter_relevant_memories(
        scenario_id="SCN-PILOT-003-malformed-json-handling",
        candidates=[
            {"memory_id": "old-1", "age_days": 45, "tags": ["json"]},
            {"memory_id": "fresh-1", "age_days": 2, "tags": ["json", "pilot"]},
        ],
        max_age_days=14,
    )

    assert [item["memory_id"] for item in selected] == ["fresh-1"]
