**Engineering Autonomous Sovereignty: A Technical Analysis of the Agentic Coding Flywheel and the Architecture of Unsupervised Development**
============================================================================================================================================

The evolution of software engineering in the era of large language models has shifted from code generation to agentic orchestration. The concept of the "Agentic Coding Flywheel," popularized by the platform at agent-flywheel.com, posits that the primary bottleneck in modern development is not the ability to write individual lines of code, but the coordination of multiple high-intelligence agents working in parallel across complex, multi-repo environments.1 This paradigm shift necessitates a robust infrastructure that transcends the capabilities of local IDE extensions like GitHub Copilot or Cursor. While these tools excel at real-time pair programming, they are inherently limited by the constraints of local hardware and the need for constant human supervision.1 Achieving a "plan-and-review" workflow, where agents execute autonomously overnight, requires a transition to persistent, server-side environments and the adoption of sophisticated coordination, memory, and safety tools.2

**Infrastructure Foundations: The Necessity of the Virtual Private Server**
---------------------------------------------------------------------------

The core architecture of a high-velocity agentic environment is built upon the Virtual Private Server (VPS).1 Modern agentic workflows are resource-intensive; each active agent session typically consumes approximately 2GB of RAM.1 Running a swarm of ten or more agents—a requirement for parallel progress across multiple projects—demands 48GB to 64GB of RAM, a capacity that exceeds standard consumer laptops.1 Beyond raw compute, the VPS offers 24/7 availability, allowing agents to perform long-running refactors, extensive testing, and iterative debugging cycles while the developer is offline.1

The Agent Flywheel ecosystem advocates for the use of providers like Contabo or OVH, which offer high-RAM configurations at flat monthly rates, avoiding the unpredictable hourly billing of hyper-scalers like AWS, GCP, or Azure.1 This infrastructure choice is critical for "vibe mode" development, where passwordless sudo and dangerous flags are enabled to maximize iteration speed in throwaway environments.1 The installation of this environment is typically managed via an idempotent bootstrapping system, such as the Agentic Coding Flywheel Setup (ACFS), which transforms a fresh Ubuntu instance into a fully configured development hub in under thirty minutes.7

**Infrastructure Component**

**Minimum Requirement**

**Recommended Specification**

**Rationale**

**Operating System**

Ubuntu 22.04 LTS

Ubuntu 25.10

Support for modern runtimes and kernel features.7

**CPU Cores**

4 vCPUs

8+ vCPUs

Parallel execution of agents and compilation tasks.8

**RAM**

4 GB

64 GB

Scaling from 1-2 agents to 10+ simultaneous agents.1

**Storage**

40 GB NVMe

100+ GB NVMe

Fast indexing of large repositories and project maps.8

**Network**

1 Gbps

10 Gbps

Low-latency API calls and multi-repo synchronization.4

The ACFS architecture relies on a single source of truth—the acfs.manifest.yaml—which defines the installation logic, category groupings, and verification commands for over thirty developer tools.7 This manifest-driven approach ensures environmental parity across team members, eliminating the "works on my machine" problem in multi-agent workflows.7 The system employs a TypeScript-based generator to produce category-specific shell scripts, including a "Doctor" utility that verifies the health of the entire stack.7 This rigorous setup is the prerequisite for the flywheel effect, providing the stable ground upon which agents can operate without manual intervention.

**Deconstructing the Agent Flywheel Stack: Coordination and Orchestration**
---------------------------------------------------------------------------

The magic of the Agent Flywheel is not found in any single AI model, but in the twenty interconnected tools that facilitate coordination, memory, and safety.5 The Named Tmux Manager (NTM) serves as the primary orchestration layer, transforming tmux into a multi-agent command center.5 NTM allows users to spawn Claude, Codex, and Gemini agents in named panes, broadcast prompts to agent types, and maintain persistent sessions that survive SSH disconnections.1

Effective coordination between these agents is managed by MCP Agent Mail, a system designed to act as "Gmail for agents".3 In a multi-agent environment, the primary risk is conflict—two agents editing the same file or misaligning on task priorities.5 MCP Agent Mail provides a threaded messaging layer and an advisory file reservation system.14 Agents use this tool to declare their intentions, search past conversations, and reserve files via SQLite-backed persistent storage, ensuring that the swarm operates as a cohesive unit rather than a collection of disjointed processes.5

**Flywheel Tool**

**Category**

**Core Capability**

**Impact on Autonomy**

**NTM**

Orchestration

Multi-agent tmux management and prompt broadcasting.5

Enables parallel execution across multiple projects.5

**Mail**

Coordination

Threaded messaging and file reservation system.14

Prevents edit conflicts in multi-agent swarms.5

**BV**

Task Tracking

PageRank-based issue prioritization and DAG analysis.14

Identifies critical paths to unblock autonomous work.3

**CASS**

Search

Sub-millisecond search across 11+ agent formats.12

Retreives past solutions to prevent repetitive errors.3

**CM**

Memory

Three-layer cognitive architecture (Episodic, Working, Procedural).14

Provides cross-session learning for persistent intelligence.5

**UBS**

Static Analysis

1,000+ pattern-based bug detection rules.5

Catches security issues and code smells before commit.3

Task prioritization is another critical component of the flywheel. The Beads system and its visual counterpart, the Beads Viewer (BV), apply graph theory and PageRank algorithms to prioritize tasks that unblock the most work.3 By visualizing task dependencies as a Directed Acyclic Graph (DAG), BV allows agents to navigate complex backlogs with a "critical path" understanding, ensuring that autonomous progress overnight is directed toward the most impactful goals.5

**Memory Systems and Cognitive Continuity**
-------------------------------------------

One of the most significant barriers to unsupervised agentic execution is the lack of persistent memory.14 Standard AI sessions are ephemeral; an agent loses context the moment a process ends. The Agent Flywheel addresses this through the Coding Agent Session Search (CASS) and the CM memory system.5 CASS provides a unified TUI for searching local history across Claude Code, Codex, Cursor, Gemini, and more, using Tantivy for full-text indexing.12

The CM system extends this by implementing the Autonomous Cognitive Entity (ACE) framework.12 This architecture divides agent memory into three distinct layers: episodic memory (records of past experiences and session histories), working memory (active context for the current task), and procedural memory (lessons learned and reusable skills).12 This structured memory allows an agent to "remember" that a specific library version caused a build failure in a previous session, preventing the agent from repeating the same mistake autonomously.5 The use of Thompson sampling within the Meta Skill platform further optimizes these memory systems by tracking the effectiveness of various agentic strategies over time.13

This cognitive continuity is essential for the "plan-and-review" workflow. When a developer provides a high-level plan, the memory system ensures that the agent has access to the "procedural" knowledge of the codebase—how things are built, where the secrets are stored, and what architectural patterns are preferred.5 This historical grounding reduces the need for the agent to ask clarifying questions, enabling it to push through implementation tasks independently.17

**Safety, Guards, and the "Two-Person Rule"**
---------------------------------------------

Autonomous execution introduces significant risks, particularly regarding destructive commands or security vulnerabilities.17 The Flywheel stack manages these risks through multiple layers of safety tools. The Destructive Command Guard (DCG) is a high-performance Rust binary that intercepts potentially catastrophic operations, such as rm -rf or git reset --hard, before they are executed.13 DCG uses SIMD-accelerated pattern matching to provide sub-millisecond protection without impacting development velocity.14

For higher-risk actions, the stack employs the Simultaneous Launch Button (SLB), which implements a "two-person rule" for AI agents.5 SLB classifies commands into four risk tiers: CRITICAL, DANGEROUS, CAUTION, and SAFE.5 Commands labeled as CRITICAL require cryptographic approval from a second, independent agent or a human supervisor before execution.5 This peer-review mechanism ensures that even if one agent proposes a risky shortcut, the system's structural safeguards prevent it from causing systemic damage.5

Further safety is provided by the Ultimate Bug Scanner (UBS), which serves as a meta-runner for language-specific analyzers.5 UBS integrates over 1,000 detection rules across eight languages, providing a consistent JSON interface that agents use to scan their own work before committing.3 This self-policing loop—where agents use tools like UBS to catch their own errors—is a primary driver of the reliability needed for overnight autonomy.3

**Economic Re-Engineering: The $60 Monthly Blueprint**
------------------------------------------------------

The current pricing of the Agent Flywheel platform is largely driven by high-tier, seat-based subscriptions to proprietary AI models, such as Claude Max and ChatGPT Pro, which can cost $200 per month each.1 To achieve comparable outcomes within a $60 budget, the architecture must pivot from seat-based subscriptions to an API-first, usage-based model.21

### **Strategic Infrastructure Allocation**

The first step in the $60 blueprint is rightsizing the infrastructure. While the Flywheel recommends 64GB of RAM for massive swarms, a single developer can maintain high productivity with 16GB to 32GB of RAM by utilizing more efficient orchestration.1 VPS providers such as Contabo or Hostinger offer 16GB RAM instances with NVMe storage for approximately $11 to $18 per month.8

**VPS Provider**

**Plan**

**RAM**

**vCPU**

**Monthly Cost**

**Efficiency Rating**

**Contabo**

Cloud VPS 2

16 GB

6

$11.27

Excellent (Price/Performance).9

**Hetzner**

CX33

8 GB

4

$6.51

Good for lightweight agents.9

**Hostinger**

KVM 4

16 GB

4

$17.99

High reliability and support.9

**Raff**

Basic

4 GB

2

$4.99

Best for US-based hobbyists.24

**HostWild**

Mid-Range

16 GB

6

$19.99

Strong 10 Gbps networking.11

By allocating approximately $15 for the VPS, the remaining $45 of the budget is dedicated to API credits. Using an aggregator like OpenRouter allows for the granular selection of models based on the specific task requirements.21

### **Model Tiering and Token Economics**

The "plan-and-review" workflow benefits from a multi-model strategy where high-reasoning models handle architecture and planning, while cost-efficient models handle implementation and debugging.21 The current state-of-the-art models for coding and reasoning, such as DeepSeek R1, GPT 5.3 (hypothesized equivalent to o1/o3-mini), and Claude 4.6 (hypothesized equivalent to 3.5 Sonnet), are all accessible via OpenRouter at highly competitive rates.25

DeepSeek R1, in particular, has disrupted the market by offering performance on par with OpenAI's o1 at a fraction of the cost—roughly $0.70 per 1 million input tokens.22 A $45 monthly credit allocation would allow for the processing of over 60 million input tokens, far exceeding the typical limits of a $200 per month subscription.22 Furthermore, the use of prompt caching for models like Claude 4.6 (Sonnet) can reduce the cost of repetitive context by up to 90%, making long-running autonomous sessions economically viable.4

**Model Role**

**Recommended Model**

**Pricing (per 1M In/Out)**

**Strategic Usage**

**Planning**

Claude 4.6 (Sonnet)

$3.00 / $15.00

High-level architecture and complex beads generation.27

**Reasoning**

GPT 5.3 (o3-mini)

$1.10 / $4.40

Logic verification, edge-case detection, and TDD prep.26

**Execution**

DeepSeek R1

$0.70 / $2.50

Massive code writing, refactoring, and documentation.22

**Debugging**

DeepSeek V3 / Qwen 3

$0.20 / $0.60

Iterative bug fixing and linter error resolution.21

This tiering approach ensures that the most expensive "intelligence" is only invoked when necessary, while the heavy lifting of code generation is handled by models that offer the best value-per-token.21

**Open-Source Alternatives: Aider, Plandex, and OpenHands**
-----------------------------------------------------------

Replicating the Flywheel's automation without the proprietary stack requires the integration of best-in-class open-source agents. Aider, Plandex, and OpenHands each offer unique strengths that, when combined, provide a comprehensive autonomous development environment.30

### **Aider: Git-Native Pair Programming and Watch Mode**

Aider is a terminal-based pair programming tool that differentiates itself through its tight integration with the Git workflow.4 It automatically creates descriptive commit messages for every change, ensuring a traceable history.4 Aider's "repository map" feature is a crucial architectural innovation; it uses ctags to build a concise map of the codebase's symbols and function signatures.4 This allows the agent to understand the broader context of the project without consuming the massive token volume required to load every file.4

For the "plan-and-review" workflow, Aider's --watch-files mode is transformative.36 In this mode, Aider monitors the codebase for special "AI!" comments.36 A developer can spend the evening writing high-level instructions as comments in the code, and Aider will autonomously process these tasks, implementing the code and running the associated tests.36 This allows for a seamless transition where the human "plans" in the IDE and the agent "executes" in the background terminal.36

### **Plandex: Large-Task Planning and Sandbox Safety**

Plandex is designed for tasks that are too large for simple pair-programming tools.10 It handles tasks that touch dozens of files and require complex, multi-step implementation plans.10 One of its standout features is the "diff review sandbox," where all AI-generated changes are accumulated separately from the project's source files.27 This allows the agent to iterate, run commands, and debug without leaving a "mess" in the working directory.10

Plandex's "Full Auto Mode" enables end-to-end autonomy, covering planning, implementation, command execution (for builds and tests), and automatic debugging.10 It utilizes tree-sitter for fast project map generation across thirty languages and supports a 2M token context window by loading only what is needed for each individual step.10 This "sliding context window" is critical for maintaining performance in million-line projects.27

### **OpenHands: The Platform for Scalable Agents**

OpenHands (formerly OpenDevin) focuses on being an open platform for cloud-based coding agents.41 It is built as a composable SDK, allowing developers to embed agentic capabilities into custom apps and workflows.41 OpenHands is particularly strong in multi-agent research and complex system engineering, as it supports sub-agent delegation and task decomposition.42 Its architecture is designed for scalability, capable of running thousands of agents in Docker or Kubernetes environments.41

**Feature**

**Aider**

**Plandex**

**OpenHands**

**Interface**

CLI / Terminal-focused.31

CLI / TUI with Sandbox.10

Web GUI / CLI / SDK.41

**Git Integration**

Native; auto-commits everything.33

Client-side; optional auto-commit.33

Integrated with GitHub App.42

**Context**

Repo maps (ctags-based).34

Tree-sitter maps; 2M window.10

Context Condenser.42

**Best For**

Fast, terminal-first edits.4

Complex, multi-file refactors.10

Large-scale automation.42

**Autonomy**

High (via watch/scripting).36

Very High (Full Auto Mode).37

Enterprise (Agent delegation).42

**Strategies for Unsupervised Execution and Reliability**
---------------------------------------------------------

Moving to an "overnight" autonomous workflow requires mechanisms that allow agents to self-correct and verify their work without human feedback. The primary strategy for this is the integration of Test-Driven Development (TDD) as the anchor for the agentic loop.44

### **The TDD Feedback Loop**

Reliable autonomy is predicated on the ability to define success programmatically.6 In a TDD-anchored workflow, the agent is tasked with writing or updating tests before implementing the solution.44 Tools like Aider can be configured with the --test-cmd and --auto-test flags, causing the agent to automatically run the test suite after every edit.47 If the tests fail, Aider treats the failure output as a new prompt, iteratively modifying the code until the tests pass.47

This approach can be codified in simple Bash scripts that orchestrate the "plan-and-review" cycle.46 A script like tdd.sh can feed the initial requirements to an LLM to generate code, run pytest, and if the tests fail, pass the traceback back to the LLM for a second attempt.46 This loop continues until success is achieved or a maximum number of iterations is reached, ensuring that the human reviewer wakes up to code that has already passed all functional requirements.6

### **The "Ralph Wiggum" Philosophy of Persistent Loops**

For more complex or open-ended tasks, the "Ralph Wiggum" loop offers a robust alternative to deterministic scripts.6 The core philosophy is simple: let the agent fail repeatedly until it succeeds.6 This is implemented as a Bash loop that intercepts the agent's exit code; if the agent attempts to stop without meeting certain success criteria (such as a specific completion string or a passing build), the loop re-feeds the original prompt and forces the agent to continue.6

This method, originally proposed by Geoffrey Huntley, has been refined into plugins like ralph-claude-code, which add tmux dashboards, rate limiting, and circuit breakers to manage costs and prevent runaway loops.6 The agent maintains context across these iterations by observing the modified files and git history from its previous attempts, effectively allowing it to "learn" from its own mistakes over several hours of autonomous work.6

### **Advanced Reasoning with LATS**

For the most difficult tasks, agents can utilize Language Agent Tree Search (LATS).49 LATS replaces standard reinforcement learning components with LLM calls to navigate a search tree of potential actions.49 It uses the Upper Confidence Bound (UCT) formula to balance exploration (trying new implementation strategies) with exploitation (refining existing successful paths).49 By writing unit tests to score each trajectory, LATS allows the agent to objectively evaluate multiple implementation paths and backpropagate the scores to the root of the task, ensuring that the final solution is the most logically sound.49

**Proposed Technical Architecture: The "Budget Flywheel"**
----------------------------------------------------------

To achieve Agent Flywheel-level automation on a $60 budget, a developer should implement the following architecture on a dedicated VPS.

### **1\. The Orchestration Layer: NTM and Tmux**

The foundation is a tmux-based environment managed by the open-source Named Tmux Manager (NTM).5 This allows for the creation of named sessions—for example, a "Plan" session for Plandex, an "Execute" session for Aider, and a "Monitor" session for UBS and static analysis tools.5 This separation of concerns prevents any single agent from overwhelming the context of the others.

### **2\. The Task and Memory Layer: CASS and Beads**

For task tracking, use the Beads format to log issues and dependencies in a local beads.jsonl file.15 This file acts as the persistent backlog that agents can read from and write to autonomously.5 Memory persistence is achieved through the Coding Agent Session Search (CASS) index, which should be configured to run as a background service on the VPS.12 By indexing every terminal session, CASS ensures that agents can retrieve successful solutions from previous overnight runs.3

### **3\. The Autonomous Execution Engine: Aider Scripting**

The heavy lifting of implementation is handled by Aider in a scripted loop.43 Using Aider's Python API or the --message-file flag, the developer can queue up a sequence of tasks.43 Each task should be executed with the --auto-test flag pointing to the project's test suite.47 This creates a self-healing loop where Aider works through the task list, fixes its own bugs, and commits only verified code.4

### **4\. The Safety Layer: DCG and UBS**

To protect the codebase, the Destructive Command Guard (DCG) and Ultimate Bug Scanner (UBS) must be integrated into the agent's workflow.5 DCG is installed as a pre-tool-use hook, while UBS is configured to run as a pre-commit hook or as part of the Aider --test-cmd.13 This ensures that any code generated autonomously is scanned for security vulnerabilities and code smells before it enters the git history.5

### **5\. Multi-Model Routing via OpenRouter**

Model costs are managed through OpenRouter's API, utilizing DeepSeek R1 for the majority of execution tasks and reserving Claude 4.6 (Sonnet) for complex planning phases.21 Prompt caching should be enabled in the Aider configuration to minimize the overhead of repeated codebase indexing.4

**Cost Category**

**Item**

**Monthly Allocation**

**Value Provided**

**Compute**

Contabo 16GB VPS

$12.00

24/7 agent environment and tmux persistence.9

**Logic**

DeepSeek R1 API Credits

$25.00

~35M input tokens for heavy coding and debugging.22

**Planning**

Claude 4.6 API Credits

$15.00

~5M input tokens for architecture and refinement.29

**Verification**

GPT 5.3 / o3-mini

$8.00

~2M tokens for logic review and edge-case detection.26

**Total**

**Agentic Sovereign Stack**

**$60.00**

**Autonomous overnight "Plan-and-Review" workflow.**

**Improving Reliability and Reducing Intervention**
---------------------------------------------------

The transition from a "pilot" role to a "reviewer" role is contingent upon the reduction of agent "thrashing"—the phenomenon where an agent makes repeated, unproductive changes.30

### **Hierarchical Planning and Beads Decomposition**

The primary cause of thrashing is a lack of granular planning.5 Agents should be required to decompose any complex feature into a set of "beads" before writing code.3 By breaking a 5,000-line feature into 300 granular sub-tasks (beads), the agent's search space for any single action is drastically reduced, leading to higher accuracy and fewer interventions.5 This decomposition should be performed by a high-reasoning model (Claude 4.6 or GPT 5.3) and reviewed by the human developer before the overnight execution begins.5

### **Automated Plan Revision (APR)**

Integrating an Automated Plan Reviser (APR) into the loop provides a second layer of defense.51 Before an implementation agent begins its work, an APR agent reviews the proposed plan against the project's architectural constraints and existing procedural memory.49 This iterative refinement—where one agent "plans" and another "critiques"—identifies potential failures before they consume execution tokens.5

### **Event-Driven Automation with WezTerm Automata**

For advanced users, monitoring agent state transitions in real-time can be achieved through WezTerm Automata (WA).5 WA observes terminal output and triggers custom automation based on specific patterns.5 For example, if WA detects that an agent has been stuck on the same linter error for three iterations, it can trigger a "context refresh" command or switch the model from DeepSeek R1 to a more capable reasoning model like GPT 5.3 to unblock the process.5

**Future Outlook: The Self-Evolving Living System**
---------------------------------------------------

The ultimate goal of this agentic stack is to transition from static software to "living systems" capable of self-guided adaptation.52 As agents are embedded more deeply into the production infrastructure, they can begin to reason over real-world data and usage patterns, evolving the codebase dynamically as requirements shift.17

This paradigm shift requires a move away from the traditional view of software as something that is "written and deployed" toward a model where software is "nurtured and guided".52 The tools developed within the Flywheel ecosystem—CASS for memory, Beads for prioritization, and SLB for safety—are the precursors to this new era of engineering.3 By mastering these tools on a modest $60 budget, developers can achieve levels of productivity that were previously unimaginable, reclaiming the hours spent on alert triage and active monitoring for higher-level creative and architectural work.2

The implementation of this autonomous sovereign stack represents a definitive step toward the agentic future. By combining the persistence of a VPS, the cognitive continuity of structured memory systems, and the rigorous verification of TDD-anchored loops, developers can build a self-reinforcing flywheel that spins faster with every task completed.2 The result is a 24/7 development swarm that executes with precision, learns from experience, and delivers complex, production-ready software with minimal human intervention.5

## Q&A
### Question
Could you please answer a few questions on the report?
"This approach can be codified in simple Bash scripts that orchestrate the "plan-and-review" cycle. A script like tdd.sh can feed the initial requirements to an LLM to generate code, run pytest, and if the tests fail, pass the traceback back to the LLM for a second attempt." Could you provide a quick example of this?

"One of its standout features is the "diff review sandbox," where all AI-generated changes are accumulated separately from the project's source files. This allows the agent to iterate, run commands, and debug without leaving a "mess" in the working directory." are there any examples where this is achieved in a repo/git/by a small amount of code? I think this is interesting but I'm leaning towards another tool than plandex but I like this feature

"For the most difficult tasks, agents can utilize Language Agent Tree Search (LATS). LATS replaces standard reinforcement learning components with LLM calls to navigate a search tree of potential actions. It uses the Upper Confidence Bound (UCT) formula to balance exploration (trying new implementation strategies) with exploitation (refining existing successful paths). By writing unit tests to score each trajectory, LATS allows the agent to objectively evaluate multiple implementation paths and backpropagate the scores to the root of the task, ensuring that the final solution is the most logically sound." How would something like this work? Now the process is plan, spec, tasks and then prompt the agent to complete the tasks. How would this work in implementation? Is it a part of the planning or executing (or both or niether)

"For example, if WA detects that an agent has been stuck on the same linter error for three iterations, it can trigger a "context refresh" command or switch the model from DeepSeek R1 to a more capable reasoning model like GPT 5.3 to unblock the process." How might this be implemented (big picture)? As a secondary example could this same process be used to switch models if say your api usage is up with one model so the calls return an error could it switch to the next?

### Answer
The transition to a "plan-and-review" workflow requires specific scripting techniques and structural choices to ensure agents can operate safely and effectively without constant supervision.

### 1. Bash Script Example for the TDD Loop (`tdd.sh`)

The following script demonstrates a basic "plan-and-review" loop using standard CLI tools. It feeds a test file to a model, runs the test, and uses any failure output to prompt a fix.


```bash
#!/usr/bin/env bash
# tdd.sh: Orchestrates an LLM to pass a specific test suite
set -euo pipefail
ATTEMPTS=5
TEST_FILE=$1
APP_FILE=$2

# 1. Initial generation
echo "Generating initial version of $APP_FILE..."
aider --message "Write a Python module to pass $TEST_FILE" "$APP_FILE" --yes

# 2. Iterative loop until success
for i in $(seq 1 $ATTEMPTS); do
    echo "Attempt $i: Running tests..."
    if pytest "$TEST_FILE" > test_output.log 2>&1; then
        echo "✅ Success! Tests passed."
        exit 0
    else
        echo "❌ Tests failed. Feeding error back to agent..."
        # Pass the failure log back as a correction prompt
        aider --message "The tests failed with this output: $(cat test_output.log). Please fix the errors." "$APP_FILE" --yes
    fi
done

echo "Failed to pass tests after $ATTEMPTS attempts."
exit 1
```

### 2. Git-Native Sandboxing (Worktree vs. Plandex)

You can replicate the "diff review sandbox" without specialized platforms by using **Git Worktrees**. A worktree allows you to have multiple branches checked out in different directories simultaneously while sharing the same `.git` database. This keeps AI-generated "mess" in a parallel directory that never touches your main codebase until you merge it.

A small script to achieve this isolation:

```bash
#!/bin/bash
# create-sandbox.sh <task-name>
TASK_NAME=$1
BRANCH_NAME="ai/$TASK_NAME"
SANDBOX_PATH="../sandboxes/$TASK_NAME"

# Create a new branch and checkout to a separate directory
git worktree add -b "$BRANCH_NAME" "$SANDBOX_PATH" main

echo "Sandbox created at $SANDBOX_PATH. Point your agent there."
cd "$SANDBOX_PATH" && aider  # Agent works in complete isolation
```

This is often preferred over `git stash` because it allows you to run tests and build processes in the sandbox directory without interrupting your work in the primary directory.

### 3. Language Agent Tree Search (LATS) in Practice

LATS unifies reasoning, planning, and acting into a single search algorithm. In the context of your "plan, spec, task" workflow, it acts as a **bridge between planning and execution**:

- **How it works:** Instead of following a single path (Task A → Task B), LATS generates multiple potential implementation paths (Expansion). It then uses a "Value Function"—typically a suite of unit tests—to score each path (Evaluation).
    
- **Implementation Role:** It is primarily an **execution strategy**. While your current workflow is linear, LATS allows the agent to "hallucinate" three different ways to solve a specific task, run tests for all three, and only commit the one that actually works based on the **Upper Confidence Bound (UCT)** formula:
    
    $$UCT = \frac{\text{value}}{\text{visits}} + c \sqrt{\frac{\ln(\text{parent.visits})}{\text{visits}}}$$
    
- **Outcome:** This ensures that the agent doesn't get stuck in a "local minimum" where a bad initial implementation choice makes subsequent tasks impossible.
    

### 4. Automated Error Detection and Model Switching

Implementing a system that reacts to repeated errors or API failures involves two distinct layers: pattern detection and routing.

#### Big Picture Implementation: Pattern Detection

Tooling like **WezTerm Automata (WA)** or custom tmux wrappers monitor the agent's stdout.

- **Logic:** A background script pipes the agent's terminal output to a parser (like `grep` or a lightweight Rust watcher).
    
- **Counter:** If the string "Linter Error: [Error Code]" appears 3 times in the last 100 lines of output, the script sends a `SIGINT` to the agent process and restarts it with a "Rescue Prompt" or a more capable model.
    

#### Model Switching for API Errors (LiteLLM)

For handling API limits (429 errors) or server failures (500 errors), the most efficient approach is using **LiteLLM** as a proxy. It allows you to define a "fallback list" in a simple YAML config:

```yaml
# litellm_config.yaml
model_list:
  - model_name: high-tier-coder
    litellm_params:
      model: deepseek/deepseek-r1
      api_key: os.environ/DEEPSEEK_API_KEY
  - model_name: high-tier-coder
    litellm_params:
      model: gpt-5.3-preview
      api_key: os.environ/OPENAI_API_KEY

# Automatic fallback if DeepSeek is rate-limited or fails
fallbacks: [{"deepseek/deepseek-r1": ["gpt-5.3-preview"]}]
```

By pointing your agent tools (Aider, Plandex, etc.) to the LiteLLM proxy address instead of direct API endpoints, the model switch happens transparently in the background without the agent ever knowing its provider changed.

### Question
Would this https://jykoh.com/search-agents https://github.com/kohjingyu/search-agents be examples that you could use to build your own Language Agent Tree Search (LATS)? Could you implement a lats.sh?

### Answer
Yes, the `search-agents` repository by Jing Yu Koh is an excellent practical reference for building your own **Language Agent Tree Search (LATS)**. While LATS is a specific academic framework, `search-agents` implements a structurally similar "best-first tree search" that explicitly performs exploration and multi-step planning using environmental feedback.

### Using `search-agents` as a Blueprint for LATS

The `search-agents` implementation is highly relevant because it modularizes the core components required for LATS:

- **Tree Search for Planning:** It moves away from linear prompt trajectories to explore multiple potential actions at each step.
    
- **Value Function:** It uses a high-reasoning model (like GPT-4o) to score trajectories and decide which branch to follow.
    
- **Search Hyperparameters:** It includes configurable logic for `max_depth` (how many steps to plan), `branching_factor` (how many alternative actions to generate), and `vf_budget` (the total number of evaluations allowed).
    
### Implementing `lats.sh`

A full Language Agent Tree Search requires four steps: **Select, Expand, Reflect + Evaluate, and Backpropagate**. Below is a simplified implementation of `lats.sh` using Bash and Aider. This script executes a "Beam Search" style tree search, which is the most common practical derivative of LATS for coding tasks.

```bash
#!/usr/bin/env bash
# lats.sh: A simplified Language Agent Tree Search for coding tasks
set -euo pipefail

TASK=$1
BRANCHES=3     # Expansion factor (Number of alternative paths to try)
MAX_DEPTH=3    # Search depth
BEST_SCORE=0
CURRENT_DIR=$(pwd)

# Function to evaluate a branch using environment feedback (tests)
evaluate_branch() {
    local branch_id=$1
    echo "Evaluating Branch $branch_id..."
    
    # Run tests and count passes
    if pytest > test_results.log 2>&1; then
        echo 10  # Perfect score for passing tests
    else
        # Extract number of passing tests vs total as a score
        local passed=$(grep -oP '\d+(?= passed)' test_results.log |

| echo 0)
        local failed=$(grep -oP '\d+(?= failed)' test_results.log |

| echo 1)
        echo "$passed" # Simple score based on progress
    fi
}

# 1. Initial State
mkdir -p.lats_search
echo "$TASK" >.lats_search/root_task.txt

# 2. Search Loop
for depth in $(seq 1 $MAX_DEPTH); do
    echo "--- Search Depth $depth ---"
    declare -A scores
    
    # EXPAND: Generate alternative implementation paths
    for b in $(seq 1 $BRANCHES); do
        local branch_path=".lats_search/depth_${depth}_branch_${b}"
        cp -r "$CURRENT_DIR" "$branch_path"
        
        pushd "$branch_path" > /dev/null
        # Use Aider to implement one variation of the plan
        aider --message "Try implementation approach $b for: $(cat../root_task.txt). Focus on passing the tests." --yes
        
        # EVALUATE: Get feedback from the environment
        scores[$b]=$(evaluate_branch $b)
        popd > /dev/null
    done
    
    # SELECT: Find the branch with the highest score (Backpropagation/Selection)
    winner=1
    high_score=0
    for b in "${!scores[@]}"; do
        if [ "${scores[$b]}" -gt "$high_score" ]; then
            high_score=${scores[$b]}
            winner=$b
        fi
    done
    
    echo "Branch $winner selected with score $high_score. Promoting to main codebase."
    
    # Apply the winning branch back to the main directory
    cp -r.lats_search/depth_${depth}_branch_${winner}/* "$CURRENT_DIR/"
    
    if [ "$high_score" -eq 10 ]; then
        echo "✅ Task successfully solved at depth $depth."
        exit 0
    fi
done

echo "Maximum search depth reached without a perfect solution."
exit 1
```

### Key Differences in Implementation

While `search-agents` is optimized for web navigation (using multimodal models for the value function), a coding-focused `lats.sh` relies on **Unit Tests** as the primary "Value Function". This objective feedback allows the agent to navigate the decision tree with much higher reliability than models that only use internal reasoning. By writing tests before code (TDD), your LATS implementation can score its own trajectories and discard paths that lead to regressions.

#### **Works cited**

1.  Agent Flywheel - AI Agents Coding For You, accessed February 15, 2026, [https://agent-flywheel.com/](https://agent-flywheel.com/)
    
2.  Jeff Emanuel Dicklesworthstone - GitHub, accessed February 15, 2026, [https://github.com/Dicklesworthstone](https://github.com/Dicklesworthstone)
    
3.  Jeffrey Emanuel: Agentic Coding Tooling, AI Infrastructure & Markets, accessed February 15, 2026, [https://jeffreyemanuel.com/](https://jeffreyemanuel.com/)
    
4.  Getting Started with Aider: AI-Powered Coding from the Terminal - OpenReplay Blog, accessed February 15, 2026, [https://blog.openreplay.com/getting-started-aider-ai-coding-terminal/](https://blog.openreplay.com/getting-started-aider-ai-coding-terminal/)
    
5.  Unheard-of Velocity in Complex Software - Agent Flywheel, accessed February 15, 2026, [https://agent-flywheel.com/flywheel](https://agent-flywheel.com/flywheel)
    
6.  Ralph Wiggum: Autonomous Loops for Claude Code - Emergent Minds | paddo.dev, accessed February 15, 2026, [https://paddo.dev/blog/ralph-wiggum-autonomous-loops/](https://paddo.dev/blog/ralph-wiggum-autonomous-loops/)
    
7.  Dicklesworthstone/agentic\_coding\_flywheel\_setup: System ... - GitHub, accessed February 15, 2026, [https://github.com/Dicklesworthstone/agentic\_coding\_flywheel\_setup](https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup)
    
8.  10 Best Cheap VPS Hosting Providers Compared \[2026\], accessed February 15, 2026, [https://blog.ishosting.com/en/best-cheap-vps-hosting](https://blog.ishosting.com/en/best-cheap-vps-hosting)
    
9.  VPS Price Comparison - GetDeploying, accessed February 15, 2026, [https://getdeploying.com/reference/compute-prices](https://getdeploying.com/reference/compute-prices)
    
10.  Open source AI coding agent. Designed for large projects and real world tasks. - GitHub, accessed February 15, 2026, [https://github.com/plandex-ai/plandex](https://github.com/plandex-ai/plandex)
    
11.  Best & Cheap VPS Provider in 2026 - Programming Insider, accessed February 15, 2026, [https://programminginsider.com/best-cheap-vps-provider-in-2026/](https://programminginsider.com/best-cheap-vps-provider-in-2026/)
    
12.  Projects | Jeffrey Emanuel, accessed February 15, 2026, [https://jeffreyemanuel.com/projects](https://jeffreyemanuel.com/projects)
    
13.  Projects | Jeffrey Emanuel, accessed February 15, 2026, [https://www.jeffreyemanuel.com/projects](https://www.jeffreyemanuel.com/projects)
    
14.  The Agentic Coding Flywheel - TL;DR - Jeffrey Emanuel, accessed February 15, 2026, [https://jeffreyemanuel.com/tldr](https://jeffreyemanuel.com/tldr)
    
15.  The Agentic Coding Flywheel - TL;DR, accessed February 15, 2026, [https://agent-flywheel.com/tldr](https://agent-flywheel.com/tldr)
    
16.  7 Tips to Build Self-Improving AI Agents with Feedback Loops | Datagrid, accessed February 15, 2026, [https://datagrid.com/blog/7-tips-build-self-improving-ai-agents-feedback-loops](https://datagrid.com/blog/7-tips-build-self-improving-ai-agents-feedback-loops)
    
17.  How Do Autonomous AI Agents Transform Development Workflows | Augment Code, accessed February 15, 2026, [https://www.augmentcode.com/learn/how-do-autonomous-ai-agents-transform-development-workflows](https://www.augmentcode.com/learn/how-do-autonomous-ai-agents-transform-development-workflows)
    
18.  I ran Claude Code in a self-learning loop until it successfully translated our entire Python repo to TypeScript : r/ClaudeAI - Reddit, accessed February 15, 2026, [https://www.reddit.com/r/ClaudeAI/comments/1pez28a/i\_ran\_claude\_code\_in\_a\_selflearning\_loop\_until\_it/](https://www.reddit.com/r/ClaudeAI/comments/1pez28a/i_ran_claude_code_in_a_selflearning_loop_until_it/)
    
19.  agentic\_coding\_flywheel\_setup/AGENTS.md at main - GitHub, accessed February 15, 2026, [https://github.com/Dicklesworthstone/agentic\_coding\_flywheel\_setup/blob/main/AGENTS.md](https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup/blob/main/AGENTS.md)
    
20.  Releases · Dicklesworthstone/agentic\_coding\_flywheel\_setup - GitHub, accessed February 15, 2026, [https://github.com/Dicklesworthstone/agentic\_coding\_flywheel\_setup/releases](https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup/releases)
    
21.  My Quest for the Most Cost-Effective AI Tools, accessed February 15, 2026, [https://tedawf.com/blog/ted-tries-ai-tools](https://tedawf.com/blog/ted-tries-ai-tools)
    
22.  Which API is more cost-effective? Direct DeepSeek API, OpenRouter, or Chutes? - Reddit, accessed February 15, 2026, [https://www.reddit.com/r/SillyTavernAI/comments/1lx5vbp/which\_api\_is\_more\_costeffective\_direct\_deepseek/](https://www.reddit.com/r/SillyTavernAI/comments/1lx5vbp/which_api_is_more_costeffective_direct_deepseek/)
    
23.  Best Local LLMs for 16GB VRAM: Practical Performance Testing 2026, accessed February 15, 2026, [https://localllm.in/blog/best-local-llms-16gb-vram](https://localllm.in/blog/best-local-llms-16gb-vram)
    
24.  Top 3 Cheap VPS Providers in 2025 (That I've Actually Used) - DEV Community, accessed February 15, 2026, [https://dev.to/sst21/top-3-cheap-vps-providers-in-2025-that-ive-actually-used-1b2k](https://dev.to/sst21/top-3-cheap-vps-providers-in-2025-that-ive-actually-used-1b2k)
    
25.  Models - OpenRouter, accessed February 15, 2026, [https://openrouter.ai/models](https://openrouter.ai/models)
    
26.  R1 - API, Providers, Stats - OpenRouter, accessed February 15, 2026, [https://openrouter.ai/deepseek/deepseek-r1](https://openrouter.ai/deepseek/deepseek-r1)
    
27.  Show HN: Plandex v2 – open source AI coding agent for large projects and tasks | Hacker News, accessed February 15, 2026, [https://news.ycombinator.com/item?id=43710576](https://news.ycombinator.com/item?id=43710576)
    
28.  Running Open-Source AI Coding Assistants Aider and Claude Dev (2024) | by John Maeda, accessed February 15, 2026, [https://johnmaeda.medium.com/running-open-source-ai-coding-assistants-aider-and-claude-dev-2024-768190538280](https://johnmaeda.medium.com/running-open-source-ai-coding-assistants-aider-and-claude-dev-2024-768190538280)
    
29.  State of AI 2025: 100T Token LLM Usage Study | OpenRouter, accessed February 15, 2026, [https://openrouter.ai/state-of-ai](https://openrouter.ai/state-of-ai)
    
30.  Best Open Source AI Coding Agents 2026: Tested & Reviewed, accessed February 15, 2026, [https://cssauthor.com/best-open-source-ai-coding-agents/](https://cssauthor.com/best-open-source-ai-coding-agents/)
    
31.  Best AI Coding Assistants as of February 2026 - Shakudo, accessed February 15, 2026, [https://www.shakudo.io/blog/best-ai-coding-assistants](https://www.shakudo.io/blog/best-ai-coding-assistants)
    
32.  12 Coding Agents Defining the Future of AI Development - Cline Blog, accessed February 15, 2026, [https://cline.bot/blog/12-coding-agents-defining-the-future-of-ai-development](https://cline.bot/blog/12-coding-agents-defining-the-future-of-ai-development)
    
33.  Congrats on the launch. Can you please compare and contrast Plandex features wit... | Hacker News, accessed February 15, 2026, [https://news.ycombinator.com/item?id=39924660](https://news.ycombinator.com/item?id=39924660)
    
34.  Create a “black box” test case | aider, accessed February 15, 2026, [https://aider.chat/examples/add-test.html](https://aider.chat/examples/add-test.html)
    
35.  Usage | aider, accessed February 15, 2026, [https://aider.chat/docs/usage.html](https://aider.chat/docs/usage.html)
    
36.  Aider in your IDE | aider, accessed February 15, 2026, [https://aider.chat/docs/usage/watch.html](https://aider.chat/docs/usage/watch.html)
    
37.  Plandex v2: an open source AI coding agent with diff review sandbox, full auto mode, and 2M token effective context - Reddit, accessed February 15, 2026, [https://www.reddit.com/r/ChatGPTCoding/comments/1jgmbsa/plandex\_v2\_an\_open\_source\_ai\_coding\_agent\_with/](https://www.reddit.com/r/ChatGPTCoding/comments/1jgmbsa/plandex_v2_an_open_source_ai_coding_agent_with/)
    
38.  Plandex - Open source AI coding agent for large tasks, accessed February 15, 2026, [https://plandex.ai/](https://plandex.ai/)
    
39.  An open source AI coding agent for real world projects - YouTube, accessed February 15, 2026, [https://www.youtube.com/watch?v=SFSu2vNmlLk](https://www.youtube.com/watch?v=SFSu2vNmlLk)
    
40.  Context Management | Plandex Docs, accessed February 15, 2026, [https://docs.plandex.ai/core-concepts/context-management](https://docs.plandex.ai/core-concepts/context-management)
    
41.  OpenHands | The Open Platform for Cloud Coding Agents, accessed February 15, 2026, [https://openhands.dev/](https://openhands.dev/)
    
42.  OpenHands/OpenHands: OpenHands: AI-Driven ... - GitHub, accessed February 15, 2026, [https://github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands)
    
43.  Scripting aider, accessed February 15, 2026, [https://aider.chat/docs/scripting.html](https://aider.chat/docs/scripting.html)
    
44.  Test-Driven Development for Code Generation - arXiv, accessed February 15, 2026, [https://arxiv.org/html/2402.13521v1](https://arxiv.org/html/2402.13521v1)
    
45.  A simplified approach to understanding Test Driven Development (TDD) and Automated testing | by Armstrong Ebong, accessed February 15, 2026, [https://lil-armstrong.medium.com/a-better-approach-to-understanding-tdd-and-automated-testing-using-python-doc-test-8b916f3842b3](https://lil-armstrong.medium.com/a-better-approach-to-understanding-tdd-and-automated-testing-using-python-doc-test-8b916f3842b3)
    
46.  An LLM TDD loop - David Winterbottom, accessed February 15, 2026, [https://codeinthehole.com/tips/llm-tdd-loop-script/](https://codeinthehole.com/tips/llm-tdd-loop-script/)
    
47.  Linting and testing - Aider, accessed February 15, 2026, [https://aider.chat/docs/usage/lint-test.html](https://aider.chat/docs/usage/lint-test.html)
    
48.  Aider in your IDE | aider, accessed February 15, 2026, [https://aider.chat/docs/usage/watch.html#autonomous-coding](https://aider.chat/docs/usage/watch.html#autonomous-coding)
    
49.  agents - LangChain Blog, accessed February 15, 2026, [https://blog.langchain.dev/tag/agents/](https://blog.langchain.dev/tag/agents/)
    
50.  Scripting aider | aider, accessed February 15, 2026, [https://aider.chat/docs/scripting.html#python-scripting-api](https://aider.chat/docs/scripting.html#python-scripting-api)
    
51.  Learning Hub | Agent Flywheel, accessed February 15, 2026, [https://agent-flywheel.com/learn](https://agent-flywheel.com/learn)
    
52.  Autonomous Coding Agents: Beyond Developer Productivity | C3 AI Blog, accessed February 15, 2026, [https://c3.ai/blog/autonomous-coding-agents-beyond-developer-productivity/](https://c3.ai/blog/autonomous-coding-agents-beyond-developer-productivity/)
    
53.  Automate Smarter, Not Louder: Using Interactive AI Feedback Loops, accessed February 15, 2026, [https://www.cybersec-automation.com/p/automate-smarter-not-louder-using-interactive-ai-feedback-loops](https://www.cybersec-automation.com/p/automate-smarter-not-louder-using-interactive-ai-feedback-loops)

---

## Official / 2026 links

- [`agent_flywheel_clawdbot_skills_and_integrations`](https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations) · [`mcp_agent_mail`](https://github.com/Dicklesworthstone/mcp_agent_mail)
- [`findings_orchestration_opencode_ralph_ruflo_flywheel.md`](research_overnight_stack_web/findings_orchestration_opencode_ralph_ruflo_flywheel.md)
