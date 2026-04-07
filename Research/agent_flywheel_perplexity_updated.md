
## 1. Setup and Infrastructure (Updated)

### 1.1 Use the Agent Flywheel Wizard as Your Bootstrap

Instead of hand‑rolling the VPS environment, you can lean on ACFS + the web wizard:

- The wizard walks you through:
    - OS choice, SSH keys, renting VPS, connecting, and running the installer.[^2][^1]
    - One‑liner ACFS install that:
        - Installs 30+ dev tools (tmux, zsh, modern shell, linters, etc.).[^1][^2]
        - Sets up the Flywheel tools (NTM, Mail, BV, CASS, CM, UBS, SLB, DCG, etc.) out of the box.[^6]
- Benefit for you:
    - You get a **known-good, Flywheel-compatible** environment in ~30 minutes.[^2][^1]
    - No need to reimplement tmux orchestration, resource protection (SRPS), or much of the utility plumbing.[^7][^6]

**Update to plan:**
Replace the custom “bootstrap script” step with:

1. Follow the wizard: [agent-flywheel.com/wizard/os-selection](https://agent-flywheel.com/wizard/os-selection).[^1]
2. Use its instructions to:
    - Rent a 16–32GB VPS from a cheap provider (Contabo, Hetzner, etc.).[^6]
    - Run the ACFS installer and verify via the Doctor/status checks.[^2][^6]

You still target 16–32GB rather than 64GB; the wizard and ACFS don’t mandate huge RAM, they just scale better when you have it.[^6]

***

## 2. Orchestration and Agents (Updated)

### 2.1 Keep NTM, Mail, BV, CASS from Flywheel

Because the Flywheel setup is free and ACFS installs everything, you should **embrace** its orchestration tools instead of reimplementing them:

- **NTM**: Use it as your tmux orchestrator for:
    - Spawning and naming sessions for Sisyphus/OpenCode, Aider, Plandex, etc.[^6]
- **Agent Mail**:
    - Use it as your “Gmail for agents” for file reservations and cross‑agent messaging.[^6]
- **BV / Beads**:
    - Use Beads and BV for task DAG and prioritization instead of Plane/Linear.[^6]
- **CASS / CM**:
    - Let ACFS give you CASS + CM for session search and memory instead of building SQLite+Qdrant from scratch.[^6]

**Update to plan:**
The “Beads backlog + Qdrant + Plane” part is now:

- Backlog and dependency graph → Beads + BV (built in).[^6]
- Memory and search → CASS + CM.[^6]
- You still add your own procedural markdown docs, but they sit *on top* of CM instead of replacing it.


### 2.2 Add Oh My OpenCode on Top of ACFS

Oh My OpenCode (OpenCode) gives you a higher‑level “engineering manager” agent (Sisyphus) with curated sub‑agents for specific roles.[^3][^4]

Key capabilities:

- **Sisyphus** (main agent) orchestrates sub‑agents:
    - Planner, Oracle (architecture/debug), Librarian (docs/research), Explore (code search), Frontend engineer, etc.[^4][^3]
- It’s designed to:
    - Mix and match models per sub‑agent (“orchestrate them by purpose”).[^3]
    - Delegate background tasks to **faster, cheaper models** while keeping Sisyphus on a strong reasoning model.[^3]

This lines up perfectly with your desire to:

- Think in terms of planning/delegation (you + Sisyphus)
- Let sub‑agents run overnight on cheaper models

**Update to plan:**

On the Flywheel VPS after ACFS is done:

1. Install Oh My OpenCode (Sisyphus) following its README.[^8][^3]
2. Integrate with Flywheel tooling:
    - Run Sisyphus inside an NTM‑managed tmux session.
    - Give Sisyphus access to Beads/CASS so it can:
        - Read beads and project state.
        - Write status and new beads as needed.

Now your orchestration stack looks like:

- ACFS: base environment + Flywheel tools (NTM, Mail, BV, CASS, etc.).[^2][^6]
- Oh My OpenCode: higher‑level agent harness that chooses which “teammate” to call for each task.[^4][^3]
- Aider/Plandex: still valuable for TDD loops and big refactors, but can be driven by Sisyphus when appropriate.[^6]

***

## 3. Model Strategy (Updated for Oh My OpenCode + Free Tiers)

Your initial idea: “Hephaestus, Oracle, Frontend engineer, Librarian, Explore” on GPT/Gemini/Claude. That’s great conceptually but overkill for your **\$60/month** constraint if you use premium tiers for everything.[^4][^3]

You can instead:

- Keep the **same roles**, but:
    - Run them on cheaper or free models where possible.
    - Use paid models only for the most impactful reasoning.


### 3.1 Roles and Suggested Models

Here’s a revised mapping, mixing paid and free options and leveraging free‑token tiers from resources like `free-llm-api-resources`.[^5]


| Role (Oh My OpenCode) | Function | Recommended Model Tier | Notes |
| :-- | :-- | :-- | :-- |
| **Sisyphus** (main) | Planner, delegator, complex tasks | Mid‑tier Claude/Qwen/Sonnet via OpenRouter | Use your “best” paid model here; this is your brain. |
| **Hephaestus** | Autonomous deep worker | Cheap high‑token model (DeepSeek R1/V3) | Bulk coding \& refactors. |
| **Oracle** | Design \& deep debugging | Same as Sisyphus, but lower usage | Hit it only for nasty bugs/architecture. |
| **Frontend Engineer** | UI/UX + frontend | Gemini 2/3 code or Qwen‑Code free tier | Use free/cheap web dev‑optimized models when possible.[^5] |
| **Librarian** | Docs \& external OSS lookup | Claude Haiku / Gemini free / free LLM API | IO‑heavy but not always heavy reasoning. |
| **Explore** | Code search / grep helper | Claude Haiku / cheap fast model | Lots of calls, but low reasoning. |

**Implementation idea:**

- Configure OpenCode’s agents to prefer:
    - **Free/low‑cost endpoints** from `free-llm-api-resources` where fit (Gemini, Qwen, etc.).[^5]
    - A single strong paid model (e.g. Claude Sonnet) reserved for Sisyphus + Oracle.
    - A cheap high‑throughput model (DeepSeek) for Hephaestus.

This preserves:

- Role separation (good for mental model and reliability).
- Budget discipline, because:
    - High‑IQ tokens are used rarely.
    - Bulk work runs on cheap or free APIs.


### 3.2 Concrete Budget Sketch with Free Tokens

Rough monthly allocation:

- **Sisyphus + Oracle (Paid Model)**
    - \$15–\$20 on Sonnet/strong model
    - Used for plan review, beads decomposition, hard debugging
- **Hephaestus (Deep Worker)**
    - \$10–\$15 on DeepSeek (or similar cheap code model)
    - Main cost sink; handles overnight code + TDD loops
- **Frontend/Librarian/Explore**
    - Mostly on free or nearly‑free APIs (Gemini, Qwen, etc.) as listed in `free-llm-api-resources`.[^5]
    - Possibly a small buffer (\$5) for overages / backups
- **VPS**
    - \$10–\$18 for 16–32GB machine, as before.[^6]

You can keep Copilot/Cursor in your existing \$30 budget or slowly phase them out as this stack takes over more work.

***

## 4. Workflow Adjustments with Sisyphus + Flywheel

Here’s how your **plan-and-review** loop changes with the new stack:

### 4.1 During the Day: You + Sisyphus

- You write your `agents.md` / openspec as before.
- You then ask **Sisyphus** to:

1. Read the spec + relevant code.
2. Decompose into **beads** (using BV’s beads format).
3. Assign beads to:
        - Hephaestus (deep worker) for backend tasks.
        - Frontend engineer for UI beads.
        - Librarian for any research beads.
4. Store beads in the Flywheel backlog so BV can compute critical paths.[^3][^4][^6]
- You briefly review / tweak beads, just like a tech lead reviewing a sprint plan.


### 4.2 Overnight: Sisyphus as Engineering Manager

- Sisyphus:
    - Pulls ready beads from the Flywheel backlog (via CASS/BV).
    - Delegates them to the right agent:
        - Hephaestus → big backend bead using DeepSeek.
        - Frontend → Gemini/Qwen for UI.
        - Librarian → docs/docs alignment.
    - Uses Aider/Plandex where appropriate:
        - For TDD loops and big refactors, call Aider or Plandex under the hood instead of doing everything via one chat agent.
- NTM and Agent Mail:
    - Coordinate tmux sessions and file locks.
    - Prevent conflicting edits.[^6]


### 4.3 Morning: Same Review Model, Better Delegation

Your review process is unchanged in spirit, just cleaner in implementation:

- Look at Beads/BV:
    - Which beads moved from “todo” → “done”?
- Check:
    - Diffs (from Aider commits or Plandex sandbox).
    - Test results.
    - CASS/CM summaries of each agent session.

Your time is focused on:

- “Do I accept these changes?”
- “Do I need to improve the plan or the procedural docs for next time?”

***

## 5. What to Implement First with This New Stack

Minimal path to value with your new idea:

1. **Use the ACFS Wizard**
    - Get a Flywheel VPS environment up.[^1][^2][^6]
2. **Install Oh My OpenCode**
    - Wire Sisyphus to:
        - Use one good paid model (Sonnet or similar) for itself + Oracle.
        - Use DeepSeek + free Gemini/Qwen for sub‑agents.[^4][^5][^3]
3. **Connect Sisyphus to Flywheel Primitives**
    - Have Sisyphus:
        - Read/write beads in the Flywheel backlog.
        - Use NTM for spawning TDD agents (Aider/Plandex).
        - Store transcripts into CASS.
4. **Pilot a Simple Overnight Run**
    - 1–3 beads, narrow scope.
    - Sisyphus plans + delegates to Hephaestus using Aider for execution.
    - You review in the morning, just as in the previous plan.

From there, you can grow toward:

- More sub‑agents.
- More parallelism.
- Better memory/procedural docs.

But the key difference after this update is:

- **Setup complexity drops** (ACFS wizard instead of manual).
- **Model strategy is richer** (Oh My OpenCode roles + free/cheap APIs).
- **You still stay inside your ~\$60/month envelope** while gaining a stronger “engineering manager” abstraction.
<span style="display:none">[^10][^11][^12][^13][^14][^15][^9]</span>

<div align="center">⁂</div>

[^1]: https://agent-flywheel.com

[^2]: https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup

[^3]: https://github.com/code-yeongyu/oh-my-opencode/blob/dev/README.md

[^4]: https://x.com/aeitroc/status/2003789446542418173

[^5]: https://github.com/cheahjs/free-llm-api-resources

[^6]: richtext_converted_to_markdown-1.md

[^7]: https://agent-flywheel.com/learn/srps

[^8]: https://github.com/code-yeongyu/oh-my-opencode

[^9]: https://www.youtube.com/watch?v=foVZPizNESw

[^10]: https://www.amazon360.net/agency-flywheel-os

[^11]: https://www.linkedin.com/posts/atmaneayoub_github-cheahjsfree-llm-api-resources-activity-7390450334382456832-k_8p

[^12]: https://agentflywheel.io/flywheel-workflow

[^13]: https://www.youtube.com/watch?v=uuV1DcvObsg

[^14]: https://www.reddit.com/r/GithubCopilot/comments/1pjwum1/github_cheahjsfreellmapiresources_a_list_of_free/

[^15]: https://www.agentflywheel.io/new

---

## Official / 2026 links

- [`agent_flywheel_clawdbot_skills_and_integrations`](https://github.com/Dicklesworthstone/agent_flywheel_clawdbot_skills_and_integrations) · [`mcp_agent_mail`](https://github.com/Dicklesworthstone/mcp_agent_mail)
- [`findings_orchestration_opencode_ralph_ruflo_flywheel.md`](research_overnight_stack_web/findings_orchestration_opencode_ralph_ruflo_flywheel.md)
