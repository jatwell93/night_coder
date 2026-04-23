"""Tests for src/lib/run_config.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lib import run_config
from lib.run_config import RunConfig, RunConfigError


def valid_data(tmp_path: Path) -> dict[str, object]:
    return {
        "artifacts_root": str(tmp_path / "artifacts"),
        "scenario_catalog_path": str(tmp_path / "scenarios"),
        "profile": "offline",
        "budget": {
            "token_cap_per_run": 250_000,
            "cost_cap_usd_per_run": 5.0,
            "iteration_cap": 40,
        },
        "policy_refs": {
            "guardrail_policy": str(tmp_path / "policies" / "guardrail.yaml"),
            "model_policy": str(tmp_path / "policies" / "model.yaml"),
        },
    }


class TestFromDict:
    def test_valid_data_loads(self, tmp_path: Path) -> None:
        config = run_config.from_dict(valid_data(tmp_path))
        assert isinstance(config, RunConfig)
        assert config.profile == "offline"
        assert config.budget.token_cap_per_run == 250_000
        assert config.budget.iteration_cap == 40

    def test_paths_are_path_objects(self, tmp_path: Path) -> None:
        config = run_config.from_dict(valid_data(tmp_path))
        assert isinstance(config.artifacts_root, Path)
        assert isinstance(config.scenario_catalog_path, Path)
        assert isinstance(config.policy_refs.guardrail_policy, Path)

    def test_invalid_profile_rejected(self, tmp_path: Path) -> None:
        bad = valid_data(tmp_path)
        bad["profile"] = "staging"
        with pytest.raises(RunConfigError, match="profile"):
            run_config.from_dict(bad)

    def test_missing_artifacts_root_rejected(self, tmp_path: Path) -> None:
        bad = valid_data(tmp_path)
        del bad["artifacts_root"]
        with pytest.raises(RunConfigError, match="artifacts_root"):
            run_config.from_dict(bad)

    def test_negative_token_cap_rejected(self, tmp_path: Path) -> None:
        bad = valid_data(tmp_path)
        bad["budget"]["token_cap_per_run"] = -1  # type: ignore[index]
        with pytest.raises(RunConfigError, match="token_cap"):
            run_config.from_dict(bad)

    def test_zero_iteration_cap_rejected(self, tmp_path: Path) -> None:
        bad = valid_data(tmp_path)
        bad["budget"]["iteration_cap"] = 0  # type: ignore[index]
        with pytest.raises(RunConfigError, match="iteration_cap"):
            run_config.from_dict(bad)

    def test_budget_defaults_applied_when_missing(self, tmp_path: Path) -> None:
        data = valid_data(tmp_path)
        del data["budget"]
        config = run_config.from_dict(data)
        assert config.budget.token_cap_per_run > 0
        assert config.budget.cost_cap_usd_per_run > 0
        assert config.budget.iteration_cap > 0

    def test_online_profile_accepted(self, tmp_path: Path) -> None:
        data = valid_data(tmp_path)
        data["profile"] = "online"
        assert run_config.from_dict(data).profile == "online"


class TestFromFile:
    def test_loads_json_file(self, tmp_path: Path) -> None:
        cfg_path = tmp_path / "run.json"
        cfg_path.write_text(json.dumps(valid_data(tmp_path)))
        config = run_config.from_file(cfg_path)
        assert config.profile == "offline"

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(RunConfigError, match="not found"):
            run_config.from_file(tmp_path / "nope.json")

    def test_non_json_file_raises(self, tmp_path: Path) -> None:
        bad = tmp_path / "run.json"
        bad.write_text("not json {{{")
        with pytest.raises(RunConfigError, match="JSON"):
            run_config.from_file(bad)


class TestFromEnv:
    def test_basic_env_vars_load(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("NIGHT_CODER_ARTIFACTS_ROOT", str(tmp_path / "artifacts"))
        monkeypatch.setenv("NIGHT_CODER_SCENARIO_CATALOG", str(tmp_path / "scenarios"))
        monkeypatch.setenv("NIGHT_CODER_PROFILE", "online")
        monkeypatch.setenv(
            "NIGHT_CODER_GUARDRAIL_POLICY",
            str(tmp_path / "guardrail.yaml"),
        )
        monkeypatch.setenv("NIGHT_CODER_MODEL_POLICY", str(tmp_path / "model.yaml"))
        config = run_config.from_env()
        assert config.profile == "online"
        assert config.artifacts_root == tmp_path / "artifacts"

    def test_missing_required_env_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for key in (
            "NIGHT_CODER_ARTIFACTS_ROOT",
            "NIGHT_CODER_SCENARIO_CATALOG",
            "NIGHT_CODER_PROFILE",
            "NIGHT_CODER_GUARDRAIL_POLICY",
            "NIGHT_CODER_MODEL_POLICY",
        ):
            monkeypatch.delenv(key, raising=False)
        with pytest.raises(RunConfigError, match="NIGHT_CODER_ARTIFACTS_ROOT"):
            run_config.from_env()

    def test_budget_env_overrides(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("NIGHT_CODER_ARTIFACTS_ROOT", str(tmp_path / "artifacts"))
        monkeypatch.setenv("NIGHT_CODER_SCENARIO_CATALOG", str(tmp_path / "scenarios"))
        monkeypatch.setenv("NIGHT_CODER_PROFILE", "offline")
        monkeypatch.setenv(
            "NIGHT_CODER_GUARDRAIL_POLICY",
            str(tmp_path / "guardrail.yaml"),
        )
        monkeypatch.setenv("NIGHT_CODER_MODEL_POLICY", str(tmp_path / "model.yaml"))
        monkeypatch.setenv("NIGHT_CODER_TOKEN_CAP", "100000")
        monkeypatch.setenv("NIGHT_CODER_COST_CAP_USD", "2.5")
        monkeypatch.setenv("NIGHT_CODER_ITERATION_CAP", "20")
        config = run_config.from_env()
        assert config.budget.token_cap_per_run == 100_000
        assert config.budget.cost_cap_usd_per_run == 2.5
        assert config.budget.iteration_cap == 20


class TestImmutable:
    def test_run_config_is_frozen(self, tmp_path: Path) -> None:
        config = run_config.from_dict(valid_data(tmp_path))
        with pytest.raises((AttributeError, Exception)):
            config.profile = "online"  # type: ignore[misc]
