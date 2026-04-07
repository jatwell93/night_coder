# Artifact Registry — Research Report

**Question:** Where should plans, prompts, traces, verdicts, and run outputs live so they are indexed and queryable?

## Answer

- **Split metadata vs blobs:** Follow MLOps pattern — **small structured metadata** (IDs, SHAs, tags, URIs) in something queryable; **large payloads** in object storage or DVC/LFS remotes. [MLflow artifact stores](https://mlflow.org/docs/latest/tracking/artifacts-stores) document the same split.
- **Pilot-minimal:** **Git + conventions** under e.g. `runs/<date>/<run_id>/` with `manifest.json`, `plan.md`, `verdict.md`, `summary.json`; large traces via **DVC** or **MinIO/S3** URIs in the manifest only. Human query: `git log`, `rg`. **Langfuse** (Observability) owns **LLM runtime traces**; registry owns **durable, reviewable** plans/verdicts and run manifests.
- **v1:** Add **SQLite** or small **Postgres** catalog (`runs`, `artifacts` with `uri`, `sha256`) plus blob tier; optional **DuckDB/DuckLake** for analytics. Avoid duplicating Langfuse’s trace UI unless you need a second source of truth.

## Sources

Findings: [`findings_registry.md`](findings_registry.md) — MLflow, DVC, [Langfuse data model](https://langfuse.com/docs/observability/data-model), [DuckLake](https://ducklake.select/), OpenTelemetry GenAI conventions.

## Gaps

Exact directory layout should align with existing `docs/superpowers/pilot/` artifacts and Quint problem IDs.
