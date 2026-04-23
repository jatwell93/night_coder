"""US1 unattended run launcher workflow (T020)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lib.run_config import RunConfig, from_env
from lib.run_identity import new_run_id
from services.guardrail_policy_service import default_policy, load_guardrail_policy
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
    return parser.parse_args(argv)


def run_launcher(args: argparse.Namespace, *, config: RunConfig) -> dict[str, Any]:
    profile = args.profile or config.profile
    run_id = new_run_id()
    commands = args.command or ["python -m pytest -q"]

    policy = _resolve_policy(config.policy_refs.guardrail_policy)
    result = start_guarded_run(
        run_id=run_id,
        commands=commands,
        profile=profile,
        policy=policy,
    )
    return {
        "run_id": result.run_id,
        "profile": profile,
        "status": result.status,
        "transitions": list(result.transitions),
        "blocked_count": result.blocked_count,
        "allowed_count": result.allowed_count,
        "blocked_events": result.blocked_events,
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
