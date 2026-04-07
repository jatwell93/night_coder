# Artifact Registry Pillar — Research Plan

## Question
Where should plans, prompts, traces, verdicts, and run outputs live so they are indexed and queryable for morning review and v1 scale?

## Subtopics
1. **Git-native** — branches, tags, structured dirs, LFS.
2. **Light registries** — SQLite/duckdb index, local object store, MinIO.
3. **Observability overlap** — Langfuse + files vs dedicated registry.

## Synthesis
Pilot-minimal vs v1 registry pattern; avoid duplicating Langfuse’s role.
