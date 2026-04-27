# Quickstart: Overnight VPS Coding Trial

## Goal

Run one end-to-end unattended trial using the selected stack and produce artifacts needed for
morning review and V1 progression decisions.

## Prerequisites

- Branch: `001-overnight-vps-system`
- Decisions and briefs available in `docs/superpowers/pilot/`
- DTU configuration available (`docs/superpowers/pilot/dtu/`)
- Guardrail policy installed and active
- External judge harness configured and immutable from coding-agent execution path
- Telemetry and memory services reachable in trial mode

## Trial Steps

1. **Prepare environment**
   - Load scoped secrets via Doppler.
   - Start required local services (DTU, memory, trace export path).
   - Confirm orchestrator and guardrails are active.

2. **Launch unattended run**
   - Start a run with `offline` profile by default.
   - Execute one or more predefined scenarios.
   - Capture run id and start timestamp.

3. **Validate safety behavior**
   - Confirm at least one blocked command event is denied and logged.
   - Confirm allowed development actions proceed.

4. **Evaluate outcomes**
   - Execute external judge on run traces + scenario definitions.
   - Persist verdict(s) using `judge-verdict.schema.json` structure.

5. **Capture run artifacts**
   - Produce run manifest per `run-manifest.schema.json`.
   - Link trace, verdict, and DTU artifact references.

6. **Morning review simulation**
   - Complete triage in under 10 minutes.
   - Record key failure reasons and memory updates.

## Validated Pilot References

- Trial runbook: `docs/superpowers/pilot/runbooks/trial-e2e.md`
- Supervised checklist: `docs/superpowers/pilot/runbooks/supervised-dry-run.md`
- Findings log: `docs/superpowers/pilot/runbooks/dry-run-results.md`
- Verification record: `docs/superpowers/pilot/runbooks/verification-results.md`
- US3 flow guide: `docs/superpowers/pilot/runbooks/us3-dtu-memory-loop.md`

## Validation Checklist

- [ ] Guardrails blocked dangerous command(s) with reason code
- [ ] Judge produced scenario-based verdict with reasoning
- [ ] DTU-backed validation completed without live dependency requirement
- [ ] Memory retrieval reduced repeated failure behavior (when applicable)
- [ ] Trace artifacts are sufficient for run diagnosis
- [ ] Run manifest links all required references

## Success Criteria Mapping

- SC-001: unattended completion rate
- SC-002: blocked high-risk attempt coverage
- SC-003: judge verdict coverage
- SC-004: DTU execution ratio
- SC-005: repeated failure reduction
- SC-006: morning review duration

## Rollback / Failure Handling

- If guardrails block legitimate critical path: switch to approved profile override and log incident.
- If judge is unavailable: mark run as `evaluation-pending`, do not claim scenario success.
- If DTU unavailable: abort validation stage and classify as infrastructure failure.
