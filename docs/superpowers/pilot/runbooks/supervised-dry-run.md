# Supervised Dry Run Checklist (T094)

Checklist for a human-supervised run before enabling live unattended schedule.

## Preflight

- [ ] Scenario catalog locked read-only for run window.
- [ ] DTU mappings/profile loaded for target scenarios.
- [ ] Memory service health check passes.
- [ ] OTEL exporter phase selected and writable/reachable.
- [ ] Budget caps/fallback policy confirmed.

## Launch

- [ ] Start run with supervised terminal attached.
- [ ] Capture run ID and start timestamp.
- [ ] Confirm guardrails initialized.

## In-flight checks

- [ ] Observe at least one allowed command path.
- [ ] Observe at least one blocked-action event with reason code.
- [ ] Verify DTU responses match selected scenario profile.
- [ ] Verify telemetry events are emitted.

## Completion checks

- [ ] Verdict artifact(s) produced.
- [ ] Run manifest produced and schema-valid.
- [ ] Morning review report produced.
- [ ] Any `evaluation-pending` scenarios explicitly recorded.

## Post-run decision

- [ ] Findings written to `dry-run-results.md`.
- [ ] Risks triaged using `troubleshooting.md`.
- [ ] Recommendation ready for T096 go/no-go.
