# Orchestration research: OpenHands, CrewAI Flows, AG2/AutoGen (VPS / unattended coding, 2025–2026)

Scope: tools and patterns for **autonomous coding on a VPS or other server**—headless CLIs, SDKs, Docker/remote runtimes, and multi-step or long-running agent workflows. Sources are official docs, GitHub, and first-party product pages unless noted.

---

## 1. OpenHands (successor to the OpenDevin lineage)

**Context:** OpenHands is the open-source AI software-engineering agent stack from **All-Hands AI**. It is widely described as evolving from the earlier **OpenDevin** effort; current branding and docs use **OpenHands**. Primary app repo: [https://github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands).

### Headless CLI (scripts, CI/CD, no interactive UI)

- Official guide: [https://docs.all-hands.dev/openhands/usage/cli/headless](https://docs.all-hands.dev/openhands/usage/cli/headless)
- **Command:** `openhands --headless` with a task via `-t` / `--task` or `-f` / `--file` (required).
- **Automation fit:** Documented for CI/CD, batch jobs, and integration with other tools.
- **Safety note:** Headless mode runs in **`always-approve`** behavior—the agent executes actions without interactive confirmation; `--llm-approve` is not available in headless mode.
- **Structured logs:** `--json` emits **JSONL** (one JSON object per line) for parsing, pipelines, and logging.

**Quick-start matrix** (modes including headless, web, serve): [https://docs.all-hands.dev/openhands/usage/cli/quick-start](https://docs.all-hands.dev/openhands/usage/cli/quick-start)

### CLI installation and Docker-wrapped CLI

- Installation (uv, binary, Docker): [https://docs.all-hands.dev/openhands/usage/cli](https://docs.all-hands.dev/openhands/usage/cli)
- **uv (recommended):** `uv tool install openhands --python 3.12` (Python **3.12+**).
- **Binary:** install script [https://install.openhands.dev/install.sh](https://install.openhands.dev/install.sh)
- **Docker example** (from docs): runs a Python 3.12 image, installs `openhands` via `uv`, mounts `docker.sock`, `~/.openhands`, and sets `AGENT_SERVER_IMAGE_REPOSITORY` / `AGENT_SERVER_IMAGE_TAG` (e.g. `ghcr.io/openhands/agent-server` and a pinned tag like `1.15.0-python`), plus `SANDBOX_USER_ID` and `SANDBOX_VOLUMES` for workspace access and permission alignment.

**Local / server setup (GUI, compose, requirements):** [https://docs.all-hands.dev/openhands/usage/local-setup](https://docs.all-hands.dev/openhands/usage/local-setup)

### Software Agent SDK and remote agent server (VPS-friendly)

- SDK landing: [https://docs.all-hands.dev/sdk/index](https://docs.all-hands.dev/sdk/index)
- **Positioning:** Python + **REST** APIs aimed at **code-centric** agents; pre-built tools (bash, edit files, browse, MCP, etc.); **REST-based Agent Server** for **Docker and Kubernetes**.
- **Remote agent server overview:** [https://docs.all-hands.dev/sdk/guides/agent-server/overview](https://docs.all-hands.dev/sdk/guides/agent-server/overview)
  - Packages the SDK for deployment on **Kubernetes, VMs, on-prem, or cloud** with isolated workspaces.
  - Same client API as local; swap **workspace** implementation (`DockerWorkspace`, `APIRemoteWorkspace`, etc.).
  - **DockerWorkspace** uses images such as `ghcr.io/openhands/agent-server:latest-python` (docs show pattern; pin versions for production).
  - **APIRemoteWorkspace** can target a **Runtime API** (docs reference `https://runtime.eval.all-hands.dev` as an example URL pattern for remote sandboxes).
  - Architecture: HTTP/WebSocket server, event streaming, file upload/download and command execution through the workspace abstraction.
- **Docker sandbox guide:** [https://docs.all-hands.dev/sdk/guides/agent-server/docker-sandbox](https://docs.all-hands.dev/sdk/guides/agent-server/docker-sandbox)
- **SDK source (workspace base, remote conversation):** [https://github.com/OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk)

### Running unattended on a server (practical summary)

- Use **`openhands --headless`** with task file or `-t`, optionally **`--json`**, under `systemd`, cron, or a job runner; ensure secrets live in env or `~/.openhands/settings.json` as documented.
- For **isolation and remote execution**, prefer the **Agent Server + DockerWorkspace / API workspace** path so workloads stay in containers or remote runtimes rather than on the host shell.
- **Compose:** upstream `docker-compose.yml` lives in the main repo (e.g. [https://github.com/All-Hands-AI/OpenHands/blob/main/docker-compose.yml](https://github.com/All-Hands-AI/OpenHands/blob/main/docker-compose.yml))—verify the branch you deploy.
- **Docs index (discovery):** [https://docs.openhands.dev/llms.txt](https://docs.openhands.dev/llms.txt) (mirrors all-hands Mintlify content paths).

---

## 2. CrewAI: Flows, production posture, recent releases

### Flows (multi-step orchestration)

- **Concepts / API:** [https://docs.crewai.com/concepts/flows](https://docs.crewai.com/concepts/flows)
- **Product overview:** [https://crewai.com/crewai-flows](https://crewai.com/crewai-flows)
- **Stated capabilities:** Chain crews/tasks and custom logic; **shared state** across steps; **event-driven** execution; **branching, loops, conditionals**; decorators such as `@start()` and `@listen()` for entry points and dependencies; visualization via `flow.plot()` in examples.

### Production / enterprise themes

- **Company blog (enterprise complexity, observability, regulated use cases):** [https://blog.crewai.com/how-crewai-delivers-enterprise-level-complexity-without-compromise/](https://blog.crewai.com/how-crewai-delivers-enterprise-level-complexity-without-compromise/)
- **Changelog (concrete enterprise items):** [https://docs.crewai.com/changelog](https://docs.crewai.com/changelog) — e.g. **v1.13.0** mentions “Improve enterprise release resilience and UX,” **SSO** configuration guide, **RBAC** permissions matrix and deployment guide, A2UI extension, telemetry spans for skills/memory, and **Flow** modeled as **Pydantic `BaseModel`** for serialization/validation.
- **GitHub release (example):** [https://github.com/crewAIInc/crewAI/releases/tag/1.13.0](https://github.com/crewAIInc/crewAI/releases/tag/1.13.0)

### Recent release snapshot (verify on changelog)

As of the fetched changelog, **v1.13.0** highlights include: `RuntimeState` RootModel; Flow → Pydantic; enterprise/RBAC/SSO documentation; A2UI v0.8/v0.9 support; performance work (lazy event bus, skip tracing when disabled). **Always confirm the latest version** on [https://docs.crewai.com/changelog](https://docs.crewai.com/changelog) before pinning dependencies.

### VPS / overnight jobs angle

Flows are a natural fit for **longer pipelines** (multi-stage tasks, stateful handoffs). Pair with your own process supervisor, queues, and secrets management; CrewAI’s own enterprise docs (SSO, RBAC, deployment) are the right starting point if you need **governed** unattended runs.

---

## 3. AG2 / AutoGen (Microsoft): multi-agent patterns and LangGraph

### Branding and docs

- **AG2** is the community-driven continuation of AutoGen; docs home: [https://docs.ag2.ai/latest/docs/home/](https://docs.ag2.ai/latest/docs/home/)
- **Install:** `pip install "ag2[openai]"`; Python **>= 3.10, < 3.14** (per quick start).

### Patterns relevant to longer or structured workflows

- **Quick start** shows `ConversableAgent`, `LLMConfig`, and a **`run()` then `process()`** two-step pattern so you can inspect or adjust the workflow before execution—useful for programmatic control outside a chat UI: same page as above.
- **Group Chat** (multi-agent collaboration): [https://docs.ag2.ai/latest/docs/user-guide/basic-concepts/introducing-group-chat/](https://docs.ag2.ai/latest/docs/user-guide/basic-concepts/introducing-group-chat/)
- **Browser playground** for experiments: [https://playground.ag2.ai/](https://playground.ag2.ai/)

### LangGraph integration (official AutoGen cookbook)

- **Using LangGraph-backed agent:** [https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/cookbook/langgraph-agent.html](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/cookbook/langgraph-agent.html)
- **Mechanism:** Example defines `LangGraphToolUseAgent` as a `RoutedAgent` that compiles a LangGraph `StateGraph` (`MessagesState`, conditional edges to a `ToolNode` or `END`), then invokes the compiled graph inside `handle_user_message`. Dependencies called out in the doc include **LangGraph** and **LangChain**-family packages (`langchain_openai`, etc.).
- **Implication:** You can combine **AutoGen/AG2’s runtime and routing** with **LangGraph’s graph state and tool loops** for workflows that need explicit graph control (e.g. repeated tool cycles, conditional routing) while staying inside the AutoGen agent model.

### VPS / unattended note

AG2 does not replace your **supervisor** (systemd, Docker, k8s Job); for unattended servers, combine **headless Python entrypoints**, **logging**, and **timeouts/budgets** at the orchestration layer. For **deep research** comparisons (third-party architecture article mentioning AG2 vs LangGraph): [https://towardsai.net/p/machine-learning/the-architects-guide-to-deep-research-agents-a-comparative-analysis-of-google-adk-microsoft-ag2-and-langgraph](https://towardsai.net/p/machine-learning/the-architects-guide-to-deep-research-agents-a-comparative-analysis-of-google-adk-microsoft-ag2-and-langgraph)

---

## URL index (full paths)

| Topic | URL |
| --- | --- |
| OpenHands repo | https://github.com/All-Hands-AI/OpenHands |
| OpenHands CLI headless | https://docs.all-hands.dev/openhands/usage/cli/headless |
| OpenHands CLI quick start | https://docs.all-hands.dev/openhands/usage/cli/quick-start |
| OpenHands CLI install | https://docs.all-hands.dev/openhands/usage/cli |
| OpenHands local setup | https://docs.all-hands.dev/openhands/usage/local-setup |
| OpenHands SDK | https://docs.all-hands.dev/sdk/index |
| Remote Agent Server overview | https://docs.all-hands.dev/sdk/guides/agent-server/overview |
| Docker sandbox (SDK) | https://docs.all-hands.dev/sdk/guides/agent-server/docker-sandbox |
| Software Agent SDK source | https://github.com/OpenHands/software-agent-sdk |
| Docs index | https://docs.openhands.dev/llms.txt |
| CrewAI Flows (docs) | https://docs.crewai.com/concepts/flows |
| CrewAI Flows (product) | https://crewai.com/crewai-flows |
| CrewAI changelog | https://docs.crewai.com/changelog |
| CrewAI enterprise blog | https://blog.crewai.com/how-crewai-delivers-enterprise-level-complexity-without-compromise/ |
| CrewAI release 1.13.0 | https://github.com/crewAIInc/crewAI/releases/tag/1.13.0 |
| AG2 quick start / home | https://docs.ag2.ai/latest/docs/home/ |
| AG2 group chat | https://docs.ag2.ai/latest/docs/user-guide/basic-concepts/introducing-group-chat/ |
| AutoGen LangGraph cookbook | https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/cookbook/langgraph-agent.html |
| AG2 playground | https://playground.ag2.ai/ |

---

*Research method: limited web search (5 queries) plus direct fetch of official documentation pages listed above. Re-check versions and deployment details before production use.*
