# Research report: Fabro & Kilroy vs overnight pilot and v1 options

## Executive summary

**Fabro** and **Kilroy** both implement **workflow-as-code** using **Graphviz DOT** graphs with **multi-turn coding agents** at nodes, **human gates**, and **checkpointed** progress—closely aligned with the **StrongDM “Attractor”** ideas already in your `Research/Research_Summary_Table.md`. They differ mainly in **packaging and runtime**: Fabro is **Rust / single binary**, **cloud-sandbox-first** (Daytona), with a **productized API + UI**; Kilroy is **Go**, **local-repo-first**, with **CXDB** as the run ledger and **git worktrees + per-node commits** as the code ledger.

Your **pilot** centers **Ralph** as the orchestrator (hats, events, JSONL, limits) plus **orthogonal pillars**: **OpenJudge**, **WireMock DTU**, **Langfuse/OpenLLMetry**, **NTM**—none of which Fabro/Kilroy replace end-to-end. A **v1** move to **CrewAI** or **OpenHands** addresses *different* layers (Python agent framework vs autonomous coding runtime); **Fabro/Kilroy** are closer to **replacing or wrapping the orchestration subgraph** than to replacing the judge or mocks.

---

## 1. Fabro vs Kilroy (side by side)

| Dimension | Fabro | Kilroy |
| --------- | ----- | ------ |
| **Language / delivery** | Rust; one binary | Go; `kilroy` CLI (`brew`, `go install`) |
| **Workflow definition** | DOT + graph-level model stylesheet | DOT; StrongDM-oriented semantics |
| **Primary execution locus** | **Cloud sandboxes** (Daytona) emphasized | **Local git worktree** + run branch |
| **Run / audit store** | Git checkpoints + run metadata (retros) | **CXDB** (events + blobs) + git per-node commits |
| **Remote / UI** | REST + SSE, React UI, 24/7 API server | Experimental `serve` (localhost, no auth) |
| **Ingest (NL → graph)** | Natural-language specs mentioned; “generate implementations” | `attractor ingest` via **Claude CLI** + skill |
| **Multi-provider story** | CSS-like routing, fallbacks, cost routing | Explicit provider plugins; API vs CLI per provider |
| **Maturity signal** | Tagged releases (e.g. v0.176.x cited on snapshot) | README notes **no releases published** (snapshot) |

**Conclusion:** Same **paradigm** (graph + agents + gates); different **operational sweet spot**. Fabro optimizes for **team-scale, cloud-isolated, always-on** runs. Kilroy optimizes for **spec-faithful Attractor + CXDB** and **local reproducibility** with a heavier **data-plane** (CXDB) dependency.

---

## 2. How this maps to your pilot

From `Research/Research_Summary_Table.md` and pilot docs, the overnight stack is roughly:

| Pillar | Pilot choice | Role |
| ------ | -------------- | ---- |
| **Orchestration** | **Ralph** (CLI, hats, `.agent/events.jsonl`) | Loop controller, backends, cost/iteration caps |
| **Judge** | **OpenJudge** (`py-openjudge`) | External scenario + trace scoring (dec-20260406-003) |
| **DTU** | **WireMock** (and related) | Dependency mocks |
| **Leash / session** | **NTM** | Policy + audit-oriented agent cockpit |
| **Observability** | **Langfuse** + OpenLLMetry | Traces, export |

**Fabro** explicitly lists **LLM-as-judge** inside the **workflow graph** as a verification layer. That is **conceptually similar** to your judge pillar but **not interchangeable** with OpenJudge’s chosen **headless Python grader + schema** without a custom integration (export traces into a node, call your grader, branch on score).

**Kilroy** focuses on **stage artifacts** (`prompt.md`, `response.md`, `status.json`, archives). That is **CXDB-grade** run history—**analogous** to what you want for morning review, but again **not** your Langfuse/OpenJudge wiring out of the box.

**Neither** product is your **WireMock DTU**; both assume agents talk to real tools/APIs inside sandboxes or local trees.

**Alignment note:** Your research already treats **StrongDM-style attractors** as the mental model for orchestration. **Kilroy** is the most literal OSS implementation of that spec line in this pair; **Fabro** is the same **idea family** with a **different** execution and distribution story.

---

## 3. Pilot vs a hypothetical v1 (CrewAI / OpenHands)

| Option | What it is | vs Fabro/Kilroy | vs your pilot |
| ------ | ---------- | ---------------- | ------------- |
| **Pilot (Ralph)** | Event-driven orchestrator with hats/backends | **Not graph-native** in DOT; process lives in Ralph config and conventions | Baseline you are implementing on VPS |
| **CrewAI** | Python framework: agents, tasks, **Flows** | **Programmatic** orchestration; you embed graphs in code or build your own DAG—**no single DOT file** as source of truth unless you add it | Strong for **role separation** and **conditional flows**; you still add **judge, DTU, observability** |
| **OpenHands** | Full **coding agent platform** (Docker sandbox, SDK/CLI, events) | **Heavy execution environment** + agent; **not** primarily a DOT workflow engine | Strong **headless VPS** story; overlaps **sandbox** with Fabro’s Daytona story but with a **different** product surface |
| **Fabro** | DOT workflows + cloud sandboxes + API/UI | **Highest** “software factory” packaging; **opinionated** cloud path | Could **replace Ralph’s loop** for teams that want **explicit graphs** and **managed isolation**; still need **your** judge/DTU decisions or embed analogs in-graph |
| **Kilroy** | Local Attractor runner + CXDB | **Closest OSS to StrongDM pipeline spec** in-repo | Fits **self-hosted VPS** if you accept **CXDB** ops; **Ralph → Kilroy** is a **paradigm shift** (DOT + CXDB vs Ralph events) |

---

## 4. Practical takeaways

1. **If the goal is “StrongDM-style attractor on a repo”** — **Kilroy** is the more **literal** research vehicle; **Fabro** is the more **productized** alternative with **cloud sandboxes** and less emphasis on CXDB in the README.
2. **If the goal is “upgrade path from Ralph”** — neither is a **drop-in**; both imply **re-expressing** control flow as **DOT** and adopting their **runtime** (Daytona/Fabro vs CXDB+worktrees/Kilroy). Ralph’s **hats/backends** map more naturally to **CrewAI roles** or **OpenHands sessions** than to DOT **without** a migration project.
3. **Judge / OpenJudge** — stays a **separate concern** unless you **embed** scoring as **graph nodes** and bridge outputs to your **JSON schema** (`satisfied`, `score`, `reasoning`).
4. **VPS overnight** — **Kilroy’s** local-first + optional autostart scripts may **fit small VMs** if CXDB cost is acceptable; **Fabro’s** cloud sandboxes may **reduce** what runs on your droplet but **add** external dependency and network policy work.

---

## 5. Gaps and limitations

- READMEs are authoritative for **marketing claims**; **production** characteristics (scale limits, CXDB ops, Daytona billing) need evaluation in your environment.
- **Kilroy** experimental HTTP server **lacks authentication**—same class of caveat as any localhost admin surface.
- **Fabro** contribution model is **issue-only PRs**—forking is the path for deep customization.

---

## Source list

- [fabro-sh/fabro](https://github.com/fabro-sh/fabro)  
- [danshapiro/kilroy](https://github.com/danshapiro/kilroy)  
- [strongdm/attractor](https://github.com/strongdm/attractor) (referenced by Kilroy)  
- [strongdm/cxdb](https://github.com/strongdm/cxdb) (referenced by Kilroy)  
- Internal: `Research/Research_Summary_Table.md`, `docs/superpowers/pilot/runbooks/vps-ralph-install.md`, `.quint/decisions/dec-20260406-003.md`
