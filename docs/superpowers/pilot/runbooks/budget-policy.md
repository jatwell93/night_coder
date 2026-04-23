# Budget policy (pilot) — T077

Operator approval record for:

- per-run and nightly budget caps,
- backend/provider fallback order,
- kill-switch thresholds and actions.

This runbook is intentionally policy-first: the system should not run unattended production-like
windows until these values are approved and wired into config/services.

---

## 1. Scope and intent

This policy governs cost/rate-limit resilience for overnight runs driven by Ralph and backend CLIs
(Gemini, OpenCode, Codex, etc.), with secrets injected via Doppler.

Primary goals:

1. Prevent uncontrolled spend.
2. Keep runs continuous when one provider/key is exhausted.
3. Fail closed (safe stop) when fallback is not available.

---

## 2. Ralph behavior when a provider hits limits

Observed from Ralph upstream docs:

- Ralph supports explicit backend selection (`ralph run --backend ...`) and per-hat backend
  overrides in `ralph.yml`.
- Ralph exposes loop stop conditions (`max-iterations`, `max-runtime`, `max-cost`) and exit codes.
- Ralph docs do **not** currently document built-in automatic key/provider rotation on
  provider-quota errors.

Implication for pilot policy:

- Treat provider-key exhaustion as an external failure class that must be handled by
  our model policy + launcher/service logic (T050/T076 and later runtime services),
  not by Ralph alone.

References:

- [Ralph Backends](https://mikeyobrien.github.io/ralph-orchestrator/guide/backends/)
- [Ralph Configuration](https://mikeyobrien.github.io/ralph-orchestrator/guide/configuration/)
- [Ralph CLI Reference](https://mikeyobrien.github.io/ralph-orchestrator/guide/cli-reference/)

---

## 3. Budget units and currency

All cost policy values in this runbook are in **AUD**.

Important note:

- Most providers meter/return charges in USD.
- Runtime guards may track an internal USD estimate and convert for reporting.
- Operator approvals and go/no-go thresholds remain AUD.

If conversion is used in code, pin a documented FX source and refresh cadence in implementation.

---

## 4. Canonical policy (recommended starter values)

Recommended for pilot on a single 4GB VPS with one unattended nightly window.
These are intentionally conservative and can be relaxed after 1-2 stable weeks.

| Policy key | Value (AUD unless noted) | Status | Notes |
|------------|---------------------------|--------|-------|
| `per_run_cap_aud` | `8.00` | Proposed | Hard stop for a single unattended run. |
| `nightly_cap_aud` | `20.00` | Proposed | Aggregate cap per local-night scheduler window. |
| `judge_cap_aud` | `4.00` | Proposed | Reserve for external judge calls (US2) to avoid coder starvation. |
| `max_iterations` | `40` | Proposed | Loop guardrail; compatible with current `run_config` defaults. |
| `max_runtime_seconds` | `21600` | Proposed | 6h cap per run (within overnight window). |
| `rate_limit_backoff_seconds` | `60` | Proposed | Initial backoff on 429/quota-pressure errors. |
| `max_retries_per_provider` | `3` | Proposed | Then provider marked unavailable for the run. |

### 4.1 Cost anomaly slope (recommended)

- If estimated burn rate projects exceeding `per_run_cap_aud` within 30 minutes, trigger
  `pause_and_require_operator_resume`.
- If two consecutive runs hit anomaly pause in one night, stop timer and require manual review.

---

## 5. Provider/key fallback order (required)

Define role-specific fallback order. Example below includes your requested chain:

| Role | Priority 1 | Priority 2 | Priority 3 | Priority 4 |
|------|------------|------------|------------|------------|
| `coder` | `glm` (via configured backend/provider) | `gemini` | `qwen` | `openrouter` |
| `judge` | `openrouter` | `openai` | `gemini` | `__optional__` |
| `memory-writer` | `openrouter` | `gemini` | `openai` | `__optional__` |

Policy rules:

1. If a provider returns quota/rate-limit/auth-exhausted signals repeatedly, mark that provider
   unavailable for the current run and move to next priority.
2. Never loop back to a failed provider in the same run unless explicitly reset by operator.
3. Record every fallback transition in telemetry with reason code and provider name.
4. If all providers in chain are unavailable, trigger kill-switch action `halt_run`.
5. After a fallback switch, enforce a 5-minute cooldown before trying to re-enable a failed
   provider (only if explicitly allowed by operator policy).

---

## 6. Failure classification for fallback

Fallback-eligible (switch provider):

- HTTP `429` / explicit rate-limit responses,
- explicit quota/billing exhausted responses,
- provider capacity throttling / temporary overload,
- transient network failures beyond retry threshold.

Non-fallback (halt immediately or require operator):

- policy violation / guardrail block,
- invalid prompt contract or malformed payload bugs,
- repeated authentication failure due to misconfiguration across all providers.

---

## 7. Kill-switch thresholds and actions

Define explicit automatic actions:

| Trigger | Threshold | Action | Severity |
|---------|-----------|--------|----------|
| Per-run spend | `>= per_run_cap_aud` | `halt_run` | `error` |
| Nightly spend | `>= nightly_cap_aud` | `disable_scheduler_and_alert` | `error` |
| Provider fallback exhaustion | all providers unavailable for role | `halt_run` | `error` |
| Retry storm | retries exceed `max_retries_per_provider` for all providers | `halt_run` | `error` |
| Cost anomaly | estimated burn rate exceeds approved slope | `pause_and_require_operator_resume` | `warn` |

Recommended scheduler action for nightly cap breach:

```bash
systemctl --user stop night-coder-run.timer
```

Then perform operator review before re-enabling.

---

## 8. Doppler key layout for fallback

Store all potentially used provider keys in Doppler (no plaintext in repo), for example:

- `GLM_API_KEY`,
- `GEMINI_API_KEY`,
- `QWEN_API_KEY`,
- `OPENROUTER_API_KEY`,
- `OPENAI_API_KEY`,
- backend-specific aliases required by your selected CLI wrappers.

Injection rule:

- Runtime selects provider from policy chain; only required env vars are consumed by that backend.
- Missing key for the selected provider is a startup validation error, not a silent skip.

---

## 9. Operator approval record (T077)

| Item | Owner | Date | Decision |
|------|-------|------|----------|
| Per-run cap approved (AUD) | USER | `__TODO__` | Default proposal: `8.00` |
| Nightly cap approved (AUD) | USER | `__TODO__` | Default proposal: `20.00` |
| Fallback order approved per role | USER | `__TODO__` | Default proposal: `glm -> gemini -> openrouter -> openai` for coder |
| Kill-switch thresholds approved | USER | `__TODO__` | Default proposal: section 7 + anomaly slope in 4.1 |
| Retry/backoff policy approved | USER | `__TODO__` | Default proposal: `60s` backoff, `3` retries/provider |
| Go-live allowed for unattended schedule | USER | `__TODO__` | `__TODO__` |

---

## 10. Validation checklist

- [ ] All budget caps filled in AUD.
- [ ] Fallback chain defined for each active role (`coder`, `judge`, `memory-writer`).
- [ ] Kill-switch actions approved and operationally testable.
- [ ] Doppler contains all keys required by fallback chain.
- [ ] Policy decisions reflected in runtime config (`run_config`, model policy, and scheduler guard).
- [ ] T077 marked complete in `specs/001-overnight-vps-system/tasks.md`.

---

## 11. References

- Task list: [`../../../../specs/001-overnight-vps-system/tasks.md`](../../../../specs/001-overnight-vps-system/tasks.md)
- Secrets bootstrap: [`./vps-secrets-bootstrap.md`](./vps-secrets-bootstrap.md)
- Ralph install/details: [`./vps-ralph-install.md`](./vps-ralph-install.md)
- Model policy service: `src/services/model_policy_service.py` (T050)
- Run configuration loader: `src/lib/run_config.py` (T076)

---

## Revision

| Date | Notes |
|------|-------|
| 2026-04-23 | Initial T077 runbook with AUD-denominated caps, provider fallback chain, and kill-switch policy template. |
| 2026-04-23 | Added conservative proposed AUD caps, retry/backoff defaults, and anomaly trigger guidance for quick USER approval. |
