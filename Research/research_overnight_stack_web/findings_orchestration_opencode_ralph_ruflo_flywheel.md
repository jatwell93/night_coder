# Web research: orchestration stack (oh-my-opencode, Ralph, Ruflo/claude-flow, Agent Flywheel)

**Scope:** Short desk research (2025–2026 sources surfaced by web search). **Method:** Up to five web queries; facts below are summaries with primary URLs—verify on the live pages before production decisions.

---

## 1. oh-my-opencode (`code-yeongyu/oh-my-opencode`)

**Canonical / user-specified repo:** [https://github.com/code-yeongyu/oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode)

**Naming note:** Search results also point heavily to **`oh-my-openagent`** under the same org (e.g. README tab and issues/PRs use that path). Treat **`code-yeongyu/oh-my-openagent`** as the same product line if README redirects or the project was renamed—confirm in the repo’s current default branch README.

- **README / overview:** [https://github.com/code-yeongyu/oh-my-opencode?tab=readme-ov-file](https://github.com/code-yeongyu/oh-my-opencode?tab=readme-ov-file) (alternate: [https://github.com/code-yeongyu/oh-my-openagent?tab=readme-ov-file](https://github.com/code-yeongyu/oh-my-openagent?tab=readme-ov-file))
- **Multi-agent:** Described in secondary summaries as a TypeScript “multi-agent harness” orchestrating several model providers (Claude, GPT, Gemini, etc.) rather than a single vendor—**confirm** wording and feature list in the live README.
- **ralph-loop:** Treated as a **built-in command** implementing an iterative agent loop; configuration examples in the ecosystem include JSON such as `ralph_loop.enabled`, `default_max_iterations` (e.g. 100).  
  - **PR (behavior / context):** [fix(ralph-loop): keep LLM in smart zone with fresh context per iteration · PR #1348](https://github.com/code-yeongyu/oh-my-opencode/pull/1348) — introduces or documents a `default_strategy` with modes like **`reset`** (fresh session per iteration to stay in a “smart” context window band) vs **`continue`** (same session across iterations).  
  - **Issue (command loading):** [oh-my-opencode commands not loading (ralph-loop missing) · Issue #952](https://github.com/code-yeongyu/oh-my-openagent/issues/952) — discusses `discoverCommandsSync()` and plugin config for disabled commands (historical debugging context).

---

## 2. Ralph orchestrator & Huntley Ralph

### mikeyobrien / Ralph Orchestrator

- **Project site:** [https://mikeyobrien.github.io/ralph-orchestrator/](https://mikeyobrien.github.io/ralph-orchestrator/)
- **Overview:** [https://mikeyobrien.github.io/ralph-orchestrator/guide/overview/](https://mikeyobrien.github.io/ralph-orchestrator/guide/overview/)
- **Quick start:** [https://mikeyobrien.github.io/ralph-orchestrator/quick-start/](https://mikeyobrien.github.io/ralph-orchestrator/quick-start/)
- **FAQ (limits, completion):** [https://mikeyobrien.github.io/ralph-orchestrator/faq/](https://mikeyobrien.github.io/ralph-orchestrator/faq/)

**Reported design (from docs summaries):**

- Frames Ralph as a **continuous loop** until work completes; overview describes the core idea as roughly **“a Bash loop”** feeding an agent until done, named after the **Ralph Wiggum** meme/metaphor.
- **“Hats”:** Documented as **specialized Ralph personas** coordinated via typed events for multi-step workflows.
- **Overnight / long-run guardrails (FAQ):** Typical **defaults** cited in FAQ-style summaries include **iteration limit (~100)**, **runtime limit (~4 hours)**, **cost limit (~$50)**, **loop detection** (e.g. high similarity across several consecutive outputs), and **consecutive error thresholds**. Completion may be signaled via markers such as **`- [x] TASK_COMPLETE`** in **`PROMPT.md`** (verify exact file contract in current docs).
- **Backends:** Described as supporting **Claude Code**, **Gemini CLI**, **Q Chat**, and other **ACP-compliant** agents.
- **Other features (marketing/docs):** Backpressure, persistent memories, task tracking, terminal UI—**confirm** on the live site.

### ghuntley / original Ralph Wiggum technique

- **Repo:** [https://github.com/ghuntley/how-to-ralph-wiggum](https://github.com/ghuntley/how-to-ralph-wiggum)
- **Methodology (high level):** Summaries describe **phased workflow** (requirements / JTBD → spec files) and a **Ralph loop** with modes such as **planning** vs **building** (plan updates vs implementation/tests/commits). Related community guide: [ClaytonFarr/ralph-playbook](https://github.com/ClaytonFarr/ralph-playbook).
- **Discussion (Hacker News):** [https://news.ycombinator.com/item?id=47536978](https://news.ycombinator.com/item?id=47536978)

---

## 3. Ruflo / `ruvnet/ruflo` and claude-flow (npm)

**Primary repo:** [https://github.com/ruvnet/ruflo](https://github.com/ruvnet/ruflo)

**Naming / npm:** Described in ecosystem material as an orchestration platform for Claude, with **npm** usage under the **claude-flow** lineage (e.g. **`@claude-flow/cli`**). Some indexes still cross-link **claude-flow** and **ruflo**—confirm package name and latest scope on [https://www.npmjs.com/](https://www.npmjs.com/) (search `claude-flow` / `@claude-flow/cli` / `ruflo`).

**Background daemon & workers (from issue/discussion summaries):**

- CLI patterns cited include:  
  `npx @claude-flow/cli@latest daemon start --foreground --quiet`  
  plus worker triggers such as **`daemon trigger --worker <name>`**, with state in **`daemon-state.json`**.
- **Headless / background:** Daemon mode is positioned for **non-interactive** scheduled workers.

**Operational caveats (verify fix version):**

- [Issue #1335 — Daemon workers / scheduler / metrics](https://github.com/ruvnet/ruflo/issues/1335) — reports of scheduler not firing, metrics not updating under `.claude-flow/metrics/`, incomplete worker output; check closure notes and release tags.
- [Ruflo v3.5.0 — release overview · Issue #1240](https://github.com/ruvnet/ruflo/issues/1240) — release-thread style context for v3.5.x line.

---

## 4. Agent Flywheel (ACFS) · Dicklesworthstone · NTM · MCP mail

### Agent Flywheel / ACFS skills repo

- **Repo:** [https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations](https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations)  
  Described as skills/integrations for **ACFS (Agentic Coding Flywheel Setup)**-style workflows (verify README for exact acronym expansion and scope).

### NTM (Named Tmux Manager)

- **Skill doc in repo:** [https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations/blob/main/skills/ntm/SKILL.md](https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations/blob/main/skills/ntm/SKILL.md)  
  Summaries: Go CLI to run multiple AI agents in **parallel tmux** panes with dashboards/context rotation—**read SKILL.md** for authoritative behavior.

### MCP Agent Mail

- **Repo:** [https://github.com/Dicklesworthstone/mcp_agent_mail](https://github.com/Dicklesworthstone/mcp_agent_mail)  
- **Top-level SKILL:** [https://github.com/Dicklesworthstone/mcp_agent_mail/blob/main/SKILL.md](https://github.com/Dicklesworthstone/mcp_agent_mail/blob/main/SKILL.md)  
- **Agent-mail skill inside flywheel repo:** [https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations/blob/main/skills/agent-mail/SKILL.md](https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations/blob/main/skills/agent-mail/SKILL.md)

**Reported capabilities (from README/skill summaries):** Mail-like async coordination between agents (inbox/outbox, threading), **identities**, **file reservation leases**, contact policies, FastMCP-based server (e.g. local HTTP endpoint cited as `http://127.0.0.1:8765` in skill text—**confirm port and transport in current SKILL.md**).

---

## Sources index (URLs only)

| Topic | URL |
|--------|-----|
| oh-my-opencode | https://github.com/code-yeongyu/oh-my-opencode |
| oh-my-openagent (related) | https://github.com/code-yeongyu/oh-my-openagent |
| ralph-loop PR #1348 | https://github.com/code-yeongyu/oh-my-opencode/pull/1348 |
| ralph-loop issue #952 | https://github.com/code-yeongyu/oh-my-openagent/issues/952 |
| Ralph Orchestrator | https://mikeyobrien.github.io/ralph-orchestrator/ |
| Ralph Orchestrator overview | https://mikeyobrien.github.io/ralph-orchestrator/guide/overview/ |
| Ralph Orchestrator FAQ | https://mikeyobrien.github.io/ralph-orchestrator/faq/ |
| how-to-ralph-wiggum (ghuntley) | https://github.com/ghuntley/how-to-ralph-wiggum |
| ralph-playbook | https://github.com/ClaytonFarr/ralph-playbook |
| HN Ralph discussion | https://news.ycombinator.com/item?id=47536978 |
| ruflo | https://github.com/ruvnet/ruflo |
| ruflo issue #1335 | https://github.com/ruvnet/ruflo/issues/1335 |
| ruflo issue #1240 | https://github.com/ruvnet/ruflo/issues/1240 |
| agent_flywheel_clawdbot_skills | https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations |
| NTM SKILL | https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations/blob/main/skills/ntm/SKILL.md |
| mcp_agent_mail | https://github.com/Dicklesworthstone/mcp_agent_mail |
| mcp_agent_mail SKILL | https://github.com/Dicklesworthstone/mcp_agent_mail/blob/main/SKILL.md |
| agent-mail SKILL (flywheel repo) | https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations/blob/main/skills/agent-mail/SKILL.md |

---

*End of findings (web search, 5 queries, April 2026).*
