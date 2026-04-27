"""End-of-run workflow linking telemetry, memory, and manifest (T042)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from services.memory_relevance_service import filter_relevant_memories
from services.run_manifest_service import build_and_write_run_manifest


@dataclass(frozen=True, slots=True)
class RunFinalizeResult:
    """Summary outputs of run finalization."""

    manifest_path: Path
    telemetry_bundle: dict[str, Any]
    selected_memories: list[dict[str, object]]


def finalize_run(
    *,
    artifacts_root: Path,
    run_id: str,
    git_sha: str,
    profile: str,
    scenario_ids: list[str],
    verdict_refs: list[str],
    telemetry_events: list[dict[str, Any]],
    memory_candidates: list[dict[str, object]],
) -> RunFinalizeResult:
    """Finalize run by selecting memory, bundling telemetry, and writing manifest."""
    selected = filter_relevant_memories(
        scenario_id=scenario_ids[0] if scenario_ids else "SCN-UNKNOWN",
        candidates=memory_candidates,
        max_age_days=14,
    )
    telemetry_bundle = {
        "run_id": run_id,
        "partial": False,
        "events": telemetry_events,
    }
    artifact_refs = [f"runs/{run_id}/artifacts/finalize.json"]
    trace_refs = [f"runs/{run_id}/traces/events.jsonl"]
    manifest_path = build_and_write_run_manifest(
        artifacts_root=artifacts_root,
        run_id=run_id,
        git_sha=git_sha,
        profile=profile,
        scenario_ids=scenario_ids,
        verdict_refs=verdict_refs,
        artifact_refs=artifact_refs,
        trace_refs=trace_refs,
        status="completed",
        notes="Finalized with telemetry and memory linkage.",
    )
    return RunFinalizeResult(
        manifest_path=manifest_path,
        telemetry_bundle=telemetry_bundle,
        selected_memories=selected,
    )
