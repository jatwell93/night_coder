# US3 Continuous Validation Flow (T043)

Operator playbook for DTU-backed validation with memory-assisted feedback and telemetry closure.

---

## 1) Scope

This runbook covers the US3 loop:

1. Load scenario from read-only catalog.
2. Select DTU profile/mappings.
3. Run validation cycle.
4. Capture telemetry and judge/verdict outcomes.
5. Read/write memory feedback.
6. Finalize manifest and produce morning review inputs.

---

## 2) Runtime components

- Scenario loader: `src/services/scenario_catalog_service.py`
- DTU validation: `src/services/dtu_validation_service.py`
- DTU health classification: `src/services/dtu_health_service.py`
- Memory relevance filter: `src/services/memory_relevance_service.py`
- Memory feedback orchestration: `src/services/memory_feedback_service.py`
- Telemetry publishing: `src/services/telemetry_service.py`
- Finalization/manifest: `src/services/run_finalize_service.py`, `src/services/run_manifest_service.py`

---

## 3) Per-run operator checklist

### 3.1 Before run

- Confirm scenario catalog is locked read-only (`chmod -R a-w` during run window).
- Confirm DTU mapping profile exists for each scheduled scenario.
- Confirm memory service health check passes.
- Confirm OTEL exporter phase is set appropriately (`phase1` or `phase2`).

### 3.2 During run

- Monitor DTU startup events and fail fast on `DTU.error.startup-failure`.
- Track retries and timeout behavior for scenario-specific DTU mappings.
- Ensure partial telemetry still emits on failure paths.

### 3.3 After run

- Verify run manifest was written and schema-valid.
- Confirm memory writeback occurred for failed or retried paths.
- Assemble morning review report and capture unsatisfied scenarios.

---

## 4) Failure-mode handling

- **DTU startup failure**: classify as infrastructure failure; do not treat as scenario logic failure.
- **Stale memory candidates**: filter by age threshold before retrieval.
- **Partial telemetry**: preserve emitted events and mark bundle as partial.
- **Evaluation pending**: preserve fallback reason and schedule re-evaluation.

---

## 5) Artifacts to review each morning

- `runs/<run_id>/manifest.json`
- `runs/<run_id>/events.jsonl` (or OTEL export location)
- `runs/<run_id>/verdicts/*.json`
- morning review report JSON output
- memory-service write/read summary logs

---

## 6) Validation checklist

- [ ] Scenario catalog read-only boundary enforced during run.
- [ ] DTU profile selected per scenario and validated.
- [ ] Memory retrieval uses staleness filtering.
- [ ] Telemetry bundle includes failure-path partial captures.
- [ ] Manifest written and schema-valid for each run.
- [ ] Morning review report generated from telemetry + verdicts.

---

## 7) References

- `docs/superpowers/pilot/runbooks/scenario-catalog.md`
- `docs/superpowers/pilot/runbooks/memory-service-bootstrap.md`
- `docs/superpowers/pilot/runbooks/langfuse-bootstrap.md`
- `specs/001-overnight-vps-system/tasks.md` (`T043`)
