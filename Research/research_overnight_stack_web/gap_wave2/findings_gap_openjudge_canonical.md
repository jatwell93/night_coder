# Gap: OpenJudge — canonical package, repo, releases, docs

**Sources:** PyPI JSON API (`/pypi/{name}/json`), GitHub project pages, README content mirrored on PyPI, and targeted web search (≤5 queries).

---

## Canonical `pip install` (AI evaluation framework)

| Field | Value |
|--------|--------|
| **PyPI package name** | `py-openjudge` |
| **Install** | `pip install py-openjudge` |
| **Import namespace** | `openjudge` (per upstream README; package name ≠ import name) |
| **Current version (PyPI)** | `0.2.3` |
| **Python** | `>=3.10` (`requires_python` on PyPI) |
| **License** | Apache-2.0 |

- **PyPI project:** https://pypi.org/project/py-openjudge/
- **PyPI JSON (machine-readable):** https://pypi.org/pypi/py-openjudge/json

`project_urls` on PyPI list **only** the AgentScope AI org repo and docs:

- Homepage: https://github.com/agentscope-ai/OpenJudge  
- Repository: https://github.com/agentscope-ai/OpenJudge  
- Documentation: https://agentscope-ai.github.io/OpenJudge/

The long description on PyPI matches the GitHub README (installation block shows `pip install py-openjudge`).

---

## Primary GitHub repo vs `modelscope/OpenJudge`

**Primary (canonical for distribution and docs):** https://github.com/agentscope-ai/OpenJudge  

Evidence:

- PyPI `py-openjudge` **Homepage** and **Repository** URLs both point here (see JSON `project_urls` above).
- Published docs site is **GitHub Pages under the same org:** https://agentscope-ai.github.io/OpenJudge/

**Also exists:** https://github.com/modelscope/OpenJudge  

GitHub shows the same one-line description (“OpenJudge: A Unified Framework for Holistic Evaluation and Quality Rewards”). This repo is **not** linked from the `py-openjudge` PyPI metadata. Treat **`agentscope-ai/OpenJudge` as the canonical source for the PyPI package**; `modelscope/OpenJudge` is a same-name sibling org repo (typical for ModelScope/AgentScope ecosystem mirroring or hosting—confirm fork/sync policy in that repo’s README if you need exact mirroring semantics).

**Related docs (integration, not package ownership):** AgentScope documents OpenJudge usage at https://doc.agentscope.io/tutorial/task_eval_openjudge.html (framework tutorial, not PyPI canonical).

---

## Release activity (`py-openjudge`)

From https://pypi.org/pypi/py-openjudge/json, published versions include (wheel/sdist upload times, UTC):

| Version | Notable upload times (approx.) |
|---------|---------------------------------|
| 0.1.7 | 2025-12-25 |
| 0.1.8 | 2025-12-26 |
| 0.2.0 | 2025-12-26 |
| 0.2.1 | 2026-01-21 |
| 0.2.2 | 2026-02-12 |
| **0.2.3** | **2026-03-04** (latest) |

**Summary:** Active cadence in late 2025–early 2026; latest release **0.2.3** as of metadata retrieval.

**Legacy (pre–0.2.x):** Upstream README on PyPI states OpenJudge was previously published as **`rm-gallery`** (v0.1.x), with breaking changes at v0.2.0; legacy branch referenced as `v0.1.7-legacy` on the agentscope-ai repo. Citation URL in README: https://github.com/agentscope-ai/OpenJudge

---

## Docs site ownership

| Resource | URL | Notes |
|----------|-----|--------|
| **Official docs (GitHub Pages)** | https://agentscope-ai.github.io/OpenJudge/ | Linked from PyPI `project_urls` as “Documentation”; path space `/OpenJudge/` matches the repo name. |
| **Product / marketing site** | https://openjudge.me/ | Linked from README (badges, playground). |
| **Online app** | https://openjudge.me/app/ | Playground; README explicitly references it. |

**Ownership alignment:** Docs are served from **`agentscope-ai.github.io`**, consistent with **`agentscope-ai/OpenJudge`** as the canonical GitHub project.

---

## Two packages on PyPI (name collision)

Yes — **two different projects** share the “openjudge” naming space on PyPI:

| PyPI name | Purpose | Latest (JSON) | Homepage in metadata |
|-----------|---------|---------------|----------------------|
| **`py-openjudge`** | LLM/agent **evaluation framework** (this OpenJudge) | **0.2.3** | https://github.com/agentscope-ai/OpenJudge |
| **`openjudge`** | **LAN programming contest** judging (MongoDB, unrelated) | **3.0.8** (upload 2018-04-13) | http://github.com/theSage21/openJudge |

- **Contest package:** https://pypi.org/project/openjudge/  
- **PyPI JSON:** https://pypi.org/pypi/openjudge/json  

**Recommendation:** For the AI evaluation stack, use **`pip install py-openjudge`**, not `pip install openjudge`.

---

## Method / search budget

- **Web searches used:** 4 (PyPI install discovery, GitHub org comparison, `site:pypi.org` for duplicate packages, modelscope vs agentscope relationship).
- **Verification:** PyPI JSON endpoints and GitHub fetches for project pages.
