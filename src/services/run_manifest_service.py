"""Run manifest builder and writer (T041)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from lib.artifact_paths import for_run
from lib.manifest_validation import validate_manifest
from lib.run_identity import to_iso8601, utc_now

ManifestStatus = Literal["completed", "failed", "aborted", "evaluation-pending"]


def build_and_write_run_manifest(
    *,
    artifacts_root: Path,
    run_id: str,
    git_sha: str,
    profile: str,
    scenario_ids: list[str],
    verdict_refs: list[str],
    artifact_refs: list[str],
    trace_refs: list[str],
    status: ManifestStatus,
    notes: str | None = None,
) -> Path:
    """Build schema-compliant run manifest and persist under run artifacts."""
    paths = for_run(artifacts_root, run_id)
    paths.ensure_run_tree()

    now = to_iso8601(utc_now())
    summary: dict[str, str] = {
        "status": status,
        "started_at": now,
        "ended_at": now,
    }
    if notes is not None:
        summary["notes"] = notes

    manifest = {
        "run_id": run_id,
        "git_sha": git_sha,
        "profile": profile,
        "scenario_ids": scenario_ids,
        "verdict_refs": verdict_refs,
        "artifact_refs": artifact_refs,
        "trace_refs": trace_refs,
        "summary": summary,
    }
    validate_manifest(manifest)
    paths.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return paths.manifest
