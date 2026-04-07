# Findings: Model Routing and Failover Best Practices for Autonomous Agents

## Scope

This note summarizes practical best practices for:
- Per-role model policy
- Fallback chains
- Timeout/retry controls
- Circuit-breaker style protections
- Outage handling

The guidance focuses on patterns that are implementable with current tooling and provider docs.

## 1) Per-role model policy (route by task role, not one global default)

**Recommended pattern**
- Define explicit roles in your agent workflow (for example: `planner`, `coder`, `critic`, `retriever`, `summarizer`).
- Assign each role a primary model plus constraints (cost ceiling, max latency, context length, required capabilities like tool-calling or JSON mode).
- Keep routing policy declarative (config-driven) so it can be changed without code deploys.

**Why**
- Different stages have different quality/latency/cost requirements; one model is rarely optimal everywhere.
- Role policies reduce random model selection and make behavior auditable.

**Tooling evidence**
- LiteLLM supports router-level and hierarchical settings (`global`, `team`, `key`) for routing behavior, retries, and timeouts; this maps well to per-role/per-tenant policy layers.

Source URLs:
- https://docs.litellm.ai/docs/router_architecture
- https://docs.litellm.ai/docs/proxy/load_balancing
- https://docs.litellm.ai/docs/proxy/keys_teams_router_settings

## 2) Fallback chains (ordered, typed, and bounded)

**Recommended pattern**
- Use ordered fallbacks, but split by failure type:
  - Safety/policy rejection fallback
  - Context-window fallback
  - Generic transport/rate-limit fallback
- Limit fallback depth (usually 1-3 hops) to control latency blowups.
- Preserve idempotency and request correlation IDs across hops.

**Why**
- Typed fallback avoids masking root causes (for example, context overflow should route to long-context model, not arbitrary backup).
- Bounded chains prevent cascading delays under provider stress.

**Tooling evidence**
- LiteLLM documents distinct fallback classes (`content_policy_fallbacks`, `context_window_fallbacks`, and general `fallbacks`).
- LangChain `with_fallbacks` / `RunnableWithFallbacks` provides ordered fallback execution and exception scoping (`exceptions_to_handle`), which is useful for typed fallback logic.

Source URLs:
- https://docs.litellm.ai/docs/proxy/reliability
- https://docs.litellm.ai/docs/router_architecture
- https://reference.langchain.com/python/langchain-core/runnables/base/Runnable/with_fallbacks
- https://reference.langchain.com/python/langchain-core/runnables/fallbacks/RunnableWithFallbacks

## 3) Timeout + retry strategy (small budgets, exponential backoff, jitter)

**Recommended pattern**
- Set strict per-attempt timeouts per role (shorter for interactive steps, longer for batch/offline).
- Retry only transient classes (429, 5xx, network reset, timeout) with exponential backoff + jitter.
- Keep max attempts low (for example 2-3) and enforce total request deadline so retries cannot exceed UX budget.
- Combine retries with fallback: retry within same model group first, then fallback provider/model.

**Why**
- Unbounded retry is a common outage amplifier.
- Backoff with jitter reduces synchronized retry storms during rate-limit pressure.

**Tooling evidence**
- OpenAI rate-limit guidance recommends exponential backoff and avoiding request bursts.
- LiteLLM exposes router timeout and retry controls (`timeout`, `num_retries`) and composes retries with fallback behavior.

Source URLs:
- https://developers.openai.com/api/docs/guides/rate-limits/
- https://developers.openai.com/cookbook/examples/how_to_handle_rate_limits/
- https://help.openai.com/en/articles/6891753-what-are-the-best-practices-for-managing-my-rate-limits-in-the-api
- https://docs.litellm.ai/docs/router_architecture
- https://docs.litellm.ai/docs/proxy/load_balancing

## 4) Circuit-breaker style controls (protect the system during partial outages)

**Recommended pattern**
- Add circuit-breaker state per provider/model group:
  - `CLOSED`: normal traffic
  - `OPEN`: fail fast / reroute after threshold breach
  - `HALF_OPEN`: limited probes to test recovery
- Trigger on rolling error-rate and latency thresholds, with minimum sample size.
- Pair with bulkheads/concurrency caps to isolate failing providers.

**Why**
- Circuit breakers prevent saturation from repeatedly calling known-failing dependencies.
- Half-open probes restore service faster without flooding recovering providers.

**Tooling evidence**
- Resilience4j docs provide a mature circuit-breaker model (state machine, sliding windows, failure thresholds) applicable to model-provider wrappers.
- Hystrix is in maintenance mode; modern deployments commonly use Resilience4j-style controls.

Source URLs:
- https://resilience4j.readme.io/docs/circuitbreaker
- https://resilience4j.readme.io/docs/comparison-to-netflix-hystrix

## 5) Outage handling and operational playbook

**Recommended pattern**
- Integrate provider status signals and your own synthetic probes; do not rely on status pages alone.
- During incident mode, automatically:
  - lower concurrency
  - tighten deadlines
  - switch to cheaper/faster backup models for non-critical paths
  - disable non-essential agent steps/tool calls
- Log degradation decisions in traces (what route was chosen and why).

**Why**
- Official status updates can lag real failures; internal probes catch user-impact sooner.
- Controlled degradation is better than total failure in autonomous workflows.

**Tooling evidence**
- OpenAI provides webhook/event infrastructure for operational integration points.
- Status tooling can be used for incident-triggered automation, but should be supplemented with active health checks.

Source URLs:
- https://platform.openai.com/docs/guides/webhooks
- https://platform.openai.com/docs/api-reference/webhook-events
- https://status.openai.com/

## Implementation Checklist (practical defaults)

- Define role-to-model policy table with primary + fallback model group.
- Configure per-role timeout, retry count, and total deadline budget.
- Implement typed fallback rules (policy/context/general) rather than one generic backup.
- Add per-provider circuit breaker with rolling windows and half-open probes.
- Emit routing telemetry (`role`, `primary_model`, `fallback_used`, `retry_count`, `breaker_state`, `latency_ms`, `error_class`).
- Add incident mode toggle and runbook automation hooks.

## Notes / Limitations

- Provider/model behavior and limits change frequently; validate against live docs before hard-coding thresholds.
- Some examples in ecosystem docs are illustrative and should be load-tested in your traffic profile before production rollout.
