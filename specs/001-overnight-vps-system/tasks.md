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
- **T077 [USER]**: Approve model budget caps and fallback policy (financial/risk decision).
- **T078 [USER]**: Provide provider API credentials (OpenRouter / judge LLM / etc.) via Doppler — credential handling.
- **T079 [USER]**: Author and approve initial guardrail blocklist policy (security decision).
- **T083 [USER]**: Author first production scenario(s) (requires real product/domain judgement).
- **T087 [USER]**: Author first DTU behavior profile(s) (requires real dependency-behaviour knowledge).
- **T096 [USER]**: Execute go/no-go decision and enable scheduler for live unattended runs (deployment gate).

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

#### T077 [USER] Model Budget and Fallback Policy
- **User actions**
  - Decide per-run and nightly token/cost caps.
  - Decide fallback model order and degraded-mode behaviour.
  - Approve kill-switch thresholds for cost or rate-limit breaches.
- **Agent follow-up**
  - Encode budget caps into model policy adapter config.
  - Add breach detection and fail-safe shutdown paths.
  - Document policy in `docs/superpowers/pilot/runbooks/budget-policy.md`.

#### T078 [USER] Provider API Credentials
- **User actions**
  - Create/retrieve OpenRouter (and any fallback provider) API keys.
  - Store keys in Doppler project created in T059.
  - Approve which runs/environments may use which credential scopes.
- **Agent follow-up**
  - Reference credentials via Doppler in run scripts (no plaintext in repo).
  - Add startup credential validation with clear missing-key errors.
  - Document key rotation in the secrets runbook.

#### T079 [USER] Initial Guardrail Blocklist
- **User actions**
  - Review and approve the initial NTM blocklist entries.
  - Approve override/bypass procedure for legitimate operator intervention.
  - Sign off that offline/online profile patterns are acceptable.
- **Agent follow-up**
  - Encode approved patterns in `docs/superpowers/pilot/config/guardrail-policy.yaml`.
  - Wire policy loader (T018) to read from that path.
  - Add regression tests for approved blocklist entries.

#### T083 [USER] Initial Production Scenario Authoring
- **User actions**
  - Draft 3-5 outcome-based scenarios for the target feature/project.
  - Store under the external catalog location approved in T062.
  - Confirm scenarios are outside the coding agent's writable scope.
- **Agent follow-up**
  - Validate each scenario conforms to schema (title, outcomes, evidence, DTU deps).
  - Add scenario smoke-tests in integration suite.
  - Reference scenario IDs in quickstart and runbooks.

#### T087 [USER] Initial DTU Behaviour Profile(s)
- **User actions**
  - Identify which external dependencies need mocking for the first scenarios.
  - Draft WireMock (or equivalent) stub definitions with expected responses.
  - Approve fidelity vs minimal-mock trade-offs.
- **Agent follow-up**
  - Load DTU profiles in `src/services/wiremock_dtu_service.py`.
  - Add DTU health checks and startup validation.
  - Document profile update process.

#### T096 [USER] Go/No-Go for Live Unattended Runs
- **User actions**
  - Review supervised dry-run results (T095).
  - Confirm budget, guardrail, scenario, and DTU readiness.
  - Flip scheduler enable switch in the VPS scheduler runbook.
- **Agent follow-up**
  - Record go/no-go outcome and trigger timestamp.
  - Monitor first live run telemetry and report back next morning.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize feature-level artifacts and quality baseline.

> **Ordering:** **T055–T059** can be completed without a `night_coder` git checkout on the Droplet (Ralph installs from upstream; Doppler is account-side). **T060+** use repo files (for example `docs/superpowers/pilot/dtu/`). Before running T060, complete **`docs/superpowers/pilot/runbooks/vps-bootstrap.md` §12** (pilot repo clone on the VPS). If T056 was marked done before §12 existed, perform §12 as a catch-up step — no earlier task was wrong.

- [x] T055 [USER] Provision VPS baseline (provider instance, SSH hardening, firewall, non-root operator) in `docs/superpowers/pilot/runbooks/vps-bootstrap.md`
- [x] T056 Install runtime prerequisites (Python 3.12+, git, tmux, curl, jq); **clone this repo onto the VPS per `vps-bootstrap.md` §12** for pilot paths; record commands in `docs/superpowers/pilot/runbooks/vps-bootstrap.md`
- [x] T057 Install and validate container runtime (Docker/Podman rootless profile) in `docs/superpowers/pilot/runbooks/vps-container-runtime.md`
- [x] T058 Install Ralph orchestrator and verify CLI health checks in `docs/superpowers/pilot/runbooks/vps-ralph-install.md`
- [x] T059 [USER] Configure Doppler service-token injection flow for run environment in `docs/superpowers/pilot/runbooks/vps-secrets-bootstrap.md`
- [x] T060 [P] Install and smoke-test DTU/judge dependencies (WireMock, OpenJudge, Langfuse/OpenLLMetry hooks) in `docs/superpowers/pilot/runbooks/vps-dependency-smoke-tests.md` — **requires** `vps-bootstrap.md` §12 (repo checkout) and prior container-runtime / secrets runbooks
- [x] T061 Configure NTM guardrail runtime and baseline policies on VPS in `docs/superpowers/pilot/runbooks/vps-guardrails-bootstrap.md`
- [x] T062 [USER] Define external read-only scenario catalog location and access boundaries in `docs/superpowers/pilot/runbooks/scenario-catalog.md`
- [x] T063 Configure unattended scheduler (systemd timer/cron) for overnight run windows in `docs/superpowers/pilot/runbooks/vps-scheduler.md`
- [x] T001 Create runtime documentation skeleton in `docs/superpowers/pilot/runbooks/README.md`
- [x] T002 Create trial configuration directory in `docs/superpowers/pilot/config/README.md`
- [x] T003 [P] Create testing directory placeholders in `tests/unit/.gitkeep`
- [x] T004 [P] Create testing directory placeholders in `tests/integration/.gitkeep`
- [x] T005 [P] Create testing directory placeholders in `tests/contract/.gitkeep`
- [x] T006 Configure quality check script reference in `docs/superpowers/pilot/runbooks/quality-gates.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core contracts and shared utilities required before any user-story delivery.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Define canonical run status taxonomy in `docs/superpowers/pilot/runbooks/status-taxonomy.md`
- [x] T008 Define shared reason-code taxonomy for guardrails and judge in `docs/superpowers/pilot/runbooks/reason-codes.md`
- [x] T009 Implement run manifest schema validator in `src/lib/manifest_validation.py`
- [x] T010 Implement judge verdict schema validator in `src/lib/verdict_validation.py`
- [x] T011 [P] Implement artifact path resolver utility in `src/lib/artifact_paths.py`
- [x] T012 [P] Implement run id and timestamp utility in `src/lib/run_identity.py`
- [x] T013 Implement structured event envelope utility in `src/lib/event_envelope.py`
- [x] T049 [P] Add unit test for model role-policy adapter with fallback in `tests/unit/test_model_policy_adapter.py`
- [x] T050 Implement model/provider role-policy adapter with fallback handling in `src/services/model_policy_service.py`
- [x] T064 [P] Add unit test for telemetry/trace secret redaction rules in `tests/unit/test_secret_redaction.py`
- [x] T065 Implement shared secret redaction filter for logs/traces/events in `src/lib/secret_redaction.py`
- [x] T073 Create Python package scaffolding and dev tooling config in `pyproject.toml` and `requirements-dev.txt`
- [x] T074 Configure pytest, coverage, and `tests/conftest.py` in `pyproject.toml` / `tests/conftest.py`
- [x] T075 Implement structured logger bootstrap with redaction hook in `src/lib/logging_setup.py`
- [x] T076 Implement run configuration loader (paths, profile, budget, policy refs) in `src/lib/run_config.py`
- [x] T077 [USER] Approve and record model budget caps, fallback order, and kill-switch thresholds in `docs/superpowers/pilot/runbooks/budget-policy.md`
- [x] T078 [USER] Provide provider API credentials (OpenRouter / judge LLM) via Doppler and document required keys in `docs/superpowers/pilot/runbooks/vps-secrets-bootstrap.md`
- [x] T014 Configure feature-level quality and test command matrix in `docs/superpowers/pilot/runbooks/verification-matrix.md` (depends on T073/T074)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Safe Overnight Execution (Priority: P1) 🎯 MVP

**Goal**: Run unattended sessions safely with enforceable guardrails and reviewable blocked-action evidence.

**Independent Test**: Start an unattended run with guardrails enabled and confirm blocked dangerous commands are denied while allowed commands proceed.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T015 [P] [US1] Add contract test for blocked-action event payload in `tests/contract/test_guardrail_event_contract.py`
- [x] T016 [P] [US1] Add integration test for guarded unattended run path in `tests/integration/test_guarded_overnight_run.py`
- [x] T017 [P] [US1] Add integration test for offline/online profile enforcement in `tests/integration/test_execution_profiles.py`
- [x] T051 [P] [US1] Add integration test for orchestrator iteration loop with satisfaction-based termination in `tests/integration/test_orchestrator_iteration_loop.py`

### Implementation for User Story 1

- [x] T018 [P] [US1] Implement guardrail policy loader in `src/services/guardrail_policy_service.py`
- [x] T019 [P] [US1] Implement blocked-command interception adapter in `src/services/guardrail_enforcement_service.py`
- [x] T020 [US1] Implement unattended run launcher workflow in `src/cli/run_overnight.py`
- [x] T021 [US1] Implement run lifecycle state transitions in `src/services/run_session_service.py`
- [x] T022 [US1] Implement blocked-action logging with reason codes in `src/services/guardrail_audit_service.py`
- [x] T023 [US1] Wire profile selection (`offline` default) in `src/services/run_profile_service.py`
- [x] T052 [US1] Implement orchestrator iteration controller with satisfaction-based loop termination in `src/services/orchestrator_loop_service.py`
- [x] T079 [USER] Author initial guardrail blocklist policy file in `docs/superpowers/pilot/config/guardrail-policy.yaml`
- [x] T080 [US1] Implement NTM adapter wiring for command interception in `src/services/ntm_adapter.py`
- [x] T081 [US1] Implement Ralph orchestrator launch integration in `src/services/ralph_launcher.py`
- [x] T082 [US1] Wire run launcher into scheduler wrapper script (replace T020 placeholder) in `~/night_coder/scripts/run-overnight.sh` (document diff in `docs/superpowers/pilot/runbooks/vps-scheduler.md`)
- [x] T024 [US1] Document US1 operator flow in `docs/superpowers/pilot/runbooks/us1-safe-execution.md`

**Checkpoint**: User Story 1 should be fully functional and independently testable.

---

## Phase 4: User Story 2 - External Outcome-Based Judging (Priority: P2)

**Goal**: Evaluate run outcomes via immutable external harness with scenario-based verdicts.

**Independent Test**: Execute a scenario where process completes but user outcome is wrong and verify unsatisfactory verdict with evidence.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T025 [P] [US2] Add contract test for judge verdict schema compliance in `tests/contract/test_judge_verdict_contract.py`
- [x] T026 [P] [US2] Add integration test for immutable judge harness boundary in `tests/integration/test_judge_immutability_boundary.py`
- [x] T027 [P] [US2] Add integration test for outcome-based unsatisfactory verdict path in `tests/integration/test_outcome_based_judging.py`
- [x] T066 [P] [US2] Add integration test for judge-unavailable fallback to `evaluation-pending` in `tests/integration/test_judge_unavailable_fallback.py`

### Implementation for User Story 2

- [x] T028 [P] [US2] Implement scenario evidence assembler in `src/services/scenario_evidence_service.py`
- [x] T029 [P] [US2] Implement external judge invocation wrapper in `src/services/judge_runner_service.py`
- [x] T030 [US2] Implement verdict persistence workflow in `src/services/judge_verdict_service.py`
- [x] T031 [US2] Implement immutable harness path guard in `src/services/judge_harness_guard_service.py`
- [x] T032 [US2] Integrate verdict generation into run completion pipeline in `src/services/run_completion_service.py`
- [x] T067 [US2] Implement judge-unavailable fallback handler setting run state to `evaluation-pending` in `src/services/judge_fallback_service.py`
- [x] T083 [USER] Author first production scenario(s) under external catalog path defined in T062 (3-5 outcome-based scenarios)
- [x] T084 [US2] Implement OpenJudge adapter with structured verdict normalization in `src/services/openjudge_adapter.py`
- [x] T085 [US2] Create and version judge prompt template in `docs/superpowers/pilot/judge/prompt-template.md`
- [x] T086 [US2] Implement LLM budget/cost guard for judge calls (respects T077 caps) in `src/services/judge_budget_service.py`
- [x] T033 [US2] Document US2 reviewer flow in `docs/superpowers/pilot/runbooks/us2-outcome-judging.md`

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
- [ ] T087 [USER] Author first DTU behaviour profile(s) under `docs/superpowers/pilot/dtu/` (WireMock stub definitions for scenarios from T083)
- [ ] T088 [US3] Implement WireMock DTU configuration loader and lifecycle control in `src/services/wiremock_dtu_service.py`
- [ ] T089 [US3] Bootstrap mcp-memory-service (sqlite_vec storage path, health check, startup contract) in `docs/superpowers/pilot/runbooks/memory-service-bootstrap.md`
- [ ] T090 [US3] Implement OTEL exporter wiring for Langfuse (phase 1 files, phase 2 UI) in `src/lib/otel_setup.py`
- [ ] T091 [US3] Document Langfuse self-hosted phase 2 deployment in `docs/superpowers/pilot/runbooks/langfuse-bootstrap.md`
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
- [ ] T092 [P] Create morning-review report template (pairs with T054) in `docs/superpowers/pilot/runbooks/morning-review-template.md`
- [ ] T093 [P] Create runbook index and navigation in `docs/superpowers/pilot/runbooks/INDEX.md`
- [ ] T094 Create supervised dry-run checklist in `docs/superpowers/pilot/runbooks/supervised-dry-run.md`
- [ ] T095 Execute supervised dry run and record findings in `docs/superpowers/pilot/runbooks/dry-run-results.md`
- [ ] T096 [USER] Execute go/no-go decision and enable scheduler for live unattended runs (updates `docs/superpowers/pilot/runbooks/vps-scheduler.md` §8)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately (T001-T006 + T055-T063)
- **Foundational (Phase 2)**: Depends on Setup completion. Includes package scaffolding (T073), tooling (T074), logger (T075), config (T076), and user-required budget (T077) + credentials (T078). Blocks all user stories.
- **User Story Phases (Phase 3-5)**: Depend on Foundational completion
  - US1 is MVP-first. T079 (policy content) must precede T018 policy loader wiring. T082 (wrapper script wiring) depends on T020 + T081.
  - US2 depends on US1 + foundational tests. T083 (scenario authoring) must precede T028 scenario evidence assembler wiring.
  - US3 depends on US1 + US2. T087 (DTU profile authoring) must precede T088 (WireMock loader); T091 Langfuse Phase 2 depends on T090 OTEL wiring.
- **Polish (Phase 6)**: Depends on US1+US2+US3 complete. T095 dry-run requires T044-T048 documentation; T096 (user go/no-go) depends on T095 results.

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
- T073 (pyproject) and T075 (logger) can run in parallel once scaffolding decision is made
- T077 (USER budget policy) and T078 (USER credentials) can happen in parallel while agent works on T073-T076
- T083 (USER scenario authoring) and T087 (USER DTU authoring) can be done by the user in parallel
- Contract and integration tests within each story marked [P] can run in parallel
- Core service tasks marked [P] in each story can be split across contributors
- Polish tasks T092 and T093 can run in parallel; T094/T095/T096 are sequential

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
