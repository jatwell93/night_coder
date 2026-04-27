# Troubleshooting Matrix (T045)

Common failure modes and operator actions for overnight pilot runs.

| Symptom | Likely Cause | Detection Signal | Immediate Action | Follow-up |
|---|---|---|---|---|
| Guardrails block valid action | Allowlist too strict | `GRD.block.*` events on expected workflow command | Re-run with approved profile override after review | Update policy + regression test |
| Judge unavailable | Provider/API outage or budget gate | `evaluation-pending`, `JDG.fallback.evaluation-pending` | Mark pending and queue re-evaluation | Validate judge endpoint and budget caps |
| DTU startup failure | WireMock container/config issue | `DTU.error.startup-failure` | Fail run as infrastructure | Fix mapping/profile and rerun |
| Malformed verdict payload | Adapter/schema mismatch | Contract validation error | Stop publish; inspect raw payload | Update adapter normalization and tests |
| Memory retrieval not helping | Stale/irrelevant entries | High retry_count persists | Tighten relevance filter window | Review memory write policy |
| Missing telemetry tail | Early crash before finalize | Partial telemetry bundle flagged | Preserve partial bundle and classify failure | Add startup/teardown instrumentation |
| Manifest invalid | Missing refs or bad summary status | `ManifestValidationError` | Halt publication; regenerate manifest | Patch finalize path and add test |
| Scheduler didn’t run | Timer disabled or service failure | No run_id generated overnight | Execute manual supervised run | Re-enable timer and verify unit status |

## Escalation Levels

- **P1:** Data loss, secret exposure, destructive command bypass
- **P2:** No verdict/manifest, DTU hard failure, scheduler outage
- **P3:** Degraded telemetry, noisy retries, partial memory quality

## Reference docs

- `reason-codes.md`
- `status-taxonomy.md`
- `us1-safe-execution.md`
- `us2-outcome-judging.md`
- `us3-dtu-memory-loop.md`
