"""Blocked-command interception adapter (T019)."""

from __future__ import annotations

from dataclasses import dataclass

from services.guardrail_policy_service import GuardrailPolicy, command_allowed_by_policy
from services.run_profile_service import profile_allows_command

__all__ = ["EnforcementDecision", "evaluate_command"]


@dataclass(frozen=True, slots=True)
class EnforcementDecision:
    allowed: bool
    reason_code: str
    detail: str


def evaluate_command(
    *,
    command: str,
    profile: str,
    policy: GuardrailPolicy,
) -> EnforcementDecision:
    """Evaluate a command against profile + guardrail policy."""
    if not command.strip():
        return EnforcementDecision(
            allowed=False,
            reason_code="GRD.block.unknown-binary",
            detail="empty command",
        )

    lowered = command.lower()
    if any(token in lowered for token in ("sudo ", " su ", " su\n", "pkexec ")):
        return EnforcementDecision(
            allowed=False,
            reason_code="GRD.block.privileged-escalation",
            detail="privileged escalation command denied",
        )

    if not profile_allows_command(profile, command):
        return EnforcementDecision(
            allowed=False,
            reason_code="GRD.block.network-egress",
            detail=f"profile {profile!r} disallows network command",
        )

    if not command_allowed_by_policy(command, policy):
        reason = (
            "GRD.block.destructive-filesystem"
            if any(token in lowered for token in ("rm -rf", "mkfs", "chmod 777 /"))
            else "GRD.block.unknown-binary"
        )
        return EnforcementDecision(
            allowed=False,
            reason_code=reason,
            detail="policy denied command",
        )

    return EnforcementDecision(
        allowed=True,
        reason_code="GRD.allow.permitted",
        detail="command passed profile and policy checks",
    )
