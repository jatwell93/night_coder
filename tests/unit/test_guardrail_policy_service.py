"""Tests for guardrail policy loader (T018)."""

from __future__ import annotations

from pathlib import Path

import pytest

from services.guardrail_policy_service import (
    GuardrailPolicyError,
    command_allowed_by_policy,
    default_policy,
    load_guardrail_policy,
)


def test_default_policy_blocks_destructive_command() -> None:
    policy = default_policy()
    assert command_allowed_by_policy("rm -rf /tmp/x", policy) is False


def test_default_policy_allows_basic_python_command() -> None:
    policy = default_policy()
    assert command_allowed_by_policy("python -m pytest -q", policy) is True


def test_load_guardrail_policy_from_yaml(tmp_path: Path) -> None:
    policy_file = tmp_path / "guardrail-policy.yaml"
    policy_file.write_text(
        """
policy_id: us1
version: "1"
mode: block_allow_only
applies_to_profile: both
blocked_patterns:
  - "rm -rf *"
allowed_patterns:
  - "python*"
""".strip()
    )
    policy = load_guardrail_policy(policy_file)
    assert policy.policy_id == "us1"
    assert command_allowed_by_policy("python -m pytest -q", policy) is True


def test_load_guardrail_policy_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(GuardrailPolicyError, match="not found"):
        load_guardrail_policy(tmp_path / "missing.yaml")
