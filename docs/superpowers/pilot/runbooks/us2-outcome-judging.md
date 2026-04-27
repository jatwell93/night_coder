# US2 Outcome-Based Judging Runbook (T033)

Operator flow for reviewing external judge outcomes produced by the US2 pipeline.

---

## 1) Inputs and artifacts

- Scenario definitions from `SCENARIO_CATALOG_PATH`
- Evidence assembled by `src/services/scenario_evidence_service.py`
- Judge decision produced via `src/services/judge_runner_service.py`
- Persisted verdict artifacts from `src/services/judge_verdict_service.py`
- Fallback records from `src/services/judge_fallback_service.py`

---

## 2) Verdict states

- `completed`: judge returned a verdict with `satisfied`, `score`, and `reasoning`.
- `evaluation-pending`: judge unavailable or budget blocked; fallback record written.

`evaluation-pending` is a manifest summary status, not a RunSession status.

---

## 3) Reviewer checklist

For each scenario in a run:

1. Open verdict artifact for the scenario.
2. Verify `scenario_id` and `run_id` align with the manifest.
3. Confirm `score` is in `[0, 1]` and `reasoning` is non-empty.
4. Compare reasoning claims with evidence references.
5. Record one of:
   - accepted satisfactory,
   - accepted unsatisfactory,
   - needs re-evaluation.

For `evaluation-pending`:

1. Inspect fallback record reason code (`JDG.fallback.evaluation-pending` expected).
2. Confirm unavailability cause (provider outage, budget cap, transport error).
3. Queue re-evaluation once judge path is healthy and budget allows.

---

## 4) Failure triage guidance

- Outcome mismatch with valid evidence: treat as product/workflow failure.
- Missing evidence refs: treat as pipeline/instrumentation gap.
- Repeated `evaluation-pending`: treat as judge reliability/capacity issue.
- Budget cap violations: review T077 policy and adjust only with explicit approval.

---

## 5) Related references

- `docs/superpowers/pilot/runbooks/reason-codes.md`
- `docs/superpowers/pilot/runbooks/status-taxonomy.md`
- `docs/superpowers/pilot/judge/prompt-template.md`
- `specs/001-overnight-vps-system/contracts/judge-verdict.schema.json`
