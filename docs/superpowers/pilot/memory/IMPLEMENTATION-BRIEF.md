# Memory Pillar Implementation Brief

Decision reference: `dec-20260406-007`  
Selected approach: **mcp-memory-service (sqlite_vec-first)**  
Context: overnight-pilot

## Goal

Implement a durable, local-first memory layer that:

- improves cross-run continuity (fewer repeated mistakes and setup rework)
- supports explicit read/write and retrieval during overnight runs
- remains auditable in morning review
- stays within solo-operator operational limits

This layer must **not** replace orchestration (Ralph) or decision authority.

## Scope

**In scope**

- Minimal deployment: **sqlite_vec** backend only for v1 baseline
- Memory write/read policy (what gets stored, when, and retention)
- Integration touchpoints with existing pilot flow (orchestrator, judge, planner artifacts as inputs only)
- Backup, restore, and migration notes
- Evidence capture for `dec-20260406-007`

**Out of scope (defer)**

- Hybrid/cloud backends until local profile is stable
- Full multi-tenant or remote MCP production hardening
- Replacing Quint or OpenJudge with memory-driven “truth”

## 1) Minimal sqlite_vec deployment profile

- Install and run **mcp-memory-service** in local mode with **sqlite_vec** only.
- Document: install command, env vars, data directory path, and how the overnight host starts/stops the service.
- **Acceptance:** service starts headlessly; no cloud credentials required for baseline.

## 2) Memory contract (write/read policy)

Define and document:

- **Namespaces or tags** (e.g. `pilot`, `scenario_id`, `run_id`, `component:ralph|judge|planner`)
- **What to store:** failures, fixes, env quirks, DTU URLs, one-line “do not repeat” learnings
- **What not to store:** secrets, full prompts with PII, unbounded raw logs
- **Retention:** max age or max rows policy; compaction or export strategy

**Acceptance:** policy is written in one place and referenced from the runbook.

## 3) Workflow integration points

Specify **when** memory is read and written in the overnight loop, for example:

- **Before run:** load relevant tags for scenario + repo
- **After failure:** write structured learning entry
- **After judge verdict:** optional summary memory entry (non-authoritative vs judge JSON)
- **Morning review:** human can list/search recent memories for the scenario

**Acceptance:** at least three concrete hooks are documented (read start, write on failure, read before retry branch).

## 4) Observability alignment

Ensure memory operations do not break existing tracing:

- log or trace memory read/write counts and latency (if your stack supports it)
- avoid silent failures; surface memory errors to orchestrator stop conditions where appropriate

**Acceptance:** one overnight run log shows memory operations or explicit “memory disabled” reason.

## 5) Backup and restore

- Document **backup** path (copy DB + config) and **restore** drill.
- Run one **restore test** on a copy of data before claiming production readiness.

**Acceptance:** backup + restore drill completed; integrity check documented.

## 6) Evidence checklist (maps to decision)

Complete and record results for `dec-20260406-007`:

- [ ] Reduced repeated failure or setup rework in at least one trial scenario vs baseline
- [ ] Retrieval latency and success rate measured under pilot workload
- [ ] Backup + restore drill passed
- [ ] Integration effort measured (actual hours)
- [ ] Controlled outage/failure simulation; graceful degradation documented

**Artifacts:** trial notes, metrics table, backup/restore log, outage drill notes.

## Rollback (if triggers fire)

Per `dec-20260406-007`:

1. **Primary fallback:** pivot to **Acontext** skill-file memory (preserve exports).
2. Optionally use **Beads** as **execution/work graph** memory alongside whichever long-term memory wins.
3. Update `DECISIONS.md` and runbooks; re-run evidence requirements.

## Done criteria

This brief is complete when:

- sqlite_vec-only profile is running on the pilot path
- policy + integration hooks + backup/restore are documented
- all five evidence requirements are satisfied or explicitly deferred with rationale
