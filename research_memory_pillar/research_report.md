# Memory Pillar Research Report

Date: 2026-04-06

## Research Question

Which memory-layer approach should the overnight autonomous coding system adopt for v1 to provide durable cross-run memory, reliable retrieval, and low operational risk for a solo operator?

## Synthesis

- **Strong v1 primary candidate:** `mcp-memory-service` in local `sqlite_vec` mode.
- **Strong alternative:** `Acontext` for file-inspectable skill-memory workflows.
- **Important complementary option:** `Beads` is excellent for execution/work-memory graph state, but not a full semantic long-term memory replacement by itself.
- **Promising but higher-risk substrate:** `YAMS` (powerful local corpus engine, explicitly experimental).
- **Research track:** `A-MEM` is high-potential but currently best treated as R&D rather than immediate production memory pillar.

## Why this shape

1. You need a memory service that works unattended overnight and integrates cleanly with existing pillars.
2. `mcp-memory-service` is service-native and retrieval-centric with practical self-hosted operation.
3. `Acontext` is highly inspectable and portable (memory as files/skills), which is great for auditability.
4. `Beads` should be treated as task/work-state memory (execution memory), not full semantic memory.

## Proposed Decision Direction

- **Primary memory pillar for v1:** `mcp-memory-service` (`sqlite_vec` first, evaluate hybrid later).
- **Fallback:** `Acontext`.
- **Complement (optional):** `Beads` for task graph/work-memory if execution coordination needs increase.

## Source URLs

- Beads: https://github.com/gastownhall/beads
- Acontext: https://github.com/memodb-io/Acontext
- A-MEM: https://github.com/agiresearch/A-mem
- mcp-memory-service: https://github.com/doobidoo/mcp-memory-service
- YAMS: https://github.com/trvon/yams
