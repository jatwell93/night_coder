#attractor
# DeepWiki Q&A with Code Context for Repository: mikeyobrien/ralph-orchestrator
## Q1
I'm working on a autonomous agent scaffold so I can run agents at night and review work in the morning. Would ralph fit cleanly into any of the pieces I have thus far? 

### Answer
Yes, Ralph Orchestrator aligns well with your autonomous agent scaffold, primarily fitting your **Attractor (Orchestrator)** role while also providing built-in capabilities for **CXDB (Context & Trace Store)** and **Leash (Guardrails)**. It does not include DTU or LLM Judge components.

## Mapping Ralph to Your Scaffold

| Your Component                   | Ralph Equivalent                                    | Fit Assessment |
| -------------------------------- | --------------------------------------------------- | -------------- |
| **Attractor (Orchestrator)**     | `EventLoop` + hat-based coordination                | ✅ Strong fit   |
| **CXDB (Context & Trace Store)** | `.agent/scratchpad.md` + `.agent/events.jsonl`      | ✅ Built-in     |
| **Leash (Guardrails)**           | Safety limits (iterations, runtime, cost, failures) | ✅ Built-in     |
| **Digital Twin Universe (DTU)**  | Not present                                         | ❌ Missing      |
| **LLM Judge**                    | Not present                                         | ❌ Missing      |

## Why Ralph Fits Your Orchestrator Role

Ralph implements the **Ralph Wiggum technique** — autonomous task completion through continuous iteration with fresh context each cycle ralph-orchestrator:11-28 . The `EventLoop` coordinates execution through:

- **Event-driven handoffs** via JSONL events (`.agent/events.jsonl`) that enable multi-agent workflows ralph-orchestrator:69-70 
- **Hat-based architecture** where specialized personas coordinate through triggers/publishes ralph-orchestrator:68-69 
- **"Hatless Ralph"** as a constant coordinator that delegates to hats but always remains as fallback ralph-orchestrator:20-26 

## Built-in Context & Trace (CXDB)

Ralph provides persistent state without a separate database:
- **Scratchpad** (`.agent/scratchpad.md`) serves as shared memory across iterations ralph-orchestrator:513-518 
- **Event log** (`.agent/events.jsonl`) records every agent action and handoff for audit trails ralph-orchestrator:72-96 

## Built-in Guardrails (Leash)

Ralph includes multiple safety mechanisms that align with your Leash component ralph-orchestrator:99-147 :
- `max_iterations` (default: 100)
- `max_runtime_seconds` (default: 4h)
- `max_cost_usd` (user-defined)
- `max_consecutive_failures` (default: 5)
- Loop detection for repetitive outputs

## What's Missing

- **DTU**: Ralph has no in-memory service mocking; it relies on live CLI tools
- **LLM Judge**: No probabilistic evaluation; completion is binary via `LOOP_COMPLETE` promise ralph-orchestrator:141-142 

## Recommendation

Ralph is an excellent foundation for your **Attractor + CXDB + Leash** needs. Its event-driven architecture and safety mechanisms are production-ready for overnight runs. You would need to add:
1. DTU integration if you require service mocking
2. LLM Judge for probabilistic outcome evaluation

The hat system provides the structured phases (design → implement → test → refactor) you want, with 24+ presets for common patterns ralph-orchestrator:71-72 .

## Notes

- Ralph v2 simplified from v1 by cutting over-engineered features (web dashboard, SQLite, complex security) to focus on the core loop ralph-orchestrator:57-78 
- State persistence uses files rather than databases, aligning with the Ralph philosophy that "disk is state, git is memory" ralph-orchestrator:59-60 
- Per-hat backend configuration allows different AI models for different phases if needed ralph-orchestrator:432-450 

Wiki pages you might want to explore:
- [Overview (mikeyobrien/ralph-orchestrator)](/wiki/mikeyobrien/ralph-orchestrator#1)
- [Hat-Based Multi-Agent Architecture (mikeyobrien/ralph-orchestrator)](/wiki/mikeyobrien/ralph-orchestrator#3.2)
### Citations
**File:** docs/guide/overview.md (L11-28)
```markdown
### The Ralph Wiggum Technique

At its core, as [Geoffrey Huntley](https://ghuntley.com/ralph/) originally defined it: **"Ralph is a Bash loop."**

```bash
while :; do cat PROMPT.md | claude ; done
```

This simple yet powerful approach to AI orchestration is "deterministically bad in an undeterministic world" - it fails predictably but in ways you can address. The technique requires "faith and belief in eventual consistency," improving through iterative tuning.

The workflow is straightforward:

1. **Give the AI a task** via a prompt file (PROMPT.md)
2. **Let it iterate** continuously on the problem
3. **Monitor progress** through checkpoints and metrics
4. **Stop when complete** or when limits are reached

This approach leverages the AI's ability to self-correct and improve through multiple iterations, inverting typical AI workflows by defining success criteria upfront rather than directing step-by-step.
```
**File:** docs/guide/overview.md (L72-96)
```markdown
## How It Works

### 1. Initialization Phase

When you start Ralph Orchestrator, it:

- Validates the prompt file for security
- Detects available AI agents
- Sets up monitoring and metrics collection
- Creates working directories for checkpoints
- Initializes cost and token tracking

### 2. Iteration Loop

The main orchestration loop:

1. **Pre-flight checks**: Verify token/cost limits haven't been exceeded
2. **Context management**: Check if context window needs summarization
3. **Agent execution**: Run the selected AI agent with the prompt
4. **Response processing**: Capture and analyze the agent's output
5. **Metrics collection**: Track tokens, costs, and performance
6. **Progress evaluation**: Monitor progress towards objectives
7. **Checkpoint**: Save state at configured intervals
8. **Repeat**: Continue until task is complete or limits are reached

```
**File:** docs/guide/overview.md (L99-147)
```markdown
Multiple layers of protection ensure safe operation:

```
                                 🛡️ Five Safety Mechanisms

  ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
  │  Iteration Limit  │     │   Runtime Limit   │     │    Cost Limit     │
  │ (default: 100)    │     │   (default: 4h)   │     │   (default: $10)  │
  └───────────────────┘     └───────────────────┘     └───────────────────┘
            │                         │                         │
            │                         │                         │
            ∨                         ∨                         ∨
          ╔═══════════════════════════════════════════════════════╗
          ║                    SafetyGuard.check()                ║
          ╚═══════════════════════════════════════════════════════╝
            ∧                         ∧                         ∧
            │                         │                         │
            │                         │                         │
  ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
  │ Consecutive Fails │     │   Loop Detection  │     │ Completion Marker │
  │   (default: 5)    │     │   (90% similar)   │     │ [x] TASK_COMPLETE │
  └───────────────────┘     └───────────────────┘     └───────────────────┘
```

<details>
<summary>graph-easy source</summary>

```
graph { label: "🛡️ Five Safety Mechanisms"; flow: south; }
[ Iteration Limit (default: 100) ] -> [ SafetyGuard.check() ] { border: double; }
[ Runtime Limit (default: 4h) ] -> [ SafetyGuard.check() ]
[ Cost Limit (default: $10) ] -> [ SafetyGuard.check() ]
[ Consecutive Fails (default: 5) ] -> [ SafetyGuard.check() ]
[ Loop Detection (90% similar) ] -> [ SafetyGuard.check() ]
[ Completion Marker [x] TASK_COMPLETE ] -> [ SafetyGuard.check() ]
```

</details>

- **Input validation**: Sanitizes prompts to prevent injection attacks
- **Resource limits**: Enforces iteration, runtime, and cost boundaries
- **Completion markers**: Early exit when `- [x] TASK_COMPLETE` detected in prompt file
- **Completion promises**: Early exit when agent output contains a configured string (default: `LOOP_COMPLETE`)
- **Loop detection**: Stops when agent outputs are ≥90% similar to recent history
- **Consecutive failure limit**: Stops after repeated failures (default: 5)
- **Context overflow**: Automatically summarizes when approaching limits
- **Graceful shutdown**: Handles interrupts and saves state
- **Error recovery**: Retries with exponential backoff

```
**File:** docs/guide/overview.md (L513-518)
```markdown

```
**File:** README.md (L59-60)
```markdown
4. **Disk Is State, Git Is Memory** — Files are the handoff mechanism.
5. **Steer With Signals, Not Scripts** — Add signs, not scripts.
```
**File:** README.md (L68-70)
```markdown
- **Hat System** — Specialized Ralph personas with distinct behaviors
- **Event-Driven Coordination** — Hats communicate through typed events with glob pattern matching
- **Backpressure Enforcement** — Gates that reject incomplete work (tests, lint, typecheck)
```
**File:** README.md (L71-72)
```markdown
- **Presets Library** — 20+ pre-configured workflows for common development patterns
- **Interactive TUI** — Real-time terminal UI for monitoring Ralph's activity (experimental)
```
**File:** specs/event-loop/idea-honing.md (L20-26)
```markdown
- Single, irreplaceable "hatless Ralph" — the classic Ralph Wiggum technique
- Hatless Ralph is always present as the orchestrator/manager/scrum master
- Additional hats are optional extensions that Ralph can **delegate to**
- Users ADD hats, they don't REPLACE core Ralph
- Ralph coordinates; hats execute

**Key insight:** Ralph becomes the constant, the orchestrator. Hats become his team.
```
**File:** specs/v1-v2-feature-parity.spec.md (L57-78)
```markdown
### ❌ CUT — YAGNI / Over-Engineering

| v1 Feature | Location | Reason to Cut |
|------------|----------|---------------|
| **Web Dashboard** | `web/` (FastAPI, WebSocket, Chart.js) | Against Ralph philosophy. Watch terminal or `tail -f` logs. |
| **JWT Authentication** | `web/auth.py` | No web dashboard = no auth needed |
| **SQLite Database** | `web/database.py` | History lives in git commits |
| **ACP Protocol** | `adapters/acp*.py` | Over-abstracted. Just run CLI commands. |
| **QChat Adapter** | `adapters/qchat.py` | Deprecated in v1, don't port |
| **Fuzzy Loop Detection** | `safety.py` (rapidfuzz) | Agents self-correct. Consecutive failures sufficient. |
| **Context Optimization** | `context.py` | CLI tools manage their context. Not our job. |
| **Prompt Summarization** | `context.py` | Same as above |
| **Security Masking** | `security.py` | CLI tools (Claude) handle sensitive data |
| **Path Sanitization** | `security.py` | Agent sandboxing handles this |
| **Tool Call Tracking** | `output/base.py` | Agents report their own tool usage |
| **Per-Tool Pricing Tables** | `metrics.py` | CLI tools report costs. Don't duplicate. |
| **Async Execution Mode** | `adapters/base.py` | Single agent at a time. Sync is fine. |
| **MCP Server Inheritance** | `adapters/claude.py` | Claude handles via `--inherit-user-settings` |
| **Tool Allowlist/Denylist** | `adapters/claude.py` | Managed by CLI tools, not orchestrator |
| **Archive Prompts** | `orchestrator.py` | Git history provides this |
| **Rate Limiting** | `web/rate_limit.py` | No web API = no rate limiting |

```
**File:** docs/guide/configuration.md (L432-450)
```markdown
### Hat Backends

Each hat can specify its own backend:

```yaml
cli:
  backend: claude  # Default backend for Ralph

hats:
  - name: builder
    backend: gemini  # This hat uses Gemini
    triggers: ["build.task"]
    publishes: ["build.done"]
    
  - name: reviewer
    backend:
      type: kiro
      agent: codex  # Kiro with custom agent
    triggers: ["review.request"]
```

---

## Official / 2026 links

- [Ralph Orchestrator docs](https://mikeyobrien.github.io/ralph-orchestrator/) · [Overview](https://mikeyobrien.github.io/ralph-orchestrator/guide/overview/) · [FAQ (limits)](https://mikeyobrien.github.io/ralph-orchestrator/faq/)
- [ghuntley/how-to-ralph-wiggum](https://github.com/ghuntley/how-to-ralph-wiggum)
- [`research_overnight_stack_web/findings_orchestration_opencode_ralph_ruflo_flywheel.md`](research_overnight_stack_web/findings_orchestration_opencode_ralph_ruflo_flywheel.md)
