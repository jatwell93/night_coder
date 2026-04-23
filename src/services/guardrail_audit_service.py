"""US1 blocked-action audit event helpers."""

from __future__ import annotations

from typing import Any

from lib.event_envelope import EventType, Severity, new_envelope


def build_blocked_action_event(
    *,
    run_id: str,
    attempted_action: str,
    reason_code: str,
) -> dict[str, Any]:
    """Build a contract-shaped blocked-action event payload."""
    if not attempted_action.strip():
        msg = "attempted_action must be non-empty"
        raise ValueError(msg)
    if not reason_code.startswith("GRD."):
        msg = f"reason_code must start with 'GRD.' for guardrail events, got {reason_code!r}"
        raise ValueError(msg)
    env = new_envelope(
        run_id=run_id,
        event_type=EventType.GUARDRAIL,
        severity=Severity.ERROR,
        reason_code=reason_code,
    )
    out = env.to_dict()
    out["attempted_action"] = attempted_action
    out["policy_domain"] = "guardrail"
    return out
