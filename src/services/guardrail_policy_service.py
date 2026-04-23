"""Guardrail policy loading and command matching (T018)."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path

import yaml

__all__ = [
    "GuardrailPolicy",
    "GuardrailPolicyError",
    "command_allowed_by_policy",
    "default_policy",
    "load_guardrail_policy",
]


class GuardrailPolicyError(ValueError):
    """Raised when a guardrail policy is malformed."""


@dataclass(frozen=True, slots=True)
class GuardrailPolicy:
    policy_id: str
    version: str
    mode: str
    applies_to_profile: str
    blocked_patterns: tuple[str, ...]
    allowed_patterns: tuple[str, ...]


def load_guardrail_policy(path: Path) -> GuardrailPolicy:
    """Load and validate a guardrail policy from YAML."""
    if not path.exists():
        msg = f"Guardrail policy file not found: {path}"
        raise GuardrailPolicyError(msg)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = "Guardrail policy must be a mapping/object"
        raise GuardrailPolicyError(msg)

    policy_id = _require_non_empty_str(raw, "policy_id")
    version = _require_non_empty_str(raw, "version")
    mode = _require_non_empty_str(raw, "mode")
    applies_to_profile = _require_non_empty_str(raw, "applies_to_profile")
    blocked_patterns = _require_pattern_list(raw, "blocked_patterns", must_be_non_empty=True)
    allowed_patterns = _require_pattern_list(raw, "allowed_patterns", must_be_non_empty=True)

    if mode != "block_allow_only":
        msg = f"Unsupported guardrail mode {mode!r}; expected 'block_allow_only'"
        raise GuardrailPolicyError(msg)
    if applies_to_profile not in {"offline", "online", "both"}:
        msg = (
            f"Invalid applies_to_profile {applies_to_profile!r}; "
            "expected one of ['both', 'offline', 'online']"
        )
        raise GuardrailPolicyError(msg)

    return GuardrailPolicy(
        policy_id=policy_id,
        version=version,
        mode=mode,
        applies_to_profile=applies_to_profile,
        blocked_patterns=blocked_patterns,
        allowed_patterns=allowed_patterns,
    )


def default_policy(*, profile: str = "both") -> GuardrailPolicy:
    """Return a conservative in-memory fallback policy.

    Used when policy file wiring has not landed on a host yet.
    """
    return GuardrailPolicy(
        policy_id="pilot-default",
        version="1",
        mode="block_allow_only",
        applies_to_profile=profile,
        blocked_patterns=(
            "rm -rf /*",
            "sudo *",
            "su *",
            "mkfs*",
            ":(){ :|:& };:",
            "* > /etc/*",
            "*chmod 777 /*",
        ),
        allowed_patterns=(
            "python*",
            "pytest*",
            "ruff*",
            "mypy*",
            "ls*",
            "cat*",
            "echo*",
            "git status*",
            "git diff*",
            "git log*",
        ),
    )


def command_allowed_by_policy(command: str, policy: GuardrailPolicy) -> bool:
    """Return True iff command passes block/allow checks."""
    lowered = command.strip().lower()
    if not lowered:
        return False
    if _matches_any(lowered, policy.blocked_patterns):
        return False
    return _matches_any(lowered, policy.allowed_patterns)


def _matches_any(command: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(command, pattern.lower()) for pattern in patterns)


def _require_non_empty_str(raw: dict[str, object], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        msg = f"Guardrail policy field {key!r} must be a non-empty string"
        raise GuardrailPolicyError(msg)
    return value


def _require_pattern_list(
    raw: dict[str, object],
    key: str,
    *,
    must_be_non_empty: bool,
) -> tuple[str, ...]:
    value = raw.get(key)
    if not isinstance(value, list):
        msg = f"Guardrail policy field {key!r} must be a list"
        raise GuardrailPolicyError(msg)
    if must_be_non_empty and not value:
        msg = f"Guardrail policy field {key!r} must not be empty"
        raise GuardrailPolicyError(msg)
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            msg = f"Guardrail policy field {key!r} must contain non-empty strings"
            raise GuardrailPolicyError(msg)
        out.append(item.strip())
    return tuple(out)
