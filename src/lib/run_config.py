"""Run configuration loader.

A :class:`RunConfig` bundles everything a single overnight run needs to know
before the orchestrator starts: where to write artifacts, where the scenario
catalog lives, which execution profile applies, budget caps, and the paths to
the guardrail and model policy files.

Three loaders are provided:

- :func:`from_dict` — typed loader used by tests and in-memory construction.
- :func:`from_file` — reads a JSON file from disk.
- :func:`from_env` — builds a config from ``NIGHT_CODER_*`` environment
  variables (the form Doppler injects on the VPS).

All three return an immutable :class:`RunConfig`. Validation errors raise
:class:`RunConfigError` with a message that names the offending field.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

__all__ = [
    "BudgetConfig",
    "PolicyRefs",
    "RunConfig",
    "RunConfigError",
    "from_dict",
    "from_env",
    "from_file",
]

Profile = Literal["offline", "online"]
_VALID_PROFILES: frozenset[str] = frozenset({"offline", "online"})

_DEFAULT_TOKEN_CAP = 250_000
_DEFAULT_COST_CAP_USD = 5.0
_DEFAULT_ITERATION_CAP = 40


class RunConfigError(ValueError):
    """Raised when run configuration inputs are missing or invalid."""


@dataclass(frozen=True, slots=True)
class BudgetConfig:
    """Per-run budget caps."""

    token_cap_per_run: int = _DEFAULT_TOKEN_CAP
    cost_cap_usd_per_run: float = _DEFAULT_COST_CAP_USD
    iteration_cap: int = _DEFAULT_ITERATION_CAP


@dataclass(frozen=True, slots=True)
class PolicyRefs:
    """Filesystem paths to policy files consumed by the run."""

    guardrail_policy: Path
    model_policy: Path


@dataclass(frozen=True, slots=True)
class RunConfig:
    """All configuration needed to start one overnight run."""

    artifacts_root: Path
    scenario_catalog_path: Path
    profile: Profile
    policy_refs: PolicyRefs
    budget: BudgetConfig = field(default_factory=BudgetConfig)


def from_dict(data: dict[str, Any]) -> RunConfig:
    """Build a :class:`RunConfig` from a plain dict (validated)."""
    artifacts_root = _require_path(data, "artifacts_root")
    scenario_catalog_path = _require_path(data, "scenario_catalog_path")
    profile = _require_profile(data)
    policy_refs = _require_policy_refs(data)
    budget = _parse_budget(data.get("budget"))
    return RunConfig(
        artifacts_root=artifacts_root,
        scenario_catalog_path=scenario_catalog_path,
        profile=profile,
        policy_refs=policy_refs,
        budget=budget,
    )


def from_file(path: Path) -> RunConfig:
    """Load a :class:`RunConfig` from a JSON file on disk."""
    if not path.exists():
        msg = f"Run config file not found: {path}"
        raise RunConfigError(msg)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"Run config file {path} is not valid JSON: {exc.msg}"
        raise RunConfigError(msg) from exc
    if not isinstance(data, dict):
        msg = f"Run config file {path} must contain a JSON object at the top level"
        raise RunConfigError(msg)
    return from_dict(data)


def from_env() -> RunConfig:
    """Load a :class:`RunConfig` from ``NIGHT_CODER_*`` environment variables.

    Required variables:

    - ``NIGHT_CODER_ARTIFACTS_ROOT``
    - ``NIGHT_CODER_SCENARIO_CATALOG``
    - ``NIGHT_CODER_PROFILE``
    - ``NIGHT_CODER_GUARDRAIL_POLICY``
    - ``NIGHT_CODER_MODEL_POLICY``

    Optional budget overrides:

    - ``NIGHT_CODER_TOKEN_CAP``
    - ``NIGHT_CODER_COST_CAP_USD``
    - ``NIGHT_CODER_ITERATION_CAP``
    """
    data: dict[str, Any] = {
        "artifacts_root": _require_env("NIGHT_CODER_ARTIFACTS_ROOT"),
        "scenario_catalog_path": _require_env("NIGHT_CODER_SCENARIO_CATALOG"),
        "profile": _require_env("NIGHT_CODER_PROFILE"),
        "policy_refs": {
            "guardrail_policy": _require_env("NIGHT_CODER_GUARDRAIL_POLICY"),
            "model_policy": _require_env("NIGHT_CODER_MODEL_POLICY"),
        },
    }
    budget_overrides: dict[str, Any] = {}
    if (raw := os.environ.get("NIGHT_CODER_TOKEN_CAP")) is not None:
        budget_overrides["token_cap_per_run"] = _parse_int(raw, field="NIGHT_CODER_TOKEN_CAP")
    if (raw := os.environ.get("NIGHT_CODER_COST_CAP_USD")) is not None:
        budget_overrides["cost_cap_usd_per_run"] = _parse_float(
            raw, field="NIGHT_CODER_COST_CAP_USD"
        )
    if (raw := os.environ.get("NIGHT_CODER_ITERATION_CAP")) is not None:
        budget_overrides["iteration_cap"] = _parse_int(raw, field="NIGHT_CODER_ITERATION_CAP")
    if budget_overrides:
        data["budget"] = budget_overrides
    return from_dict(data)


def _require_path(data: dict[str, Any], field_name: str) -> Path:
    if field_name not in data:
        msg = f"run config is missing required field: {field_name}"
        raise RunConfigError(msg)
    value = data[field_name]
    if not isinstance(value, (str, Path)) or not str(value):
        msg = f"run config field {field_name!r} must be a non-empty path"
        raise RunConfigError(msg)
    return Path(value)


def _require_profile(data: dict[str, Any]) -> Profile:
    if "profile" not in data:
        msg = "run config is missing required field: profile"
        raise RunConfigError(msg)
    value = data["profile"]
    if value not in _VALID_PROFILES:
        msg = f"run config profile must be one of {sorted(_VALID_PROFILES)}; got {value!r}"
        raise RunConfigError(msg)
    # mypy narrows ``value`` to ``str`` via the ``in`` check above, but the
    # Literal return type still requires an assertion to convince it.
    assert value in _VALID_PROFILES
    return value


def _require_policy_refs(data: dict[str, Any]) -> PolicyRefs:
    raw = data.get("policy_refs")
    if not isinstance(raw, dict):
        msg = "run config field 'policy_refs' must be an object"
        raise RunConfigError(msg)
    return PolicyRefs(
        guardrail_policy=_require_path(raw, "guardrail_policy"),
        model_policy=_require_path(raw, "model_policy"),
    )


def _parse_budget(raw: Any) -> BudgetConfig:
    if raw is None:
        return BudgetConfig()
    if not isinstance(raw, dict):
        msg = "run config field 'budget' must be an object"
        raise RunConfigError(msg)

    token_cap = raw.get("token_cap_per_run", _DEFAULT_TOKEN_CAP)
    cost_cap = raw.get("cost_cap_usd_per_run", _DEFAULT_COST_CAP_USD)
    iteration_cap = raw.get("iteration_cap", _DEFAULT_ITERATION_CAP)

    if not isinstance(token_cap, int) or token_cap <= 0:
        msg = f"budget.token_cap_per_run must be a positive integer; got {token_cap!r}"
        raise RunConfigError(msg)
    if not isinstance(cost_cap, (int, float)) or cost_cap <= 0:
        msg = f"budget.cost_cap_usd_per_run must be a positive number; got {cost_cap!r}"
        raise RunConfigError(msg)
    if not isinstance(iteration_cap, int) or iteration_cap <= 0:
        msg = f"budget.iteration_cap must be a positive integer; got {iteration_cap!r}"
        raise RunConfigError(msg)

    return BudgetConfig(
        token_cap_per_run=token_cap,
        cost_cap_usd_per_run=float(cost_cap),
        iteration_cap=iteration_cap,
    )


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not value.strip():
        msg = f"Required environment variable {name} is not set"
        raise RunConfigError(msg)
    return value


def _parse_int(raw: str, *, field: str) -> int:
    try:
        return int(raw)
    except ValueError as exc:
        msg = f"{field} must be an integer; got {raw!r}"
        raise RunConfigError(msg) from exc


def _parse_float(raw: str, *, field: str) -> float:
    try:
        return float(raw)
    except ValueError as exc:
        msg = f"{field} must be a number; got {raw!r}"
        raise RunConfigError(msg) from exc
