"""Unit tests for read-only scenario catalog loader (T071)."""

from __future__ import annotations

import os
import stat

import pytest

from services.scenario_catalog_service import load_scenario_catalog


def test_load_scenario_catalog_returns_id_to_markdown_mapping(tmp_path) -> None:
    scenario_file = tmp_path / "SCN-PILOT-001-upstream-ok.md"
    scenario_file.write_text(
        "# SCN-PILOT-001: Upstream dependency returns ok\n\n## Goal\nCheck status endpoint.\n",
        encoding="utf-8",
    )
    os.chmod(tmp_path, stat.S_IREAD | stat.S_IEXEC)

    loaded = load_scenario_catalog(catalog_path=tmp_path)

    assert "SCN-PILOT-001" in loaded
    assert "Upstream dependency returns ok" in loaded["SCN-PILOT-001"]


def test_load_scenario_catalog_rejects_writable_catalog(tmp_path) -> None:
    scenario_file = tmp_path / "SCN-PILOT-002-timeout.md"
    scenario_file.write_text("# SCN-PILOT-002: Timeout case\n", encoding="utf-8")
    os.chmod(tmp_path, stat.S_IRWXU)

    with pytest.raises(PermissionError, match="write bits"):
        load_scenario_catalog(catalog_path=tmp_path)
