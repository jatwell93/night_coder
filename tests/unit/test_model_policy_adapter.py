"""Tests for src/services/model_policy_service.py — T049."""

from __future__ import annotations

from typing import Any

import pytest

from services import model_policy_service
from services.model_policy_service import (
    ModelChoice,
    ModelPolicy,
    ModelPolicyError,
    ModelPolicyService,
)


def valid_policy_dict() -> dict[str, Any]:
    return {
        "version": "1",
        "roles": {
            "coder": [
                {"provider": "openrouter", "model": "anthropic/claude-sonnet-4"},
                {"provider": "anthropic", "model": "claude-sonnet-4"},
                {"provider": "openai", "model": "gpt-4o"},
            ],
            "judge": [
                {"provider": "openrouter", "model": "openai/gpt-4o"},
                {"provider": "openai", "model": "gpt-4o"},
            ],
            "memory-writer": [
                {"provider": "openrouter", "model": "meta-llama/llama-3.1-70b-instruct"},
            ],
        },
    }


class TestLoadPolicy:
    def test_valid_policy_loads(self) -> None:
        policy = model_policy_service.load_policy(valid_policy_dict())
        assert isinstance(policy, ModelPolicy)
        assert policy.version == "1"
        assert set(policy.roles.keys()) == {"coder", "judge", "memory-writer"}

    def test_empty_roles_rejected(self) -> None:
        bad = {"version": "1", "roles": {}}
        with pytest.raises(ModelPolicyError, match="roles"):
            model_policy_service.load_policy(bad)

    def test_role_without_candidates_rejected(self) -> None:
        bad = valid_policy_dict()
        bad["roles"]["coder"] = []
        with pytest.raises(ModelPolicyError, match="coder"):
            model_policy_service.load_policy(bad)

    def test_missing_provider_rejected(self) -> None:
        bad = valid_policy_dict()
        bad["roles"]["coder"][0] = {"model": "no-provider"}
        with pytest.raises(ModelPolicyError):
            model_policy_service.load_policy(bad)

    def test_missing_version_rejected(self) -> None:
        bad = valid_policy_dict()
        del bad["version"]
        with pytest.raises(ModelPolicyError, match="version"):
            model_policy_service.load_policy(bad)


class TestChooseForRolePrimary:
    def test_returns_primary_when_all_available(self) -> None:
        svc = ModelPolicyService(policy=model_policy_service.load_policy(valid_policy_dict()))
        choice = svc.choose_for_role("coder")
        assert choice.provider == "openrouter"
        assert choice.model == "anthropic/claude-sonnet-4"
        assert choice.reason == "primary"

    def test_unknown_role_raises(self) -> None:
        svc = ModelPolicyService(policy=model_policy_service.load_policy(valid_policy_dict()))
        with pytest.raises(ModelPolicyError, match="unknown role"):
            svc.choose_for_role("does-not-exist")


class TestChooseForRoleFallback:
    def test_falls_back_when_primary_unavailable(self) -> None:
        svc = ModelPolicyService(
            policy=model_policy_service.load_policy(valid_policy_dict()),
            unavailable_providers={"openrouter"},
        )
        choice = svc.choose_for_role("coder")
        assert choice.provider == "anthropic"
        assert choice.reason.startswith("fallback:")
        assert "openrouter" in choice.reason

    def test_skips_multiple_unavailable_providers(self) -> None:
        svc = ModelPolicyService(
            policy=model_policy_service.load_policy(valid_policy_dict()),
            unavailable_providers={"openrouter", "anthropic"},
        )
        choice = svc.choose_for_role("coder")
        assert choice.provider == "openai"

    def test_raises_when_no_candidates_available(self) -> None:
        svc = ModelPolicyService(
            policy=model_policy_service.load_policy(valid_policy_dict()),
            unavailable_providers={"openrouter"},
        )
        with pytest.raises(ModelPolicyError, match="no available provider"):
            svc.choose_for_role("memory-writer")

    def test_unavailable_set_can_change_between_calls(self) -> None:
        unavailable: set[str] = set()
        svc = ModelPolicyService(
            policy=model_policy_service.load_policy(valid_policy_dict()),
            unavailable_providers=unavailable,
        )
        assert svc.choose_for_role("coder").provider == "openrouter"
        unavailable.add("openrouter")
        assert svc.choose_for_role("coder").provider == "anthropic"


class TestModelChoice:
    def test_is_immutable(self) -> None:
        choice = ModelChoice(provider="x", model="y", reason="primary")
        with pytest.raises((AttributeError, Exception)):
            choice.provider = "mutated"  # type: ignore[misc]
