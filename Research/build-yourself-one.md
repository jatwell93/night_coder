#validition #validator #todo
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
Think of your scenario definition as the ultimate meta-prompt for the entire system. When you write a scenario, you are not just writing a test; you are defining a desired state of the universe that your agent's code must help realize.

For your **first overnight experiment**, I strongly recommend **Option A**. Create 3-5 simple but meaningful `.scenario.md` files for a feature you understand well. Build a simple Python script that acts as the judge, reads the scenario and a log file, and calls `gpt-4o` to get a yes/no. Once that manual loop works, you can automate it with CrewAI.

This approach directly addresses your core need: an immutable, external source of truth that forces the agent to genuinely solve the problem, not just game the system.

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

- [StrongDM Principles](https://factory.strongdm.ai/principles) — external / holdout scenarios framing
- [OpenJudge docs](https://agentscope-ai.github.io/OpenJudge/) · [`py-openjudge` on PyPI](https://pypi.org/project/py-openjudge/)
- [`research_overnight_stack_web/research_report.md`](research_overnight_stack_web/research_report.md) (stack map)
