# Artifact Registry Implementation Brief

Decision reference: `dec-20260407-003`  
Selected approach: **Git-native run manifests (pilot) + Langfuse for LLM traces**  
Research: [`research_artifact_registry/`](../../../../research_artifact_registry/) (plan, findings, report)

## Goal

Make overnight outputs **discoverable for morning review** without standing up a second observability platform. **Langfuse** remains the source of truth for LLM/runtime traces; git holds durable, reviewable **plans**, **verdicts**, and **summaries**.

## Scope

**In scope**

- Directory convention under `docs/superpowers/pilot/` (or successor), e.g. `runs/<YYYY-MM-DD>/<run_id>/`.
- Required files: `manifest.json` (run id, timestamps, git SHA, tags, URIs to large blobs), `verdict.md` or pointer to judge output, `summary.json` (pass/fail, key metrics).
- Large artifacts: **only** pointers in manifest (S3/MinIO/DVC); no multi-megabyte traces in plain git.
- One example run committed or documented external path + schema for `manifest.json`.

**Out of scope (defer)**

- **SQLite/Postgres catalog** until grep/git log is painful (`dec-20260407-003` stepping stone).
- **MLflow-style tracking server** as default.

## Split of concerns

| Concern | Where it lives |
|--------|----------------|
| LLM spans, token/cost, session drill-down | Langfuse (`dec-20260406-004`) |
| Plan text, verdict narrative, run manifest | Git (this pillar) |
| Large stdout bundles, raw trace exports | Object storage or DVC; URI in manifest |

## Checklist

1. Agree path layout and `manifest.json` schema (even minimal JSON Schema in repo).
2. Wire one pilot job to emit manifest + verdict path after run.
3. Document morning review: `git log -- runs/`, `rg`, links to Langfuse session id in manifest.

## Rollback

Stop writing manifests; rely on ad hoc logs (only if convention blocks velocity).
