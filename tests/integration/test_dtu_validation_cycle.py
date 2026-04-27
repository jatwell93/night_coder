"""T035 [US3] integration test for DTU-only validation execution."""

from __future__ import annotations

import pytest

from services.dtu_validation_service import execute_dtu_validation_cycle


@pytest.mark.integration
@pytest.mark.us3
def test_dtu_validation_cycle_executes_without_live_dependency_calls(tmp_path) -> None:
    result = execute_dtu_validation_cycle(
        scenario_id="SCN-PILOT-001-configurable-upstream-happy-path",
        dtu_profile_path=tmp_path / "wiremock-profile.json",
        allow_live_dependencies=False,
    )

    assert result.mode == "dtu-only"
    assert result.live_dependency_calls == 0
