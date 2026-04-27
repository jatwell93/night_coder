# US1 operator flow — safe unattended execution (pilot) — T024

Operator runbook for **User Story 1**:

> Start an unattended run with guardrails enabled and confirm blocked dangerous commands are
> denied while allowed commands proceed.

This runbook is the operational counterpart to US1 implementation tasks (`T018`–`T023`,
`T052`, `T080`–`T082`).

---

## 1. Scope

This runbook covers:

- loading and validating guardrail policy,
- profile-aware command enforcement (`offline` default),
- blocked-action event evidence,
- unattended launcher invocation (`src/cli/run_overnight.py`),
- scheduler-wrapper integration (`scripts/run-overnight.sh`).

It does **not** cover judge verdict flows (US2) or DTU/memory flows (US3).

---

## 2. Prerequisites

- [`vps-bootstrap.md`](./vps-bootstrap.md) (T055/T056)
- [`vps-container-runtime.md`](./vps-container-runtime.md) (T057)
- [`vps-ralph-install.md`](./vps-ralph-install.md) (T058)
- [`vps-secrets-bootstrap.md`](./vps-secrets-bootstrap.md) (T059)
- [`vps-guardrails-bootstrap.md`](./vps-guardrails-bootstrap.md) (T061)
- [`scenario-catalog.md`](./scenario-catalog.md) (T062)
- [`vps-scheduler.md`](./vps-scheduler.md) (T063)

Repo state:

- US1 services and tests present under `src/services/` and `tests/`.
- `scripts/run-overnight.sh` synced to VPS path `~/night_coder/scripts/run-overnight.sh`.

---

## 3. US1 architecture map

| Concern | Component | Task |
|---------|-----------|------|
| Guardrail policy load | `src/services/guardrail_policy_service.py` | T018 |
| Command interception decision | `src/services/guardrail_enforcement_service.py` | T019 |
| Lifecycle + transitions | `src/services/run_session_service.py` | T021 |
| Blocked-action payloads | `src/services/guardrail_audit_service.py` | T022 |
| Profile enforcement | `src/services/run_profile_service.py` | T023 |
| Iteration loop stop logic | `src/services/orchestrator_loop_service.py` | T052 |
| NTM gate | `src/services/ntm_adapter.py` | T080 |
| Ralph launch integration | `src/services/ralph_launcher.py` | T081 |
| Unattended launcher | `src/cli/run_overnight.py` | T020 |

---

## 4. Policy file and profile defaults

### 4.1 Guardrail policy location

Current runtime expects `NIGHT_CODER_GUARDRAIL_POLICY` to point at a YAML policy file.
If missing, launcher falls back to in-code conservative defaults.

For pilot operations, keep policy in:

`docs/superpowers/pilot/config/guardrail-policy.yaml`

> `T079 [USER]` tracks authoring/approval of this file.

### 4.2 Profile behavior

- Default profile is `offline`.
- `offline` blocks network-egress command patterns.
- `online` allows network-egress patterns.

Use profile override only when scenario requirements explicitly need live egress.

---

## 5. Local verification flow (repo root)

Run from `/home/ja/night_coder` (or VPS checkout path).

### 5.1 Unit + integration + contract slice for US1

```bash
.venv/bin/pytest -q \
  tests/contract/test_guardrail_event_contract.py \
  tests/integration/test_guarded_overnight_run.py \
  tests/integration/test_execution_profiles.py \
  tests/integration/test_orchestrator_iteration_loop.py \
  tests/unit/test_guardrail_policy_service.py \
  tests/unit/test_guardrail_enforcement_service.py \
  tests/unit/test_ntm_adapter.py \
  tests/unit/test_ralph_launcher.py \
  tests/unit/test_run_overnight_cli.py
```

Expected: all pass.

### 5.2 Full project gates

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest -q
.venv/bin/mypy src
```

Expected: all exit `0`.

---

## 6. Launcher smoke checks

### 6.1 Guardrail pre-check only (no live Ralph execution)

```bash
doppler run -- python src/cli/run_overnight.py --json \
  --command "python -m pytest -q" \
  --command "rm -rf /tmp/demo"
```

Expected:

- `blocked_count` >= 1
- blocked event contains `GRD.block.destructive-filesystem`
- status remains non-crash (`completed` or policy-defined failure state)

### 6.2 Profile behavior check

```bash
doppler run -- python src/cli/run_overnight.py --json \
  --profile offline \
  --command "curl https://example.com"
```

Expected:

- blocked event reason `GRD.block.network-egress`.

### 6.3 Optional live Ralph execution path

```bash
doppler run -- python src/cli/run_overnight.py --json \
  --execute-ralph \
  --ralph-config ralph.yml \
  --ralph-backend gemini \
  --command "python -m pytest -q"
```

Expected:

- NTM gate runs first.
- launcher includes `ralph` summary object with return code.

---

## 7. Scheduler wrapper check (T082 path)

On VPS:

```bash
bash ~/night_coder/scripts/run-overnight.sh
```

Expected:

- PATH sanity and NTM presence check pass.
- scenario catalog directory check passes.
- wrapper executes `doppler run -- python .../src/cli/run_overnight.py --json`.

If wrapper diverges from repo canonical script, resync:

```bash
cp ~/night_coder/scripts/run-overnight.sh ~/night_coder/scripts/run-overnight.sh.bak
cp ~/night_coder/scripts/run-overnight.sh /tmp/run-overnight.current.sh
cp /home/ja/night_coder/scripts/run-overnight.sh ~/night_coder/scripts/run-overnight.sh
chmod +x ~/night_coder/scripts/run-overnight.sh
```

---

## 8. Evidence to retain for morning review

For each US1 unattended run, keep:

- launcher JSON summary output,
- blocked action events (reason codes + attempted action),
- systemd unit status (`night-coder-run.service`),
- journal tail for the run window.

Recommended capture:

```bash
journalctl --user -u night-coder-run.service --no-pager -n 200
systemctl --user status night-coder-run.service
```

---

## 9. Known operator decisions still pending

- `T082` VPS deployment confirmation remains environment-specific even though repo wiring is done.

---

## 10. T024 completion checklist

- [x] US1 operator flow documented end-to-end (policy -> enforcement -> launcher -> scheduler).
- [x] Includes concrete commands for verification and expected outcomes.
- [x] References all US1 implementation components and task IDs.
- [x] Includes evidence retention guidance for morning review.
- [x] Linked from runbook index (`README.md`).

---

## 11. References

- Task list: [`../../../../specs/001-overnight-vps-system/tasks.md`](../../../../specs/001-overnight-vps-system/tasks.md)
- Scheduler wiring: [`./vps-scheduler.md`](./vps-scheduler.md)
- Quality gates: [`./quality-gates.md`](./quality-gates.md)
- Verification matrix: [`./verification-matrix.md`](./verification-matrix.md)

---

## Revision

| Date | Notes |
|------|-------|
| 2026-04-23 | Initial T024 runbook covering US1 safe unattended execution operator flow. |
