# Artifact registry patterns for AI agent runs

Research note: storing **plans**, **prompts**, **traces**, **verdicts**, and **outputs** in a **queryable** way. Sources are linked; claims below are summarized from public docs and posts (April 2026).

---

## 1. What “artifact registry” means here

In MLOps, an **artifact store** holds large binaries (models, images, parquet); a **backend store** holds **queryable metadata** (runs, parameters, metrics, tags, URIs into the artifact store). That split is the standard pattern to make “what happened?” and “where is the blob?” answerable without scanning object storage.

- **MLflow** documents this explicitly: artifacts (S3, GCS, Azure, MinIO, etc.) vs metadata in PostgreSQL/MySQL/MSSQL (or local `./mlruns` for dev).  
  - [Artifact Stores (tracking)](https://mlflow.org/docs/latest/tracking/artifacts-stores)  
  - [Artifact Stores (self-hosting architecture)](https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/)  
- **Model Registry** sits on the same **database-backed** tracking server; models are registered from logged artifacts.  
  - [Model Registry Workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow/)

For **coding agents**, the same idea applies: **small structured fields** (IDs, timestamps, tags, scores, pointers) in something SQL- or API-queryable; **large payloads** (full traces, diffs, tarballs) in **object storage** or **git LFS/DVC remotes**.

---

## 2. Git-native layouts and conventions

**Git** is strong for **text** (plans, prompts as files, verdicts as markdown/JSON), **history**, and **review**. It is weak for **high-volume telemetry** and **ad hoc filters** across thousands of runs unless you add tooling.

**DVC (Data Version Control)** is the reference pattern for “Git + pointers + remote blobs”:

- Large files are **not** stored in Git; **`.dvc` files** and **`dvc.yaml`** live in Git and point to content in a **cache/remote** (S3, GCS, etc.).  
  - [What is DVC?](https://dvc.org/doc/understanding-dvc)  
  - [Project structure](https://docs.dvc.org/user-guide/project-structure)  
- **Experiment metadata** can live in versioned text (`params.yaml`, `metrics.json`, stages in `dvc.yaml`)—useful analogy for **agent run manifests**.  
  - [ML experiment versioning (DVC blog)](https://dvc.org/blog/ml-experiment-versioning/)  
- **Custom Git refs** (`refs/exps`) store many lightweight experiments without branch pollution; refs are **local by default** unless explicitly shared.  
  - [Git custom references for ML experiments](https://dvc.ai/blog/experiment-refs)

**Layout sketch for agents (convention-only, no new product):**

| Path / artifact        | Role                          | Query in Git?      |
|------------------------|-------------------------------|--------------------|
| `runs/<id>/run.json`   | IDs, model, tags, status      | `rg`, `git log`    |
| `runs/<id>/plan.md`    | Human plan                    | diff, blame        |
| `runs/<id>/verdict.md`| Gate / review outcome         | same               |
| `runs/<id>/manifest.json` | SHA256 + URI to blob store | structured grep    |
| Large trace / bundle   | S3/MinIO key in manifest      | indirect           |

Example repos showing **pipeline + metrics + DVC** layout: [iterative/example-get-started-experiments](https://github.com/iterative/example-get-started-experiments) (structure described in README).

---

## 3. SQLite / DuckDB as catalogs (“light DB index”)

**SQLite** is the minimal **embedded** catalog: one file, SQL, filters, joins. MLflow itself can use `sqlite:///mlruns.db` for **local** tracking ([Model Registry workflows](https://mlflow.org/docs/latest/ml/model-registry/workflow/) shows example URI).

**DuckDB** excels at **analytical** queries over **Parquet** and federated reads; for a **custom** agent registry you might:

- Append **one row per run** (or per span) into Parquet/SQLite; query with DuckDB; or  
- Use **DuckLake** (DuckDB team): metadata in a **SQL catalog DB** (DuckDB, SQLite, PostgreSQL, MySQL), data files in **Parquet** on disk or **S3**—snapshots, time travel, metadata tables.  
  - [DuckLake site](https://ducklake.select/)  
  - [DuckLake announcement (SQL as lakehouse format)](https://ducklake.select/2025/05/27/ducklake-01/)  
  - [DuckDB extension: ducklake](https://duckdb.org/docs/current/core_extensions/ducklake)  
  - [duckdb/ducklake (GitHub)](https://github.com/duckdb/ducklake)  

DuckLake is **lakehouse-oriented** (tables/partitions), not a drop-in “LLM trace UI,” but it illustrates how teams **query catalog metadata** while blobs live elsewhere.

---

## 4. MinIO / S3 for blobs

**S3-compatible object storage** (AWS S3, **MinIO**, DigitalOcean Spaces, etc.) is the usual **durable blob tier** for large artifacts.

- MLflow: `s3://bucket/path` with optional **`MLFLOW_S3_ENDPOINT_URL`** for MinIO/custom endpoints; multipart upload for large files via tracking server.  
  - [Artifact Stores – S3 and S3-compatible](https://mlflow.org/docs/latest/tracking/artifacts-stores)  
- MinIO’s own write-up on **MLflow + MinIO**: models/datasets in object store, registry workflow.  
  - [MLflow Model Registry and MinIO](https://www.min.io/blog/mlflow-model-registry-and-minio)  

**Pattern:** manifest in DB/Git holds `s3://…` or `s3://bucket/key` + checksum; lifecycle policies manage cost ([MLflow ops-style article](https://www.youngju.dev/blog/ai-platform/2026-03-05-ai-platform-mlflow2-experiment-tracking-registry.en) discusses separation of tracking server vs artifact store and S3 lifecycle—third-party, 2026).

---

## 5. Overlap with Langfuse

**Langfuse** is **LLM observability**: **traces**, **sessions**, **observations** (generations, tool calls, RAG steps), plus **prompt management**, scores, cost/token metrics, datasets/experiments in the product surface. It is **built on OpenTelemetry**, so traces can **also** go to other OTel backends.

- Observability overview (tracing = prompts, responses, tools, latency, cost):  
  [LLM Observability & Application Tracing](https://langfuse.com/docs/observability)  
- Data model (traces, observations, sessions; OTel foundation; mutability notes for cloud vs OSS):  
  [Core Concepts / data model](https://langfuse.com/docs/observability/data-model)  
- Linking **prompt versions** to **traces** for metrics per prompt version:  
  [Link prompts to traces](https://langfuse.com/docs/prompt-management/features/link-to-traces)  
- **Export / pull** observations for analytics (API field groups, pagination):  
  [Observations API](https://langfuse.com/docs/api-and-data-platform/features/observations-api)  

| Concern                         | Langfuse                         | Generic artifact registry (Git + S3 + index) |
|---------------------------------|----------------------------------|-----------------------------------------------|
| LLM spans, token/cost           | Native                           | You model or adopt OTel + store               |
| Prompt versioning + UI          | Native                           | Files in Git or your DB                       |
| **Verdicts / code-review gates**| Custom metadata or outside       | First-class in repo (markdown/JSON)           |
| **Plans** (design docs)         | Not the core product             | Git-native strength                           |
| **Repo diffs / PR artifacts**   | Indirect                         | Git/Git hosting                               |
| Long-term **vendor-neutral** raw store | Export APIs; self-host OSS | You own layout                                |

**Practical split:** use **Langfuse** (or any OTel-backed APM) for **runtime LLM telemetry**; use **Git + conventions** (and optional **object store**) for **durable, reviewable** plans, policies, and **verdicts** that must align with code changes.

---

## 6. OpenTelemetry and agent-shaped traces

Standardizing **attributes** and **spans** helps if you export traces to **multiple** backends (Langfuse + your own store).

- **GenAI** attribute registry (`gen_ai.*`, tokens, models, tools, etc.):  
  [OpenTelemetry Gen AI registry](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/)  
- **Agent** span conventions (e.g. `create_agent`, `invoke_agent`; `gen_ai.conversation.id`, `gen_ai.data_source.id`)—note **development** status in spec:  
  [GenAI agent and framework spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/)  

Community discussion on **richer agent observability** (e.g. memory spans) illustrates demand beyond a single vendor:  
[OpenTelemetry Semantic Conventions for AI Agents (RFC discussion)](https://github.com/traceloop/openllmetry/issues/3460)

---

## 7. Summary table (pattern → query model)

| Pattern              | Query surface              | Blobs              | Best for                          |
|----------------------|----------------------------|--------------------|-----------------------------------|
| Git + markdown/JSON  | `git`, `rg`, hosting UI    | LFS / DVC / none   | Plans, verdicts, small outputs    |
| SQLite catalog       | SQL                        | paths/URLs in rows | Single-node index, tests          |
| DuckDB (+ Parquet)   | SQL, analytics             | Parquet/S3         | Reports, dashboards, bulk scan    |
| DuckLake             | SQL on catalog + Parquet   | S3/disk            | Lakehouse-style tables/snapshots  |
| MLflow-style         | UI + API + DB              | S3/MinIO           | ML runs/models (closest analog)   |
| Langfuse             | UI + API                   | Hosted/self-host DB| LLM traces, prompts, eval metrics |

---

## 8. Pilot-minimal vs v1

### Pilot-minimal: Git + conventions

- **Commit per run** (or per meaningful attempt): `runs/YYYY-MM-DD/<run_id>/` with fixed filenames: `manifest.json` (id, timestamps, git SHA, parent, tags), `plan.md`, `prompts/` (or redacted hashes only), `verdict.md`, `summary.json` (metrics, pass/fail).  
- **Large outputs / raw traces**: store under `artifacts/` with **DVC** or document **MinIO keys** only in `manifest.json` (no binary in Git).  
- **Queryable enough for humans**: `git log -- runs/`, `rg`, code review on verdicts; CI can grep `summary.json`.  
- **No new services**; reproducibility ties to **commit SHA** in manifest.

### v1: Light DB index

- Add **SQLite** (single writer) or small **PostgreSQL** table: `runs`, `spans` (optional), `artifacts` (type, uri, sha256, run_id).  
- **Ingest** from agent: append row on run start/end; write blobs to **S3/MinIO**; store only URIs + metadata in DB.  
- **Query**: SQL for “all failed verdicts last week,” “runs using model X,” join to Git SHA for code.  
- **Optional**: export OTel to Langfuse for **LLM-specific** drill-down; keep **verdicts/plans** in Git or mirror summary columns in DB for one dashboard.

This matches the proven **metadata DB + object store** split used in MLflow and MinIO reference architectures, adapted for **agent run artifacts** and **human-in-the-loop** records.

---

*Searches used (5): Langfuse observability/data model; MLflow artifact stores + MinIO; DuckLake/DuckDB catalog; DVC/Git experiment layout; OpenTelemetry GenAI/agent semantic conventions.*
