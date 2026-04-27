"""US1 unattended run launcher workflow (T020)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lib.run_config import RunConfig, from_env
from lib.run_identity import new_run_id
from services.guardrail_policy_service import default_policy, load_guardrail_policy
from services.ralph_launcher import launch_ralph_run
from services.run_session_service import start_guarded_run


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one guarded overnight session.")
    parser.add_argument(
        "--profile",
        choices=["offline", "online"],
        default=None,
        help="Override profile from environment config.",
    )
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="Command candidate to evaluate (repeatable).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON summary.",
    )
    parser.add_argument(
        "--execute-ralph",
        action="store_true",
        help="Execute `ralph run` after guardrail pre-check passes.",
    )
    parser.add_argument(
        "--ralph-config",
        default="ralph.yml",
        help="Path to ralph config file (default: ralph.yml).",
    )
    parser.add_argument(
        "--ralph-backend",
        default=None,
        help="Optional backend override passed to `ralph run --backend`.",
    )
    return parser.parse_args(argv)


def run_launcher(args: argparse.Namespace, *, config: RunConfig) -> dict[str, Any]:
    profile = args.profile or config.profile
    run_id = new_run_id()
    commands = args.command or ["python -m pytest -q"]

    policy = _resolve_policy(config.policy_refs.guardrail_policy)
    guard_result = start_guarded_run(
        run_id=run_id,
        commands=commands,
        profile=profile,
        policy=policy,
    )
    ralph_summary: dict[str, Any] | None = None
    status = guard_result.status
    if args.execute_ralph and guard_result.status == "completed":
        launch = launch_ralph_run(
            config_path=Path(args.ralph_config),
            backend=args.ralph_backend,
            max_iterations=config.budget.iteration_cap,
            working_directory=config.artifacts_root.parent
            if config.artifacts_root.parent
            else None,
            enforce_ntm=True,
        )
        ralph_summary = {
            "command": launch.command,
            "returncode": launch.returncode,
        }
        if launch.returncode != 0:
            status = "failed"
    return {
        "run_id": guard_result.run_id,
        "profile": profile,
        "status": status,
        "transitions": list(guard_result.transitions),
        "blocked_count": guard_result.blocked_count,
        "allowed_count": guard_result.allowed_count,
        "blocked_events": guard_result.blocked_events,
        "ralph": ralph_summary,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = from_env()
    summary = run_launcher(args, config=config)

    if args.json:
        print(json.dumps(summary, separators=(",", ":")))
    else:
        print(f"[run_overnight] run_id={summary['run_id']}")
        print(f"[run_overnight] profile={summary['profile']} status={summary['status']}")
        print(
            f"[run_overnight] allowed={summary['allowed_count']} blocked={summary['blocked_count']}"
        )
    return 0 if summary["status"] == "completed" else 1


def _resolve_policy(path: Path):
    if path.exists():
        return load_guardrail_policy(path)
    return default_policy(profile="both")


if __name__ == "__main__":
    raise SystemExit(main())
