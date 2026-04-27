# Overnight Trial E2E Runbook (T044)

End-to-end operator runbook for one supervised overnight trial before live unattended scheduling.

---

## 1) Objective

Execute one controlled overnight run that exercises:

- guardrails and blocked-action evidence,
- scenario-based judging,
- DTU profile execution,
- memory + telemetry + manifest closure,
- morning review output.

---

## 2) Preconditions

- Phase 1 bootstrap complete (`T055-T063`)
- US1/US2/US3 tasks complete through `T091`
- Scenario catalog contains `SCN-PILOT-001..003`
- DTU mappings/profiles for those scenarios exist under `docs/superpowers/pilot/dtu/`

---

## 3) E2E execution steps

1. Lock scenario catalog read-only for run window.
2. Start DTU runtime (WireMock) and confirm health.
3. Confirm memory service health check passes.
4. Launch trial run using scheduler wrapper in supervised mode.
5. Monitor telemetry stream + blocked-action logs.
6. Confirm verdict artifacts and manifest are written.
7. Generate morning review report and complete review checklist.

---

## 4) Required outputs

- Run manifest (`runs/<run_id>/manifest.json`)
- Judge verdict artifacts (`runs/<run_id>/verdicts/*.json`)
- Telemetry events (`events.jsonl` and/or OTEL export)
- Morning review report JSON
- Dry-run findings document update (`dry-run-results.md`)

---

## 5) Pass criteria

- Guardrail blocked at least one prohibited action with reason code.
- At least one scenario produces a satisfactory verdict and one produces unsatisfactory or fallback.
- DTU path executes without needing live third-party dependencies.
- Manifest passes schema validation.
- Morning review completes with actionable findings.

---

## 6) References

- `quickstart.md`
- `supervised-dry-run.md`
- `dry-run-results.md`
- `verification-results.md`
