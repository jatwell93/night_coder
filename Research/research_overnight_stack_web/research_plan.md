# Web research plan: overnight agent stack topics

## Main question

What is the current state (2025–2026) of each tool and pattern in the Research summary table for **autonomous / overnight coding**: orchestration, guardrails, digital-twin mocks, LLM-as-judge, and observability? Focus on headless or VPS operation, official docs/releases, and integration angles for a StrongDM-style stack.

## Subtopics (9 files, 3 subagents per wave)

| # | Subtopic file | Scope | Expected output |
|---|---------------|-------|-----------------|
| 1 | `findings_reference_strongdm_opensource.md` | StrongDM Software Factory blog/product updates; open-source **attractor** / **CXDB** if any; related “non-interactive dev” discourse | URLs, what is shipping vs aspirational |
| 2 | `findings_orchestration_openhands_crewai_ag2.md` | OpenHands CLI/headless/VPS; CrewAI Flows; AG2 (Microsoft); LangGraph checkpointing for long runs | Install paths, version notes, caveats |
| 3 | `findings_orchestration_deer_agentflow_gas.md` | Deer Flow (harness); AgentFlow (Flow-GRPO / arXiv); Gas Town / Steve Yegge public writeups | Product vs research, cost model hints |
| 4 | `findings_orchestration_opencode_ralph_ruflo_flywheel.md` | oh-my-opencode; Ralph orchestrator (mikeyobrien); Ruflo / claude-flow; Agent Flywheel / ACFS | GitHub activity, overnight/daemon claims |
| 5 | `findings_guardrails_ntm.md` | NTM (Named Tmux Manager): policies, audit, agent workflows | Fit for “Leash” layer |
| 6 | `findings_dtu_mockoon_keploy_msw.md` | Mockoon CLI/Docker; Keploy record-replay; MSW 2.x / Node | Best-for matrix, 2025 updates |
| 7 | `findings_judge_openjudge_agentscope_dify.md` | OpenJudge; AgentScope eval; why Dify is/is not a judge microservice | APIs, lightweight alternatives |
| 8 | `findings_observability_langfuse_openllmetry.md` | Langfuse agent tracing + evals; OpenLLMetry (Traceloop) CrewAI | Self-host, OTEL export |
| 9 | `findings_complementary_aider_scenarios.md` | Aider watch/automation; industry “external scenarios” / LLM judge patterns beyond StrongDM | Practical links |

## Synthesis

Merge into `research_report.md`: table mapping each summary-table row → 2–4 bullet updates + citations; gaps and contradictions; suggested follow-up experiments.
