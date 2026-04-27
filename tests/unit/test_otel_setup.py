"""Unit tests for OTEL exporter wiring (T090)."""

from __future__ import annotations

from lib.otel_setup import build_otel_exporter_config


def test_build_otel_exporter_config_for_phase1_file_export() -> None:
    config = build_otel_exporter_config(
        run_id="run-20260427T220000Z-abcd1234",
        phase="phase1",
        traces_dir="/tmp/night-coder/traces",
    )

    assert config["exporter"] == "file"
    assert config["endpoint"].endswith(".otel.jsonl")


def test_build_otel_exporter_config_for_phase2_langfuse_export() -> None:
    config = build_otel_exporter_config(
        run_id="run-20260427T220000Z-abcd1234",
        phase="phase2",
        traces_dir="/tmp/night-coder/traces",
        otlp_endpoint="http://langfuse.local:4318/v1/traces",
    )

    assert config["exporter"] == "otlp-http"
    assert config["endpoint"] == "http://langfuse.local:4318/v1/traces"
