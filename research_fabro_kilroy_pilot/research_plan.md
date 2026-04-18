# Research plan: Fabro & Kilroy vs overnight pilot / v1

## Main question

How do [fabro-sh/fabro](https://github.com/fabro-sh/fabro) and [danshapiro/kilroy](https://github.com/danshapiro/kilroy) compare to each other, and how might either relate to the **night_coder overnight pilot** (Ralph, OpenJudge, DTU, Langfuse, NTM) and a plausible **v1** upgrade path (for example CrewAI or OpenHands)?

## Subtopics

1. **Fabro** — product shape, execution model, sandboxing, API/UI, differentiation.
2. **Kilroy** — Attractor alignment, CXDB, local CLI model, provider wiring, gaps vs Fabro.
3. **Pilot / v1 fit** — mapping to pillars from `Research/Research_Summary_Table.md` and pilot runbooks; where these tools substitute, complement, or overlap Ralph/CrewAI/OpenHands.

## Expected outputs per subtopic

| Subtopic | Expected information |
| -------- | -------------------- |
| Fabro | Feature table, install path, workflow-as-graph, cloud vs laptop, sources |
| Kilroy | Commands, CXDB, StrongDM spec link, local-first constraints, sources |
| Fit | Side-by-side: orchestration layer, judge/DTU, ops burden, migration notes |

## Synthesis

Single narrative answering: when Fabro vs Kilroy vs staying on Ralph vs adopting CrewAI/OpenHands; trade-offs for unattended VPS and for graph-defined pipelines.

## Sources

- Repository READMEs: https://github.com/fabro-sh/fabro, https://github.com/danshapiro/kilroy  
- StrongDM Attractor (Kilroy references): https://github.com/strongdm/attractor  
- Project context: `docs/superpowers/pilot/`, `Research/Research_Summary_Table.md`, `dec-20260406-003` (OpenJudge)
