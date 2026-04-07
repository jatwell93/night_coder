# Research: OpenJudge, AgentScope evaluation, Dify (judge stack)

Web research (5 searches). Focus: LLM grading, traces/observability hooks, official docs/repos, and when a full app platform is more than a lightweight judge.

---

## 1. OpenJudge

**What it is:** Open-source Python evaluation framework for LLM and agent outputs: collect test data → define graders → run at scale → analyze → iterate. Positions itself as a broad grading library plus integrations for observability and RL-style reward signals.

**LLM grading:** 50+ built-in graders (format, text, code/math, multimodal, multi-turn, agent-oriented); custom graders and rubric-style graders are documented. Results can feed reward signals for training/optimization (e.g. mentions of VERL-style pipelines in ecosystem materials).

**Execution traces / observability:** Documented integrations with **LangSmith** and **Langfuse** so grading can run against or alongside traced runs (e.g. external evaluation on historical runs, scheduled/incremental assessment in LangSmith-oriented docs). Treat traces as coming from those platforms when wired to OpenJudge, not necessarily a bespoke trace format inside OpenJudge alone.

**URLs**

| Resource | URL |
|----------|-----|
| GitHub (AgentScope-affiliated repo commonly linked from docs) | https://github.com/agentscope-ai/OpenJudge |
| GitHub (ModelScope listing also appears in search results) | https://github.com/modelscope/OpenJudge |
| Documentation (site root) | https://agentscope-ai.github.io/OpenJudge/ |
| Quick start | https://agentscope-ai.github.io/OpenJudge/get_started/quickstart/ |
| Custom graders | https://agentscope-ai.github.io/OpenJudge/building_graders/create_custom_graders/ |
| LangSmith integration | https://agentscope-ai.github.io/OpenJudge/integrations/langsmith/ |
| Marketing / hosted demo reference | https://openjudge.me/ |

**Note:** If both GitHub orgs host the project, confirm which is canonical for releases and PyPI before pinning dependencies.

---

## 2. AgentScope (Alibaba) — evaluation, judges, benchmarks

**What it is:** Developer-centric multi-agent framework; evaluation is a first-class tutorial area with benchmarks, tasks, metrics, evaluators, and storage.

**Evaluation model (concepts):** Benchmark → Task (inputs, ground truth, metrics) → Metric → Evaluator (orchestration + aggregation) → Evaluator storage. Supports **RayEvaluator** (parallel/distributed) and **GeneralEvaluator** (sequential, debugging-friendly).

**Judge functions / semantic grading:** Native docs emphasize task metrics and evaluators; for richer semantic judging, AgentScope documents **OpenJudge integration** (many pre-built graders: hallucination, relevance, etc.) as an extension path.

**Benchmarks:** Docs mention **ACEBench** as integrated and **GAIA** as in development (status may change; check current tutorial).

**URLs**

| Resource | URL |
|----------|-----|
| Evaluation tutorial (EN) | https://doc.agentscope.io/tutorial/task_eval.html |
| OpenJudge + AgentScope | https://doc.agentscope.io/tutorial/task_eval_openjudge.html |
| Evaluation tutorial (ZH) | https://doc.agentscope.io/zh_CN/tutorial/task_eval.html |
| AgentScope 1.0 paper (Hugging Face Papers) | https://huggingface.co/papers/2508.16279 |

---

## 3. Dify — open-source LLM app platform; overkill vs. a lightweight judge

**What it is:** Open-source platform to build LLM apps and agentic workflows (visual builder, RAG, tools, multiple app modes). Self-hosted via Docker Compose; docs at `docs.dify.ai`.

**When Dify is the wrong abstraction for “just judging”**

- **Lightweight judge:** A small codebase (or notebook/CI job) that loads a dataset, calls an LLM or rule-based scorer, and writes scores — no product UI, no multi-user app shell, no vector DB/RAG unless you need it. Libraries like **OpenJudge** (or plain “LLM-as-judge” prompts) fit here.
- **Dify shines when** you already want a **productized** workflow: drag-and-drop pipelines, knowledge bases, chat/agent surfaces, ops integrations, and team-facing iteration. That stack has **operational and cognitive overhead** (deploy, upgrades, permissions, workflow DSL) versus a script.
- **Middle ground:** Teams using Dify for the app often pair **external LLMOps** (Langfuse, LangSmith, etc.) for traces and evaluation; community patterns exist (e.g. scenario testing articles, `dify-eval`-style projects) for quality measurement *around* Dify rather than replacing a tiny judge with the whole platform.

**URLs**

| Resource | URL |
|----------|-----|
| Dify docs (introduction) | https://docs.dify.ai/ |
| Key concepts (app types) | https://docs.dify.ai/en/use-dify/getting-started/key-concepts |
| External ops / monitoring integrations | https://docs.dify.ai/en/guides/monitoring/integrate-external-ops-tools/README |
| Blog: LangSmith & Langfuse integration | https://dify.ai/blog/dify-integrates-langsmith-langfuse |
| Example: `dify-eval` (community tooling) | https://github.com/hustyichi/dify-eval |
| Article: scenario testing for Dify chatbot quality | https://dev.to/shuntarookuma/how-i-measure-my-dify-chatbot-quality-with-scenario-testing-5bl0 |

---

## Cross-stack takeaway

- **OpenJudge** = reusable grading library + strong ties to **LangSmith/Langfuse** for run-based evaluation.
- **AgentScope** = agent framework with native evaluators/benchmarks; **OpenJudge** documented as the path to richer judges.
- **Dify** = full LLM application platform; use a **lightweight judge** when you only need batch scoring or CI checks without workflows, RAG, or a hosted app surface.
