# Tasks: Overnight VPS Coding System

**Input**: Design documents from `/specs/001-overnight-vps-system/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story includes automated validation evidence.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [USER?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[USER]**: Requires human/user action (accounts, billing, credentials, external approvals, provider console operations)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## User-Required Setup Tasks

These tasks must be performed (or explicitly approved) by the user and cannot be fully automated by an AI coding agent:

- **T055 [USER]**: Provision VPS provider instance, account/billing, network/security baseline, and operator access.
- **T059 [USER]**: Create Doppler org/project/service token and approve secret-scope policy.
- **T062 [USER]**: Approve external scenario catalog host/repo location and access control boundary.

### USER/Agent Handoff Details

#### T055 [USER] VPS Provisioning
- **User actions**
  - Create/confirm VPS provider account, billing, and region.
  - Provision instance size/image and attach SSH key.
  - Approve baseline network policy (firewall/security group ports).
- **Agent follow-up**
  - Verify SSH connectivity and capture host bootstrap commands.
  - Apply OS hardening steps and non-root operator setup in runbook.
  - Record reproducible bootstrap script snippets in `docs/superpowers/pilot/runbooks/vps-bootstrap.md`.

#### T059 [USER] Doppler Access and Token
- **User actions**
  - Create Doppler project/environment and minimal-scope service token.
  - Decide ownership/rotation policy and approve secret scope.
  - Provide token through secure local injection path (never commit token).
- **Agent follow-up**
  - Implement `doppler run` integration in run scripts.
  - Add startup checks for required secret keys and missing-secret failure messages.
  - Document rotation/update procedure in `docs/superpowers/pilot/runbooks/vps-secrets-bootstrap.md`.

#### T062 [USER] External Scenario Catalog Boundary
- **User actions**
  - Choose scenario storage location (separate repo/path) outside coding-agent writable scope.
  - Set read/write permissions so coding agent cannot modify scenario source of truth.
  - Approve change-control policy for scenario updates.
- **Agent follow-up**
  - Wire read-only mount/path usage into scenario loader and validation flow.
  - Add immutability boundary checks in integration tests.
  - Document catalog structure and update process in `docs/superpowers/pilot/runbooks/scenario-catalog.md`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature-level artifacts and quality baseline.

- [x] T055 [USER] Provision VPS baseline (provider instance, SSH hardening, firewall, non-root operator) in `docs/superpowers/pilot/runbooks/vps-bootstrap.md`
- [x] T056 Install runtime prerequisites (Python 3.12+, git, tmux, curl, jq) and record commands in `docs/superpowers/pilot/runbooks/vps-bootstrap.md`
- [x] T057 Install and validate container runtime (Docker/Podman rootless profile) in `docs/superpowers/pilot/runbooks/vps-container-runtime.md`
- [x] T058 Install Ralph orchestrator and verify CLI health checks in `docs/superpowers/pilot/runbooks/vps-ralph-install.md`
- [ ] T059 [USER] Configure Doppler service-token injection flow for run environment in `docs/superpowers/pilot/runbooks/vps-secrets-bootstrap.md`
- [ ] T060 [P] Install and smoke-test DTU/judge dependencies (WireMock, OpenJudge, Langfuse/OpenLLMetry hooks) in `docs/superpowers/pilot/runbooks/vps-dependency-smoke-tests.md`
- [ ] T061 Configure NTM guardrail runtime and baseline policies on VPS in `docs/superpowers/pilot/runbooks/vps-guardrails-bootstrap.md`
- [ ] T062 [USER] Define external read-only scenario catalog location and access boundaries in `docs/superpowers/pilot/runbooks/scenario-catalog.md`
- [ ] T063 Configure unattended scheduler (systemd timer/cron) for overnight run windows in `docs/superpowers/pilot/runbooks/vps-scheduler.md`
- [ ] T001 Create runtime documentation skeleton in `docs/superpowers/pilot/runbooks/README.md`
- [ ] T002 Create trial configuration directory in `docs/superpowers/pilot/config/README.md`
- [ ] T003 [P] Create testing directory placeholders in `tests/unit/.gitkeep`
- [ ] T004 [P] Create testing directory placeholders in `tests/integration/.gitkeep`
- [ ] T005 [P] Create testing directory placeholders in `tests/contract/.gitkeep`
- [ ] T006 Configure quality check script reference in `docs/superpowers/pilot/runbooks/quality-gates.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core contracts and shared utilities required before any user-story delivery.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Define canonical run status taxonomy in `docs/superpowers/pilot/runbooks/status-taxonomy.md`
- [ ] T008 Define shared reason-code taxonomy for guardrails and judge in `docs/superpowers/pilot/runbooks/reason-codes.md`
- [ ] T009 Implement run manifest schema validator in `src/lib/manifest_validation.py`
- [ ] T010 Implement judge verdict schema validator in `src/lib/verdict_validation.py`
- [ ] T011 [P] Implement artifact path resolver utility in `src/lib/artifact_paths.py`
- [ ] T012 [P] Implement run id and timestamp utility in `src/lib/run_identity.py`
- [ ] T013 Implement structured event envelope utility in `src/lib/event_envelope.py`
- [ ] T049 [P] Add unit test for model role-policy adapter with fallback in `tests/unit/test_model_policy_adapter.py`
- [ ] T050 Implement model/provider role-policy adapter with fallback handling in `src/services/model_policy_service.py`
- [ ] T064 [P] Add unit test for telemetry/trace secret redaction rules in `tests/unit/test_secret_redaction.py`
- [ ] T065 Implement shared secret redaction filter for logs/traces/events in `src/lib/secret_redaction.py`
- [ ] T014 Configure feature-level quality and test command matrix in `docs/superpowers/pilot/runbooks/verification-matrix.md`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Safe Overnight Execution (Priority: P1) 🎯 MVP

**Goal**: Run unattended sessions safely with enforceable guardrails and reviewable blocked-action evidence.

**Independent Test**: Start an unattended run with guardrails enabled and confirm blocked dangerous commands are denied while allowed commands proceed.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T015 [P] [US1] Add contract test for blocked-action event payload in `tests/contract/test_guardrail_event_contract.py`
- [ ] T016 [P] [US1] Add integration test for guarded unattended run path in `tests/integration/test_guarded_overnight_run.py`
- [ ] T017 [P] [US1] Add integration test for offline/online profile enforcement in `tests/integration/test_execution_profiles.py`
- [ ] T051 [P] [US1] Add integration test for orchestrator iteration loop with satisfaction-based termination in `tests/integration/test_orchestrator_iteration_loop.py`

### Implementation for User Story 1

- [ ] T018 [P] [US1] Implement guardrail policy loader in `src/services/guardrail_policy_service.py`
- [ ] T019 [P] [US1] Implement blocked-command interception adapter in `src/services/guardrail_enforcement_service.py`
- [ ] T020 [US1] Implement unattended run launcher workflow in `src/cli/run_overnight.py`
- [ ] T021 [US1] Implement run lifecycle state transitions in `src/services/run_session_service.py`
- [ ] T022 [US1] Implement blocked-action logging with reason codes in `src/services/guardrail_audit_service.py`
- [ ] T023 [US1] Wire profile selection (`offline` default) in `src/services/run_profile_service.py`
- [ ] T052 [US1] Implement orchestrator iteration controller with satisfaction-based loop termination in `src/services/orchestrator_loop_service.py`
- [ ] T024 [US1] Document US1 operator flow in `docs/superpowers/pilot/runbooks/us1-safe-execution.md`

**Checkpoint**: User Story 1 should be fully functional and independently testable.

---

## Phase 4: User Story 2 - External Outcome-Based Judging (Priority: P2)

**Goal**: Evaluate run outcomes via immutable external harness with scenario-based verdicts.

**Independent Test**: Execute a scenario where process completes but user outcome is wrong and verify unsatisfactory verdict with evidence.

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T025 [P] [US2] Add contract test for judge verdict schema compliance in `tests/contract/test_judge_verdict_contract.py`
- [ ] T026 [P] [US2] Add integration test for immutable judge harness boundary in `tests/integration/test_judge_immutability_boundary.py`
- [ ] T027 [P] [US2] Add integration test for outcome-based unsatisfactory verdict path in `tests/integration/test_outcome_based_judging.py`
- [ ] T066 [P] [US2] Add integration test for judge-unavailable fallback to `evaluation-pending` in `tests/integration/test_judge_unavailable_fallback.py`

### Implementation for User Story 2

- [ ] T028 [P] [US2] Implement scenario evidence assembler in `src/services/scenario_evidence_service.py`
- [ ] T029 [P] [US2] Implement external judge invocation wrapper in `src/services/judge_runner_service.py`
- [ ] T030 [US2] Implement verdict persistence workflow in `src/services/judge_verdict_service.py`
- [ ] T031 [US2] Implement immutable harness path guard in `src/services/judge_harness_guard_service.py`
- [ ] T032 [US2] Integrate verdict generation into run completion pipeline in `src/services/run_completion_service.py`
- [ ] T067 [US2] Implement judge-unavailable fallback handler setting run state to `evaluation-pending` in `src/services/judge_fallback_service.py`
- [ ] T033 [US2] Document US2 reviewer flow in `docs/superpowers/pilot/runbooks/us2-outcome-judging.md`

**Checkpoint**: User Stories 1 and 2 both operate independently with trustworthy verdict outputs.

---

## Phase 5: User Story 3 - Continuous Validation with DTU and Memory (Priority: P3)

**Goal**: Enable repeatable DTU-backed validation and memory-assisted reduction of repeated failures.

**Independent Test**: Run repeated validations against DTU and verify memory retrieval reduces repeated failure loops.

### Tests for User Story 3 (REQUIRED) ⚠️

- [ ] T034 [P] [US3] Add contract test for run manifest schema compliance in `tests/contract/test_run_manifest_contract.py`
- [ ] T035 [P] [US3] Add integration test for DTU-only validation execution in `tests/integration/test_dtu_validation_cycle.py`
- [ ] T036 [P] [US3] Add integration test for memory retrieval reducing repeated failures in `tests/integration/test_memory_feedback_loop.py`
- [ ] T053 [P] [US3] Add integration test for morning review report assembly from telemetry and verdicts in `tests/integration/test_morning_review_report.py`
- [ ] T068 [P] [US3] Add integration test for DTU-startup failure classification as infrastructure failure in `tests/integration/test_dtu_startup_failure.py`
- [ ] T069 [P] [US3] Add integration test for stale-memory relevance filtering in `tests/integration/test_memory_relevance_filter.py`
- [ ] T070 [P] [US3] Add integration test for partial telemetry capture on failed runs in `tests/integration/test_partial_telemetry_failed_run.py`

### Implementation for User Story 3

- [ ] T037 [P] [US3] Implement DTU dependency readiness checker in `src/services/dtu_health_service.py`
- [ ] T038 [P] [US3] Implement DTU-backed scenario executor in `src/services/dtu_validation_service.py`
- [ ] T039 [P] [US3] Implement memory retrieval and writeback orchestration in `src/services/memory_feedback_service.py`
- [ ] T040 [US3] Implement telemetry event publisher for execution/safety/judge/memory in `src/services/telemetry_service.py`
- [ ] T041 [US3] Implement run manifest builder and writer in `src/services/run_manifest_service.py`
- [ ] T042 [US3] Link telemetry, memory, and manifest steps into end-of-run workflow in `src/services/run_finalize_service.py`
- [ ] T054 [US3] Implement morning review report assembler in `src/services/morning_review_service.py`
- [ ] T071 [US3] Implement scenario catalog loader with read-only boundary enforcement in `src/services/scenario_catalog_service.py`
- [ ] T072 [US3] Implement memory relevance and staleness filtering before writeback/reuse in `src/services/memory_relevance_service.py`
- [ ] T043 [US3] Document US3 continuous validation flow in `docs/superpowers/pilot/runbooks/us3-dtu-memory-loop.md`

**Checkpoint**: All user stories are independently functional and traceable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening and end-to-end verification across stories.

- [ ] T044 [P] Consolidate overnight trial runbook in `docs/superpowers/pilot/runbooks/trial-e2e.md`
- [ ] T045 [P] Add troubleshooting matrix for failure modes in `docs/superpowers/pilot/runbooks/troubleshooting.md`
- [ ] T046 Validate performance budget and review-time targets in `tests/integration/test_trial_performance_budgets.py`
- [ ] T047 Validate quickstart end-to-end flow in `specs/001-overnight-vps-system/quickstart.md`
- [ ] T048 Run full verification matrix and record outcomes in `docs/superpowers/pilot/runbooks/verification-results.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (including VPS bootstrap T055-T060) - blocks all user stories
- **User Story Phases (Phase 3-5)**: Depend on Foundational completion
  - US1 is MVP-first and should be completed first
  - US2 and US3 can start after foundation, but US2 should precede full US3 trial closure
- **Polish (Phase 6)**: Depends on target user stories completed

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories. T052 (iteration controller) depends on T020 (launcher), T021 (state transitions), and uses US2 verdict outputs as the satisfaction signal for loop termination.
- **US2 (P2)**: Depends on US1 run lifecycle outputs for scenario evidence and run completion hooks
- **US3 (P3)**: Depends on US1 run flow and US2 verdict outputs for complete manifest and telemetry closure. T054 (morning review assembler) depends on T040 (telemetry), T041 (manifest), and US2 verdict outputs. T071 depends on setup task T062 (external scenario catalog boundary).

### Within Each User Story

- Tests MUST be written and fail before implementation
- Contract/integration tests before service wiring
- Core service logic before CLI/workflow integration
- Documentation updates after implementation and tests pass

### Parallel Opportunities

- Setup placeholders and docs tasks marked [P] can run in parallel
- Platform bootstrap T060 can run in parallel once T055-T059 complete
- Bootstrap tasks T061-T063 can proceed in parallel after base VPS provisioning T055
- Foundational utility services T011 and T012 can run in parallel
- Contract and integration tests within each story marked [P] can run in parallel
- Core service tasks marked [P] in each story can be split across contributors

---

## Parallel Example: User Story 2

```bash
# Run US2 tests in parallel:
Task: "T025 [US2] tests/contract/test_judge_verdict_contract.py"
Task: "T026 [US2] tests/integration/test_judge_immutability_boundary.py"
Task: "T027 [US2] tests/integration/test_outcome_based_judging.py"

# Build US2 services in parallel:
Task: "T028 [US2] src/services/scenario_evidence_service.py"
Task: "T029 [US2] src/services/judge_runner_service.py"
Task: "T031 [US2] src/services/judge_harness_guard_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete all US1 tests and implementation tasks
3. Validate guarded unattended run behavior
4. Stop and review MVP readiness

### Incremental Delivery

1. Deliver US1 safe unattended execution
2. Add US2 external judging and immutability boundary
3. Add US3 DTU + memory + telemetry feedback loop
4. Finish Phase 6 cross-cutting validation

### Parallel Team Strategy

1. One owner completes foundational shared utilities
2. Once foundation is complete:
   - Engineer A: US1
   - Engineer B: US2
   - Engineer C: US3
3. Rejoin for integration and polish tasks

---

## Notes

- All tasks follow required checklist format with task id, optional [P], optional [USx], and file path.
- Story phases are independently testable and map directly to spec priorities.
- Suggested MVP scope is **Phase 1 + Phase 2 + Phase 3 (US1)**.
