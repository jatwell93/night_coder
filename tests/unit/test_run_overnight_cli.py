"""Tests for unattended run launcher workflow (T020)."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from cli.run_overnight import run_launcher
from lib.run_config import BudgetConfig, PolicyRefs, RunConfig


def _config(tmp_path: Path) -> RunConfig:
    return RunConfig(
        artifacts_root=tmp_path / "artifacts",
        scenario_catalog_path=tmp_path / "scenarios",
        profile="offline",
        policy_refs=PolicyRefs(
            guardrail_policy=tmp_path / "missing-policy.yaml",
            model_policy=tmp_path / "model-policy.yaml",
        ),
        budget=BudgetConfig(),
    )


def test_run_launcher_returns_summary(tmp_path: Path) -> None:
    args = Namespace(
        profile=None,
        command=["python -m pytest -q"],
        json=False,
        execute_ralph=False,
        ralph_config="ralph.yml",
        ralph_backend=None,
    )
    summary = run_launcher(args, config=_config(tmp_path))
    assert summary["run_id"].startswith("run-")
    assert summary["status"] == "completed"
    assert summary["blocked_count"] == 0
    assert summary["ralph"] is None


def test_run_launcher_uses_profile_override(tmp_path: Path) -> None:
    args = Namespace(
        profile="online",
        command=["curl https://example.com"],
        json=False,
        execute_ralph=False,
        ralph_config="ralph.yml",
        ralph_backend=None,
    )
    summary = run_launcher(args, config=_config(tmp_path))
    assert summary["profile"] == "online"
