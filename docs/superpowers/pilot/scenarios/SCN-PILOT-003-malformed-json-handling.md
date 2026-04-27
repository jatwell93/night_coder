# SCN-PILOT-003: Malformed JSON response yields structured failure

## Goal
If upstream returns malformed JSON, the agent detects parse failure and returns structured error output with explicit log evidence.

## Given
- `UPSTREAM_METHOD`, `UPSTREAM_PATH`, and `UPSTREAM_BASE_URL` are provided by run config/environment.
- DTU stub for the configured endpoint returns `200` with intentionally malformed JSON response body.
- Scenario defines required structured parse-error fields and required failure log marker.

## When
The agent executes the workflow step that calls the configured upstream endpoint and attempts to parse the response content.

## Then
- [ ] The agent detects malformed payload and classifies it as parse/contract failure.
- [ ] The agent emits structured error output (not plain-text-only failure).
- [ ] The agent log includes an explicit failure marker suitable for judge evidence (for example `SCENARIO_RESULT=UNSATISFIED` with parse reason code).
- [ ] Workflow remains stable (no uncontrolled crash).
- [ ] Evidence includes a response snippet (redacted as needed) and parser error context.

## Grading notes
- Use deterministic checks to confirm malformed payload fixture and structured error schema compliance.
- Judge should confirm parse failure is handled explicitly and not misclassified as timeout/network failure.
- Scenario is unsatisfied if structured error output or explicit failure marker is missing.

## Out of scope
- Upstream schema migration strategy.
- Automatic payload repair heuristics.
- Non-JSON content-type negotiation.
