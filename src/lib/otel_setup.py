"""OTEL exporter wiring for Langfuse phased rollout (T090)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

OtelPhase = Literal["phase1", "phase2"]


def build_otel_exporter_config(
    *,
    run_id: str,
    phase: OtelPhase,
    traces_dir: str,
    otlp_endpoint: str | None = None,
) -> dict[str, str]:
    """Build exporter configuration for Phase 1 file export or Phase 2 OTLP."""
    if phase == "phase1":
        file_path = str(Path(traces_dir) / f"{run_id}.otel.jsonl")
        return {
            "phase": phase,
            "exporter": "file",
            "endpoint": file_path,
        }

    if not otlp_endpoint:
        msg = "otlp_endpoint is required for phase2 exporter wiring"
        raise ValueError(msg)
    return {
        "phase": phase,
        "exporter": "otlp-http",
        "endpoint": otlp_endpoint,
    }
