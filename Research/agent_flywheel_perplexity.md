
# Engineering a “Budget Flywheel”: Autonomous Overnight Coding Under $60/Month

**Audience:** Solo developer currently using GitHub Copilot Pro + Cursor Pro (~$30/mo)  
**Goal:** Move from *watch-and-guide* in the IDE to *plan-and-review* with overnight autonomous execution  
**Budget:** Up to ~$60/month total

---

## 1. Context and Objectives

You already have:

- Strong prompting and spec discipline (agents.md, openspec planning, etc.)
- Copilot Pro + Cursor Pro giving you good interactive coding support
- A clear pain: having to **sit and watch** agents in VS Code, intervening when they tunnel on local fixes or miss broader context

You want to:

- Describe work once (high‑quality plan/spec)
- Hand it off to agents
- Let them run **unsupervised for hours (overnight)**
- Wake up to diffs/PRs that:
  - Pass tests
  - Respect architectural constraints
  - Require review but not rescue

This is exactly the “agentic coding flywheel” vision—but the commercial Flywheel stack gets there via:

- High‑RAM VPS (often 64GB)
- Multiple high‑end seats (Claude Max, ChatGPT Pro, etc.)
- Swarm of 10+ agents coordinated via custom tooling

Total: **$400–$600/month**.

The good news: you can get **80–90% of the autonomy and velocity** for **~$45–$60/month** by combining:

- A right‑sized VPS (16–32GB RAM instead of 64GB)
- Usage‑based APIs (OpenRouter/DeepSeek/etc.) instead of pricey seats
- Open‑source orchestration and coding agents
- TDD‑anchored loops and structured planning

The rest of this document is a single, integrated plan to get you there.

---

## 2. What Actually Matters from Agent Flywheel

The Flywheel ecosystem is 20+ tools, but the value for *your* goal comes from a few core ideas:

### 2.1 Persistent Server-Side Environment (VPS)

Why your current IDE‑only setup is limiting:

- Local laptop:
  - Limited RAM → 1–2 agents max before things get sluggish
  - No 24/7 uptime → overnight sessions risk network/sleep issues
  - No standardized environment → more “works on my machine” friction
- A VPS gives you:
  - **Always-on** tmux sessions for agents
  - Enough RAM for **3–6 concurrent agents** on a modest box
  - A single, reproducible dev environment

You don’t need Flywheel’s 64GB monster. For one dev:

- 16–32 GB RAM is enough for meaningful parallelism
- Typical cost: **$11–$20/month** for a 16GB NVMe VPS

### 2.2 Orchestration and Coordination

Flywheel’s key orchestration concepts:

- **NTM (Named Tmux Manager)** – tmux as a multi‑agent cockpit
  - Spawn named agent sessions
  - Broadcast prompts
  - Keep agents alive across SSH
- **MCP Agent Mail / file reservations**
  - Threaded message bus for agents
  - Advisory file locking so agents don’t stomp on each other
- **Beads + Beads Viewer (BV)**
  - Backlog as a **graph of beads** (tiny tasks)
  - DAG + PageRank to identify *critical path* beads that unblock the most work

The lesson: the magic isn’t “one smarter agent” but:

- Many agents
- Clear decomposition of work into beads
- A central place they all read/write state and negotiate access to files

### 2.3 Memory and Cognitive Continuity

Flywheel solves ephemeral memory via:

- **CASS**
  - Unified search over all agent transcripts (Claude, Cursor, Gemini, etc.)
  - Non‑trivial: full‑text + semantic search tuned for coding sessions
- **CM (Cognitive Memory / ACE)**
  - Episodic memory: raw logs and events
  - Working memory: current context
  - Procedural memory: distilled “how we do things here”

For you, this means:

- Agents should “remember”:
  - Which patterns worked before
  - Which library versions broke the build
  - How auth, logging, and error‑handling are done in this codebase
- Memory should feed **before** each new session, so agents don’t rediscover the same landmines nightly.

### 2.4 Safety and Quality Gates

Flywheel uses:

- **DCG (Destructive Command Guard)** – intercept dangerous shell commands (`rm -rf`, etc.)
- **SLB (Two-person rule)** – high‑risk actions require a second approval
- **UBS (meta static analysis runner)** – runs multiple language-specific linters/analysers

The key pattern:

- Agents are allowed to run for hours **because**:
  - Their blast radius is controlled (feature branches, guards)
  - They must pass tests and linters before code lands
  - Risky shell operations require humans (or a second agent) to co‑sign

---

## 3. Budget Architecture: “Budget Flywheel” for ~\$45–\$60/Month

### 3.1 Cost Outline

A realistic configuration for you:

| Category       | Component                              | Monthly est. |
|----------------|----------------------------------------|-------------:|
| Compute        | 16GB NVMe VPS (Contabo/Hetzner/etc.)  | $10–$18      |
| High‑IQ Reasoning | Claude Sonnet / similar via OpenRouter | $15–$20      |
| Volume Execution | DeepSeek R1/V3 or similar via API      | $10–$15      |
| Verification   | Cheaper model (o3‑mini/Qwen etc.)     | $5–$8        |
| **Total AI+VPS** |                                      | **$40–$55**  |

You can keep **either** Copilot **or** Cursor for local interactive coding and still stay near $60:

- Option A: Drop Cursor, keep Copilot + Budget Flywheel
- Option B: Drop Copilot, keep Cursor + Budget Flywheel
- Option C: Keep both, but be stricter on API usage (aim ~$40 total including IDE tools)

The rest of the stack is **open-source and free**.

### 3.2 Core Components

**Compute & Environment**

- VPS: Ubuntu 22.04 or later
- Install once via a small “bootstrap” script (inspired by ACFS):
  - Git, Docker, tmux, Python, Node, build tools
  - Aider, Plandex, Cline (if you want code server), linters, test tools

**Orchestration & Coordination**

- **tmux + NTM** (or your own thin wrapper)
  - Named sessions: `plan`, `execute:aider`, `execute:plandex`, `monitor`
- Optional **n8n** for high‑level cron and integration flows (GitHub, notifications, etc.)
- Simple **file-lock registry** for advisory locking

**Coding Agents**

- **Aider** – git‑native, repo maps, watch mode, TDD loops
- **Plandex** – large, multi‑file, multi‑step tasks with a diff sandbox and “Full Auto” mode
- Optionally **OpenHands** – more heavy‑weight cloud agent platform (if you grow into it)

**Task & Memory**

- **Beads-style backlog**:
  - A `beads.jsonl` file or a lightweight Plane/Linear project
  - Each bead = one small, testable task
- **CASS-like memory**
  - SQLite + Qdrant to index:
    - Agent transcripts
    - Past PR descriptions
    - Known patterns / gotchas
- Procedural memory as markdown playbooks in your repo (`/docs/procedures/*.md`)

**Safety & Quality**

- Git feature branches for all agent work
- Aider/Plandex configured with:
  - `--auto-test` / `--test-cmd`
  - Linters/statics (UBS‑equivalent) in `pre-commit` or CI
- Shell aliases/filters as a DCG-lite
- No agent gets `git push` or production access

---

## 4. Tooling Stack in Detail

### 4.1 Orchestration: tmux + NTM + (Optionally) n8n

**tmux + Named Sessions**

- One tmux session per “activity”:
  - `plan`: high-level planning (Sonnet)
  - `execute:aider`: Aider auto‑test loop
  - `execute:plandex`: Plandex Full Auto on big features
  - `monitor`: logs, tests, dashboards
- NTM (or equivalent) lets you:
  - Spin up agents with a command like `ntm spawn aider:auth-refactor`
  - Re‑attach in the morning to see what happened

**n8n for Scheduling and Glue**

Use n8n to:

- Run cron every 30/60 minutes overnight:
  - Poll `beads.jsonl` or Plane/Linear for ready beads
  - Assign them to an agent (Aider or Plandex)
  - Log start/end, status, tokens, test results
- Trigger:
  - Slack/Discord messages when a run finishes or fails
  - GitHub PR creation when tests pass

You don’t *need* n8n on day one, but it becomes very useful once you have multiple agents and multiple repos.

### 4.2 Coding Agents: Aider, Plandex, (Optional) OpenHands

**Aider**

Best for:

- Small/medium tasks
- Refactors within a few related files
- Code changes tightly bound to a clear test

Key features you care about:

- **Git-native**
  - Auto‑commits each coherent change
  - Easy rollback: `git reset --hard HEAD~1` if a run goes bad
- **Repository map**
  - Builds a compact symbol map with ctags
  - Avoids blowing context on irrelevant files
- **`--watch-files` + “AI!” comments**
  - You mark code with comments like `# AI! Implement pagination here`
  - Aider scans for these and autonomously executes the changes
  - Very close to “you plan in the evening; Aider executes at night”

**Plandex**

Best for:

- Large features touching many files
- Multi‑step workflows
- Tasks where you want a **sandbox** and a big context window

Highlights:

- **Diff review sandbox**
  - AI makes changes in a sandbox area, not directly in your main tree
  - Safer for overnight runs → you only merge what looks sane
- **Full Auto mode**
  - Plans → implements → runs commands (build, tests) → debugs
- **Tree-sitter project map + large context**
  - Efficient navigation of very large repos

Strategy:

- Use Plandex for “beads cluster” (a group of related beads that form a feature)
- Use Aider for smaller, frequent, surgical changes

**OpenHands (Optional Later)**

- More suited when you start building more complex, multi‑agent flows across containers or services
- For now you probably don’t need it, but it’s a natural upgrade path if you want more elaborate, cloud-native automation.

### 4.3 Memory: CASS/CM‑Inspired on a Budget

Implement three layers:

1. **Episodic Memory**
   - Store each agent session as a JSONL log:
     - Model, prompt, key decisions, diffs, test results, outcome
   - Save to SQLite for cheap queries

2. **Semantic Search (CASS-like)**
   - Qdrant (self-hosted) as your vector DB
   - After each *successful* run, generate a short summary:
     - “Fixed login race condition in `auth/service.py` by using `asyncio.Lock`”
   - Embed and index that summary + metadata
   - Before a new session:
     - Search Qdrant with “auth race condition” or the current bead description
     - Feed top 3–5 past solutions into the agent’s context

3. **Procedural Memory**
   - When you see recurring patterns, distill into “procedures”:
     - `docs/procedures/auth-pattern.md`
     - `docs/procedures/feature-flagging.md`
   - Agents are instructed to:
     - Search these docs for patterns before coding
     - Update them when new best practices appear

This gives you 80% of Flywheel’s CASS/CM benefit at almost no ongoing cost.

### 4.4 Safety and Quality: DCG/UBS/SLB Equivalents

**Branch and Commit Discipline**

- All agent work happens on feature branches:
  - `agent/2026-02-15-auth-cleanup`
- Only you (or CI) merge into `main`

**Static and Test Gates**

- `pre-commit` config runs:
  - Language formatters (black, prettier, gofmt, etc.)
  - Linters (flake8/eslint/mypy/etc.)
- CI (GitHub Actions or similar) runs:
  - Full test suite
  - Security scanners (Bandit, etc.)

**Command Guard (DCG-lite)**

- Shell aliases or wrapper scripts used in agent sessions:
  - `rm`, `mv`, `git reset --hard`, `docker system prune` → replaced with safe wrappers that log and refuse
- Agents are told:
  - “If you think you need a destructive operation, write a comment about it / open a bead, do not execute it.”

**Two-Person Rule (SLB-lite)**

- Define a set of **protected operations**:
  - DB migrations
  - Auth changes
  - Infrastructure (Terraform, K8s)
- Agents may:
  - Propose these as **draft PRs**
  - But they never auto-merge them
- You (or a second “review agent”) must approve explicitly

---

## 5. Plan-and-Review Workflow: What a Night Looks Like

Here is a concrete overnight workflow that synthesizes your current habits, Flywheel concepts, and the added research.

### 5.1 During the Day: Planning and Decomposition

1. **Define Beads from Your Spec**

   - Take your existing `agents.md` + openspec document
   - Decompose into **beads**:
     - Each bead is:
       - One concise task
       - Testable
       - Scoped to a module/area
   - Store beads as `beads.jsonl` or tasks in Plane/Linear:
     ```jsonl
     {"id": "B-101", "title": "Add pagination to /users API", "scope": "api/users", "tests": ["tests/api/test_users.py::test_pagination"], "deps": ["B-099"], "priority": "high"}
     ```

2. **Select Beads for Tonight**

   - Choose 3–10 beads that:
     - Are independent (few or no mutual deps)
     - Have clear acceptance tests
   - Label them with:
     - `agent: aider` or `agent: plandex`
     - `model: deepseek` or `model: sonnet` if special reasoning is needed

3. **Prime Procedural Memory (Optional but Powerful)**

   - If you know the area has quirks (auth, tenancy, performance):
     - Add or update a short procedural doc
     - e.g. `docs/procedures/pagination.md`
   - Agents will read this before changing code.

### 5.2 Before Bed: Kick Off Autonomous Loops

#### Option A – Aider Watch Mode (for scattered small fixes)

- In your code, sprinkle “AI!” comments:
  ```python
  # AI! Improve error handling here to include user_id and request_id in logs

  # AI! Add pagination to this endpoint using the Pagination helper in utils/pagination.py
```

- On the VPS, run:

```bash
aider \
  --model <deepseek-or-claude> \
  --watch-files \
  --auto-test \
  --test-cmd "pytest tests/api/test_users.py -q"
```

- Aider:
    - Monitors for `AI!` comments
    - Implements them
    - Runs tests after each change
    - Keeps committing as tests pass


#### Option B – Plandex Full Auto (for large features)

- For a big bead cluster (e.g. “Implement multi-tenant billing”):
    - Start Plandex in a named tmux session:

```bash
tmux new -s plan-billing 'plandex --auto --task-file beads/billing-plan.md'
```

- Plandex:
    - Builds a plan
    - Makes changes in its sandbox
    - Runs commands (`pytest`, `npm test`, etc.)
    - Iterates until tests pass or a retry limit is hit
- In the morning, you:
    - Review its sandbox diff
    - Promote good changes into your main branch


#### Option C – “Ralph Wiggum” Persistent Loop (for stubborn tasks)

For occasionally hard problems:

- Use a Bash loop around your agent:
    - If tests are failing or a “done” marker is not present, **do not end**; re‑prompt.
- The loop:
    - Refeeds the original plan
    - Keeps context via modified files and git history
    - Lets the agent “fail forward” for hours until success or budget is reached


### 5.3 Overnight: Coordination and Safety

- n8n can:
    - Watch for stuck logs (no progress for 30+ min)
    - Mark a bead as “blocked” and move on
    - Enforce token and time budgets
- File‑scope and module assignments prevent conflicts:
    - `agent 1` → `api/users/**`
    - `agent 2` → `frontend/users/**`
    - `agent 3` → `tests/**`

Everything happens in feature branches or sandboxes.

### 5.4 Morning: Review and Integrate

When you come back:

1. **Summaries and Logs**
    - For each agent session:
        - A brief summary file (generated at the end of the loop)
        - “What changed, why, how tests looked”
2. **PRs and Diffs**
    - For Aider work:
        - One or more commits on `agent/...` branches
    - For Plandex:
        - Diff in its sandbox
    - You:
        - Spot‑check diffs
        - Rerun tests as desired
        - Merge or squash-merge into your main branch
3. **Memory Update**
    - Index successful sessions into Qdrant
    - Update procedural docs if you see new stable patterns

Time spent: ideally <30 minutes.

---

## 6. Reliability Strategies to Reduce Intervention

Key synthesis from Flywheel + additional research:

### 6.1 TDD as the Core Feedback Loop

- Every bead that agents work on must have:
    - At least one test case (existing or to be added)
- Aider and Plandex are configured with:
    - `--test-cmd "pytest ..."` (or your equivalent)
    - `--auto-test` / full-auto flows that:
        - Treat failing tests as a **new prompt**
        - Iterate until green or max retries

This moves your role from “watch what the agent is doing” to “specify success in tests.”

### 6.2 Hierarchical Planning and Plan Critique

- Before code:
    - High‑IQ model (Claude Sonnet/o3-mini) decomposes a large feature into beads and substeps
- Plan review:
    - You skim the plan
    - Optionally run an “Automated Plan Reviser” pass:
        - A second agent critiques the plan for:
            - Architectural violations
            - Missing acceptance cases
            - Ambiguous or oversized steps

This dramatically reduces the thrash you see now (agents flailing mid‑execution).

### 6.3 Scoped Agents and File/Module Constraints

- Each agent (Aider, Plandex) gets:
    - An explicit **scope**:
        - Directories allowed
        - Files it should not touch
- Combined with:
    - A simple file-lock mechanism
    - Module ownership (“auth is agent X’s territory tonight”)

This lowers both merge conflicts and weird cross‑module mistakes.

### 6.4 Circuit Breakers and Budget Guards

- Track:
    - Tokens by agent, by night
    - Time per bead
- Enforce:
    - Daily API budget limit
    - Max retries per bead
    - Hard stop if tests are failing for N consecutive runs

If a task continues to fail:

- The system:
    - Rolls back last commit
    - Files a “needs human review” bead
    - Moves on to the next item

---

## 7. Incremental Rollout (0–8+ Weeks)

You don’t need to build everything at once. Here’s a pragmatic path.

### Week 1–2: Single-Agent, TDD-First

- Set up:
    - VPS with tmux, Aider, Git, tests
    - Single repo deployed there
- Workflows:
    - Run Aider on clearly scoped beads with `--auto-test`
    - Do *supervised* runs the first couple of evenings to establish trust
- Goal:
    - Get comfortable with TDD loops and rollback/branching
    - Confirm Aider can complete small beads with almost no intervention


### Week 3–4: Overnight Runs + Memory

- Introduce:
    - Overnight Aider runs via `--watch-files` and AI! comments
    - Qdrant + SQLite for basic episodic + semantic memory
- Workflows:
    - You plan beads and AI! comments in the evening
    - Aider executes overnight on a feature branch
- Goal:
    - Wake up to working, tested code in narrow areas
    - Minimal or zero mid‑run supervision


### Week 5–6: Plandex for Big Work and Multi-Agent

- Add:
    - Plandex for multi‑file/feature beads
    - n8n (optional) to schedule and monitor separate Aider and Plandex sessions
- Workflows:
    - Aider: small/medium beads
    - Plandex: big bead clusters
- Goal:
    - Several beads completed per night
    - Parallelism (2–3 agents) without conflicts


### Week 7–8+: Full Budget Flywheel

- Enhance:
    - Memory (better summaries, more procedural docs)
    - Safety (more refined “two-person rule,” stricter DCG-style guards)
    - Automatic PR creation
- Optionally:
    - Add more fine‑grained coordination (simple MCP tooling, message bus)
    - Experiment with LATS-like strategies for especially hard problems

Goal: a stable “plan-and-review” ecosystem where:

- Your main work is planning, decomposition, and review
- Agents handle the midnight grind under well‑defined constraints
- Your total spend stays ≤ ~\$60/month

---

## 8. Summary

By combining:

- A modest VPS (16–32GB RAM) for persistent, parallel agent sessions
- Usage-based APIs (Sonnet/DeepSeek/etc.) instead of expensive seats
- Open-source coding agents (Aider, Plandex) wired into:
    - TDD loops
    - Repo maps and sandboxed diffs
- Lightweight Flywheel-inspired orchestration:
    - tmux + NTM for sessions
    - Beads backlog + basic PageRank-ish prioritization
    - CASS/CM-like memory built from SQLite + Qdrant
    - DCG/UBS/SLB analogues via shell guards, tests, and branch discipline

…you can move from *watching Cursor and Copilot work* to *delegating overnight tasks to a small swarm* and reviewing their output over coffee.

You’re not trying to copy Agent Flywheel’s exact stack; you’re capturing its **principles**:

- Persistent environment
- Many small, testable beads
- Memory that compounds across nights
- Safety rails that let agents run unsupervised
- Smart model tiering to squeeze maximum value from every dollar

Within your ~\$60/month budget, that’s entirely achievable—and the attached research plus your existing habits give you a strong head start.

---

## Official / 2026 links

- [`agent_flywheel_clawdbot_skills_and_integrations`](https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations) · [`mcp_agent_mail`](https://github.com/Dicklesworthstone/mcp_agent_mail)
- [`findings_orchestration_opencode_ralph_ruflo_flywheel.md`](research_overnight_stack_web/findings_orchestration_opencode_ralph_ruflo_flywheel.md)
