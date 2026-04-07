# DeepWiki Q&A with Code Context for Repository: ruvnet/ruflo
## Q1
Analyse the ruflor repo and create a comprehensive response tailored for my current requirements and sticking points> I currently use GitHub Copilot Pro and Cursor Pro (not married to these tools happy to change), I am willing to potentially double this investment to around $60 per month plus and additional $20 for a smaller VPS, but I require demonstrably better outcomes to justify the additional cost. My primary pain point is the excessive time spent actively watching the agent execute in VSCode, monitoring its thinking process, and intervening when I notice it may have skipped a fix broader fix to focus on the current task. I think this is useful, but I could better use my time elsewhere. While I have established a solid workflow utilising detailed agents.md documentation and openspec for planning, this still requires much hands-on supervision. My desired workflow shift is from active monitoring to planning and delegation: I want to define the work, set the agent executing, and return after an extended period such as overnight to review completed work. This would free me to focus on developing my prompting capabilities, context engineering techniques, and other skills that improve agentic engineering outcomes. Please provide a detailed technical report covering: the core components and capabilities of ruflo that would be most valuable, alternative open-source or lower-cost tools and frameworks that could replicate this functionality, a proposed architecture combining available tools within my $60/month budget, specific implementation strategies for achieving autonomous overnight execution with minimal supervision, and recommendations for improving agent reliability and reducing the need for intervention during execution cycles. Include specific tools, configurations, and integration approaches that would enable me to transition from my current watch-and-guide workflow to a plan-and-review workflow.
### Answer
# Ruflo Technical Report: Transitioning to a Plan-and-Review Workflow

---

## Executive Summary

**Ruflo** (the npm package `claude-flow`, v3.5.1) is not a coding assistant — it is an **enterprise AI agent orchestration layer** that sits on top of Claude Code (or OpenAI Codex CLI) and manages state, memory, coordination, and background execution so that the underlying AI does all real work autonomously. This distinction is the foundation of the entire system's value proposition for your use case. ruflo:11-18 

The core design philosophy directly matches your goal: `claude-flow` is the ledger, not the worker. ruflo:30-35 

---

## Part 1: Core Ruflo Components Most Valuable to Your Use Case

### 1.1 The Background Worker Daemon — Your "Overnight Engine"

This is the single most important component for your workflow shift. The `WorkerDaemon` (`daemon.ts`) can be started as a **detached background process** that runs independently of any terminal session. It manages 12 specialised workers that fire at configurable intervals without any human presence. ruflo:213-245 

When started in background mode, the daemon forks a detached child process, writes a PID file, and logs to `.claude-flow/daemon.log`. You can close your terminal and the work continues. The default workers and their intervals are: ruflo:94-103 

The staggered `offsetMs` values prevent workers from competing for resources simultaneously — a critical reliability detail for unattended overnight runs.

### 1.2 The Headless Worker Executor — AI Without a UI

For workers that require intelligence rather than just scripting, the `HeadlessWorkerExecutor` class runs **Claude Code in headless mode** (`claude --headless`) inside a sandboxed subprocess. This is the mechanism that lets AI analysis (security audits, test gap detection, optimisation) happen while you sleep. ruflo:591-618 

Workers are classified into two groups:
- **Headless workers** (require Claude Code AI): `audit`, `optimize`, `testgaps`, `document`, `ultralearn`, `refactor`, `deepdive`, `predict`
- **Local workers** (run without AI, pure logic): `map`, `consolidate`, `benchmark`, `preload` ruflo:35-48 

Each headless worker has a pre-built prompt template, sandbox mode (`strict`/`permissive`/`disabled`), model selection, and timeout configuration. For example, the `audit` worker runs on `haiku` (cheap and fast) in `strict` sandbox with a 5-minute timeout: ruflo:282-310 

The process pool limits concurrent Claude Code processes to prevent resource exhaustion: ruflo:680-700 

### 1.3 Anti-Drift Swarm Topology — Replacing Your Intervention Role

Your primary pain point — catching when an agent skips a broader fix to focus on the current task — is precisely what the **hierarchical topology with raft consensus** is designed to prevent. The coordinator agent validates each sub-agent's output against the original goal before proceeding. ruflo:53-77 

The CLAUDE.md configuration explicitly defines anti-drift settings as project defaults: ruflo:271-280 

The "spawn and wait" pattern is critically important: agents are spawned in background mode, the orchestrator reports what is happening to you, and then **stops** — it does not poll or check status repeatedly, which is the behaviour that currently forces you to watch: ruflo:126-158 

### 1.4 The 3-Tier Model Routing System — Cost Efficiency

This directly extends the value of your Claude subscription by routing simple tasks to WASM (free), medium tasks to Haiku, and only complex tasks to Sonnet/Opus: ruflo:20-50 

The README quantifies this: "extend your Claude Code usage by 250% or save significantly on direct API costs." ruflo:266-275 

### 1.5 Persistent Vector Memory — Cross-Session Context

The HNSW-indexed AgentDB memory system means your agents remember successful patterns across sessions. This directly addresses your pain point of agents repeating mistakes you've already corrected. The 4-step pipeline (RETRIEVE → JUDGE → DISTILL → CONSOLIDATE) runs before every task: ruflo:41-44 

The memory commands you would use before and after every work session: ruflo:163-187 

Semantic vector scores above 0.7 mean the pattern is strongly matched and should be used without modification: ruflo:649-658 

### 1.6 Session Persistence — Overnight Handoff

Session start/end hooks preserve full context so that when you return in the morning, the agent can restore exactly where it left off: ruflo:544-553 

### 1.7 The Hooks System — Self-Learning Without Your Input

The 27 hooks + 12 background workers create a self-improving loop. The `pre-task` hook routes intelligently; the `post-task` hook stores what worked: ruflo:380-412 

The `ultralearn` and `deepdive` background workers (manually triggered) perform deep codebase analysis that pre-loads the agent with architectural knowledge before you begin a session: ruflo:384-412 

---

## Part 2: Alternative Open-Source / Lower-Cost Tools

The following tools can replicate parts of Ruflo's functionality if you want to reduce vendor dependency or supplement it.

### 2.1 Aider (Free, Open Source)
**Replicates**: Headless autonomous coding, git-integrated workflow, multi-file edits.
Aider runs entirely from the CLI with `--yes` flags for autonomous mode, integrates with any git repo, and outputs structured diffs. It is the most mature open-source alternative for "fire and forget" code generation. Run it in a `tmux` session on your VPS overnight with `aider --model claude-sonnet --yes --message "..." > aider.log 2>&1`.

### 2.2 OpenHands (formerly OpenDevin — Free, Self-Hosted)
**Replicates**: Full autonomous agent with browser, terminal, and file system access in a Docker sandbox. It handles multi-step tasks and recovers from errors without intervention. This is the closest open-source equivalent to a "plan and return tomorrow" workflow. Can run entirely on your $20 VPS.

### 2.3 SWE-Agent (Free, Princeton Research)
**Replicates**: Autonomous GitHub issue resolution. If your workflow involves fixing bugs or implementing features from issue descriptions, SWE-Agent is purpose-built for this. Pair it with your existing `openspec` planning docs.

### 2.4 Continue.dev (Free Tier Available — ~$0–$10/month)
**Replicates**: Most of what Cursor Pro provides for ~$0 (with your own API keys). Drop Cursor Pro and save $20/month. Continue.dev supports Claude, GPT-4, and local models, and works as a VSCode/JetBrains extension.

### 2.5 tmux + Claude Code (`claude --headless`)
**Replicates**: The daemon's core overnight execution. This is the low-tech, zero-cost version of Ruflo's headless executor. A `tmux` session on your VPS with `claude --headless -p "$(cat task.md)" > output.log 2>&1` is the minimal viable overnight executor.

### 2.6 ReasoningBank / agentic-flow (Bundled with Ruflo)
**Replicates**: The learning pipeline within Ruflo itself. The `agentic-flow-bridge.ts` exposes this as an optional dependency for external integration: ruflo:1-56 

---

## Part 3: Proposed Architecture Within Your $80/Month Budget

```
┌─────────────────────────────────────────────────────────────────────┐
│  YOUR WORKFLOW (Plan & Review — NOT Watch & Guide)                  │
├───────────────────┬─────────────────────────────────────────────────┤
│  PLANNING (YOU)   │  EXECUTION (UNATTENDED)                         │
│  Morning session  │  VPS + Daemon running overnight                 │
│  ~30-60 min       │  ~8-12 hours autonomous                         │
└───────────────────┴─────────────────────────────────────────────────┘
```

### Budget Allocation (Replacing, Not Adding)

| Current Tool | Cost | Replacement | Cost | Saving |
|---|---|---|---|---|
| GitHub Copilot Pro | ~$10-19/mo | Drop entirely | $0 | ~$10-19 |
| Cursor Pro | $20/mo | Continue.dev + own keys | $0 | $20 |
| — | — | Claude Code (Max/Pro) | $20-100/mo | — |
| — | — | VPS (e.g. Hetzner CX11) | $4-6/mo | — |
| — | — | Ruflo (MIT, npm) | $0 | — |

**Recommended Stack for ~$60/month total:**
- **Claude Code Pro** ($20/mo) — the executor, runs headlessly on VPS
- **Anthropic API** ($10-20/mo usage-based, for Haiku/Sonnet routing) — keeps costs low via 3-tier routing
- **Hetzner VPS CX21** ($6/mo, 2 vCPU, 4GB RAM) — runs the daemon permanently
- **Continue.dev** ($0) — replaces Cursor Pro for your interactive planning sessions
- **Ruflo** ($0, MIT licence) — orchestration layer

**Total: ~$36-46/month**, well within your $60 budget, with the remainder as API cost buffer.

### System Architecture Diagram

```mermaid
graph TD
    "You (Planning)" --> "CLAUDE.md / AGENTS.md\n(Task Specification)"
    "CLAUDE.md / AGENTS.md\n(Task Specification)" --> "Ruflo init\n(session-start hook)"
    "Ruflo init\n(session-start hook)" --> "VPS Daemon\n(detached background)"

    subgraph "VPS — Runs Overnight Unattended"
        "VPS Daemon\n(detached background)" --> "memory_search\n(HNSW retrieve patterns)"
        "memory_search\n(HNSW retrieve patterns)" --> "Swarm Init\n(hierarchical, max 8 agents)"
        "Swarm Init\n(hierarchical, max 8 agents)" --> "Coordinator Agent\n(anti-drift enforcer)"
        "Coordinator Agent\n(anti-drift enforcer)" --> "Coder Agent\n(headless claude)"
        "Coordinator Agent\n(anti-drift enforcer)" --> "Tester Agent\n(headless claude)"
        "Coordinator Agent\n(anti-drift enforcer)" --> "Reviewer Agent\n(headless claude)"
        "Coder Agent\n(headless claude)" --> "post-task hook\n(memory_store patterns)"
        "Tester Agent\n(headless claude)" --> "post-task hook\n(memory_store patterns)"
        "Reviewer Agent\n(headless claude)" --> "post-task hook\n(memory_store patterns)"
        "post-task hook\n(memory_store patterns)" --> "session-end\n(persist state, export metrics)"
    end

    "session-end\n(persist state, export metrics)" --> "You (Review)\nNext Morning"
```

---

## Part 4: Specific Implementation Strategy for Overnight Execution

### Step 1: VPS Setup (~30 minutes, one-time)

Install Node.js 20+, Claude Code CLI, and Ruflo on your Hetzner VPS. The install script handles everything: ruflo:154-162 

Run `npx ruflo@alpha doctor --fix` to validate the environment: ruflo:590-616 

### Step 2: Configure the Daemon for Overnight Runs

The daemon starts detached by default. Key workers to enable for overnight execution:

- `ultralearn` — deep codebase ingestion before the session (manual trigger at session start)
- `audit` — runs every 10 minutes, catches security regressions introduced by the coder agents
- `testgaps` — runs every 20 minutes, identifies missing test coverage in real-time
- `optimize` — runs every 15 minutes, flags performance issues ruflo:19-31 

### Step 3: Your Evening Planning Session (~30–60 min)

1. Write your task specification using your existing `agents.md` + `openspec` workflow
2. Run `npx ruflo hooks pretrain` to bootstrap the intelligence system from your repo
3. Run `npx ruflo hooks session-start --session-id "overnight-$(date +%Y%m%d)"`
4. Trigger `ultralearn` to deep-scan the codebase: `npx ruflo daemon trigger -w ultralearn`
5. Init the swarm with anti-drift configuration: ruflo:85-124 

6. Spawn all agents in one message with `run_in_background: true` and **stop**. The critical rule: ruflo:147-157 

### Step 4: Overnight Autonomous Execution Pattern

The headless executor manages a concurrent process pool (default: 2 simultaneous Claude Code processes) with automatic queuing for overflow: ruflo:660-700 

Each worker prompt is structured, sandboxed, and has a hard timeout. Workers that fail are logged to `.claude-flow/logs/headless/` and do not crash the daemon — the pool simply continues: ruflo:882-900 

### Step 5: Your Morning Review Session

```bash
# 1. Check daemon logs for overnight activity
cat .claude-flow/daemon.log | tail -100

# 2. Restore session context
npx ruflo hooks session-restore --latest

# 3. Review metrics
npx ruflo hooks metrics --v3-dashboard

# 4. Check what patterns were learned
npx ruflo memory list --namespace patterns

# 5. Review swarm status and completed tasks
npx ruflo swarm status
npx ruflo task list --all

# 6. End session, export metrics for trend tracking
npx ruflo hooks session-end --generate-summary true --export-metrics true
```

---

## Part 5: Reducing Intervention — Agent Reliability Recommendations

### 5.1 The AGENTS.md Pattern (You Already Have This — Amplify It)

Your existing `agents.md` documentation is directly supported by Ruflo's AGENTS.md standard. The critical addition is the **memory search before every task** rule. Store your proven patterns explicitly so agents don't reinvent them: ruflo:20-27 

The vector search threshold of `score > 0.7` means a past pattern is matched with high confidence and should be used directly — this is how the system prevents the agent from "skipping a broader fix": ruflo:597-605 

### 5.2 Use `hierarchical` Topology with `raft` Consensus

This is the most important single configuration choice for reducing drift and intervention needs. The `hierarchical` topology means a coordinator validates every sub-agent's output. `raft` consensus means there is always a single authoritative leader maintaining state — no conflicting decisions between agents. ruflo:365-393 

### 5.3 Task Routing Codes — Pre-Define Agent Teams Per Task Type

The routing table maps task types to specific agent team compositions. Using this eliminates ambiguity about which agents should handle a given task, reducing the coordination failures that require your intervention: ruflo:213-224 

### 5.4 Continuous Improvement Triggers — Automated Where Your Eye Currently Goes

Map the specific situations where you currently intervene to the correct background worker trigger: ruflo:190-206 

### 5.5 Coverage-Aware Routing — Prevents the "Skipped Fix" Problem

The `coverage-route` and `coverage-gaps` hooks specifically address your pain point of agents skipping broader fixes. Before assigning a task, the hook identifies what test coverage is missing and routes accordingly, so the agent is aware of the broader context, not just the immediate ticket: ruflo:455-463 

### 5.6 The Claims System — Work Ownership Prevents Duplication

The claims-based authorization system assigns explicit ownership of work to specific agents. This prevents two agents from both touching the same file (a common cause of conflicts that require your intervention): ruflo:746-749 

### 5.7 The `doctor` Command — Pre-Flight Reliability Check

Before every overnight session, run a health check. This catches broken configurations before they cause silent failures at 2am: ruflo:28-29 

---

## Part 6: Transition Roadmap

### Week 1: Infrastructure Setup
- Provision Hetzner CX21 VPS ($6/mo)
- Install Claude Code + Ruflo with `--full` flag
- Replace Cursor Pro with Continue.dev + your own Anthropic API key (saves $20/mo)
- Run `npx ruflo init --wizard` on your primary project

### Week 2: Memory Bootstrapping
- Run `npx ruflo hooks pretrain` on your existing codebase to ingest patterns
- Trigger `ultralearn` manually: `npx ruflo daemon trigger -w ultralearn`
- Store your 10–15 most successful past problem-solving patterns using `memory store`
- Validate semantic search is returning relevant results above the 0.7 threshold

### Week 3: First Supervised Overnight Run
- Start with a well-defined, bounded task (not open-ended)
- Use `maxAgents: 4–6` and `hierarchical` topology
- Leave the daemon running; check logs in the morning
- Identify which failure modes require hook customisation

### Week 4: Full Autonomy Mode
- Enable `audit` + `testgaps` workers continuously
- Drop GitHub Copilot Pro (Continue.dev covers interactive completion)
- Shift your "watch time" to prompt/context engineering improvement as intended

---

## Notes

1. **Ruflo is not an agent — it is an orchestration layer.** The actual code writing is done by Claude Code (which runs headlessly as a subprocess). This means your Anthropic subscription is the true execution budget; Ruflo itself is MIT-licensed and free. ruflo:2-6 

2. **The repository is named `ruflo` but the npm package is `claude-flow`.** The rename is recent and explained in the README: "Claude Flow is now Ruflo — named by Ruv." Both names refer to the same system. ruflo:28-29 

3. **Alpha stability caveat.** Ruflo v3 is currently in alpha (`ruflo@alpha` on npm). The daemon and headless executor are functional, but for production overnight runs you should pin a specific version and validate with `doctor --fix` before each session. The v3.0.0 stable release target is noted in planning docs. ruflo:25-26 

4. **The Codex dual-mode feature** allows you to run Claude Code for interactive sessions and spawn headless Codex (OpenAI) workers for parallel background tasks — relevant if you want to hedge against Anthropic pricing or availability. ruflo:546-574 

5. **The comparison document** in the repo notes that Claude Code's own `TeammateTool` (v2.1.19+) implements a 92% architecturally similar swarm system natively. As Claude Code matures, some of Ruflo's coordination features may be redundant — but the memory persistence, headless daemon, and hooks system remain uniquely valuable for your overnight execution use case. ruflo:8-18
### Citations
**File:** AGENTS.md (L11-18)
```markdown
╔═══════════════════════════════════════════════════════════════════════════╗
║  1. claude-flow = LEDGER (tracks state, stores memory, coordinates)       ║
║  2. Codex = EXECUTOR (writes code, runs commands, creates files)          ║
║  3. NEVER stop after calling claude-flow - IMMEDIATELY continue working   ║
║  4. If you need something BUILT/EXECUTED, YOU do it, not claude-flow      ║
║  5. ALWAYS search memory BEFORE starting: memory search --query "task"    ║
║  6. ALWAYS store patterns AFTER success: memory store --namespace patterns║
╚═══════════════════════════════════════════════════════════════════════════╝
```
**File:** AGENTS.md (L20-27)
```markdown

**Workflow (Use MCP Tools):**
1. `memory_search(query="task keywords")` → LEARN from past patterns (score > 0.7 = use it)
2. `swarm_init(topology="hierarchical")` → coordination record (instant)
3. **YOU write the code / run the commands** ← THIS IS WHERE WORK HAPPENS
4. `memory_store(key="pattern-x", value="what worked", namespace="patterns")` → REMEMBER for next time

---
```
**File:** AGENTS.md (L30-35)
```markdown

```
┌─────────────────────────────────────────────────────────────┐
│  CLAUDE-FLOW = ORCHESTRATOR (tracks state, coordinates)     │
│  CODEX = WORKER (writes code, runs commands, implements)    │
└─────────────────────────────────────────────────────────────┘
```
**File:** AGENTS.md (L597-605)
```markdown

### Vector Search Tips
- Searches are SEMANTIC (meaning-based, not just keywords)
- Score > 0.7 = strong match, use that pattern
- Score 0.5-0.7 = partial match, adapt as needed
- Store DETAILED values for better future retrieval

### CLI Fallback (if MCP unavailable)
```bash
```
**File:** v3/@claude-flow/cli/src/commands/daemon.ts (L19-31)
```typescript
    { name: 'workers', short: 'w', type: 'string', description: 'Comma-separated list of workers to enable (default: map,audit,optimize,consolidate,testgaps)' },
    { name: 'quiet', short: 'Q', type: 'boolean', description: 'Suppress output' },
    { name: 'background', short: 'b', type: 'boolean', description: 'Run daemon in background (detached process)', default: true },
    { name: 'foreground', short: 'f', type: 'boolean', description: 'Run daemon in foreground (blocks terminal)' },
    { name: 'headless', type: 'boolean', description: 'Enable headless worker execution (E2B sandbox)' },
    { name: 'sandbox', type: 'string', description: 'Default sandbox mode for headless workers', choices: ['strict', 'permissive', 'disabled'] },
  ],
  examples: [
    { command: 'claude-flow daemon start', description: 'Start daemon in background (default)' },
    { command: 'claude-flow daemon start --foreground', description: 'Start in foreground (blocks terminal)' },
    { command: 'claude-flow daemon start -w map,audit,optimize', description: 'Start with specific workers' },
    { command: 'claude-flow daemon start --headless --sandbox strict', description: 'Start with headless workers in strict sandbox' },
  ],
```
**File:** v3/@claude-flow/cli/src/commands/daemon.ts (L213-245)
```typescript
  // Use spawn with explicit arguments instead of shell string interpolation
  // This prevents command injection via paths
  const child = spawn(process.execPath, [
    cliPath,
    'daemon', 'start', '--foreground', '--quiet'
  ], {
    cwd: resolvedRoot,
    detached: true,
    stdio: ['ignore', fs.openSync(logFile, 'a'), fs.openSync(logFile, 'a')],
    env: { ...process.env, CLAUDE_FLOW_DAEMON: '1' },
  });

  // Get PID from spawned process directly (no shell echo needed)
  const pid = child.pid;

  if (!pid || pid <= 0) {
    output.printError('Failed to get daemon PID');
    return { success: false, exitCode: 1 };
  }

  // Save PID
  fs.writeFileSync(pidFile, String(pid));

  if (!quiet) {
    output.printSuccess(`Daemon started in background (PID: ${pid})`);
    output.printInfo(`Logs: ${logFile}`);
    output.printInfo(`Stop with: claude-flow daemon stop`);
  }

  // Unref so parent can exit immediately
  child.unref();

  return { success: true };
```
**File:** v3/@claude-flow/cli/src/services/worker-daemon.ts (L94-103)
```typescript
// Default worker configurations with improved intervals (P0 fix: map 5min -> 15min)
const DEFAULT_WORKERS: WorkerConfigInternal[] = [
  { type: 'map', intervalMs: 15 * 60 * 1000, offsetMs: 0, priority: 'normal', description: 'Codebase mapping', enabled: true },
  { type: 'audit', intervalMs: 10 * 60 * 1000, offsetMs: 2 * 60 * 1000, priority: 'critical', description: 'Security analysis', enabled: true },
  { type: 'optimize', intervalMs: 15 * 60 * 1000, offsetMs: 4 * 60 * 1000, priority: 'high', description: 'Performance optimization', enabled: true },
  { type: 'consolidate', intervalMs: 30 * 60 * 1000, offsetMs: 6 * 60 * 1000, priority: 'low', description: 'Memory consolidation', enabled: true },
  { type: 'testgaps', intervalMs: 20 * 60 * 1000, offsetMs: 8 * 60 * 1000, priority: 'normal', description: 'Test coverage analysis', enabled: true },
  { type: 'predict', intervalMs: 10 * 60 * 1000, offsetMs: 0, priority: 'low', description: 'Predictive preloading', enabled: false },
  { type: 'document', intervalMs: 60 * 60 * 1000, offsetMs: 0, priority: 'low', description: 'Auto-documentation', enabled: false },
];
```
**File:** v3/@claude-flow/cli/src/services/headless-worker-executor.ts (L35-48)
```typescript
export type HeadlessWorkerType =
  | 'audit'
  | 'optimize'
  | 'testgaps'
  | 'document'
  | 'ultralearn'
  | 'refactor'
  | 'deepdive'
  | 'predict';

/**
 * Local worker types - workers that run locally without AI
 */
export type LocalWorkerType = 'map' | 'consolidate' | 'benchmark' | 'preload';
```
**File:** v3/@claude-flow/cli/src/services/headless-worker-executor.ts (L282-310)
```typescript
export const HEADLESS_WORKER_CONFIGS: Record<HeadlessWorkerType, HeadlessWorkerConfig> = {
  audit: {
    type: 'audit',
    mode: 'headless',
    intervalMs: 30 * 60 * 1000,
    priority: 'critical',
    description: 'AI-powered security analysis',
    enabled: true,
    headless: {
      promptTemplate: `Analyze this codebase for security vulnerabilities:
- Check for hardcoded secrets (API keys, passwords)
- Identify SQL injection risks
- Find XSS vulnerabilities
- Check for insecure dependencies
- Identify authentication/authorization issues

Provide a JSON report with:
{
  "vulnerabilities": [{ "severity": "high|medium|low", "file": "...", "line": N, "description": "..." }],
  "riskScore": 0-100,
  "recommendations": ["..."]
}`,
      sandbox: 'strict',
      model: 'haiku',
      outputFormat: 'json',
      contextPatterns: ['**/*.ts', '**/*.js', '**/.env*', '**/package.json'],
      timeoutMs: 5 * 60 * 1000,
    },
  },
```
**File:** v3/@claude-flow/cli/src/services/headless-worker-executor.ts (L384-412)
```typescript
  ultralearn: {
    type: 'ultralearn',
    mode: 'headless',
    intervalMs: 0, // Manual trigger only
    priority: 'normal',
    description: 'Deep knowledge acquisition',
    enabled: false,
    headless: {
      promptTemplate: `Deeply analyze this codebase to learn:
- Architectural patterns used
- Coding conventions
- Domain-specific terminology
- Common patterns and idioms
- Team preferences

Provide insights as JSON:
{
  "architecture": { "patterns": [...], "style": "..." },
  "conventions": { "naming": "...", "formatting": "..." },
  "domains": ["..."],
  "insights": ["..."]
}`,
      sandbox: 'strict',
      model: 'opus',
      outputFormat: 'json',
      contextPatterns: ['**/*.ts', '**/CLAUDE.md', '**/README.md'],
      timeoutMs: 15 * 60 * 1000,
    },
  },
```
**File:** v3/@claude-flow/cli/src/services/headless-worker-executor.ts (L591-618)
```typescript
export class HeadlessWorkerExecutor extends EventEmitter {
  private projectRoot: string;
  private config: Required<HeadlessExecutorConfig>;
  private processPool: Map<string, PoolEntry> = new Map();
  private pendingQueue: QueueEntry[] = [];
  private contextCache: Map<string, CacheEntry> = new Map();
  private claudeCodeAvailable: boolean | null = null;
  private claudeCodeVersion: string | null = null;

  constructor(projectRoot: string, options?: HeadlessExecutorConfig) {
    super();
    this.projectRoot = projectRoot;

    // Merge with defaults
    this.config = {
      maxConcurrent: options?.maxConcurrent ?? 2,
      defaultTimeoutMs: options?.defaultTimeoutMs ?? 5 * 60 * 1000,
      maxContextFiles: options?.maxContextFiles ?? 20,
      maxCharsPerFile: options?.maxCharsPerFile ?? 5000,
      logDir: options?.logDir ?? join(projectRoot, '.claude-flow', 'logs', 'headless'),
      cacheContext: options?.cacheContext ?? true,
      cacheTtlMs: options?.cacheTtlMs ?? 60000, // 1 minute default
    };

    // Ensure log directory exists
    this.ensureLogDir();
  }

```
**File:** v3/@claude-flow/cli/src/services/headless-worker-executor.ts (L660-700)
```typescript
  async execute(
    workerType: HeadlessWorkerType,
    configOverrides?: Partial<HeadlessOptions>
  ): Promise<HeadlessExecutionResult> {
    const baseConfig = HEADLESS_WORKER_CONFIGS[workerType];
    if (!baseConfig) {
      throw new Error(`Unknown headless worker type: ${workerType}`);
    }

    // Check availability
    const available = await this.isAvailable();
    if (!available) {
      const result = this.createErrorResult(
        workerType,
        'Claude Code CLI not available. Install with: npm install -g @anthropic-ai/claude-code'
      );
      this.emit('error', result);
      return result;
    }

    // Check concurrent limit
    if (this.processPool.size >= this.config.maxConcurrent) {
      // Queue the request
      return new Promise((resolve, reject) => {
        const entry: QueueEntry = {
          workerType,
          config: configOverrides,
          resolve,
          reject,
          queuedAt: new Date(),
        };
        this.pendingQueue.push(entry);
        this.emit('queued', {
          workerType,
          queuePosition: this.pendingQueue.length,
        });
      });
    }

    // Execute immediately
    return this.executeInternal(workerType, configOverrides);
```
**File:** v3/@claude-flow/cli/src/services/headless-worker-executor.ts (L882-900)
```typescript
      this.logExecution(executionId, 'result', JSON.stringify(executionResult, null, 2));

      this.emit('complete', executionResult);
      return executionResult;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      const executionResult = this.createErrorResult(workerType, errorMessage);
      executionResult.executionId = executionId;
      executionResult.durationMs = Date.now() - startTime;

      this.logExecution(executionId, 'error', errorMessage);
      this.emit('error', executionResult);

      return executionResult;
    } finally {
      // Process next in queue
      this.processQueue();
    }
  }
```
**File:** v3/@claude-flow/cli/CLAUDE.md (L20-50)
```markdown
### 🤖 INTELLIGENT 3-TIER MODEL ROUTING (ADR-026)

**The routing system has 3 tiers for optimal cost/performance:**

| Tier | Handler | Latency | Cost | Use Cases |
|------|---------|---------|------|-----------|
| **1** | Agent Booster | <1ms | $0 | Simple transforms (var→const, add-types, remove-console) |
| **2** | Haiku | ~500ms | $0.0002 | Simple tasks, bug fixes, low complexity |
| **3** | Sonnet/Opus | 2-5s | $0.003-$0.015 | Architecture, security, complex reasoning |

**Before spawning agents, get routing recommendation:**
```bash
npx @claude-flow/cli@latest hooks pre-task --description "[task description]"
```

**When you see these recommendations:**

1. `[AGENT_BOOSTER_AVAILABLE]` → Skip LLM entirely, use Edit tool directly
   - Intent types: `var-to-const`, `add-types`, `add-error-handling`, `async-await`, `add-logging`, `remove-console`

2. `[TASK_MODEL_RECOMMENDATION] Use model="X"` → Use that model in Task tool:
```javascript
Task({
  prompt: "...",
  subagent_type: "coder",
  model: "haiku"  // ← USE THE RECOMMENDED MODEL (haiku/sonnet/opus)
})
```

**Benefits:** 75% cost reduction, 352x faster for Tier 1 tasks

```
**File:** v3/@claude-flow/cli/CLAUDE.md (L53-77)
```markdown
### 🛡️ Anti-Drift Config (PREFERRED)

**Use this to prevent agent drift:**
```bash
# Small teams (6-8 agents) - use hierarchical for tight control
npx @claude-flow/cli@latest swarm init --topology hierarchical --max-agents 8 --strategy specialized

# Large teams (10-15 agents) - use hierarchical-mesh for V3 queen + peer communication
npx @claude-flow/cli@latest swarm init --topology hierarchical-mesh --max-agents 15 --strategy specialized
```

**Valid Topologies:**
- `hierarchical` - Queen controls workers directly (anti-drift for small teams)
- `hierarchical-mesh` - V3 queen + peer communication (recommended for 10+ agents)
- `mesh` - Fully connected peer network
- `ring` - Circular communication pattern
- `star` - Central coordinator with spokes
- `hybrid` - Dynamic topology switching

**Anti-Drift Guidelines:**
- **hierarchical**: Coordinator catches divergence
- **max-agents 6-8**: Smaller team = less drift
- **specialized**: Clear roles, no overlap
- **consensus**: raft (leader maintains state)

```
**File:** v3/@claude-flow/cli/CLAUDE.md (L85-124)
```markdown
// STEP 1: Initialize swarm coordination (anti-drift config)
Bash("npx @claude-flow/cli@latest swarm init --topology hierarchical --max-agents 8 --strategy specialized")

// STEP 2: Spawn ALL agents IN BACKGROUND in a SINGLE message
// Use run_in_background: true so agents work concurrently
Task({
  prompt: "Research requirements, analyze codebase patterns, store findings in memory",
  subagent_type: "researcher",
  description: "Research phase",
  run_in_background: true  // ← CRITICAL: Run in background
})
Task({
  prompt: "Design architecture based on research. Document decisions.",
  subagent_type: "system-architect",
  description: "Architecture phase",
  run_in_background: true
})
Task({
  prompt: "Implement the solution following the design. Write clean code.",
  subagent_type: "coder",
  description: "Implementation phase",
  run_in_background: true
})
Task({
  prompt: "Write comprehensive tests for the implementation.",
  subagent_type: "tester",
  description: "Testing phase",
  run_in_background: true
})
Task({
  prompt: "Review code quality, security, and best practices.",
  subagent_type: "reviewer",
  description: "Review phase",
  run_in_background: true
})

// STEP 3: WAIT - Tell user agents are working, then STOP
// Say: "I've spawned 5 agents to work on this in parallel. They'll report back when done."
// DO NOT check status repeatedly. Just wait for user or agent responses.
```
```
**File:** v3/@claude-flow/cli/CLAUDE.md (L126-158)
```markdown
### ⏸️ CRITICAL: Spawn and Wait Pattern

**After spawning background agents:**

1. **TELL USER** - "I've spawned X agents working in parallel on: [list tasks]"
2. **STOP** - Do not continue with more tool calls
3. **WAIT** - Let the background agents complete their work
4. **RESPOND** - When agents return results, review and synthesize

**Example response after spawning:**
```
I've launched 5 concurrent agents to work on this:
- 🔍 Researcher: Analyzing requirements and codebase
- 🏗️ Architect: Designing the implementation approach
- 💻 Coder: Implementing the solution
- 🧪 Tester: Writing tests
- 👀 Reviewer: Code review and security check

They're working in parallel. I'll synthesize their results when they complete.
```

### 🚫 DO NOT:
- Continuously check swarm status
- Poll TaskOutput repeatedly
- Add more tool calls after spawning
- Ask "should I check on the agents?"

### ✅ DO:
- Spawn all agents in ONE message
- Tell user what's happening
- Wait for agent results to arrive
- Synthesize results when they return

```
**File:** v3/@claude-flow/cli/CLAUDE.md (L163-187)
```markdown
# 1. Search memory for relevant patterns from past successes
Bash("npx @claude-flow/cli@latest memory search --query '[task keywords]' --namespace patterns")

# 2. Check if similar task was done before
Bash("npx @claude-flow/cli@latest memory search --query '[task type]' --namespace tasks")

# 3. Load learned optimizations
Bash("npx @claude-flow/cli@latest hooks route --task '[task description]'")
```

### After Completing Any Task Successfully
```bash
# 1. Store successful pattern for future reference
Bash("npx @claude-flow/cli@latest memory store --namespace patterns --key '[pattern-name]' --value '[what worked]'")

# 2. Train neural patterns on the successful approach
Bash("npx @claude-flow/cli@latest hooks post-edit --file '[main-file]' --train-neural true")

# 3. Record task completion with metrics
Bash("npx @claude-flow/cli@latest hooks post-task --task-id '[id]' --success true --store-results true")

# 4. Trigger optimization worker if performance-related
Bash("npx @claude-flow/cli@latest hooks worker dispatch --trigger optimize")
```

```
**File:** v3/@claude-flow/cli/CLAUDE.md (L190-206)
```markdown
| Trigger | Worker | When to Use |
|---------|--------|-------------|
| After major refactor | `optimize` | Performance optimization |
| After adding features | `testgaps` | Find missing test coverage |
| After security changes | `audit` | Security analysis |
| After API changes | `document` | Update documentation |
| Every 5+ file changes | `map` | Update codebase map |
| Complex debugging | `deepdive` | Deep code analysis |

### Memory-Enhanced Development

**ALWAYS check memory before:**
- Starting a new feature (search for similar implementations)
- Debugging an issue (search for past solutions)
- Refactoring code (search for learned patterns)
- Performance work (search for optimization strategies)

```
**File:** v3/@claude-flow/cli/CLAUDE.md (L213-224)
```markdown
### 📋 Agent Routing (Anti-Drift)

| Code | Task | Agents |
|------|------|--------|
| 1 | Bug Fix | coordinator, researcher, coder, tester |
| 3 | Feature | coordinator, architect, coder, tester, reviewer |
| 5 | Refactor | coordinator, architect, coder, reviewer |
| 7 | Performance | coordinator, perf-engineer, coder |
| 9 | Security | coordinator, security-architect, auditor |
| 11 | Docs | researcher, api-docs |

**Codes 1-9: hierarchical/specialized (anti-drift). Code 11: mesh/balanced**
```
**File:** v3/@claude-flow/cli/CLAUDE.md (L271-280)
```markdown
## Project Config (Anti-Drift Defaults)

- **Topology**: hierarchical (prevents drift)
- **Max Agents**: 8 (smaller = less drift)
- **Strategy**: specialized (clear roles)
- **Consensus**: raft
- **Memory**: hybrid
- **HNSW**: Enabled
- **Neural**: Enabled

```
**File:** v3/@claude-flow/cli/CLAUDE.md (L380-412)
```markdown
## 🪝 V3 Hooks System (27 Hooks + 12 Workers)

### All Available Hooks

| Hook | Description | Key Options |
|------|-------------|-------------|
| `pre-edit` | Get context before editing files | `--file`, `--operation` |
| `post-edit` | Record editing outcome for learning | `--file`, `--success`, `--train-neural` |
| `pre-command` | Assess risk before commands | `--command`, `--validate-safety` |
| `post-command` | Record command execution outcome | `--command`, `--track-metrics` |
| `pre-task` | Record task start, get agent suggestions | `--description`, `--coordinate-swarm` |
| `post-task` | Record task completion for learning | `--task-id`, `--success`, `--store-results` |
| `session-start` | Start/restore session (v2 compat) | `--session-id`, `--auto-configure` |
| `session-end` | End session and persist state | `--generate-summary`, `--export-metrics` |
| `session-restore` | Restore a previous session | `--session-id`, `--latest` |
| `route` | Route task to optimal agent | `--task`, `--context`, `--top-k` |
| `route-task` | (v2 compat) Alias for route | `--task`, `--auto-swarm` |
| `explain` | Explain routing decision | `--topic`, `--detailed` |
| `pretrain` | Bootstrap intelligence from repo | `--model-type`, `--epochs` |
| `build-agents` | Generate optimized agent configs | `--agent-types`, `--focus` |
| `metrics` | View learning metrics dashboard | `--v3-dashboard`, `--format` |
| `transfer` | Transfer patterns via IPFS registry | `store`, `from-project` |
| `list` | List all registered hooks | `--format` |
| `intelligence` | RuVector intelligence system | `trajectory-*`, `pattern-*`, `stats` |
| `worker` | Background worker management | `list`, `dispatch`, `status`, `detect` |
| `progress` | Check V3 implementation progress | `--detailed`, `--format` |
| `statusline` | Generate dynamic statusline | `--json`, `--compact`, `--no-color` |
| `coverage-route` | Route based on test coverage gaps | `--task`, `--path` |
| `coverage-suggest` | Suggest coverage improvements | `--path` |
| `coverage-gaps` | List coverage gaps with priorities | `--format`, `--limit` |
| `pre-bash` | (v2 compat) Alias for pre-command | Same as pre-command |
| `post-bash` | (v2 compat) Alias for post-command | Same as post-command |

```
**File:** v3/@claude-flow/cli/CLAUDE.md (L455-463)
```markdown

# Coverage-aware routing
npx @claude-flow/cli@latest hooks coverage-gaps --format table
npx @claude-flow/cli@latest hooks coverage-route --task "[task]"

# Statusline (for Claude Code integration)
npx @claude-flow/cli@latest hooks statusline
npx @claude-flow/cli@latest hooks statusline --json
```
```
**File:** v3/@claude-flow/cli/CLAUDE.md (L544-553)
```markdown
```

### Session Persistence (Cross-Conversation Learning)
```bash
# At session start - restore previous context
Bash("npx @claude-flow/cli@latest session restore --latest")

# At session end - persist learned patterns
Bash("npx @claude-flow/cli@latest hooks session-end --generate-summary true --persist-state true --export-metrics true")
```
```
**File:** v3/@claude-flow/cli/CLAUDE.md (L590-616)
```markdown

Run `npx @claude-flow/cli@latest doctor` to check:
- Node.js version (20+)
- npm version (9+)
- Git installation
- Config file validity
- Daemon status
- Memory database
- API keys
- MCP servers
- Disk space
- TypeScript installation

## 🚀 Quick Setup

```bash
# Add MCP servers (auto-detects MCP mode when stdin is piped)
claude mcp add claude-flow -- npx -y @claude-flow/cli@latest
claude mcp add ruv-swarm -- npx -y ruv-swarm mcp start  # Optional
claude mcp add flow-nexus -- npx -y flow-nexus@latest mcp start  # Optional

# Start daemon
npx @claude-flow/cli@latest daemon start

# Run doctor
npx @claude-flow/cli@latest doctor --fix
```
```
**File:** v3/@claude-flow/cli/README.md (L28-29)
```markdown
> **Why Ruflo?** Claude Flow is now Ruflo — named by Ruv, who loves Rust, flow states, and building things that feel inevitable. The "Ru" is the Ruv. The "flo" is the flow. Underneath, WASM kernels written in Rust power the policy engine, embeddings, and proof system. 5,800 commits later, the alpha is over. This is v3.5.

```
**File:** v3/@claude-flow/cli/README.md (L154-162)
```markdown
# One-line install (recommended)
curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/claude-flow@main/scripts/install.sh | bash

# Or full setup with MCP + diagnostics
curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/claude-flow@main/scripts/install.sh | bash -s -- --full

# Or via npx
npx ruflo@alpha init --wizard
```
```
**File:** v3/@claude-flow/cli/README.md (L266-275)
```markdown

Smart routing skips expensive LLM calls when possible. Simple edits use WASM (free), medium tasks use cheaper models. This can extend your Claude Code usage by 250% or save significantly on direct API costs.

| Complexity | Handler | Speed |
|------------|---------|-------|
| Simple | Agent Booster (WASM) | <1ms |
| Medium | Haiku/Sonnet | ~500ms |
| Complex | Opus + Swarm | 2-5s |

</details>
```
**File:** v3/@claude-flow/cli/README.md (L365-393)
```markdown

**Why This Prevents Drift:**

| Setting | Anti-Drift Benefit |
|---------|-------------------|
| `hierarchical` | Coordinator validates each output against goal, catches divergence early |
| `maxAgents: 6-8` | Fewer agents = less coordination overhead, easier alignment |
| `specialized` | Clear boundaries - each agent knows exactly what to do, no overlap |
| `raft` consensus | Leader maintains authoritative state, no conflicting decisions |

**Additional Anti-Drift Measures:**

- Frequent checkpoints via `post-task` hooks
- Shared memory namespace for all agents
- Short task cycles with verification gates
- Hierarchical coordinator reviews all outputs

**Task → Agent Routing (Anti-Drift):**

| Code | Task Type | Recommended Agents |
|------|-----------|-------------------|
| 1 | Bug Fix | coordinator, researcher, coder, tester |
| 3 | Feature | coordinator, architect, coder, tester, reviewer |
| 5 | Refactor | coordinator, architect, coder, reviewer |
| 7 | Performance | coordinator, perf-engineer, coder |
| 9 | Security | coordinator, security-architect, auditor |
| 11 | Memory | coordinator, memory-specialist, perf-engineer |

</details>
```
**File:** v3/@claude-flow/cli/README.md (L546-574)
```markdown
### Dual-Mode Integration (Claude Code + Codex)

Run Claude Code for interactive development and spawn headless Codex workers for parallel background tasks:

```
┌─────────────────────────────────────────────────────────────────┐
│  CLAUDE CODE (interactive)  ←→  CODEX WORKERS (headless)        │
│  - Main conversation         - Parallel background execution    │
│  - Complex reasoning         - Bulk code generation            │
│  - Architecture decisions    - Test execution                   │
│  - Final integration         - File processing                  │
└─────────────────────────────────────────────────────────────────┘
```

```bash
# Spawn parallel Codex workers from Claude Code
claude -p "Analyze src/auth/ for security issues" --session-id "task-1" &
claude -p "Write unit tests for src/api/" --session-id "task-2" &
claude -p "Optimize database queries in src/db/" --session-id "task-3" &
wait  # Wait for all to complete
```

| Dual-Mode Feature | Benefit |
|-------------------|---------|
| Parallel Execution | 4-8x faster for bulk tasks |
| Cost Optimization | Route simple tasks to cheaper workers |
| Context Preservation | Shared memory across platforms |
| Best of Both | Interactive + batch processing |

```
**File:** v3/@claude-flow/cli/README.md (L649-658)
```markdown
### Vector Search Details

- **Embedding Dimensions**: 384
- **Search Algorithm**: HNSW (sub-millisecond)
- **Similarity Scoring**: 0-1 (higher = better)
  - Score > 0.7: Strong match, use pattern
  - Score 0.5-0.7: Partial match, adapt
  - Score < 0.5: Weak match, create new

</details>
```
**File:** v3/@claude-flow/cli/README.md (L746-749)
```markdown
| **Consensus Protocols** | ✅ 5 (Raft, BFT, etc.) | ⛔ | ⛔ | ⛔ | ⛔ |
| **Work Ownership** | ✅ Claims system | ⛔ | ⛔ | ⛔ | ⛔ |
| **Background Workers** | ✅ 12 auto-triggered | ⛔ | ⛔ | ⛔ | ⛔ |
| **Multi-Provider LLM** | ✅ 6 with failover | 2 | 3 | 2 | 1 |
```
**File:** CLAUDE.local.md (L28-29)
```markdown

`npx claude-flow@v3alpha doctor` checks: Node 20+, npm 9+, git, config, daemon, memory DB, API keys, MCP servers, disk space, TypeScript.
```
**File:** CLAUDE.local.md (L41-44)
```markdown
## Intelligence System (RuVector)

4-step pipeline: RETRIEVE (HNSW) → JUDGE (verdicts) → DISTILL (LoRA) → CONSOLIDATE (EWC++)

```
**File:** v3/@claude-flow/cli/src/services/agentic-flow-bridge.ts (L1-56)
```typescript
/**
 * agentic-flow v3 integration bridge
 *
 * Provides a single lazy-loading entry point for all agentic-flow v3
 * subpath exports. Every accessor returns `null` when agentic-flow is
 * not installed — callers never throw on missing optional dependency.
 *
 * @module agentic-flow-bridge
 */

// ---------------------------------------------------------------------------
// Cached module handles (Promise-based to prevent TOCTOU races)
// ---------------------------------------------------------------------------

let _reasoningBankP: Promise<typeof import('agentic-flow/reasoningbank') | null> | null = null;
let _routerP: Promise<typeof import('agentic-flow/router') | null> | null = null;
let _orchestrationP: Promise<typeof import('agentic-flow/orchestration') | null> | null = null;

// ---------------------------------------------------------------------------
// Public loaders
// ---------------------------------------------------------------------------

/**
 * Load the ReasoningBank module (4-step learning pipeline).
 * Returns null if agentic-flow is not installed.
 * Race-safe: concurrent callers share the same import Promise.
 */
export function getReasoningBank() {
  if (_reasoningBankP === null) {
    _reasoningBankP = import('agentic-flow/reasoningbank').catch(() => null);
  }
  return _reasoningBankP;
}

/**
 * Load the ModelRouter module (multi-provider LLM routing).
 * Returns null if agentic-flow is not installed.
 */
export function getRouter() {
  if (_routerP === null) {
    _routerP = import('agentic-flow/router').catch(() => null);
  }
  return _routerP;
}

/**
 * Load the Orchestration module (workflow engine).
 * Returns null if agentic-flow is not installed.
 */
export function getOrchestration() {
  if (_orchestrationP === null) {
    _orchestrationP = import('agentic-flow/orchestration').catch(() => null);
  }
  return _orchestrationP;
}

```
**File:** package.json (L2-6)
```json
  "name": "claude-flow",
  "version": "3.5.1",
  "description": "Ruflo - Enterprise AI agent orchestration for Claude Code. Deploy 60+ specialized agents in coordinated swarms with self-learning, fault-tolerant consensus, vector memory, and MCP integration",
  "main": "dist/index.js",
  "type": "module",
```
**File:** v3/implementation/planning/CLAUDE-FLOW-V3-MASTER-PLAN.md (L25-26)
```markdown
**Target Release**: v3.0.0 on 2026-06-01

```
**File:** v3/docs/CLAUDE-FLOW-VS-TEAMMATE-TOOL-COMPARISON.md (L8-18)
```markdown
## Executive Summary

A detailed analysis reveals **striking architectural similarities** between Claude Flow V3's swarm system and Claude Code's TeammateTool. The terminology differs, but the core concepts, data structures, and workflows are nearly identical.

| Similarity Score | 92% Overlap |
|------------------|-------------|
| Core Concepts | 95% match |
| Data Structures | 90% match |
| Workflow Patterns | 93% match |
| Terminology | 70% match (different words, same meaning) |

```

---

## Official / 2026 links

- [GitHub `ruvnet/ruflo`](https://github.com/ruvnet/ruflo) · [Issue #1335 (closed; v3.5.22+)](https://github.com/ruvnet/ruflo/issues/1335)
- [claude-flow PR #1365](https://github.com/ruvnet/claude-flow/pull/1365)
- [`research_overnight_stack_web/gap_wave2/findings_gap_opencode_ruflo_gastown.md`](research_overnight_stack_web/gap_wave2/findings_gap_opencode_ruflo_gastown.md)
