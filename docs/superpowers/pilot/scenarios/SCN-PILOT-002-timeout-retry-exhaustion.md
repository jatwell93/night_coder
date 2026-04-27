# SCN-PILOT-002: Timeout with retry exhaustion yields structured failure

## Goal
When the configured upstream call repeatedly times out, the agent fails gracefully with structured error output and explicit evidence logging.

## Given
- `UPSTREAM_METHOD`, `UPSTREAM_PATH`, and `UPSTREAM_BASE_URL` are provided by run config/environment.
- DTU stub for the configured endpoint is set to timeout for all retry attempts.
- Retry policy (max attempts and backoff behavior) is defined in config and available to the run.
- Scenario defines required structured error fields and required failure log marker.

## When
The agent executes the workflow step that calls the configured upstream endpoint and all retries are exhausted due to timeout.

## Then
- [ ] The agent attempts retries according to configured retry policy.
- [ ] Final outcome is a structured error object that includes timeout/retry-exhausted classification.
- [ ] The agent log includes an explicit failure marker suitable for judge evidence (for example `SCENARIO_RESULT=UNSATISFIED` plus timeout reason code).
- [ ] Error handling remains controlled and deterministic (no unhandled exception crash).
- [ ] Produced evidence includes retry-attempt traces and terminal failure record.

## Grading notes
- Use deterministic checks to verify retry count and required structured error fields.
- Judge should reject outcomes that only include plain-text logs but omit structured failure output.
- Scenario is unsatisfied if retries are missing, failure classification is wrong, or the explicit failure marker is absent.

## Out of scope
- Circuit-breaker redesign.
- Global scheduler abort policy.
- Alternate fallback provider selection.
