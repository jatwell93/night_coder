# DeepWiki Q&A with Code Context for Repository: OpenHands/OpenHands
## Q1
Analyse the OpenHands reply and create a comprehensive response detailing how to achieve comparable levels of automation and agentic workflow execution without the need for expensive claude code, Codex and Gemini accounts costing $400-$600 per month. I currently use GitHub Copilot Pro and Cursor Pro (not married to these tools happy to change), I am willing to potentially double this investment to around $60 per month plus and additional $20 for a smaller VPS, but I require demonstrably better outcomes to justify the additional cost. My primary pain point is the excessive time spent actively watching the agent execute in VSCode, monitoring its thinking process, and intervening when I notice it may have skipped a fix broader fix to focus on the current task. I think this is useful, but I could better use my time elsewhere. While I have established a solid workflow utilising detailed agents.md documentation and openspec for planning, this still requires much hands-on supervision. My desired workflow shift is from active monitoring to planning and delegation: I want to define the work, set the agent executing, and return after an extended period such as overnight to review completed work. This would free me to focus on developing my prompting capabilities, context engineering techniques, and other skills that improve agentic engineering outcomes. Please provide a detailed technical report covering: the core components and capabilities of OpenHands that would be most valuable, alternative open-source or lower-cost tools and frameworks that could replicate this functionality, a proposed architecture combining available tools within my $60/month budget, specific implementation strategies for achieving autonomous overnight execution with minimal supervision, and recommendations for improving agent reliability and reducing the need for intervention during execution cycles. Include specific tools, configurations, and integration approaches that would enable me to transition from my current watch-and-guide workflow to a plan-and-review workflow.
### Answer
# Technical Report: Autonomous Agentic Workflow with OpenHands on a $80/Month Budget

---

## Executive Summary

Your pain point — active supervision of agent execution — is solvable through OpenHands' self-hosted, headless deployment. The core insight is that you do not need Claude Code, Codex, or Gemini subscriptions. OpenHands uses LiteLLM to route to any LLM provider including cheaper alternatives, and its architecture includes built-in stuck detection, memory condensation, plan-mode task tracking, and a GitHub Issue Resolver, all designed for exactly the unattended overnight execution you want.

**Target budget breakdown:**

| Item | Cost/Month |
|---|---|
| VPS (Hetzner CX21 or Hetzner CX31) | $7–$15 |
| OpenHands self-hosted | $0 |
| LLM API (OpenRouter — Gemini 2.5 Flash / DeepSeek-V3) | $15–30 |
| GitHub Copilot Pro (keep for inline IDE use) | $10 |
| **Total** | **~$35–55** |

You can drop Cursor Pro entirely for agentic work — OpenHands replaces it.

---

## Part 1: Core OpenHands Capabilities That Solve Your Problem

### 1.1 The CodeActAgent — The Primary Engine

The agent you will use is `CodeActAgent`. It unifies all execution actions into a single code-action space: bash commands, Python/Jupyter cells, file editing, browser control, and MCP tool calls. Its tool set is fully configurable. OpenHands:57-84 

### 1.2 Headless Mode and Confirmation Mode — The Keys to Unattended Execution

The `AgentController` has two parameters that are critical for overnight autonomy:

- `headless_mode=True` — the default for CLI/API usage. In headless mode, the stuck detector inspects **all history**, not just post-last-user-message, giving it more signal to self-recover.
- `confirmation_mode` — when `False`, the agent executes every action without prompting for human approval. This is how you go from watch-and-guide to plan-and-review. OpenHands:124-165 OpenHands:45-72 

### 1.3 Plan Mode — Solving the "Skipped Broader Fix" Problem

Your core frustration — the agent fixating on the immediate task and skipping broader related fixes — is directly addressed by `enable_plan_mode`. When set to `True`, it activates the `task_tracker` tool and switches to the `system_prompt_long_horizon.j2` system prompt, which instructs the agent to:

- Decompose work into multiple phases upfront
- Track status as `todo` → `in_progress` → `done`
- Maintain only ONE active task at a time (avoiding scope drift)
- Rediscover requirements that emerge during implementation and add them to the tracker OpenHands:59-62 OpenHands:1-40 OpenHands:112-143 

The task tracker enforces a discipline you currently enforce manually: it keeps tasks active until tests pass, errors resolve, and requirements are fully met. OpenHands:114-135 

### 1.4 Stuck Detection — Automatic Loop Recovery

The `StuckDetector` is always running in the background and handles five distinct failure modes without human intervention:

1. **Scenario 1**: Same action → same observation repeated 4 times
2. **Scenario 2**: Same action → error observation repeated 3 times
3. **Scenario 3**: Agent monologue (same agent message repeated 3 times)
4. **Scenario 4**: Alternating 2-step action-observation pattern repeating across 6 steps
5. **Scenario 5**: Context window condensation loop (10+ condensation events with nothing between them) OpenHands:107-138 OpenHands:409-462 

When stuck, the agent can be configured to restart from before the loop, restart with the last user message, or stop cleanly. OpenHands:610-627 

### 1.5 Memory Condensers — Enabling Long-Running Sessions Without Crashing

Context window overflow is what kills overnight runs. OpenHands ships with six condenser strategies: OpenHands:18-200 

**For overnight autonomous runs, the recommended setup is a pipeline:**

1. **`LLMSummarizingCondenser`** (`type = "llm"`) — Uses a cheap LLM (e.g. GPT-4o-mini or Gemini Flash) to summarize forgotten events into a rolling summary. Crucially, it preserves `TASK_TRACKING` sections so the plan-mode task tracker survives condensation. OpenHands:17-80 

2. **`AmortizedForgettingCondenser`** (`type = "amortized"`) — Zero LLM cost alternative; simply drops oldest events while keeping `keep_first` initial events (your task spec) and a tail of recent events. OpenHands:13-58 

The `LLMSummarizingCondenser` is better for complex multi-phase work because it explicitly carries task tracking state through its summaries. OpenHands:42-46 

### 1.6 Microagents — Your Existing AGENTS.md Works Natively

Your existing `AGENTS.md` documentation is already supported. OpenHands natively reads `AGENTS.md`, `agents.md`, `AGENT.md`, and `agent.md` from the repository root, as well as `.cursorrules`. These are loaded as `RepoMicroagent` instances and are **always active** in every session. OpenHands:26-49 OpenHands:277-341 

Beyond repo-level always-on instructions, you can create **Knowledge Microagents** with trigger keywords, and **Task Microagents** that accept parameterized inputs. These live in `.openhands/microagents/`. OpenHands:11-37 

**Practical use:** Create knowledge microagents triggered by keywords like "auth", "database", "API design" that inject domain-specific best practices and broader fix checklists automatically when those terms appear in a task.

### 1.7 The GitHub Issue Resolver — Your Overnight Pipeline

The `IssueResolver` is the most powerful feature for your use case. It is a completely headless pipeline that:
- Takes a GitHub (or GitLab/Bitbucket) issue number
- Spawns a `CodeActAgent` in a Docker sandbox
- Lets it implement a solution with up to `max_iterations` steps
- Captures the full git diff
- Optionally creates a pull request

This is the exact "plan-and-review" workflow: you file a detailed issue, trigger the resolver, go to sleep, wake up, and review a PR. OpenHands:52-100 OpenHands:182-211 

The resolver also runs `.openhands/setup.sh` and `.openhands/pre-commit.sh` automatically before and after execution: OpenHands:305-310 

### 1.8 Budget Guards and Trajectory Saving

Two configuration parameters prevent runaway costs and enable post-execution review:

- `max_budget_per_task` — The agent stops if it exceeds this USD spend per session
- `save_trajectory_path` — Full serialized replay of every action/observation, so you can audit exactly what happened overnight OpenHands:84-86 OpenHands:104-105 

### 1.9 LLM Provider Flexibility via LiteLLM

OpenHands uses LiteLLM to talk to every major LLM provider. The `base_url` parameter allows pointing to any OpenAI-compatible endpoint, including Ollama (local), OpenRouter, or any self-hosted model. OpenHands:19-111 

**Models with function calling support** (required for `CodeActAgent`'s tool use): OpenHands:69-100 

The cheapest function-calling models supported include `deepseek-chat` (DeepSeek-V3), `kimi-k2-0711-preview`, `qwen3-coder*`, and `gemini-2.5-pro*`/`gemini-2.5-flash`.

OpenRouter support is built directly into the LiteLLM config layer: OpenHands:67-68 

### 1.10 Multiple Runtime Options

You have four runtime choices, critical for VPS deployment: OpenHands:1-1 

- **Docker** (default, sandboxed, recommended)
- **Local** (no Docker, runs directly on VPS — saves Docker overhead for simple tasks)
- **CLI** (lightweight for scripted automation)
- **Kubernetes** (for scaling multiple parallel overnight jobs)

The local runtime runs directly on the host machine: OpenHands:1-2 

---

## Part 2: Proposed Architecture Within the $80/Month Budget

```
┌─────────────────────────────────────────────────────────────┐
│                  YOUR PLANNING ENVIRONMENT                    │
│  GitHub Issues (detailed specs)  ←→  Your AGENTS.md          │
│  OpenSpec documents              ←→  .openhands/microagents/  │
└──────────────────────────┬──────────────────────────────────┘
                           │ gh issue create / API trigger
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              VPS ($7-15/month, Hetzner CX21)                 │
│                                                              │
│  OpenHands (self-hosted, Docker)                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  IssueResolver / AgentController (headless_mode=True)│   │
│  │  CodeActAgent (enable_plan_mode=True)                 │   │
│  │  StuckDetector (5 auto-recovery scenarios)            │   │
│  │  LLMSummarizingCondenser (cheap model)               │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│  Scheduler:     │  cron / GitHub Actions webhook trigger     │
│  tmux sessions  │  nohup for overnight unattended runs       │
└─────────────────┼────────────────────────────────────────────┘
                  │ LiteLLM
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenRouter ($15-30/month)                        │
│  Primary:   Gemini 2.5 Flash  ($0.15/$0.60 per M tokens)    │
│   OR        DeepSeek-V3      ($0.27/$1.10 per M tokens)      │
│  Condenser: GPT-4o-mini      ($0.15/$0.60 per M tokens)     │
└─────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│       GitHub (PR review in the morning)                       │
│  save_trajectory_path → full overnight audit trail           │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 3: Complete `config.toml` for Autonomous Overnight Execution

Based on the configuration schema from the codebase: OpenHands:1-100 OpenHands:380-435 

Here is the recommended configuration for overnight autonomous runs:

```toml
[core]
max_iterations = 300           # Enough for complex overnight tasks
max_budget_per_task = 3.0     # $3 hard stop per task (guardrail)
save_trajectory_path = "./trajectories"   # Full audit trail
runtime = "docker"
default_agent = "CodeActAgent"

[llm]
model = "openrouter/google/gemini-2.5-flash"
api_key = "YOUR_OPENROUTER_KEY"
base_url = "https://openrouter.ai/api/v1"
temperature = 0.0
num_retries = 8
retry_min_wait = 15
retry_max_wait = 120
caching_prompt = true

[llm.condenser_llm]
model = "openrouter/openai/gpt-4o-mini"
api_key = "YOUR_OPENROUTER_KEY"
base_url = "https://openrouter.ai/api/v1"
temperature = 0.1

[agent]
enable_plan_mode = true           # Task tracker + long-horizon prompt
enable_stuck_detection = true     # Auto-recovery from loops
enable_history_truncation = true  # Handles context overflow
enable_browsing = true
enable_cmd = true
enable_think = true

[condenser]
type = "llm"
llm_config = "condenser_llm"
keep_first = 1
max_size = 200
max_event_length = 10000

[sandbox]
timeout = 300
enable_auto_lint = true           # Catches errors before committing

[security]
confirmation_mode = false         # CRITICAL: no human interruption
``` OpenHands:55-73 OpenHands:75-78 

---

## Part 4: Implementation Strategies for Overnight Execution

### 4.1 GitHub Issue → Overnight PR Pipeline (Recommended)

The `IssueResolver` is your primary overnight automation path. It accepts a GitHub issue number, resolves it autonomously, and produces a git patch (optionally a PR): OpenHands:8-100 

**Invocation:**
```bash
# Run in tmux or with nohup so it survives SSH disconnection
tmux new-session -d -s overnight "python -m openhands.resolver.resolve_issue \
  --selected-repo YOUR_ORG/YOUR_REPO \
  --issue-number 42 \
  --llm-model 'openrouter/google/gemini-2.5-flash' \
  --llm-api-key YOUR_KEY \
  --max-iterations 200 \
  --output-dir ./resolver-output"
```

The resolver runs `.openhands/setup.sh` before execution and `.openhands/pre-commit.sh` after — giving you full control over the pre/post environment. OpenHands:305-312 

### 4.2 Issue Quality as Your Primary Reliability Lever

Since you already use OpenSpec for planning, convert your spec documents directly into detailed GitHub issues. The agent's prompt template reads the issue body, comments, and repository structure. The more comprehensive the issue (acceptance criteria, edge cases, affected files, test strategy), the fewer interventions you'll need.

The resolver uses Jinja templates for the prompt, which you can customize: OpenHands:109-127 

### 4.3 Migrating Your AGENTS.md to a Microagent Hierarchy

Your current `AGENTS.md` is already read natively by OpenHands at `repo.md` level (always active). Extend it into a hierarchy: OpenHands:300-341 

```
.openhands/microagents/
├── repo.md          ← Your existing AGENTS.md content (always active)
├── auth.md          ← Knowledge microagent (triggers: ["auth", "jwt", "oauth"])
├── database.md      ← Knowledge microagent (triggers: ["database", "migration", "query"])
├── api-design.md    ← Knowledge microagent (triggers: ["api", "endpoint", "REST"])
└── broader-fix.md   ← Knowledge microagent (triggers: ["fix", "bug", "refactor"])
                        Content: "When fixing X, ALWAYS check for Y, Z patterns..."
```

The `broader-fix.md` knowledge microagent is your solution to the "agent skips related fixes" problem — it injects broader fix checklists exactly when the triggering keywords appear in the task. OpenHands:174-204 

### 4.4 Cost Control via Budget Flags

Set `max_budget_per_task` to prevent runaway overnight costs. The controller checks this against accumulated LLM spend on every step: OpenHands:886-900 OpenHands:104-106 

For Gemini 2.5 Flash at typical code task token volumes (~100k tokens per complex task), $3/task gives you generous headroom.

### 4.5 MCP Servers for Extended Tool Capabilities

OpenHands supports MCP (Model Context Protocol) servers as additional tools: OpenHands:486-526 

Add the GitHub MCP server so the agent can read issues, create PRs, and manage labels autonomously:

```toml
[mcp]
stdio_servers = [
  {name = "github", command = "npx", args = ["-y", "@modelcontextprotocol/server-github"], 
   env = {GITHUB_TOKEN = "YOUR_TOKEN"}},
  {name = "filesystem", command = "npx", args = ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]}
]
```

### 4.6 Scheduling Overnight Runs

On the VPS, use either:

**cron-based scheduling** (for regular overnight runs):
```bash
# Run at 11 PM every weekday, log to dated file
0 23 * * 1-5 cd /opt/openhands && tmux new-session -d -s "night-$(date +\%Y\%m\%d)" \
  "python -m openhands.resolver.resolve_issue --issue-number $(cat .next_issue) ... >> logs/$(date +\%Y\%m\%d).log 2>&1"
```

**GitHub Actions trigger** (preferred for repo-integrated work):
```yaml
on:
  issues:
    types: [labeled]
# Trigger when you add label "agent-ready" to a well-specified issue
```

---

## Part 5: Improving Agent Reliability — Specific Interventions

### 5.1 The Long-Horizon System Prompt Covers Your Core Problem

The `system_prompt.j2` that all sessions use already instructs the agent on problem-solving workflow, code quality, version control discipline, and troubleshooting strategy: OpenHands:49-96 

The key instruction for your "skipped broader fix" problem: OpenHands:88-96 

When enabled, `system_prompt_long_horizon.j2` additionally mandates task tracker usage for all multi-phase work and, critically, maintains task tracking continuity through memory condensation events: OpenHands:42-46 

### 5.2 Enable Auto-Lint to Catch Errors Before They Cascade

Set `enable_auto_lint = true` in `[sandbox]`. This lints after every file edit, catching syntax errors before they accumulate and cause the stuck detector to trigger. OpenHands:75-78 

### 5.3 Choose the Right Condenser for Task Complexity

| Task Type | Best Condenser | Why |
|---|---|---|
| Complex multi-phase, long overnight | `llm` with cheap model | Preserves TASK_TRACKING through summarization |
| Simple focused tasks | `amortized` | Zero extra cost, no LLM needed |
| Debugging sessions with many shell outputs | `observation_masking` | Masks old outputs, keeps structure |
| Mixed workloads | `pipeline` with `[observation_masking, amortized]` | Layer strategies | OpenHands:165-200 

### 5.4 Function Calling Model Selection Is Critical

**Do not use a model without function calling support.** The `CodeActAgent` depends on structured tool calls. Verify your chosen model is in the supported list: OpenHands:69-100 

**Best budget options for overnight unattended work (via OpenRouter):**
1. **Gemini 2.5 Flash** — `gemini-2.5-flash` — best price/performance ratio, large context window
2. **DeepSeek-V3** — `deepseek-chat` — excellent at code, very cheap
3. **Kimi-K2** — `kimi-k2-0711-preview` — strong at long-horizon coding tasks
### Citations
**File:** openhands/agenthub/codeact_agent/codeact_agent.py (L57-84)
```python
class CodeActAgent(Agent):
    VERSION = '2.2'
    """
    The Code Act Agent is a minimalist agent.
    The agent works by passing the model a list of action-observation pairs and prompting the model to take the next step.

    ### Overview

    This agent implements the CodeAct idea ([paper](https://arxiv.org/abs/2402.01030), [tweet](https://twitter.com/xingyaow_/status/1754556835703751087)) that consolidates LLM agents' **act**ions into a unified **code** action space for both *simplicity* and *performance* (see paper for more details).

    The conceptual idea is illustrated below. At each turn, the agent can:

    1. **Converse**: Communicate with humans in natural language to ask for clarification, confirmation, etc.
    2. **CodeAct**: Choose to perform the task by executing code
    - Execute any valid Linux `bash` command
    - Execute any valid `Python` code with [an interactive Python interpreter](https://ipython.org/). This is simulated through `bash` command, see plugin system below for more details.

    ![image](https://github.com/OpenHands/OpenHands/assets/38853559/92b622e3-72ad-4a61-8f41-8c040b6d5fb3)

    """

    sandbox_plugins: list[PluginRequirement] = [
        # NOTE: AgentSkillsRequirement need to go before JupyterRequirement, since
        # AgentSkillsRequirement provides a lot of Python functions,
        # and it needs to be initialized before Jupyter for Jupyter to use those functions.
        AgentSkillsRequirement(),
        JupyterRequirement(),
    ]
```
**File:** openhands/controller/agent_controller.py (L124-165)
```python
    def __init__(
        self,
        agent: Agent,
        event_stream: EventStream,
        conversation_stats: ConversationStats,
        iteration_delta: int,
        budget_per_task_delta: float | None = None,
        agent_to_llm_config: dict[str, LLMConfig] | None = None,
        agent_configs: dict[str, AgentConfig] | None = None,
        sid: str | None = None,
        file_store: FileStore | None = None,
        user_id: str | None = None,
        confirmation_mode: bool = False,
        initial_state: State | None = None,
        is_delegate: bool = False,
        headless_mode: bool = True,
        status_callback: Callable | None = None,
        replay_events: list[Event] | None = None,
        security_analyzer: 'SecurityAnalyzer | None' = None,
    ):
        """Initializes a new instance of the AgentController class.

        Args:
            agent: The agent instance to control.
            event_stream: The event stream to publish events to.
            max_iterations: The maximum number of iterations the agent can run.
            max_budget_per_task: The maximum budget (in USD) allowed per task, beyond which the agent will stop.
            agent_to_llm_config: A dictionary mapping agent names to LLM configurations in the case that
                we delegate to a different agent.
            agent_configs: A dictionary mapping agent names to agent configurations in the case that
                we delegate to a different agent.
            sid: The session ID of the agent.
            confirmation_mode: Whether to enable confirmation mode for agent actions.
            initial_state: The initial state of the controller.
            is_delegate: Whether this controller is a delegate.
            headless_mode: Whether the agent is run in headless mode.
            status_callback: Optional callback function to handle status updates.
            replay_events: A list of logs to replay.
        """
        self.id = sid or event_stream.sid
        self.user_id = user_id
        self.file_store = file_store
```
**File:** openhands/controller/agent_controller.py (L610-627)
```python
    async def _handle_loop_recovery_action(self, action: LoopRecoveryAction) -> None:
        # Check if this is a loop recovery option
        if self._stuck_detector.stuck_analysis:
            option = action.option

            # Handle the loop recovery option
            if option == 1:
                # Option 1: Restart from before loop
                await self._perform_loop_recovery(self._stuck_detector.stuck_analysis)
            elif option == 2:
                # Option 2: Restart with last user message
                await self._restart_with_last_user_message(
                    self._stuck_detector.stuck_analysis
                )
            elif option == 3:
                # Option 3: Stop agent completely
                await self.set_agent_state_to(AgentState.STOPPED)
            return
```
**File:** openhands/controller/agent_controller.py (L886-900)
```python
        # Synchronize spend across all llm services with the budget flag
        self.state_tracker.sync_budget_flag_with_metrics()
        if self.agent.config.enable_stuck_detection and self._is_stuck():
            await self._react_to_exception(
                AgentStuckInLoopError('Agent got stuck in a loop')
            )
            return

        try:
            self.state_tracker.run_control_flags()
        except Exception as e:
            logger.warning('Control flag limits hit')
            await self._react_to_exception(e)
            return

```
**File:** openhands/controller/stuck.py (L45-72)
```python
    def is_stuck(self, headless_mode: bool = True) -> bool:
        """Checks if the agent is stuck in a loop.

        Args:
            headless_mode: Matches AgentController's headless_mode.
                          If True: Consider all history (automated/testing)
                          If False: Consider only history after last user message (interactive)

        Returns:
            bool: True if the agent is stuck in a loop, False otherwise.
        """
        filtered_history_offset = 0
        if not headless_mode:
            # In interactive mode, only look at history after the last user message
            last_user_msg_idx = -1
            for i, event in enumerate(reversed(self.state.history)):
                if (
                    isinstance(event, MessageAction)
                    and event.source == EventSource.USER
                ):
                    last_user_msg_idx = len(self.state.history) - i - 1
                    break
            filtered_history_offset = last_user_msg_idx + 1
            history_to_check = self.state.history[last_user_msg_idx + 1 :]
        else:
            # In headless mode, look at all history
            history_to_check = self.state.history

```
**File:** openhands/controller/stuck.py (L107-138)
```python
        if self._is_stuck_repeating_action_observation(
            last_actions, last_observations, filtered_history, filtered_history_offset
        ):
            return True

        # scenario 2: same action, errors
        if self._is_stuck_repeating_action_error(
            last_actions, last_observations, filtered_history, filtered_history_offset
        ):
            return True

        # scenario 3: monologue
        if self._is_stuck_monologue(filtered_history, filtered_history_offset):
            return True

        # scenario 4: action, observation pattern on the last six steps
        if len(filtered_history) >= 6:
            if self._is_stuck_action_observation_pattern(
                filtered_history, filtered_history_offset
            ):
                return True

        # scenario 5: context window error loop
        if len(filtered_history) >= 10:
            if self._is_stuck_context_window_error(
                filtered_history, filtered_history_offset
            ):
                return True

        # Empty stuck_analysis when not stuck
        self.stuck_analysis = None
        return False
```
**File:** openhands/controller/stuck.py (L409-462)
```python
    def _is_stuck_context_window_error(
        self, filtered_history: list[Event], filtered_history_offset: int = 0
    ) -> bool:
        """Detects if we're stuck in a loop of context window errors.

        This happens when we repeatedly get context window errors and try to trim,
        but the trimming doesn't work, causing us to get more context window errors.
        The pattern is repeated AgentCondensationObservation events without any other
        events between them.

        Args:
            filtered_history: List of filtered events to check

        Returns:
            bool: True if we detect a context window error loop
        """
        # Look for AgentCondensationObservation events
        condensation_events = [
            (i, event)
            for i, event in enumerate(filtered_history)
            if isinstance(event, AgentCondensationObservation)
        ]

        # Need at least 10 condensation events to detect a loop
        if len(condensation_events) < 10:
            return False

        # Get the last 10 condensation events
        last_condensation_events = condensation_events[-10:]

        # Check if there are any non-condensation events between them
        for i in range(len(last_condensation_events) - 1):
            start_idx = last_condensation_events[i][0]
            end_idx = last_condensation_events[i + 1][0]

            # Look for any non-condensation events between these two
            has_other_events = False
            for event in filtered_history[start_idx + 1 : end_idx]:
                if not isinstance(event, AgentCondensationObservation):
                    has_other_events = True
                    break

            if not has_other_events:
                logger.warning(
                    'Context window error loop detected - repeated condensation events'
                )
                self.stuck_analysis = StuckDetector.StuckAnalysis(
                    loop_type='context_window_error',
                    loop_repeat_times=2,
                    loop_start_idx=start_idx + filtered_history_offset,
                )
                return True

        return False
```
**File:** openhands/core/config/agent_config.py (L55-73)
```python
    enable_history_truncation: bool = Field(default=True)
    """Whether history should be truncated to continue the session when hitting LLM context length limit."""
    enable_som_visual_browsing: bool = Field(default=True)
    """Whether to enable SoM (Set of Marks) visual browsing."""
    enable_plan_mode: bool = Field(default=True)
    """Whether to enable plan mode, which uses the long horizon system message and add the new tool - task_tracker - for planning, tracking and executing complex tasks."""
    enable_stuck_detection: bool = Field(default=True)
    """Whether to enable stuck/loop detection. When disabled, the agent will not automatically detect and recover from loops."""
    condenser: CondenserConfig = Field(
        # The default condenser is set to the conversation window condenser -- if
        # we use NoOp and the conversation hits the LLM context length limit,
        # the agent will generate a condensation request which will never be
        # handled.
        default_factory=lambda: ConversationWindowCondenserConfig()
    )
    model_routing: ModelRoutingConfig = Field(default_factory=ModelRoutingConfig)
    """Model routing configuration settings."""
    extended: ExtendedConfig = Field(default_factory=lambda: ExtendedConfig({}))
    """Extended configuration for the agent."""
```
**File:** openhands/agenthub/codeact_agent/prompts/system_prompt_long_horizon.j2 (L1-40)
```jinja
{% include "system_prompt.j2" %}

<TASK_MANAGEMENT>
* You have access to the `task_tracker` tool to help you organize and monitor development work. Use this tool REGULARLY to maintain task visibility and provide users with clear progress updates. This tool is ESSENTIAL for systematic planning and decomposing complex development work into manageable components. Failing to use this tool for planning may result in overlooked requirements - which is unacceptable.
* It is crucial that you update task status to "done" immediately upon completion of each work item. Do not accumulate multiple finished tasks before updating their status.
* For complex, multi-phase development work, use `task_tracker` to establish a comprehensive plan with well-defined steps:
  1. Begin by decomposing the overall objective into primary phases using `task_tracker`
  2. Include detailed work items as necessary to break complex activities into actionable units
  3. Update tasks to "in_progress" status when commencing work on them
  4. Update tasks to "done" status immediately after completing each item
  5. For each primary phase, incorporate additional work items as you identify new requirements
  6. If you determine the plan requires substantial modifications, suggest revisions and obtain user confirmation before proceeding
* Example workflow for debugging and resolution:
  ```
  User: "Execute the test suite and resolve any validation failures"
  Assistant: I'm going to use the task_tracker tool to organize the following work items:
  - Execute the test suite
  - Resolve any validation failures
  I'm now going to run the test suite using the terminal.
  [After running tests and discovering 8 validation failures]
  I found 8 validation failures that need attention. I'm going to use the task_tracker tool to add 8 specific items to the task list.
  [Updating first task to in_progress]
  Let me begin addressing the first validation issue...
  [After resolving first failure]
  The first validation issue has been resolved, let me mark that task as done and proceed to the second item...
  ```
* Example workflow for component development:
  ```
  User: "Build a dashboard component that displays analytics data with interactive charts and filtering options"
  Assistant: I'll help you create an analytics dashboard with interactive charts and filtering. Let me first use the task_tracker tool to organize this development work.
  Adding the following tasks to the tracker:
  1. Analyze existing analytics data structure and requirements
  2. Design dashboard layout and component architecture
  3. Implement data visualization charts with interactivity
  4. Create filtering and search functionality
  5. Integrate components and perform testing
  Let me start by examining the current analytics data structure to understand what we're working with...
  [Assistant proceeds with implementation step by step, updating tasks to in_progress and done as work progresses]
  ```
</TASK_MANAGEMENT>
```
**File:** openhands/agenthub/codeact_agent/prompts/system_prompt_long_horizon.j2 (L42-46)
```jinja
<TASK_TRACKING_PERSISTENCE>
* IMPORTANT: If you were using the task_tracker tool before a condensation event, continue using it after condensation
* Check condensation summaries for TASK_TRACKING sections to maintain continuity
* If you see a condensation event with TASK_TRACKING, immediately use task_tracker to view and continue managing them
</TASK_TRACKING_PERSISTENCE>
```
**File:** openhands/agenthub/codeact_agent/tools/task_tracker.py (L112-143)
```python
## Status Management and Workflow

1. **Status Values**: Track work using these states:
   - todo: Not yet initiated
   - in_progress: Currently active (maintain single focus)
   - done: Successfully completed

2. **Workflow Practices**:
   - Update status dynamically as work progresses
   - Mark completion immediately upon task finish
   - Limit active work to ONE task at any given time
   - Complete current activities before initiating new ones
   - Remove obsolete tasks from tracking entirely

3. **Completion Criteria**:
   - Mark tasks as done only when fully achieved
   - Keep status as in_progress if errors, blocks, or partial completion exist
   - Create new tasks for discovered issues or dependencies
   - Never mark done when:
       - Test suites are failing
       - Implementation remains incomplete
       - Unresolved errors persist
       - Required resources are unavailable

4. **Task Organization**:
   - Write precise, actionable descriptions
   - Decompose complex work into manageable units
   - Use descriptive, clear naming conventions

When uncertain, favor using this tool. Proactive task management demonstrates
systematic approach and ensures comprehensive requirement fulfillment.
"""
```
**File:** openhands/core/config/condenser_config.py (L18-200)
```python
class NoOpCondenserConfig(BaseModel):
    """Configuration for NoOpCondenser."""

    type: Literal['noop'] = Field(default='noop')

    model_config = ConfigDict(extra='forbid')


class ObservationMaskingCondenserConfig(BaseModel):
    """Configuration for ObservationMaskingCondenser."""

    type: Literal['observation_masking'] = Field(default='observation_masking')
    attention_window: int = Field(
        default=100,
        description='The number of most-recent events where observations will not be masked.',
        ge=1,
    )

    model_config = ConfigDict(extra='forbid')


class BrowserOutputCondenserConfig(BaseModel):
    """Configuration for the BrowserOutputCondenser."""

    type: Literal['browser_output_masking'] = Field(default='browser_output_masking')
    attention_window: int = Field(
        default=1,
        description='The number of most recent browser output observations that will not be masked.',
        ge=1,
    )


class RecentEventsCondenserConfig(BaseModel):
    """Configuration for RecentEventsCondenser."""

    type: Literal['recent'] = Field(default='recent')

    # at least one event by default, because the best guess is that it is the user task
    keep_first: int = Field(
        default=1,
        description='The number of initial events to condense.',
        ge=0,
    )
    max_events: int = Field(
        default=100, description='Maximum number of events to keep.', ge=1
    )

    model_config = ConfigDict(extra='forbid')


class LLMSummarizingCondenserConfig(BaseModel):
    """Configuration for LLMCondenser."""

    type: Literal['llm'] = Field(default='llm')
    llm_config: LLMConfig = Field(
        ..., description='Configuration for the LLM to use for condensing.'
    )

    # at least one event by default, because the best guess is that it's the user task
    keep_first: int = Field(
        default=1,
        description='Number of initial events to always keep in history.',
        ge=0,
    )
    max_size: int = Field(
        default=100,
        description='Maximum size of the condensed history before triggering forgetting.',
        ge=2,
    )
    max_event_length: int = Field(
        default=10_000,
        description='Maximum length of the event representations to be passed to the LLM.',
    )

    model_config = ConfigDict(extra='forbid')


class AmortizedForgettingCondenserConfig(BaseModel):
    """Configuration for AmortizedForgettingCondenser."""

    type: Literal['amortized'] = Field(default='amortized')
    max_size: int = Field(
        default=100,
        description='Maximum size of the condensed history before triggering forgetting.',
        ge=2,
    )

    # at least one event by default, because the best guess is that it's the user task
    keep_first: int = Field(
        default=1,
        description='Number of initial events to always keep in history.',
        ge=0,
    )

    model_config = ConfigDict(extra='forbid')


class LLMAttentionCondenserConfig(BaseModel):
    """Configuration for LLMAttentionCondenser."""

    type: Literal['llm_attention'] = Field(default='llm_attention')
    llm_config: LLMConfig = Field(
        ..., description='Configuration for the LLM to use for attention.'
    )
    max_size: int = Field(
        default=100,
        description='Maximum size of the condensed history before triggering forgetting.',
        ge=2,
    )

    # at least one event by default, because the best guess is that it's the user task
    keep_first: int = Field(
        default=1,
        description='Number of initial events to always keep in history.',
        ge=0,
    )

    model_config = ConfigDict(extra='forbid')


class StructuredSummaryCondenserConfig(BaseModel):
    """Configuration for StructuredSummaryCondenser instances."""

    type: Literal['structured'] = Field(default='structured')
    llm_config: LLMConfig = Field(
        ..., description='Configuration for the LLM to use for condensing.'
    )

    # at least one event by default, because the best guess is that it's the user task
    keep_first: int = Field(
        default=1,
        description='Number of initial events to always keep in history.',
        ge=0,
    )
    max_size: int = Field(
        default=100,
        description='Maximum size of the condensed history before triggering forgetting.',
        ge=2,
    )
    max_event_length: int = Field(
        default=10_000,
        description='Maximum length of the event representations to be passed to the LLM.',
    )

    model_config = ConfigDict(extra='forbid')


class CondenserPipelineConfig(BaseModel):
    """Configuration for the CondenserPipeline."""

    type: Literal['pipeline'] = Field(default='pipeline')
    condensers: list[CondenserConfig] = Field(
        default_factory=list,
        description='List of condenser configurations to be used in the pipeline.',
    )

    model_config = ConfigDict(extra='forbid')


class ConversationWindowCondenserConfig(BaseModel):
    """Configuration for ConversationWindowCondenser.

    Not currently supported by the TOML or ENV_VAR configuration strategies.
    """

    type: Literal['conversation_window'] = Field(default='conversation_window')

    model_config = ConfigDict(extra='forbid')


# Type alias for convenience
CondenserConfig = (
    NoOpCondenserConfig
    | ObservationMaskingCondenserConfig
    | BrowserOutputCondenserConfig
    | RecentEventsCondenserConfig
    | LLMSummarizingCondenserConfig
    | AmortizedForgettingCondenserConfig
    | LLMAttentionCondenserConfig
    | StructuredSummaryCondenserConfig
    | CondenserPipelineConfig
    | ConversationWindowCondenserConfig
)
```
**File:** openhands/memory/condenser/impl/llm_summarizing_condenser.py (L17-80)
```python
class LLMSummarizingCondenser(RollingCondenser):
    """A condenser that summarizes forgotten events.

    Maintains a condensed history and forgets old events when it grows too large,
    keeping a special summarization event after the prefix that summarizes all previous summarizations
    and newly forgotten events.
    """

    def __init__(
        self,
        llm: LLM,
        max_size: int = 100,
        keep_first: int = 1,
        max_event_length: int = 10_000,
    ):
        if keep_first >= max_size // 2:
            raise ValueError(
                f'keep_first ({keep_first}) must be less than half of max_size ({max_size})'
            )
        if keep_first < 0:
            raise ValueError(f'keep_first ({keep_first}) cannot be negative')
        if max_size < 1:
            raise ValueError(f'max_size ({max_size}) cannot be non-positive')

        self.max_size = max_size
        self.keep_first = keep_first
        self.max_event_length = max_event_length
        self.llm = llm

        super().__init__()

    def _truncate(self, content: str) -> str:
        """Truncate the content to fit within the specified maximum event length."""
        return truncate_content(content, max_chars=self.max_event_length)

    def get_condensation(self, view: View) -> Condensation:
        head = view[: self.keep_first]
        target_size = self.max_size // 2
        # Number of events to keep from the tail -- target size, minus however many
        # prefix events from the head, minus one for the summarization event
        events_from_tail = target_size - len(head) - 1

        summary_event = (
            view[self.keep_first]
            if isinstance(view[self.keep_first], AgentCondensationObservation)
            else AgentCondensationObservation('No events summarized')
        )

        # Identify events to be forgotten (those not in head or tail)
        forgotten_events = []
        for event in view[self.keep_first : -events_from_tail]:
            if not isinstance(event, AgentCondensationObservation):
                forgotten_events.append(event)

        # Construct prompt for summarization
        prompt = """You are maintaining a context-aware state summary for an interactive agent.
You will be given a list of events corresponding to actions taken by the agent, and the most recent previous summary if one exists.
If the events being summarized contain ANY task-tracking, you MUST include a TASK_TRACKING section to maintain continuity.
When referencing tasks make sure to preserve exact task IDs and statuses.

Track:

USER_CONTEXT: (Preserve essential user requirements, goals, and clarifications in concise form)

```
**File:** openhands/memory/condenser/impl/amortized_forgetting_condenser.py (L13-58)
```python
class AmortizedForgettingCondenser(RollingCondenser):
    """A condenser that maintains a condensed history and forgets old events when it grows too large."""

    def __init__(self, max_size: int = 100, keep_first: int = 0):
        """Initialize the condenser.

        Args:
            max_size: Maximum size of history before forgetting.
            keep_first: Number of initial events to always keep.

        Raises:
            ValueError: If keep_first is greater than max_size, keep_first is negative, or max_size is non-positive.
        """
        if keep_first >= max_size // 2:
            raise ValueError(
                f'keep_first ({keep_first}) must be less than half of max_size ({max_size})'
            )
        if keep_first < 0:
            raise ValueError(f'keep_first ({keep_first}) cannot be negative')
        if max_size < 1:
            raise ValueError(f'max_size ({keep_first}) cannot be non-positive')

        self.max_size = max_size
        self.keep_first = keep_first

        super().__init__()

    def get_condensation(self, view: View) -> Condensation:
        target_size = self.max_size // 2
        head = view[: self.keep_first]

        events_from_tail = target_size - len(head)
        tail = view[-events_from_tail:]

        event_ids_to_keep = {event.id for event in head + tail}
        event_ids_to_forget = {event.id for event in view} - event_ids_to_keep

        event = CondensationAction(
            forgotten_events_start_id=min(event_ids_to_forget),
            forgotten_events_end_id=max(event_ids_to_forget),
        )

        return Condensation(action=event)

    def should_condense(self, view: View) -> bool:
        return len(view) > self.max_size or view.unhandled_condensation_request
```
**File:** openhands/microagent/microagent.py (L26-49)
```python
    PATH_TO_THIRD_PARTY_MICROAGENT_NAME: ClassVar[dict[str, str]] = {
        '.cursorrules': 'cursorrules',
        'agents.md': 'agents',
        'agent.md': 'agents',
    }

    @classmethod
    def _handle_third_party(
        cls, path: Path, file_content: str
    ) -> Union['RepoMicroagent', None]:
        # Determine the agent name based on file type
        microagent_name = cls.PATH_TO_THIRD_PARTY_MICROAGENT_NAME.get(path.name.lower())

        # Create RepoMicroagent if we recognized the file type
        if microagent_name is not None:
            return RepoMicroagent(
                name=microagent_name,
                content=file_content,
                metadata=MicroagentMetadata(name=microagent_name),
                source=str(path),
                type=MicroagentType.REPO_KNOWLEDGE,
            )

        return None
```
**File:** openhands/microagent/microagent.py (L174-204)
```python
class KnowledgeMicroagent(BaseMicroagent):
    """Knowledge micro-agents provide specialized expertise that's triggered by keywords in conversations.

    They help with:
    - Language best practices
    - Framework guidelines
    - Common patterns
    - Tool usage
    """

    def __init__(self, **data):
        super().__init__(**data)
        if self.type not in [MicroagentType.KNOWLEDGE, MicroagentType.TASK]:
            raise ValueError('KnowledgeMicroagent must have type KNOWLEDGE or TASK')

    def match_trigger(self, message: str) -> str | None:
        """Match a trigger in the message.

        It returns the first trigger that matches the message.
        """
        message = message.lower()
        for trigger in self.triggers:
            if trigger.lower() in message:
                return trigger

        return None

    @property
    def triggers(self) -> list[str]:
        return self.metadata.triggers

```
**File:** openhands/microagent/microagent.py (L277-341)
```python
def load_microagents_from_dir(
    microagent_dir: Union[str, Path],
) -> tuple[dict[str, RepoMicroagent], dict[str, KnowledgeMicroagent]]:
    """Load all microagents from the given directory.

    Note, legacy repo instructions will not be loaded here.

    Args:
        microagent_dir: Path to the microagents directory (e.g. .openhands/microagents)

    Returns:
        Tuple of (repo_agents, knowledge_agents) dictionaries
    """
    if isinstance(microagent_dir, str):
        microagent_dir = Path(microagent_dir)

    repo_agents = {}
    knowledge_agents = {}

    # Load all agents from microagents directory
    logger.debug(f'Loading agents from {microagent_dir}')

    # Always check for .cursorrules and AGENTS.md files in repo root, regardless of whether microagents_dir exists
    special_files = []
    repo_root = microagent_dir.parent.parent

    # Check for .cursorrules
    if (repo_root / '.cursorrules').exists():
        special_files.append(repo_root / '.cursorrules')

    # Check for AGENTS.md (case-insensitive)
    for agents_filename in ['AGENTS.md', 'agents.md', 'AGENT.md', 'agent.md']:
        agents_path = repo_root / agents_filename
        if agents_path.exists():
            special_files.append(agents_path)
            break  # Only add the first one found to avoid duplicates

    # Collect .md files from microagents directory if it exists
    md_files = []
    if microagent_dir.exists():
        md_files = [f for f in microagent_dir.rglob('*.md') if f.name != 'README.md']

    # Process all files in one loop
    for file in chain(special_files, md_files):
        try:
            agent = BaseMicroagent.load(file, microagent_dir)
            if isinstance(agent, RepoMicroagent):
                repo_agents[agent.name] = agent
            elif isinstance(agent, KnowledgeMicroagent):
                # Both KnowledgeMicroagent and TaskMicroagent go into knowledge_agents
                knowledge_agents[agent.name] = agent
        except MicroagentValidationError as e:
            # For validation errors, include the original exception
            error_msg = f'Error loading microagent from {file}: {str(e)}'
            raise MicroagentValidationError(error_msg) from e
        except Exception as e:
            # For other errors, wrap in a ValueError with detailed message
            error_msg = f'Error loading microagent from {file}: {str(e)}'
            raise ValueError(error_msg) from e

    logger.debug(
        f'Loaded {len(repo_agents) + len(knowledge_agents)} microagents: '
        f'{[*repo_agents.keys(), *knowledge_agents.keys()]}'
    )
    return repo_agents, knowledge_agents
```
**File:** openhands/microagent/types.py (L11-37)
```python
class MicroagentType(str, Enum):
    """Type of microagent."""

    KNOWLEDGE = 'knowledge'  # Optional microagent, triggered by keywords
    REPO_KNOWLEDGE = 'repo'  # Always active microagent
    TASK = 'task'  # Special type for task microagents that require user input


class InputMetadata(BaseModel):
    """Metadata for task microagent inputs."""

    name: str
    description: str


class MicroagentMetadata(BaseModel):
    """Metadata for all microagents."""

    name: str = 'default'
    type: MicroagentType = Field(default=MicroagentType.REPO_KNOWLEDGE)
    version: str = Field(default='1.0.0')
    agent: str = Field(default='CodeActAgent')
    triggers: list[str] = []  # optional, only exists for knowledge microagents
    inputs: list[InputMetadata] = []  # optional, only exists for task microagents
    mcp_tools: MCPConfig | None = (
        None  # optional, for microagents that provide additional MCP tools
    )
```
**File:** openhands/resolver/issue_resolver.py (L52-100)
```python
class IssueResolver:
    GITLAB_CI = os.getenv('GITLAB_CI') == 'true'

    def __init__(self, args: Namespace) -> None:
        """Initialize the IssueResolver with the given parameters.

        Params initialized:
            owner: Owner of the repo.
            repo: Repository name.
            token: Token to access the repository.
            username: Username to access the repository.
            platform: Platform of the repository.
            runtime_container_image: Container image to use.
            max_iterations: Maximum number of iterations to run.
            output_dir: Output directory to write the results.
            llm_config: Configuration for the language model.
            prompt_template: Prompt template to use.
            issue_type: Type of issue to resolve (issue or pr).
            repo_instruction: Repository instruction to use.
            issue_number: Issue number to resolve.
            comment_id: Optional ID of a specific comment to focus on.
            base_domain: The base domain for the git server.
        """
        parts = args.selected_repo.rsplit('/', 1)
        if len(parts) < 2:
            raise ValueError('Invalid repository format. Expected owner/repo')
        owner, repo = parts

        token = (
            args.token
            or os.getenv('GITHUB_TOKEN')
            or os.getenv('GITLAB_TOKEN')
            or os.getenv('BITBUCKET_TOKEN')
            or os.getenv('AZURE_DEVOPS_TOKEN')
            or os.getenv('FORGEJO_TOKEN')
        )
        username = args.username if args.username else os.getenv('GIT_USERNAME')
        if not username:
            raise ValueError('Username is required.')

        if not token:
            raise ValueError('Token is required.')

        platform = call_async_from_sync(
            identify_token,
            GENERAL_TIMEOUT,
            token,
            args.base_domain,
        )
```
**File:** openhands/resolver/issue_resolver.py (L109-127)
```python
        # Read the prompt template
        prompt_file = args.prompt_file
        if prompt_file is None:
            if issue_type == 'issue':
                prompt_file = os.path.join(
                    os.path.dirname(__file__), 'prompts/resolve/basic-with-tests.jinja'
                )
            else:
                prompt_file = os.path.join(
                    os.path.dirname(__file__), 'prompts/resolve/basic-followup.jinja'
                )
        with open(prompt_file, 'r') as f:
            user_instructions_prompt_template = f.read()

        with open(
            prompt_file.replace('.jinja', '-conversation-instructions.jinja')
        ) as f:
            conversation_instructions_prompt_template = f.read()

```
**File:** openhands/resolver/issue_resolver.py (L182-211)
```python
    @classmethod
    def update_openhands_config(
        cls,
        config: OpenHandsConfig,
        max_iterations: int,
        workspace_base: str,
        base_container_image: str | None,
        runtime_container_image: str | None,
        is_experimental: bool,
        runtime: str | None = None,
    ) -> OpenHandsConfig:
        config.default_agent = 'CodeActAgent'
        # Use provided runtime or fallback to config value or default to 'docker'
        config.runtime = runtime or config.runtime or 'docker'
        config.max_budget_per_task = 4
        config.max_iterations = max_iterations

        # do not mount workspace
        config.workspace_base = workspace_base
        config.workspace_mount_path = workspace_base
        config.agents = {'CodeActAgent': AgentConfig(disabled_microagents=['github'])}

        cls.update_sandbox_config(
            config,
            base_container_image,
            runtime_container_image,
            is_experimental,
        )

        return config
```
**File:** openhands/resolver/issue_resolver.py (L305-312)
```python

        # Run setup script if it exists
        logger.info('Checking for .openhands/setup.sh script...')
        runtime.maybe_run_setup_script()

        # Setup git hooks if they exist
        logger.info('Checking for .openhands/pre-commit.sh script...')
        runtime.maybe_setup_git_hooks()
```
**File:** openhands/core/config/openhands_config.py (L84-86)
```python
    save_trajectory_path: str | None = Field(default=None)
    save_screenshots_in_trajectory: bool = Field(default=False)
    replay_trajectory_path: str | None = Field(default=None)
```
**File:** openhands/core/config/openhands_config.py (L104-106)
```python
    max_iterations: int = Field(default=OH_MAX_ITERATIONS)
    max_budget_per_task: float | None = Field(default=None)
    init_git_in_empty_workspace: bool = Field(default=False)
```
**File:** openhands/core/config/llm_config.py (L19-111)
```python
class LLMConfig(BaseModel):
    """Configuration for the LLM model.

    Attributes:
        model: The model to use.
        api_key: The API key to use.
        base_url: The base URL for the API. This is necessary for local LLMs.
        api_version: The version of the API.
        aws_access_key_id: The AWS access key ID.
        aws_secret_access_key: The AWS secret access key.
        aws_region_name: The AWS region name.
        num_retries: The number of retries to attempt.
        retry_multiplier: The multiplier for the exponential backoff.
        retry_min_wait: The minimum time to wait between retries, in seconds. This is exponential backoff minimum. For models with very low limits, this can be set to 15-20.
        retry_max_wait: The maximum time to wait between retries, in seconds. This is exponential backoff maximum.
        timeout: The timeout for the API.
        max_message_chars: The approximate max number of characters in the content of an event included in the prompt to the LLM. Larger observations are truncated.
        temperature: The temperature for the API.
        top_p: The top p for the API.
        top_k: The top k for the API.
        custom_llm_provider: The custom LLM provider to use. This is undocumented in openhands, and normally not used. It is documented on the litellm side.
        max_input_tokens: The maximum number of input tokens. Note that this is currently unused, and the value at runtime is actually the total tokens in OpenAI (e.g. 128,000 tokens for GPT-4).
        max_output_tokens: The maximum number of output tokens. This is sent to the LLM.
        input_cost_per_token: The cost per input token. This will available in logs for the user to check.
        output_cost_per_token: The cost per output token. This will available in logs for the user to check.
        ollama_base_url: The base URL for the OLLAMA API.
        drop_params: Drop any unmapped (unsupported) params without causing an exception.
        modify_params: Modify params allows litellm to do transformations like adding a default message, when a message is empty.
        disable_vision: If model is vision capable, this option allows to disable image processing (useful for cost reduction).
        caching_prompt: Use the prompt caching feature if provided by the LLM and supported by the provider.
        log_completions: Whether to log LLM completions to the state.
        log_completions_folder: The folder to log LLM completions to. Required if log_completions is True.
        custom_tokenizer: A custom tokenizer to use for token counting.
        native_tool_calling: Whether to use native tool calling if supported by the model. Can be True, False, or not set.
        reasoning_effort: The effort to put into reasoning. This is a string that can be one of 'low', 'medium', 'high', or 'none'. Can apply to all reasoning models.
        seed: The seed to use for the LLM.
        safety_settings: Safety settings for models that support them (like Mistral AI and Gemini).
        for_routing: Whether this LLM is used for routing. This is set to True for models used in conjunction with the main LLM in the model routing feature.
        completion_kwargs: Custom kwargs to pass to litellm.completion.
    """

    model: str = Field(default='claude-opus-4-5-20251101')
    api_key: SecretStr | None = Field(default=None)
    base_url: str | None = Field(default=None)
    api_version: str | None = Field(default=None)
    aws_access_key_id: SecretStr | None = Field(default=None)
    aws_secret_access_key: SecretStr | None = Field(default=None)
    aws_region_name: str | None = Field(default=None)
    openrouter_site_url: str = Field(default='https://docs.all-hands.dev/')
    openrouter_app_name: str = Field(default='OpenHands')
    # total wait time: 8 + 16 + 32 + 64 = 120 seconds
    num_retries: int = Field(default=5)
    retry_multiplier: float = Field(default=8)
    retry_min_wait: int = Field(default=8)
    retry_max_wait: int = Field(default=64)
    timeout: int | None = Field(default=None)
    max_message_chars: int = Field(
        default=30_000
    )  # maximum number of characters in an observation's content when sent to the llm
    temperature: float = Field(default=0.0)
    top_p: float = Field(default=1.0)
    top_k: float | None = Field(default=None)
    custom_llm_provider: str | None = Field(default=None)
    max_input_tokens: int | None = Field(default=None)
    max_output_tokens: int | None = Field(default=None)
    input_cost_per_token: float | None = Field(default=None)
    output_cost_per_token: float | None = Field(default=None)
    ollama_base_url: str | None = Field(default=None)
    # This setting can be sent in each call to litellm
    drop_params: bool = Field(default=True)
    # Note: this setting is actually global, unlike drop_params
    modify_params: bool = Field(default=True)
    disable_vision: bool | None = Field(default=None)
    disable_stop_word: bool | None = Field(default=False)
    caching_prompt: bool = Field(default=True)
    log_completions: bool = Field(default=False)
    log_completions_folder: str = Field(default=os.path.join(LOG_DIR, 'completions'))
    custom_tokenizer: str | None = Field(default=None)
    native_tool_calling: bool | None = Field(default=None)
    reasoning_effort: str | None = Field(default=None)
    seed: int | None = Field(default=None)
    safety_settings: list[dict[str, str]] | None = Field(
        default=None,
        description='Safety settings for models that support them (like Mistral AI and Gemini)',
    )
    for_routing: bool = Field(default=False)
    # The number of correction attempts for the LLM draft editor
    correct_num: int = Field(default=5)
    completion_kwargs: dict[str, Any] | None = Field(
        default=None,
        description='Custom kwargs to pass to litellm.completion',
    )

```
**File:** openhands/llm/model_features.py (L69-100)
```python
FUNCTION_CALLING_PATTERNS: list[str] = [
    # Anthropic families
    'claude-3-7-sonnet*',
    'claude-3.7-sonnet*',
    'claude-sonnet-3-7-latest',
    'claude-3-5-sonnet*',
    'claude-3.5-sonnet*',  # Accept dot-notation for Sonnet 3.5 as well
    'claude-3.5-haiku*',
    'claude-3-5-haiku*',
    'claude-sonnet-4*',
    'claude-opus-4*',
    # OpenAI families
    'gpt-4o*',
    'gpt-4.1',
    'gpt-5*',
    # o-series (keep exact o1 support per existing list)
    'o1-2024-12-17',
    'o3*',
    'o4-mini*',
    # Google Gemini
    'gemini-2.5-pro*',
    'gemini-3*',
    # Groq models (via groq/ provider prefix)
    'groq/*',
    # Others
    'kimi-k2-0711-preview',
    'kimi-k2-instruct',
    'qwen3-coder*',
    'qwen3-coder-480b-a35b-instruct',
    'deepseek-chat',
    'grok-code-fast-1',
]
```
**File:** openhands/runtime/impl (L1-1)
```text
[{"name":"__init__.py","path":"openhands/runtime/impl/__init__.py","sha":"00e04d3a38f761bfe99141532b69c2769c3b5bda","size":1156,"url":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/__init__.py?ref=main","html_url":"https://github.com/OpenHands/OpenHands/blob/main/openhands/runtime/impl/__init__.py","git_url":"https://api.github.com/repos/OpenHands/OpenHands/git/blobs/00e04d3a38f761bfe99141532b69c2769c3b5bda","download_url":"https://raw.githubusercontent.com/OpenHands/OpenHands/main/openhands/runtime/impl/__init__.py","type":"file","_links":{"self":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/__init__.py?ref=main","git":"https://api.github.com/repos/OpenHands/OpenHands/git/blobs/00e04d3a38f761bfe99141532b69c2769c3b5bda","html":"https://github.com/OpenHands/OpenHands/blob/main/openhands/runtime/impl/__init__.py"}},{"name":"action_execution","path":"openhands/runtime/impl/action_execution","sha":"c930ab91a8d1240fa859bb94759b3ed610605ac6","size":0,"url":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/action_execution?ref=main","html_url":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/action_execution","git_url":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/c930ab91a8d1240fa859bb94759b3ed610605ac6","download_url":null,"type":"dir","_links":{"self":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/action_execution?ref=main","git":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/c930ab91a8d1240fa859bb94759b3ed610605ac6","html":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/action_execution"}},{"name":"cli","path":"openhands/runtime/impl/cli","sha":"c6abfef2bc94cf11d296655520317f6f5641ba02","size":0,"url":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/cli?ref=main","html_url":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/cli","git_url":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/c6abfef2bc94cf11d296655520317f6f5641ba02","download_url":null,"type":"dir","_links":{"self":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/cli?ref=main","git":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/c6abfef2bc94cf11d296655520317f6f5641ba02","html":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/cli"}},{"name":"docker","path":"openhands/runtime/impl/docker","sha":"3f2894e551e8e41ca4eeef1096ca87ce16fc7870","size":0,"url":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/docker?ref=main","html_url":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/docker","git_url":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/3f2894e551e8e41ca4eeef1096ca87ce16fc7870","download_url":null,"type":"dir","_links":{"self":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/docker?ref=main","git":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/3f2894e551e8e41ca4eeef1096ca87ce16fc7870","html":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/docker"}},{"name":"kubernetes","path":"openhands/runtime/impl/kubernetes","sha":"8b5f68898881fa7c5215feb5b77af029d09f1da6","size":0,"url":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/kubernetes?ref=main","html_url":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/kubernetes","git_url":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/8b5f68898881fa7c5215feb5b77af029d09f1da6","download_url":null,"type":"dir","_links":{"self":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/kubernetes?ref=main","git":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/8b5f68898881fa7c5215feb5b77af029d09f1da6","html":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/kubernetes"}},{"name":"local","path":"openhands/runtime/impl/local","sha":"874d3f930415f5a708f0c044aac1b79646ec7ee0","size":0,"url":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/local?ref=main","html_url":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/local","git_url":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/874d3f930415f5a708f0c044aac1b79646ec7ee0","download_url":null,"type":"dir","_links":{"self":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/local?ref=main","git":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/874d3f930415f5a708f0c044aac1b79646ec7ee0","html":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/local"}},{"name":"remote","path":"openhands/runtime/impl/remote","sha":"df19c2692c94bdab1922aed1ca96fb6efa453977","size":0,"url":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/remote?ref=main","html_url":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/remote","git_url":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/df19c2692c94bdab1922aed1ca96fb6efa453977","download_url":null,"type":"dir","_links":{"self":"https://api.github.com/repos/OpenHands/OpenHands/contents/openhands/runtime/impl/remote?ref=main","git":"https://api.github.com/repos/OpenHands/OpenHands/git/trees/df19c2692c94bdab1922aed1ca96fb6efa453977","html":"https://github.com/OpenHands/OpenHands/tree/main/openhands/runtime/impl/remote"}}]
```
**File:** openhands/runtime/impl/local/local_runtime.py (L1-2)
```python
"""This runtime runs the action_execution_server directly on the local machine without Docker."""

```
**File:** config.template.toml (L1-100)
```text
###################### OpenHands Configuration Example ######################
#
# All settings have default values, so you only need to uncomment and
# modify what you want to change
# The fields within each section are sorted in alphabetical order.
#
##############################################################################

#################################### Core ####################################
# General core configurations
##############################################################################
[core]
# API keys and configuration for core services

# Base path for the workspace
#workspace_base = "./workspace"

# Cache directory path
#cache_dir = "/tmp/cache"

# Debugging enabled
#debug = false

# Disable color in terminal output
#disable_color = false

# Path to store trajectories, can be a folder or a file
# If it's a folder, the session id will be used as the file name
#save_trajectory_path="./trajectories"

# Whether to save screenshots in the trajectory
# The screenshots are encoded and can make trajectory json files very large
#save_screenshots_in_trajectory = false

# Path to replay a trajectory, must be a file path
# If provided, trajectory will be loaded and replayed before the
# agent responds to any user instruction
#replay_trajectory_path = ""

# File store path
#file_store_path = "/tmp/file_store"

# File store type
#file_store = "memory"

# Maximum file size for uploads, in megabytes
#file_uploads_max_file_size_mb = 0

# Enable the browser environment
#enable_browser = true

# Maximum budget per task, 0.0 means no limit
#max_budget_per_task = 0.0

# Maximum number of iterations
#max_iterations = 500

# Path to mount the workspace in the sandbox
#workspace_mount_path_in_sandbox = "/workspace"

# Path to mount the workspace
#workspace_mount_path = ""

# Path to rewrite the workspace mount path to
#workspace_mount_rewrite = ""

# Run as openhands
#run_as_openhands = true

# Runtime environment
#runtime = "docker"

# Name of the default agent
#default_agent = "CodeActAgent"

# JWT secret for authentication
#jwt_secret = ""

# Restrict file types for file uploads
#file_uploads_restrict_file_types = false

# List of allowed file extensions for uploads
#file_uploads_allowed_extensions = [".*"]

# Whether to enable the default LLM summarizing condenser when no condenser is specified in config
# When true, a LLMSummarizingCondenserConfig will be used as the default condenser
# When false, a NoOpCondenserConfig (no summarization) will be used
#enable_default_condenser = true

# Maximum number of concurrent conversations per user
#max_concurrent_conversations = 3

# Maximum age of conversations in seconds before they are automatically closed
#conversation_max_age_seconds = 864000  # 10 days

#################################### LLM #####################################
# Configuration for LLM models (group name starts with 'llm')
# use 'llm' for the default LLM config
##############################################################################
[llm]
```
**File:** config.template.toml (L380-435)
```text
#################################### Condenser #################################
# Condensers control how conversation history is managed and compressed when
# the context grows too large. Each agent uses one condenser configuration.
##############################################################################
[condenser]
# The type of condenser to use. Available options:
# - "noop": No condensing, keeps full history (default)
# - "observation_masking": Keeps full event structure but masks older observations
# - "recent": Keeps only recent events and discards older ones
# - "llm": Uses an LLM to summarize conversation history
# - "amortized": Intelligently forgets older events while preserving important context
# - "llm_attention": Uses an LLM to prioritize most relevant context
type = "noop"

# Examples for each condenser type (uncomment and modify as needed):

# 1. NoOp Condenser - No additional settings needed
#type = "noop"

# 2. Observation Masking Condenser
#type = "observation_masking"
# Number of most-recent events where observations will not be masked
#attention_window = 100

# 3. Recent Events Condenser
#type = "recent"
# Number of initial events to always keep (typically includes task description)
#keep_first = 1
# Maximum number of events to keep in history
#max_events = 100

# 4. LLM Summarizing Condenser
#type = "llm"
# Reference to an LLM config to use for summarization
#llm_config = "condenser"
# Number of initial events to always keep (typically includes task description)
#keep_first = 1
# Maximum size of history before triggering summarization
#max_size = 100

# 5. Amortized Forgetting Condenser
#type = "amortized"
# Number of initial events to always keep (typically includes task description)
#keep_first = 1
# Maximum size of history before triggering forgetting
#max_size = 100

# 6. LLM Attention Condenser
#type = "llm_attention"
# Reference to an LLM config to use for attention scoring
#llm_config = "condenser"
# Number of initial events to always keep (typically includes task description)
#keep_first = 1
# Maximum size of history before triggering attention mechanism
#max_size = 100

```
**File:** config.template.toml (L486-526)
```text
#################################### MCP #####################################
# Configuration for Model Context Protocol (MCP) servers
# MCP allows OpenHands to communicate with external tool servers
##############################################################################
[mcp]
# SSE servers - Server-Sent Events transport (legacy)
#sse_servers = [
#    # Basic SSE server with just a URL
#    "http://localhost:8080/mcp/sse",
#
#    # SSE server with authentication
#    {url = "https://api.example.com/mcp/sse", api_key = "your-api-key"}
#]

# SHTTP servers - Streamable HTTP transport (recommended)
#shttp_servers = [
#    # Basic SHTTP server with default 60s timeout
#    "https://api.example.com/mcp/shttp",
#
#    # SHTTP server with custom timeout for long-running tools
#    {
#        url = "https://api.example.com/mcp/shttp",
#        api_key = "your-api-key",
#        timeout = 180  # 3 minutes for processing-heavy tools (1-3600 seconds)
#    }
#]

# Stdio servers - Direct process communication (development only)
#stdio_servers = [
#    # Basic stdio server
#    {name = "filesystem", command = "npx", args = ["@modelcontextprotocol/server-filesystem", "/"]},
#
#    # Stdio server with environment variables
#    {
#        name = "fetch",
#        command = "uvx",
#        args = ["mcp-server-fetch"],
#        env = {DEBUG = "true"}
#    }
#]

```
**File:** openhands/core/config/sandbox_config.py (L75-78)
```python
    enable_auto_lint: bool = Field(
        default=False
    )  # once enabled, OpenHands would lint files after editing
    use_host_network: bool = Field(default=False)
```
**File:** openhands/resolver/resolve_issue.py (L8-100)
```python
def main() -> None:
    import argparse

    def int_or_none(value: str) -> int | None:
        if value.lower() == 'none':
            return None
        else:
            return int(value)

    parser = argparse.ArgumentParser(description='Resolve a single issue.')
    parser.add_argument(
        '--selected-repo',
        type=str,
        required=True,
        help='repository to resolve issues in form of `owner/repo`.',
    )
    parser.add_argument(
        '--token',
        type=str,
        default=None,
        help='token to access the repository.',
    )
    parser.add_argument(
        '--username',
        type=str,
        default=None,
        help='username to access the repository.',
    )
    parser.add_argument(
        '--base-container-image',
        type=str,
        default=None,
        help='base container image to use.',
    )
    parser.add_argument(
        '--runtime-container-image',
        type=str,
        default=None,
        help='Container image to use.',
    )
    parser.add_argument(
        '--runtime',
        type=str,
        default=None,
        help='Runtime environment to use (default: docker).',
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=50,
        help='Maximum number of iterations to run.',
    )
    parser.add_argument(
        '--issue-number',
        type=int,
        required=True,
        help='Issue number to resolve.',
    )
    parser.add_argument(
        '--comment-id',
        type=int_or_none,
        required=False,
        default=None,
        help='Resolve a specific comment',
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory to write the results.',
    )
    parser.add_argument(
        '--llm-model',
        type=str,
        default=None,
        help='LLM model to use.',
    )
    parser.add_argument(
        '--llm-api-key',
        type=str,
        default=None,
        help='LLM API key to use.',
    )
    parser.add_argument(
        '--llm-base-url',
        type=str,
        default=None,
        help='LLM base URL to use.',
    )
    parser.add_argument(
        '--prompt-file',
        type=str,
        default=None,
```
**File:** openhands/agenthub/codeact_agent/prompts/system_prompt.j2 (L49-96)
```jinja
<PROBLEM_SOLVING_WORKFLOW>
1. EXPLORATION: Thoroughly explore relevant files and understand the context before proposing solutions
2. ANALYSIS: Consider multiple approaches and select the most promising one
3. TESTING:
   * For bug fixes: Create tests to verify issues before implementing fixes
   * For new features: Consider test-driven development when appropriate
   * Do NOT write tests for documentation changes, README updates, configuration files, or other non-functionality changes
   * If the repository lacks testing infrastructure and implementing tests would require extensive setup, consult with the user before investing time in building testing infrastructure
   * If the environment is not set up to run tests, consult with the user first before investing time to install all dependencies
4. IMPLEMENTATION:
   * Make focused, minimal changes to address the problem
   * Always modify existing files directly rather than creating new versions with different suffixes
   * If you create temporary files for testing, delete them after confirming your solution works
5. VERIFICATION: If the environment is set up to run tests, test your implementation thoroughly, including edge cases. If the environment is not set up to run tests, consult with the user first before investing time to run tests.
</PROBLEM_SOLVING_WORKFLOW>

<SECURITY>
* Only use GITHUB_TOKEN and other credentials in ways the user has explicitly requested and would expect.
* Use APIs to work with GitHub or other platforms, unless the user asks otherwise or your task requires browsing.
</SECURITY>

<SECURITY_RISK_ASSESSMENT>
{% include 'security_risk_assessment.j2' %}
</SECURITY_RISK_ASSESSMENT>

<EXTERNAL_SERVICES>
* When interacting with external services like GitHub, GitLab, Bitbucket, or Azure DevOps, use their respective APIs instead of browser-based interactions whenever possible.
* Only resort to browser-based interactions with these services if specifically requested by the user or if the required operation cannot be performed via API.
</EXTERNAL_SERVICES>

<ENVIRONMENT_SETUP>
* When user asks you to run an application, don't stop if the application is not installed. Instead, please install the application and run the command again.
* If you encounter missing dependencies:
  1. First, look around in the repository for existing dependency files (requirements.txt, pyproject.toml, package.json, Gemfile, etc.)
  2. If dependency files exist, use them to install all dependencies at once (e.g., `pip install -r requirements.txt`, `npm install`, etc.)
  3. Only install individual packages directly if no dependency files are found or if only specific packages are needed
* Similarly, if you encounter missing dependencies for essential tools requested by the user, install them when possible.
</ENVIRONMENT_SETUP>

<TROUBLESHOOTING>
* If you've made repeated attempts to solve a problem but tests still fail or the user reports it's still broken:
  1. Step back and reflect on 5-7 different possible sources of the problem
  2. Assess the likelihood of each possible cause
  3. Methodically address the most likely causes, starting with the highest probability
  4. Document your reasoning process
* When you run into any major issue while executing a plan from the user, please don't try to directly work around it. Instead, propose a new plan and confirm with the user before proceeding.
</TROUBLESHOOTING>

```

---

## Official / 2026 links

- [Headless mode](https://docs.openhands.dev/openhands/usage/run-openhands/headless-mode)
- [SDK index](https://docs.openhands.dev/sdk/index) · [Agent Server](https://docs.openhands.dev/sdk/guides/agent-server/overview) · [Docker sandbox](https://docs.openhands.dev/sdk/guides/agent-server/docker-sandbox)
- [GitHub `All-Hands-AI/OpenHands`](https://github.com/All-Hands-AI/OpenHands)
- Gap notes: [`research_overnight_stack_web/gap_wave2/findings_gap_openhands_production.md`](research_overnight_stack_web/gap_wave2/findings_gap_openhands_production.md)
