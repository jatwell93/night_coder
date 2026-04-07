#gas-town 
# From Gas Town to Budget Autonomy: Building a Plan-and-Review Agentic Coding Workflow on $60/Month

## Executive Summary

Gas Town, Steve Yegge's open-source multi-agent orchestration framework, represents the current state of the art in coordinating 20–30 parallel AI coding agents with persistent state, crash recovery, and autonomous workflow execution. However, its operational cost—requiring multiple Claude Code Max subscriptions totalling $400–$600+/month—puts it beyond the reach of solo developers. This report analyses Gas Town's core architectural patterns and maps them onto a practical, budget-constrained stack that achieves the same fundamental goal: shifting from an active-monitoring workflow to a plan-and-review workflow where agents execute autonomously overnight with minimal supervision.[1][2][3]

The recommended architecture combines Claude Code Pro ($20/month), GitHub Copilot Pro ($10/month), and approximately $20–30/month in API credits or tool upgrades, staying within a $60/month ceiling. By leveraging Anthropic's long-running agent harness patterns, GitHub Copilot's background coding agent, Claude Code's native subagents and hooks, and open-source tools like Claude Autopilot and the Overnight Development skill, a solo developer can replicate the most valuable Gas Town patterns—persistent work state, autonomous execution, work decomposition, crash recovery, and quality gating—without the factory-scale costs.

***

## Gas Town Architecture: What Matters Most

### Core Architectural Concepts

Gas Town is built in Go (~189,000 lines of code) on top of Beads, a Git-backed issue tracking system. Its architecture centres on a hierarchical agent system where the human operates as an "Overseer" managing a factory of AI workers. The key abstraction layers are:[2][1]

| Component     | Function                                                                  | Budget Equivalent                                                    |
| ------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| **Beads**     | Git-backed JSONL issue tracking; atomic work units                        | `todo.md` / `feature_list.json` tracked in Git                       |
| **Molecules** | Chained task sequences with acceptance criteria                           | OpenSpec change proposals with task breakdowns                       |
| **Formulas**  | Reusable TOML workflow templates                                          | Claude Code Skills and subagent definitions                          |
| **Hooks**     | Git worktree persistent storage per agent                                 | Native Claude Code hooks + Git worktrees                             |
| **GUPP**      | "If there is work on your hook, you MUST run it" – scheduling persistence | Claude Autopilot queue + progress file checks [[ralph-orchestrator]] |
| **Mayor**     | AI coordinator dispatching tasks                                          | Primary Claude Code session or orchestrator prompt                   |
| **Polecats**  | Ephemeral worker agents                                                   | Claude Code subagents / GitHub Copilot coding agent                  |
| **Witness**   | Supervisor detecting stuck agents                                         | CI checks + morning review workflow                                  |

The most architecturally significant insight from Gas Town is **Nondeterministic Idempotence**: workflows achieve durability not through deterministic replay (like Temporal) but through persistent workflow definitions with explicit acceptance criteria stored in Git. If an agent crashes mid-step, the next session picks up where it left off because the work definition and acceptance criteria are immutable. The path is nondeterministic—agents might take different approaches—but the outcome converges.[2]

### What Gas Town Costs and Why

Yegge ran approximately 40 Claude Code Max accounts simultaneously, with costs reaching thousands per month. He explicitly warns: "You won't like Gas Town if you ever have to think, even for a moment, about where money comes from". The system is designed for Stage 7–8 developers already running 10+ parallel agents. For a solo developer at Stage 5–6, the relevant question is not "how do I run Gas Town?" but rather "which Gas Town patterns can I adopt at my scale?"[3][1]

### The Five Gas Town Patterns Worth Replicating

1. **Persistent work state**: All progress stored in files and Git, never reliant on agent memory or context windows[4]
2. **Work decomposition**: Large tasks broken into small, **independently verifiable units** with explicit acceptance criteria[1]
3. **Crash recovery**: Any agent session can resume work from file-based state without human re-explanation[5]
4. **Autonomous execution loops**: Agents cycle through work queues without human intervention[1]
5. **Quality gating**: Automated tests, linters, and review gates prevent bad code from progressing[2]

***

## The Anthropic Long-Running Agent Harness

Anthropic's engineering team published the most directly applicable pattern for autonomous overnight execution: a two-agent harness that enables Claude to work effectively across many context windows.[6]

### How It Works

The core challenge is that each new agent session begins with no memory of prior sessions. Anthropic's solution decomposes this into two parts:[6]

1. **Initializer Agent**: Runs once to set up the environment—a `feature_list.json` with 200+ granular features (each marked as passing/failing), an `init.sh` script, a `claude-progress.txt` file, and an initial Git commit.[6]

2. **Coding Agent**: Every subsequent session reads the progress file and Git history, chooses the highest-priority incomplete feature, implements it incrementally, tests it end-to-end, commits with descriptive messages, and updates the progress file.[6]

### Key Design Decisions

The feature list uses JSON rather than Markdown because models are less likely to inappropriately modify structured JSON files. The coding agent is explicitly instructed to work on only one feature at a time—this incremental approach proved critical to avoiding the model's tendency to attempt too much at once.[6]

A typical session flow looks like:[6]

```
1. Read claude-progress.txt and feature_list.json
2. Check git log for recent work
3. Run init.sh to start development server
4. Test basic functionality (catch broken state)
5. Choose next failing feature
6. Implement and test end-to-end
7. Commit with descriptive message
8. Update progress file
```

The harness is open-sourced at `github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding`.[7]

| Failure Mode | Harness Solution |
|-------------|-----------------|
| Agent declares victory too early | Feature list with explicit pass/fail status in JSON[6] |
| Environment left in broken state | Git commits + progress notes; session starts by testing basics[6] |
| Features marked done prematurely | End-to-end testing with browser automation (Puppeteer MCP)[6] |
| Agent wastes time figuring out environment | `init.sh` script written by initializer[6] |

***

## Proposed Budget Architecture

### Tool Stack and Costs

| Tool | Monthly Cost | Role | Key Capability |
|------|-------------|------|----------------|
| **Claude Code Pro** | $20 | Primary coding agent | Subagents, hooks, background tasks, 40–80 hrs/week Sonnet[8][9] |
| **GitHub Copilot Pro** | $10 | Background autonomous agent + autocomplete | Coding agent creates PRs in GitHub Actions[10][11] |
| **Claude API credits** | $15–20 | GitHub Actions integration + overflow | Claude Code GitHub Actions for CI/CD automation[12] |
| **Open-source tools** | $0 | Orchestration layer | Claude Autopilot, Overnight Dev skill, Roo Code, Aider |
| **Total** | **$45–50** | | Under $60 budget |

**Alternative configuration** (if Cursor is preferred over GitHub Copilot):

| Tool | Monthly Cost | Role |
|------|-------------|------|
| **Claude Code Pro** | $20 | Primary coding agent |
| **Cursor Pro** | $20 | IDE + background agents (usage-based extra) |
| **API credits** | $10–20 | Overflow and automation |
| **Total** | **$50–60** | |

Note: Cursor's background agents bill separately from the subscription at API rates and require MAX mode with a 20% surcharge. This makes the Cursor path less predictable for budget management. GitHub Copilot's coding agent, by contrast, is included in the base subscription and runs on GitHub Actions minutes.[10][13][14]

### Claude Code Pro: Maximising $20/Month

The Pro plan provides approximately 40–80 hours per week of Claude Sonnet 4.5 usage in the terminal, resetting on 5-hour cycles. Key strategies to maximise this allocation:[8][9]

- **Automate the first prompt of the day** at 5am via cron so that by 8am the timer has already reset once, giving a full speed window in the morning[15]
- **Use `/clear` aggressively** and maintain state in files (todo.md, progress.txt) rather than relying on conversation context, which consumes tokens faster[16][15]
- **Keep CLAUDE.md under 150 lines** as a routing file pointing to `.claude/rules/*.md` for detailed context—long CLAUDE.md files cause the model to ignore rules buried in noise[17][18][16]
- **Use background subagents** for parallel work: Claude Code natively supports foreground (blocking) and background (concurrent) subagents with worktree isolation[19][20]
- **Configure hooks** to automatically run tests after code changes and lint before commits, removing the need for manual quality checks[21][17]

### GitHub Copilot Coding Agent: Free Background Execution

The single most impactful tool for achieving overnight autonomy at low cost is GitHub Copilot's coding agent, included with all paid Copilot plans. This agent:[13][22]

- Runs autonomously in an isolated GitHub Actions environment—no local machine needed[10]
- Works even when VS Code is closed[10]
- Creates a pull request with all changes, then requests review[23][10]
- Can explore codebases, make multi-file changes, run builds, tests, and linters[10]
- Responds to PR comments tagged with `@copilot` for iteration[10]

**Workflow**: Write detailed GitHub issues describing each task with acceptance criteria → assign to `@copilot` → agent works in background → review PRs in the morning. This directly mirrors Gas Town's Polecat pattern where worker agents receive beads (issues) and execute them autonomously.[13][23][1]

***

## Implementation Strategy: The Overnight Execution Pipeline

### Phase 1: Planning and Decomposition (30–60 minutes, evening)

This phase replaces the current watch-and-guide pattern with structured delegation. The existing OpenSpec workflow is well-suited here:[24][25]

1. **Create the specification** using OpenSpec's `/opsx:draft` command to generate a change proposal with motivation, scope, and expected impact[25][24]
2. **Generate the technical plan** with `/opsx:plan`, producing implementation details respecting architecture constraints[24]
3. **Break into atomic tasks** with `/opsx:tasks`, creating a task list where each task has clear acceptance criteria[26][24]
4. **Convert tasks to GitHub issues** with detailed descriptions, file references, and test expectations

The Anthropic harness pattern adds a critical refinement: maintain a `feature_list.json` file with structured pass/fail tracking for each feature, rather than relying on markdown task lists. This prevents agents from accidentally modifying or deleting requirements.[6]

### Phase 2: Delegation and Queue Setup (15–30 minutes)

Distribute work across the available autonomous execution channels:

**Channel 1: GitHub Copilot Coding Agent**
- Assign well-scoped issues to `@copilot`—ideal for feature implementation, bug fixes, test coverage, and documentation[23][10]
- Write issues with the same specificity as Gas Town's bead descriptions: clear scope, file locations, expected behaviour, and test commands

**Channel 2: Claude Code with Autopilot Extension**
- Install Claude Autopilot for VS Code, which enables task queuing and batch processing with auto-resume when usage limits reset[27]
- Queue tasks that require deeper codebase understanding or architectural decisions
- The extension includes sleep prevention (keeps computer awake), health monitoring, and error recovery[27]

**Channel 3: Claude Code Overnight Development Skill**
- Install the overnight-dev skill which enforces TDD via Git hooks: pre-commit hooks run tests and linting, blocking commits until all checks pass[28][29]
- The agent cycles through test-debug loops autonomously, resulting in a clean commit history by morning[29]
- Setup: `/overnight-setup` configures hooks, then define the task with clear success criteria[29]

### Phase 3: Autonomous Execution (Overnight, 6–10 hours)

During execution, the following mechanisms keep agents productive without supervision:

**State Persistence** (Gas Town's Beads pattern):
- All state lives in files: `claude-progress.txt`, `feature_list.json`, `todo.md`[30][6]
- Every meaningful change gets a Git commit with a descriptive message[6]
- If any session crashes, the next session reads files and Git history to resume[4][6]

**Quality Gating** (Gas Town's Witness pattern):
- Git pre-commit hooks enforce tests passing before any commit lands[31][29]
- CI pipelines run on each push, catching integration issues[12]
- Claude Code hooks auto-run linters and test suites on file changes[21][17]

**Crash Recovery** (Gas Town's GUPP pattern):
- Claude Autopilot auto-resumes processing when Claude usage limits reset[27]
- File-based state survives `/clear`, crashes, and session restarts[30]
- The Anthropic harness pattern ensures each new session starts by checking environment health before doing new work[6]

### Phase 4: Morning Review (30–60 minutes)

This is where the workflow fundamentally differs from active monitoring. Upon return:

1. **Review GitHub PRs** created by Copilot's coding agent—check diffs, test results, and implementation quality[10]
2. **Check `claude-progress.txt`** and Git log for Claude Code overnight work[6]
3. **Run the validation prompt** from the Reddit overnight workflow pattern: activate a validation prompt within the same session to get a structured report of what was accomplished versus the original requirements[30]
4. **Update `feature_list.json`** to reflect verified completions and identify remaining work
5. **Iterate via PR comments** for Copilot agent (`@copilot please fix X`) or queue new tasks for the next overnight session[10]

***

## Improving Agent Reliability for Unsupervised Execution

### Context Engineering for Autonomous Agents

The single most important factor in agent reliability is context quality. For unsupervised execution, context must be self-contained in files rather than relying on conversation history:[32][30]

**CLAUDE.md Architecture** (keep under 150 lines):[16][17]

```markdown
# Project: [Name]
## Tech Stack
- [framework, language, database, etc.]
## Commands
- Test: `npm test -- --coverage`
- Lint: `npm run lint`
- Build: `npm run build`
## Architecture
- [2-3 sentences on structure]
## Rules
- See .claude/rules/frontend.md for UI conventions
- See .claude/rules/api.md for API patterns
- See .claude/rules/testing.md for test requirements
## Current State
- See claude-progress.txt for session continuity
- See feature_list.json for remaining work
```

**Modular Rules Architecture**: Split task-specific context into `.claude/rules/*.md` files loaded only when relevant, preventing context window pollution.[33][18]

**Subagent Configuration**: Define custom subagents in `.claude/agents/` with specific descriptions, tool restrictions, and skills. Use `background: true` for long-running tasks and `isolation: worktree` to prevent file conflicts between parallel agents.[19]

### Test-Driven Development as the Primary Guardrail

TDD is the most effective mechanism for unsupervised agent quality control because it creates a machine-verifiable feedback loop:[31][29]

- **Write tests first** in the planning phase, defining expected behaviour before agents implement
- **Install tdd-guard or equivalent hooks** that block commits unless tests pass[34][31]
- **Configure coverage thresholds** (aim for >80% on new code)[16]
- **Use Puppeteer MCP** for end-to-end browser testing of web applications—Anthropic found this dramatically improved feature completion quality[6]

### Git Worktree Isolation for Parallel Agents

When running multiple Claude Code sessions, Git worktrees prevent agents from overwriting each other's changes:[35][36]

1. Create isolated worktrees: `git worktree add ../feature-branch-1 -b feature-1`
2. Symlink shared secrets (`.env`, credentials) into each worktree[35]
3. Isolate databases per worktree using environment variables[35]
4. Run each Claude Code instance in its own worktree directory

This mirrors Gas Town's core isolation mechanism where each Polecat works in its own hook (Git worktree). A setup script can automate this to one command per new agent workspace.[5][1][35]

### Structured Progress Tracking

Adopt the Anthropic harness's progress tracking pattern:[6]

```json
{
  "features": [
    {
      "id": "auth-001",
      "category": "functional",
      "description": "User can log in with email and password",
      "steps": ["Navigate to login page", "Enter credentials", "Submit form", "Verify dashboard loads"],
      "passes": false
    }
  ]
}
```

JSON is preferred over Markdown because agents are less likely to accidentally modify or delete structured JSON entries. Each agent session should only change the `passes` field, never edit or remove feature definitions.[6]

***

## Open-Source Tools to Augment the Stack

### Claude Autopilot (VS Code Extension)

A VS Code/Cursor extension enabling fully automated Claude Code task management:[27]

- **Queue hundreds of tasks** and process them sequentially without intervention
- **Auto-resume** when Claude usage limits reset
- **Sleep prevention** keeps the computer awake during overnight processing
- **Health monitoring** with automatic retry on failures
- Tagline: "Queue up 100 tasks Friday evening, wake up Monday with everything done"[27]

### Roo Code (Free VS Code Extension)

An open-source autonomous coding agent living in VS Code with multi-agent, role-driven execution:[37][38]

- **Modes**: Architect, Code, Debug, Ask, and Custom—each with specific tool access
- **Self-initiated mode switching**: Code mode can automatically switch to Test Engineer mode when ready for testing[37]
- **Works with any OpenAI-compatible API**: use with Claude API, DeepSeek, or local models
- **Free** with optional paid Roo Cloud for team features[37]

### Goosetown (Open-Source Multi-Agent Orchestration)

Built by Block (the company behind Goose), Goosetown is a minimal Gas Town-inspired multi-agent orchestration layer:[39]

- **Orchestrator** breaks tasks into phases (research, build, review) and spawns parallel delegates
- **Town Wall**: append-only communication log where agents coordinate
- **Beads integration** for crash-recoverable progress tracking
- Allows setting cheaper models for subagents to control costs[39]
- Fully open source on GitHub

### Aider (Open-Source Terminal Agent)

A well-established open-source AI pair programming tool:[40]

- Works with Claude, GPT-4, DeepSeek, and local models
- Maps entire codebases for better context
- Automatic Git commits with sensible messages
- Can run in automated/scripted mode for batch processing
- 29.9k+ GitHub stars with active community[41]

***

## Workflow Comparison: Current vs. Proposed

| Dimension | Current Workflow | Proposed Workflow |
|-----------|-----------------|-------------------|
| **Role** | Active monitor and guide | Planner and reviewer |
| **Time in IDE** | 4–8 hours watching agent | 1–2 hours planning + reviewing |
| **Overnight work** | None (agent stops when you stop) | Agents execute autonomously |
| **Error handling** | Manual intervention when agent drifts | Git hooks + TDD auto-block bad code |
| **State management** | In-context (lost on crash) | File-based + Git-backed (survives crashes) |
| **Parallelism** | 1 agent at a time | 2–4 agents via worktrees + Copilot |
| **Monthly cost** | ~$30 | ~$50–60 |
| **Skill development** | Limited by monitoring time | Freed to improve prompting, context engineering, business |

***

## Implementation Roadmap

### Week 1: Foundation

- Add Claude Code Pro ($20/month) subscription if not already active
- Set up CLAUDE.md with modular rules architecture pointing to `.claude/rules/*.md`[18][17]
- Create `feature_list.json` and `claude-progress.txt` templates following the Anthropic harness pattern[6]
- Install Claude Autopilot VS Code extension[27]
- Migrate existing `agents.md` documentation into Claude Code's native subagent configuration format (`.claude/agents/`)[19]

### Week 2: Autonomous Execution Setup

- Install the Overnight Development skill for TDD-enforced autonomous sessions[29]
- Configure Git pre-commit hooks for test and lint enforcement
- Set up GitHub Copilot coding agent: enable on repositories, write 3–5 template issues with detailed acceptance criteria[10]
- Test the overnight pipeline on a small, non-critical task: plan → delegate → sleep → review

### Week 3: Parallel Execution

- Set up Git worktree automation script for parallel Claude Code sessions[35]
- Configure Claude Code background subagents with worktree isolation[19]
- Establish the morning review protocol: PR review → progress check → validation prompt → task queue update
- Add Claude Code GitHub Actions for automated code review on PRs[12]

### Week 4: Optimisation

- Tune CLAUDE.md based on observed failure patterns (document what Claude gets wrong, remove rules it already follows)[17][16]
- Refine task decomposition granularity—smaller tasks with tighter acceptance criteria yield higher autonomous success rates[6]
- Set up cron job for early-morning Claude Code prompt to maximise 5-hour rate limit cycles[15]
- Evaluate whether API credits for Roo Code or Aider add value for specific task types

***

## Key Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Agent produces subtly broken code overnight | TDD with pre-commit hooks blocks commits; morning review catches issues[29] |
| Context window exhaustion mid-task | Anthropic harness pattern: incremental progress + progress files + Git commits[6] |
| Claude Pro rate limits hit during overnight run | Claude Autopilot auto-resumes on limit reset; stagger with Copilot agent[27] |
| Agent goes off-track on complex tasks | Smaller task granularity; explicit acceptance criteria in JSON; review gates[6][26] |
| Merge conflicts from parallel agents | Git worktree isolation ensures each agent works on separate files/branches[35][36] |
| Copilot coding agent produces low-quality PRs | Write extremely detailed issue descriptions; use `.github/copilot-instructions.md`[10] |

***

## Conclusion

Gas Town's most valuable contribution is not its specific tooling but its architectural philosophy: treat agent sessions as ephemeral, store all state in Git, decompose work into verifiable units, and let agents cycle through work queues autonomously. These patterns are reproducible at a fraction of Gas Town's cost.[1][2]

The combination of Claude Code Pro ($20/month) for primary coding with native subagents and hooks, GitHub Copilot Pro ($10/month) for background autonomous execution via the coding agent, and $15–20/month in API credits for GitHub Actions automation creates a capable autonomous development stack for approximately $50/month. Supplemented by free open-source tools—Claude Autopilot for task queuing, the Overnight Development skill for TDD enforcement, and Git worktrees for parallel isolation—this architecture enables the transition from active monitoring to plan-and-review workflows.

The critical shift is from managing agent execution to managing agent inputs: detailed specifications, structured feature lists, explicit acceptance criteria, and automated quality gates. Time previously spent watching agents think is redirected toward improving the planning artifacts that make autonomous execution reliable—a higher-leverage activity that compounds over time.

---

## Official / 2026 links

- [`gastownhall/gastown`](https://github.com/gastownhall/gastown) · [cost issue #24](https://github.com/gastownhall/gastown/issues/24)
- [`findings_gap_opencode_ruflo_gastown.md`](research_overnight_stack_web/gap_wave2/findings_gap_opencode_ruflo_gastown.md)
