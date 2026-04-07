You can get to a plan‑and‑review, overnight coding workflow by running an AG2‑style “AgentOS” on a VPS with a sandboxed code executor, multi‑agent orchestration, and git/CI integration, plus a pay‑as‑you‑go LLM backend. This can be done within your rough budget by keeping Copilot/Cursor for interactive work, adding API‑metered LLM usage, and using fully open‑source frameworks (AG2/LangGraph/CrewAI/OpenHands) and a ~$30/month VPS.​

Below I’ll first pull out the AG2 concepts that matter for you, then lay out a concrete architecture and implementation plan for autonomous overnight execution and higher reliability.

---

## AG2 concepts most relevant to your use case

AG2 (formerly AutoGen) is positioned as an “AgentOS” for building AI agents and multi‑agent systems, with a focus on agent collaboration, tool use, and human‑in‑the‑loop or fully autonomous workflows. It is a Python framework (>=3.10) installable via `pip install ag2[openai]`, and is designed to work with multiple LLM providers via config files like `OAI_CONFIG_LIST`.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​

Key concepts you’d actually use:

- **ConversableAgent and derived agents**
    
    - `ConversableAgent` is the base type for LLM‑backed agents that send/receive messages and produce replies using models, tools, or human input.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
    - Higher‑level agents include `AssistantAgent` and `UserProxyAgent`, the latter being a programmable “human proxy” for human‑in‑the‑loop or human‑as‑agent workflows.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
- **Multi‑agent orchestration primitives**
    
    - AG2 supports group patterns like group chat, swarms, sequential and nested chats, and higher‑level orchestration helpers like `AutoPattern` and `run_group_chat` to coordinate multiple specialized agents (e.g., teacher/planner/reviewer).[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
    - More recently, AG2 ships a “swarm” orchestration modelled after OpenAI’s Swarm, with explicit hand‑offs, shared context variables, and optional human involvement via `UserProxyAgent`.[](https://dev.to/ag2ai/building-swarm-based-agents-with-ag2-aj8)​
        
- **Tools and code execution**
    
    - Tools are just Python functions registered with agents via `register_function`, allowing agents to call external capabilities (APIs, utilities, etc.).[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
    - For code, AG2 has several code execution mechanisms:
        
        - Command‑line and Jupyter code executors that run generated code in either new processes (stateless) or a persistent Jupyter kernel (stateful).[](https://docs.ag2.ai/latest/docs/user-guide/advanced-concepts/code-execution/)​
            
        - Higher‑level `PythonCodeExecutionTool` that lets an agent run Python code in a specified environment (system, virtualenv, or Docker), using a working directory you control.[](https://docs.ag2.ai/0.9.6/docs/user-guide/reference-tools/code-execution/)​
            
        - Specialized executors like `RemyxCodeExecutor` for exploring and running code in pre‑built Docker images of research repos, with both interactive and non‑interactive (“batch mode”) operation via `interactive=False`.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
            
- **Advanced design patterns**
    
    - AG2 supports structured outputs, RAG integration, human‑in‑the‑loop controls, and code execution as first‑class features to build richer “agentic” workflows.
        
    - Its swarm and group patterns explicitly support transitions between agents, shared memory, and optional automatic transitions (e.g., “when agent A is done, hand off to B”).[](https://dev.to/ag2ai/building-swarm-based-agents-with-ag2-aj8)
These are exactly the primitives you need: multi‑agent workflows, robust code execution in an isolated environment, tool calls for tests/linters/git, and an orchestration layer that can run unattended.

---

## What “stack” AG2 implies for your problem


1. **LLM backends**
    
    - Configured via a model list (e.g., `OAI_CONFIG_LIST`) that maps logical model names to provider keys and models (OpenAI, etc.).[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
    - You can have multiple tiers (fast/cheap, slow/accurate) and select per agent or per step.
        
2. **Agent orchestration layer**
    
    - Python agents with system prompts, roles and descriptions (planner, coder, reviewer, test‑runner, git‑bot).[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
    - Group orchestration using patterns (swarm, group chat, sequential) with hand‑offs and termination conditions (“DONE” or “APPROVED” in content).
        
3. **Code execution sandbox**
    
    - Code executors that run generated code inside a controlled environment: system shell, virtualenv, or Docker containers, with timeouts and working directories.
        
    - In the Remyx example, AG2 spins up a Docker image representing a codebase, then an “explorer” and an “executor” agent coordinate exploration and execution non‑interactively.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
4. **Tools for tests, git, CI, and external services**
    
    - Tools are Python functions that can wrap `pytest`, `npm test`, `flake8`, `git diff/commit/push`, REST calls, etc., and can be attached to specific agents (e.g., only the “Executor” agent can call `run_tests` or `git_push`).
        
5. **Memory and state**
    
    - Core “memory” is the conversation history among agents.[](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen)​
        
    - Swarm context variables give a shared structured state that agents can update via function calls.[](https://dev.to/ag2ai/building-swarm-based-agents-with-ag2-aj8)​
        
    - For longer‑lived memory or cross‑session behaviour, you typically plug in a separate memory/RAG tool (see below) rather than relying solely on message history.
        
6. **Logging and observability**
    
    - AG2 examples rely on Python logging and explicit summaries (e.g., `response.summary`) from group runs, giving you minimalist but useful observability you can capture to files or dashboards.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        

To move from “watch‑and‑guide in Cursor” to “plan‑and‑review overnight”, you basically replicate this stack on a VPS and build a workflow tuned to your repos and tests.

---

## Alternative frameworks that can replicate AG2’s functionality

All of the major agent frameworks are open‑source: you pay for infrastructure and model APIs, not license fees. Several can give you AG2‑like capabilities, sometimes with better reliability or observability for long‑running workflows.​[](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen)​

## High‑level comparison

|Framework|Strengths for your goal|Weaknesses / trade‑offs|
|---|---|---|
|**AG2 (AutoGen)**|Conversation‑driven multi‑agent collaboration, strong human‑in‑the‑loop story, built‑in code execution and swarm patterns; relatively lightweight to prototype in Python.|Less opinionated about production‑grade state persistence; reliability is catching up vs newer graph‑based frameworks.|
|**LangGraph**|Graph‑based workflows with stateful memory, checkpoints, and high control over transitions, making it strong for long‑running, repeatable pipelines.|More engineering effort to design graphs; heavier infra requirements when scaled. ​[](https://jetthoughts.com/blog/autogen-crewai-langgraph-ai-agent-frameworks-2025/)​|
|**CrewAI**|Role‑based “crew” of agents with simple API, good for sequential/parallel tasks and human checkpoints; tends to be efficient in token usage.|Less fine‑grained control over complex branching and state than LangGraph; more linear workflows.|
|**OpenHands**|Purpose‑built for cloud coding agents: secure sandboxed runtime, integration with GitHub/GitLab/Slack, scalable task runs; very close to “fire‑and‑forget coding agent on a server.” [](https://openhands.dev)​|More opinionated platform; you fit into its deployment and runtime model rather than composing bare‑metal agents. [](https://openhands.dev)​|
|**VoltAgent**|TypeScript framework with first‑class observability, tools/MCP, memory, and workflow support, oriented toward building observable agents and integrating with JS/TS stacks. [](https://voltagent.dev)​|TS/Node ecosystem rather than Python; more work to bridge to Python‑heavy codebases unless you want to standardise in TS. [](https://voltagent.dev)​|

There are also ecosystem tools from a curated OSS list—AgentOps, Langfuse for telemetry/testing, Mem0/Zetta for memory, BrowserUse/Open Interpreter for computer control, etc.—that plug into any of the above to improve monitoring, memory, and reliability.[](https://www.reddit.com/r/AI_Agents/comments/1l1eca5/curated_list_of_opensource_packages_and_tools_for/)​

Given your Python + code‑centric scenario and desire for autonomous coding, AG2 or OpenHands as the core, optionally with LangGraph‑style ideas for stricter control, is a good fit.

---

## Proposed architecture within your budget

You’re roughly targeting:

- ~$60/month total for AI tooling (including your existing Copilot Pro + Cursor Pro at ~$30 combined).
    
- ~$30/month for a VPS.
    

Because the frameworks are open‑source and there are no mandatory subscriptions for AG2/LangGraph/CrewAI/OpenHands, your ongoing costs become:

- VPS (~$30/month).
    
- Pay‑as‑you‑go LLM API usage from providers of your choice.
    
- Optional: small spend for observability tools if you choose a managed option, but this can be zero if you self‑host logging/metrics.​
    

A concrete, budget‑aligned stack:

## Core components

1. **VPS**
    
    - Linux VPS with at least 4 vCPUs, 8–16 GB RAM, and SSD storage (for Docker images, repos, and logs).
        
    - Install Python 3.11, Docker, and git.
        
2. **Agent framework**
    
    - **Option A (default)**: AG2 as your main agent framework for orchestration, code execution, and multi‑agent workflows.
        
    - **Option B**: OpenHands as “outer shell” with AG2‑like flows under the hood, if you prefer a more out‑of‑the‑box cloud coding agent platform with GitHub integration.[](https://openhands.dev)​
        
3. **LLM provider**
    
    - One or two high‑quality API models (e.g., one “fast/cheap” for most steps, one “reliable” for planning/review).
        
    - AG2’s `LLMConfig` lets you load multiple models from a JSON file and select per agent.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
4. **Code execution sandbox**
    
    - Use AG2’s `PythonCodeExecutionTool` on the VPS, configured to run in a Docker environment with your repo mounted, so the agent can:
        
        - Edit files in a working tree.
            
        - Run Python tests, linters, build scripts, etc., with enforced timeout and resource caps.[](https://docs.ag2.ai/0.9.6/docs/user-guide/reference-tools/code-execution/)​
    - Alternatively, if you use OpenHands, you get a built‑in secure sandboxed runtime for code editing and execution.[](https://openhands.dev)​
        
5. **Repositories and git integration**
    
    - Mirror or directly clone your GitHub repos onto the VPS.
        
    - Create tools that wrap `git status/diff/commit/push` and expose them only to a “GitAgent” to keep VCS usage controlled.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
6. **Task and job orchestration**
    
    - A small Python service or CLI that:
        
        - Reads “task specs” (YAML or markdown with your `agents.md` + openspec‑style specs plus a goal).
            
        - Kicks off an AG2 swarm or group chat run.
            
        - Stores logs, artifacts (diffs, test logs), and final summaries to disk for morning review.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
            
7. **Observability and evaluation**
    
    - Start with file‑based logging using Python `logging` and AG2’s `response.summary`.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
    - Optionally plug in Langfuse/AgentOps later for deeper telemetry and failure analysis (both are commonly used for agent tracing and evaluation).[](https://www.reddit.com/r/AI_Agents/comments/1l1eca5/curated_list_of_opensource_packages_and_tools_for/)​
        

This stack lets you retain Copilot/Cursor for in‑editor productivity, while all autonomous agent work runs on the VPS overnight.

---

## Implementation strategy for overnight autonomous execution

Here’s a concrete, step‑by‑step path to a “define at night, review in the morning” workflow.

## 1. Setup AG2 and the code sandbox on the VPS

- **Install AG2 with OpenAI extras**:
    
    - `pip install "ag2[openai]"` on Python 3.10–3.13.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
- **Configure LLMs**:
    
    - Create `OAI_CONFIG_LIST` (or similar) with at least two entries, e.g. `"fast_model"` and `"reliable_model"`, and load via `LLMConfig.from_json`.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
- **Configure PythonCodeExecutionTool or equivalent**:
    
    - Create a Docker image that contains:
        
        - Your language runtimes (Python, Node, etc.).
            
        - Dependencies for your projects, or ability to `pip install` from `requirements.txt`.
            
    - Use AG2’s `PythonCodeExecutionTool` with `python_environment` pointing to a Docker‑based environment and `work_dir` set to a per‑task working directory that mounts your repo.[](https://docs.ag2.ai/0.9.6/docs/user-guide/reference-tools/code-execution/)​
        
    - Set conservative timeouts and resource limits to avoid runaway jobs.
        

## 2. Define a standard “Overnight Coding Crew”

Use AG2’s `ConversableAgent` and group patterns (e.g., `AutoPattern`, swarm) to create a small set of specialized agents.

Example crew:

- **PlannerAgent**
    
    - System prompt: “You are a senior architect. Given a spec and the current repo structure, break work into a prioritized list of small tasks and high‑level implementation strategy.”
        
    - Uses `reliable_model`, no tools except a read‑only repository inspection tool (e.g., `read_file`, `list_files`).
        
- **CoderAgent**
    
    - System prompt: “You are a focused implementation engineer. Implement tasks step‑by‑step, running tests and linters frequently. Prefer minimal, safe changes.”
        
    - Uses `fast_model`.
        
    - Has tools: `PythonCodeExecutionTool`, `run_tests`, `run_lint`, `apply_patch`, maybe a search tool for docs.
        
- **ReviewerAgent**
    
    - System prompt: “You are a code reviewer. Given diffs and test results, identify logical issues, missing tests, and design problems. Propose concrete changes; do not make them yourself.”
        
    - Uses `reliable_model`, tools only to read diffs and test logs.
        
- **GitAgent**
    
    - Extremely constrained agent whose only tools are `git_status`, `git_diff`, `git_commit`, `git_push`.
        
    - System prompt emphasises commit hygiene, branch naming, and never force‑push to `main`.
        
- **(Optional) HumanProxyAgent**
    
    - You can create a `UserProxyAgent` attached to the swarm but with `human_input_mode="NEVER"` by default, and only used when you explicitly enable interactive runs.
        

Wire these together using:

- **Swarm orchestration** with explicit hand‑offs:
    
    - Planner produces task list → hand‑off to Coder.
        
    - Coder completes a batch of tasks and passes context to Reviewer.
        
    - Reviewer either:
        
        - Hands back to Coder with feedback, or
            
        - Hands off to GitAgent with approval flag set (e.g., in a context variable or tool output).[](https://dev.to/ag2ai/building-swarm-based-agents-with-ag2-aj8)​
            
- **Termination condition**
    
    - Teacher/manager agent that monitors global state and terminates when either:
        
        - All tasks are marked done, or
            
        - Max rounds/time budget is hit.
            

This mimics AG2’s lesson‑planning examples but applied to coding and tests.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​

## 3. Express tasks in structured “overnight spec” files

Instead of ad‑hoc prompts in Cursor, define a small schema for nightly work items, e.g.:

text

`title: Implement feature X for service Y repo_path: /repos/my-service branch: feature/overnight-feature-x spec_markdown: ./specs/feature-x.md      # your detailed openspec/agents.md content constraints:   - Do not modify database schema  - All changes must pass pytest suite foo and bar max_hours: 5 priority: high`

Your “Overnight Runner” script:

- Reads this YAML.
    
- Checks out the target branch on the VPS (creating if necessary) and pulls latest from origin.
    
- Starts an AG2 swarm run with:
    
    - Initial message = spec content + constraints + any relevant context.
        
    - Maximum rounds derived from `max_hours` (e.g., time budget + token budget).
        
- Logs everything to a timestamped directory: prompts, histories, diffs, test logs, final summary.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
You queue up multiple such specs and launch them at night; each runs in its own process/container.

## 4. Make runs safe and self‑correcting

For unattended overnight runs, safety and self‑correction matter more than raw speed.

- **Test‑gated progression**
    
    - Require that before GitAgent can commit/push, tests and linters pass (`run_tests` and `run_lint` return success).[](https://docs.ag2.ai/0.9.6/docs/user-guide/reference-tools/code-execution/) **NOTE** you would need to stop it from using the `--no-verify` flag to easily skip​
        
    - Use structured tool outputs (e.g., JSON with `status: passed/failed`, `failed_tests: [...]`) to let CoderAgent reason about failures.[](https://docs.ag2.ai/0.8.7/docs/blog/2024/05/24/Agent/)​
        
- **Feature‑branch isolation**
    
    - All commits go to feature branches (`feature/agent-YYY-MM-DD-...`).
        
    - You review diffs in the morning and squash/merge manually.
        
- **Time and token budgets**
    
    - Enforce `timeout` on each code execution call and total `max_turns` for the swarm run, similar to how `RemyxCodeExecutor` uses `max_turns` in batch mode.
        
    - If budget exhausted, manager agent produces a “partial completion” summary and stops.
        
- **Containerised execution**
    
    - Always use Docker‑backed executors for generated code, as AG2 docs highlight that running generated code has inherent risk and that Docker gives stronger isolation than system or bare virtualenv.[](https://docs.ag2.ai/0.9.6/docs/user-guide/reference-tools/code-execution/)​
        
- **Logging and checkpoints**
    
    - Save intermediate state (plans, partial diffs, failing test logs) so that if a run stops mid‑way, you can either resume or manually pick up the pieces.
        

---

## Reducing need for intervention and improving reliability

The main reason you currently “hover” over agents is because they’re not reliably optimising for your real objective (passing tests, preserving architecture, etc.), and because there’s no outer workflow enforcing structure. The AG2‑style approach plus a few additional tools helps here.

## 1. Make objectives explicit and machine‑checkable

- **Tests as ground truth**
    
    - Use your test suite (or even minimal smoke tests) as the hard gate for success; the CoderAgent must get tests green before GitAgent gets permission.[](https://docs.ag2.ai/0.9.6/docs/user-guide/reference-tools/code-execution/)​
        
    - If you don’t have tests, one of the overnight agents can be a “TestWriterAgent” tasked first with writing regression tests for existing behavior.
        
- **Structured outputs and checkers**
    
    - Where possible, use structured outputs (JSON/typed fields) from agents for plans, task lists, and check results—AG2 supports structured outputs and advanced patterns for this.[](https://docs.ag2.ai/0.8.7/docs/blog/2024/05/24/Agent/)​
    - Simple Python validators can then enforce invariants (e.g., “no tasks with missing `estimate_hours`”, “max file size change”, etc.).
        

## 2. Use memory and context more deliberately

- **Shared swarm context**
    
    - Use AG2 swarm context variables as a shared “project state” object that stores:
        
        - Current tasks and their states.
            
        - Important architectural decisions.
            
        - Non‑negotiable constraints (e.g., “do not change public API X”).[](https://dev.to/ag2ai/building-swarm-based-agents-with-ag2-aj8)​
            
- **RAG over your docs**
    
    - Build a simple RAG tool over your `agents.md`, openspec docs, ADRs, and README files, and expose it as a tool to Planner and Coder agents so they can pull precise context rather than hallucinate.
        
- **Cross‑run memory**
    
    - If you want persistence across nights, plug in a memory store such as Mem0/Zetta or a custom vector DB, which the agents can query for “what we decided last time”, similar to how other agent builders use these tools.[](https://www.reddit.com/r/AI_Agents/comments/1l1eca5/curated_list_of_opensource_packages_and_tools_for/)​
        

## 3. Add observability and post‑mortem feedback

- **Logging and traces**
    
    - Start simple: store full conversation histories plus a high‑level `response.summary` file per run.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
    - As complexity grows, integrate tools like Langfuse or AgentOps (both appear in common agent‑builder stacks) to get timeline views, latency, error rates, and token usage per step.[](https://www.reddit.com/r/AI_Agents/comments/1l1eca5/curated_list_of_opensource_packages_and_tools_for/)​
        
- **Retrospective agent**
    
    - Periodically run a “PostMortemAgent” over previous logs to identify patterns of failure or inefficiency (“the planner always underestimates DB migrations; we skip updating docs”), then update system prompts and guardrails.
        

## 4. Gradual autonomy ramp‑up

Borrowing from examples where autonomous agents build software overnight (e.g., an agent pushing 28 commits and deploying between 9:50 PM and 1:30 AM with zero intervention), you want to ramp up autonomy gradually.[](https://atalupadhyay.wordpress.com/2026/02/16/ai-agent-revolution-building-autonomous-software-overnight/)​

- Start with **small, low‑risk tasks** (refactor, documentation, unit‑level changes).
    
- Then move to **feature branches for moderate features** with strong tests.
    
- Only once you’re comfortable with reliability and logs should you consider larger overnight epics or deployment automation (and even then, keep deployment steps behind explicit manual approvals).[](https://atalupadhyay.wordpress.com/2026/02/16/ai-agent-revolution-building-autonomous-software-overnight/)​
    

---

## Concrete tools and configurations to adopt

Putting it all together, here’s a concrete tool stack you can start implementing:

- **Core orchestration**: AG2 (`ag2[openai]`) on your VPS as the primary multi‑agent system.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
    
- **Code execution**:
    
    - `PythonCodeExecutionTool` configured with Docker environments per project.[](https://docs.ag2.ai/0.9.6/docs/user-guide/reference-tools/code-execution/)​
        
    - Timeouts and working directories tuned for each repo.[](https://docs.ag2.ai/latest/docs/user-guide/advanced-concepts/code-execution/)​
        
- **Secondary frameworks (optional)**:
    
    - Consider borrowing ideas from **LangGraph** if you find you need stricter state diagrams for complex workflows, especially if you later add more decision points.
        
    - Consider **OpenHands** if you’d rather adopt a ready‑made “cloud coding agent” platform with GitHub/GitLab/Slack integration instead of building all orchestration yourself.[](https://openhands.dev)​
        
- **Memory/RAG**:
    
    - Lightweight vector store or Mem0/Zetta‑style memory to capture your specs and decisions; integrated via AG2 tools.[](https://www.reddit.com/r/AI_Agents/comments/1l1eca5/curated_list_of_opensource_packages_and_tools_for/)​
        
- **Observability**:
    
    - Start with AG2 + Python logging and artifact files.[](https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/agentchat_remyx_executor/)​
        
    - Optionally add Langfuse/AgentOps later for richer telemetry and debugging.[](https://www.reddit.com/r/AI_Agents/comments/1l1eca5/curated_list_of_opensource_packages_and_tools_for/)​
        
- **CI/Deployment**:
    
    - Keep CI as an external system (GitHub Actions, etc.), triggered by the GitAgent’s pushes.
        
    - Only move deployment under agent control once you’re confident in tests and guardrails, similar to how some autonomous setups push commits and deploy overnight.
        

With this architecture, you can spend your time defining rich, structured specs and refining agent prompts and tools, while your VPS‑hosted AG2 system does the actual coding, testing, and committing overnight—aligning directly with your goal of shifting from “watch and intervene” to “plan and review.”

---

## Official / 2026 links

- [docs.ag2.ai](https://docs.ag2.ai/latest/docs/home/) · [Group chat](https://docs.ag2.ai/latest/docs/user-guide/basic-concepts/introducing-group-chat/)
- [LangGraph + AutoGen cookbook](https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/cookbook/langgraph-agent.html)
- [`research_overnight_stack_web/findings_orchestration_openhands_crewai_ag2.md`](research_overnight_stack_web/findings_orchestration_openhands_crewai_ag2.md)
