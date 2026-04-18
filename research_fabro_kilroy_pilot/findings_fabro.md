# Findings: Fabro (fabro-sh/fabro)

**Primary source:** [fabro-sh/fabro README](https://github.com/fabro-sh/fabro) (retrieved via project snapshot, April 2026).

## One-line positioning

**Fabro** bills itself as an open-source “dark software factory”: encode software process as **version-controlled Graphviz DOT workflow graphs**, run **multi-turn agent sessions** at nodes, add **human approval gates**, and layer **deterministic verifications** (tests, linters, LLM-as-judge) with automatic fix loops.

## Technical shape

| Aspect | Detail |
| ------ | ------ |
| **Implementation** | Rust (~89% per GitHub language stats); **single static binary**, no Python/Node/Docker required for the core CLI |
| **Workflow DSL** | Graphviz `digraph` with nodes (tasks), edges, **CSS-like `model_stylesheet`** on the graph for per-node model routing and fallbacks |
| **Human-in-the-loop** | Hexagon nodes for approval; can steer agents mid-run; “interview” steps for structured input |
| **Execution environment** | **Daytona cloud sandboxes** — isolated VMs, snapshot setup, network controls, cleanup; **SSH** (`fabro sandbox ssh`) and **preview links** for ports |
| **Persistence** | **Git checkpointing** — stages commit code + metadata to branches; resume, revert, trace |
| **Observability / meta** | **Automatic retrospectives** per run (cost, duration, files, LLM narrative) |
| **Surface area** | **REST API** with **SSE**, **React web UI**, queueing for **24/7** runs |
| **License** | MIT |
| **Contribution model** | Issue-based; maintainers implement (no drive-by PRs) |

## Differentiators called out upstream

- Extend **disengagement time** — verification gates so you are not babysitting a REPL.
- **Ensemble routing** — different models for implement vs critique vs summarize in one graph.
- **Token cost** — route cheap models via stylesheets.
- **Security** — untrusted code off laptop via sandboxes.
- **Scale** — concurrent workflows in cloud sandboxes.

## Relation to “Attractor-style” thinking

Fabro shares the **graph-of-stages** mental model with StrongDM-style attractors (explicit control flow, human gates, multi-model steps) but is a **standalone product** with first-class **managed sandbox** and **hosted-style** API/UI story rather than specifying StrongDM’s CXDB contract.

## URLs

- https://github.com/fabro-sh/fabro  
- https://fabro.sh/install.sh (referenced in README)
