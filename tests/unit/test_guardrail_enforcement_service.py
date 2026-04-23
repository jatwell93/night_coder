"""Tests for blocked-command interception adapter (T019)."""

from __future__ import annotations

from services.guardrail_enforcement_service import evaluate_command
from services.guardrail_policy_service import default_policy


def test_enforcement_blocks_network_in_offline_profile() -> None:
    decision = evaluate_command(
        command="curl https://example.com",
        profile="offline",
        policy=default_policy(),
    )
    assert decision.allowed is False
    assert decision.reason_code == "GRD.block.network-egress"


def test_enforcement_blocks_privileged_escalation() -> None:
    decision = evaluate_command(
        command="sudo rm -rf /tmp/x",
        profile="online",
        policy=default_policy(),
    )
    assert decision.allowed is False
    assert decision.reason_code == "GRD.block.privileged-escalation"


def test_enforcement_allows_expected_command() -> None:
    decision = evaluate_command(
        command="python -m pytest -q",
        profile="offline",
        policy=default_policy(),
    )
    assert decision.allowed is True
    assert decision.reason_code == "GRD.allow.permitted"
