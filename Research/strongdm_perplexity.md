
## 1. What StrongDM’s factory is actually doing

StrongDM’s Software Factory is built around non‑interactive development: specs and scenarios go in, agents run through a graph of phases, and the outcome is judged by automated harnesses and scenario satisfaction, not by humans watching the cursor.[^2][^5][^1]

Key patterns and components that matter for you:

- **Attractor – non‑interactive coding agent**
    - Defined as “a non-interactive coding agent structured as a graph of phases” that “runs end-to-end when the work is fully specified.”[^3]
    - The public repo is just detailed natural‑language specs; you feed those into your coding agent of choice to build the Attractor implementation and then use Attractor to run work as a phased graph (design → implement → test → refactor, etc.).[^6][^4]
    - Emphasis on phases that can re‑enter each other (e.g., tests fail → back to implementation) without human approval.[^4][^5][^1]
- **CXDB – context store and execution trace DB**
    - “Self-hosted context store for AI agents” with support for branching conversations, DAGs, blob deduplication, typed tool calls, and “visual debugging.”[^7][^3]
    - It lets them store all agent steps, states, tool invocations, and outputs, so they can reason about long‑horizon work and inspect what happened after the fact instead of watching in real time.[^7][^4]
- **Scenario‑based validation \& Digital Twin Universe**
    - They treat scenarios like holdout “user stories” that describe real‑world behavior the system must satisfy. Agents write code/tests to satisfy these scenarios.[^5][^1][^2]
    - A “Digital Twin Universe” clones external services like Okta, Slack, Google Docs/Drive/Sheets so the agent can call them at high scale and low risk.[^1][^2][^4][^5]
    - They move from a boolean test notion (“all tests passed”) to probabilistic satisfaction metrics across many scenarios.[^8][^2][^4]
- **Leash – security, policies, and guardrails**
    - Open‑source component that “authorizes and monitors AI agents with policy enforcement, sandboxed execution, and real‑time observability.”
    - Provides sandboxed execution, MCP authorization (what tools an agent can call), and Cedar policy‑based rules on what an agent can or cannot do.
    - Meant to ensure that non‑interactive agents can run unattended without compromising security.
- **StrongDM ID – identity for humans/workloads/agents**
    - Acts as identity and access control for both humans and AI agents, using federated auth and path‑scoped sharing.[^3]
    - In your context this translates to: make sure agents run with constrained credentials and separate identities from your own user.

Conceptually, StrongDM’s stack gives them:

- A **phase graph** for work (Attractor).
- A **long‑term execution memory and trace** (CXDB).
- **Validation worlds** (scenarios + digital twins + harnesses).
- **Security \& policies** around what an agent can do (Leash + StrongDM ID).
- A **non‑interactive posture**: humans define specs/scenarios and evaluate metrics, not intermediate steps.[^2][^4][^5][^1]

***

## 2. Affordable / open substitutes for each capability

Within ~USD 60/month you won’t replicate their infrastructure at company scale, but you can implement the same ideas:

### Phase‑graph coding agent (Attractor‑like)

You already have Cursor Pro, which effectively gives you:

- YOLO / long‑running tasks, refactors, and multi‑file edits.
- Workspace‑level context and iterative refactoring.

To build an Attractor‑like graph of phases:

- Use a **runner/orchestrator** that can call your model/IDE agent in phases:
    - Options:
        - Open‑source agent frameworks: **LangChain**, **Semantic Kernel**, **Haystack Agents**, **CrewAI**, **AutoGen**, **OpenAI’s Swarm‑like patterns**, etc.[^9]
        - For a lighter approach, a small Python driver script that:
            - Reads a markdown “NLSpec” (your equivalent of Attractor’s spec).
            - For each phase, calls an LLM via API or triggers Cursor via CLI/integration (see below).
            - Commits after each phase and logs results in a DB.
- You can also directly leverage Attractor’s NLSpec repo as a template for your own phase structure: design, scaffolding, implementation, tests, refactors, docs.[^6][^4]
    - Use their phase design as a blueprint but plug it into your own LLM endpoints and file operations.


### Context store and trace (CXDB‑like)

If you want something very close to CXDB:

- StrongDM’s CXDB itself is open‑sourced as a self‑hosted context store.[^4][^7]
    - It’s designed for branching conversations, typed tool calls, and “visual debugging,” exactly the kind of post‑hoc inspection you want.[^7]
    - You could run CXDB locally in Docker and connect your orchestrator to it as the log and context backend.

If you prefer simpler alternatives:

- **LiteLLM + Postgres**: log each tool call/LLM call in DB rows keyed by run ID, with message, tool, inputs, outputs, and timestamps.
- **Open‑source traces**:
    - Arize Phoenix, LangSmith‑like OSS tools, or OpenLLMetry can give you structured traces and dashboards. [[openllmetry]]

Either way, your **goal** is to store:

- The full conversation (prompts, outputs).
- Phase transitions and decisions.
- Tool invocations (e.g., test runs, git commands).
So you can review the whole overnight run in the morning without babysitting.


### Scenarios, digital twins, and validation

You can approximate their validation environment as follows:

- **Scenarios as markdown + tests**
    - Maintain a `scenarios/` folder where each scenario is a small YAML or markdown file describing:
        - Initial state (fixtures, setup script).
        - Actions (CLI calls, HTTP requests, UI flows).
        - Expected behavior (assertions; logs; metrics).
    - Your harness can be a Python test runner (pytest) or a dedicated script that executes these scenarios using mocks or test doubles.
- **Digital Twin Universe equivalents**
    - For external services like Slack, Google APIs, etc., use:
        - Local mocks/fakes (e.g., WireMock for HTTP APIs).
        - Dockerized test versions of services (e.g., MinIO as an S3 twin; a local SMTP test server; a small HTTP server implementing only the endpoints you need).
    - The important bit: agents always run against **these twins**, not against production APIs, so they can safely run overnight and at high volume.[^5][^1][^2][^4]
- **Probabilistic satisfaction metrics**
    - Instead of “all tests pass or fail,” collect metrics per scenario:
        - Pass/fail, number of attempts, coverage (which code paths changed), maybe heuristic “quality” signals (documentation updated; complexity metrics stayed bounded, etc.).
    - A simple aggregator script can compute a “satisfaction score” per scenario, which you check in the morning to decide if the change is acceptable.[^8][^1][^2][^4]


### Security and guardrails (Leash/StrongDM ID‑like)

You can’t fully match StrongDM ID, but you can get similar properties:

- **Leash itself is open‑source and free** (Apache‑2), built “for agents” with sandboxed execution, MCP authorization, and Cedar policies.
    - You can run Leash locally to sandbox your agent’s tool access and enforce what it can do during an overnight run.
- Use **separate API keys and OS users** for the agent:
    - Run the overnight agent under a dedicated Unix user with limited filesystem permissions.
    - Use dedicated API keys (GitHub PAT with minimal scopes, sandbox environment variables) so if the agent misbehaves, blast radius is small.
- Policies:
    - Explicitly forbid destructive commands outside specific project dirs.
    - Only allow network access to your digital twins and safe services.
    - Use Cedar policies with Leash or a similar rule engine to enforce these at the tool layer.

***

## 3. Proposed architecture within ~USD 60/month

You currently pay ~USD 30 for GitHub Copilot Pro + Cursor Pro. To move into a factory‑like mode:

### Budget‑friendly stack

Approximate monthly allocation (USD):

- **Cursor Pro** – already in place, keep it (~\$20–\$30 depending on plan).
- **One high‑end model API** (OpenAI or Anthropic etc.) – ~\$20–\$30 in usage for long‑horizon runs.
- **Infra costs** (cloud VM or local machine; DB) – assume negligible or part of your existing dev budget.

This keeps you under or near \$60/month while giving you:

- Cursor for interactive/completion and local refactors.
- API calls for batch, long‑horizon, non‑interactive phases driven by your own orchestrator.


### High‑level architecture

| Layer | Role | Suggested tools |
| :-- | :-- | :-- |
| Spec \& scenarios | You write NLSpecs and holdout scenarios | `agents.md`, `openspec`, `scenarios/*.md` |
| Phase orchestrator | Runs Attractor‑like graph | Small Python service using LangChain/AutoGen/CrewAI or custom |
| Coding agent | Writes/edits code | Cursor + a model API (Claude / GPT‑4.x / similar) |
| Context store \& traces | Logs runs and tool calls | CXDB or Postgres + tracing library |
| Validation harness | Runs scenarios \& tests | Pytest / custom script + Dockerized twins |
| Guardrails | Policies, sandbox, monitoring | Leash + separate Unix user and keys |
| CI / Git | Integration path | GitHub Actions, branch per run |

Workflow:

1. You define a spec and scenarios (NLSpec + scenario files).
2. You trigger a “run” via a CLI command or GitHub Action.
3. The orchestrator executes phases (plan → scaffold → implement → test → fix → doc) with your chosen model, editing code in a local clone.
4. After each phase, it commits to a branch, logs into CXDB/DB, and runs scenario harnesses.
5. If satisfaction is below a threshold, it automatically loops back to a previous phase; otherwise, it finishes and posts a summary.
6. In the morning, you review:
    - Run summary.
    - Scenario metrics.
    - Git diff.
    - Traces in CXDB (if needed).

***

## 4. Concrete strategies for autonomous overnight execution

Here’s how to push your workflow from “watch and guide” in VSCode to “plan and review”:

### 4.1. Turn specs + scenarios into first‑class artifacts

You already use `agents.md` and openspec, which is excellent. Evolve this into:

- `specs/feature-X.md` – Attractor‑style spec for each job:
    - Goals, non‑goals, constraints.
    - Phases: what “done” looks like in each phase (plan, implementation, tests, docs, refactor).
- `scenarios/feature-X/*.md` – scenario descriptions, including:
    - Setup instructions.
    - Step‑by‑step user flows or API calls.
    - Expected behavior/outcomes.

Then your agent orchestration prompt is mostly: “Here is the spec and scenarios for this run; carry out the phases defined in the spec, and do not ask me for confirmation.”

This mirrors the way StrongDM defined Attractor solely via detailed NLSpecs.[^6][^4][^5]

### 4.2. Design the phase graph (inspired by Attractor)

Start with a simple phase graph, e.g.:

1. **Phase 1 – High‑level plan**
    - Input: spec.
    - Output: `plan.md` with sub‑tasks and mapping to scenarios.
2. **Phase 2 – Scaffolding**
    - Create or modify files minimally to support the new feature; no full implementations yet.
3. **Phase 3 – Implementation**
    - Implement functionality, keeping each change small and testable.
4. **Phase 4 – Tests \& scenarios**
    - Implement unit/integration tests; code scenario runners.
5. **Phase 5 – Run harness \& self‑repair**
    - Run tests and scenarios.
    - If failures, re‑enter Phase 3 with a bounded loop count (e.g., up to 5 fix cycles).
6. **Phase 6 – Refactor \& docs**
    - Clean up code, update docs/changelog.
7. **Phase 7 – Summary \& PR**
    - Produce a `run-summary.md`, including scenario satisfaction metrics and known limitations.

Implement this in a Python orchestrator that:

- Reads a run config (spec name, target branch).
- Uses your model API to generate code/edits via e.g. file‑editing tools (apply diff patches).
- Commits after each phase, tagging commit messages with `[PHASE:x]`.
- Logs all prompts/responses into CXDB or Postgres.


### 4.3. Integrate with Cursor / Copilot

You can use Cursor in two ways:

- During your active work: design the spec and scenarios with help from Cursor.
- For the overnight factory: let the orchestrator use the same model underlying Cursor via API, instead of driving Cursor itself.
    - If Cursor exposes a CLI for running “tasks” from a spec, you can integrate that; otherwise, calling the LLM APIs directly is simpler.

Your overnight run should **not** be inside VSCode; it should be:

- A terminal command like `factory run specs/feature-X.md`.
- Using a fresh working tree or a dedicated branch.
- Logging into CXDB or DB.

This removes the temptation to watch the “thinking” live and encourages you to review only the outcomes.

### 4.4. Use Leash for sandboxing

Adopt Leash to constrain what your overnight agent can touch:

- Configure it as the policy and execution layer for your agent’s tools (file system, shell, HTTP).
    - Sandboxed execution with resource limits and network boundaries.
    - MCP authorization so the agent can only call specific tools (e.g., a git tool, a test runner tool, a dependency install tool).
    - Cedar policies to block destructive or out‑of‑scope actions.

This makes unattended runs safer and simplifies your mental model: the agent literally cannot step outside the project boundaries you define.

***

## 5. Improving reliability and reducing intervention

The StrongDM team’s experience points to specific practices that make non‑interactive runs viable:[^1][^2][^4][^5]

### 5.1. Use holdout scenarios as the main steering signal

Instead of you noticing “it skipped a broader fix,” encode that concern as:

- Scenarios that reflect “nearby” and “long‑horizon” behaviors:
    - A bug fix scenario, plus a regression scenario for adjacent flows.
- A policy that the agent **must** maintain or increase scenario satisfaction score, not only make tests green.

If a scenario keeps failing after X loops, the run stops and reports: the agent cannot satisfy scenario S; here is what it tried.

### 5.2. Make “pyramid summaries” of context

StrongDM mentions “Pyramid Summaries”: multiple levels of summary so an agent can skim high‑level context and zoom in as needed.[^10][^1]

You can implement this cheaply:

- Maintain:
    - `SUMMARY-L0.md` – very high‑level project overview.
    - `SUMMARY-L1-<module>.md` – per‑module summaries.
    - `SUMMARY-L2-<file>.md` – optional detailed summaries for dense files.
- Let your agent use these summaries as first‑line context, resorting to raw code only when necessary.

This reduces context sprawl and helps the model stay aligned with architecture without you watching.

### 5.3. Cap self‑repair loops and scope

Reliability often fails because agents drift: they keep refactoring, introduce regressions, or chase irrelevant fixes.[^11][^4]

Your orchestrator should:

- Put **hard caps** on loops:
    - e.g., After 5 test‑fix cycles, stop and report limitations.
- Limit **blast radius** per run:
    - Only allow edits in directories explicitly whitelisted in the spec.
    - Forbids renaming/deleting files outside those directories.
- Use diff‑based edits: the agent proposes a patch; your tool applies it only if it touches allowed regions.


### 5.4. Reviews at the right granularity

Your new “review surface” in the morning should be:

- A `run-summary.md` describing:
    - What phases ran; how many loops.
    - Which scenarios passed/failed.
    - Known risks, TODOs.
- A scenario satisfaction report (table).
- A Git diff between base and the final commit.
- Optional: a pointer into CXDB traces if you want to see how the agent reasoned.[^4][^7]

This aligns with StrongDM’s focus on evaluating outputs and metrics, not internal chains of thought.[^2][^1][^4]

***

## 6. Concrete tool list and integration sketch

To make this actionable, here’s a minimal “v1 factory” configuration you could realistically build in a few weekends:

- **IDE \& local work**
    - Cursor Pro + Copilot Pro (keep as‑is).
- **LLM backend for factory**
    - One strong model subscription or pay‑as‑you‑go: choose your preferred vendor; budget \$20–\$30/month.
- **Orchestrator**
    - Small Python project:
        - Phases implemented as functions.
        - LLM calls via a simple client (e.g., `litellm`, `openai`, or Anthropic client).
        - File operations via apply‑diff pattern.
- **Context store / traces**
    - Option A: CXDB deployed locally (Docker) as a dedicated agent context DB.[^3][^7][^4]
    - Option B: Postgres + a bare‑bones schema (runs, steps, tools, messages).
- **Validation harness**
    - `tests/` (unit/integration) + `scenarios/` harness script.
    - Digital twins via minimal HTTP mock servers or Dockerized services.
- **Guardrails**
    - Leash to enforce policies on tools and network; Cedar to encode what’s allowed.
    - Separate Unix user and API keys for overnight runs.

Trigger an overnight run via:

```bash
factory run specs/feature-X.md \
  --branch feature-X-factory \
  --scenarios scenarios/feature-X \
  --max-fix-loops 5
```

You go to sleep; in the morning you get:

- A PR on `feature-X-factory`.
- `run-summary.md` and scenario report.
- Optional link to CXDB run view.

From there you act as a supervisor: approve/adjust/re‑spec, rather than micromanaging the agent’s every thought.

***

## Follow ups

Here are concrete, copy‑pasteable templates you can drop into a real repo today. They’re designed to be:

- Judge‑friendly: structured, explicit, and easy to feed to an LLM.
    
- Agent‑safe: live in a repo/directory the coding agent never edits, acting as a true “holdout” set.36kr+2
    

I’ll assume a typical web/service project with HTTP APIs plus some background jobs; you can adapt names as needed.

---

## 1. Scenario file format (Judge‑friendly, agent‑safe)

**Storage & conventions**

- Put scenarios in a separate repo or top‑level directory, e.g. `factory-scenarios/`.
    
- **Coding agents never mount this directory; only the Validation Harness reads it.**
    
- One scenario per file, named with a stable ID: `S-001-login-happy-path.md`.
    

## Scenario template

text

```markdown
# Scenario S-001: User can log in with email and password

## Metadata

id: S-001
title: User login with valid credentials
version: 1
priority: high          # low | medium | high | critical
area: auth              # subsystem or domain
type: functional        # functional | regression | performance | security | ux
status: active          # active | deprecated | experimental

## Business Goal

As a registered user,
I want to log into the application using my email and password,
so that I can access my personal dashboard and data.

## Preconditions

- A user account exists with:
  - email: `user@example.com`
  - password: `CorrectHorseBatteryStaple123`
- The application is running in the Digital Twin Universe environment.
- The database is seeded with the baseline fixture `auth/basic_user_seed`.

## Test Environment

environment_name: dtu-auth-v1
base_url: http://app.dtu.local:8080
services_in_scope:
  - web_app
  - auth_service
  - session_store

## Steps

1. Open the login page at `GET /login`.
2. Submit the login form with:
   - email: `user@example.com`
   - password: `CorrectHorseBatteryStaple123`
   as `POST /login` (form-encoded or JSON, as implemented).
3. Follow any redirects until a stable page is reached.

## Expected Outcomes (System-Level)

- HTTP-level:
  - The final response status is 200 or 302 (redirect to dashboard).
  - No 4xx or 5xx responses are seen in the login flow.
- Session/State:
  - A valid session cookie is set for the main app domain.
  - The session store contains a session linked to `user@example.com`.
- Domain:
  - The user is considered “logged in” on subsequent authenticated requests.

## Expected Outcomes (User-Level)

From the user’s perspective:

- They see a dashboard (or equivalent) page, with their email visible somewhere on screen.
- They do **not** see an error message related to login failure.
- They can refresh the page and remain logged in.

## Evidence Collected

The validation harness will collect and provide to the Judge:

- HTTP request/response logs for this flow (including URLs, status codes, and relevant headers).
- Final HTML or JSON body of the last page.
- Session store snapshot for the user’s session.
- Application logs (redacted) for the auth_service during this flow.
```

``` markdown
## Judge Task

You are an independent evaluator. You have:

- The scenario description (this file).
- The execution trace and evidence from running this scenario in a test environment.

Your task:

1. Decide if this scenario is **SATISFIED** or **NOT SATISFIED**.
2. Explain your reasoning in a few bullet points, referencing concrete evidence.
3. If NOT SATISFIED, classify the failure:
   - `implementation_bug`
   - `regression`
   - `scenario_or_fixture_issue`
   - `environment_or_infrastructure_issue`
4. Provide up to three concise suggestions for what the implementation should change.

Respond in **valid JSON** with this schema:

```json
{
  "scenario_id": "S-001",
  "status": "SATISFIED or NOT_SATISFIED",
  "satisfaction_score": 0.0,
  "failure_class": "implementation_bug | regression | scenario_or_fixture_issue | environment_or_infrastructure_issue | none",
  "reasons": ["..."],
  "suggestions": ["..."]
}
```


You can derive additional scenarios (e.g., invalid password, locked account, expired password, SSO flow) by reusing the same structure with different Preconditions, Steps, and Expected Outcomes.[1][2]

***

## 2. PATTERNS.md template (Gene Transfusion)

This file sits **inside** the code repo and is meant to be generated/refreshed by a “Pattern Extractor” agent, then consumed read‑only by coding agents.[4][5]

```markdown
# PATTERNS: Project Coding Patterns and Idioms

> This document captures concrete patterns from the existing codebase.
> Agents SHOULD follow these patterns when adding or modifying code.

## 1. HTTP API Handlers

### 1.1 Structure

When implementing a new HTTP handler in this project:

- Use the `router` from `src/server/router.ts`.
- Handlers follow this pattern (TypeScript example):

```ts
router.post("/api/v1/widgets", requireAuth, async (req, res) => {
  const input = WidgetCreateSchema.parse(req.body);

  const widget = await createWidget({
    ownerId: req.user.id,
    name: input.name,
    color: input.color ?? "blue",
  });

  res.status(201).json({ widget });
});

```

Key points:

- Input is always validated with a Zod schema named `{Entity}CreateSchema`.
    
- Authenticated routes always include the `requireAuth` middleware.
    
- Responses are JSON objects with a single top-level key (`{entity}` or `data`).
    

## 1.2 Error Handling

Error handling follows this pattern:

```ts
try {
  // ...
} catch (err) {
  logger.error({ err, route: "/api/v1/widgets" }, "failed to create widget");
  if (err instanceof ZodError) {
    return res.status(400).json({ error: "invalid_request", details: err.errors });
  }
  return res.status(500).json({ error: "internal_error" });
}

```

Rules:

- Always log errors with `logger.error({ err, route }, message)`.
    
- 4xx codes are only returned for validation/auth errors.
    
- All other errors become a 500 with `error: "internal_error"`.
    

## 2. Logging

- Use the shared logger from `src/shared/logger.ts`.
    
- Log messages include both a human-readable string and structured context.
    
- Log levels:
    
    - `debug` for flow details and decision points.
        
    - `info` for significant events (user login, resource creation).
        
    - `error` for unexpected failures only.
        

Example:


```ts
`logger.info(   { userId, widgetId },  "user created widget" );
```

## 3. Data Access

- Use the `db` client from `src/shared/db.ts`.
    
- All queries are wrapped in repository functions under `src/repos/*`.
    

Example:

```ts
logger.info(
  { userId, widgetId },
  "user created widget"
);

```

Guidelines:

- Avoid inline `db.*` calls in handlers; always go through repo functions.
    
- Reuse existing repository functions where possible before creating new ones.
    
## 4. Background Jobs

- Background jobs live under `src/jobs/*`.
    
- Each job exports:
    
    - `name: string`
        
    - `handler: (payload: JobPayload) => Promise<void>`
        

Pattern:
```ts
export async function createWidget(params: {
  ownerId: string;
  name: string;
  color: string;
}) {
  return db.widget.create({
    data: {
      ownerId: params.ownerId,
      name: params.name,
      color: params.color,
    },
  });
}
```

## 5. Frontend Components (if applicable)

- Components are function components with TypeScript and hooks.
    
- Shared components live in `src/components/` and are reused instead of duplicating logic.
    
- CSS is applied using Tailwind classes; no inline styles.
    

Example:

```tsx
export function PrimaryButton(props: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      className={
        "inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 " +
        (props.className ?? "")
      }
    />
  );
}

```


---

## 6. General Guidelines for Agents

- Prefer using existing patterns and modules over inventing new abstractions.
    
- When unsure, search the codebase for similar examples and mimic their structure.
    
- New code should feel consistent with the surrounding files in naming, structure, and error handling.
    



You can seed the first version of `PATTERNS.md` yourself, then gradually hand its maintenance over to a Gene‑Transfusion agent.

***

## 3. SUMMARY-L0.md template (Pyramid Summaries, level 0)

`SUMMARY-L0.md` is the top‑level, human‑written/agent‑refreshed project overview. It should be short enough to fit into almost every prompt.[5][4]

```markdown
# SUMMARY-L0: Project Overview

## 1. What this project is

- Name: WidgetHub
- Purpose: SaaS web application for managing "widgets" (configurable resources) for small teams.
- Core features:
  - User authentication (email/password + optional Google OAuth).
  - CRUD operations on widgets.
  - Team membership and role-based access control.
  - Audit logging of key actions.

## 2. High-Level Architecture

- Frontend:
  - React + TypeScript SPA in `frontend/`.
  - Communicates with backend via JSON APIs under `/api/v1/*`.

- Backend:
  - Node.js + TypeScript service in `backend/`.
  - Express-based HTTP API.
  - Background jobs run via a simple job runner (BullMQ) processing Redis queues.

- Data & Infrastructure:
  - PostgreSQL as primary data store.
  - Redis for job queues and short-lived caches.
  - All external integrations are accessed via adapters in `backend/src/integrations/*`.

## 3. Key Invariants and Constraints

- Auth:
  - Every authenticated endpoint must enforce a user context (`req.user`) via middleware.
  - Session tokens are HTTP-only cookies; no JWTs in localStorage.

- Authorization:
  - Access control is centralized in `backend/src/authz/policies.ts`.
  - Do not embed ad-hoc permission checks directly in handlers.

- Data Integrity:
  - Widget names are unique per owner (user or team).
  - Deleting a user requires transferring or deleting their widgets first.

- Reliability:
  - API handlers should never throw uncaught exceptions; all errors must be mapped to appropriate HTTP responses and logged.

## 4. Modules (Level 1 Summaries)

- `frontend/`
  - SPA, routes, and UI components.
- `backend/src/server/`
  - Express app, routes, middlewares.
- `backend/src/repos/`
  - Data access layer for all entities.
- `backend/src/auth/`
  - Authentication and session management.
- `backend/src/authz/`
  - Authorization policies and helpers.
- `backend/src/jobs/`
  - Background job definitions and runners.
- `backend/src/integrations/`
  - External services (email provider, payment processor, messaging).

## 5. External Dependencies and Twins

- External services:
  - Email provider (e.g., SendGrid).
  - Payment processor (e.g., Stripe).
  - Optional messaging integration (e.g., Slack).

- Digital Twin Universe:
  - Email twin: local SMTP server recording sent messages for inspection.
  - Payment twin: local HTTP service emulating Stripe subset used by the app.
  - Messaging twin: local HTTP service capturing "messages" in an in-memory store.

Agents should assume all automated validation runs take place in the Digital Twin Universe, not against real external services.

```

You can then create `SUMMARY-L1-*.md` files for each major module, following the same pattern in more detail (responsibilities, key data types, important flows).

---
For a non‑interactive factory, you as the human mostly look at **run‑level summaries and scenario‑level metrics**, not individual code edits. Below I’ll answer each question concretely and keep it close to what a CXDB‑style stack would actually record.strongdm+5

---

## 1) What metrics would the human evaluate?

At the end of an overnight run, you’d review a small set of metrics pulled from traces and Judge outputs. The key dimensions:simonwillison+3

## Per‑scenario metrics

For each scenario (S‑001, S‑002, …):factory.strongdm+2

- **Satisfaction status**: SATISFIED / NOT_SATISFIED (from the Judge JSON).
    
- **Satisfaction score**: e.g. 0.0–1.0 or 0–100, capturing confidence in user satisfaction.
    
- **Attempts**: how many execution trajectories the factory tried for that scenario in this run.
    
- **Regression flag**: was this scenario SATISFIED in a previous run but is now NOT_SATISFIED?
    
- **Failure class**: implementation bug vs scenario/fixture issue vs infra (from Judge).
    
- **Runtime stats** (optional): average latency, error rate, etc. in the DTU for this scenario.hyper+1
    

## Run‑level metrics

Aggregated over all scenarios in that run:rywalker+3

- **Scenario coverage**: scenarios attempted / total active scenarios.
    
- **Satisfaction rate**: fraction of scenario trajectories judged SATISFIED (StrongDM’s “satisfaction” metric).simonw.substack+3
    
- **Regression count**: how many scenarios flipped from SATISFIED in the previous baseline to NOT_SATISFIED.
    
- **Token/compute budget usage**: rough cost of the run.
    
- **Change footprint**: number of files changed, LoC added/removed, number of migrations, etc.
    
- **Doc/ops hygiene**: did the run update docs, changelog, or runbooks for affected areas (can be measured as a simple boolean or percentage of changed modules with docs touched).
    

You then make a **decision** at the run level:

- Accept: merge branch / ship.
    
- Roll forward: run another shift with refined spec or more budget.
    
- Roll back: discard or partially cherry‑pick.
    

You’re not reading code line‑by‑line; you’re reading a **dashboard** of scenario satisfaction and risk.strongdm+3

---

## 2) Pseudocode for a satisfaction aggregator script

Assume:

- CXDB (or a DB) stores **runs**, **executions**, and **scenario results**.linkedin+1
    
- Each scenario execution has a Judge JSON payload like the template we defined earlier.
    
- You also know previous baseline results so you can detect regressions.
    

Here’s high‑level pseudocode in a Python‑like style.

## Data model (conceptual)

- `Run`: `{id, started_at, finished_at, branch, spec_id}`
    
- `ScenarioResult`: `{run_id, scenario_id, status, satisfaction_score, failure_class, attempts, changed_files, docs_touched}`
    
- `Baseline`: last accepted run per branch or `main`.
    

## Aggregator pseudocode

```python
def load_run(run_id):
    # From CXDB or your DB
    run = db.get_run(run_id)
    scenario_results = db.get_scenario_results(run_id)
    return run, scenario_results

def load_baseline(branch_name):
    baseline_run = db.get_last_accepted_run(branch_name)
    if not baseline_run:
        return None, {}
    baseline_results = db.get_scenario_results(baseline_run.id)
    # Map by scenario_id for quick lookup
    baseline_by_scenario = {r.scenario_id: r for r in baseline_results}
    return baseline_run, baseline_by_scenario

def compute_satisfaction_metrics(run_id, branch_name):
    run, results = load_run(run_id)
    baseline_run, baseline_by_scenario = load_baseline(branch_name)

    total_scenarios = len(results)
    satisfied = 0
    total_score = 0.0
    regressions = []
    improvements = []

    per_scenario_report = []

    for r in results:
        is_satisfied = (r.status == "SATISFIED")
        if is_satisfied:
            satisfied += 1
        total_score += r.satisfaction_score

        # Regression detection
        baseline = baseline_by_scenario.get(r.scenario_id)
        was_baseline_satisfied = baseline and baseline.status == "SATISFIED"
        is_regression = was_baseline_satisfied and not is_satisfied
        is_improvement = (baseline and baseline.status == "NOT_SATISFIED" and is_satisfied)

        if is_regression:
            regressions.append(r.scenario_id)
        if is_improvement:
            improvements.append(r.scenario_id)

        per_scenario_report.append({
            "scenario_id": r.scenario_id,
            "status": r.status,
            "satisfaction_score": r.satisfaction_score,
            "attempts": r.attempts,
            "failure_class": r.failure_class,
            "is_regression": is_regression,
            "is_improvement": is_improvement,
            "changed_files": r.changed_files,
            "docs_touched": r.docs_touched,
        })

    satisfaction_rate = satisfied / total_scenarios if total_scenarios else 0.0
    avg_satisfaction_score = total_score / total_scenarios if total_scenarios else 0.0

    # Simple doc hygiene metric
    scenarios_with_docs = sum(1 for r in per_scenario_report if r["docs_touched"] > 0)
    doc_hygiene = scenarios_with_docs / total_scenarios if total_scenarios else 0.0

    # Build overall run report
    run_report = {
        "run_id": run_id,
        "branch": branch_name,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "total_scenarios": total_scenarios,
        "satisfaction_rate": satisfaction_rate,          # fraction SATISFIED
        "avg_satisfaction_score": avg_satisfaction_score,
        "regression_count": len(regressions),
        "regressions": regressions,
        "improvements": improvements,
        "doc_hygiene": doc_hygiene,
        "per_scenario": per_scenario_report,
    }

    return run_report

```

## Example: collecting CXDB‑style fields

If you integrate with CXDB or a similar trace store, each scenario result could be built from:

- Number of **executions** for that scenario in this run (attempts).
    
- **Judge JSON** stored as a typed tool output in CXDB (status, score, failure_class).factory.strongdm+1
    
- **Changed files** from git diff between baseline commit and final run commit.
    
- **Docs touched** from diff filtered to e.g. `docs/` or `SUMMARY-*.md`.
    

The aggregator just stitches these into a shape you can read over coffee in the morning.

---

## 3) What are “nearby” and “long‑horizon” scenarios?

The idea here is: you’re currently catching “it skipped the broader fix” by watching Cursor think. StrongDM’s approach is to **encode those broader concerns as scenarios** so the system itself notices when the agent fixed a symptom but broke or neglected something important nearby.vercel.hyper+3

## “Bug fix scenario” vs “nearby scenario” vs “long‑horizon scenario”

Imagine you’re fixing a bug: “Login button doesn’t work on mobile Safari.”

- **Bug fix scenario (local)**
    
    - Very specific to the defect.
        
    - Example:
        
        - Scenario S‑101: “On mobile Safari, tapping the Login button with valid credentials logs the user in and shows the dashboard.”
            
- **Nearby scenarios (adjacent behavior)**
    
    - Behavior in the same area that must _not_ regress while fixing the bug.
        
    - Example:
        
        - S‑102: “Desktop Chrome login still works.”
            
        - S‑103: “Password reset flow still works for the same user.”
            
- **Long‑horizon scenarios (broader flows involving that area)**
    
    - Multi‑step sequences that cross module boundaries and reflect a real user journey.
        
    - Example:
        
        - S‑150: “New user signs up on mobile, confirms email, logs in, creates a widget, logs out, and logs back in later.”
            

When you say:

> “it skipped a broader fix to focus on the current task”

that often means:

- The agent made the **local scenario** pass (the immediate bug),
    
- But ignored or broke a **nearby** or **long‑horizon** scenario (login now works on Safari, but broke desktop; or login works alone but fails inside a longer flow).
    

## How this changes your workflow

Today:

- You watch Cursor; when you see it only changing one file, you think “hmm, but what about this other code path?” and intervene.
    

Factory‑style:

- You encode those “other code paths” as explicit scenarios:
    
    - One or two **nearby** scenarios per bug.
        
    - A handful of **long‑horizon** user journeys touching that area.
        
- The overnight loop runs: bug scenario + nearby + long‑horizon.
    
- If the bug scenario passes but a nearby scenario fails, the Judge labels it as regression and your satisfaction score stays low.36kr+3
    
- The Debugger agent focuses on fixing the broader behavior without you watching individual edits.
    

Concretely, when you open your morning report, you might see:

- S‑101: SATISFIED (score 0.95)
    
- S‑102: NOT_SATISFIED (regression, score 0.2)
    
- S‑150: NOT_SATISFIED (regression, score 0.4)
    

That’s the system telling you “the local bug is fixed but the broader login flows are now broken,” which is exactly the broader fix you currently catch manually.


[^1]: https://simonwillison.net/2026/Feb/7/software-factory/

[^2]: https://www.strongdm.com/blog/the-strongdm-software-factory-building-software-with-ai

[^3]: https://factory.strongdm.ai/products

[^4]: https://eu.36kr.com/en/p/3675741413302915

[^5]: https://vercel.hyper.ai/en/stories/eb7b9cb01c2d0faabbebc97981a06997

[^6]: https://github.com/strongdm/attractor

[^7]: https://www.linkedin.com/posts/tprendergast_this-week-we-hosted-a-small-event-in-palo-activity-7425633593730871297-9xFz

[^8]: https://www.alldevblogs.com/article/simon-willison-1/how-strongdms-ai-team-build-serious-software-without-even-looking-at-the-code

[^9]: https://www.reddit.com/r/AIGuild/comments/1r28ibp/how_are_you_steering_coding_agents_i_built_a/

[^10]: https://simonw.substack.com/p/how-strongdms-ai-team-build-serious

[^11]: https://news.ycombinator.com/item?id=46955602

[^12]: https://www.letsdatascience.com/news/strongdm-builds-software-factory-with-agentic-testing-c5aae799

[^13]: https://www.alldevblogs.com/article/simon-willison/how-strongdms-ai-team-build-serious-software-without-even-looking-at-the-code

[^14]: https://docs.strongdm.com/concepts/what-is-strongdm

[^15]: https://news.ycombinator.com/item?id=46924426

---

## Official / 2026 links

- [Software Factory](https://factory.strongdm.ai/) · [Principles](https://factory.strongdm.ai/principles) · [DTU technique](https://factory.strongdm.ai/techniques/dtu)
- [Blog](https://www.strongdm.com/blog/the-strongdm-software-factory-building-software-with-ai) · [CXDB repo](https://github.com/strongdm/cxdb) · [Leash repo](https://github.com/strongdm/leash) · [attractorbench](https://github.com/strongdm/attractorbench)
- Web research: [`research_overnight_stack_web/findings_reference_strongdm_opensource.md`](research_overnight_stack_web/findings_reference_strongdm_opensource.md)
