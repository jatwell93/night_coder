"""Unit tests for WireMock DTU loader/lifecycle control (T088)."""

from __future__ import annotations

import json

from services.wiremock_dtu_service import (
    load_wiremock_mappings,
    validate_wiremock_mappings,
)


def test_load_wiremock_mappings_reads_json_mapping_files(tmp_path) -> None:
    mapping = {
        "request": {"method": "GET", "url": "/api/status"},
        "response": {"status": 200, "jsonBody": {"status": "ok"}},
    }
    mapping_path = tmp_path / "pilot-status.json"
    mapping_path.write_text(json.dumps(mapping), encoding="utf-8")

    loaded = load_wiremock_mappings(mappings_dir=tmp_path)

    assert loaded[0]["request"]["url"] == "/api/status"


def test_validate_wiremock_mappings_requires_request_and_response() -> None:
    valid = [{"request": {"method": "GET", "url": "/ok"}, "response": {"status": 200}}]
    validate_wiremock_mappings(valid)
