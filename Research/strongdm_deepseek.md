## **Executive Summary**
StrongDM's Software Factory represents a paradigm shift from interactive coding assistance to fully autonomous, non-interactive development. Their core innovation isn't a single tool, but a **system of interconnected principles and techniques**: replacing tests with external **Scenarios**, creating isolated **Digital Twin Universes (DTU)** for validation, and measuring success via probabilistic **Satisfaction**.

Replicating this exactly is capital-intensive (they suggest spending >\$1,000/day/engineer on tokens), but the principles can be adapted for a solo developer on a ~\$60/month budget. Your VPS investment is crucial, as it provides a persistent, powerful environment for agents to work unattended. The key is shifting your role from **supervisor to release engineer**, where you define the spec and validation criteria, and the system iterates autonomously until it converges on a solution that passes all checks.

---

### **1. Analysis of StrongDM's Core Components & Capabilities**
StrongDM's approach is built on a philosophy of "non-interactive development," where human effort is focused entirely on specification and validation, not on coding or review. Here are the components most valuable for your goal:

- **Scenarios Over Tests**: This is the most critical concept. StrongDM found that in-agent tests are easily "reward-hacked" (e.g., an agent writing `assert true` to pass a test). They moved to **Scenarios**—end-to-end user stories stored **outside the codebase** the agent can see.
  - **Your Takeaway**: You need an external, LLM-readable evaluation harness that the coding agent cannot modify. This harness runs the agent's code against real-world scenarios and uses an LLM to judge if the outcomes were "satisfactory."[[build-yourself-one]]

- **Digital Twin Universe (DTU)**: To run thousands of scenarios without cost, rate limits, or legal issues, they built high-fidelity clones of APIs like Okta and Slack.
  - **Your Takeaway**: For your projects, you need lightweight, containerized mocks or simulators of your external dependencies. This allows you to run validation cycles 24/7 on your VPS for pennies.[[Tags/mockoon]], [[keploy]], [[msw]]

- **Satisfaction Metric**: Moving from a binary "tests pass/fail" to a probabilistic "satisfaction" score based on observed trajectories through scenarios.
  - **Your Takeaway**: Your validation step shouldn't just be "did it run?" but "did the agent's execution path produce the correct user outcome?" This requires an LLM-as-a-judge to evaluate the final state and the process. [[OpenJudge]],

- **The "Attractor" Principle**: They open-sourced `attractor`, which contains no code, only an extremely detailed spec (thousands of lines).
  - **Your Takeaway**: The quality of the output is directly proportional to the quality and detail of the input spec. Your existing `agents.md` is a good start, but for autonomous execution, you need to move towards these "executable specifications." [[ralph-orchestrator]], [[semantic-kernal]]

---

### **2. Alternative Open-Source and Lower-Cost Tools**
You cannot buy a "\$60/month Software Factory," but you can assemble one using open-source tools on your VPS. The budget will cover API token costs (your primary expense) and the VPS.

| StrongDM Concept             | Open-Source / Low-Cost Alternative                  | Rationale                                                                                                                                                                                                              |
| ---------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Orchestration & Agents**   | **CrewAI** or **AG2** (formerly AutoGen)            | Both are Python frameworks for orchestrating multi-agent collaborations. CrewAI's role-based agent design is intuitive, while AG2 offers more complex conversation patterns. You can run the orchestrator on your VPS. |
| **Visual Workflow Builder**  | **Flowise** or **Waldiez**                          | If you prefer a GUI, these tools let you design agent workflows, tool usage, and logic flows visually. They can be self-hosted on your VPS, acting as the control plane.                                               |
| **Scenario Execution & DTU** | **Docker + Browserless** + **LocalStack / Mockoon** | Run the agent's code in isolated Docker containers. Use Browserless for headless browser automation to test UI scenarios. Use LocalStack to mock AWS services or Mockoon to create quick API mocks for your DTU.       |
| **LLM-as-a-Judge**           | **OpenAI / Anthropic API**                          | You will use calls to frontier models (like `gpt-4o` or `claude-3.5-sonnet`) to judge the outcomes of your scenarios. This is your primary token cost.                                                                 |
| **Context Store**            | **CXDB** (StrongDM's own) or **Weaviate**           | CXDB is an open-source AI Context Store. Alternatively, Weaviate is a vector database you can self-host on your VPS to give agents long-term memory and a way to search past execution logs and project documentation. |
| **Local LLM (Optional)**     | **Tabby** or **Ollama**                             | To save on API costs for non-critical tasks like code completion or generating summaries, you can run a smaller model (e.g., via Tabby) on your VPS. This offloads work from your laptop and the expensive API.        |
### **3. Proposed Architecture for a $60/Month "Solo Software Factory"**

This architecture leverages your VPS as the persistent "factory floor" where work happens without your supervision.

```flowchart TD
subgraph Your Laptop ["Your Laptop (Day - Plan)"]
	A[("Detailed Spec\n(agents.md + Scenarios)")]
end
subgraph VPS ["VPS (~$30/month) - The Factory Floor"]
	direction TB
	B[("Code Repository\n(Git)")]
	C[("Orchestrator\n(CrewAI/AG2)")]
	D[("Validation Harness")]
	E[("Digital Twin Universe\n(Docker Mocks)")]
	F[("LLM Judge\n(e.g., GPT-4o)")]
	G[("Context Store\n(Weaviate/CXDB)")]
	C -- "1. Reads spec & clones repo" --> B
	C -- "2. Assigns tasks to agents" --> C
	C -- "3. Agent writes/runs code" --> B
	B -- "4. Code commit triggers" --> D
	D -- "5. Runs scenarios against" --> E
	D -- "6. Asks for evaluation" --> F
	F -- "7. Satisfaction score" --> D
	D -- "8. Result & logs" --> C
	C -- "9. Iterates or stops" --> C
	C -- "10. Stores all traces" --> G
end
subgraph Morning ["Morning (Day+1 - Review)"]
	H["You review final code\nand satisfaction reports"]
end
A -- "Push Spec & Scenarios" --> VPS
VPS -- "Execution Report" --> H
```

**How the workflow would function overnight:**

1. **Planning (You, Day)**: You write an extremely detailed spec and a set of scenarios (e.g., "As a user, I can log in with Google SSO. Validate that the OAuth flow completes and session cookie is set."). You push these to your repo.
2. **Delegation (Evening)**: You trigger the orchestrator on your VPS (e.g., via a script or a webhook). This is the last human action.
3. **Overnight Execution (VPS)**:
    - The orchestrator (CrewAI) spawns agents (e.g., "Coding Agent," "Debugging Agent").
    - They read the spec, pull the latest code, and begin their work.
    - After each change, the code is run through the **Validation Harness**.
    - The harness executes the code against the **Digital Twin Universe** (mocked APIs, test databases in Docker).
    - The **LLM Judge** evaluates the traces from these runs against the scenarios, returning a satisfaction score.
    - This loop continues: code, validate, score, refine. All steps are logged to the **Context Store**.
4. **Review (You, Next Day)**: You wake up to a full report. The orchestrator has either converged on a solution with a high satisfaction score or stopped after a max number of iterations, logging all failures for you to analyze.

### **4. Implementation Strategy for Autonomous Overnight Execution**

This is a phased approach to build reliability without being overwhelmed.

- **Phase 1: Foundation (Weeks 1-2)**
    
    - **VPS Setup**: Provision your $30 VPS (e.g., Hetzner or DigitalOcean). Install Docker, Python, and `git`. Secure it with UFW (firewall) as shown in the `alderaan/vps` repository.
    - **Self-Host Tabby**: Deploy Tabby on your VPS pointing to your OpenAI API key. Connect your local VS Code/Cursor to it. This immediately offloads autocomplete from your laptop and familiarizes you with self-hosted AI.
    - **Simple Orchestration**: Install Flowise via Docker. Create a simple "agent" that can read a `todo.md` file and make commits to a test repo based on instructions. This proves the basic "agent-on-VPS" concept.
- **Phase 2: The Validation Harness (Weeks 3-4)**
    
    - **Define Scenarios**: For a current project, write 3-5 scenarios. Store them as Markdown files in a `/scenarios` folder **outside your main codebase**.
    - **Build the Judge**: Create a Python script (your first version of the Validation Harness) that:
        1. Checks out the latest code from your repo into a Docker container.
        2. Runs the application.
        3. For each scenario, it either makes an API call or uses Browserless to simulate user interaction.
        4. It then sends the full trace (logs, API outputs, final state) to an LLM (e.g., `gpt-4o`) with the prompt: "Given this scenario: [scenario text], does this execution trace satisfy the user's goal? Answer YES/NO and why." This is your LLM Judge.
        5. The script outputs a "satisfaction score" (e.g., 4/5 scenarios satisfied).
    - **Integrate with Cursor**: Manually run this script after your current Cursor sessions to start building a dataset of what "good" looks like.
- **Phase 3: The Autonomous Loop (Weeks 5+)**
    
    - **Adopt CrewAI**: Replace your manual process with a CrewAI flow on the VPS.
        - Create two agents: a `Developer` (writes code) and a `Debugger` (analyzes validation harness failures and suggests fixes).
        - Create a `Crew` that runs them in a loop: `Developer` codes, `Debugger` reviews the validation report, and then the loop repeats until the satisfaction score is 100% or a max iteration is hit.
    - **Integrate Context Store**: Start feeding successful and failed runs into Weaviate. Your agents can then query this store to see how similar problems were solved in the past, improving reliability.

---

### **5. Recommendations for Improving Agent Reliability**

Reliability is the key to unsupervised execution. These strategies are drawn directly from the research and StrongDM's experience.

- **Embrace the "Sherlock" Principle: Selective Verification**: The academic paper "Sherlock" demonstrates that you don't need to verify every single agent step. By analyzing your workflows, you can identify which steps are most error-prone and apply expensive verification (LLM-as-a-judge) only there. This reduces latency and cost. For your system, this means your validation harness might only run full scenarios after a coding block is complete, not after every single file edit.
- **Externalize and Freeze Scenarios**: Your scenarios are your most precious asset. Treat them like a "holdout set" in machine learning. **Never** let your coding agents see or modify them. They are the immutable standard against which all work is judged. Store them in a separate, read-only directory that only the validation harness can access.
- **Use "AgentDevel" Release Engineering**: The AgentDevel paper reframes agent improvement as a release pipeline. This is exactly your goal.
    - **Implementation-Blind Critic**: Your LLM Judge should only see the _symptoms_ of failure (logs, outputs, states), not the agent's internal reasoning or the code itself. This prevents bias.
    - **Flip-Centered Gating**: When evaluating a new "release candidate" (the code after an overnight run), prioritize fixing regressions (things that used to work but now fail) over adding new functionality. Your satisfaction score should heavily weigh against regressions.
- **Practice "Gene Transfusion"**: StrongDM uses this term for having agents extract patterns from existing, human-written code and reuse them. Before an overnight run, have an agent scan your codebase for established patterns (e.g., "how we write API error handlers," "our logging format") and write them into a `PATTERNS.md` file that the coding agent can reference during its work.
- **Master the Spec**: Your existing `agents.md` is the foundation. To reach autonomy, you must evolve it. The StrongDM `attractor` spec is thousands of lines for a reason. Your spec must not just describe _what_ to build, but the **constraints, architectural patterns, and edge cases** to avoid. The time you spend writing this spec is the time you save by not watching the agent

## Follow up
Your understanding is spot-on. The StrongDM stack is built around these core components, each addressing a specific challenge in autonomous software development. Here’s a one-sentence summary of each piece you identified:

1.  **Attractor (Orchestrator)**: A minimal, code‑free specification that guides agents through structured phases (e.g., design → implement → test → refactor), acting as a high‑level blueprint for autonomous execution.
2.  **CXDB (Context & Trace Store)**: A database that records every agent action, tool call, and execution trace, providing a shared memory for agents and a complete audit trail for human review.
3.  **Leash (Guardrails)**: A safety layer that intercepts and restricts dangerous commands (e.g., `rm -rf /`, excessive API calls), preventing agents from damaging the project or environment.
4.  **Digital Twin Universe (DTU)**: High‑fidelity, in‑memory clones of external services (like Okta, Slack) used to run thousands of scenarios safely and scalably, eliminating dependency on live APIs and preventing reward hacking.
5.  **LLM Judge**: An evaluator that reviews execution outcomes against human‑written scenarios and specs, producing a probabilistic “satisfaction” score rather than relying on easily gamed tests.

These components work together to enable **non‑interactive development**—the system can iterate overnight, with you only reviewing the final results and satisfaction reports in the morning. Your summary correctly captures the essence of the StrongDM philosophy.

## Question
I've been doing more research on each piece of this stack and different options I can use to piece together a full system. The part I'm struggling to find options for is this:
`Define Scenarios: For a current project, write 3-5 scenarios. Store them as Markdown files in a /scenarios folder outside your main codebase.`

It sounds a bit to me like Behavioural Driven Design (BDD) https://github.com/bitloops/ddd-hexagonal-cqrs-es-eda but I know that's more a testing framework and less a definition of scenarios. Could you please help me find some open-source projects that would be a good product-fit for defining scenarios? Even if we just build it ourselves. I think an important piece is moving away from tests that can be faked to a separate source of truth

## Answer
You are exactly right to focus on this. The scenario layer is the philosophical core of the StrongDM approach, and you've correctly identified that traditional BDD frameworks, while conceptually similar, fall short because they live **inside** the codebase the agent can manipulate.

The GitHub repository you linked (`bitloops/ddd-hexagonal-cqrs-es-eda`) is an excellent example of sophisticated software architecture and even includes BDD. However, for your specific goal of **non-interactive development with an immutable source of truth**, it is not the right product fit. The scenarios (or BDD features) in that project would be stored in `.feature` files or test specifications within the repository, exactly where a motivated agent could find and alter them to "prove" success.

You need a system where the evaluation criteria are **externally enforced and agent-proof**. You are not looking for a testing framework; you are looking for a **specification and evaluation harness**. Since this is a nascent field, a perfect off-the-shelf open-source product likely doesn't exist. You will need to build a lightweight version yourself, leveraging the concepts you've researched.

Here is a breakdown of how to approach building this "Scenario Definition & Evaluation" layer, drawing on the principles from the StrongDM blog and combining them with practical, existing tools.

### 🧱 Core Requirements for Your Scenario System
Based on our discussion, your system must have these non-negotiable properties:
1.  **Externally Stored**: Scenarios reside outside the main codebase the agent modifies (e.g., in a separate, read-only directory or a dedicated database).
2.  **Immutable & Agent-Proof**: The coding agent must never be able to read or write these files during its execution loop. Only the **Validator/Judge** can read them.
3.  **LLM-Friendly**: Scenarios should be written in a way that an LLM can easily understand the goal, the steps, and the criteria for success.
4.  **Executable & Verifiable**: The system must be able to take a scenario, execute the agent's code against it (often in an isolated environment like a Docker container), and collect a trace for evaluation.

### 🛠️ How to Build It: A Hybrid Approach
You cannot buy this, but you can assemble it. Here is a practical path combining existing formats with a custom-built judge.

**Option A: Use a Structured Format You Control (Recommended Start)**
This is the simplest and most flexible way to begin. You design the format, so you control the source of truth completely.

| Component | Tool/Format | Your Implementation Task |
| :--- | :--- | :--- |
| **Scenario Definition** | **Markdown + YAML Frontmatter** | Create `.scenario.md` files. Use YAML frontmatter for structured data (like initial state, mocks to use) and the Markdown body for the natural language story and validation criteria. Store these in a `/scenarios` folder **outside** your main project repo (e.g., in a separate `project-specs` repo). |
| **Orchestration** | **CrewAI / AG2** | Your orchestrator's main loop will: 1) Read the next scenario from the external folder. 2) Instruct a "Tester" agent to set up the DTU (Docker mocks). 3) Run the latest build of your main code against it. 4) Collect all logs, API calls, and final state. |
| **LLM Judge** | **GPT-4o / Claude 3.5** | Package the scenario text and the full execution trace into a prompt: "Given this scenario goal: [scenario]. Did the execution trace satisfy all user intentions? Explain why or why not, focusing on the outcomes, not the code structure." The judge returns a boolean or a satisfaction score. |
| **Trace Storage** | **CXDB / Weaviate** | Store every scenario run, its trace, and the judge's verdict in your context store. This builds memory for future agent runs ("We solved a similar login scenario last week, here's how"). |

**Option B: Adapt Existing BDD Tools with a Critical Twist**
This leverages familiar syntax but requires strict process controls.

| Component | Tool/Format | The Critical Twist for Agent-Proofing |
| :--- | :--- | :--- |
| **Scenario Definition** | **Gherkin (.feature files)** | You **must** store these files in a **separate, read-only directory** that the main coding agent's container cannot mount or access. Only the validation container can see them. |
| **Test Harness** | **Cucumber / Behave** | Your validation harness (a separate process/container) runs Cucumber, pointing it to the read-only `.feature` files and the running instance of the agent's code. The harness then captures the output. |
| **LLM Judge** | **Custom Script** | Cucumber will give a green/red for individual steps. But you need more nuance. Your script will take the Cucumber report **and** the full application logs and ask an LLM: "The step 'user logs in' passed, but did the system set the correct session cookie and return the expected user object? Judge the *quality* of the pass." |

### ✨ Key Insight: The Scenario is the Prompt
Think of your scenario definition as the ultimate meta-prompt for the entire system. **When you write a scenario, you are not just writing a test; you are defining a desired state of the universe that your agent's code must help realize.**

For your **first overnight experiment**, I strongly recommend **Option A**. Create 3-5 simple but meaningful `.scenario.md` files for a feature you understand well. Build a simple Python script that acts as the judge, reads the scenario and a log file, and calls `gpt-4o` to get a yes/no. Once that manual loop works, you can automate it with CrewAI.

This approach directly addresses your core need: an immutable, external source of truth that forces the agent to genuinely solve the problem, not just game the system.

Would you like me to elaborate on the structure of an effective `.scenario.md` file, or dive deeper into how the LLM judge prompt should be engineered for maximum reliability?

An effective `scenario.md` file is the cornerstone of your autonomous development system. It serves as the immutable, external specification that both guides the agent's work and provides the criteria for the LLM judge to evaluate success. Think of it as a hybrid between a user story, a test case, and a oracle prompt.

Here's a detailed breakdown of how to structure and write these files for maximum clarity and reliability.

### 🧩 Core Principles of a Good Scenario

Before diving into the template, keep these principles in mind:

1.  **External & Immutable**: The file must be stored **outside** the codebase the agent modifies (e.g., in a separate `scenarios/` directory, perhaps even in a different repository). The agent should never be able to read or alter it during execution.
2.  **LLM-Readable**: Write in clear, unambiguous natural language. Avoid jargon or assumptions that a language model might misinterpret.
3.  **Outcome-Focused**: Describe what the user experiences and what the system should ultimately achieve, not the internal implementation details. This prevents the agent from "gaming" the scenario by taking shortcuts.
4.  **Executable by a Judge**: The scenario must contain enough information for an LLM (the judge) to look at a trace of the agent's execution (logs, API calls, final state) and confidently decide whether the scenario was satisfied.

### 📝 Recommended `scenario.md` Template

I recommend using Markdown with YAML frontmatter for metadata. This gives you both human-readable narrative and machine-parseable fields.

```yaml
---
id: SCN-001
name: User successfully logs in with valid credentials
tags: [authentication, login, happy-path]
prerequisites:
  - A registered user exists with email "test@example.com" and password "ValidP@ssw0rd"
  - The application is running and accessible at http://localhost:3000
mocks:
  - Okta identity provider (if SSO is used)
---
# Scenario: User Login

## Narrative
As a registered user,
I want to log in to the application with my email and password,
So that I can access my dashboard and start using the service.

## Execution Steps
1. The user navigates to the login page at `/login`.
2. The user enters `test@example.com` in the email field.
3. The user enters `ValidP@ssw0rd` in the password field.
4. The user clicks the "Sign In" button.

## Expected Outcomes
- The system authenticates the user and redirects them to the dashboard page (`/dashboard`).
- A session cookie named `session_id` is set in the browser.
- The dashboard page displays a personalized welcome message containing the user's email, e.g., "Welcome back, test@example.com!".
- No error messages are shown.
- The login attempt is recorded in the application logs with status "success".

## Validation Notes for Judge
- Check the final URL: it must be `/dashboard`.
- Verify that a cookie named `session_id` exists and has a valid format (non-empty, looks like a JWT or UUID).
- Look for a visible element on the dashboard that contains the user's email.
- Examine the logs for an entry like `LOGIN_SUCCESS` for the user.
```

### 🔍 Detailed Breakdown of Each Section

#### **YAML Frontmatter**
- **`id`**: A unique identifier. Helps in tracking and referencing.
- **`name`**: A short, descriptive title.
- **`tags`**: Useful for categorizing scenarios (e.g., `critical-path`, `regression`, `performance`). The orchestrator could select a subset of scenarios to run.
- **`prerequisites`**: List any necessary conditions that must be true before the scenario can be executed. This might include database state, environment variables, or other services. The agent must ensure these are set up (or the validation harness must set them up).
- **`mocks`**: Specify which external services should be simulated by your Digital Twin Universe. This tells the validation harness which mocks to spin up.

#### **Narrative**
A classic user story format (As a… I want… So that…). This provides context for both the agent (to understand the feature) and the judge (to understand the user's intent). It's especially useful for the agent during the design phase.

#### **Execution Steps**
A clear, ordered list of actions a user would take. These are the steps the validation harness will simulate (e.g., via browser automation or API calls). Be as explicit as possible about element names, button labels, and navigation.

#### **Expected Outcomes**
This is the most critical part for the LLM judge. Instead of saying "the test passes," you describe **observable phenomena** that indicate success. Include:
- **State changes**: URL changes, cookies set, data created.
- **UI elements**: Messages, page titles, specific text.
- **Log entries**: Expected log lines (optional but helpful).
- **Side effects**: Emails sent, API calls made to external systems.

The more concrete and verifiable these outcomes, the easier it is for the judge to evaluate.

#### **Validation Notes for Judge**
This section is optional but highly recommended. It provides hints to the LLM judge on what to look for in the execution trace. Since the judge might not have perfect vision (if it's examining logs or DOM snapshots), these notes help focus its evaluation. For example, "Check that the cookie is secure and HTTP-only" or "Ensure the welcome message uses the correct email case."

### 🎯 Example: A More Complex Scenario

Here's a scenario for a multi-step feature with conditional outcomes:

```yaml
---
id: SCN-042
name: User resets password via email link
tags: [authentication, password-reset, email]
prerequisites:
  - A registered user exists with email "forgot@example.com"
  - The email service is mocked (the judge should capture the reset link)
mocks:
  - SMTP server (fake)
---
# Scenario: Password Reset

## Narrative
As a user who forgot my password,
I want to reset it using a link sent to my email,
So that I can regain access to my account.

## Execution Steps
1. User goes to the login page and clicks "Forgot Password".
2. User enters `forgot@example.com` in the email field and submits.
3. System shows a message: "If an account exists with that email, you will receive a reset link."
4. The mocked email service receives a message to `forgot@example.com` with a subject containing "Reset your password".
5. The email body contains a link (URL) with a path `/reset-password` and a token parameter.
6. User clicks that link (simulated via HTTP GET).
7. The reset page loads with fields for new password and confirm password.
8. User enters `NewP@ssw0rd!` and confirms, then submits.
9. User is redirected to login page with a success message.

## Expected Outcomes
- A unique, one-time-use reset token is generated and stored in the database (associated with the user).
- The token is valid for no more than 1 hour.
- After reset, the user can log in with `forgot@example.com` and `NewP@ssw0rd!`.
- The old password no longer works.
- The reset link becomes invalid after use.
- An email is sent to the user notifying them of the successful password change.
- All actions are logged appropriately.

## Validation Notes for Judge
- Extract the reset link from the captured email. Verify the token format.
- Simulate using the link and check that the page loads correctly.
- After reset, attempt login with new password (via API) and verify session.
- Check that login with old password fails.
- Try to reuse the reset link again; it should fail.
```

### ✍️ Tips for Writing Effective Scenarios

- **Be Specific, Not Vague**: Instead of "the user sees a confirmation," say "the page displays a green banner with the text 'Password reset successfully'."
- **Cover Edge Cases**: Create separate scenarios for validation errors, non-existent users, expired tokens, etc. This builds robustness.
- **Keep Scenarios Independent**: Each scenario should be able to run in isolation. If one scenario requires state from another, use prerequisites and reset the environment before each run.
- **Use Consistent Terminology**: If you call it "sign in" in one scenario, don't call it "log in" in another unless that's the actual UI text.
- **Think Like a Judge**: When writing expected outcomes, ask yourself: "If I were an LLM looking at a log file and a screenshot, what evidence would convince me this worked?"

### 🤖 How the Judge Uses the Scenario

In your automated loop, the validation harness will:

1.  Read the scenario file (frontmatter and markdown).
2.  Set up the prerequisites and mocks (e.g., seed a test database, start mock servers).
3.  Execute the steps (via browser automation or API calls) against the agent's latest code.
4.  Capture the full trace: console logs, network requests, database snapshots, screenshots (if UI), and final application state.
5.  Construct a prompt for the LLM judge that includes:
    - The entire scenario content (especially the Expected Outcomes).
    - The captured trace.
    - Instructions to evaluate each expected outcome and provide a justification.
6.  Parse the judge's response (e.g., a JSON with scores for each outcome) and determine if the scenario is satisfied.

By structuring your `scenario.md` files this way, you create a robust, external specification that can drive truly autonomous development. The agent writes code to make these scenarios pass, and the judge ensures the code genuinely meets the user's needs—not just a narrow test.

Would you like me to provide a more detailed example for a specific type of feature (e.g., API, background job, or UI flow)?

---

## Official / 2026 links

- [Software Factory](https://factory.strongdm.ai/) — scenarios, satisfaction, non-interactive narrative
- [Principles](https://factory.strongdm.ai/principles) — seed → harness → holdout scenarios
- [Digital Twin Universe (technique)](https://factory.strongdm.ai/techniques/dtu)
- [Blog: Building Software with AI](https://www.strongdm.com/blog/the-strongdm-software-factory-building-software-with-ai)
- [CXDB (product)](https://factory.strongdm.ai/products/cxdb) · [GitHub `strongdm/cxdb`](https://github.com/strongdm/cxdb)
- [Leash (product)](https://leash.strongdm.ai/) · [GitHub `strongdm/leash`](https://github.com/strongdm/leash) · [Policy enforcement blog](https://www.strongdm.com/blog/policy-enforcement-for-agentic-ai-with-leash)
- [Attractor (product)](https://factory.strongdm.ai/products/attractor)
- [GitHub `strongdm/attractorbench`](https://github.com/strongdm/attractorbench)
- Web research notes: [`research_overnight_stack_web/findings_reference_strongdm_opensource.md`](research_overnight_stack_web/findings_reference_strongdm_opensource.md)
