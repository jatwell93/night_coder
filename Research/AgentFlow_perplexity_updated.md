# From Watch-and-Guide to Plan-and-Review: Building an Autonomous Agentic Coding Workflow

## Executive Summary

The transition from active agent supervision to a plan-and-review workflow is achievable today using a combination of open-source tooling, structured harness architectures, and disciplined context engineering. Stanford's AgentFlow framework demonstrates the power of modular agent decomposition — splitting work into Planner, Executor, Verifier, and Generator modules — while Anthropic's long-running agent harness provides a battle-tested pattern for overnight autonomous coding sessions. This report analyses the AgentFlow architecture, maps its principles to practical coding tools available within a ~$60/month budget, and provides specific implementation strategies for achieving autonomous overnight execution with minimal supervision.[^1]

Three additional innovations sharpen this plan beyond basic agent loops: **GUARDRAILS.md** as a persistent failure-memory protocol that prevents agents from repeating mistakes across sessions; **model cascading** via OpenRouter to route cheap models for simple tasks and escalate to frontier models only when needed, cutting API costs by 40–85%; and the **OpenHands V1 SDK's two-phase planning-agent architecture** with built-in security analysis, sub-agent delegation, and read-only planning tools that enforce true separation between planning and execution.[^2][^3][^4][^5][^6]

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

Flow-GRPO is AgentFlow's reinforcement learning algorithm that trains the Planner on-policy inside the multi-turn loop. While training custom RL models is beyond most individual developers' budgets, the principle is directly applicable: **the quality of your planning phase determines the quality of autonomous execution**. AgentFlow demonstrated that a well-optimised 7B-parameter planner outperforms GPT-4o across 10 benchmarks, achieving +14.9% on search tasks, +14.0% on agentic reasoning, +14.5% on mathematical reasoning, and +4.1% on scientific reasoning. The lesson is clear — investing time in better planning (specifications, task decomposition, tool selection) yields outsised returns compared to simply using a larger model.

### "The Gutter" — Why Persistent Memory Matters

The GUARDRAILS.md methodology identifies a critical failure mode called "The Gutter" that directly threatens overnight autonomous execution. When an agent's context window fills with error logs and failed attempts, it begins prioritising recent failures over its original instructions, entering a recursive loop of repeated mistakes. Unlike compilers that fail deterministically, AI agents fail stochastically — the same prompt might succeed nine times and catastrophically fail on the tenth. AgentFlow's evolving memory was designed to solve exactly this problem at the framework level, and GUARDRAILS.md provides a file-based equivalent for practical coding workflows.[^4]

### Key Takeaways from AgentFlow for Your Workflow

1. **Modular decomposition beats monolithic execution.** Separate planning from execution from verification. Do not let a single agent handle everything in one pass.
2. **Structured memory bridges context windows.** Use explicit, deterministic progress tracking rather than relying on the model's ability to recall prior context.
3. **Verification must be automated and rigorous.** AgentFlow's Verifier module produces a binary signal — pass or continue. Map this to automated test suites that gate progress.
4. **Incremental sub-goals outperform one-shot approaches.** AgentFlow decomposes problems into sequential turns, each with a specific sub-goal and tool selection.
5. **Persistent failure memory prevents regression.** Externalise lessons from failures into a file the agent reads every session, preventing it from repeating known mistakes.[^4]

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

Using this architecture, Anthropic built a complete clone of claude.ai with 200+ features implemented autonomously. The community has replicated similar results — one developer built 61 features for a Rust API server overnight using the Context Engine harness, with zero human intervention after initial setup.[^7][^8][^1]

***

## Alternative Open-Source Tools and Frameworks

### Coding Agent Comparison

| Tool | Type | Cost | Autonomous Mode | Best For |
|------|------|------|----------------|----------|
| **Claude Code** | Terminal agent | $20/mo (Pro) – $200/mo (Max) | `--dangerously-skip-permissions` + harness | Long-running autonomous sessions with sub-agents[^9][^10] |
| **Aider** | Terminal pair programmer | Free (OSS) + API costs | `--message` + `--yes` flags for scripting[^11] | Scripted batch operations, budget-conscious workflows[^12] |
| **OpenHands** | Full autonomous platform | Free (OSS) + API costs | Headless mode (`--headless -t "task"`)[^13][^14] | Self-hosted autonomous execution on VPS[^15] |
| **SWE-Agent** | Issue-to-PR agent | Free (OSS) + API costs | CLI (`sweagent run --issue URL`)[^16] | GitHub issue resolution, benchmarking |
| **Cursor** | IDE with AI | $20–$200/mo | Background agents (limited) | Interactive development, code exploration[^17][^18] |
| **Cline** | VSCode agent | Free (OSS) + API costs | Configurable auto-approve | Editor-native workflows with model flexibility[^19] |

### OpenHands — Best Self-Hosted Option

OpenHands (formerly OpenDevin) is the strongest candidate for VPS-hosted autonomous execution. It provides sandboxed Docker environments, a model-agnostic architecture supporting any LLM, headless mode for scripting, and REST/WebSocket APIs for integration. Installation is straightforward:[^20][^15][^21]

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

Headless mode enables fully autonomous task execution:[^13]

```bash
openhands --headless -t "Implement the authentication module per spec in TASKS.md" \
  -i 50 -b 10.0
```

### Context Engine — Best Autonomous Harness

The Context Engine project provides a four-layer memory architecture specifically designed for overnight autonomous coding:[^8]

| Memory Layer | Purpose | Lifecycle |
|-------------|---------|-----------|
| Working Context | Current task only | Rebuilt each session |
| Episodic Memory | Recent decisions, patterns | Rolling window |
| Semantic Memory | Project knowledge, architecture | Persistent |
| Procedural Memory | What worked, what failed | Append-only |

The autonomous loop operates as: compile context → implement feature → run tests → sub-agent review → commit → exit → repeat. It integrates with Claude Code's hooks system, using `SessionStart` and `PreCompact` hooks to automatically save and restore context across sessions.[^22][^7][^8]

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
2. **Scripted batch execution** (Aider): For well-defined, repetitive tasks like applying the same refactoring across many files, running through a list of fixes, or implementing boilerplate from specs.[^11]
3. **Autonomous sessions** (OpenHands on VPS): For complex, multi-step feature implementation that runs unattended overnight.[^14][^13]

### Alternative Higher-Budget Configuration

If outcomes justify it, upgrading to Claude Max 5x ($100/mo) unlocks the most capable autonomous coding experience with Claude Code's `--dangerously-skip-permissions` mode and sub-agent orchestration. Combined with a VPS ($30/mo), this provides approximately $130/mo total but delivers the most polished autonomous experience currently available.[^9][^10]

***

## Implementation Strategy: Achieving Overnight Autonomous Execution

### Phase 1: Planning Infrastructure (Week 1)

Establish the specification and task-tracking system that agents will consume. This maps directly to AgentFlow's Planner module and Anthropic's Initialiser Agent.[^1]

**Create a standardised project specification format:**

```
project-root/
├── .agents.md              # Agent behaviour rules and project conventions
├── GUARDRAILS.md            # Persistent failure memory — learned safety constraints
├── .openspec/
│   ├── spec.md             # Full project specification
│   └── architecture.md     # Architecture decisions
├── features.json           # Feature list with pass/fail tracking (JSON)
├── progress.md             # Session-by-session progress log
├── init.sh                 # Environment setup script
├── tools/                  # Custom tool library for safe agent operations
│   ├── safe_refactor.sh    # Branch, lint, diff, then commit
│   ├── verify.sh           # Gate script — all checks must pass
│   └── notify.sh           # Webhook/email notification on completion or failure
└── tasks/
    ├── current.md          # Current sprint tasks
    └── completed/          # Archive of completed task specs
```

The additional research emphasises the importance of two new files in this structure:

**GUARDRAILS.md** — persistent failure memory. Unlike `.agents.md` which defines "how to behave," GUARDRAILS.md captures "what not to do" based on actual failures. Each guardrail (called a "Sign") includes a trigger condition, a deterministic instruction, a reason, and provenance (when/how the failure was discovered). This file is read at the start of every agent session and grows over time as new failure patterns emerge:[^4]

```markdown
# GUARDRAILS.md
## Meta
Created: 2026-02-21
Total Signs: 2

## SIGN #1
**Trigger:** Modifying database models
**Instruction:** ALWAYS create a migration file. Never modify the schema directly.
**Reason:** Direct schema changes caused data loss on 2026-02-15
**Provenance:** Overnight run failure, manual intervention required

## SIGN #2
**Trigger:** Adding new API endpoint
**Instruction:** Copy pattern from src/routes/users.ts including error handling, validation middleware, and OpenAPI decorator
**Reason:** Agent created inconsistent error handling without the template pattern
**Provenance:** Code review, 2026-02-18
```

**The `tools/` directory** — a custom tool library. Instead of relying on the agent to perform complex multi-step operations safely, encapsulate risky operations into deterministic scripts that the agent can call. This makes agent behaviour more predictable and prevents entire categories of mistakes:[^4]

```bash
#!/bin/bash
# tools/safe_refactor.sh — Agent calls this instead of directly editing
set -e
git checkout -b refactor/$(date +%s)
# Agent performs changes here
npm run lint --fix
npm run typecheck
git diff --stat
echo "Refactor complete on branch. Ready for merge after review."
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
- **LLM-based verification** (new): In addition to deterministic checks, use a separate LLM call as a code-review verifier. OpenHands supports this pattern natively — the verifier agent uses an LLM to analyse whether the changes actually match the feature specification, catching semantic errors that linters miss.[^23][^24]
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

### Vertical Decomposition — Verify Then Fix

The OpenHands team's work on parallel refactoring revealed a critical pattern for reliable autonomous execution: **vertical task decomposition**. Rather than giving an agent a monolithic task ("refactor all state management"), split each task into two explicit stages:[^24][^23]

1. **Verification stage**: An agent (or script) identifies what needs to change without making changes. It produces a specific list of required modifications.
2. **Fix stage**: A separate agent implements exactly the changes identified in stage 1, then verification runs again.

This two-stage approach directly addresses the pain point of agents skipping broader fixes — the verification stage catches everything first, and the fix stage addresses each item systematically.[^24]

### Phase 3: Autonomous Execution Loop (Week 3)

**Option A: OpenHands V1 SDK two-phase workflow** (recommended):[^2]

The OpenHands V1 SDK now provides a native two-phase planning-then-execution workflow that mirrors AgentFlow's architecture with remarkable precision. The planning agent has **read-only tools** (GlobTool, GrepTool, PlanningFileEditorTool) — it can explore the codebase and write a PLAN.md file but cannot modify any source code. The execution agent then reads PLAN.md and implements it with full editing capabilities. This enforced separation prevents the common failure mode where an agent jumps into implementation before understanding the full scope:[^2]

```python
#!/usr/bin/env python3
# overnight_runner.py — runs on VPS
import json, subprocess, os
from pathlib import Path
from pydantic import SecretStr
from openhands.sdk import LLM, Conversation
from openhands.tools.preset.default import get_default_agent
from openhands.tools.preset.planning import get_planning_agent

# Configure LLM with OpenRouter for model cascading
planner_llm = LLM(
    model="anthropic/claude-sonnet-4-5-20250929",
    base_url="https://openrouter.ai/api/v1",
    api_key=SecretStr(os.getenv("OPENROUTER_API_KEY")),
)
executor_llm = LLM(
    model="anthropic/claude-haiku-4-5-20250929",  # Cheaper for execution
    base_url="https://openrouter.ai/api/v1",
    api_key=SecretStr(os.getenv("OPENROUTER_API_KEY")),
)

def get_next_feature():
    with open("features.json") as f:
        features = json.load(f)
    for feat in sorted(features, key=lambda x: x["priority"]):
        if not feat["passes"]:
            return feat
    return None

def run_feature(feature):
    workspace = Path.cwd()
    guardrails = (workspace / "GUARDRAILS.md").read_text()
    agents_md = (workspace / ".agents.md").read_text()

    # Phase 1: Planning (read-only tools)
    planning_agent = get_planning_agent(llm=planner_llm)
    plan_conv = Conversation(agent=planning_agent, workspace=str(workspace))
    plan_conv.send_message(
        f"Read GUARDRAILS.md first. Then analyse the codebase and create a "
        f"detailed implementation plan for: {feature['description']}\n"
        f"Acceptance criteria: {json.dumps(feature['steps'])}\n"
        f"Project rules: {agents_md}\nGuardrails: {guardrails}"
    )
    plan_conv.run()

    # Phase 2: Execution (full editing tools)
    exec_agent = get_default_agent(llm=executor_llm, cli_mode=True)
    exec_conv = Conversation(agent=exec_agent, workspace=str(workspace))
    exec_conv.send_message(
        f"Read PLAN.md and implement all steps. Run tools/verify.sh after "
        f"each file change. Do NOT proceed if verification fails."
    )
    exec_conv.run()

# Main overnight loop
while (feature := get_next_feature()):
    print(f"Starting: {feature['id']} - {feature['description']}")
    run_feature(feature)
    result = subprocess.run(["./tools/verify.sh"], capture_output=True)
    if result.returncode == 0:
        # Mark complete and commit
        with open("features.json", "r+") as f:
            features = json.load(f)
            for feat in features:
                if feat["id"] == feature["id"]:
                    feat["passes"] = True
            f.seek(0)
            json.dump(features, f, indent=2)
            f.truncate()
        subprocess.run(["git", "add", "-A"])
        subprocess.run(["git", "commit", "-m",
            f"Feature {feature['id']}: {feature['description']} [automated]"])
    else:
        with open("progress.md", "a") as f:
            f.write(f"FAILED: {feature['id']} at {os.popen('date').read()}")
        subprocess.run(["git", "stash"])

print("All features complete or blocked.")
subprocess.run(["./tools/notify.sh", "Overnight run complete"])
```

**Option B: Aider-based scripted loop** (simpler, budget-friendly):[^11]

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

aider --model sonnet --yes --auto-commits \
  --message "Read GUARDRAILS.md first. Then implement feature $FEAT_ID: $FEAT_DESC. 
  Read features.json for acceptance criteria. 
  Run tools/verify.sh after changes. 
  Only mark as passing if all tests pass." \
  src/ tests/ features.json GUARDRAILS.md

if ./tools/verify.sh; then
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

exec "$0"  # Continue to next feature
```

**Option C: Claude Code autonomous harness** (if upgrading to Max):[^10][^7]

```bash
claude --dangerously-skip-permissions \
  --resume overnight-session \
  --max-turns 200 \
  "Read GUARDRAILS.md first. Read features.json. Work through features one 
   at a time, starting with the highest priority incomplete feature. 
   For each feature: implement it, run tools/verify.sh, only mark 
   as passing if all tests pass. Commit after each feature. 
   Update progress.md. Continue to the next feature."
```

### Phase 4: Monitoring and Review (Ongoing)

Set up lightweight monitoring so the morning review is efficient:

- **Git log review**: `git log --oneline --since="12 hours ago"` shows what was accomplished overnight.
- **Progress file diff**: `git diff HEAD~10 progress.md` shows the narrative of what happened.
- **Feature completion dashboard**: A simple script that counts `"passes": true` vs `"passes": false` in `features.json`.
- **Failure alerts** (optional): Use a webhook or email notification if the loop encounters repeated failures.
- **Cost tracking**: Monitor API spend with `--max-budget-usd` flags on OpenHands or Aider's built-in cost tracking.[^14]

### Human-in-the-Loop Gates for Critical Actions

The additional research highlights an important middle ground between full autonomy and constant supervision: **selective human approval gates**. Rather than watching every action, programme the system to pause and notify for specific high-risk operations:[^25][^26]

- **Database migrations**: Always require human approval before running schema changes.
- **Git push to main/production**: Autonomous commits to feature branches are fine; merging requires review.
- **External API calls with side effects**: Billing, email sending, third-party service modifications.
- **Deleting files or directories**: Agent should flag and wait rather than removing.

OpenHands V1 supports this natively through its `SecurityAnalyzer` and `ConfirmationPolicy` system. Each tool call is rated as low, medium, high, or unknown risk. A `ConfirmRisky` policy blocks actions exceeding a configurable risk threshold, and the agent pauses in a `WAITING_FOR_CONFIRMATION` state until explicitly approved. This can be configured to auto-approve in sandboxed environments while requiring confirmation for production-touching actions:[^27][^5]

```python
# OpenHands security configuration
from openhands.sdk.security import ConfirmRisky, LLMSecurityAnalyzer

agent = Agent(
    security_analyzer=LLMSecurityAnalyzer(),
    confirmation_policy=ConfirmRisky(threshold="high"),
    # Low/medium risk: auto-approved
    # High risk: pauses for human confirmation
)
```

This provides the safety net that allows confident overnight execution — the agent handles 95% of actions autonomously, pausing only for the genuinely dangerous 5%.[^26]

***

## Strategies for Improving Agent Reliability

### Context Engineering Best Practices

The single most impactful skill for reducing agent intervention is context engineering — ensuring the agent has exactly the right information at the right time.[^28]

- **Ground in code, not abstractions.** Instead of "add rate limiting middleware," prompt "search for existing middleware patterns in src/middleware/, check our Redis configuration in config/, then propose rate limiting that follows the same error handling and export structure".[^29]
- **Use `.agents.md` as a living document.** Include project-specific patterns, naming conventions, architectural decisions, and explicit do/don't rules. Keep it concise — under 2,000 tokens — to avoid consuming too much context window.[^30]
- **Provide examples of desired output.** Show the agent a completed feature file as a template for new features. Concrete examples consistently outperform abstract instructions.[^29]
- **Pre-load context deliberately.** Use "explain how X works" prompts to force the agent to read and load relevant code into its context window before making changes.[^29]
- **Separate `.agents.md` from `GUARDRAILS.md`.** The former defines positive behaviour ("how to behave"); the latter captures negative constraints learned from failures ("what not to do"). Both are read at session start, but they serve different cognitive functions for the agent.[^31][^4]

### The Tool Library Pattern

The additional research emphasises building a library of **custom bash scripts or Python tools** that encapsulate risky multi-step operations into safe, deterministic commands. This fundamentally changes the agent's action space — instead of improvising complex operations, it calls a tested script:[^4]

| Custom Tool | What It Encapsulates | Why It's Safer |
|------------|---------------------|---------------|
| `tools/safe_refactor.sh` | Branch → edit → lint → typecheck → diff | Prevents dirty commits to main branch |
| `tools/add_endpoint.sh` | Copy route template → scaffold → register in router | Enforces consistent patterns |
| `tools/run_migration.sh` | Create migration file → validate → apply to dev DB only | Prevents direct schema modification |
| `tools/verify.sh` | Lint + typecheck + unit + integration tests | Single gate script with clear pass/fail |
| `tools/notify.sh` | Send webhook/email with status summary | Async notification for morning review |

This pattern directly mirrors AgentFlow's Dynamic Tool Integration — the system loads and uses diverse tools as needed, but each tool is a well-tested, deterministic operation rather than an open-ended LLM action.

### Structural Safeguards

- **Git as safety net.** Every change should be committed incrementally. If something goes wrong, `git reset --hard HEAD~1` recovers instantly.[^10][^1]
- **Turn budgets.** Set maximum iterations (`--max-turns`, `-i 50`) to prevent infinite loops.[^10][^14]
- **Cost caps.** Use `--max-budget-usd` to prevent runaway API spending during autonomous sessions.[^14][^10]
- **Sandboxed execution.** Run autonomous agents inside Docker containers or on a VPS, never directly on a machine with production data or credentials. OpenHands provides Docker sandboxing by default with dedicated file systems and resource isolation.[^5][^10]
- **Feature isolation.** Each feature should be implementable independently. Avoid tasks that require coordinated changes across multiple subsystems in a single agent session.[^1]
- **Scaffolding patterns for large changes.** For major refactors, create a temporary scaffolding layer that allows old and new code to coexist, then rip out the scaffolding after all changes are verified. This prevents the "big bang" failure mode where a half-completed refactor breaks everything.[^24]

### Reducing Common Failure Modes

| Failure Mode | Prevention Strategy |
|-------------|-------------------|
| Agent declares task complete prematurely | Require automated test passage before marking complete; use JSON feature tracking[^1] |
| Agent gets stuck in error loops ("The Gutter") | GUARDRAILS.md with learned failure patterns; turn budgets; git stash and skip on repeated failures[^4] |
| Context degradation over long sessions | Session-based architecture with fresh context per task; OpenHands event-sourced state with condensation[^7][^5] |
| Agent modifies the wrong files | Read-only planning agent phase identifies files first; explicit file scoping in prompts[^28][^2] |
| Agent skips broader fixes for current task | Vertical decomposition: verify stage identifies all needed changes before fix stage begins[^23][^24] |
| Hallucinated API calls or non-existent functions | Planning agent's GlobTool and GrepTool verify what exists before execution agent writes code[^2] |
| Runaway API costs overnight | Model cascading via OpenRouter; `--max-budget-usd` caps; cheap models for routine tasks[^32][^6] |
| Catastrophic action (drop table, push to prod) | OpenHands SecurityAnalyzer with HITL gates for high-risk actions[^27][^26] |

### The Plan-and-Review Mindset Shift

The shift from watching an agent to reviewing its output requires a fundamental change in how work is structured:[^30]

- **Planning becomes the primary skill.** The quality of the specification directly determines the quality of autonomous output. Invest 30–60 minutes writing a detailed spec for every 4–8 hours of autonomous execution.
- **Decomposition is essential.** Break every project into features that can be independently implemented, tested, and verified. If a feature cannot be tested in isolation, it is too large.
- **Review replaces monitoring.** Instead of watching the agent think, review git diffs, test results, and progress logs the next morning. This is faster and more effective than real-time supervision.
- **Iteration replaces perfection.** Accept that autonomous output will sometimes be 80% correct. Quick manual fixes on a mostly-complete implementation are still dramatically faster than building from scratch.
- **Failure analysis is the highest-ROI activity.** The most valuable data from overnight runs is when things go wrong. Spend review time analysing failure logs to understand why verification failed — then add a new Sign to GUARDRAILS.md. Each failure that gets captured permanently improves all future runs.[^4]

***

## Recommended Implementation Roadmap

### Immediate Actions (This Week)

1. Set up a VPS (4-core, 8GB RAM, ~$25–30/mo from Hetzner, Contabo, or DigitalOcean).
2. Install Docker, OpenHands V1 SDK, Redis, and Aider on the VPS.
3. Create an OpenRouter account and add $10–20 credit. Configure API key for model cascade routing.[^32]
4. Create the project specification structure (`features.json`, `progress.md`, `init.sh`, `.agents.md`, `GUARDRAILS.md`, `tools/` directory).
5. Write `tools/verify.sh` for the current project with all automated checks.
6. Seed `GUARDRAILS.md` with known failure patterns from past agent sessions.

### Short-Term (Weeks 2–3)

7. Implement the OpenHands V1 two-phase workflow script (planning agent → execution agent) for a single feature. Run it supervised to calibrate.[^2]
8. Run the first extended autonomous session — start the loop, check in after 1 hour, then 2 hours, extending gradually.
9. After each session, review failures and add new Signs to `GUARDRAILS.md`.[^4]
10. Build 3–5 custom tools in the `tools/` directory for the most common risky operations in the project.
11. Configure OpenHands security policies — auto-approve low-risk actions, gate high-risk actions.[^27]
12. Establish a morning review routine: git log → progress diff → feature completion count → GUARDRAILS.md update → targeted code review.

### Medium-Term (Month 2+)

13. Develop reusable specification templates for common feature types.
14. Build a library of context engineering prompts that reliably produce good autonomous output.
15. Experiment with parallel agents for large refactors — OpenHands supports batching files into independent groups and dispatching concurrent agents. Start with 3–5 concurrent agents.[^23][^24]
16. Implement Redis-backed task queue for more sophisticated job management: priority queuing, dead letter queues for failed tasks, and state persistence that survives process restarts.[^33][^34]
17. Tune the model cascade: analyse which tasks succeed with cheap models and which genuinely need escalation. The cost savings compound over time.[^3][^35]
18. Consider upgrading to Claude Max if autonomous session quality and throughput justify the cost.[^9]

This phased approach transforms the current watch-and-guide workflow into a structured plan-and-review process. The key additions from the supplementary research — GUARDRAILS.md for persistent failure memory, model cascading for cost control, two-phase planning architecture, HITL gates for critical actions, and a custom tool library — each address specific failure modes that would otherwise require human intervention. Together, they create a system that genuinely improves with every overnight run, making autonomous execution progressively more reliable over time.

---
## Q & A
Short answers:

1. Yes—MCP Agent Mail is designed for **real cross‑agent communication plus coordination**, not just file locks.mcpagentmail+3
    
2. Yes—**n8n can still be useful**, but now more as an outer workflow/automation layer around the Flywheel stack (NTM + Agent Mail + CASS/CM), not as the core coordinator.leanware+1
    

Below are the details.

---

## 1. What Agent Mail Actually Provides

## 1.1 Cross‑Agent Communication Capabilities

From the MCP Agent Mail description and skill docs:glama+3

- Each agent gets a **named identity** and an inbox/outbox.
    
- Messages are:
    
    - Git-backed markdown (human‑auditable) + SQLite indexed (fast search).
        
    - Threaded, searchable, and can be summarized.
        
- It is explicitly pitched as “like Gmail for your coding agents” so **multiple agents and tools can communicate and coordinate** across projects.linkedin+1
    
- It supports:
    
    - Sending detailed markdown messages between agents.
        
    - Starting new threads or replying to existing ones.
        
    - Human overseer messages into those same threads.
        

So yes, in practice:

- Agents can send each other:
    
    - “I’m stuck on bead B‑123 because tests `X`/`Y` keep failing with error Z.”
        
    - “I’ve reserved `src/auth/**` and plan to refactor sessions; please avoid these files until I release the lease.”
        
    - “I finished the backend change; frontend agent, please implement the UI according to this contract.”
        

Whether they **actually do** this in a “smart” way depends on:

- How you prompt/configure them (the AGENTS.md blurb).
    
- How much you rely on those mailboxes in your workflows.
    

But the plumbing is there for meaningful communication, not just a thin lock file.

## 1.2 File Reservations and Pausing/Handoffs

Agent Mail’s file reservation system:pulsemcp+2

- Provides **advisory leases** on files/globs:
    
    - Exclusive/shared modes.
        
    - Stored in SQLite + Git (auditable).
        
- Integrates with Flywheel tools (NTM, BV, CASS, CM) via skill hooks.​
    

This enables behaviors like:

- Agent A claims `/backend/auth/**` while working a bead.
    
- Agent B:
    
    - Sees the lease and either:
        
        - Waits, or
            
        - Works on a different bead not touching those paths.
            
- When Agent A is stuck:
    
    - It can:
        
        - Send a mail to another agent: “I’m blocked; please take over this bead.”
            
        - Release the lease (or set a shorter expiry), allowing another agent to pick it up.
            

There isn’t a built‑in “scheduler” in Agent Mail that automatically reassigns beads, but:

- **NTM + BV + CASS/CM + Agent Mail** together give you:
    
    - Messaging and intent signaling (Agent Mail).glama+1
        
    - Task graph and prioritization (Beads/BV).​
        
    - Session search and memory (CASS/CM).[​
        
    - tmux‑level orchestration (NTM robot mode).skills+1
        

If you configure your agents with the provided AGENTS.md snippet (Jeff says this explicitly in his post), they **do** start leaving notes for each other and coordinating handoffs in a natural way.​

So to your question:

> If one was stuck could it pause the bead for another model or leave some sort of note?

- **Leave a note / context for another agent:** Yes—via a thread and/or bead‑linked mail thread, this is exactly the intended use.pulsemcp+2
    
- **Pause/hand off in a structured way:** There’s support to:
    
    - Write that state into the thread or bead metadata.
        
    - Use leases to relinquish file control.
        
    - Have another agent pick it up based on those signals.
        
- The “automatic reassignment” logic (e.g., “if stuck for 30 minutes, hand this bead to a different model”) is something you still glue together via NTM scripts or a workflow engine—but Agent Mail provides the **shared memory and coordination channel** that make that handoff meaningful.
    

---

## 2. Is n8n Still Useful with CASS + CM + Agent Mail?

## 2.1 What n8n Adds That Flywheel Doesn’t Try to Own

The Flywheel stack focuses on **coding‑centric coordination**: tmux sessions, file leases, task graphs, session search.​

n8n focuses on **workflow integration**: connecting your agents to the rest of your world (GitHub, Slack, calendar, issue trackers, etc.) and scheduling/monitoring them.n8n+1

With CASS + CM + Agent Mail + NTM in place, n8n is no longer your _core_ multi-agent orchestrator, but it can still be valuable in three areas:

1. **Scheduling & Triggers**
    
    - Cron‑like triggers for “nightly agent run.”
        
    - Event triggers:
        
        - When a GitHub issue with label `bead:ready` appears, spawn an NTM profile for that project.
            
        - When a specific bead moves to `ready` in BV (exposed via some script/API), run a job.
            
2. **External Integrations**
    
    - When agents finish work:
        
        - Automatically open GitHub PRs.
            
        - Post summaries to Slack/Discord.
            
        - Update your project management tool.
            
    - When Agent Mail threads change:
        
        - n8n can read them via an MCP node or a simple HTTP API and:
            
            - Route “stuck” events to you.
                
            - Log them into an external incident/tracking system.​
                
3. **Supervision and Observability**
    
    - Central dashboards of:
        
        - Which agents ran overnight.
            
        - Which beads got completed.
            
        - Simple metrics (fail/success counts).
            
    - Alerting:
        
        - If a certain pattern appears in Agent Mail (e.g., repeated “I’m stuck” messages).
            
        - If no commits/PRs were created during an expected window.
            

## 2.2 How It Fits the Updated Plan

So, answering your specific question:

> Would this section regarding n8n still be useful even in the updated version of our plan using cass + cm + agentmail?

- **Yes, but with a narrower focus.**  
    n8n is still useful as:
    
    - A **scheduler** to kick off NTM profiles / agent squads at certain times.
        
    - A **bridge** between the Flywheel world (Agent Mail, Beads, NTM) and:
        
        - GitHub, Slack, Linear/Jira, monitoring, etc.n8n+1
            
- What changes compared to earlier drafts:
    
    - The _inner loop_ (which bead to work on, coordinating file access, agent‑to‑agent messaging) should now lean on **BV + Agent Mail + NTM** rather than n8n.
        
    - n8n becomes the **outer shell**:
        
        - “At 11pm, start the overnight squad for Project X.”
            
        - “When a PR is ready and tests pass, post a summary to Slack and assign to Josh.”
            

If you prefer to keep things lean at first, you can:

- Start **without n8n**:
    
    - Use ACFS, Agent Mail, NTM, Beads, CASS/CM for the core coding loop.
        
    - Trigger runs manually (or with simple cron scripts).
        
- Add n8n later when:
    
    - You want richer automation around GitHub/Slack/issue trackers.
        
    - You want a visual view of the whole process or more complex triggering conditions.
        

---

## Practical Takeaways for You

- **Agent Mail:**  
    You can absolutely rely on it for real cross‑agent collaboration and “leaving notes”/handoffs, as long as your AGENTS.md prompts tell agents to use it that way.glama+2
    
- **n8n:**  
    Still worth keeping in the toolbox, but repositioned as:
    
    - “External workflow orchestrator and scheduler”  
        not
        
    - “Primary internal agent coordinator” (that’s now NTM + Agent Mail + BV/CASS/CM).
        

If you’d like, next step could be to sketch:

- A concrete “stuck bead” flow:
    
    - How an agent uses Agent Mail to mark a bead as blocked and suggest a handoff.
        
    - How NTM/Oh My OpenCode might act on that.
        
    - How n8n could notify you or escalate only when needed.
## References

1. [How to Build AI Agents That Work While You Sleep](https://www.linkedin.com/pulse/how-build-ai-agents-work-while-you-sleep-anthropics-coding-avramenko-9kwdc) - Anthropic's engineering team recently published their breakthrough approach to building a complete c...

2. [Creating Custom Agent - OpenHands Docs](https://docs.openhands.dev/sdk/guides/agent-custom) - Learn how to design specialized agents with custom tool sets

3. [Your AI Agent Bill Is 30x Higher Than It Needs to Be: The Cost Optimization Playbook](https://micheallanham.substack.com/p/your-ai-agent-bill-is-30x-higher) - Slash Your AI Agent Bill by 30x

4. [Safety Protocol for Autonomous Agents](https://guardrails.md) - GUARDRAILS.md: Persistent safety constraints that prevent catastrophic failures in AI coding agents.

5. [[Literature Review] The OpenHands Software Agent SDK](https://www.themoonlight.io/en/review/the-openhands-software-agent-sdk-a-composable-and-extensible-foundation-for-production-agents) - The OpenHands Software Agent SDK provides a composable and extensible foundation for building produc...

6. [lemony-ai/cascadeflow: Smart AI model cascading for cost ...](https://github.com/lemony-ai/cascadeflow) - Benefit. Speculative Cascading, Tries cheap models first, escalates intelligently. 40-85% Cost Savin...

7. [I built an autonomous harness for Claude Code that ...](https://www.reddit.com/r/ClaudeAI/comments/1pk230x/i_built_an_autonomous_harness_for_claude_code/) - I made a harness for long-running Claude Code sessions with GitHub integration ... I built 18 autono...

8. [zeddy89/Context-Engine](https://github.com/zeddy89/Context-Engine) - Autonomous project builder for Claude Code that doesn't forget what it's doing. Built 61 features fo...

9. [Claude Code Pricing](https://www.claudelog.com/claude-code-pricing/) - Claude AI price breakdown: Pro from $17/month vs Max from $100/month plans, API costs, usage limits....

10. [Claude Code Autonomous Mode: Complete Guide to](https://pasqualepillitteri.it/en/news/141/claude-code-dangerously-skip-permissions-guide-autonomous-mode) - Complete guide to --dangerously-skip-permissions and Claude Code permission modes. Learn how to conf...

11. [Scripting aider | Synthetic Souls](https://synthetic-souls.nlr.ai/venv/lib/python3.12/site-packages/aider/website/docs/scripting) - You can script aider via the command line or python.

12. [GitHub - Aider-AI/aider: aider is AI pair programming in your terminal](https://github.com/Aider-AI/aider) - aider is AI pair programming in your terminal. Contribute to Aider-AI/aider development by creating ...

13. [Headless Mode](https://docs.openhands.dev/openhands/usage/cli/headless) - Run OpenHands without UI for scripting, automation, and CI/CD pipelines

14. [Headless - OpenHands Docs](https://docs.openhands.dev/openhands/usage/run-openhands/headless-mode) - You can run OpenHands with a single command, without starting the web application. This makes it eas...

15. [Setup - OpenHands Docs](https://docs.openhands.dev/openhands/usage/run-openhands/local-setup) - Getting started with running OpenHands on your own.

16. [OpenHands vs SWE-Agent: Best AI Coding Agent 2026](https://localaimaster.com/blog/openhands-vs-swe-agent) - Complete comparison of OpenHands and SWE-Agent. SWE-bench benchmarks, architecture, setup guides.

17. [Claude Code vs Cursor: What to Choose in 2026](https://www.builder.io/blog/cursor-vs-claude-code) - Claude Code vs Cursor compared across features, pricing, and background agents. Based on daily use o...

18. [Claude Code vs Cursor 2026: Features, Pricing & Real ...](https://spectrumailab.com/blog/claude-code-vs-cursor) - Terminal-based Claude Code vs full IDE Cursor compared by developers who use both daily. Pricing and...

19. [Top 11 Open-Source Autonomous Agents & Frameworks in 2025](https://cline.bot/blog/top-11-open-source-autonomous-agents-frameworks-in-2025)

20. [[2511.03690] The OpenHands Software Agent SDK: A Composable ...](https://arxiv.org/abs/2511.03690) - Agents are now used widely in the process of software development, but building production-ready sof...

21. [OpenHands - AI Code Editor Tool | Detailed Review & Features](https://www.aicodeide.org/ai-code-editor/openhands) - AI-Powered Autonomous Development: OpenHands agents can autonomously modify code, run commands, brow...

22. [Claude Code Session Hooks: Auto-Load Context Every Time](https://claudefa.st/blog/tools/hooks/session-lifecycle-hooks) - Claude Fast | SessionStart, SessionEnd, Setup, and PreCompact hooks for Claude Code. Auto-load conte...

23. [Automating Massive Refactors with OpenHands Agents Working in Parallel](https://www.youtube.com/watch?v=MKrPPa6lE0s) - Learn how elite engineering teams use OpenHands to automate large refactors with many agents working...

24. [Automating Large Scale Refactors with Parallel Agents - Robert Brennan, OpenHands](https://www.youtube.com/watch?v=rcsliSIy_YU) - Today's agents are best at small, atomic coding tasks. Much larger tasks--like major refactors and b...

25. [Human-in-the-Loop for AI Agents: Best Practices ...](https://www.permit.io/blog/human-in-the-loop-for-ai-agents-best-practices-frameworks-use-cases-and-demo) - Learn how to safely integrate AI agents with human-in-the-loop (HITL) workflows. Explore best practi...

26. [Human-in-the-Loop for AI Agents](https://inference.sh/human-in-the-loop) - Add approval gates to AI agent actions with one flag. Agents pause, show what they want to do, and w...

27. [The OpenHands Software Agent SDK: A Composable and ...](https://arxiv.org/html/2511.03690v1) - The SDK defines an event-sourced state model with deterministic replay, an immutable configuration f...

28. [How to build reliable AI workflows with agentic primitives ...](https://github.blog/ai-and-ml/github-copilot/how-to-build-reliable-ai-workflows-with-agentic-primitives-and-context-engineering/) - Agentic workflows in Markdown apply prompt and context engineering that leverages agent primitives t...

29. [Planning & Execution - Master Agentic Coding](https://agenticoding.ai/docs/practical-techniques/lesson-7-planning-execution) - Lesson 5: Grounding covered how RAG and semantic search enable agents to retrieve context from your ...

30. [Refactoring & Code Quality...](https://www.digitalapplied.com/blog/practical-agentic-engineering-workflow-2025) - Master production agentic engineering: blast radius frameworks, GPT-5 Codex vs Claude, parallel agen...

31. [Guardrails.md - Safety Protocol for Autonomous Agents](http://guardrails.md) - GUARDRAILS.md: Persistent safety constraints that prevent catastrophic failures in AI coding agents.

32. [OpenRouter Pricing Calculator & Cost Guide (Feb 2026)](https://costgoat.com/pricing/openrouter) - Start with the cheapest model that might work, then escalate to more expensive ones only when needed...

33. [Top AI Agent Orchestration Platforms in 2026](https://redis.io/blog/ai-agent-orchestration-platforms/) - AWS Bedrock Agents is a fully managed service supporting autonomous AI agents with sophisticated orc...

34. [AI agent orchestration for production systems](https://redis.io/blog/ai-agent-orchestration/) - Production agent frameworks provide durable execution, state management, and human-in-the-loop capab...

35. [Cost-Aware Model Selection (CAMS) - Agentic Design | Agentic ...](https://agentic-design.ai/patterns/resource-aware-optimization/cost-aware-model-selection) - Intelligently selects AI models based on cost-performance trade-offs for specific tasks

---

## Official / 2026 links

- [agentflow.stanford.edu](https://agentflow.stanford.edu/) · [arXiv 2510.05592](https://arxiv.org/html/2510.05592)
- [`research_overnight_stack_web/findings_orchestration_deer_agentflow_gas.md`](research_overnight_stack_web/findings_orchestration_deer_agentflow_gas.md)
