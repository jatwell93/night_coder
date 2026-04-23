# Pilot runbooks — index

Operator-facing runbooks for the overnight VPS coding system. Each runbook maps to one or more
tasks in [`specs/001-overnight-vps-system/tasks.md`](../../../../specs/001-overnight-vps-system/tasks.md)
and is intended to be followed top-to-bottom on a fresh VPS.

## How to use this index

1. Start with **Phase 1 bootstrap** runbooks in the order listed — each depends on the previous.
2. Use **Phase 2+ references** as they are introduced by user-story implementation.
3. Every runbook ends with a **Validation checklist** — do not mark a task complete until every
   checklist item is green.
4. Record any deviation (non-default path, alternate install method, etc.) in the runbook's
   revision table so the next operator inherits your context.

## Phase 1 — VPS bootstrap and baseline infrastructure

| Order | Task | Runbook | Purpose |
|-------|------|---------|---------|
| 1 | T055 | [`vps-bootstrap.md`](./vps-bootstrap.md) | Provision Ubuntu 24.04, create `deploy` user, SSH hardening, firewall, repo clone (§12). |
| 2 | T056 | [`vps-bootstrap.md`](./vps-bootstrap.md) §13 | Install runtime prerequisites (Python 3.12+, git, tmux, curl, jq). |
| 3 | T057 | [`vps-container-runtime.md`](./vps-container-runtime.md) | Install rootless Podman (or Docker) for DTU containers. |
| 4 | T058 | [`vps-ralph-install.md`](./vps-ralph-install.md) | Install Ralph orchestrator CLI. |
| 5 | T059 | [`vps-secrets-bootstrap.md`](./vps-secrets-bootstrap.md) | Install Doppler service-token injection flow. |
| 6 | T060 | [`vps-dependency-smoke-tests.md`](./vps-dependency-smoke-tests.md) | Smoke test DTU/judge/observability dependencies. |
| 7 | T061 | [`vps-guardrails-bootstrap.md`](./vps-guardrails-bootstrap.md) | Install NTM + DCG guardrail layer and baseline policy. |
| 8 | T062 | [`scenario-catalog.md`](./scenario-catalog.md) | Create scenario catalog, lock read-only, set `SCENARIO_CATALOG_PATH`. |
| 9 | T063 | [`vps-scheduler.md`](./vps-scheduler.md) | Install systemd user timer + wrapper for unattended run windows. |

## Phase 1 — shared conventions

| Task | Runbook | Purpose |
|------|---------|---------|
| T001 | [`README.md`](./README.md) (this file) | Runbook index and operator conventions. |
| T006 | [`quality-gates.md`](./quality-gates.md) | Lint/test/quality command matrix used across the repo. |
| — | [`../config/README.md`](../config/README.md) | Trial configuration directory — per-environment overrides. |

## Phase 2 — foundational taxonomies

| Task | Runbook | Purpose |
|------|---------|---------|
| T007 | [`status-taxonomy.md`](./status-taxonomy.md) | Canonical run status vocabulary. |
| T008 | [`reason-codes.md`](./reason-codes.md) | Shared guardrail and judge reason codes. |
| T014 | [`verification-matrix.md`](./verification-matrix.md) | Feature-level quality and test command matrix. |

## Phase 3+ — user-story runbooks (placeholders)

These runbooks are created by the tasks listed. They do not exist yet — links will activate as
each task ships.

| Task | Runbook | Purpose |
|------|---------|---------|
| T024 | `us1-safe-execution.md` | US1 operator flow — safe unattended execution. |
| T033 | `us2-outcome-judging.md` | US2 reviewer flow — outcome-based judging. |
| T043 | `us3-dtu-memory-loop.md` | US3 continuous validation — DTU + memory feedback. |
| T044 | `trial-e2e.md` | End-to-end overnight trial runbook (Phase 6). |
| T045 | `troubleshooting.md` | Failure-mode troubleshooting matrix. |
| T048 | `verification-results.md` | Full verification matrix outcomes. |

## Runbook conventions

- **Audience:** a technical operator with SSH access to the VPS and sudo-capable `deploy` user.
- **OS baseline:** Ubuntu 24.04 LTS (noble). Commands assume `bash` and `systemd`.
- **Paths:** `~/night_coder` on the VPS = this repository's checkout. Relative paths in runbooks
  resolve from that root unless stated otherwise.
- **No secrets in runbooks.** Any API key, token, or credential is injected via Doppler
  (`doppler run -- …`) or the operator's shell — never committed.
- **Every runbook ends with a validation checklist** and a revision table. Record the date,
  option chosen (where applicable), and any deviation.

## Related references

- [`../DECISIONS.md`](../DECISIONS.md) — Stack decisions (orchestrator, guardrails, judge, DTU,
  observability, sandbox, secrets, memory, artifact registry).
- [`../../../../specs/001-overnight-vps-system/plan.md`](../../../../specs/001-overnight-vps-system/plan.md) —
  Implementation plan and constitution gates.
- [`../../../../specs/001-overnight-vps-system/tasks.md`](../../../../specs/001-overnight-vps-system/tasks.md) —
  Task list (source of truth for task IDs used above).
