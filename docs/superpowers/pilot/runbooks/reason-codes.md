# Reason codes (pilot) — T008

Shared vocabulary for **why** something happened: guardrail blocks, judge outcomes, run
failures, and memory decisions. Every structured event, verdict, and blocked-action record MUST
use one of these canonical codes.

The goal is operator-facing triage: reading a reason code should tell an on-call reviewer what
happened without needing to open the full trace.

**Sources:**
- [`../../../../specs/001-overnight-vps-system/spec.md`](../../../../specs/001-overnight-vps-system/spec.md) — FR-003 (blocked action recording).
- [`./status-taxonomy.md`](./status-taxonomy.md) (T007) — paired status vocabulary.

---

## 1. Format

```text
<NAMESPACE>.<CATEGORY>.<SPECIFIC_REASON>
```

- **NAMESPACE:** 3–4 char uppercase domain code (`GRD`, `JDG`, `RUN`, `MEM`, `DTU`, `SYS`).
- **CATEGORY:** single lowercase word (`block`, `deny`, `timeout`, `missing`, ...).
- **SPECIFIC_REASON:** kebab-case descriptor.

Examples:

- `GRD.block.destructive-filesystem`
- `JDG.deny.evidence-missing`
- `RUN.timeout.window-exceeded`

---

## 2. Guardrail (GRD) — T022 blocked-action logging

Emitted when NTM or DCG refuses a command.

| Code | Meaning | Operator action |
|------|---------|-----------------|
| `GRD.block.destructive-filesystem` | Command would delete, chmod, or overwrite protected paths (`~`, `/etc`, repo root). | Review command in blocked-action log; adjust policy only if benign. |
| `GRD.block.scenario-catalog-write` | Attempt to modify the read-only scenario catalog. | Confirm catalog lock is active (see `scenario-catalog.md` §4.2). |
| `GRD.block.judge-harness-write` | Attempt to modify the judge harness path. | Should not occur if `judge_harness_guard_service` (T031) is healthy. |
| `GRD.block.network-egress` | Outbound network call not allowed under the current profile (usually `offline`). | Expected in `offline`; switch to `online` profile only if scenario requires it. |
| `GRD.block.privileged-escalation` | `sudo`, `su`, or capability-raising command. | Never permitted during a run; investigate how it was attempted. |
| `GRD.block.unknown-binary` | Command not on the allowlist. | Expand allowlist only after security review. |
| `GRD.allow.permitted` | Command matched an allow pattern (emitted only at `debug` severity). | No action. |

---

## 3. Judge (JDG) — T030 verdict persistence, T067 fallback

Emitted with every `JudgeVerdict` and with judge-runner failures.

| Code | Meaning |
|------|---------|
| `JDG.satisfied.ok` | Scenario's expected outcomes all met; `satisfied=true`. |
| `JDG.deny.outcome-mismatch` | Process completed but user outcome differs from scenario expectation. |
| `JDG.deny.evidence-missing` | Required evidence artifact not produced by the run. |
| `JDG.deny.grading-uncertain` | Judge could not confidently decide; `satisfied=false` with low score. |
| `JDG.fallback.evaluation-pending` | Judge harness unavailable; manifest set to `evaluation-pending` (T067). |
| `JDG.error.harness-invalid` | Judge harness input was malformed (contract violation). |

---

## 4. Run lifecycle (RUN)

Emitted by `run_session_service` (T021) and `run_completion_service` (T032).

| Code | Meaning |
|------|---------|
| `RUN.start.ok` | RunSession transitioned `queued → running`. |
| `RUN.end.completed` | Normal termination with verdicts recorded. |
| `RUN.end.failed` | Terminated before verdicts could be recorded (see paired sub-reason). |
| `RUN.end.aborted` | Operator-triggered cancel. |
| `RUN.timeout.window-exceeded` | Exceeded the 8h systemd `TimeoutStartSec` or orchestrator budget. |
| `RUN.timeout.iteration-budget` | Exceeded per-iteration budget in `orchestrator_loop_service` (T052). |
| `RUN.error.orchestrator-crash` | Orchestrator process exited non-zero. |
| `RUN.error.missing-secret` | Doppler injection failed for a required key. |

---

## 5. DTU (DTU) — T037 health checks

Emitted by `dtu_health_service` (T037) and `dtu_validation_service` (T038).

| Code | Meaning |
|------|---------|
| `DTU.health.ready` | Dependency passed readiness check. |
| `DTU.health.degraded` | Responding but outside SLO. |
| `DTU.health.down` | Not reachable. Runs depending on it MUST NOT start. |
| `DTU.error.startup-failure` | DTU failed to start; classified as infrastructure failure per T068. |

---

## 6. Memory (MEM) — T039 memory feedback, T072 relevance filter

Emitted by `memory_feedback_service` and `memory_relevance_service`.

| Code | Meaning |
|------|---------|
| `MEM.retrieve.hit` | Relevant memory retrieved and injected into context. |
| `MEM.retrieve.miss` | No relevant memory found; scenario starts with empty prior. |
| `MEM.filter.stale` | Candidate memory rejected by relevance filter (T072). |
| `MEM.write.stored` | New memory written after run completion. |
| `MEM.write.redacted` | Attempted write was redacted because content contained a secret pattern. |

---

## 7. System (SYS)

Low-frequency events outside the other categories.

| Code | Meaning |
|------|---------|
| `SYS.config.loaded` | Config file successfully loaded at startup. |
| `SYS.config.invalid` | Config validation failed at startup; run aborts. |
| `SYS.telemetry.partial` | Partial telemetry captured on failed run (T070). |

---

## 8. Pairing with status

Every terminal `RUN.end.*` reason pairs with a RunSession status:

| RunSession status | Valid `RUN.end.*` codes |
|-------------------|-------------------------|
| `completed` | `RUN.end.completed` |
| `failed` | `RUN.end.failed`, `RUN.timeout.*`, `RUN.error.*`, `DTU.error.startup-failure` |
| `aborted` | `RUN.end.aborted` |

This invariant is enforced by `run_completion_service` (T032).

---

## 9. Usage rules

- **One reason per event.** If multiple reasons apply, use the most specific upstream cause and
  reference others in the event payload.
- **Never invent codes inline.** Adding a code requires updating this document and the
  consuming service's enum in the same PR.
- **Operator-visible strings only.** Never put secret values in reason codes or payloads — see
  `src/lib/secret_redaction.py` (T065).

---

## 10. Validation checklist

- [x] Namespaces cover every emitter surface (guardrail, judge, run, DTU, memory, system).
- [x] Every terminal run code maps to a valid `RunSession.status`.
- [x] Evaluation-pending pairing with T067 documented.
- [x] Document linked from [`README.md`](./README.md).

---

## 11. References

- Status taxonomy: [`./status-taxonomy.md`](./status-taxonomy.md) (T007)
- Blocked-action logging: future `src/services/guardrail_audit_service.py` (T022)
- Judge persistence: future `src/services/judge_verdict_service.py` (T030)
- Secret redaction: future `src/lib/secret_redaction.py` (T065)

---

## Revision

| Date | Change | Notes |
|------|--------|-------|
| 2026-04-23 | Initial reason codes (T008) | Covers GRD/JDG/RUN/DTU/MEM/SYS namespaces. |
