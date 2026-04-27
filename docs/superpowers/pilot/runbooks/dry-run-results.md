# Supervised Dry Run Results (T095)

## Run Session

- Date: 2026-04-27
- Mode: supervised (local verification run)
- Scope: US1+US2+US3 validation surfaces and phase-6 readiness artifacts

## What was executed

- Unit and integration subsets validating:
  - judge fallback and outcome paths,
  - US3 DTU/memory/telemetry/manifest/finalize flows,
  - OTEL phase wiring,
  - WireMock mapping loader/validation.

## Observed outcomes

- Guardrail/judge/manifest contract tests pass for implemented flows.
- US3 integration set passes including partial-telemetry and morning review assembly.
- OTEL exporter config supports both phase1 file export and phase2 OTLP endpoint mode.
- DTU mappings for `SCN-PILOT-001..003` are present and loadable.

## Open items before live unattended go/no-go

- Execute full VPS-hosted supervised run using scheduler wrapper in target environment.
- Capture real overnight artifacts (manifest, verdicts, telemetry) from VPS run window.
- Record operator timing from morning review template (<10 minute target).

## Recommendation

- Status: **Ready for tonight supervised VPS test run**.
- Not yet ready for unattended go/no-go (`T096`) until VPS supervised execution evidence is collected.
