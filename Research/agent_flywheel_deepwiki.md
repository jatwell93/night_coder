Technical Report: Achieving Autonomous Agentic Workflows on a Budget
====================================================================

Executive Summary
-----------------

After analyzing the Agent Flywheel (ACFS) system, I must clarify a critical misconception: **Agent Flywheel itself does not eliminate the cost of Claude Code, Codex, and Gemini**. The system is designed to install and configure these expensive agent CLIs, not replace them. 

However, the **true value** of Agent Flywheel lies in its coordination infrastructure and workflow patterns, which can be adapted to work with your existing Cursor Pro and GitHub Copilot Pro setup at a fraction of the cost.

Core Agent Flywheel Components Most Valuable for Your Use Case
--------------------------------------------------------------

### 1\. **Named Tmux Manager (NTM)** - The Agent Cockpit

NTM is the orchestration layer that spawns, monitors, and coordinates multiple agent sessions in tmux. This is the cornerstone for "set it and forget it" workflows. 

**Value for overnight execution**: NTM allows you to spawn multiple isolated sessions, send commands programmatically, and monitor progress without active supervision. PLAN\_TO\_CREATE\_ACFS.md:244

### 2\. **MCP Agent Mail** - Coordination Fabric

This provides identity management, inbox/outbox messaging, and advisory file reservations (leases) to prevent agents from clobbering each other's work. AGENTS.md:216-223

**Critical for autonomous operation**: The file reservation system prevents your exact pain point - agents missing broader fixes because they're operating in isolation. Leases ensure agents coordinate file access. AGENTS.md:229-237

### 3\. **CASS (Coding Agent Session Search)** + CASS Memory (CM)

CASS indexes all agent session history for unified search, while CM transforms these sessions into procedural memory. README.md:788-790

**Value**: Reduces redundant work and helps agents learn from past sessions, improving autonomous decision-making quality.

### 4\. **Ultimate Bug Scanner (UBS)**

Automated bug scanning with guardrails that runs continuously. README.md:788

**Value for overnight runs**: Catches issues early without requiring your active monitoring, acting as an automated quality gate.

The Cost Reality: What Agent Flywheel Actually Installs
-------------------------------------------------------

Agent Flywheel sets up three AI coding agents that **still require paid API access**:

The system provides "vibe mode" aliases that bypass safety confirmations, but these still call the underlying paid APIs. Your $400-600/month cost estimate is accurate for professional usage of these services.

Proposed Architecture: Budget-Constrained Alternative ($80/month total)
-----------------------------------------------------------------------

### Budget Breakdown

*   **Cursor Pro**: $20/month (you have this)
    
*   **GitHub Copilot Pro**: $10/month (you have this)
    
*   **Additional AI budget**: $30/month (for API calls via Cursor/Copilot agents)
    
*   **VPS (Contabo Cloud VPS M)**: $20/month (16GB RAM, 6 vCPU cores) research\_vps\_pricing.mjs:1-88
    
*   **Total**: $80/month (within your $80 budget)
    

### Architecture Components

Implementation Strategy: Achieving Overnight Autonomous Execution
-----------------------------------------------------------------

### Phase 1: Infrastructure Setup (Week 1)

**Step 1: Provision VPS and Install ACFS Base**

Run the ACFS installer to get the foundation, but **skip the expensive agents**: 
You'll get the shell environment, dev tools, and coordination infrastructure without the agent CLIs.

**Step 2: Install the Dicklesworthstone Stack**

The full stack provides the coordination layer you need:
These tools are **free and open-source** - this is where Agent Flywheel's true value lies for your budget.

### Phase 2: Custom Agent Integration (Week 2)

**Strategy: Adapt Cursor/Copilot to Work with NTM**

Instead of using expensive agent CLIs, create wrapper scripts that:

1.  **Launch Cursor in headless mode via SSH** to your VPS
    
2.  **Use tmux sessions managed by NTM** for isolation
    
3.  **Implement the Agent Mail coordination patterns** manually via file locks and message queues
    
4.  **Log all activity to CASS** for session history
    

**Critical Configuration Pattern from ACFS:**

The system uses a manifest-driven approach where each tool has install commands and verification logic. 

Adapt this pattern for your custom agent wrappers.

### Phase 3: Coordination Layer Implementation (Week 3)

**Implement Simplified Agent Mail Patterns**

Agent Mail provides the key coordination primitives you need:

**Budget-friendly adaptation:**

*   Use filesystem-based locks instead of the full MCP server
    
*   Implement simple file reservation via flock or directory-based semaphores
    
*   Create a message queue using watched directories or SQLite
    
*   Store agent state in JSON files under ~/.acfs/coordination/
    

**Key Integration Points:**

The ACFS shell configuration provides the foundation: 

### Phase 4: Overnight Execution Patterns (Week 4)

**Pattern 1: Task Queue with NTM Orchestration**

1.  Define tasks in Beads format (included with Agent Mail installation)
    
2.  Create an orchestrator script that:
    
    *   Reads the task queue
        
    *   Spawns NTM sessions for each parallel task
        
    *   Monitors progress via log files
        
    *   Implements retry logic for failures
        
    *   Writes results back to the queue
        

**Pattern 2: File-Based Coordination**

```   
# Create a coordination directory structure    ~/.acfs/coordination/      ├── tasks/           # Pending work items      ├── in_progress/     # Active work with locks      ├── completed/       # Finished work      ├── failed/          
# Failed attempts      └── reservations/    # File locks by agent   
```

**Pattern 3: Checkpoint-Based Resumption**

Agent Flywheel uses checkpointing for idempotent installs: 

Adapt this pattern for your agent workflows - save state at each major step so agents can resume after failures.

Specific Recommendations for Reducing Intervention
--------------------------------------------------

### 1\. **Implement Pre-flight Validation**

ACFS includes extensive preflight checks: 

**Adaptation for agents:**

*   Validate context completeness before starting
    
*   Check all required files exist
    
*   Verify tool availability
    
*   Confirm no conflicting work is in progress
    

### 2\. **Use the ACFS Doctor Pattern for Health Monitoring**

The doctor command provides comprehensive health checks: 

Create an agent-doctor command that:

*   Verifies all agent processes are healthy
    
*   Checks coordination lock states
    
*   Validates session logs for errors
    
*   Reports stuck agents
    

### 3\. **Implement Automatic Bug Scanning**

UBS runs with "easy-mode" guardrails: acfs.manifest.yaml:619-641

This catches issues automatically, reducing the need for you to monitor for obvious mistakes.

### 4\. **Leverage AGENTS.md Discipline**

ACFS enforces strict rules through AGENTS.md: 

**Key rules to implement:**

*   Never delete files without explicit approval
    
*   Prefer safe operations with backups
    
*   Document all destructive actions
    
*   Implement audit trails
    

This discipline is **more important than the agent CLI** for preventing the "skipped broader fix" problem you experience.

### 5\. **Session Completion Protocol**

ACFS mandates a completion checklist: AGENTS.md:286-310

**Adaptation:**

*   Every agent session must complete a shutdown checklist
    
*   Push all work to remote before ending
    
*   Update task status in your tracking system
    
*   Generate a completion report
    

Alternative Tools and Frameworks
--------------------------------

### Open-Source Coordination Tools

1.  **Temporal.io** (Community Edition - Free)
    
    *   Workflow orchestration with retries and timeouts
        
    *   Better than NTM for complex DAGs
        
    *   Self-hostable on your $20 VPS
        
2.  **n8n** (Self-hosted - Free)
    
    *   Visual workflow automation
        
    *   Can orchestrate agent sequences
        
    *   Includes error handling and monitoring
        
3.  **Langflow** (Open Source)
    
    *   Visual LLM application builder
        
    *   Can work with local models or API calls
        
    *   Good for prototyping agent workflows
        
4.  **Autogen** (Microsoft - Open Source)
    
    *   Multi-agent conversation framework
        
    *   Works with any LLM API
        
    *   Better coordination primitives than manual scripting
        

### Lower-Cost Agent Options

1.  **Aider** (Open Source)
    
    *   AI pair programming in the terminal
        
    *   Works with any OpenAI-compatible API
        
    *   Can use Cursor's API endpoint
        
    *   **Cost**: $0 (uses your existing API keys)
        
2.  **GPT-Engineer** (Open Source)
    
    *   Autonomous coding agent
        
    *   Supports multiple models including cheaper ones
        
    *   **Cost**: Pay per API call (can be <$10/month for light use)
        
3.  **Local Models via Ollama**
    
    *   Run Llama 3, CodeLlama, Mistral locally
        
    *   **Cost**: $0 (uses VPS compute only)
        
    *   Quality is lower but useful for routine tasks
        

Proposed Overnight Execution Architecture
-----------------------------------------

### The Complete Stack

| Service | Provider/Tool       | Specs/Details               | Cost      |
| ------- | ------------------- | --------------------------- | --------- |
| VPS     | Contabo Cloud VPS M | 16GB RAM, 6 vCPU, 400GB SSD | $20/month |

| Service            | Cost      |
| ------------------ | --------- |
| Cursor Pro         | $20/month |
| GitHub Copilot Pro | $10/month |
| API Credits        | $30/month |
- **ntm** – Session orchestration
- **agent_mail** – Coordination layer (simplified)
- **ubs** – Bug scanning
- **cass** – Session history
- **beads_viewer** – Task management
- **aider** – Free coding agent
- **tmux** – Session management
- **temporal** – Workflow engine (optional)

**Total:** $80/month
### Overnight Workflow Example

**Before Sleep (Planning Phase - 15 minutes):**

1.  Create task breakdown in Beads format
    
2.  Define acceptance criteria for each task
    
3.  Set up file reservations for parallel work
    
4.  Start orchestrator with ntm spawn project --parallel=3
    
5.  Verify agents started successfully
    
6.  Review initial output for ~5 minutes to catch setup issues
    

**During Sleep (Autonomous Phase - 8 hours):**

1.  Agents work independently in tmux sessions
    
2.  Coordination layer prevents conflicts via file locks
    
3.  UBS scans output continuously
    
4.  Progress logged to CASS
    
5.  Failed tasks automatically retry (configurable)
    
6.  Checkpoint state saved every 30 minutes
    

**After Waking (Review Phase - 30 minutes):**

1.  Run agent-doctor to see overall health
    
2.  Review completion reports from each agent
    
3.  Check UBS scan results for issues
    
4.  Use CASS to search session history for decisions made
    
5.  Merge completed work or address failures
    

Critical Success Factors
------------------------

### 1\. **Context Engineering is Paramount**

Your existing practice of using detailed AGENTS.md and OpenSpec is **the right approach**. The coordination infrastructure just amplifies this.

**Enhancement**: Use CASS Memory to build procedural memory: README.md:789

This transforms session history into reusable patterns that improve future autonomous runs.

### 2\. **Start with Short Runs, Build Confidence**

Don't jump straight to overnight execution:

*   Week 1: 30-minute unattended runs
    
*   Week 2: 2-hour runs
    
*   Week 3: 4-hour runs
    
*   Week 4: Overnight runs
    

Use the checkpoint/resume pattern to recover from failures gracefully.

### 3\. **Invest in Observability**

ACFS includes comprehensive logging: 

**Your implementation needs:**

*   Real-time log aggregation (tail multiple tmux sessions)
    
*   Error pattern detection
    
*   Notification on critical failures (Discord webhook, email, SMS)
    
*   Dashboard showing agent status
    

### 4\. **Embrace the Beads Workflow**

Agent Mail includes Beads tools for task management: 

This provides the task visibility you need for planning without active monitoring.

Implementation Timeline
-----------------------

### Week 1: Foundation

*   Set up VPS with ACFS installer
    
*   Install Dicklesworthstone stack (free components only)
    
*   Configure tmux + NTM for session management
    
*   Test basic orchestration with shell scripts
    

### Week 2: Integration

*   Create Cursor/Copilot wrapper scripts
    
*   Implement file-based coordination
    
*   Set up CASS for session logging
    
*   Test 30-minute unattended runs
    

### Week 3: Refinement

*   Add UBS integration for quality gates
    
*   Implement checkpoint/resume logic
    
*   Create agent-doctor health monitoring
    
*   Test 2-4 hour runs with recovery
    

### Week 4: Production

*   Add Beads task management
    
*   Implement notification system
    
*   Create completion report templates
    
*   Test first overnight run
    

### Week 5+: Optimization

*   Build procedural memory with CM
    
*   Add Temporal.io for complex workflows (optional)
    
*   Integrate Aider for additional agent capacity
    
*   Measure and reduce intervention rate
    

Cost Comparison
---------------

### Your Current Pain: Active Monitoring

*   **Time cost**: 4-6 hours/day watching agents = $150-300/day at $50/hour rate
    
*   **Opportunity cost**: Can't develop better prompts/context engineering
    
*   **Mental overhead**: Constant context switching
    

### Agent Flywheel Full Stack

*   **Monthly cost**: $400-600 for agent CLIs + $20-50 VPS = $420-650/month
    
*   **Time saved**: Significant, but expensive
    

### Proposed Budget Architecture

*   **Monthly cost**: $80/month (within your budget)
    
*   **Time saved**: Similar to full Agent Flywheel (80-90% reduction in monitoring)
    
*   **Trade-off**: More initial setup work (4 weeks), slightly lower agent quality vs Claude Code
    

**ROI Calculation:**

*   Investment: $80/month + 40 hours setup work (one-time)
    
*   Savings: 20-25 hours/week of monitoring time
    
*   Break-even: Week 2-3
    
*   Ongoing benefit: ~100 hours/month freed for higher-value work
    

Notes
-----

### Critical Clarification on Agent Flywheel

Agent Flywheel (ACFS) is **not a replacement** for expensive agent subscriptions - it's an installer and coordination framework that **assumes you have** those subscriptions. The system's value proposition is helping beginners go from zero to fully configured in 30 minutes. README.md:12-24

### The Real Value: Coordination Patterns, Not Agent CLIs

The Dicklesworthstone Stack provides the coordination infrastructure that makes autonomous execution possible. These 8 tools are **free and open-source**: PLAN\_TO\_CREATE\_ACFS.md:241-252

This is what you should extract and adapt, not the agent CLIs themselves.

### Why Your Current Approach Requires Intervention

The core issue isn't your tools (Cursor/Copilot) - it's the **lack of coordination infrastructure**. You're watching agents because:

1.  No file reservation system (agents can conflict)
    
2.  No session memory (agents repeat mistakes)
    
3.  No automated quality gates (you catch bugs manually)
    
4.  No orchestration layer (you're the orchestrator)
    

Adding NTM + simplified Agent Mail + UBS addresses all four issues within your budget.

### VPS Sizing Recommendation

The $20/month VPS (16GB RAM, 6 vCPU) is sufficient for: research\_vps\_pricing.mjs:1-154

*   3-4 parallel agent sessions
    
*   CASS indexing
    
*   UBS scanning
    
*   Coordination infrastructure
    
*   Session logs and checkpoints
    

If you need more parallel capacity, upgrade to Cloud VPS L (32GB) for ~$35/month still within your overall budget.

### Alternative to Full ACFS Install

You don't need the complete ACFS installation. The valuable components for your use case are:

1.  **NTM** - orchestration (free)
    
2.  **Agent Mail coordination patterns** - file locks and messaging (free to implement)
    
3.  **UBS** - bug scanning (free)
    
4.  **CASS + CM** - session history and memory (free)
    
5.  **Beads** - task management (free)
    

Skip the expensive agent CLI installations and adapt these patterns to your existing Cursor/Copilot setup.

### Success Metric

Your goal is to reduce intervention from "every 15-30 minutes" to "once every 4-8 hours". The proposed architecture should achieve:

*   **Week 1**: Intervention every 1-2 hours
    
*   **Week 2**: Intervention every 2-4 hours
    
*   **Week 4**: Intervention every 6-8 hours (overnight feasible)
    
*   **Week 8**: Intervention only for review/planning
    

The key is **incremental trust building** through reliable coordination infrastructure, not more expensive agents.

---

## Official / 2026 links

- [agent_flywheel_clawdbot_skills_and_integrations](https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations) (NTM + agent-mail skills)
- [mcp_agent_mail](https://github.com/Dicklesworthstone/mcp_agent_mail)
- [`research_overnight_stack_web/findings_orchestration_opencode_ralph_ruflo_flywheel.md`](research_overnight_stack_web/findings_orchestration_opencode_ralph_ruflo_flywheel.md)
