"""T015 [US1] contract tests for blocked-action event payload."""

from __future__ import annotations

import pytest

from services.guardrail_audit_service import build_blocked_action_event


@pytest.mark.contract
@pytest.mark.us1
def test_blocked_action_event_contract_shape() -> None:
    event = build_blocked_action_event(
        run_id="run-20260423T130000Z-deadbeef",
        attempted_action="rm -rf /tmp/demo",
        reason_code="GRD.block.destructive-filesystem",
    )

    assert event["event_type"] == "guardrail"
    assert event["severity"] in {"warn", "error"}
    assert event["run_id"].startswith("run-")
    assert event["reason_code"].startswith("GRD.")
    assert event["attempted_action"]
    assert event["policy_domain"] == "guardrail"


@pytest.mark.contract
@pytest.mark.us1
def test_blocked_action_event_rejects_non_guardrail_reason() -> None:
    with pytest.raises(ValueError, match="GRD"):
        build_blocked_action_event(
            run_id="run-20260423T130000Z-deadbeef",
            attempted_action="rm -rf /tmp/demo",
            reason_code="RUN.end.failed",
        )
