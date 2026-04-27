# SCN-PILOT-001: Configurable upstream happy-path success

## Goal
The agent calls the configured upstream endpoint and correctly handles a healthy success response.

## Given
- `UPSTREAM_METHOD`, `UPSTREAM_PATH`, and `UPSTREAM_BASE_URL` are provided by run config/environment.
- DTU stub for that method/path returns `200` with a valid success JSON body defined by project contract.
- Scenario defines the success indicator key/value(s) expected for this project.

## When
The agent executes the workflow step that calls the configured upstream endpoint and parses the response.

## Then
- [ ] The request uses the configured method/path and does not rely on a hard-coded endpoint.
- [ ] The HTTP response status is `200`.
- [ ] The parsed response includes the scenario-defined success indicator(s).
- [ ] The agent emits a structured success output object.
- [ ] The agent log includes an explicit success marker suitable for judge evidence (for example `SCENARIO_RESULT=SATISFIED`).
- [ ] No error/exception stack trace appears in logs for this upstream call path.

## Grading notes
- Use deterministic checks to verify endpoint configurability and success-indicator presence in parsed output.
- Use judge reasoning to confirm the behavior reflects scenario intent, not just a superficial `200` response.
- Required evidence should include request/response capture and agent stdout/stderr snippets.

## Out of scope
- Timeout/retry behavior.
- Malformed payload handling.
- Non-200 classification policy.
