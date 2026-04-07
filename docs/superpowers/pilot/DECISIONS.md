# Pilot decisions

Source of truth for "Choice" fields: Quint comparison workflow in [`qunit_code_workflows`](../../../qunit_code_workflows), evaluating **all** candidates listed for each pillar in [`Research/Research_Summary_Table.md`](../../../Research/Research_Summary_Table.md) §1 (see plan header *Stack selection rule*). Record the **winner per pillar** and link to `/q-decide` output or `quint-code board` reference.

| Decision | Choice | Rationale (one line) |
|----------|--------|----------------------|
| Reference rubric | StrongDM-style principles (scenarios, DTU, satisfaction) | |
| Orchestration (Attractor) | **Ralph Orchestrator** (hat-based fresh-context loop) — Quint `dec-20260406-001` | Hat-based delegation with fresh context per iteration; cost/time/iteration caps; JSONL audit trail |
| Planner | **Spec Kit** — Quint `dec-20260406-005`; brief: [`planner/IMPLEMENTATION-BRIEF.md`](planner/IMPLEMENTATION-BRIEF.md) | Spec/plan/tasks/acceptance artifacts; Ralph stays runtime orchestrator; headless-compatible |
| Guardrails (Leash) | **NTM** (Named Tmux Manager) | Only candidate with PATH-level command interception, composable with any orchestrator, tamper-evident audit trail for morning review; see decision record below |
| DTU / mocks | **WireMock standalone** — Quint `dec-20260406-002`; compose: `dtu/docker-compose.wiremock.yml` | MCP-native agent operability + REST Admin API; record/replay; Mockoon as documented rollback |
| Judge & scenarios | **OpenJudge** (`py-openjudge`) — Quint `dec-20260406-003`; brief: [`judge/IMPLEMENTATION-BRIEF.md`](judge/IMPLEMENTATION-BRIEF.md); long-form narrative below | Python grading library: LLM + function graders, trajectory evaluation, batch runner, native Langfuse integration; dominates build-yourself and category-collapses Dify/AgentScope |
| Observability (CXDB) | **Langfuse** (self-hosted, phased) — Quint `dec-20260406-004`; brief: [`observability/IMPLEMENTATION-BRIEF.md`](observability/IMPLEMENTATION-BRIEF.md) | Phase 1: OTEL file export on pilot VPS; Phase 2: Langfuse UI on sized host; OpenLLMetry instrumentation, backend-agnostic app code |
| Memory (continuity) | **mcp-memory-service** (sqlite_vec-first) — Quint `dec-20260406-007`; brief: [`memory/IMPLEMENTATION-BRIEF.md`](memory/IMPLEMENTATION-BRIEF.md) | Local-first persistent memory + retrieval for cross-run learning; rollback to Acontext; Beads optional as execution work-graph complement |
| Execution sandbox | **Docker/Podman per task** (named offline/online profiles) — Quint `dec-20260407-001`; brief: [`sandbox/IMPLEMENTATION-BRIEF.md`](sandbox/IMPLEMENTATION-BRIEF.md) | Workspace-scoped mounts, default-deny egress for offline profile; Firejail/bwrap as optional low-RAM lane |
| Secrets / IAM | **Doppler** (service tokens + `doppler run`) — Quint `dec-20260407-002`; brief: [`secrets/IMPLEMENTATION-BRIEF.md`](secrets/IMPLEMENTATION-BRIEF.md) | Single bootstrap secret per trust boundary; 1Password/SOPS as documented alternates |
| Artifact registry | **Git-native run manifests** + Langfuse for traces — Quint `dec-20260407-003`; brief: [`artifact-registry/IMPLEMENTATION-BRIEF.md`](artifact-registry/IMPLEMENTATION-BRIEF.md) | Plans/verdicts/manifests in git; LLM telemetry in Langfuse; SQLite catalog deferred |
| Model / Provider | **OpenRouter-first** + internal role-policy adapter — Quint `dec-20260406-006`; brief: [`model-provider/IMPLEMENTATION-BRIEF.md`](model-provider/IMPLEMENTATION-BRIEF.md) | Per-role routing, typed failover, budget ladder; multi-provider escape hatches |
| Complementary | *pending* | Optional tools (e.g. Aider-style workers) — not load-bearing for pilot architecture |
| Coding model (LLM for agent) | *Configured via Model/Provider policy* (`dec-20260406-006`) | Set primary/fallback models for `coder` (and related) roles in policy config |
| Judge model (LLM for judge) | *Configured via Model/Provider policy* (`dec-20260406-006`) | Set primary/fallback models for `judge` role in policy config; OpenJudge stays the judge library |
| Host | Laptop OR VPS hostname | |
| Start time (local) | | |
| Hard stop time | | |

**Sign-off:** I accept CONSTRAINTS.md and will not intervene until the stop time: _________________ (initials/date)

---

## Decision Record: Guardrails (Leash) → NTM

**Date:** 2026-04-05
**Mode:** Standard (pillar-by-pillar comparison per `qunit_code_workflows`)
**Research basis:** `Research/Research_Summary_Table.md` §1 + §3, detailed write-ups in `Research/ntm.md`, `Research/ralph-orchestrator.md`, `Research/oh_my_opencode_deepwiki.md`, `Research/ruflo_deepwiki.md`, `Research/agent_flywheel_deepwiki.md`, `Research/research_overnight_stack_web/findings_guardrails_ntm.md`

### Problem framing

**Signal:** The overnight autonomous execution loop requires a safety layer that prevents destructive commands (shell, git, file, DB) during unattended operation. Prompt-level guidance is insufficient — enforcement must happen at the OS/PATH level.

**Constraints:**
1. Must work without human approval during the overnight window
2. Must be composable — independent of orchestrator choice
3. Must intercept at a level where prompt-level "please don't" is not enough
4. OSS, budget-compatible

**Acceptance:** A single designated tool that blocks dangerous commands, logs interceptions with audit integrity, and works with any orchestrator that spawns agents in tmux.

### Characterization (comparison dimensions)

| Dimension | Scale | Polarity |
|-----------|-------|----------|
| Command interception depth | none → prompt → hook → PATH → OS-level | higher = better |
| Interception breadth | classes of commands covered | wider = better |
| Configurability | fixed → YAML/regex → programmable | more = better |
| Composability | coupled-to-one-orchestrator → orchestrator-agnostic | more independent = better |
| Audit trail quality | ephemeral → file → tamper-evident hash-chain | more durable = better |
| Unattended operation | requires-human → configurable → native | more autonomous = better |
| Maturity | alpha → tagged releases → stable | more mature = better |

### Variants explored

| # | Variant | Kind | Weakest link |
|---|---------|------|-------------|
| 1 | **NTM** | Dedicated policy engine with PATH-level command interception | Interactive approval model (mitigable: configure policy.yaml to block/allow only, no approval tier) |
| 2 | **Ralph limits** | Resource caps (iterations, runtime, cost, consecutive failures) | Not actually command interception — cannot block any specific destructive command |
| 3 | **oh-my-openagent hooks** | Prompt/hook-level PreToolUse guards | No OS-level interception; research explicitly flags "significant risk gap" for overnight |
| 4 | **Ruflo sandbox modes** | Worker-scoped sandbox (strict/permissive/disabled) | Alpha stability; tightly coupled to claude-flow worker system |
| 5 | **Agent Flywheel** | Installer that bundles NTM internally | Not a tool itself — its leash capability IS NTM |

### Comparison result

**Category collapse:** Variants 2–4 are not variant *Leash* tools — they provide different kinds of safety (resource caps, prompt discipline, execution isolation) that belong to their respective orchestrator's internal configuration. Comparing them to NTM on the Leash dimension is a category error.

**Variant 5** (Agent Flywheel) derives its leash from NTM. Selecting NTM directly is cleaner for the modular pillar model.

**Pareto front:** {NTM} — it dominates all candidates on every Leash-specific dimension.

| Dimension | NTM | Ralph | oh-my-openagent | Ruflo | Agent Flywheel |
|-----------|-----|-------|-----------------|-------|----------------|
| Interception depth | PATH-level | None (resource caps) | Hook-level | Worker-sandbox | NTM-derived |
| Interception breadth | Shell, git, DB, file ops | N/A | Tool-level only | Worker-scoped | NTM-derived |
| Configurability | YAML policy, regex patterns | Config limits | Hook code (TS) | Worker configs | NTM policy |
| Composability | **HIGH** (tmux-agnostic) | LOW (Ralph-only) | LOW (OpenCode-only) | LOW (Ruflo-only) | MEDIUM |
| Audit trail | Tamper-evident, hash-chain | JSONL events | /tmp debug log | .claude-flow/logs | NTM audit |
| Unattended mode | Configurable (remove approval tier) | Native | Native | Native | NTM-based |
| Maturity | v1.11+ tagged releases | v2 stable | Active dev | v3 alpha | Installer |

### Decision

**Winner: NTM (Named Tmux Manager)**

**Invariants:**
- Policy engine must be configured with `block` and `allow` tiers only (no `approval_required`) for overnight mode
- Audit logs must be preserved for morning review (`ntm audit show <session>`)
- NTM's PATH wrappers must be on the execution PATH for whichever orchestrator is selected

**Admissibility (not acceptable):**
- Running overnight without any command interception ("no leash" variant)
- Relying solely on prompt-level safety during unattended execution

**Rollback plan:** NTM's policy engine is a YAML file and PATH wrapper scripts. Removal is `ntm safety uninstall` + removing `.ntm/policy.yaml`. No deep system integration to unwind.

**Weakest link:** PATH-based interception can be bypassed if the orchestrator uses absolute paths to binaries or executes commands inside Docker containers without NTM's wrappers installed. The pilot must verify the chosen orchestrator's execution path goes through NTM's interception layer.

**Stepping stone:** NTM's pipeline and swarm features could absorb partial orchestrator responsibilities in future iterations, but for the pilot it is scoped strictly to the Leash role.

**Refresh trigger:** Re-evaluate if (a) the chosen orchestrator executes commands outside tmux/PATH, (b) NTM's upstream maintainer stops accepting bug reports, or (c) a dedicated agent-safety tool emerges that operates at a deeper level (e.g., seccomp/eBPF).

**Valid until:** 2026-07-05 (3 months — reassess after pilot retrospective)

### Links

- NTM repository: https://github.com/Dicklesworthstone/ntm
- NTM install: `go install github.com/Dicklesworthstone/ntm@latest`
- Policy file: `.ntm/policy.yaml`
- Safety CLI: `ntm safety status`, `ntm safety check`, `ntm safety blocked`
- Audit CLI: `ntm audit show <session>`

---

## Decision Record: DTU / mocks → WireMock (primary designate)

**Date:** 2026-04-05  
**Mode:** Standard (pillar-by-pillar comparison per `qunit_code_workflows`)  
**Research basis:** [`Research/Research_Summary_Table.md`](../../../Research/Research_Summary_Table.md) §1 (DTU rows), [`Research/research_overnight_stack_web/findings_dtu_mockoon_keploy_msw.md`](../../../Research/research_overnight_stack_web/findings_dtu_mockoon_keploy_msw.md), [`Research/research_overnight_stack_web/findings_dtu_extended_landscape.md`](../../../Research/research_overnight_stack_web/findings_dtu_extended_landscape.md), [`Research/mockoon.md`](../../../Research/mockoon.md), [`Research/keploy.md`](../../../Research/keploy.md), [`Research/msw.md`](../../../Research/msw.md), gap wave 2 AWS/browser: [`Research/research_overnight_stack_web/gap_wave2/findings_gap_dtu_localstack_browserless.md`](../../../Research/research_overnight_stack_web/gap_wave2/findings_gap_dtu_localstack_browserless.md)

### Problem framing (PROB — inherited)

**Signal:** Overnight autonomous coding must exercise integration-shaped code against **external dependencies** without calling live third-party APIs (cost, rate limits, flakiness, data handling). The twin must be reachable as a **normal HTTP URL** from any language the agent may produce.

**Constraints:**

1. Headless operation — mock service starts via compose/CLI and stays up unattended.
2. **Language-agnostic** consumer — not bound to a single runtime (exclude in-process-only tools as *pillar default*).
3. Budget-compatible — OSS/self-hosted; no per-call metered APIs for the stubbed dependency.
4. Reversible — swapping mock implementation must not invalidate the **external scenario** contract (URL + expected behavior), only implementation details under `dtu/` or compose.

**Optimization targets:**

1. Lowest **overnight ops risk** (stable container, predictable ports, deterministic responses for judge).
2. **Expressiveness** for future scenarios (templating, faults, delays, record/replay) without mandatory kernel features.
3. **Agent/harness maintainability** — mocks can evolve with repo or agent assistance (e.g. OpenAPI, MCP).

**Acceptance:** One **designated** primary tool for HTTP-style DTU; conditional secondaries documented where spec-, contract-, async-, or AWS-shaped deps apply. Pilot scenario `SCN-PILOT-001` remains satisfiable (GET → JSON); existing Mockoon artifacts may remain until deliberately replaced.

**Blast radius / reversibility:** Tactical — change compose files and env URLs; no schema migration.

---

### Characterization (/q-char)

**Selection policy (pre-declared):** Among variants that are **out-of-process HTTP twins** with Docker or equivalent unattended startup, prefer the option that **maximizes** {expressiveness + record/replay without eBPF, agent-adjacent ergonomics} subject to **not** requiring a full Kubernetes platform for v1. **MSW** and **Agent VCR** are evaluated only as **out-of-band** references (wrong layer for pillar default). **LocalStack** / **Browserless** are out of scope for this decision except as **add-ons** when dependencies are AWS- or browser-shaped.

**Parity rules (fair comparison):**

- Same **evaluation task:** HTTP mock serves `GET /api/status` → `200` + `{"status":"ok"}` (or equivalent path from scenario), base URL via env (e.g. `UPSTREAM_URL`).
- Same **host assumption:** Linux VPS or laptop, Docker available.
- Same **unattended criterion:** no interactive UI required to keep mocks running overnight.
- **Note:** Keploy and Microcks require additional setup (record session, K8s/Helm); parity is “documented path exists for pilot-class host,” not “equal time-to-first-stub.”

| Dimension | Scale | Polarity |
|-----------|-------|----------|
| Out-of-process HTTP twin | in-process only → dedicated server | server = required for pillar default |
| Overnight / headless ops | fragile → single container → platform | simpler = better for v1 |
| Language agnosticism | JS-only → HTTP any client | any client = better |
| Expressiveness | static JSON → templating → state + faults | more = better (for growth) |
| Record / replay | none → proxy/CLI → eBPF multi-hop | higher capability = better, **if** ops cost acceptable |
| Spec / contract alignment | ad hoc → OpenAPI → Pact → multi-spec platform | match org truth = better (conditional) |
| Protocol breadth | HTTP only → TCP/SMTP → DB+queue capture | broader = better **when** deps require it |
| Host / kernel coupling | pure userland → JVM → eBPF | looser coupling = better for default |
| Agent maintainability | hand-edit only → OpenAPI → MCP-assisted | higher = better for long-run factory |

---

### Variants explored (/q-explore)

| # | Variant | Kind | Weakest link | Stepping stone |
|---|---------|------|--------------|----------------|
| 1 | **WireMock** | JVM HTTP mock + Docker; templating; record/replay; WireMock MCP | JVM footprint vs Mockoon | Strong simulation + agent tooling path |
| 2 | **Mockoon** | JSON + CLI/Docker; minimal static routes | Limited advanced simulation vs WireMock | Fastest pilot hello-world; already in slice |
| 3 | **Hoverfly** | Go proxy capture → simulate | Capture discipline / simulation quality | Best when proxy-first workflow is natural |
| 4 | **MockServer** | JVM HTTP mock + proxy (WireMock peer) | Redundant ecosystem vs WireMock for *new* choice | Valid if team already standardized on MockServer |
| 5 | **Keploy** | eBPF record-replay; HTTP + DB + queues | Kernel/container caps; record-before-replay lifecycle | Full-stack offline replay when accepted |
| 6 | **Prism** | OpenAPI/Postman-driven mock + validate | Meaningless without maintained spec | When API spec is SoT |
| 7 | **Pact stub server** | Pact file / Broker-driven | Requires Pact contract discipline | Consumer-driven contract shops |
| 8 | **Microcks** | Multi-spec platform; AsyncAPI/Kafka; K8s | Ops weight for overnight slice | Factory-scale async + governance |
| 9 | **Mountebank** | Multi-protocol imposters | Complexity for HTTP-only cases | SMTP/TCP/non-HTTP wires |
| 10 | **Mockintosh** | REST + Kafka/Rabbit scenarios | Smaller community than Microcks for async platform | Middle ground for broker mocks |
| 11 | **Imposter** | Scriptable plugins (OpenAPI/SOAP/SF) | Another runtime to own | Scripted twins without Microcks |
| 12 | **Karate Netty** | Standalone JAR mock | Karate-centric | Teams already on Karate |
| 13 | **MSW** | In-process Node/browser intercept | **Not** language-agnostic server | Superb **in-repo** JS/TS tests — not pillar DTU |
| 14 | **LocalStack** (gap 2) | AWS API emulation | Not generic HTTP Stripe/Slack twin | When deps are AWS-shaped |
| 15 | **Browserless / Playwright** (gap 2) | Headless browser pool | Not HTTP API DTU | UI/E2E scenarios |

---

### Comparison (/q-compare)

**Pareto front (non-dominated on the characterization dimensions for *default HTTP DTU*):**  
{**WireMock**, **Mockoon**, **Hoverfly**, **Keploy**, **Prism**, **Microcks**, **Mountebank**} — each wins on at least one dimension where others are strictly worse (e.g. Mockoon on minimal ops, Keploy on capture breadth, Prism on spec-native mocks, Mountebank on non-HTTP protocols, Microcks on governed multi-protocol/async).

**Dominated / excluded from primary designate:**

- **MSW** — dominated for **pillar default** on *language agnosticism* and *out-of-process twin*; retained as complementary for JS/TS test harnesses.
- **MockServer** — largely **peer** to WireMock; **WireMock** chosen as the JVM HTTP representative for MCP/record narrative and community momentum (either is admissible if pre-existing standard says MockServer).
- **Agent VCR** — wrong problem (MCP JSON-RPC), not HTTP DTU.

**Fair-check (parity audit):** All HTTP-server variants (1–4, 6–12) can satisfy `SCN-PILOT-001` with a single route and Docker or JAR/CLI. Keploy adds a **recording** prerequisite before replay. Microcks implies **platform** install — explicitly out of parity for “single-compose overnight slice” unless the org already runs it.

**Selection policy applied:** Prefer **WireMock** among {WireMock, Mockoon, Hoverfly} on **expressiveness + record/replay without eBPF + MCP/agent path**, while accepting slightly higher complexity than Mockoon. **Mockoon** remains **admissible tactical alternate** and **current pilot default** until compose is migrated.

**Conditional winners (not replacing WireMock as HTTP default — add alongside when deps match):**

| Condition | Designate |
|-----------|-----------|
| OpenAPI/Postman is contract of record | **Prism** (or generate stubs consumed by WireMock — composable) |
| Pact + Broker workflow | **Pact stub server** |
| Kafka/Rabbit as first-class | **Mockintosh** or **Microcks** |
| Non-HTTP protocols (SMTP, TCP, …) | **Mountebank** |
| DB + HTTP capture without hand mocks | **Keploy** |
| AWS APIs | **LocalStack** |
| Browser E2E | **Playwright Docker / Browserless** |

---

### Decision (/q-decide) — DRR contract

**Winner (primary designate): WireMock**

**Invariants:**

1. HTTP dependencies for autonomous runs are satisfied by an **out-of-process** mock with a stable base URL and version-pinned container image (or pinned CLI).
2. Scenario files under `docs/superpowers/pilot/scenarios/` remain **authoritative** for expected behavior; DTU config implements that behavior — agent does not edit scenarios or DTU assets during autonomous coding (per pilot constraints).
3. **MSW** is not relied upon as the **sole** DTU for multi-language or repo-wide overnight runs.

**Pre-conditions:**

- `docker compose` (or documented WireMock standalone) brings the twin up before the orchestrator loop.
- `UPSTREAM_URL` (or equivalent) points at the mock; health check documented in runbook.

**Post-conditions:**

- `curl` or scenario script against `/api/status` returns expected JSON after run.
- Mock definitions live under repo-controlled paths (e.g. `docs/superpowers/pilot/dtu/` or successor) and are committed.

**Admissibility (not acceptable):**

- Calling live billed third-party APIs during the unattended window for stubbable HTTP deps.
- Designating **in-process JS-only** mocking as the **only** DTU for the overnight factory (blocks non-JS sandboxes).

**Rollback plan:** Revert compose to **Mockoon** (or prior tool); keep route JSON equivalent. No data migration — only URL and container image.

**Weakest link:** **JVM/Docker resource usage** and **stub maintenance discipline** — teams that never adopt record/OpenAPI will hand-curate JSON; quality depends on human/agent process, not the tool alone.

**Refresh triggers / valid_until:**

- Re-evaluate before **2026-07-05** (3 months) or sooner if: (a) WireMock MCP/agent path proves unstable in practice, (b) orchestrator requires non-Docker execution without JVM, (c) first-class deps become **async** or **non-HTTP** and a second tool (Microcks, Mountebank, Keploy) becomes load-bearing.

**Stepping stones:**

- **Mockoon** — keep for current vertical-slice files until WireMock compose is validated.
- **Hoverfly** — evaluate if proxy capture becomes the preferred authoring path.
- **Keploy** — evaluate when DB/queue capture outweighs eBPF ops cost.

### Links

- WireMock: https://www.wiremock.org/
- WireMock Docker: see official docs / Docker Hub
- WireMock MCP (agent workflows): https://www.wiremock.io/post/wiremock-mcp-ai-coding-agents
- WireMock CLI recording: https://www.wiremock.io/post/local-api-recording-with-wiremock-cli
- Mockoon (tactical alternate): https://mockoon.com/cli/
- Extended DTU landscape: [`Research/research_overnight_stack_web/findings_dtu_extended_landscape.md`](../../../Research/research_overnight_stack_web/findings_dtu_extended_landscape.md)

### Quint MCP artifacts

| Artifact | ID |
|---|---|
| ProblemCard | `prob-20260406-002` |
| SolutionPortfolio | `sol-20260406-002` |
| DecisionRecord | `dec-20260406-002` (valid until 2026-10-06) |

Full decision body: `.quint/decisions/dec-20260406-002.md`

### Implementation files

| File | Purpose |
|---|---|
| `docs/superpowers/pilot/dtu/docker-compose.wiremock.yml` | WireMock service on port 3000 |
| `docs/superpowers/pilot/dtu/mappings/pilot-status.json` | Stub: GET /api/status → `{"status":"ok"}` |

---

## Decision Record: Judge & scenarios → OpenJudge (`py-openjudge`)

**Date:** 2026-04-05
**Mode:** Standard (pillar-by-pillar comparison per `qunit_code_workflows`)
**Research basis:** [`Research/Research_Summary_Table.md`](../../../Research/Research_Summary_Table.md) §1 (Judge rows), [`Research/OpenJudge.md`](../../../Research/OpenJudge.md), [`Research/dify.md`](../../../Research/dify.md), [`Research/agentscope.md`](../../../Research/agentscope.md), [`Research/build-yourself-one.md`](../../../Research/build-yourself-one.md), [`Research/langfuse_deep_wiki.md`](../../../Research/langfuse_deep_wiki.md), [`Research/research_overnight_stack_web/findings_judge_openjudge_agentscope_dify.md`](../../../Research/research_overnight_stack_web/findings_judge_openjudge_agentscope_dify.md), [`Research/research_overnight_stack_web/gap_wave2/findings_gap_openjudge_canonical.md`](../../../Research/research_overnight_stack_web/gap_wave2/findings_gap_openjudge_canonical.md), [`Research/strongdm_deepseek.md`](../../../Research/strongdm_deepseek.md)

### Problem framing

**Signal:** The overnight autonomous execution loop requires an external evaluator that reads agent-proof scenario specifications and execution traces, then renders a structured satisfaction verdict. The current pilot uses a ~50-line `pilot_judge.py` with a single hard-coded OpenAI prompt — this has no batch evaluation, no trajectory analysis, no multi-dimensional scoring, and no integration with the observability layer. As scenarios scale beyond the pilot, this script either grows into a bespoke framework or gets replaced by one.

**Constraints:**

1. Must be a **library**, not a platform — the Judge is one pillar in a modular architecture; it must compose with whatever orchestrator wins, not introduce its own infrastructure.
2. Must accept **arbitrary inputs** (scenario markdown text + execution traces in various formats) and produce **structured satisfaction scores** (JSON-shaped, storable in observability/CXDB).
3. **Python-native** (the pilot stack is Python 3.12+).
4. Budget-compatible — no per-evaluation metered costs beyond the underlying LLM API calls themselves.
5. Must not duplicate orchestration or introduce a second application platform.

**Optimization targets:**

1. **Scenario-trace alignment** — how naturally does the tool map to "scenario markdown + trace → satisfaction score"?
2. **Expressiveness** — multi-dimensional scoring, trajectory step analysis, rubric generation, batch evaluation with concurrency.
3. **Observability integration** — connects to Langfuse/CXDB so scores flow into the morning review dashboard.

**Acceptance:** One designated tool that can evaluate scenario-trace pairs, return structured scores, support growth to batch evaluation of multiple scenarios, and integrate with the Observability pillar (Langfuse). The existing pilot scenario `SCN-PILOT-001` remains satisfiable. The current `pilot_judge.py` may be retained as a reference until the new judge is validated.

**Blast radius / reversibility:** Tactical — swap a Python dependency and rewrite the judge script; no infrastructure or schema migration.

---

### Characterization (/q-char)

**Selection policy (pre-declared):** Among candidates that can evaluate scenario-trace pairs and return structured satisfaction scores, prefer the option that **maximizes** {built-in grading capabilities + observability integration + growth path to batch multi-scenario evaluation} subject to **not** requiring platform-scale infrastructure (databases, container orchestration, admin UI) for the judge component alone.

**Parity rules (fair comparison):**

- Same **evaluation task:** Read `SCN-PILOT-001-upstream-ok.md` scenario + `sample_trace.txt` → return `{satisfied: bool, score: float, reasoning: string}`.
- Same **host assumption:** Python 3.12+ on Linux VPS or laptop.
- Same **model assumption:** OpenAI-compatible API (e.g. `gpt-4o-mini`); judge cost is the LLM API call, not the tool itself.
- **Note:** Dify and AgentScope require significant additional infrastructure beyond the judge function itself; parity is "documented path to produce a satisfaction score from scenario + trace," not "equal deployment complexity."

| Dimension | Scale | Polarity |
|-----------|-------|----------|
| Scenario-trace evaluation | hard-coded prompt → template kwargs → structured grading pipeline | more structured = better |
| Trajectory analysis | none → single-prompt → step-by-step multi-dimension | deeper = better |
| Deterministic checks | none → manual if/else → composable function graders | composable = better |
| Batch evaluation | manual loop → concurrent runner with progress | concurrent = better |
| Rubric generation | manual prompt engineering → auto-generated from scenario | auto = better for growth |
| Observability integration | none → DIY API → native platform integration | native = better |
| Infrastructure weight | pip install → Docker containers → full platform (DB, queue, web) | lighter = better for pillar modularity |
| Composability | coupled to framework → standalone library → platform-locked | standalone = better |
| Maturity | custom script → alpha → tagged releases | more mature = better |

---

### Variants explored (/q-explore)

| # | Variant | Kind | Weakest link | Stepping stone |
|---|---------|------|--------------|----------------|
| 1 | **OpenJudge** (`py-openjudge`) | Python grading library: LLMGrader, FunctionGrader, TrajectoryComprehensiveGrader, GradingRunner, SimpleRubricsGenerator; Langfuse + LangSmith integrations | Young project (first release Dec 2025); PyPI naming requires `py-openjudge` not `openjudge` | Full grading pipeline for overnight factory |
| 2 | **Dify** | Full LLM application platform: visual workflow builder, RAG, tools, multi-app modes; Docker Compose with PostgreSQL, Redis, Celery | Massive infrastructure overhead for a judge function; no Python SDK; redundant orchestration | When you need an end-user LLM app surface — not a judge |
| 3 | **AgentScope** (eval patterns) | Agent framework with Task/Metric/Evaluator/Storage; RayEvaluator for distributed eval; OpenTelemetry trace capture | No built-in LLM judge implementations — all judge logic must be manually written; own docs recommend OpenJudge | Reference architecture for Task/Metric/Storage patterns at scale |
| 4 | **Build-yourself harness** (`pilot_judge.py`) | Custom Python script: reads scenario + trace, single OpenAI API call with `response_format=json_schema` | No batch eval, no trajectory analysis, no multi-dimensional scoring, no Langfuse integration, no upstream maintenance | Already in place; retain as reference until OpenJudge validated |

---

### Comparison (/q-compare)

**Category collapse:** Variants 2–3 are not variant *Judge tools* in the same category as OpenJudge:

- **Dify** (variant 2) is an **application platform** that requires PostgreSQL, Redis, Celery workers, and a web server — for a component that should be a library call. Research across multiple sources explicitly concludes Dify is "NOT a good fit for your LLM Judge component." It solves a different problem (building end-user LLM apps). **Category error.**
- **AgentScope** (variant 3) provides evaluation **infrastructure** (Task, MetricBase, Evaluator) but **no built-in LLM judge implementations**. AgentScope's own documentation recommends OpenJudge as the path to richer semantic judging. Selecting AgentScope alone for judging means selecting the framework that says "use OpenJudge for this." **Points to OpenJudge.**

**Reduced comparison:** OpenJudge vs. build-yourself (`pilot_judge.py`).

| Dimension | OpenJudge | Build-yourself |
|-----------|-----------|----------------|
| Scenario-trace evaluation | `LLMGrader` with template kwargs; arbitrary parameters via `**kwargs` | Hard-coded single prompt |
| Trajectory analysis | `TrajectoryComprehensiveGrader`: step-by-step across 4 dimensions (contribution, relevance, accuracy, efficiency) | None |
| Deterministic checks | `FunctionGrader` with custom async functions | Manual if/else in script |
| Batch evaluation | `GradingRunner` with configurable concurrency + progress tracking | Sequential manual loop |
| Rubric generation | `SimpleRubricsGenerator` from scenario description + sample queries | Manual prompt engineering per scenario |
| Observability integration | Native Langfuse + LangSmith integrations (fetch traces, write scores) | DIY API calls |
| Infrastructure weight | `pip install py-openjudge` (pure Python library) | `pip install openai` (already present) |
| Composability | Standalone library, model-agnostic (any OpenAI-compatible API) | Standalone script |
| Maturity | v0.2.3 (March 2026), Apache-2.0, active 6-release cadence | N/A — you maintain everything |

**Pareto front:** {**OpenJudge**} — it dominates the build-yourself approach on every dimension except "zero new dependencies" (trivially mitigated: `pip install py-openjudge` pulls OpenAI SDK as a transitive dependency, which the pilot already uses).

**Langfuse cross-pillar note:** Langfuse (Observability pillar candidate) has built-in `EvalTemplate` LLM-as-judge features, but these are **trace-scoped** (evaluate individual traces, not holistic scenario satisfaction across an overnight session). For the full "read external scenario markdown + comprehensive trace + multi-outcome evaluation" pattern, Langfuse's built-in evals are insufficient as the **primary** judge. The recommended architecture: **OpenJudge** evaluates, **Langfuse** stores and surfaces the scores via native integration. This makes the two pillars complementary, not competing.

---

### Decision (/q-decide) — DRR contract

**Winner (primary designate): OpenJudge (`py-openjudge`)**

**Invariants:**

1. Scenario satisfaction is evaluated by an **external grading library** that reads scenario text and execution traces as inputs — the coding agent never sees scenario files, and cannot influence the judge's scoring logic.
2. The judge produces **structured output** (`GraderScore` with score, reasoning, and metadata) storable in the observability layer for morning review.
3. Both **LLM-based** (`LLMGrader`) and **deterministic** (`FunctionGrader`) checks are composable within the same evaluation — LLM scoring alone is not sufficient for binary pass/fail checks (e.g., "stdout is exactly SATISFIED").

**Pre-conditions:**

- `py-openjudge>=0.2.3` is installed in the judge virtual environment.
- An OpenAI-compatible API key is available via environment variable (same as current `pilot_judge.py`).
- Scenario files exist under `docs/superpowers/pilot/scenarios/` and trace artifacts under `docs/superpowers/pilot/traces/`.

**Post-conditions:**

- Judge output is valid JSON conforming to `GraderScore` schema (score, reason, metadata).
- Scores are written to Langfuse (when Observability pillar is wired) or to local JSON files for morning review.

**Admissibility (not acceptable):**

- Deploying a **full application platform** (Dify-class: databases, queues, web servers) solely for the judge function.
- Relying on the coding agent's **self-reported** success as the satisfaction signal — the judge must be external and read the immutable scenario spec.
- Using **only** LLM-based scoring without deterministic checks for binary outcomes (stdout matching, exit code verification).

**Rollback plan:** Revert to `pilot_judge.py` (retained as reference). No infrastructure to tear down — swap the Python import and adjust the CLI interface. The scenario and trace file formats are tool-agnostic.

**Weakest link:** **Project maturity.** OpenJudge's first release was December 2025; the library is actively developed but young. Two GitHub orgs (`agentscope-ai` and `modelscope`) host it — `agentscope-ai/OpenJudge` is canonical for PyPI. If upstream maintenance stalls, the rollback to a custom script is straightforward since the grading pattern (template + LLM call + structured output) is well-understood from the pilot.

**Stepping stones:**

- **`pilot_judge.py`** — retain as reference/fallback until OpenJudge grader is validated on the pilot fixture.
- **Langfuse built-in evals** — use for lightweight per-trace scoring alongside the primary OpenJudge evaluation once Observability pillar is wired.
- **AgentScope eval patterns** — reference architecture for Task/Metric/Storage abstractions when scenarios scale beyond the pilot to benchmark-grade evaluation.

**Refresh triggers / valid_until:**

- Re-evaluate before **2026-07-05** (3 months) or sooner if: (a) OpenJudge upstream stalls (no release for >3 months), (b) the `py-openjudge` PyPI package introduces breaking API changes that aren't backward-compatible, (c) a purpose-built "scenario satisfaction" library emerges that handles both scenario storage and grading (eliminating the need to manage scenario files separately), or (d) Langfuse's built-in eval features mature to handle full scenario-scoped evaluation natively.

### Migration path from `pilot_judge.py`

**Current:** `pilot_judge.py` constructs a raw prompt, calls `openai.chat.completions.create` with `response_format=json_schema`, parses JSON.

**Target:** Replace with OpenJudge `LLMGrader`:

```python
from openjudge.graders.llm_grader import LLMGrader
from openjudge.models.openai_chat_model import OpenAIChatModel

model = OpenAIChatModel(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])

scenario_grader = LLMGrader(
    name="pilot_scenario_judge",
    model=model,
    template="""You are an impartial judge. Given the scenario specification
and an execution trace, decide whether the expected outcomes are satisfied.

SCENARIO:
{scenario}

TRACE:
{trace}
""",
    description="Evaluates pilot scenario satisfaction from trace evidence",
)

result = await scenario_grader.aevaluate(
    scenario=scenario_text,
    trace=trace_text,
)
# result.score, result.reason, result.metadata
```

Add a `FunctionGrader` for deterministic stdout checks:

```python
from openjudge.graders.function_grader import FunctionGrader
from openjudge.graders.schema import GraderScore

async def check_stdout(stdout: str, **kwargs) -> GraderScore:
    satisfied = stdout.strip() in ("SATISFIED", "FAIL")
    return GraderScore(
        name="stdout_format",
        score=1.0 if "SATISFIED" in stdout else 0.0,
        reason=f"stdout was '{stdout.strip()}'",
    )

stdout_grader = FunctionGrader(func=check_stdout, name="stdout_check")
```

**Requirements change:** Replace `openai>=1.40.0` with `py-openjudge>=0.2.3` in `docs/superpowers/pilot/judge/requirements.txt` (OpenJudge depends on the OpenAI SDK transitively).

### Links

- OpenJudge GitHub (canonical): https://github.com/agentscope-ai/OpenJudge
- OpenJudge docs: https://agentscope-ai.github.io/OpenJudge/
- PyPI: https://pypi.org/project/py-openjudge/
- Install: `pip install py-openjudge`
- Custom graders guide: https://agentscope-ai.github.io/OpenJudge/building_graders/create_custom_graders/
- Langfuse integration: https://agentscope-ai.github.io/OpenJudge/integrations/langfuse/
- AgentScope eval + OpenJudge tutorial: https://doc.agentscope.io/tutorial/task_eval_openjudge.html
- Gap wave 2 (canonical package): [`Research/research_overnight_stack_web/gap_wave2/findings_gap_openjudge_canonical.md`](../../../Research/research_overnight_stack_web/gap_wave2/findings_gap_openjudge_canonical.md)

### Quint board / MCP

Paste or sync this section into your `quint_decision` artifact when using MCP; optional: `quint-code board` reference after commit.
