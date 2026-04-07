# Model/Provider Pillar Research Plan

## Main Research Question

What Model/Provider stack should the overnight autonomous coding system use for v1 so that model selection, routing, cost-capping, and failover are reliable, auditable, and provider-flexible?

## Subtopics

1. **Provider access layer options (aggregator vs gateway vs direct APIs)**
   - Evaluate OpenRouter and comparable access layers (e.g., LiteLLM, Portkey, AI gateways) for routing flexibility and operational reliability.
   - Expected output: shortlist of viable provider access patterns and trade-offs.

2. **Routing and failover design patterns**
   - Identify practical patterns for per-role model routing (planner/coder/judge), fallback chains, retry policy, and outage handling.
   - Expected output: recommended routing policy structure and failure-mode controls.

3. **Cost controls and budget enforcement**
   - Research mechanisms to cap spend per run/day/month, detect budget pressure, and prevent runaway loops.
   - Expected output: concrete cost-governance controls and measurable guardrails.

4. **Tooling fit with existing architecture (Ralph + OpenJudge + Langfuse)**
   - Assess integration implications for the selected Model/Provider approach with current pillars and constraints.
   - Expected output: compatibility notes, integration effort estimate bands, and key risks.

5. **Seed links relevance check**
   - Review provided links (`beads`, `Acontext`, `A-mem`, `mcp-memory-service`, `yams`) as potential adjacent components.
   - Expected output: whether each is directly relevant to Model/Provider, or better categorized under Memory/Knowledge pillar.

## Synthesis Approach

- Produce a recommendation matrix with:
  - primary option for v1
  - secondary fallback option
  - explicit no-go constraints
  - evidence-backed rollout and rollback triggers
- Keep decision boundaries clear:
  - **Model/Provider pillar** = model access, routing, budgets, failover
  - **Memory pillar** = long-term/context persistence tools
