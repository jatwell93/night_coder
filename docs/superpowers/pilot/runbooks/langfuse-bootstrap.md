# Langfuse Bootstrap (Phase 2) (T091)

Deploy and wire self-hosted Langfuse for Phase 2 observability.

---

## 1) Purpose

Move from Phase 1 file-based OTEL traces to Phase 2 Langfuse ingest/UI while keeping instrumentation OTEL-standard.

---

## 2) Preconditions

- Phase 1 OTEL file export is operational (`T090`).
- Host sizing is adequate for Langfuse stack (recommended dedicated host or upgraded VPS).
- Operator has approved self-hosted deployment for pilot phase 2.

---

## 3) Deployment notes

Use the official self-hosted Langfuse stack with:

- Postgres
- ClickHouse
- Redis
- MinIO
- Langfuse API/Web + worker

Do **not** co-locate full Langfuse stack on the same constrained host as the overnight agent unless capacity has been validated.

---

## 4) OTLP wiring contract

When Phase 2 is enabled, OTEL exporter should target:

- OTLP HTTP endpoint, for example:
  - `http://<langfuse-host>:4318/v1/traces`

`src/lib/otel_setup.py` controls the phase-based exporter configuration.

---

## 5) Smoke verification

1. Start Langfuse stack and confirm all containers healthy.
2. Send one synthetic OTEL span to the configured endpoint.
3. Verify trace appears in Langfuse UI.
4. Validate token/cost metadata fields appear for pilot LLM calls.

---

## 6) Rollback path

If Phase 2 deployment is unstable:

1. Switch exporter phase back to `phase1`.
2. Resume file-based trace export.
3. Keep Langfuse stack offline until sizing/ops issues are resolved.

---

## 7) Validation checklist

- [ ] Langfuse services healthy.
- [ ] OTLP ingest endpoint reachable from overnight runtime host.
- [ ] Pilot run spans visible in UI.
- [ ] Morning review drill completed using Langfuse traces.
- [ ] Rollback to phase1 file exporter tested.

---

## 8) References

- `docs/superpowers/pilot/observability/IMPLEMENTATION-BRIEF.md`
- `src/lib/otel_setup.py`
- `specs/001-overnight-vps-system/tasks.md` (`T091`)
