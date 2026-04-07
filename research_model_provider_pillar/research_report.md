# Model/Provider Pillar Research Report

Date: 2026-04-06

## Question

Which Model/Provider approach should the overnight autonomous coding system use for v1 to support reliable model selection, routing, cost caps, and failover while preserving provider flexibility?

## Summary

- **Primary v1 direction:** OpenRouter as access layer + internal routing policy contract.
- **Operationally stronger alternative:** LiteLLM self-hosted gateway when you want tighter control and are willing to run infra.
- **Managed governance alternative:** Portkey for policy-rich centralized routing.
- **Always keep a direct-provider escape hatch** (Anthropic/OpenAI/Google) to avoid gateway lock-in.

## Why

1. OpenRouter provides strong provider/model routing and fallback with fast integration effort.
2. LiteLLM provides deep control over retries/fallback classes/budget routing, but adds ops burden.
3. Portkey provides composable routing and governance features, but introduces platform dependency.
4. Direct providers minimize intermediary lock-in but require significantly more custom reliability logic.

## Recommended Architecture Pattern

- **Policy layer (yours):**
  - role-based routing table (`planner`, `coder`, `judge`, `critic`)
  - typed fallback classes (policy/context/transient)
  - retry+timeout budgets per role
  - budget-pressure downgrade policy
- **Provider access layer (tool):**
  - OpenRouter now; LiteLLM or Portkey as alternatives
- **Escape hatch:**
  - direct provider clients for critical path fallback

## Cost Governance Baseline

- Enforced + advisory controls must be separated.
- Use layered budgets: org -> project/workspace -> model/provider/tag/user.
- Implement pressure policies (notify -> degrade -> restrict -> enforce).

## Seed Links Relevance

The provided seed links are valuable, but they mostly map to **Memory/Knowledge** infrastructure rather than Model/Provider routing:

- `beads`, `Acontext`, `A-mem`, `mcp-memory-service`, `yams` are primarily persistent-memory systems and should be evaluated in the Memory pillar cycle.

## Source Index

- OpenRouter routing/fallback docs
- LiteLLM routing/reliability/budget docs
- Portkey routing/fallback docs
- Anthropic/OpenAI/Google quota/rate docs
- LangSmith cost-tracking docs
- AWS Bedrock cost-governance docs
- Seed memory-tool repos (for pillar boundary classification)
