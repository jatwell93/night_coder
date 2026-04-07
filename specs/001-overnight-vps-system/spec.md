# Feature Specification: Overnight VPS Coding System

**Feature Branch**: `001-overnight-vps-system`  
**Created**: 2026-04-07  
**Status**: Draft  
**Input**: User description: "Using research and pilot docs, define an overnight coding system on VPS with orchestrator, leash/guardrails, immutable external LLM judge for real user outcomes, DTU mocks, and memory plus telemetry."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Safe Overnight Execution (Priority: P1)

As an operator, I can run unattended overnight coding sessions on a VPS with enforced guardrails,
so autonomous work can proceed without damaging the project or environment.

**Why this priority**: No unattended system is viable unless safety controls reliably prevent harmful actions.

**Independent Test**: Run one unattended session with a policy profile, verify blocked dangerous actions are denied and allowed actions still proceed.

**Acceptance Scenarios**:

1. **Given** an active guarded overnight run, **When** a prohibited destructive command is attempted, **Then** the command is denied, logged, and execution remains stable.
2. **Given** an active guarded overnight run, **When** approved coding operations are performed, **Then** tasks continue and produce reviewable run artifacts.

---

### User Story 2 - External Outcome-Based Judging (Priority: P2)

As a reviewer, I can evaluate run results using an external judge harness that the coding agent
cannot modify, so acceptance is based on user outcomes rather than superficial execution signals.

**Why this priority**: This prevents reward-hacking and keeps validation aligned to real outcomes.

**Independent Test**: Execute a scenario where the run technically completes but fails expected user outcome; verify the external judge returns unsatisfactory with rationale.

**Acceptance Scenarios**:

1. **Given** scenario definitions and execution evidence, **When** evaluation runs, **Then** the judge returns structured satisfactory/unsatisfactory verdicts with score and reasoning.
2. **Given** the coding agent has write access to project files, **When** an overnight run executes, **Then** judge harness artifacts remain unmodifiable by the agent path.

---

### User Story 3 - Continuous Validation with DTU and Memory (Priority: P3)

As an operator, I can validate repeatedly against digital twins and use run memory plus telemetry,
so the system improves reliability across nights instead of repeating the same failures.

**Why this priority**: Repeatability and cross-run learning are required to move from trial to V1.

**Independent Test**: Run multiple validations against DTU scenarios and verify repeated failure patterns decline when prior run memory is available.

**Acceptance Scenarios**:

1. **Given** DTU definitions for required dependencies, **When** scheduled validation runs execute, **Then** results are reproducible without relying on live external services.
2. **Given** memory from prior runs is stored, **When** similar failure conditions recur, **Then** relevant memory is retrieved and repeated setup/retry errors are reduced.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Guardrail policy blocks a command required for a legitimate task path.
- Judge service is temporarily unavailable during verdict generation.
- DTU for a dependency fails to start at run initialization.
- Memory retrieval returns stale or irrelevant context for current scenario.
- Telemetry capture is partial for a failed run and must still support review.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow an operator to define and launch unattended overnight coding runs on a VPS.
- **FR-002**: System MUST enforce guardrail policies that block destructive commands and unsafe execution patterns during runs.
- **FR-003**: System MUST record blocked actions with run identifier, attempted action, timestamp, and policy reason.
- **FR-004**: System MUST execute coding workflow through an orchestrated run sequence with explicit run boundaries.
- **FR-005**: System MUST evaluate outcomes using an external LLM-judge harness outside coding-agent modification scope.
- **FR-006**: Judge evaluation MUST be based on scenario-defined user outcomes, not only process completion.
- **FR-007**: System MUST support DTU-based simulation of external dependencies for repeatable validation.
- **FR-008**: System MUST persist and retrieve cross-run memory records relevant to scenarios and failures.
- **FR-009**: System MUST capture telemetry for run lifecycle, guardrail events, validation steps, and verdict outputs.
- **FR-010**: System MUST generate review artifacts sufficient for morning verdict and follow-up decisions.
- **FR-011**: System MUST support role-based model usage policy with fallback handling for run continuity.
- **FR-012**: System MUST preserve a reproducible manifest linking run context, scenario, verdict, and artifact references.

### Key Entities *(include if feature involves data)*

- **Run Session**: A single unattended execution attempt with identifiers, schedule window, and completion state.
- **Guardrail Policy**: A set of safety rules and outcomes describing allowed/blocked action classes.
- **Scenario Definition**: Outcome-focused criteria describing expected user-visible behavior.
- **Judge Verdict**: Structured evaluation record containing satisfactory status, score, rationale, and evidence links.
- **DTU Definition**: Simulated dependency configuration and behavior profile used in validation.
- **Memory Record**: Cross-run learning entry tagged by context, relevance, and reuse hints.
- **Telemetry Event**: Time-ordered event record for execution, safety, and evaluation activity.
- **Run Manifest**: Aggregated run summary linking scenario, outputs, verdict, and trace pointers.

### Non-Functional Requirements *(mandatory)*

- **NFR-001 (Code Quality)**: Changes MUST pass documented quality checks and include explicit justification for any accepted warning.
- **NFR-002 (Testing Standard)**: Each user story MUST include automated validation evidence proving independent behavior.
- **NFR-003 (UX Consistency)**: Status labels, review outputs, and failure messages MUST use consistent terminology and severity semantics.
- **NFR-004 (Performance)**: Standard overnight trial runs MUST complete within defined run windows and stay within planned resource budgets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 90% of scheduled overnight runs complete without manual intervention while preserving guardrail enforcement.
- **SC-002**: 100% of blocked high-risk command attempts are denied and recorded with actionable reason codes.
- **SC-003**: 100% of completed runs produce an external judge verdict mapped to scenario outcomes with reviewable rationale.
- **SC-004**: At least 85% of scenario validations run successfully against DTU dependencies without requiring live third-party services.
- **SC-005**: Repeated failure-loop incidents for previously seen conditions decrease by at least 30% after memory retrieval is enabled.
- **SC-006**: A reviewer can complete morning review for one run in under 10 minutes using produced artifacts.

## Assumptions

- A technical operator schedules and reviews overnight runs daily.
- Linux VPS infrastructure is available for unattended trial execution windows.
- Existing pilot decisions remain in force for orchestrator, guardrails, judge, DTU, observability, memory, and provider policy.
- Scenario definitions and DTU behavior profiles are authored before overnight trial execution.
- Budget limits and fallback policy are configured before production-like overnight schedules.
- V1 scope focuses on single-operator reliability before expanding to multi-operator governance.
