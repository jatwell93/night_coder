# Findings: Kilroy (danshapiro/kilroy)

**Primary source:** [danshapiro/kilroy README](https://github.com/danshapiro/kilroy) (retrieved via project snapshot, April 2026).

## One-line positioning

**Kilroy** is a **local-first CLI** for running **StrongDM-style Attractor pipelines** in a git repo: **ingest** English → DOT, **validate**, **run** node-by-node in an **isolated git worktree**, **resume** from logs/CXDB/run branch.

## Technical shape

| Aspect | Detail |
| ------ | ------ |
| **Implementation** | Go (~98% per GitHub language stats) |
| **Workflow DSL** | Graphviz `digraph` — stages, conditionals, human gates, parallelism/fan-in; **checkpoint after each stage** |
| **CXDB** | Separate **execution database** for typed run events and artifact blobs; **“git branch is code history; CXDB is run history”** |
| **Git** | **Commit per completed node** on a **run branch**; worktree isolation |
| **Ingestion** | `attractor ingest` uses **Claude CLI** + bundled **`create-dotfile` skill** to generate DOT from natural language |
| **Providers** | Pluggable **API vs CLI** backends; built-ins include OpenAI, Anthropic, Google, Kimi, ZAI, Cerebras, Minimax; CLI mappings e.g. OpenAI→`codex`, Anthropic→`claude`, Google→`gemini` |
| **Experimental server** | `kilroy attractor serve` — REST + SSE, **no auth** (localhost-oriented); human-gate questions over HTTP |
| **Prereqs** | Go 1.25+, clean working tree for run, **CXDB** (with optional Docker autostart scripts in repo) |
| **License** | MIT |

## Spec alignment

Kilroy explicitly documents parity/delta vs **StrongDM Attractor** specs ([strongdm/attractor](https://github.com/strongdm/attractor)) and references **CXDB** ([strongdm/cxdb](https://github.com/strongdm/cxdb)).

## URLs

- https://github.com/danshapiro/kilroy  
- https://github.com/strongdm/attractor  
- https://github.com/strongdm/cxdb  
