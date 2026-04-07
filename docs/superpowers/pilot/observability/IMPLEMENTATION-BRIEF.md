# Observability (CXDB) Implementation Brief

Decision reference: `dec-20260406-004`  
Selected approach: **Langfuse self-hosted** with **phased deployment**; instrumentation via **OpenLLMetry** (OpenTelemetry-standard)  
Context: overnight-pilot

## Goal

Give morning review **LLM-aware traces**: per-call tokens/cost, session grouping, and (in Phase 2) a UI for filtering and annotation — **without** starving the pilot agent on a 4 GB VPS and **without** Langfuse-specific SDK lock-in in application code.

## Phased strategy

| Phase | Infra | Morning review | Notes |
|-------|--------|----------------|--------|
| **1** | No Langfuse on pilot VPS | OTEL spans to **files** (e.g. `traces/*.otel.jsonl`) | OpenLLMetry SDK + `@tool` style decorators for shell/git; content tracing on |
| **2** | Langfuse **self-hosted** on adequate RAM (≥4 GB for stack, separate or upgraded host) | Langfuse UI + replay/import of pilot traces | Same instrumentation; switch exporter endpoint |

**Hard rule:** Do **not** run the full Langfuse stack on the **same** 4 GB box as the agent during Phase 1 (`dec-20260406-004` admissibility).

## Scope

**In scope**

- Install **traceloop-sdk** (OpenLLMetry) / OTEL pipeline per plan runbook.
- Auto-instrument LLM calls; explicit spans for high-value tools (shell, git) as decided in pilot tasks.
- **Self-hosted only** — no Langfuse Cloud as the trace sink if that violates CONSTRAINTS.md.
- Document where JSONL (or OTLP files) land and retention/lifecycle.

**Out of scope**

- Using Langfuse built-in LLM-as-judge as **authoritative** — OpenJudge remains authority; any Langfuse eval is **supplementary** only if explicitly agreed.

## Invariants (from decision)

- Observability is **read-path only** — must not change agent correctness or timing.
- Application code uses **OTEL-standard** instrumentation so the backend can be swapped (Langfuse, Jaeger, Tempo, file).
- Trace data stays on **self-hosted** infrastructure you control.

## Checklist

**Phase 1**

1. Dependencies installed; pilot run produces **parseable** OTEL JSONL with prompts/responses and token counts.
2. Measure **disk per overnight run** for sizing Phase 2.
3. Confirm Ralph + WireMock + judge still fit RAM/CPU alongside file export.

**Phase 2**

4. Deploy Langfuse (Postgres, ClickHouse, Redis, MinIO, worker — per upstream compose) on sized host.
5. Point OTEL exporter at Langfuse ingest; verify span shape and **USD cost** display for your provider.
6. Time-box **2-minute** morning review drill on a failed scenario.
7. Record conscious decision if deferring Phase 2 (avoid silent “files forever” without Quint note).

## Rollback

Stop Langfuse containers; keep OpenLLMetry and send OTLP to **file**, **Jaeger**, or **Tempo**. Data remains OTEL-shaped. Update `DECISIONS.md` if backend changes.

## Links

- Langfuse docs: https://langfuse.com/docs  
- OpenLLMetry: project docs for `traceloop-sdk` / OTEL gen-ai instrumentation  
- Full decision: `.quint/decisions/dec-20260406-004.md`
