# Memory Pillar Research Plan

## Main Research Question

What memory-layer approach should the overnight autonomous coding system adopt for v1 to support cross-run continuity, retrieval quality, operational simplicity, and low lock-in while fitting solo-operator constraints?

## Subtopics

1. **Task/issue graph memory systems (Beads and adjacent)**
   - Investigate graph-oriented memory/tracking tools for agent workflows.
   - Expected output: strengths/limits for planning continuity, dependency tracking, and multi-run coordination.

2. **Skill-file memory systems (Acontext and adjacent)**
   - Investigate "memory as files/skills" approaches for inspectability and portability.
   - Expected output: fit for auditable memory and retrieval behavior in unattended runs.

3. **Knowledge graph + service memory backends (mcp-memory-service and peers)**
   - Investigate self-hosted API memory services, graph links, and retrieval latency/operability characteristics.
   - Expected output: integration and ops trade-offs for production-like usage.

4. **Research/experimental agentic memory (A-MEM and related)**
   - Investigate maturity and applicability of research-centric memory architectures for near-term v1.
   - Expected output: practical adoption risk and stepping-stone value.

5. **Content-addressed/local memory engines (YAMS and alternatives)**
   - Investigate local-first persistence/search engines for memory storage, retrieval, dedupe, and portability.
   - Expected output: viability as memory substrate vs complete memory product.

## Synthesis Plan

- Produce a shortlist with:
  - v1 primary candidate
  - v1 fallback candidate
  - no-go constraints
  - integration/rollback triggers
- Keep pillar boundaries explicit:
  - **Memory pillar** = persistence/retrieval/knowledge continuity
  - **Model/Provider pillar** = routing/failover/cost controls
