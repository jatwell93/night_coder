# Beads as a Memory Pillar Candidate (Autonomous Coding Systems)

## Scope
- Target: `gastownhall/beads` ([repo](https://github.com/gastownhall/beads))
- Evaluation lens: architecture, retrieval model, workflow fit, operational complexity, lock-in risk, integration pattern
- Research budget used: 4 web searches

## Executive Take
Beads is a strong candidate for **work-memory/state management** in autonomous coding systems (task graph, dependencies, claim/close lifecycle, merge-friendly persistence). It is less suitable as a full long-term semantic knowledge store by itself. Best fit is as a **work-memory pillar** paired with separate docs/knowledge memory.

## Findings

### 1) Architecture
- Beads is a distributed graph issue tracker built for agents, with persistent memory backed by Dolt.
- Core model is issue/task graph + typed relationships + dependency edges, not flat todo text.
- Storage is `.beads/` with Dolt-backed history; supports embedded mode and server mode.
- Design intent explicitly targets multi-agent/multi-branch operation with conflict-resistant IDs and merge behavior.

**Implication:** architecture is purpose-built for agent coordination and long-running execution state, not just human issue tracking.

### 2) Retrieval Model
- Primary retrieval is **operational graph queries** (`bd ready`, `bd blocked`, `bd show`, filtered `list`) rather than semantic vector retrieval.
- Ready-work detection is dependency-aware ("no open blockers"), which reduces repeated planning work by agents.
- CLI and MCP both expose structured outputs (JSON/schema-driven tools), enabling deterministic tool use in loops.
- Hierarchical IDs (epic/task/subtask) and relationship links support recursive decomposition and traversal.

**Implication:** retrieval is excellent for "what should I do next?" and workflow state; weaker for free-form semantic recall unless combined with external knowledge memory.

### 3) Workflow Fit (Autonomous Coding)
- Strong fit for agent loops needing claim/update/close and blocker-aware routing.
- `bd update --claim` atomic claim behavior is useful for parallel workers.
- Supports Git and git-free modes (`BEADS_DIR`, stealth), helping in varied execution environments.
- Maintains audit/history through Dolt commits on writes, aiding traceability for autonomous runs.

**Implication:** good fit for orchestrated or swarm-like coding systems where work state consistency matters.

### 4) Operational Complexity
- Requires operating a Dolt-backed stack (lighter in embedded mode; more moving parts in server mode).
- MCP path adds additional runtime/config surface (Python server, MCP config, env variables, per-workspace routing concerns).
- Project docs explicitly recommend CLI+hooks in shell-capable IDEs due lower token/latency overhead vs MCP.
- Multi-project routing is supported but adds context/canonical-path and concurrency caveats.

**Implication:** moderate operational burden overall; low-to-moderate for CLI-only local use, higher for shared MCP/server deployments.

### 5) Lock-in Risk
- **Data/model lock-in:** medium. The workflow semantics are Beads-centric (task graph + CLI commands), though rooted in open tooling (Go, Dolt, Git ecosystem).
- **Protocol lock-in:** low-to-medium. MCP integration exists, but docs position MCP as optional where shell is available.
- **Migration risk:** moderate due custom task graph conventions and operational habits; mitigated by open-source code/docs and explicit backup/restore tooling in Beads workflow.

**Implication:** not hard proprietary lock-in, but meaningful process/tooling coupling once deeply adopted.

### 6) Integration Pattern Recommendation
- Recommended pattern for autonomous coding systems:
  1. Use Beads as **execution memory/state plane** (tasks, dependencies, lifecycle, ownership).
  2. Keep architecture decisions, coding standards, and domain knowledge in separate doc memory (repo docs/knowledge base).
  3. Prefer CLI integration in environments with shell access (Cursor/Claude Code class tools).
  4. Use MCP integration mainly for MCP-only environments or where centralized routing is required.
- This split aligns with Beads' strengths (structured work-state retrieval) and avoids overloading it as universal memory.

## Candidate Verdict
- **Overall:** Promising memory pillar candidate for autonomous coding systems when scoped to **work-memory orchestration**.
- **Best use case:** Multi-agent execution with dependency-aware task routing and auditable state transitions.
- **Main caution:** Do not treat Beads alone as full semantic/org knowledge memory; pair with complementary knowledge layer.

## Sources (Primary + Supporting)
1. Beads repository: https://github.com/gastownhall/beads
2. README (raw): https://raw.githubusercontent.com/gastownhall/beads/main/README.md
3. Agent instructions (raw): https://raw.githubusercontent.com/gastownhall/beads/main/AGENT_INSTRUCTIONS.md
4. Beads MCP integration README (raw): https://raw.githubusercontent.com/gastownhall/beads/main/integrations/beads-mcp/README.md
5. Changelog (raw): https://raw.githubusercontent.com/gastownhall/beads/main/CHANGELOG.md
