# Status taxonomy (pilot) — T007

Canonical vocabulary for run lifecycle status. Every service, schema, log line, and operator
report MUST use these exact strings. Synonyms, adjectives, and ad-hoc values are forbidden — if
a new state is needed, propose an addition here first.

**Sources of truth:**
- [`../../../../specs/001-overnight-vps-system/data-model.md`](../../../../specs/001-overnight-vps-system/data-model.md) §1 (RunSession), §8 (RunManifest).
- [`../../../../specs/001-overnight-vps-system/contracts/run-manifest.schema.json`](../../../../specs/001-overnight-vps-system/contracts/run-manifest.schema.json) — `summary.status` enum.

---

## 1. RunSession status

Lifecycle state of a single overnight run attempt.

| Value | When it applies | Terminal? | Requires `ended_at` |
|-------|-----------------|-----------|---------------------|
| `queued` | Run record created, scheduler has not yet started it. | No | No |
| `running` | Scheduler has invoked the launcher and the orchestrator is iterating. | No | No |
| `completed` | All scheduled scenarios finished with judge verdicts recorded (satisfied or not). | **Yes** | Yes |
| `failed` | Fatal error before judging could complete (infrastructure failure, guardrail kill-switch, timeout). | **Yes** | Yes |
| `aborted` | Operator manually halted the run (e.g. `systemctl stop`, explicit cancel). | **Yes** | Yes |

### Transitions

```text
queued ──► running ──► completed
                 │
                 ├──► failed
                 │
                 └──► aborted
```

- Only `queued → running` and `running → {completed,failed,aborted}` are valid.
- No transition returns to `running` once a terminal state is reached — retries create a new
  RunSession.

### Invariants

- Terminal statuses (`completed`, `failed`, `aborted`) MUST carry `ended_at`.
- `ended_at >= started_at` when both are set.
- `running` MUST carry `started_at`.

---

## 2. RunManifest summary status

The manifest's `summary.status` field reports the **judging-level** outcome, which is a
superset of RunSession status because it adds the "judge could not run" case.

| Value | When it applies |
|-------|-----------------|
| `completed` | RunSession ended with verdicts recorded. |
| `failed` | RunSession failed before verdicts could be recorded. |
| `aborted` | Operator cancelled before verdicts could be recorded. |
| `evaluation-pending` | Run finished but the external judge harness was unavailable; verdicts are expected to be generated later. |

`evaluation-pending` is unique to manifest summaries — it is **not** a RunSession status. See
T067 (`src/services/judge_fallback_service.py`) for the fallback handler that sets it.

---

## 3. DTUArtifact health status

Used by the DTU readiness checker (T037) and reported in telemetry.

| Value | Meaning |
|-------|---------|
| `ready` | Dependency responds to health check within SLO. |
| `degraded` | Responds but with elevated latency or partial functionality. A run MAY proceed with a warning. |
| `down` | Not reachable or failing health check. A run MUST NOT start scenarios that depend on this DTU. |

**Transitions:** `ready ↔ degraded → down → ready` (after operator-triggered recovery).

---

## 4. TelemetryEvent severity

Used by `src/lib/event_envelope.py` (T013) and all downstream publishers.

| Value | Meaning |
|-------|---------|
| `info` | Normal lifecycle event. Always emitted. |
| `warn` | Degraded-but-continuing condition (e.g. DTU `degraded`, memory fallback). |
| `error` | Failure requiring operator attention; does not necessarily abort the run. |

Severity escalation from `error → aborted RunSession` is a policy decision in the guardrail
and run-completion services, not an automatic rule.

---

## 5. JudgeVerdict satisfaction

A judge verdict is a binary satisfaction result plus a score.

| Field | Values |
|-------|--------|
| `satisfied` | `true` or `false` |
| `score` | `0.0`–`1.0` (inclusive) |

`satisfied=false` with `score >= 0.5` is valid (e.g. partial success that falls short of the
scenario's acceptance threshold). `satisfied=true` with `score < 0.5` is **not** valid — the
contract's `score` reflects the judge's confidence in the `satisfied` decision.

---

## 6. Usage rules

- **Code:** define enums exactly matching the tables above. Never duplicate string literals —
  always import from the shared module once it exists.
- **Config / JSON output:** use the lowercase kebab-case-where-noted strings verbatim.
- **Operator-facing UI:** may render with title case (`Completed`, `Evaluation Pending`) but
  the underlying value MUST be the canonical string.
- **Logs / events:** always the canonical lowercase value.

---

## 7. Adding a new status

Do not add a status inline. Instead:

1. Propose the addition here with a dated revision entry.
2. Update the corresponding JSON schema in `specs/.../contracts/`.
3. Update the data model (`specs/.../data-model.md`) if a new state is modelled.
4. Update every service that consumes the enum.

---

## 8. Validation checklist

- [x] All RunSession statuses match `data-model.md` §1.
- [x] All RunManifest summary statuses match `run-manifest.schema.json`.
- [x] `evaluation-pending` documented as manifest-only (T067 reference).
- [x] Transitions documented with invariants.
- [x] Document linked from [`README.md`](./README.md).

---

## 9. References

- Run manifest contract: [`../../../../specs/001-overnight-vps-system/contracts/run-manifest.schema.json`](../../../../specs/001-overnight-vps-system/contracts/run-manifest.schema.json)
- Judge verdict contract: [`../../../../specs/001-overnight-vps-system/contracts/judge-verdict.schema.json`](../../../../specs/001-overnight-vps-system/contracts/judge-verdict.schema.json)
- Future consumer: `src/services/run_session_service.py` (T021)
- Future consumer: `src/services/judge_fallback_service.py` (T067) — sets `evaluation-pending`.

---

## Revision

| Date | Change | Notes |
|------|--------|-------|
| 2026-04-23 | Initial taxonomy (T007) | Aligned with data-model.md and run-manifest schema. |
