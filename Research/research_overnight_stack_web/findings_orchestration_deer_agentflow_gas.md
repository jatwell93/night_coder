# Orchestration stack research (web, 2025–2026)

Brief notes from limited web search (five queries). Primary sources are linked with full URLs.

---

## 1. Deer Flow (DeerFlow) — ByteDance–associated AI agent harness

### What it is

- **DeerFlow** (often styled **DeerFlow 2.0** in 2026 coverage) is described as an open-source **“SuperAgent” harness**: it **orchestrates multiple sub-agents**, memory, and **sandboxed execution** (e.g. Docker) so workflows can run for **minutes to hours** rather than a single chat turn.
- **Design themes** repeated in reporting: **infrastructure-first** runs (real filesystem, shell, browser in containers), **parallel sub-agents** for decomposed tasks, optional **Kubernetes**-style scaling for larger deployments, **skills** and **progressive skill loading** (token-cost framing).
- **Language/stack**: commonly described as **Python**-centric with **TypeScript** support; **MIT license**.

### GitHub and related URLs

- **Primary OSS repo (widely cited):** [https://github.com/bytedance/deer-flow](https://github.com/bytedance/deer-flow)
- **Project / marketing site:** [https://deerflow.tech/](https://deerflow.tech/)
- **Third-party explainer (ByteDance + trending narrative):** [https://byteiota.com/deerflow-2-0-bytedance-ai-agent-framework-hits-1-github/](https://byteiota.com/deerflow-2-0-bytedance-ai-agent-framework-hits-1-github/)
- **Self-host / cost explainer (blog):** [https://themenonlab.blog/blog/deerflow-bytedance-superagent](https://themenonlab.blog/blog/deerflow-bytedance-superagent)

### Pricing: managed vs OSS

- **Framework:** **Open source (MIT)** and **not** described in these sources as a **metered SaaS product** with public enterprise price lists.
- **Operational cost model:** **You bring your own LLM/APIs** (OpenAI, Anthropic, Google, DeepSeek, Ollama, etc.); spend is **API/compute**, not a DeerFlow subscription in the articles reviewed.
- **Illustrative per-task API ranges** (third-party blog, not official pricing): on the order of **$0.01–$0.50** per research-style task depending on model tier; **local Ollama** framed as **$0** marginal API cost.
- **Deployment:** **Self-hosted** (Docker / Node 22+ / Python stacks mentioned); **deerflow.tech** is referenced as a **web UI / examples** surface, not a substitute for reading official docs on data handling.

**Caveat:** Star counts and release dates in blogs vary; treat metrics as **time-sensitive** and confirm on GitHub.

---

## 2. “AgentFlow” — academic Flow-GRPO system vs homonyms

### This paper / research line (planner / executor / verifier / “generator”)

- **Name in research:** **AgentFlow** — **in-the-flow agentic system optimization** with a **modular** decomposition (commonly summarized as **Planner**, **Executor**, **Verifier**, plus **Generator** in some summaries) coordinated via **memory**, rather than one monolithic policy.
- **Training idea:** **Flow-GRPO** (*flow-based group refined policy optimization*) — addresses **long-horizon / sparse reward** credit assignment by **broadcasting trajectory-level reward** across turns and using **group-normalized advantages** (as described on the project page and paper HTML).
- **Venue / visibility:** Described as **ICLR 2026**-associated work (including “oral / top tier” claims on the project site); arXiv HTML landing page is linked below.

### Canonical URLs (research AgentFlow)

- **Project site:** [https://agentflow.stanford.edu/](https://agentflow.stanford.edu/)
- **arXiv (HTML):** [https://arxiv.org/html/2510.05592](https://arxiv.org/html/2510.05592)
- **ICLR 2026 virtual poster entry:** [https://iclr.cc/virtual/2026/poster/10009931](https://iclr.cc/virtual/2026/poster/10009931)
- **Related code repo (search hit; verify freshness):** [https://github.com/shouc/agentflow](https://github.com/shouc/agentflow)

### How to distinguish from other “AgentFlow” products

| Axis | Research **AgentFlow** (Stanford / Flow-GRPO) | Common homonyms |
|------|-----------------------------------------------|-----------------|
| **Goal** | **Train / optimize** modular agent policies; RL-style **Flow-GRPO** | Often **workflow automation**, **RPA**, or **vendor “agent builder”** UIs |
| **Artifact** | **Paper + code + models** (per site) | **SaaS** or **cloud console** products with per-seat or usage billing |
| **Namesake risk** | Fixed by checking **arXiv 2510.05592**, **agentflow.stanford.edu**, **ICLR 2026** poster ID | Microsoft and others use **“agent flow”** phrasing in **Power Platform / Copilot** ecosystems—**different teams, docs, and APIs** |

**Practical disambiguation:** If a link is **Stanford + arXiv 2510.05592 + Flow-GRPO**, it is this line. If it is **Microsoft Learn**, **Zapier**, or a **startup landing page** without those anchors, assume a **different product**.

---

## 3. Gas Town — Steve Yegge; Claude Code scaling; public cost notes

### What it is

- **Gas Town** is a **Go-based**, **MIT-licensed** **multi-agent orchestration** system attributed to **Steve Yegge**, aimed at running **many parallel coding agents** (commonly **Claude Code**), with **git-backed** persistence, **worktrees**, **tmux** session management, and structured **roles** (“Mayor”, workers, merge/refinery roles, etc.—summaries vary; see repo docs).
- **Scale narrative in coverage:** on the order of **20–30** concurrent agents as a **design target** in articles summarizing the project.

### Public posts and repos (full URLs)

- **GitHub repository:** [https://github.com/steveyegge/gastown](https://github.com/steveyegge/gastown)
- **Agent provider integration doc (in-repo):** [https://github.com/steveyegge/gastown/blob/main/docs/agent-provider-integration.md](https://github.com/steveyegge/gastown/blob/main/docs/agent-provider-integration.md)
- **Announcement-style Medium post (URL from search index):** [https://medium.com/p/welcome-to-gas-town-4f25ee16dd04](https://medium.com/p/welcome-to-gas-town-4f25ee16dd04)
- **Third-party overview:** [https://reading.torqsoftware.com/notes/software/ai-ml/agentic-coding/2026-01-15-gas-town-multi-agent-orchestration-framework/](https://reading.torqsoftware.com/notes/software/ai-ml/agentic-coding/2026-01-15-gas-town-multi-agent-orchestration-framework/)
- **News summary linking release:** [https://ascii.co.uk/news/article/news-20260102-190a5f9f/steve-yegge-releases-gas-town-multi-agent-orchestrator-for-c](https://ascii.co.uk/news/article/news-20260102-190a5f9f/steve-yegge-releases-gas-town-multi-agent-orchestrator-for-c)
- **User experience / critique essays:** [https://medium.com/long-context/gas-town-the-good-the-bad-the-ugly-ed3643b2bb50](https://medium.com/long-context/gas-town-the-good-the-bad-the-ugly-ed3643b2bb50) · [https://dev.to/mike_lady_d0e50f634af72dd/10-hours-with-gas-town-out-of-a-possible-48-2272](https://dev.to/mike_lady_d0e50f634af72dd/10-hours-with-gas-town-out-of-a-possible-48-2272)

### Cost commentary (public GitHub + community)

- **Cost tracking issue:** [https://github.com/steveyegge/gastown/issues/24](https://github.com/steveyegge/gastown/issues/24) — discussion states that **tmux pane capture** could not reliably read **Claude Code** cost UI in the **TUI header**, leading to **$0.00** reporting; **PR #292** mentioned as implementing infra later **disabled** pending a **programmatic** cost surface from Claude Code (env var, file, or CLI).
- **Anecdotal spend:** a **DEV** write-up claims moving to a **~$200/month** Claude Code tier after **~10 hours** of Gas Town use (self-reported; not audited).

---

## Method

- **Web searches used:** 5 (DeerFlow; AgentFlow + Flow-GRPO; Gas Town; DeerFlow pricing; Gas Town cost).
- **Limitations:** Blog and SEO pages mix facts; **verify** stars, dates, and pricing on **official repos and docs** before procurement or architecture decisions.
