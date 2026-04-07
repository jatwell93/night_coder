# Phase 0 Research: Overnight VPS Coding System

## Decision: Keep Quint-selected pillar stack as implementation baseline

**Rationale**: The project already completed full comparison cycles with decisions, implementation
briefs, and refreshed documentation. Reopening core tool choices now would delay trial execution
without adding immediate risk reduction.

**Alternatives considered**:
- Re-run tool selection for all pillars: rejected (duplication, low incremental value).
- Simplify to fewer pillars: rejected (would remove anti-reward-hacking and safety controls).

## Decision: Use Ralph + NTM as orchestration and safety runtime boundary

**Rationale**: Ralph provides unattended orchestration control loops; NTM provides command-level
interception and audit trail needed for unattended safety.

**Alternatives considered**:
- Prompt-only safeguards: rejected (insufficient enforcement depth).
- Orchestrator-coupled safety only: rejected (reduced composability/traceability).

## Decision: Externalize acceptance to OpenJudge with scenario-based verdicts

**Rationale**: Outcome-focused evaluation from immutable harness prevents reward-hacking and aligns
pass/fail with user outcomes rather than process completion.

**Alternatives considered**:
- Agent self-report as acceptance: rejected (not trustworthy).
- Generic app platforms for judging: rejected (heavy and mis-scoped).

## Decision: Use WireMock-backed DTU for repeatable external dependency behavior

**Rationale**: Containerized mock layer enables 24/7 validation without live dependency variance
or billing pressure.

**Alternatives considered**:
- Live dependencies in overnight runs: rejected (cost/flakiness/rate limits).
- In-process-only mocks: rejected (insufficient parity for unattended system-level checks).

## Decision: Use memory plus telemetry as a continuous improvement loop

**Rationale**: mcp-memory-service reduces repeated failures; OpenLLMetry/Langfuse enables forensic
review and measurable run quality improvement.

**Alternatives considered**:
- Logs only, no memory: rejected (repetition and weak adaptation).
- Memory only, no telemetry: rejected (insufficient diagnosis and confidence).

## Decision: Keep unresolved unknowns at zero for plan phase

All major ambiguities were resolved by existing decisions and documents:
- `.quint/decisions/*.md`
- `docs/superpowers/pilot/DECISIONS.md`
- `Research/Research_Summary_Table.md`

No `NEEDS CLARIFICATION` items remain for design artifact generation.
