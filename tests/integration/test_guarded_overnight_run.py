"""T016 [US1] integration test for guarded unattended run path."""

from __future__ import annotations

import pytest

from services.run_session_service import start_guarded_run


@pytest.mark.integration
@pytest.mark.us1
def test_guarded_run_blocks_prohibited_command_and_continues() -> None:
    result = start_guarded_run(
        run_id="run-20260423T130000Z-deadbeef",
        commands=[
            "python -m pytest -q",
            "rm -rf /home/deploy/night_coder",
            "python -m ruff check .",
        ],
    )

    assert result.blocked_count == 1
    assert result.allowed_count == 2
    assert result.status == "completed"
    assert result.run_id == "run-20260423T130000Z-deadbeef"
    assert result.blocked_events[0]["reason_code"] == "GRD.block.destructive-filesystem"


@pytest.mark.integration
@pytest.mark.us1
def test_guarded_run_offline_blocks_network_commands() -> None:
    result = start_guarded_run(
        run_id="run-20260423T130000Z-deadbeef",
        profile="offline",
        commands=["curl https://example.com", "python -m pytest -q"],
    )
    assert result.blocked_count == 1
    assert result.allowed_count == 1
    assert result.blocked_events[0]["reason_code"] == "GRD.block.network-egress"


@pytest.mark.integration
@pytest.mark.us1
def test_guarded_run_rejects_empty_command_list() -> None:
    with pytest.raises(ValueError, match="commands"):
        start_guarded_run(
            run_id="run-20260423T130000Z-deadbeef",
            commands=[],
        )
