# Verification matrix — feature-level quality and test commands — T014

Per-component test and quality ownership for the overnight VPS system. This is the operational
counterpart to [`quality-gates.md`](./quality-gates.md): that document defines **how** we run
checks, this one defines **what each component owes** to the checks.

Every row lists the component, the lint/type/test selectors that cover it, and which task(s) or
user story gate its verification. Before marking a task complete, run the component's row and
confirm all selectors pass.

**Baseline:** all commands assume the `.venv` is active (or prefix with `.venv/bin/`).

---

## 1. Foundational (Phase 2)

| Component | Source | Tests | Test selector | Notes |
|-----------|--------|-------|---------------|-------|
| Run identity | `src/lib/run_identity.py` | `tests/unit/test_run_identity.py` | `pytest -q tests/unit/test_run_identity.py` | T012 |
| Artifact paths | `src/lib/artifact_paths.py` | `tests/unit/test_artifact_paths.py` | `pytest -q tests/unit/test_artifact_paths.py` | T011 |
| Manifest validator | `src/lib/manifest_validation.py` | `tests/unit/test_manifest_validation.py` | `pytest -q tests/unit/test_manifest_validation.py` | T009 — schema at `specs/.../contracts/run-manifest.schema.json` |
| Verdict validator | `src/lib/verdict_validation.py` | `tests/unit/test_verdict_validation.py` | `pytest -q tests/unit/test_verdict_validation.py` | T010 — schema at `specs/.../contracts/judge-verdict.schema.json` |
| Event envelope | `src/lib/event_envelope.py` | `tests/unit/test_event_envelope.py` | `pytest -q tests/unit/test_event_envelope.py` | T013 |
| Secret redaction | `src/lib/secret_redaction.py` | `tests/unit/test_secret_redaction.py` | `pytest -q tests/unit/test_secret_redaction.py` | T064/T065 |
| Model policy adapter | `src/services/model_policy_service.py` | `tests/unit/test_model_policy_adapter.py` | `pytest -q tests/unit/test_model_policy_adapter.py` | T049/T050 |

**Phase 2 composite selector:** `pytest -q tests/unit` (all unit tests).

---

## 2. User Story 1 — Safe Overnight Execution (Phase 3)

Not yet implemented. Rows populate as tasks land.

| Component | Source | Tests | Test selector | Task |
|-----------|--------|-------|---------------|------|
| Guardrail policy loader | `src/services/guardrail_policy_service.py` | (tbd) | `pytest -q -k us1_policy` | T018 |
| Guardrail enforcement | `src/services/guardrail_enforcement_service.py` | `tests/contract/test_guardrail_event_contract.py` | `pytest -q -k us1_enforce` | T019, T015 |
| Run launcher CLI | `src/cli/run_overnight.py` | `tests/integration/test_guarded_overnight_run.py` | `pytest -q -k us1_launcher` | T020, T016 |
| Run lifecycle state | `src/services/run_session_service.py` | (tbd) | `pytest -q -k us1_lifecycle` | T021 |
| Blocked-action audit | `src/services/guardrail_audit_service.py` | (tbd) | `pytest -q -k us1_audit` | T022 |
| Profile selection | `src/services/run_profile_service.py` | `tests/integration/test_execution_profiles.py` | `pytest -q -k us1_profile` | T023, T017 |
| Orchestrator loop | `src/services/orchestrator_loop_service.py` | `tests/integration/test_orchestrator_iteration_loop.py` | `pytest -q -k us1_loop` | T052, T051 |

**US1 composite selector:** `pytest -q -m us1` (marker defined in `pyproject.toml`).

---

## 3. User Story 2 — External Outcome-Based Judging (Phase 4)

| Component | Source | Tests | Test selector | Task |
|-----------|--------|-------|---------------|------|
| Scenario evidence | `src/services/scenario_evidence_service.py` | (tbd) | `pytest -q -k us2_evidence` | T028 |
| Judge runner | `src/services/judge_runner_service.py` | (tbd) | `pytest -q -k us2_runner` | T029 |
| Verdict persistence | `src/services/judge_verdict_service.py` | `tests/contract/test_judge_verdict_contract.py` | `pytest -q -k us2_persist` | T030, T025 |
| Harness guard | `src/services/judge_harness_guard_service.py` | `tests/integration/test_judge_immutability_boundary.py` | `pytest -q -k us2_guard` | T031, T026 |
| Run completion | `src/services/run_completion_service.py` | `tests/integration/test_outcome_based_judging.py` | `pytest -q -k us2_completion` | T032, T027 |
| Judge fallback | `src/services/judge_fallback_service.py` | `tests/integration/test_judge_unavailable_fallback.py` | `pytest -q -k us2_fallback` | T067, T066 |

**US2 composite selector:** `pytest -q -m us2`.

---

## 4. User Story 3 — Continuous Validation with DTU and Memory (Phase 5)

| Component | Source | Tests | Test selector | Task |
|-----------|--------|-------|---------------|------|
| DTU health | `src/services/dtu_health_service.py` | (tbd) | `pytest -q -k us3_health` | T037 |
| DTU executor | `src/services/dtu_validation_service.py` | `tests/integration/test_dtu_validation_cycle.py` | `pytest -q -k us3_dtu` | T038, T035 |
| DTU startup failure | (same) | `tests/integration/test_dtu_startup_failure.py` | `pytest -q -k us3_dtu_startup` | T068 |
| Memory feedback | `src/services/memory_feedback_service.py` | `tests/integration/test_memory_feedback_loop.py` | `pytest -q -k us3_memory` | T039, T036 |
| Memory relevance | `src/services/memory_relevance_service.py` | `tests/integration/test_memory_relevance_filter.py` | `pytest -q -k us3_relevance` | T072, T069 |
| Telemetry publisher | `src/services/telemetry_service.py` | (tbd) | `pytest -q -k us3_telemetry` | T040 |
| Partial telemetry | (same) | `tests/integration/test_partial_telemetry_failed_run.py` | `pytest -q -k us3_partial` | T070 |
| Run manifest builder | `src/services/run_manifest_service.py` | `tests/contract/test_run_manifest_contract.py` | `pytest -q -k us3_manifest` | T041, T034 |
| Run finalizer | `src/services/run_finalize_service.py` | (tbd) | `pytest -q -k us3_finalize` | T042 |
| Morning review | `src/services/morning_review_service.py` | `tests/integration/test_morning_review_report.py` | `pytest -q -k us3_morning` | T054, T053 |
| Scenario catalog loader | `src/services/scenario_catalog_service.py` | (tbd) | `pytest -q -k us3_catalog` | T071 |

**US3 composite selector:** `pytest -q -m us3`.

---

## 5. Cross-cutting checks (every task)

Before marking **any** task complete:

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest -q
.venv/bin/mypy src
```

All four MUST exit 0. No exceptions.

---

## 6. Per-task verification protocol

1. **Before starting work:** run the composite selector for the user story (e.g. `pytest -q -m us2`) and confirm current baseline.
2. **Write failing tests first** (per task's test subtask — e.g. T015 before T019).
3. **Implement** until the component's specific selector passes.
4. **Re-run the cross-cutting checks** (§5) and confirm zero regressions elsewhere.
5. **Mark task complete** only when all of the above pass.

---

## 7. Coverage expectations

Coverage thresholds are not enforced during the pilot (we ship working vertical slices first),
but `pytest-cov` is installed so operators can spot-check:

```bash
.venv/bin/pytest --cov=src --cov-report=term-missing
```

Target for Phase 6 (T046+): **≥ 80% line coverage** on `src/lib/` and `src/services/`. CLI
modules (`src/cli/`) are covered by integration tests rather than unit lines.

---

## 8. Contract tests

Contract tests (`tests/contract/*`) validate that services produce artifacts matching the JSON
Schemas in `specs/001-overnight-vps-system/contracts/`. These tests are the boundary between
this system and any downstream consumer (reviewer UI, telemetry sink, future multi-agent
coordinator). **Do not relax contract tests to unblock a task** — update the schema and the
consuming services in the same change instead.

| Contract | Schema | Test | Task |
|----------|--------|------|------|
| Run manifest | `run-manifest.schema.json` | `tests/contract/test_run_manifest_contract.py` | T034 |
| Judge verdict | `judge-verdict.schema.json` | `tests/contract/test_judge_verdict_contract.py` | T025 |
| Guardrail event | (inline) | `tests/contract/test_guardrail_event_contract.py` | T015 |

---

## 9. Validation checklist

- [x] Every Phase 2 foundational component listed with its test selector.
- [x] Placeholder rows for Phase 3–5 components linked to their tasks.
- [x] Cross-cutting gate commands documented and matched to `quality-gates.md`.
- [x] Per-task verification protocol explicit.
- [x] Document linked from [`README.md`](./README.md).

---

## 10. References

- Quality gates: [`./quality-gates.md`](./quality-gates.md) (T006).
- Status vocabulary: [`./status-taxonomy.md`](./status-taxonomy.md) (T007).
- Reason codes: [`./reason-codes.md`](./reason-codes.md) (T008).
- Full task list: [`../../../../specs/001-overnight-vps-system/tasks.md`](../../../../specs/001-overnight-vps-system/tasks.md).
- Future: `verification-results.md` (T048) — recorded outcomes across the matrix.

---

## Revision

| Date | Change | Notes |
|------|--------|-------|
| 2026-04-23 | Initial matrix (T014) | Covers all Phase 2 components; Phase 3–5 rows are placeholders. |
