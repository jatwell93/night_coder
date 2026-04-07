# Web research report: overnight agent stack (April 2026)

This report synthesizes delegated web research per `research_plan.md`. Detailed quotes and URL tables live in the nine `findings_*.md` files in this folder.

**Sources folder:** [./](./) · **Plan:** [research_plan.md](./research_plan.md)

---

## Executive summary

- **StrongDM** continues to publish a coherent public story: [factory.strongdm.ai](https://factory.strongdm.ai/) (scenarios as holdouts, **satisfaction** as probabilistic validation, **DTU**, principles loop). **CXDB**, **Leash**, and **Attractor** have explicit product pages and **Apache 2.0** repos ([github.com/strongdm/cxdb](https://github.com/strongdm/cxdb), [github.com/strongdm/leash](https://github.com/strongdm/leash)); [attractorbench](https://github.com/strongdm/attractorbench) exists for compliance-style benchmarking. Your “assemble from OSS” strategy aligns with what they have actually open-sourced versus narrative-only pieces.

- **OpenHands** is the strongest **documented** path for true **headless** runs: [`openhands --headless`](https://docs.all-hands.dev/openhands/usage/cli/headless), **`always-approve`**, **`--json` JSONL**, plus **Software Agent SDK** and **remote Agent Server** ([overview](https://docs.all-hands.dev/sdk/guides/agent-server/overview)) for Docker/K8s/VM. Treat headless as high-trust: no interactive approval.

- **CrewAI Flows** remain the vendor-documented way to add branching, loops, and shared state ([concepts](https://docs.crewai.com/concepts/flows)); enterprise changelog items (e.g. **v1.13.0** SSO/RBAC, Flow as Pydantic) matter if your VPS runs are governed.

- **AG2** docs plus Microsoft’s **LangGraph-backed agent cookbook** ([link](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/cookbook/langgraph-agent.html)) support your existing note that **LangGraph** is the persistence/checkpoint layer for long jobs.

- **Deer Flow** is a real **MIT** OSS harness ([github.com/bytedance/deer-flow](https://github.com/bytedance/deer-flow), [deerflow.tech](https://deerflow.tech/)); cost is **BYO API**, not a DeerFlow subscription in sources checked.

- **AgentFlow** in *your* table means the **Stanford / Flow-GRPO / ICLR 2026** line ([agentflow.stanford.edu](https://agentflow.stanford.edu/), [arXiv 2510.05592](https://arxiv.org/html/2510.05592)) — not vendor “agent flow” UIs; disambiguation is essential in web search.

- **Gas Town** is **Steve Yegge**, **Go**, **MIT** ([github.com/steveyegge/gastown](https://github.com/steveyegge/gastown)), Claude-Code-centric; [issue #24](https://github.com/steveyegge/gastown/issues/24) documents **cost visibility** pain (tmux vs programmatic accounting).

- **oh-my-opencode** / **ralph-loop**: active GitHub work (e.g. [PR #1348](https://github.com/code-yeongyu/oh-my-opencode/pull/1348) on `reset` vs `continue` strategies). Verify naming against **oh-my-openagent** if READMEs move.

- **Ralph Orchestrator** docs ([site](https://mikeyobrien.github.io/ralph-orchestrator/)) reinforce **iteration, runtime, cost, loop-detection** limits for overnight safety.

- **Ruflo** / **claude-flow**: daemon/worker patterns on GitHub; check open issues ([#1335](https://github.com/ruvnet/ruflo/issues/1335)) before relying on scheduler metrics for production unattended runs.

- **NTM** exposes **policy YAML**, **`ntm safety check`**, **audit** subcommands, and **pipeline YAML** — a credible **Leash + CXDB (audit)** layer for tmux-centric workflows; see [findings_guardrails_ntm.md](./findings_guardrails_ntm.md).

- **DTU trio:** **Mockoon** (CLI/Docker, local servers), **Keploy** (eBPF record-replay, broader infra virtualization), **MSW 2** (in-process Node/browser interception, shared handlers) — complementary, not interchangeable; see [findings_dtu_mockoon_keploy_msw.md](./findings_dtu_mockoon_keploy_msw.md).

- **OpenJudge** + **Langfuse/LangSmith** integrations are documented for trace-backed grading; **AgentScope** documents OpenJudge as the “rich judge” extension ([tutorial](https://doc.agentscope.io/tutorial/task_eval_openjudge.html)). **Dify** remains a **full app platform** — still a poor fit as a *microservice judge* unless you already run Dify for other reasons.

- **Langfuse** supports **sessions**, **LLM-as-judge** scores (including categorical judges per 2026 changelog notes in findings), **self-host**, and **OTLP ingest** at `/api/public/otel` ([OTEL docs](https://langfuse.com/docs/opentelemetry)); **OpenLLMetry** is explicitly named as compatible instrumentation feeding Langfuse.

- **Aider**: **scripting** (`--message`, `--message-file`, `--yes`) is the unattended path; **watch** mode has reported edge cases ([issues #2586](https://github.com/Aider-AI/aider/issues/2586), [#2717](https://github.com/Aider-AI/aider/issues/2717)). Extra judge-harness links: [microsoft/llm-as-judge](https://github.com/microsoft/llm-as-judge), [haizelabs/verdict](https://github.com/haizelabs/verdict), etc., in [findings_complementary_aider_scenarios.md](./findings_complementary_aider_scenarios.md).

---

## Topic table (maps to `Research_Summary_Table.md`)

| Topic | What changed or confirmed (web) | Primary links | Deep dive file |
| ----- | -------------------------------- | ------------- | -------------- |
| **StrongDM** | Public factory site + blog quotes; CXDB/Leash/Attractor repos; attractorbench | [factory.strongdm.ai](https://factory.strongdm.ai/), [strongdm/cxdb](https://github.com/strongdm/cxdb), [strongdm/leash](https://github.com/strongdm/leash) | findings_reference_strongdm_opensource.md |
| **OpenHands** | Headless CLI + JSONL; SDK + remote agent server; Docker workspace images | [Headless CLI](https://docs.all-hands.dev/openhands/usage/cli/headless), [SDK index](https://docs.all-hands.dev/sdk/index) | findings_orchestration_openhands_crewai_ag2.md |
| **CrewAI** | Flows docs; enterprise/RBAC/SSO changelog line | [Flows](https://docs.crewai.com/concepts/flows), [changelog](https://docs.crewai.com/changelog) | findings_orchestration_openhands_crewai_ag2.md |
| **AG2** | Group chat; official LangGraph cookbook | [docs.ag2.ai](https://docs.ag2.ai/latest/docs/home/), [LangGraph agent](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/cookbook/langgraph-agent.html) | findings_orchestration_openhands_crewai_ag2.md |
| **Deer Flow** | ByteDance OSS SuperAgent harness; BYO cost | [github.com/bytedance/deer-flow](https://github.com/bytedance/deer-flow) | findings_orchestration_deer_agentflow_gas.md |
| **AgentFlow** | Stanford Flow-GRPO; arXiv + ICLR poster | [agentflow.stanford.edu](https://agentflow.stanford.edu/) | findings_orchestration_deer_agentflow_gas.md |
| **Gas Town** | Yegge Go orchestrator; cost tracking issue | [gastown](https://github.com/steveyegge/gastown) | findings_orchestration_deer_agentflow_gas.md |
| **oh-my-opencode** | ralph-loop PR/issue activity | [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) | findings_orchestration_opencode_ralph_ruflo_flywheel.md |
| **Ralph** | Docs: limits, hats, completion markers | [ralph-orchestrator](https://mikeyobrien.github.io/ralph-orchestrator/) | findings_orchestration_opencode_ralph_ruflo_flywheel.md |
| **Ruflo** | Daemon; open scheduler issues | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | findings_orchestration_opencode_ralph_ruflo_flywheel.md |
| **Agent Flywheel** | ACFS skills repo, NTM skill, mcp_agent_mail | [agent_flywheel…](https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations) | findings_orchestration_opencode_ralph_ruflo_flywheel.md |
| **NTM** | Policy, audit, pipelines | [Dicklesworthstone/ntm](https://github.com/Dicklesworthstone/ntm) (verify live README) | findings_guardrails_ntm.md |
| **Mockoon / Keploy / MSW** | CLI/Docker; eBPF replay; MSW 2 Node | [mockoon.com/cli](https://mockoon.com/cli/), [keploy.io/docs](https://keploy.io/docs/), [mswjs.io](https://mswjs.io/docs/integrations/node/) | findings_dtu_mockoon_keploy_msw.md |
| **OpenJudge** | Graders + Langfuse/LangSmith | [OpenJudge docs](https://agentscope-ai.github.io/OpenJudge/) | findings_judge_openjudge_agentscope_dify.md |
| **AgentScope** | Eval tutorial + OpenJudge bridge | [task_eval](https://doc.agentscope.io/tutorial/task_eval.html) | findings_judge_openjudge_agentscope_dify.md |
| **Dify** | Still full-stack; external LLMOps integrations | [docs.dify.ai](https://docs.dify.ai/) | findings_judge_openjudge_agentscope_dify.md |
| **Langfuse** | Sessions, judge scores, OTLP ingest | [langfuse.com/docs](https://langfuse.com/docs/observability/data-model) | findings_observability_langfuse_openllmetry.md |
| **OpenLLMetry** | CrewAI instrumentation; MCP; → Langfuse | [traceloop docs](https://www.traceloop.com/docs/openllmetry) (verify); Langfuse OTEL example | findings_observability_langfuse_openllmetry.md |
| **Aider** | Scripting vs watch caveats; architect split | [scripting](https://aider.chat/docs/scripting.html) | findings_complementary_aider_scenarios.md |
| **Build scenario harness** | No new product; reinforced by StrongDM + OpenJudge patterns | (conceptual) | build-yourself-one.md + this report |

---

## Gap wave 2 (closed items)

Targeted follow-up research lives in **[`gap_wave2/`](./gap_wave2/)** — start with **[`gap_wave2/research_report_gaps_wave2.md`](./gap_wave2/research_report_gaps_wave2.md)**.

**Resolved or narrowed:**

- **OpenJudge:** use **`pip install py-openjudge`**; canonical repo **`agentscope-ai/OpenJudge`**; avoid PyPI package name `openjudge` (wrong project).
- **oh-my-opencode:** **301 redirect** to **`code-yeongyu/oh-my-openagent`**; default branch **`dev`**; see PR #2417 / issue #2823.
- **Ruflo #1335:** **closed**; fixes from **`v3.5.22`** / **claude-flow#1365**.
- **Gas Town cost:** org **`gastownhall/gastown`**; **PR #941** transcript-based usage; **#24** may stay open as umbrella; no confirmed `CLAUDE_SESSION_COST` from Claude Code in thread.
- **OpenHands prod:** headless **`always-approve`** documented; **`~/.openhands/agent_settings.json`**; security advisories and issues linked in gap findings.
- **DTU gap:** **LocalStack** + **Browserless** / **Playwright** official paths documented in **`findings_gap_dtu_localstack_browserless.md`**.

---

## Gaps and limitations

- **Search budget:** Each subtopic used only **3–5** web queries; star counts, version numbers, and third-party blog claims should be **re-verified** on official docs at implementation time.

- **Canonical repos:** **OpenJudge** — see **gap wave 2** (`py-openjudge` vs unrelated `openjudge`).

- **oh-my-opencode vs oh-my-openagent:** **resolved** — rename + redirect; see gap wave 2.

- **Ruflo / Gas Town:** **partially resolved** — upgrade Ruflo/claude-flow for daemon fixes; Gas Town cost path moved toward transcript JSONL (**PR #941**); still validate in your environment.

- **No legal/compliance review:** self-hosting (Langfuse, Dify, Keploy, LocalStack tier) still needs your own security and data-policy review.

---

## Suggested next experiments (1–2 weeks)

1. **Minimal vertical slice:** OpenHands headless **or** Ralph on a VPS + **one** Mockoon service + **one** external `.scenario.md` scored by OpenJudge or Langfuse eval.

2. **Trace wiring:** Instrument the same run with **OpenLLMetry → Langfuse OTLP** and confirm morning review covers **tool** spans for `pytest`/`git`.

3. **Policy layer:** If using tmux multi-agent, trial **NTM** `policy.yaml` + `ntm safety check` in CI before enabling full daemon loops.

---

## Findings file index

| File |
| ---- |
| [findings_reference_strongdm_opensource.md](./findings_reference_strongdm_opensource.md) |
| [findings_orchestration_openhands_crewai_ag2.md](./findings_orchestration_openhands_crewai_ag2.md) |
| [findings_orchestration_deer_agentflow_gas.md](./findings_orchestration_deer_agentflow_gas.md) |
| [findings_orchestration_opencode_ralph_ruflo_flywheel.md](./findings_orchestration_opencode_ralph_ruflo_flywheel.md) |
| [findings_guardrails_ntm.md](./findings_guardrails_ntm.md) |
| [findings_dtu_mockoon_keploy_msw.md](./findings_dtu_mockoon_keploy_msw.md) |
| [findings_judge_openjudge_agentscope_dify.md](./findings_judge_openjudge_agentscope_dify.md) |
| [findings_observability_langfuse_openllmetry.md](./findings_observability_langfuse_openllmetry.md) |
| [findings_complementary_aider_scenarios.md](./findings_complementary_aider_scenarios.md) |

### Gap wave 2 (`gap_wave2/`)

| File |
| ---- |
| [gap_wave2/research_report_gaps_wave2.md](./gap_wave2/research_report_gaps_wave2.md) |
| [gap_wave2/findings_gap_openjudge_canonical.md](./gap_wave2/findings_gap_openjudge_canonical.md) |
| [gap_wave2/findings_gap_opencode_ruflo_gastown.md](./gap_wave2/findings_gap_opencode_ruflo_gastown.md) |
| [gap_wave2/findings_gap_openhands_production.md](./gap_wave2/findings_gap_openhands_production.md) |
| [gap_wave2/findings_gap_dtu_localstack_browserless.md](./gap_wave2/findings_gap_dtu_localstack_browserless.md) |
