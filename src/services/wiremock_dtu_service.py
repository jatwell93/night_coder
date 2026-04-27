"""WireMock DTU mapping loader and lifecycle validation (T088)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_wiremock_mappings(*, mappings_dir: Path) -> list[dict[str, Any]]:
    """Load all WireMock mapping JSON files from directory."""
    mappings: list[dict[str, Any]] = []
    for mapping_file in sorted(mappings_dir.glob("*.json")):
        payload = json.loads(mapping_file.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            msg = f"WireMock mapping {mapping_file} must be a JSON object"
            raise ValueError(msg)
        mappings.append(payload)
    return mappings


def validate_wiremock_mappings(mappings: list[dict[str, Any]]) -> None:
    """Validate required top-level WireMock mapping keys."""
    for index, mapping in enumerate(mappings):
        if "request" not in mapping or "response" not in mapping:
            msg = f"WireMock mapping at index {index} must contain request and response blocks"
            raise ValueError(msg)
