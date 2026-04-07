# Planner Pillar Implementation Brief

Decision reference: `dec-20260406-005`  
Selected approach: **Spec Kit** as dedicated Planner pillar  
Context: overnight-pilot

## Goal

Produce **machine-usable planning artifacts** (spec, technical plan, ordered tasks, acceptance checks) that Ralph executes and OpenJudge can evaluate — without Ralph absorbing planner responsibilities.

## Scope

**In scope**

- Spec Kit workflow for at least one pilot scenario: requirements → plan → tasks → acceptance traceability.
- Headless/CLI path suitable for overnight automation.
- Documentation of artifact paths and handoff to orchestrator.

**Out of scope**

- Replacing Ralph as orchestrator.
- Locking plans to a single LLM vendor (keep provider flexibility per decision invariants).

## Checklist

1. Install/configure Spec Kit per upstream docs; pin versions.
2. Define where plan artifacts land relative to `docs/superpowers/pilot/` (align with artifact-registry manifest if present).
3. Prove one end-to-end trial: Spec Kit output → Ralph execution → judgeable acceptance.
4. Document rollback: revert to manual/Quint-only planning if Spec Kit blocks the loop.

## Links

- Full decision: `.quint/decisions/dec-20260406-005.md`
