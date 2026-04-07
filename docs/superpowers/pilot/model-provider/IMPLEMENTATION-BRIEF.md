# Model/Provider Implementation Brief

Decision reference: `dec-20260406-006`  
Selected approach: OpenRouter-first model/provider layer with internal role-policy adapter  
Context: overnight-pilot

## Goal

Implement a model/provider layer that supports:
- role-based routing (`planner`, `coder`, `judge`, `critic`)
- typed failover for transient failures
- budget-pressure control stages
- auditable routing and cost traces in overnight runs

This layer must not replace orchestration ownership (Ralph remains orchestrator).

## Scope

In scope:
- provider adapter contract and policy config
- OpenRouter primary integration
- direct-provider escape-hatch wiring
- failover/retry/deadline controls
- budget pressure ladder behavior
- observability fields for route/cost/fallback

Out of scope:
- replacing orchestrator logic
- memory-layer changes
- non-pilot multi-tenant hardening

## Implementation Plan

## 1) Define Internal Policy Contract

Create a single policy config file for role routing and reliability controls.

Required policy sections:
- `roles`: primary model by role + fallback list
- `failure_classes`: transient/policy/context
- `retries`: max retries, backoff, jitter, total deadline
- `budget`: thresholds and actions
- `provider_order`: preferred provider sequence

Acceptance:
- Policy file exists and is machine-readable.
- All four roles have explicit primary + fallback entries.

## 2) Implement Provider Adapter

Implement a neutral adapter interface used by orchestrator tasks:
- `select_model(role, context)`
- `invoke(request)`
- `classify_error(error)`
- `resolve_fallback(role, failure_class, attempt)`

Wire OpenRouter as primary backend.
Wire direct-provider clients (Anthropic/OpenAI/Google) as escape path.

Acceptance:
- Calls can execute via OpenRouter using role policy.
- Escape path can be selected without changing orchestrator business logic.

## 3) Reliability Controls

Implement bounded reliability behavior:
- retries only for transient classes
- typed fallback by failure class
- hard stop on retry/deadline budget exhaustion

Failure classes:
- `transient`: 429, 5xx, timeout, network reset
- `context`: context/window exceeded
- `policy`: moderation/policy rejection

Acceptance:
- Injected transient failure recovers via retry/fallback in bounded time.
- No unbounded retry/fallback loops.

## 4) Budget Governance

Implement staged budget behavior:
- `70%`: notify only
- `85%`: degrade non-critical roles to cheaper models
- `95%`: restrict premium models to allowlist roles/tags
- `100%`: enforce block/degrade policy for non-critical traffic

Note: classify each control as `advisory` or `enforced` in config and logs.

Acceptance:
- Simulated budget pressure triggers expected stage transitions.
- Stage transitions are visible in logs/traces.

## 5) Observability Mapping

Emit and persist at least:
- role
- selected model
- provider
- fallback_used (bool + target)
- retry_count
- failure_class
- latency_ms
- estimated_cost_usd
- budget_stage

Acceptance:
- Morning review can see why route/fallback decisions were made.
- Cost behavior and budget-stage transitions are queryable.

## 6) Trial Run and Evidence Capture

Run one representative overnight scenario and capture evidence for all requirements in `dec-20260406-006`.

Evidence checklist:
- [ ] Role routing policy correctness shown in trace
- [ ] Simulated transient failure recovery verified
- [ ] Budget-stage transitions verified under pressure
- [ ] Integration effort measured (actual hours)
- [ ] Escape-hatch fallback drill completed

Output artifacts:
- trial run notes
- failure-injection results
- budget test results
- measured integration effort
- recommendation to keep/rollback

## Rollback Procedure (if triggers fire)

If gateway dependency risk materializes:
1. Promote LiteLLM as primary model plane (keep same internal policy contract).
2. Keep OpenRouter as secondary route where useful.
3. Keep direct-provider escape path active.
4. Update `DECISIONS.md` and rerun evidence checks.

## Done Criteria

This brief is complete when:
- all six implementation sections are delivered
- all five evidence requirements from `dec-20260406-006` are satisfied
- keep/rollback recommendation is documented with measured outcomes
