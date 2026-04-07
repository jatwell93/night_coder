# Research folder — summary tables

**Web follow-up (April 2026):** Delegated web research with cited sources, nine topic findings files, and a synthesized report live in [`research_overnight_stack_web/`](./research_overnight_stack_web/) — start with [`research_report.md`](./research_overnight_stack_web/research_report.md) and [`research_plan.md`](./research_overnight_stack_web/research_plan.md).

**Gap wave 2** (OpenJudge canonical `py-openjudge`, opencode→openagent redirect, Ruflo #1335 / Gas Town #24, OpenHands hardening, LocalStack + Browserless): [`research_overnight_stack_web/gap_wave2/research_report_gaps_wave2.md`](./research_overnight_stack_web/gap_wave2/research_report_gaps_wave2.md).

**DTU expanded landscape** (WireMock, Hoverfly, Prism, Microcks, multi-protocol mocks, etc.): [`research_overnight_stack_web/findings_dtu_extended_landscape.md`](./research_overnight_stack_web/findings_dtu_extended_landscape.md).

**Quint pillar sprints (repository root):** Later focused web research for pilot decisions, each with `research_plan.md`, `findings_*.md`, and `research_report.md` (see `docs/superpowers/pilot/*/IMPLEMENTATION-BRIEF.md` for links). Folders: [`research_model_provider_pillar/`](../research_model_provider_pillar/), [`research_memory_pillar/`](../research_memory_pillar/), [`research_execution_sandbox/`](../research_execution_sandbox/), [`research_secrets_iam/`](../research_secrets_iam/), [`research_artifact_registry/`](../research_artifact_registry/). *Planner* (`dec-20260406-005`) drew on existing `Research/` notes and Spec Kit upstream rather than a separate sprint folder.

---

Quick reference for overnight / plan-and-delegate agent stacks, grouped by the StrongDM-style pillars: **orchestration (Attractor)**, **guardrails (Leash)**, **digital twins (DTU)**, **LLM judge**, **context & traces (CXDB)**, plus **observability** and **complementary tools**.

For each topic, open the linked file under `Research/` for the full write-up.

---

## 1. Master index (by pillar)

| Pillar | Topic | Primary file(s) | One-line summary | StrongDM-style fit |
| ------ | ----- | --------------- | ---------------- | ------------------ |
| **Reference** | StrongDM Software Factory | `strongdm_deepseek.md`, `strongdm_perplexity.md` | Non-interactive dev: external **scenarios**, **DTU**, **satisfaction** judging, spec-heavy **attractor**; solo budget adaptation with OSS | Full mental model; map other rows to this |
| **Orchestration** | OpenHands | `openhands_deepseek.md`, `openhands_deepwiki.md`, `openhands_perplexity.md` | Autonomous coding platform: Docker sandbox, event stream for async review, CLI/SDK for headless VPS runs | Strong **Attractor** + sandbox; add external scenarios + judge |
| **Orchestration** | AG2 (AutoGen) | `ag2_deepseek.md`, `ag2_perplexity.md`, `ag2_notebooklm.md` | Group chat, feedback loops (plan → code → critic → revise), `ContextVariables` | **Attractor** patterns; doc recommends **LangGraph** for long-run checkpointing |
| **Orchestration** | Deer Flow | `deer_flow_deepseek.md`, `deer_flow_perplexity.md` | Integrated harness: sandbox, parallel sub-agents, SKILL.md, memory JSON, context middleware | **Attractor** + skills; replicate with CrewAI/queue + Docker + vector memory |
| **Orchestration** | CrewAI | `crewai_deepseek.md`, `crewai_perplexity.md` | Role-based agents, **Flows** for conditional orchestration, YAML agents/tasks | Strong **Attractor**; pair with LangGraph or Langfuse for control/trace |
| **Orchestration** | AgentFlow | `agent_flow_deepseek.md`, `agent_flow_deepwiki.md`, `AgentFlow_perplexity_updated.md`, `agent_flow_perplexity.md` | Modular planner/executor/verifier + Flow-GRPO idea; verification loop | **Attractor** + verifier; ties to decomposition and budgets |
| **Orchestration** | Gas Town | `gas_town_deepseek.md`, `gas_town_perplexity.md`, `gas_town_deepwiki.md` | Mayor / polecats / beads / convoys — orchestration + persistence metaphor | **Attractor** + task queue + git checkpoints; scale down for cost |
| **Orchestration** | oh-my-opencode | `oh_my_opencode_deepwiki.md` | Phased opencode plugin: Prometheus → Atlas, ralph-loop, hooks | **Attractor** strong; **CXDB**/audit weak; **Leash** shallow; no DTU; Momus ≠ outcome judge |
| **Orchestration** | Ralph orchestrator | `ralph-orchestrator.md` | Ralph loop, hats, `.agent/events.jsonl`, iteration/cost/runtime limits | **Attractor** + **CXDB** (files) + **Leash**; no DTU/judge |
| **Orchestration** | Ruflo (claude-flow) | `ruflo_deepwiki.md` | Daemon + headless Claude Code workers, anti-drift topology, vector memory | **Attractor** + overnight daemon; depends on Claude Code / API |
| **Orchestration** | Agent Flywheel (ACFS) | `agent_flywheel_deepwiki.md`, `agent_flywheel_perplexity.md`, `agent_flywheel_perplexity_updated.md`, `agent_flywheel_gemini.md` | NTM, MCP mail / leases, CASS memory, UBS | Coordination + **Leash**-ish; still pays for underlying agent CLIs |
| **Guardrails & sessions** | NTM | `ntm.md` | Tmux agent cockpit: audit logs, policy engine (block dangerous git/rm), pipeline/swarm YAML | **Leash** + **CXDB** strong; **Attractor** partial (session-oriented) |
| **DTU / mocks** | Mockoon | `mockoon.md` | Local mock APIs, CLI/Docker, unlimited routes | **DTU** for HTTP-style deps |
| **DTU / mocks** | Keploy | `keploy.md` | Record-replay traffic (eBPF), DB/queues + HTTP, offline replay | **DTU** from real traces; watch mock coverage gaps |
| **DTU / mocks** | MSW | `msw.md` | Network-level intercept; same handlers in browser + Node tests | **DTU** in-app/tests; great for TS/JS stacks |
| **DTU / mocks** | WireMock | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | HTTP mock; Docker/standalone; templating, faults, **record/replay**; **WireMock MCP** for agent-assisted mocks | **DTU** HTTP; strong parity with Mockoon + deeper simulation |
| **DTU / mocks** | Hoverfly | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | Go proxy **capture/simulate**; export simulations; latency and failure injection | **DTU** when proxy-first record beats hand-written routes |
| **DTU / mocks** | MockServer | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | Java Netty HTTP(S) mock + **proxy**; official Docker image | **DTU** HTTP; JVM footprint vs Mockoon/Hoverfly |
| **DTU / mocks** | Mountebank | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | Multi-protocol **imposters** (HTTP, TCP, SMTP, …); dynamic stubs via REST API | **DTU** beyond HTTP in one process |
| **DTU / mocks** | Prism (Stoplight) | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | Mock + validate from **OpenAPI** and **Postman** collections | **DTU** when spec is the contract of record |
| **DTU / mocks** | Pact stub server | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | Serves responses from **Pact** files (dir, URL, or Broker) | **DTU** for consumer-driven contract workflows |
| **DTU / mocks** | Microcks | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | Platform: OpenAPI, **AsyncAPI**, gRPC, GraphQL, SOAP; Helm/K8s; async (e.g. Kafka) mocks | **DTU** at factory scale; heavier ops than single-container mocks |
| **DTU / mocks** | Imposter | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | Scriptable mocks (JS/Groovy/Java); OpenAPI, SOAP, Salesforce-oriented plugins | **DTU** when responses need scripted logic without a full platform |
| **DTU / mocks** | Karate (Netty mock) | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | Standalone JAR mock server; stateful CRUD-style behavior; proxy mode | **DTU** if stack already centered on Karate |
| **DTU / mocks** | Mockintosh | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | REST mocks + **Kafka/RabbitMQ** scenarios | **DTU** when async brokers are part of the twin |
| **Complementary** | Agent VCR | `research_overnight_stack_web/findings_dtu_extended_landscape.md` | Record/replay **MCP** JSON-RPC (cassettes) for agent-tool tests | **Not** HTTP DTU — complements tooling tests; see findings §E |
| **Judge & scenarios** | OpenJudge | `OpenJudge.md` | LLM graders, `GraderScore`, trace graders, Langfuse integration | **LLM Judge** + scenario params |
| **Judge & scenarios** | Dify | `dify.md` | Full LLM app platform | **Not** recommended as embedded judge (heavy, redundant with CrewAI) |
| **Judge & scenarios** | AgentScope | `agentscope.md` | Tuner judges (RL), benchmark metrics, trajectory-aware eval, Ray + OTEL | Judge/eval **patterns**; different primary use than OpenJudge |
| **Judge & scenarios** | Build scenario harness | `build-yourself-one.md` (see also `strongdm_deepseek.md`) | External `.scenario.md`, agent-proof store, custom LLM judge | **Scenarios + Judge** spec; no product — you assemble |
| **Observability** | Langfuse | `langfuse_deep_wiki.md` | Traces, tool spans, sessions, built-in LLM-as-judge evals | **CXDB**-grade morning review + optional judge |
| **Observability** | OpenLLMetry | `openllmetry.md` | OTEL instrumentation for LLMs, CrewAI hooks, MCP tools | **CXDB** via backends; manual spans for arbitrary shell/git |
| **Complementary** | Aider | `aider_deepwiki.md` | Terminal git-centric pair, repo map, architect/editor split | Optional worker alongside VPS orchestration |
| **Meta** | Working notes | `Table.md` | Informal comparisons (ag2, agent flow, crewAI, strongdm, …) | Scratchpad — prefer this doc for navigation |
| **Meta** | Prompt template | `questions.md` | Reusable “analyse X for $60/mo overnight autonomy” prompt | Not a tool summary |

---

## 2. Orchestration comparison (overnight / delegation lens)

| Topic | Headless / VPS | Multi-agent | Persistence / recovery | Your notes (from `Table.md` + research) |
| ----- | -------------- | ----------- | ---------------------- | ---------------------------------------- |
| **OpenHands** | Yes (CLI/SDK, tmux) | Yes | Docker + event stream | Async review via event log |
| **AG2** | You host | Yes | In-memory + patterns; LangGraph suggested for checkpoints | Critic loop matches “broader fix” worry |
| **Deer Flow** | DIY on VM | Sub-agents + queue story | Memory file + DB suggestion | Mirrors managed harness in OSS pieces |
| **CrewAI** | You host | Yes (Flows) | External DB recommended | Good for Judge role; hand off after N test failures |
| **AgentFlow** | Via OpenHands stack in doc | Planner/executor/verifier | Redis/SQLite | Budgets, Flow-GRPO as ideal |
| **Gas Town** | Sacrifice parallelism | Mayor / workers | Git + task JSON | Town wall, spawn minimal context |
| **oh-my-opencode** | Opencode session | Sisyphus / Atlas / Prometheus | Tasks on disk; not full audit DB | Strong phases; not full safety/DTU/judge |
| **Ralph** | Bash/agent loop | Hats | JSONL + scratchpad | Caps: iterations, time, cost |
| **Ruflo** | Background daemon | Workers + topology | PID file, logs, memory pipeline | Anti-drift coordinator |
| **Agent Flywheel** | NTM + sessions | Swarm / mail | Leases, CASS | Easiest setup per notes; no built-in judge |

---

## 3. StrongDM five-piece coverage (at a glance)

| Piece | StrongDM idea | Well-covered in research by |
| ----- | ------------- | ---------------------------- |
| **Attractor** | Phased autonomous execution | OpenHands, CrewAI, AG2/LangGraph, Deer Flow, Gas Town, Ralph, oh-my-opencode, Ruflo |
| **Leash** | Block dangerous tools / abuse | NTM (strong); Ralph (limits); oh-my-opencode (hooks only); Ruflo (sandbox modes) |
| **DTU** | Local mocks / twins | Mockoon, Keploy, MSW; WireMock, Hoverfly, MockServer, Mountebank, Prism, Pact stub, Microcks, Imposter, Karate mock, Mockintosh ([`findings_dtu_extended_landscape.md`](./research_overnight_stack_web/findings_dtu_extended_landscape.md)); gap wave 2: LocalStack, Browserless / Playwright |
| **LLM judge** | Scenario satisfaction | OpenJudge, Langfuse evals, build-yourself harness; not Momus (plan-only) |
| **CXDB** | Traces + memory | Langfuse, OpenLLMetry, Ralph files, NTM audit; partial everywhere else |

---

## 4. File checklist (all `Research/` markdown)

| File | Typical pillar |
| ---- | -------------- |
| `strongdm_deepseek.md`, `strongdm_perplexity.md` | Reference |
| `openhands_deepseek.md`, `openhands_deepwiki.md`, `openhands_perplexity.md` | Orchestration |
| `ag2_deepseek.md`, `ag2_perplexity.md`, `ag2_notebooklm.md` | Orchestration |
| `deer_flow_deepseek.md`, `deer_flow_perplexity.md` | Orchestration |
| `crewai_deepseek.md`, `crewai_perplexity.md` | Orchestration |
| `agent_flow_deepseek.md`, `agent_flow_deepwiki.md`, `agent_flow_perplexity.md`, `AgentFlow_perplexity_updated.md` | Orchestration |
| `gas_town_deepseek.md`, `gas_town_perplexity.md`, `gas_town_deepwiki.md` | Orchestration |
| `oh_my_opencode_deepwiki.md` | Orchestration |
| `ralph-orchestrator.md` | Orchestration + CXDB + Leash |
| `ruflo_deepwiki.md` | Orchestration + overnight daemon |
| `agent_flywheel_deepwiki.md`, `agent_flywheel_perplexity.md`, `agent_flywheel_perplexity_updated.md`, `agent_flywheel_gemini.md` | Orchestration / coordination |
| `ntm.md` | Leash + CXDB |
| `mockoon.md`, `keploy.md`, `msw.md` | DTU |
| `research_overnight_stack_web/findings_dtu_extended_landscape.md` | DTU (expanded) + Agent VCR (complementary) |
| `OpenJudge.md`, `dify.md`, `agentscope.md` | Judge / eval |
| `build-yourself-one.md` | Scenarios + judge (how-to) |
| `langfuse_deep_wiki.md`, `openllmetry.md` | Observability |
| `aider_deepwiki.md` | Complementary CLI coding |
| `Table.md`, `questions.md` | Meta |

---

## 5. Suggested planning order

1. **Anchor on outcomes**: external scenarios + judge (`strongdm_deepseek.md`, `build-yourself-one.md`, `OpenJudge.md`).
2. **Pick one orchestration spine**: OpenHands *or* CrewAI+LangGraph *or* Ralph *or* oh-my-opencode — match to how much you want GUI vs Python vs opencode.
3. **Add DTU** per stack: start from [`findings_dtu_extended_landscape.md`](./research_overnight_stack_web/findings_dtu_extended_landscape.md) (Mockoon, WireMock, Hoverfly, Keploy, MSW, Prism, …); add LocalStack / Browserless when AWS- or browser-shaped deps appear ([`gap_wave2/findings_gap_dtu_localstack_browserless.md`](./research_overnight_stack_web/gap_wave2/findings_gap_dtu_localstack_browserless.md)).
4. **Add Leash** where the harness is weak (NTM, Ralph limits, custom allowlists).
5. **Instrument** (Langfuse and/or OpenLLMetry) so morning review replaces live watching.

This document is the navigation layer; depth stays in the per-topic files above.

---

## Official / 2026 links

- [Web research report](research_overnight_stack_web/research_report.md) · [Research plan](research_overnight_stack_web/research_plan.md)
- [Gap wave 2 synthesis](research_overnight_stack_web/gap_wave2/research_report_gaps_wave2.md)
- [DTU extended landscape](research_overnight_stack_web/findings_dtu_extended_landscape.md)
