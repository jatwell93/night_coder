# Observability: Langfuse & OpenLLMetry / Traceloop

**Research scope:** LLM observability, traces, sessions, LLM-as-judge evaluations, self-hosting, OpenTelemetry paths; OpenLLMetry/Traceloop instrumentation, CrewAI, MCP.  
**Method:** Up to five web searches (2025–2026 context) plus verification against official Langfuse OpenTelemetry documentation.  
**Date:** April 2026.

---

## 1. Langfuse

### 1.1 Role and data model

Langfuse is an open-source LLM observability product (MIT-licensed) used to trace LLM-related work: latency, token usage, cost, and quality signals. It is often described as a tracing-oriented layer for LLM applications, grouping work into traces and finer-grained **observations** (e.g. generations, spans, events). The platform’s conceptual model is documented here:

- https://langfuse.com/docs/observability/data-model

### 1.2 Traces and SDK overview

Tracing is exposed through Langfuse SDKs and integrations; the high-level SDK and tracing overview:

- https://langfuse.com/docs/observability/sdk/overview

Langfuse documents that its SDKs are built on **OpenTelemetry**, which allows combining Langfuse instrumentation with other OTEL-instrumented libraries in the same process when configured appropriately.

### 1.3 Sessions

**Sessions** group multiple traces (and observations) that belong to one user journey or conversation. You propagate a `sessionId` (US-ASCII, max 200 characters) so the UI can show session-level views and replay-style grouping. Documentation:

- https://langfuse.com/docs/tracing/sessions  
- https://langfuse.com/docs/observability/features/sessions  

### 1.4 LLM-as-judge evaluations and scores

Langfuse supports **model-based evaluation** (“LLM-as-a-judge”) where a judge model scores outputs against a rubric, with reasoning stored for analysis. Scores can be attached to **observations** (recommended for production), **traces**, or **experiment** runs. Score types include numeric and **categorical** labels (e.g. correctness or support triage buckets).

Primary documentation:

- https://langfuse.com/docs/scores/model-based-evals  
- https://langfuse.com/docs/scores/evals  

Notable changelog entries (execution tracing for evaluators, categorical judges):

- https://langfuse.com/changelog/2025-10-16-llm-as-a-judge-execution-tracing  
- https://langfuse.com/changelog/2026-03-20-categorical-llm-as-a-judge-scores  

Related cookbook example:

- https://langfuse.com/guides/cookbook/evaluation_with_langchain  

### 1.5 Self-hosting

Self-hosted deployments use containerized stacks (PostgreSQL, ClickHouse, Redis, object storage, Langfuse services, etc.). Version alignment matters: Langfuse documents minimum **platform** versions for newer Python/TypeScript SDK generations (e.g. self-hosted instances need sufficiently new Langfuse server images for SDK v3/v4 features).

Entry points for deployment documentation (verify current compose and version matrix on site):

- https://langfuse.com/docs/deployment/self-host  

Community write-ups (non-official; useful for resource sizing narratives):

- https://dev.to/signal-weekly/self-host-langfuse-with-docker-llm-observability-without-the-cloud-bill-5cc3  

### 1.6 OpenTelemetry: ingest, export, and interoperability

**Inbound (treat Langfuse as an OTLP backend):** Langfuse exposes an OTLP HTTP endpoint for traces at `/api/public/otel` (with signal-specific `/v1/traces` where needed). Supported transports are OTLP over HTTP (JSON and protobuf); **gRPC OTLP is documented as not supported yet**. Authentication uses Basic auth derived from Langfuse public/secret keys, plus documented headers for ingestion versioning on cloud fast-preview paths.

**SDK v3 OTEL-native path:** Langfuse SDK v3 is described as a thin layer on the official OpenTelemetry client that maps spans into Langfuse observation types and adds LLM-oriented helpers (tokens, cost, prompt linking, scores). Coexistence with “export everything” vs LLM-focused spans is controlled via filtering in advanced SDK docs.

**Ecosystem:** Official docs explicitly name **OpenLLMetry** and **OpenLIT** as examples of OTEL GenAI instrumentation that can feed Langfuse, extending language/framework coverage (e.g. Java, Go, additional frameworks) relative to first-party SDKs.

Canonical reference:

- https://langfuse.com/docs/opentelemetry  

OpenLLMetry end-to-end example linked from the same page:

- https://langfuse.com/docs/opentelemetry/example-openllmetry  

Coexistence with existing OTEL setups:

- https://langfuse.com/faq/all/existing-otel-setup  

GenAI semantic conventions (upstream OTEL):

- https://opentelemetry.io/docs/specs/semconv/attributes-registry/gen-ai/  

---

## 2. OpenLLMetry / Traceloop

### 2.1 What OpenLLMetry is

**OpenLLMetry** is an open-source initiative (maintained under the Traceloop organization) that adds **OpenTelemetry-based** instrumentation for LLM applications: automatic spans/metrics for many providers and frameworks, exportable to Traceloop’s product or to any OTLP-compatible backend.

Introduction and positioning:

- https://www.traceloop.com/blog/openllmetry  

Documentation hub:

- https://traceloop.com/docs/openllmetry  
- https://traceloop.com/docs/openllmetry/getting-started  
- https://traceloop.com/docs/openllmetry/introduction  

Repository:

- https://github.com/traceloop/openllmetry  

### 2.2 Instrumentation breadth and recent direction

Traceloop documents multi-language support (commonly cited: Python, TypeScript, Go, Ruby) and broad provider coverage. Recent upstream activity (2025) includes expanded instrumentation—for example **OpenAI Agents** tracing/metrics and **event-based** attribute patterns across multiple providers—tracked via the public GitHub project.

Illustrative PRs (verify merge status in repo for your pin):

- https://github.com/traceloop/openllmetry/pull/2966  
- https://github.com/traceloop/openllmetry/pull/2541  

Supported integrations list (living document):

- https://traceloop.com/docs/openllmetry/tracing/supported  
- https://docs.traceloop.com/docs/openllmetry/tracing/supported  

### 2.3 CrewAI support

CrewAI is listed among supported frameworks. Python users install the dedicated package and call the instrumentor (typical pattern: `CrewAIInstrumentor().instrument()`). Implementation landed via community work tracked on GitHub and published to PyPI as `opentelemetry-instrumentation-crewai`.

- https://pypi.org/project/opentelemetry-instrumentation-crewai/  
- https://github.com/traceloop/openllmetry/pull/2457  
- https://github.com/traceloop/openllmetry/issues/2339  

### 2.4 MCP (Model Context Protocol)

Traceloop addresses MCP on two axes:

1. **Instrumentation** – Tracing MCP clients and servers (e.g. Node package `@traceloop/instrumentation-mcp`; Python-side MCP instrumentation merged via OpenLLMetry PRs). Package registry entry for the Node instrumentation:

   - https://www.npmjs.com/package/@traceloop/instrumentation-mcp  
   - https://github.com/traceloop/openllmetry/pull/2829  

2. **MCP server for querying telemetry** – An open-source MCP server that connects MCP-capable clients to trace backends (Jaeger, Grafana Tempo, Traceloop, etc.) for natural-language or tool-driven investigation of production traces:

   - https://github.com/traceloop/opentelemetry-mcp-server  

Third-party announcement summarizing the MCP server launch (verify details against the GitHub README):

- https://longbridge.com/en/news/268120233  

OpenTelemetry semantic conventions for MCP (ecosystem standard, not Traceloop-specific):

- https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/  

### 2.5 Privacy and content logging

Traceloop/OpenLLMetry instrumentations commonly record prompts, completions, and embeddings on spans **by default**; production deployments often disable content capture via environment/configuration flags (e.g. `TRACELOOP_TRACE_CONTENT=false` in Python ecosystems). Confirm exact variable names in the version you deploy.

---

## 3. How the pieces fit together

- **OpenLLMetry** emits **OTLP** traces with GenAI-oriented attributes; **Langfuse** can **ingest** those traces via its OTLP endpoint and map them into the Langfuse observation model—so you can use OpenLLMetry (or similar OTEL libraries) as the instrumentation layer and Langfuse as the analysis/UI/evals store, subject to attribute mapping and version constraints documented on both sides.

- **Langfuse-native** workflows (sessions, scores, LLM-as-judge, experiments) remain primarily documented in Langfuse; **Traceloop** adds depth for **provider/framework auto-instrumentation** and optional export to generic observability stacks.

---

## 4. Source index (full URLs)

| Topic | URL |
| --- | --- |
| Langfuse OTEL backend | https://langfuse.com/docs/opentelemetry |
| Langfuse OpenLLMetry example | https://langfuse.com/docs/opentelemetry/example-openllmetry |
| Langfuse SDK overview | https://langfuse.com/docs/observability/sdk/overview |
| Langfuse sessions | https://langfuse.com/docs/observability/features/sessions |
| Langfuse LLM-as-judge | https://langfuse.com/docs/scores/model-based-evals |
| Langfuse evals hub | https://langfuse.com/docs/scores/evals |
| Langfuse changelog (judge tracing) | https://langfuse.com/changelog/2025-10-16-llm-as-a-judge-execution-tracing |
| Langfuse changelog (categorical judge) | https://langfuse.com/changelog/2026-03-20-categorical-llm-as-a-judge-scores |
| OpenLLMetry intro (blog) | https://www.traceloop.com/blog/openllmetry |
| OpenLLMetry docs | https://traceloop.com/docs/openllmetry |
| Supported integrations | https://traceloop.com/docs/openllmetry/tracing/supported |
| OpenLLMetry GitHub | https://github.com/traceloop/openllmetry |
| CrewAI PyPI instrumentation | https://pypi.org/project/opentelemetry-instrumentation-crewai/ |
| MCP instrumentation (npm) | https://www.npmjs.com/package/@traceloop/instrumentation-mcp |
| OpenTelemetry MCP server (Traceloop) | https://github.com/traceloop/opentelemetry-mcp-server |
| OTEL MCP semantic conventions | https://opentelemetry.io/docs/specs/semconv/gen-ai/mcp/ |

---

*Limitations: Vendor docs and package versions change frequently; confirm endpoints, headers, and minimum server/SDK versions before production cutover. Third-party blog and news URLs are secondary to official documentation.*
