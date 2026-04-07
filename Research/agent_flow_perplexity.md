# From Watch-and-Guide to Plan-and-Review: Building an Autonomous Agentic Coding Workflow

## Executive Summary

The transition from active agent supervision to a plan-and-review workflow is achievable today using a combination of open-source tooling, structured harness architectures, and disciplined context engineering. Stanford's AgentFlow framework demonstrates the power of modular agent decomposition — splitting work into Planner, Executor, Verifier, and Generator modules — while Anthropic's long-running agent harness provides a battle-tested pattern for overnight autonomous coding sessions. This report analyses the AgentFlow architecture, maps its principles to practical coding tools available within a ~$60/month budget, and provides specific implementation strategies for achieving autonomous overnight execution with minimal supervision.[^1]

***

## AgentFlow: Core Architecture and Transferable Concepts

### The Four-Module System

AgentFlow is a trainable, tool-integrated agentic framework developed at Stanford that coordinates four specialised modules through shared evolving memory:

| Module | Role | Trainable? | Analogue in Coding Workflow |
|--------|------|------------|---------------------------|
| **Planner** | Analyses query, selects sub-goals and tools, retrieves context from memory | Yes (via Flow-GRPO) | Your planning/prompting phase — the specification and task breakdown |
| **Executor** | Invokes the selected tool with context, returns execution result | No (frozen) | The coding agent (Claude Code, Aider, OpenHands) executing the plan |
| **Verifier** | Evaluates execution validity, checks if accumulated memory is sufficient to solve the query | No (frozen) | Automated tests, linters, and validation harnesses |
| **Generator** | Produces final output once verification passes | No (frozen) | Git commit + progress update at task completion |

The system operates as a multi-turn Markov Decision Process. At each turn, the Planner observes the current state (query, toolset, memory), selects an action, the Executor runs it, the Verifier checks results and updates memory, and the cycle repeats until the task is solved or a turn budget is exhausted.

### Evolving Memory — The Critical Innovation

AgentFlow's memory state is a deterministic, structured record of the reasoning process that updates after each turn. This is directly applicable to coding workflows: rather than relying on a single context window that degrades over time, the system maintains an explicit log of what has been done, what worked, and what remains. This concept maps directly to the `claude-progress.txt` and feature-list patterns used in Anthropic's long-running agent harness.[^1]

### Flow-GRPO and What It Means for Practitioners

Flow-GRPO is AgentFlow's reinforcement learning algorithm that trains the Planner on-policy inside the multi-turn loop. While training custom RL models is beyond most individual developers' budgets, the principle is directly applicable: **the quality of your planning phase determines the quality of autonomous execution**. AgentFlow demonstrated that a well-optimised 7B-parameter planner outperforms GPT-4o across 10 benchmarks, achieving +14.9% on search tasks, +14.0% on agentic reasoning, +14.5% on mathematical reasoning, and +4.1% on scientific reasoning. The lesson is clear — investing time in better planning (specifications, task decomposition, tool selection) yields outsized returns compared to simply using a larger model.

### Key Takeaways from AgentFlow for Your Workflow

1. **Modular decomposition beats monolithic execution.** Separate planning from execution from verification. Do not let a single agent handle everything in one pass.
2. **Structured memory bridges context windows.** Use explicit, deterministic progress tracking rather than relying on the model's ability to recall prior context.
3. **Verification must be automated and rigorous.** AgentFlow's Verifier module produces a binary signal — pass or continue. Map this to automated test suites that gate progress.
4. **Incremental sub-goals outperform one-shot approaches.** AgentFlow decomposes problems into sequential turns, each with a specific sub-goal and tool selection.

***

## Anthropic's Long-Running Agent Harness: The Production Blueprint

### Architecture Overview

Anthropic's engineering team developed a two-agent architecture that enables Claude to work effectively across many context windows for extended periods:[^1]

- **Initialiser Agent**: Runs once at project start. Sets up the environment including an `init.sh` script, a comprehensive feature list in JSON format, a `claude-progress.txt` file, and an initial git commit.[^1]
- **Coding Agent**: Runs in every subsequent session. Reads progress files and git logs, selects the highest-priority incomplete feature, implements it incrementally, tests it end-to-end, commits with descriptive messages, and updates progress notes.[^1]

This architecture directly addresses the two primary failure modes of long-running agents: (1) attempting to do too much at once (one-shotting), and (2) prematurely declaring the project complete.[^1]

### Feature List as Contract

The feature list is maintained in JSON format because models are less likely to inappropriately modify or overwrite JSON files compared to Markdown. Each feature includes a description, acceptance steps, and a `passes` boolean. Coding agents are instructed with strongly-worded rules like "It is unacceptable to remove or edit tests" to prevent the agent from gaming its own success metrics.[^1]

### The Session Startup Sequence

Every coding agent session follows a standardised sequence:[^1]

1. Run `pwd` to confirm the working directory
2. Read git logs and progress files to understand recent work
3. Read the feature list and choose the highest-priority incomplete feature
4. Run `init.sh` to start the development server
5. Run a basic end-to-end test to verify the app is in a working state
6. Begin implementation of a single feature
7. Test the feature end-to-end (using browser automation where applicable)
8. Commit progress and update the progress file

### Results

Using this architecture, Anthropic built a complete clone of claude.ai with 200+ features implemented autonomously. The community has replicated similar results — one developer built 61 features for a Rust API server overnight using the Context Engine harness, with zero human intervention after initial setup.[^2][^3][^1]

***

## Alternative Open-Source Tools and Frameworks

### Coding Agent Comparison

| Tool            | Type                     | Cost                         | Autonomous Mode                            | Best For                                              |
| --------------- | ------------------------ | ---------------------------- | ------------------------------------------ | ----------------------------------------------------- |
| **Claude Code** | Terminal agent           | $20/mo (Pro) – $200/mo (Max) | `--dangerously-skip-permissions` + harness | Long-running autonomous sessions with sub-agents      |
| **Aider**       | Terminal pair programmer | Free (OSS) + API costs       | `--message` + `--yes` flags for scripting  | Scripted batch operations, budget-conscious workflows |
| **OpenHands**   | Full autonomous platform | Free (OSS) + API costs       | Headless mode (`--headless -t "task"`)     | Self-hosted autonomous execution on VPS               |
| **SWE-Agent**   | Issue-to-PR agent        | Free (OSS) + API costs       | CLI (`sweagent run --issue URL`)           | GitHub issue resolution, benchmarking                 |
| **Cursor**      | IDE with AI              | $20–$200/mo                  | Background agents (limited)                | Interactive development, code exploration             |
| **Cline**       | VSCode agent             | Free (OSS) + API costs       | Configurable auto-approve                  | Editor-native workflows with model flexibility        |

### OpenHands — Best Self-Hosted Option

OpenHands (formerly OpenDevin) is the strongest candidate for VPS-hosted autonomous execution. It provides sandboxed Docker environments, a model-agnostic architecture supporting any LLM, headless mode for scripting, and REST/WebSocket APIs for integration. Installation is straightforward:[^15][^10][^16]

```bash
uv tool install openhands --python 3.12
openhands serve
```

Or via Docker:

```bash
docker run -it --rm --pull=always \
  -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server \
  -e LOG_ALL_EVENTS=true \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/.openhands \
  -p 3000:3000 \
  --add-host host.docker.internal:host-gateway \
  --name openhands-app \
  docker.openhands.dev/openhands/openhands:1.4
```

Headless mode enables fully autonomous task execution:[^8]

```bash
openhands --headless -t "Implement the authentication module per spec in TASKS.md" \
  -i 50 -b 10.0
```

### Context Engine — Best Autonomous Harness

The Context Engine project provides a four-layer memory architecture specifically designed for overnight autonomous coding:[^3]

| Memory Layer | Purpose | Lifecycle |
|-------------|---------|-----------|
| Working Context | Current task only | Rebuilt each session |
| Episodic Memory | Recent decisions, patterns | Rolling window |
| Semantic Memory | Project knowledge, architecture | Persistent |
| Procedural Memory | What worked, what failed | Append-only |

The autonomous loop operates as: compile context → implement feature → run tests → sub-agent review → commit → exit → repeat. It integrates with Claude Code's hooks system, using `SessionStart` and `PreCompact` hooks to automatically save and restore context across sessions.[^17][^2][^3]

***

## Proposed Architecture Within $60/Month Budget

### Budget Allocation

| Component | Tool | Monthly Cost | Purpose |
|-----------|------|-------------|---------|
| Planning & interactive work | Claude Pro (subscription) | $20 | Claude Code CLI + web for planning, spec writing, interactive sessions |
| Autonomous execution engine | Aider (OSS) + Anthropic API | ~$10–15 variable | Scripted autonomous execution with `--message` and `--yes` flags |
| Self-hosted agent platform | OpenHands on VPS | $0 (OSS) | Headless autonomous execution, sandboxed environment |
| VPS infrastructure | 4-core, 8GB RAM VPS | $25–30 | Docker host for OpenHands, overnight batch runs |
| **Total** | | **~$55–65/mo** | |

This architecture provides three tiers of agent interaction:

1. **Interactive planning** (Claude Pro): Use Claude Code or the web UI for spec writing, architecture decisions, and task decomposition. This is where planning ability and context engineering skills are invested.
2. **Scripted batch execution** (Aider): For well-defined, repetitive tasks like applying the same refactoring across many files, running through a list of fixes, or implementing boilerplate from specs.[^6]
3. **Autonomous sessions** (OpenHands on VPS): For complex, multistep feature implementation that runs unattended overnight.[^9][^8]

### Alternative Higher-Budget Configuration

If outcomes justify it, upgrading to Claude Max 5x ($100/mo) unlocks the most capable autonomous coding experience with Claude Code's `--dangerously-skip-permissions` mode and sub-agent orchestration. Combined with a VPS ($30/mo), this provides approximately $130/mo total but delivers the most polished autonomous experience currently available.[^4][^5]

***

## Implementation Strategy: Achieving Overnight Autonomous Execution

### Phase 1: Planning Infrastructure (Week 1)

Establish the specification and task-tracking system that agents will consume. This maps directly to AgentFlow's Planner module and Anthropic's Initialiser Agent.[^1]

**Create a standardised project specification format:**

```
project-root/
├── .agents.md              # Agent behaviour rules and project conventions
├── .openspec/
│   ├── spec.md             # Full project specification
│   └── architecture.md     # Architecture decisions
├── features.json           # Feature list with pass/fail tracking (JSON)
├── progress.md             # Session-by-session progress log
├── init.sh                 # Environment setup script
└── tasks/
    ├── current.md          # Current sprint tasks
    └── completed/          # Archive of completed task specs
```

**The `features.json` contract** (following Anthropic's pattern):[^1]

```json
[
  {
    "id": "AUTH-001",
    "category": "authentication",
    "description": "User can register with email and password",
    "steps": [
      "Navigate to /register",
      "Fill in email and password fields",
      "Submit form",
      "Verify user is created in database",
      "Verify redirect to dashboard"
    ],
    "passes": false,
    "priority": 1,
    "dependencies": []
  }
]
```

### Phase 2: Verification Harness (Week 2)

AgentFlow's Verifier module is the key to autonomous execution — without automated verification, agents will mark features as complete prematurely. Build a verification layer that includes:[^1]

- **Unit tests**: Automatically run after every change. The agent must pass all existing tests before proceeding.
- **Integration tests**: For API endpoints, database operations, and service interactions.
- **End-to-end tests**: Use Playwright or Puppeteer for web applications. Anthropic found that browser automation testing "dramatically improved performance".[^1]
- **Lint and type checks**: Run linters and type checkers as mandatory gates.
- **A gate script**: A single `verify.sh` that runs all checks and returns pass/fail:

```bash
#!/bin/bash
set -e
echo "Running linter..."
npm run lint
echo "Running type check..."
npm run typecheck
echo "Running unit tests..."
npm run test
echo "Running integration tests..."
npm run test:integration
echo "All checks passed ✅"
```

### Phase 3: Autonomous Execution Loop (Week 3)

**Option A: Aider-based scripted loop** (budget-friendly):[^6]

```bash
#!/bin/bash
# overnight-agent.sh — runs on VPS via tmux/screen

FEATURES=$(python3 -c "
import json
with open('features.json') as f:
    features = json.load(f)
for feat in sorted(features, key=lambda x: x['priority']):
    if not feat['passes']:
        print(feat['id'] + '|' + feat['description'])
        break
")

FEAT_ID=$(echo "$FEATURES" | cut -d'|' -f1)
FEAT_DESC=$(echo "$FEATURES" | cut -d'|' -f2)

if [ -z "$FEAT_ID" ]; then
    echo "All features complete!"
    exit 0
fi

echo "Working on: $FEAT_ID - $FEAT_DESC"

# Run aider with the task
aider --model sonnet --yes --auto-commits \
  --message "Implement feature $FEAT_ID: $FEAT_DESC. 
  Read features.json for acceptance criteria. 
  Run verify.sh after changes. 
  Only mark as passing if all tests pass." \
  src/ tests/ features.json

# Run verification
if ./verify.sh; then
    python3 -c "
import json
with open('features.json', 'r+') as f:
    features = json.load(f)
    for feat in features:
        if feat['id'] == '$FEAT_ID':
            feat['passes'] = True
    f.seek(0)
    json.dump(features, f, indent=2)
    f.truncate()
"
    git add -A && git commit -m "Feature $FEAT_ID: $FEAT_DESC [automated]"
    echo "$FEAT_ID completed at $(date)" >> progress.md
fi

# Continue to next feature
exec "$0"
```

**Option B: OpenHands headless loop** (more capable):[^8][^9]

```bash
#!/bin/bash
# Run on VPS with OpenHands installed

while true; do
    NEXT_TASK=$(python3 get_next_task.py)
    if [ -z "$NEXT_TASK" ]; then
        echo "All tasks complete at $(date)"
        break
    fi

    echo "Starting task: $NEXT_TASK at $(date)" >> progress.md

    openhands --headless \
      -t "$NEXT_TASK" \
      -d ./project \
      -i 50 \
      -b 5.0

    if ./verify.sh; then
        python3 mark_complete.py "$NEXT_TASK"
        git add -A && git commit -m "Completed: $NEXT_TASK [automated]"
    else
        echo "FAILED: $NEXT_TASK at $(date)" >> progress.md
        git stash  # Preserve working state
    fi
done
```

**Option C: Claude Code autonomous harness** (if upgrading to Max):[^5][^2]

```bash
# Run in tmux session on VPS
claude --dangerously-skip-permissions \
  --resume overnight-session \
  --max-turns 200 \
  "Read features.json. Work through features one at a time, 
   starting with the highest priority incomplete feature. 
   For each feature: implement it, run verify.sh, only mark 
   as passing if all tests pass. Commit after each feature. 
   Update progress.md. Continue to the next feature."
```

### Phase 4: Monitoring and Review (Ongoing)

Set up lightweight monitoring so the morning review is efficient:

- **Git log review**: `git log --oneline --since="12 hours ago"` shows what was accomplished overnight.
- **Progress file diff**: `git diff HEAD~10 progress.md` shows the narrative of what happened.
- **Feature completion dashboard**: A simple script that counts `"passes": true` vs `"passes": false` in `features.json`.
- **Failure alerts** (optional): Use a webhook or email notification if the loop encounters repeated failures.
- **Cost tracking**: Monitor API spend with `--max-budget-usd` flags on OpenHands or Aider's built-in cost tracking.[^9]

***

## Strategies for Improving Agent Reliability

### Context Engineering Best Practices

The single most impactful skill for reducing agent intervention is context engineering — ensuring the agent has exactly the right information at the right time.[^18] [context-best-practices]

- **Ground in code, not abstractions.** Instead of "add rate limiting middleware," prompt "search for existing middleware patterns in src/middleware/, check our Redis configuration in config/, then propose rate limiting that follows the same error handling and export structure".[^19]
- **Use `.agents.md` as a living document.** Include project-specific patterns, naming conventions, architectural decisions, and explicit do/don't rules. Keep it concise — under 2,000 tokens — to avoid consuming too much context window.[^20]
- **Provide examples of desired output.** Show the agent a completed feature file as a template for new features. Concrete examples consistently outperform abstract instructions.[^19]
- **Pre-load context deliberately.** Use "explain how X works" prompts to force the agent to read and load relevant code into its context window before making changes.[^19]

### Structural Safeguards

- **Git as safety net.** Every change should be committed incrementally. If something goes wrong, `git reset --hard HEAD~1` recovers instantly.[^5][^1]
- **Turn budgets.** Set maximum iterations (`--max-turns`, `-i 50`) to prevent infinite loops.[^5][^9]
- **Cost caps.** Use `--max-budget-usd` to prevent runaway API spending during autonomous sessions.[^9][^5]
- **Sandboxed execution.** Run autonomous agents inside Docker containers or on a VPS, never directly on a machine with production data or credentials.[^5]
- **Feature isolation.** Each feature should be implementable independently. Avoid tasks that require coordinated changes across multiple subsystems in a single agent session.[^1]

### Reducing Common Failure Modes

| Failure Mode                                     | Prevention Strategy                                                                                       |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Agent declares task complete prematurely         | Require automated test passage before marking complete; use JSON feature tracking                         |
| Agent gets stuck in error loops                  | Set turn budgets; procedural memory logs what failed to prevent repetition                                |
| Context degradation over long sessions           | Use session-based architecture with fresh context per task; leverage hooks for context injection          |
| Agent modifies the wrong files                   | Explicit file scoping in prompts; `.agents.md` with directory structure documentation                     |
| Agent skips broader fixes for current task       | Decompose into separate features in `features.json`; each session focuses on one feature only             |
| Hallucinated API calls or non-existent functions | Ground agents with actual codebase search before implementation; provide relevant file contents in prompt |

### The Plan-and-Review Mindset Shift

The shift from watching an agent to reviewing its output requires a fundamental change in how work is structured:[^20]

- **Planning becomes the primary skill.** The quality of the specification directly determines the quality of autonomous output. Invest 30–60 minutes writing a detailed spec for every 4–8 hours of autonomous execution.
- **Decomposition is essential.** Break every project into features that can be independently implemented, tested, and verified. If a feature cannot be tested in isolation, it is too large.
- **Review replaces monitoring.** Instead of watching the agent think, review git diffs, test results, and progress logs the next morning. This is faster and more effective than real-time supervision.
- **Iteration replaces perfection.** Accept that autonomous output will sometimes be 80% correct. Quick manual fixes on a mostly-complete implementation are still dramatically faster than building from scratch.

***

## Recommended Implementation Roadmap

### Immediate Actions (This Week)

1. Set up a VPS (4-core, 8GB RAM, ~$25–30/mo from providers like Hetzner, Contabo, or DigitalOcean).
2. Install Docker, OpenHands, and Aider on the VPS.
3. Create the project specification structure (`features.json`, `progress.md`, `init.sh`, `.agents.md`).
4. Write a `verify.sh` script for the current project with all automated checks.

### Short-Term (Weeks 2–3)

5. Run the first supervised autonomous session — start the loop, check in after 1 hour, then 2 hours, extending gradually.
6. Iterate on `.agents.md` based on what the agent gets wrong. Add specific do/don't rules for observed failure patterns.
7. Set up the overnight loop script with git-based recovery and progress logging.
8. Establish a morning review routine: git log → progress diff → feature completion count → targeted code review.

### Medium-Term (Month 2+)

9. Develop reusable specification templates for common feature types.
10. Build a library of context engineering prompts that reliably produce good autonomous output.
11. Experiment with multi-agent patterns — separate agents for implementation, testing, and code review.[^21]
12. Consider upgrading to Claude Max if autonomous session quality and throughput justify the cost.[^4]

This phased approach transforms the current watch-and-guide workflow into a structured plan-and-review process, where overnight autonomous execution becomes a reliable part of the development cycle rather than an experimental novelty.

---

## References

1. [How to Build AI Agents That Work While You Sleep](https://www.linkedin.com/pulse/how-build-ai-agents-work-while-you-sleep-anthropics-coding-avramenko-9kwdc) - Anthropic's engineering team recently published their breakthrough approach to building a complete c...

2. [I built an autonomous harness for Claude Code that ...](https://www.reddit.com/r/ClaudeAI/comments/1pk230x/i_built_an_autonomous_harness_for_claude_code/) - I made a harness for long-running Claude Code sessions with GitHub integration ... I built 18 autono...

3. [zeddy89/Context-Engine](https://github.com/zeddy89/Context-Engine) - Autonomous project builder for Claude Code that doesn't forget what it's doing. Built 61 features fo...

4. [Claude Code Pricing](https://www.claudelog.com/claude-code-pricing/) - Claude AI price breakdown: Pro from $17/month vs Max from $100/month plans, API costs, usage limits....

5. [Claude Code Autonomous Mode: Complete Guide to](https://pasqualepillitteri.it/en/news/141/claude-code-dangerously-skip-permissions-guide-autonomous-mode) - Complete guide to --dangerously-skip-permissions and Claude Code permission modes. Learn how to conf...

6. [Scripting aider | Synthetic Souls](https://synthetic-souls.nlr.ai/venv/lib/python3.12/site-packages/aider/website/docs/scripting) - You can script aider via the command line or python.

7. [GitHub - Aider-AI/aider: aider is AI pair programming in your terminal](https://github.com/Aider-AI/aider) - aider is AI pair programming in your terminal. Contribute to Aider-AI/aider development by creating ...

8. [Headless Mode](https://docs.openhands.dev/openhands/usage/cli/headless) - Run OpenHands without UI for scripting, automation, and CI/CD pipelines

9. [Headless - OpenHands Docs](https://docs.openhands.dev/openhands/usage/run-openhands/headless-mode) - You can run OpenHands with a single command, without starting the web application. This makes it eas...

10. [Setup - OpenHands Docs](https://docs.openhands.dev/openhands/usage/run-openhands/local-setup) - Getting started with running OpenHands on your own.

11. [OpenHands vs SWE-Agent: Best AI Coding Agent 2026](https://localaimaster.com/blog/openhands-vs-swe-agent) - Complete comparison of OpenHands and SWE-Agent. SWE-bench benchmarks, architecture, setup guides.

12. [Claude Code vs Cursor: What to Choose in 2026](https://www.builder.io/blog/cursor-vs-claude-code) - Claude Code vs Cursor compared across features, pricing, and background agents. Based on daily use o...

13. [Claude Code vs Cursor 2026: Features, Pricing & Real ...](https://spectrumailab.com/blog/claude-code-vs-cursor) - Terminal-based Claude Code vs full IDE Cursor compared by developers who use both daily. Pricing and...

14. [Top 11 Open-Source Autonomous Agents & Frameworks in 2025](https://cline.bot/blog/top-11-open-source-autonomous-agents-frameworks-in-2025) - Discover the Top 11 Open-Source Autonomous coding agents and frameworks of 2025, including Cline and...

15. [[2511.03690] The OpenHands Software Agent SDK: A Composable ...](https://arxiv.org/abs/2511.03690) - Agents are now used widely in the process of software development, but building production-ready sof...

16. [OpenHands - AI Code Editor Tool | Detailed Review & Features](https://www.aicodeide.org/ai-code-editor/openhands) - AI-Powered Autonomous Development: OpenHands agents can autonomously modify code, run commands, brow...

17. [Claude Code Session Hooks: Auto-Load Context Every Time](https://claudefa.st/blog/tools/hooks/session-lifecycle-hooks) - Claude Fast | SessionStart, SessionEnd, Setup, and PreCompact hooks for Claude Code. Auto-load conte...

18. [How to build reliable AI workflows with agentic primitives ...](https://github.blog/ai-and-ml/github-copilot/how-to-build-reliable-ai-workflows-with-agentic-primitives-and-context-engineering/) - Agentic workflows in Markdown apply prompt and context engineering that leverages agent primitives t...

19. [Planning & Execution - Master Agentic Coding](https://agenticoding.ai/docs/practical-techniques/lesson-7-planning-execution) - Lesson 5: Grounding covered how RAG and semantic search enable agents to retrieve context from your ...

20. [Refactoring & Code Quality...](https://www.digitalapplied.com/blog/practical-agentic-engineering-workflow-2025) - Master production agentic engineering: blast radius frameworks, GPT-5 Codex vs Claude, parallel agen...

21. [I built 18 autonomous agents to run my entire dev cycle in ...](https://www.reddit.com/r/ClaudeAI/comments/1qfu9pm/i_built_18_autonomous_agents_to_run_my_entire_dev/) - I built 18 autonomous agents to run my entire dev cycle in Claude Code. After months of running para...

---

## Official / 2026 links

- [agentflow.stanford.edu](https://agentflow.stanford.edu/) · [arXiv 2510.05592](https://arxiv.org/html/2510.05592)
- [`research_overnight_stack_web/findings_orchestration_deer_agentflow_gas.md`](research_overnight_stack_web/findings_orchestration_deer_agentflow_gas.md)
