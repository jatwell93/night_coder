<!--
Sync Impact Report
- Version change: N/A (template) -> 1.0.0
- Modified principles:
  - Template Principle 1 -> I. Code Quality Is a Release Criterion
  - Template Principle 2 -> II. Testing Evidence Is Mandatory
  - Template Principle 3 -> III. User Experience Consistency Across Flows
  - Template Principle 4 -> IV. Performance Budgets Are Defined and Enforced
  - Template Principle 5 -> V. Simplicity, Observability, and Safe Change
- Added sections:
  - Delivery Quality Gates
  - Development Workflow & Review Standards
- Removed sections:
  - None
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/tasks-template.md
  - ⚠ pending .specify/templates/commands/*.md (directory not present in repository)
  - ✅ README.md review complete (no constitution references to update)
- Follow-up TODOs:
  - None
-->
# night_coder Constitution

## Core Principles

### I. Code Quality Is a Release Criterion
All production changes MUST meet baseline quality gates before merge: formatting/linting pass,
warnings are either fixed or explicitly justified, and code is readable enough that ownership can
transfer without verbal explanation. New abstractions MUST be introduced only when they reduce
complexity at current scale. Rationale: durable quality reduces rework and keeps overnight
automation safe.

### II. Testing Evidence Is Mandatory
Every behavior change MUST ship with automated test evidence at the right level (unit,
integration, or contract). Bug fixes MUST include a regression test that fails before the fix and
passes after. Plans and tasks MUST define how each user story is independently validated. Rationale:
test evidence is the objective signal that changes work as intended.

### III. User Experience Consistency Across Flows
User-visible behavior MUST be consistent for naming, interaction patterns, error handling,
terminology, and defaults across comparable flows. Specs MUST define acceptance scenarios for normal
and failure paths, including clear and actionable error messages. Rationale: consistency improves
trust and lowers cognitive load.

### IV. Performance Budgets Are Defined and Enforced
Each feature MUST state explicit performance budgets (latency, throughput, memory, or startup cost
as applicable) and define how they are measured. Changes that exceed budgets MUST include documented
mitigation, rollback, or approval before release. Rationale: performance regressions are product
regressions and must be managed intentionally.

### V. Simplicity, Observability, and Safe Change
Implementations SHOULD favor the simplest design that satisfies current requirements and quality
gates. Changes MUST emit enough logs/metrics/traces to diagnose failures without live debugging.
High-risk changes MUST include rollback notes and impact boundaries in the plan. Rationale:
simplicity and observability reduce operational risk and accelerate recovery.

## Delivery Quality Gates

Before implementation begins, each plan MUST pass a Constitution Check covering:
- Code quality expectations and lint/format policy
- Test strategy and required evidence per user story
- UX consistency rules and acceptance scenarios
- Performance budgets and measurement approach
- Observability and rollback expectations

Before merge, the same gates MUST be re-validated with implementation evidence.

## Development Workflow & Review Standards

1. Specs MUST contain independently testable user stories and measurable success criteria.
2. Plans MUST identify technical constraints, quality/performance risks, and verification steps.
3. Tasks MUST include explicit test tasks and story-level validation checkpoints.
4. Reviews MUST reject changes that violate principles unless an explicit exception and rationale
   are recorded.
5. Exceptions MUST include owner, scope, expiration date, and remediation plan.

## Governance

This constitution supersedes conflicting local process notes for planning and implementation.

Amendment procedure:
1. Propose amendment with rationale and impact analysis.
2. Update dependent templates and guidance documents in the same change.
3. Record version bump rationale (major/minor/patch) in the Sync Impact Report.

Versioning policy:
- MAJOR: incompatible principle removals or redefinitions.
- MINOR: new principle/section added or materially expanded guidance.
- PATCH: clarifications, wording, or non-semantic refinements.

Compliance review expectations:
- Every plan and task artifact MUST include an explicit constitution check.
- Reviews MUST verify evidence for testing, UX consistency, and performance requirements.
- Non-compliance MUST be fixed before merge or documented as a time-bounded exception.

**Version**: 1.0.0 | **Ratified**: 2026-04-07 | **Last Amended**: 2026-04-07
