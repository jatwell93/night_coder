# StrongDM Software Factory & Open Source — Research Notes (Web, 2025–2026)

Research focus: **overnight / autonomous coding stacks** — official StrongDM narrative on non-interactive development, scenarios, Digital Twin Universe (DTU), **satisfaction** as a validation metric, **CXDB**, **Leash**, **Attractor**, plus **open-source** repositories and announcements.

---

## 1. Software Factory & non-interactive development

### Official positioning

StrongDM describes a **Software Factory** as **non-interactive development** where specifications and **scenarios** drive agents that write code, run harnesses, and converge **without human review**.

**Source:** [StrongDM Software Factory (factory.strongdm.ai)](https://factory.strongdm.ai/)

> “We built a Software Factory: non-interactive development where specs + scenarios drive agents that write code, run harnesses, and converge without human review.”

In **rule form**, the same page states:

> “- Code must not be written by humans  
> - Code must not be reviewed by humans”

The narrative ties **long-horizon agentic coding** (post–Claude 3.5 revision, ~Oct 2024) and tools like Cursor **YOLO mode** to what they call **non-interactive development** or **grown software** — contrasting **compounding correctness** with **compounding error**.

**Source:** [StrongDM Software Factory (factory.strongdm.ai)](https://factory.strongdm.ai/)

### Official blog (product announcement)

The company blog summarizes intent, scenarios, DTU, and “validation replaces code review”:

**Source:** [The StrongDM Software Factory: Building Software with AI — StrongDM Blog](https://www.strongdm.com/blog/the-strongdm-software-factory-building-software-with-ai)

> “Humans define intent: what the system should do, the scenarios it needs to handle, the constraints that matter. After that, the agents take it from there. They generate code, validate it against real-world behavior, and iterate until it converges, without hand-tuning or human review.”

> “The factory is powered by scenario-based validation, a Digital Twin Universe of systems like Okta and Slack, and agents that run end-to-end once the work is fully specified. It’s what happens when validation replaces code review.”

> “The result is a system that gets better by iterating against reality. This system runs real scenarios, validates real behavior, and corrects itself without humans in the loop.”

Alternate marketing URL for the same story (discover subdomain):

**Source:** [The StrongDM Software Factory: Building Software with AI — discover.strongdm.com](https://discover.strongdm.com/blog/the-strongdm-software-factory-building-software-with-ai)

### Principles (engineering framing)

The **Principles** page frames a closed loop: **Seed → Validation harness → Feedback**, with emphasis on end-to-end validation and iterating until **holdout scenarios** pass.

**Source:** [The Principles | StrongDM Software Factory](https://factory.strongdm.ai/principles)

> “Your validation harness must be end-to-end, as close to the real environment as possible: customers, integrations, economics.”

> “The loop runs until the holdout scenarios pass (and stay passing)”

---

## 2. Scenarios vs. tests; **satisfaction** metric

StrongDM distinguishes **scenarios** from traditional **tests**: scenarios are end-to-end “user stories,” often **outside the codebase** (analogous to a **holdout set** in ML), meant to be understood and validated flexibly by an LLM — partly to reduce **reward hacking** when code and in-repo tests co-evolve.

**Source:** [StrongDM Software Factory (factory.strongdm.ai)](https://factory.strongdm.ai/)

> “We repurposed the word scenario to represent an end-to-end ‘user story’, often stored outside the codebase (similar to a ‘holdout’ set in model training), which could be intuitively understood and flexibly validated by an LLM.”

**Satisfaction** is defined as a **probabilistic, empirical** success criterion (not boolean “suite is green”), suited to **agentic** software:

**Source:** [StrongDM Software Factory (factory.strongdm.ai)](https://factory.strongdm.ai/)

> “Because much of the software we grow itself has an agentic component, we transitioned from boolean definitions of success (‘the test suite is green’) to a probabilistic and empirical one. We use the term satisfaction to quantify this validation: of all the observed trajectories through all the scenarios, what fraction of them likely satisfy the user?”

Related motivation on rigid tests vs. LLM-as-judge and cheating:

**Source:** [StrongDM Software Factory (factory.strongdm.ai)](https://factory.strongdm.ai/)

> “1. Tests are too rigid … evaluating success often required LLM-as-judge  
> 2. Tests can be reward hacked - we needed validation that was less vulnerable to the model cheating”

---

## 3. Digital Twin Universe (DTU)

**DTU** = **behavioral clones** of third-party services (APIs, edge cases, observable behavior). Public examples named: **Okta, Jira, Slack, Google Docs, Google Drive, Google Sheets**.

**Sources:**

- [Digital Twin Universe technique page](https://factory.strongdm.ai/techniques/dtu)
- [StrongDM Software Factory main narrative](https://factory.strongdm.ai/)

Quotes (technique page):

> “We built twins of Okta, Jira, Slack, Google Docs, Google Drive, and Google Sheets, replicating their APIs, edge cases, and observable behaviors.”

> “With the DTU, we can validate at volumes and rates far exceeding production limits. We can test failure modes that would be dangerous or impossible against live services. We can run thousands of scenarios per hour without hitting rate limits, triggering abuse detection, or accumulating API costs.”

DTU page also lists: high-volume validation, dangerous failure modes, avoiding abuse detection, **determinism** / replayable conditions, and replicating behavior at the **API boundary** until behavioral differences vs. live systems stop appearing.

**Source:** [Digital Twin Universe | Techniques](https://factory.strongdm.ai/techniques/dtu)

---

## 4. Attractor (non-interactive coding agent)

**Attractor** is described as StrongDM’s **implementation of a non-interactive coding agent**: models, prompts, and tools composed into a **graph-structured pipeline**, intended to run **end-to-end** once work is fully specified.

**Source:** [Attractor | StrongDM Software Factory](https://factory.strongdm.ai/products/attractor)

Example **nodes** (phases): **Implement**, **Identify**, **Optimize**, **Validate** — each governed by a core prompt. **Edges** between nodes are **natural language**, evaluated by the LLM (including conditional / judged branches).

**Source:** [Attractor | StrongDM Software Factory](https://factory.strongdm.ai/products/attractor)

Stated execution properties include: deterministic given same inputs, observable transitions, **resumable** from checkpoints, composable graphs.

**Source:** [Attractor | StrongDM Software Factory](https://factory.strongdm.ai/products/attractor)

The product page states the **Attractor spec is open** and links a long list of **community implementations** in multiple languages (Rust, Go, Python, Java, F#, Ruby, TypeScript, Scala, C, C#, etc.) — useful for anyone comparing stacks.

**Source:** [Attractor | StrongDM Software Factory](https://factory.strongdm.ai/products/attractor)

---

## 5. CXDB (context store for agents)

**CXDB** is positioned as a **self-hosted context store** for AI agents: every conversation turn persisted with **branching**, typing, and a **visual debugger**, modeled as a **turn DAG** plus **blob CAS** (content-addressed payloads, e.g. **BLAKE3**), with performance claims (e.g. append p50 < 1ms for 10KB on the product page).

**Source:** [CXDB | StrongDM Software Factory](https://factory.strongdm.ai/products/cxdb)

> “CXDB is a self-hosted context store for AI agents. It persists every turn of every conversation with full type awareness, branching support, and a visual debugger.”

> “Observability for AI agents exists. LLM proxies exist. But what's missing is a self-hosted, inexpensive option that is 100% context- and turn-focused. CXDB fills that gap.”

License called out on the product page:

**Source:** [CXDB | StrongDM Software Factory](https://factory.strongdm.ai/products/cxdb)

> “Apache 2.0, full source. Use it for production observability, internal tools, commercial products, or learning how context stores work.”

**Open-source repository:** [https://github.com/strongdm/cxdb](https://github.com/strongdm/cxdb)

---

## 6. Leash (policy enforcement for agentic AI)

**Leash** is an **open-source** StrongDM project for **policy enforcement** aimed at **autonomous / agentic** workloads: extends StrongDM-style access thinking to **non-human** actors, using **Cedar** policies (same language family as StrongDM’s policy engine per the blog).

**Source:** [StrongDM Delivers Policy Enforcement for Agentic AI with Leash — StrongDM Blog](https://www.strongdm.com/blog/policy-enforcement-for-agentic-ai-with-leash)

> “That’s the question that led us to create Leash, an open-source project we’ve released to help developers explore how to extend StrongDM-style access guarantees to autonomous workloads and agentic systems.”

> “Leash can be used to intercept activity from agents and evaluate them against Cedar-defined policies, which is the same language that powers the StrongDM Policy Engine.”

Operational picture (in-kernel / network path):

**Source:** [StrongDM Delivers Policy Enforcement for Agentic AI with Leash — StrongDM Blog](https://www.strongdm.com/blog/policy-enforcement-for-agentic-ai-with-leash)

> “By operating inside the kernel network stack, Leash functions as a control point that can:  
> - Inspect outbound traffic and identify the target service or domain.  
> - Enforce policy before the connection is established.  
> - Apply context-aware rules defined in Cedar …”

**MCP:** Blog states Leash **parses and handles Model Context Protocol** and intercepts MCP at the OS level to reduce bypass risk.

**Source:** [StrongDM Delivers Policy Enforcement for Agentic AI with Leash — StrongDM Blog](https://www.strongdm.com/blog/policy-enforcement-for-agentic-ai-with-leash)

Product / demo site linked from the post:

**Source:** [https://leash.strongdm.ai/](https://leash.strongdm.ai/)

**Open-source repository:** [https://github.com/strongdm/leash](https://github.com/strongdm/leash)

---

## 7. Additional StrongDM GitHub repos (related announcements)

| Repo | URL | Relevance (brief) |
|------|-----|-------------------|
| **attractor** | [https://github.com/strongdm/attractor](https://github.com/strongdm/attractor) | Reference / spec implementation for the graph-based non-interactive agent pipeline (linked from factory product page). |
| **cxdb** | [https://github.com/strongdm/cxdb](https://github.com/strongdm/cxdb) | Open-source turn-DAG context store (Apache 2.0 per factory page). |
| **leash** | [https://github.com/strongdm/leash](https://github.com/strongdm/leash) | Open-source agentic policy enforcement (Cedar, kernel/network, MCP — per blog). |
| **attractorbench** | [https://github.com/strongdm/attractorbench](https://github.com/strongdm/attractorbench) | Benchmark tooling for coding-agent compliance with natural-language specs (public `AGENTS.md` and repo metadata on GitHub). |

---

## 8. Third-party commentary (context only, not official StrongDM)

Independent write-ups reference the same factory narrative (useful for cross-checking terminology such as scenarios, DTU, satisfaction):

- Simon Willison: [http://blog.simonwillison.net/2026/Feb/7/software-factory/](http://blog.simonwillison.net/2026/Feb/7/software-factory/)  
- HyperAI story page (aggregator): [https://hyper.ai/en/stories/eb7b9cb01c2d0faabbebc97981a06997](https://hyper.ai/en/stories/eb7b9cb01c2d0faabbebc97981a06997)

---

## 9. URL index (full list)

- [https://factory.strongdm.ai/](https://factory.strongdm.ai/)  
- [https://factory.strongdm.ai/principles](https://factory.strongdm.ai/principles)  
- [https://factory.strongdm.ai/techniques/dtu](https://factory.strongdm.ai/techniques/dtu)  
- [https://factory.strongdm.ai/products/attractor](https://factory.strongdm.ai/products/attractor)  
- [https://factory.strongdm.ai/products/cxdb](https://factory.strongdm.ai/products/cxdb)  
- [https://www.strongdm.com/blog/the-strongdm-software-factory-building-software-with-ai](https://www.strongdm.com/blog/the-strongdm-software-factory-building-software-with-ai)  
- [https://discover.strongdm.com/blog/the-strongdm-software-factory-building-software-with-ai](https://discover.strongdm.com/blog/the-strongdm-software-factory-building-software-with-ai)  
- [https://www.strongdm.com/blog/policy-enforcement-for-agentic-ai-with-leash](https://www.strongdm.com/blog/policy-enforcement-for-agentic-ai-with-leash)  
- [https://leash.strongdm.ai/](https://leash.strongdm.ai/)  
- [https://github.com/strongdm/attractor](https://github.com/strongdm/attractor)  
- [https://github.com/strongdm/cxdb](https://github.com/strongdm/cxdb)  
- [https://github.com/strongdm/leash](https://github.com/strongdm/leash)  
- [https://github.com/strongdm/attractorbench](https://github.com/strongdm/attractorbench)  

---

*Compiled for autonomous/overnight coding stack research. Web captures reflect content available on the indexed pages at research time; star counts on GitHub change frequently.*
