"""Model/provider role-policy adapter with fallback handling.

Every LLM call in the pilot maps a **role** (``coder``, ``judge``,
``memory-writer``, …) to a **(provider, model)** pair. The role-policy
adapter centralises that mapping and handles provider fallback when the
primary is known to be unavailable.

Policy shape::

    {
      "version": "1",
      "roles": {
        "<role>": [
          {"provider": "openrouter", "model": "anthropic/claude-sonnet-4"},
          {"provider": "anthropic",  "model": "claude-sonnet-4"},
          ...
        ]
      }
    }

The first entry in a role's candidate list is the **primary**; subsequent
entries are ordered fallbacks. Selection is deterministic: given the same
``unavailable_providers`` set, the same role always returns the same choice.

This service **does not call** any provider. It returns a :class:`ModelChoice`
describing which provider/model should be invoked; actual invocation happens
in downstream services which decide whether a failure justifies marking the
provider unavailable for subsequent calls in the same run.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

__all__ = [
    "ModelChoice",
    "ModelPolicy",
    "ModelPolicyError",
    "ModelPolicyService",
    "load_policy",
]


class ModelPolicyError(ValueError):
    """Raised for malformed policies and for roles with no available candidate."""


@dataclass(frozen=True, slots=True)
class ModelChoice:
    """A single provider/model selection plus a reason for traceability."""

    provider: str
    model: str
    reason: str


@dataclass(frozen=True, slots=True)
class _Candidate:
    provider: str
    model: str


@dataclass(frozen=True)
class ModelPolicy:
    """Validated role → candidate-list mapping.

    Construct via :func:`load_policy` — the constructor is only used by the
    loader and does not re-validate its inputs.
    """

    version: str
    roles: MappingProxyType[str, tuple[_Candidate, ...]]

    def candidates_for(self, role: str) -> tuple[_Candidate, ...]:
        try:
            return self.roles[role]
        except KeyError as exc:
            msg = f"unknown role {role!r}; known roles: {sorted(self.roles.keys())}"
            raise ModelPolicyError(msg) from exc


def load_policy(data: dict[str, Any]) -> ModelPolicy:
    """Validate and load a policy from a plain dict.

    Raises
    ------
    ModelPolicyError
        If required fields are missing or candidate entries are malformed.
    """
    if "version" not in data:
        msg = "policy is missing required field: version"
        raise ModelPolicyError(msg)

    raw_roles = data.get("roles")
    if not isinstance(raw_roles, dict) or not raw_roles:
        msg = "policy.roles must be a non-empty object mapping role name to candidate list"
        raise ModelPolicyError(msg)

    roles: dict[str, tuple[_Candidate, ...]] = {}
    for role_name, candidates in raw_roles.items():
        if not isinstance(candidates, list) or not candidates:
            msg = f"role {role_name!r} must have at least one candidate"
            raise ModelPolicyError(msg)
        roles[role_name] = tuple(_parse_candidate(c, role=role_name) for c in candidates)

    return ModelPolicy(
        version=str(data["version"]),
        roles=MappingProxyType(roles),
    )


def _parse_candidate(raw: Any, *, role: str) -> _Candidate:
    if not isinstance(raw, dict):
        msg = f"candidate under role {role!r} must be an object, got {type(raw).__name__}"
        raise ModelPolicyError(msg)
    provider = raw.get("provider")
    model = raw.get("model")
    if not isinstance(provider, str) or not provider:
        msg = f"candidate under role {role!r} is missing 'provider'"
        raise ModelPolicyError(msg)
    if not isinstance(model, str) or not model:
        msg = f"candidate under role {role!r} is missing 'model'"
        raise ModelPolicyError(msg)
    return _Candidate(provider=provider, model=model)


class ModelPolicyService:
    """Adapter that selects a provider/model for a role with fallback handling.

    ``unavailable_providers`` is an observable set — callers can add to it
    during a run (e.g. after a 503) and subsequent :meth:`choose_for_role`
    calls will honour the update without reconstructing the service.
    """

    def __init__(
        self,
        policy: ModelPolicy,
        unavailable_providers: Iterable[str] | None = None,
    ) -> None:
        self._policy = policy
        self._unavailable: set[str] = (
            unavailable_providers
            if isinstance(unavailable_providers, set)
            else set(unavailable_providers or ())
        )

    def choose_for_role(self, role: str) -> ModelChoice:
        """Return the first available candidate for ``role``.

        Raises
        ------
        ModelPolicyError
            If the role is unknown or every candidate's provider is
            currently in ``unavailable_providers``.
        """
        candidates = self._policy.candidates_for(role)
        skipped: list[str] = []
        for candidate in candidates:
            if candidate.provider in self._unavailable:
                skipped.append(candidate.provider)
                continue
            reason = "primary" if not skipped else "fallback:" + ",".join(skipped)
            return ModelChoice(
                provider=candidate.provider,
                model=candidate.model,
                reason=reason,
            )
        msg = (
            f"no available provider for role {role!r}; "
            f"all candidates marked unavailable: {sorted(self._unavailable)}"
        )
        raise ModelPolicyError(msg)
