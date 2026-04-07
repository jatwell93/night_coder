# Execution Sandbox Pillar — Research Plan

## Question
What isolation policy and tooling fit an overnight autonomous coding stack (Ralph, solo VPS) for shell, filesystem, and network per task?

## Subtopics
1. **Agent sandbox patterns** — Docker, Firejail, bubblewrap, rootless containers, devcontainers.
2. **Orchestrator integration** — how Ralph / similar runners constrain commands today.
3. **Trade-offs** — security vs ops complexity on 4GB VPS.

## Synthesis
Shortlist + v1 recommendation + rollback (full host vs stricter sandbox).
