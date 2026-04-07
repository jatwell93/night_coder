# Complementary research: Aider stack + scenario eval (web search notes)

**Scope:** Aider (architect mode, file watching, unattended/scripted runs, LiteLLM / OpenAI-compatible backends) and brief open-source complements for LLM-as-judge / agent evaluation harnesses.  
**Method:** Up to five targeted web searches; URLs cited inline.

---

## 1. Aider architect mode (pair programming)

**Idea:** Split “reasoning” from “editing” by using two models: an **Architect** proposes the approach; an **Editor** turns that into concrete edit instructions Aider applies.

**Why:** Documented motivation is better benchmark results when a strong reasoning model plans and a model better at formatted edits implements (e.g. pairing described in Aider’s architect announcement).

**How to use (documented patterns):**

- Chat mode docs: [Chat modes | aider](https://aider.chat/docs/usage/modes.html)
- Enter with `/architect`, `/chat-mode architect`, or launch with `--architect` (per modes documentation on the same site).
- Optional `--editor-model` to pin the editor model separately from the main/architect model.

**Primary references:**

- [Separating code reasoning and editing | aider](https://aider.chat/2024/09/26/architect.html) — rationale and benchmark-oriented discussion.
- [modes.md (source)](https://github.com/Aider-AI/aider/blob/main/aider/website/docs/usage/modes.md) — mode definitions in repo.
- [architect_coder.py (source)](https://github.com/Aider-AI/aider/blob/main/aider/coders/architect_coder.py) — implementation entry point.

---

## 2. Watch files (`--watch` / `--watch-files`)

**Idea:** Aider watches files for **inline AI directives** in comments and can apply changes or answer questions without typing at the REPL.

**Mechanics (as documented):**

- Markers such as `AI!` (do the work) and `AI?` (Q&A) in supported comment styles (`#`, `//`, `--`, etc.).
- [Aider in your IDE | File watching](https://aider.chat/docs/usage/watch.html) — official watch-mode documentation.
- Implementation reference: [aider/watch.py](https://github.com/Aider-AI/aider/blob/main/aider/watch.py).

**Automation caveats (from community issues, useful for overnight/stack design):**

- Watching may be **suspended during some operations** (e.g. discussion around `/run`): [Issue #2717 — watch-files suspended during `/run`](https://github.com/Aider-AI/aider/issues/2717).
- **Reliability / trigger** edge cases: [Issue #2586 — watch-files doesn’t consistently trigger](https://github.com/Aider-AI/aider/issues/2586).

Third-party summary (not official): [File Watching (--watch mode) — OpenDeep Wiki](https://opendeep.wiki/Aider-AI/aider/using-aider-file-watching).

---

## 3. Unattended / scripted runs (beyond watch)

**CLI scripting surface:**

- Official: [Scripting aider](https://aider.chat/docs/scripting.html) — documents patterns such as:
  - `--message` / `-m` — single instruction, process, exit.
  - `--message-file` / `-f` — message body from a file.
  - `--yes` — auto-accept confirmations for non-interactive use.
  - Other flags (`--no-auto-commits`, `--dry-run`, etc.) for pipeline control.

**CI / headless interest:**

- [Issue #4923 — Document `--message` + `--auto-test` for headless CI/benchmark usage](https://github.com/Aider-AI/aider/issues/4923) — signals demand for documented headless + test-loop patterns.
- [Issue #426 — non-interactive / scripting from CLI](https://github.com/paul-gauthier/aider/issues/426) — historical discussion (note older repo path; current org is `Aider-AI`).

**Reality check:** Users still report multi-step or confirmation edge cases in strict one-shot CLI use; see e.g. [Issue #4933 — single pass / architect mode from CLI](https://github.com/Aider-AI/aider/issues/4933). For brittle automation, prefer explicit scripting docs + pinning flags/models, or the Python scripting APIs referenced on the scripting page.

---

## 4. LiteLLM and OpenAI-compatible backends

**OpenAI-compatible endpoints:** Aider documents pointing any OpenAI-compatible API via `OPENAI_API_BASE` / `OPENAI_API_KEY` and model names with the `openai/` prefix.

- [OpenAI compatible APIs | aider](https://aider.chat/docs/llms/openai-compat.html)

**LiteLLM proxy:** Community issues discuss configuring Aider against a LiteLLM proxy (e.g. `litellm_proxy/<model>` style entries and env vars for base URL/API key).

- Example thread: [Configuring LLMLite proxy · Issue #3218 · Aider-AI/aider](https://github.com/Aider-AI/aider/issues/3218)
- Historical implementation note: [feat: add LiteLLM support · PR #549](https://github.com/paul-gauthier/aider/pull/549) (older fork path; verify behavior on your installed Aider version).

**LiteLLM project (gateway/SDK):**

- [LiteLLM — Berri AI docs](https://docs.litellm.ai/) (canonical project documentation; use for proxy setup, model names, and provider routing).

---

## 5. Optional complement: LLM-as-judge & agent evaluation harnesses (open source, brief)

These can sit **alongside scenario-based eval** (task scripts, traces, pass/fail) by adding **rubric or judge scoring** over outputs or trajectories.

| Project | License / note | URL |
|--------|----------------|-----|
| **microsoft/llm-as-judge** | Microsoft OSS; judges + orchestration patterns | https://github.com/microsoft/llm-as-judge |
| **NVIDIA/Judges-Verdict** | Apache-2.0; YAML judges, parallel runs; **LiteLLM** mentioned for unified provider access | https://github.com/NVIDIA/Judges-Verdict |
| **haizelabs/verdict** | Compound / hierarchical LLM-as-judge framework | https://github.com/haizelabs/verdict |
| **fsndzomga/agent-harness** | Lightweight harness; layered grading including LLM-as-judge | https://github.com/fsndzomga/agent-harness |
| **EvalForge** (community write-up) | Described as Rust + Python SDK, trace JSON from multiple agent frameworks; judge-based scoring for CI | https://dev.to/hemankumar6/i-built-an-open-source-llm-agent-evaluation-tool-that-works-with-any-framework-55h |

**Usage hint:** Pair **scenario harnesses** (fixed tasks, reproducible environments) with **one judge stack** (single rubric YAML or small judge graph) so nightly runs produce both binary outcomes and qualitative scores—avoid duplicating task definition in the judge layer.

---

## Gaps / next steps (if you deepen this locally)

- Confirm exact `litellm_proxy/...` model strings and env vars against your **installed** Aider version (`aider --version`) and current [openai-compat](https://aider.chat/docs/llms/openai-compat.html) docs.
- Prototype watch-mode reliability on your repo layout before depending on it for unattended loops.
- Pick one judge framework and one trace format (e.g. JSONL per step) so scenario eval and judging stay decoupled but composable.
