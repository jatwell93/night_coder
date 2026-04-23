"""US1 run session guardrail flow."""

from __future__ import annotations

from dataclasses import dataclass

from services.guardrail_audit_service import build_blocked_action_event
from services.guardrail_enforcement_service import evaluate_command
from services.guardrail_policy_service import GuardrailPolicy, default_policy


@dataclass(frozen=True, slots=True)
class GuardedRunResult:
    run_id: str
    transitions: tuple[str, ...]
    blocked_count: int
    allowed_count: int
    status: str
    blocked_events: list[dict[str, str]]


def start_guarded_run(
    *,
    run_id: str,
    commands: list[str],
    profile: str = "offline",
    policy: GuardrailPolicy | None = None,
) -> GuardedRunResult:
    """Evaluate commands against guardrails and profile checks."""
    if not commands:
        msg = "commands must contain at least one command"
        raise ValueError(msg)
    effective_policy = policy if policy is not None else default_policy(profile="both")
    blocked = 0
    allowed = 0
    blocked_events: list[dict[str, str]] = []
    for command in commands:
        decision = evaluate_command(
            command=command,
            profile=profile,
            policy=effective_policy,
        )
        if not decision.allowed:
            blocked += 1
            blocked_events.append(
                build_blocked_action_event(
                    run_id=run_id,
                    attempted_action=command,
                    reason_code=decision.reason_code,
                )
            )
        else:
            allowed += 1
    status = "failed" if blocked == len(commands) else "completed"
    return GuardedRunResult(
        run_id=run_id,
        transitions=("queued", "running", status),
        blocked_count=blocked,
        allowed_count=allowed,
        status=status,
        blocked_events=blocked_events,
    )
