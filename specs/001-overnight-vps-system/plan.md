# Implementation Plan: Overnight VPS Coding System

**Branch**: `001-overnight-vps-system` | **Date**: 2026-04-07 | **Spec**: `/specs/001-overnight-vps-system/spec.md`
**Input**: Feature specification from `/specs/001-overnight-vps-system/spec.md`

## Summary

Deliver a production-shaped overnight coding trial system on a Linux VPS that combines a runtime
orchestrator, enforceable guardrails, immutable external outcome-based judging, DTU-backed
validation, and cross-run memory plus telemetry. This plan uses existing stack decisions from
Quint (`.quint/decisions/dec-20260406-001` through `dec-20260407-003`) and research synthesis in
`Research/Research_Summary_Table.md`.

## Technical Context

**Language/Version**: Python 3.12+ (core scripts), Bash (run orchestration scripts)
**Primary Dependencies**: Ralph orchestrator, NTM, WireMock, OpenJudge (`py-openjudge`), Langfuse/OpenLLMetry, mcp-memory-service, Docker/Podman, Doppler
**Storage**: Git-tracked manifests plus local files; memory store (sqlite_vec); trace/event logs
**Testing**: pytest + contract/integration scenario tests + runbook validation checks
**Target Platform**: Linux VPS (Hetzner-class baseline) with unattended overnight execution
**Project Type**: Automation platform / CLI-driven orchestration system
**Performance Goals**: complete nightly run window with reproducible scenario verdicts; reviewer completes run triage in <10 minutes
**Constraints**: safety-first command interception, immutable judge path, DTU-first dependency validation, constrained VPS resources, budget-capped model calls
**Scale/Scope**: single-operator pilot moving toward repeatable V1 process across multiple scenarios

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Code quality gate: Define lint/format/static checks for each touched component; fail build on
  unexplained warnings. **PASS (planned)**.
- Testing gate: Require test evidence per story (US1 safety, US2 judging, US3 DTU/memory).
  **PASS (planned)**.
- UX consistency gate: Normalize run statuses, verdict labels, and error reason taxonomies in
  reviewer artifacts. **PASS (planned)**.
- Performance gate: Set run-window budget and review-time budget, with explicit measurement in
  quickstart validation. **PASS (planned)**.
- Observability and rollback gate: Define trace/log requirements and rollback triggers for each
  pillar integration. **PASS (planned)**.

No constitution violations currently require exception handling.

## Project Structure

### Documentation (this feature)

```text
specs/001-overnight-vps-system/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── run-manifest.schema.json
│   └── judge-verdict.schema.json
└── tasks.md
```

### Source Code (repository root)

```text
.specify/
.quint/
Research/
docs/superpowers/pilot/
  ├── dtu/
  ├── judge/
  ├── memory/
  ├── model-provider/
  ├── observability/
  ├── sandbox/
  ├── secrets/
  └── artifact-registry/
```

**Structure Decision**: Use existing pilot + Quint documentation layout and introduce plan-local
contracts for run manifest and judge verdict schemas. Implementation work remains aligned to the
already-decided pillar directories in `docs/superpowers/pilot/`.

## Phase 0: Research and Decision Consolidation

Research output is documented in `research.md` and resolves all planning unknowns by adopting
existing decisions:

- Orchestrator: Ralph (`dec-20260406-001`)
- Guardrails: NTM (documented in `DECISIONS.md`)
- DTU: WireMock (`dec-20260406-002`)
- Judge: OpenJudge (`dec-20260406-003`)
- Observability: Langfuse phased + OpenLLMetry (`dec-20260406-004`)
- Planner: Spec Kit (`dec-20260406-005`)
- Model/provider: OpenRouter-first policy adapter (`dec-20260406-006`)
- Memory: mcp-memory-service sqlite_vec-first (`dec-20260406-007`)
- Sandbox: OCI offline/online profiles (`dec-20260407-001`)
- Secrets: Doppler service-token flow (`dec-20260407-002`)
- Artifact registry: Git-native manifests + trace pointers (`dec-20260407-003`)

## Phase 1: Design Artifacts

1. **Data model** (`data-model.md`)
   - Run Session, Guardrail Policy, Scenario, Verdict, DTU Artifact, Memory Record,
     Telemetry Event, Run Manifest with validation rules and lifecycle transitions.

2. **Contracts** (`contracts/`)
   - `run-manifest.schema.json`: canonical run output metadata contract.
   - `judge-verdict.schema.json`: immutable judge output structure contract.

3. **Quickstart** (`quickstart.md`)
   - Trial execution path from setup to overnight run to morning review.
   - Includes constitution checks and success criteria measurement.

4. **Agent context refresh**
   - Run `.specify/scripts/bash/update-agent-context.sh cursor-agent`.

## Post-Design Constitution Re-Check

- Code quality gate: design includes explicit lint/test ownership by component. **PASS**
- Testing gate: each story maps to independent validation flow in quickstart. **PASS**
- UX consistency gate: common run/verdict terminology codified in contracts + quickstart. **PASS**
- Performance gate: measurable run-window and review-time criteria captured. **PASS**
- Observability/rollback gate: telemetry requirements and fallback paths documented. **PASS**

## Complexity Tracking

No constitution violations or complexity exceptions required at planning stage.
