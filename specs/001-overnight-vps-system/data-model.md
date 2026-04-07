# Data Model: Overnight VPS Coding System

## 1. RunSession

- **Purpose**: Represents one unattended overnight execution attempt.
- **Fields**:
  - `run_id` (string, required, unique)
  - `scheduled_window` (string, required)
  - `profile` (enum: `offline`, `online`, required)
  - `status` (enum: `queued`, `running`, `completed`, `failed`, `aborted`, required)
  - `started_at` (datetime, optional)
  - `ended_at` (datetime, optional)
  - `orchestrator_ref` (string, required)
  - `manifest_ref` (string, required)
- **Validation**:
  - `ended_at` MUST be >= `started_at` when both are present.
  - terminal statuses MUST include `ended_at`.

## 2. GuardrailPolicy

- **Purpose**: Defines blocked/allowed action classes for unattended runs.
- **Fields**:
  - `policy_id` (string, required)
  - `version` (string, required)
  - `blocked_patterns` (array[string], required)
  - `allowed_patterns` (array[string], required)
  - `mode` (enum: `block_allow_only`, required)
  - `applies_to_profile` (enum: `offline`, `online`, `both`, required)
- **Validation**:
  - Policy MUST include at least one blocked pattern.
  - Patterns MUST be deterministic and machine-parsable.

## 3. ScenarioDefinition

- **Purpose**: Captures expected user outcome for a validation run.
- **Fields**:
  - `scenario_id` (string, required)
  - `title` (string, required)
  - `expected_outcomes` (array[string], required)
  - `evidence_requirements` (array[string], required)
  - `dtu_dependencies` (array[string], required)
- **Validation**:
  - At least one expected outcome required.
  - Evidence requirements MUST map to measurable artifacts.

## 4. JudgeVerdict

- **Purpose**: Immutable external decision for scenario satisfaction.
- **Fields**:
  - `verdict_id` (string, required)
  - `run_id` (string, required)
  - `scenario_id` (string, required)
  - `satisfied` (boolean, required)
  - `score` (number, 0.0-1.0, required)
  - `reasoning` (string, required)
  - `evidence_refs` (array[string], required)
  - `issued_at` (datetime, required)
- **Validation**:
  - `score` MUST be within `[0,1]`.
  - `reasoning` MUST be non-empty.

## 5. DTUArtifact

- **Purpose**: Represents a mock/simulator dependency bundle used in validation.
- **Fields**:
  - `dtu_id` (string, required)
  - `type` (enum: `http-mock`, `service-simulator`, required)
  - `artifact_ref` (string, required)
  - `version` (string, required)
  - `health_status` (enum: `ready`, `degraded`, `down`, required)
- **Validation**:
  - `artifact_ref` MUST resolve to versioned config artifact.

## 6. MemoryRecord

- **Purpose**: Stores reusable cross-run learnings.
- **Fields**:
  - `memory_id` (string, required)
  - `run_id` (string, optional)
  - `tags` (array[string], required)
  - `content` (string, required)
  - `confidence` (number, 0.0-1.0, required)
  - `created_at` (datetime, required)
- **Validation**:
  - Empty or secret-bearing content is invalid.

## 7. TelemetryEvent

- **Purpose**: Time-ordered trace/log event for execution, safety, and judging.
- **Fields**:
  - `event_id` (string, required)
  - `run_id` (string, required)
  - `event_type` (enum: `execution`, `guardrail`, `judge`, `memory`, `system`, required)
  - `severity` (enum: `info`, `warn`, `error`, required)
  - `timestamp` (datetime, required)
  - `payload_ref` (string, optional)
- **Validation**:
  - Severity MUST align with event_type policy mapping.

## 8. RunManifest

- **Purpose**: Canonical summary linking run context to outputs.
- **Fields**:
  - `run_id` (string, required)
  - `git_sha` (string, required)
  - `profile` (string, required)
  - `scenario_ids` (array[string], required)
  - `verdict_refs` (array[string], required)
  - `artifact_refs` (array[string], required)
  - `trace_refs` (array[string], required)
  - `summary` (object, required)
- **Validation**:
  - `run_id` MUST match RunSession.
  - `scenario_ids` and `verdict_refs` cardinality MUST align per executed scenario.

## Relationships

- RunSession 1:N TelemetryEvent
- RunSession 1:N JudgeVerdict
- RunSession 1:N MemoryRecord
- ScenarioDefinition 1:N JudgeVerdict
- RunSession 1:1 RunManifest
- RunManifest N:M DTUArtifact (via `artifact_refs`)

## State Transitions

### RunSession.status

`queued -> running -> completed|failed|aborted`

### DTUArtifact.health_status

`ready <-> degraded -> down -> ready` (after recovery)
