# NTM (Named Tmux Manager) — guardrails, sessions, pipelines

Research focus: **Dicklesworthstone/ntm** — agent sessions, audit logging, policy / dangerous-command handling, YAML pipelines, and multi-agent (“swarm”) orchestration. Sources are the **official README** on `main`, the **GitHub releases** listing, and secondary context from web search (no separate published docs site was found; the README is the primary document).

---

## Canonical URLs

| Resource | URL |
| --- | --- |
| Repository | https://github.com/Dicklesworthstone/ntm |
| README (rendered on GitHub) | https://github.com/Dicklesworthstone/ntm/blob/main/README.md |
| README (raw) | https://raw.githubusercontent.com/Dicklesworthstone/ntm/main/README.md |
| Releases | https://github.com/Dicklesworthstone/ntm/releases |
| Tags (all versions) | https://github.com/Dicklesworthstone/ntm/tags |
| Issues | https://github.com/Dicklesworthstone/ntm/issues |
| Install script (raw) | https://raw.githubusercontent.com/Dicklesworthstone/ntm/main/install.sh |
| OpenAPI artifact (referenced in README) | https://github.com/Dicklesworthstone/ntm/blob/main/docs/openapi.json |
| License | https://github.com/Dicklesworthstone/ntm/blob/main/LICENSE |
| Planning / design notes (repo file) | https://github.com/Dicklesworthstone/ntm/blob/main/PLAN_TO_MAKE_NTM.md |
| Contributing policy | https://github.com/Dicklesworthstone/ntm/blob/main/CONTRIBUTING.md |

---

## What NTM is (one paragraph)

NTM is a **Go binary** that layers a **local control plane** on top of **tmux**: named sessions, tiled panes for multiple agent CLIs (Claude Code, Codex, Gemini CLI, plus Cursor, Windsurf, Aider, Ollama per README/support matrix), operator UX (dashboard, palette), **work triage** when `br` / `bv` data exists, **Agent Mail** and **locks** when configured, **safety policy + approvals**, **checkpoints / timelines / audit**, **YAML pipelines** under `.ntm/pipelines/`, and **machine surfaces** (`--robot-*`, `ntm serve` with REST/SSE/WebSocket and OpenAPI). Official positioning: *“Safe by default”* and *“Auditable actions”* are stated design principles in the README.

Source: https://raw.githubusercontent.com/Dicklesworthstone/ntm/main/README.md

---

## Agent sessions and swarm orchestration

- **Named tmux sessions** with explicit agent panes and a user pane; commands include `ntm quick`, `ntm spawn`, `ntm add`, `ntm list`, `ntm status`, `ntm view`, `ntm zoom`, `ntm attach`, `ntm dashboard`, `ntm palette`, `ntm kill`.
- **Labels** allow multiple coordinated swarms on the same project directory (e.g. `--label backend` / `--label frontend`).
- **Mixed swarms** are illustrated as e.g. `ntm spawn api --cc=2 --cod=1 --gmi=1` (Claude Code / Codex / Gemini counts).
- **Dispatch and monitoring**: `ntm send`, `ntm interrupt`, `ntm activity`, `ntm health`, `ntm watch`, `ntm diff`, `ntm grep`, `ntm analytics`, etc.
- **Work graph integration** (optional): `ntm work triage`, `ntm work next`, `ntm assign`, coordinator/conflict commands — depends on repo tooling such as Beads / BV where noted in README troubleshooting.

Source: https://raw.githubusercontent.com/Dicklesworthstone/ntm/main/README.md (sections “Multi-Agent Session Orchestration”, “Dispatch, Monitoring, and Recovery”, “Work Graph Triage and Assignment”)

---

## Audit logging and durable forensics

- README lists **`ntm audit`** under durable operations, with example: `ntm audit show <session>`.
- Durable operations grouping also includes **checkpoints**, **timeline**, **history**, **changes**, **resume** — framed as recoverability and forensic surfaces.
- **Analytics** over a window: e.g. `ntm analytics --days 7`.
- Design principle **“Auditable actions”**: explicit logs and durable state vs. hidden orchestration.

Source: https://raw.githubusercontent.com/Dicklesworthstone/ntm/main/README.md

---

## Policy engine, guards, and blocking dangerous commands

README describes a **first-class safety system**:

- **Policy rules** define what is **allowed**, **blocked**, or **approval-gated**.
- **Approvals** are described as durable, auditable, with **SLB-style two-person workflows** for high-risk operations.
- Example **precheck** against a command: `ntm safety check -- git reset --hard`
- Command groups: `ntm safety` (`status`, `check`, `blocked`, `install`, …), `ntm policy` (`show`, `validate`, `edit`, `automation`, …), `ntm approve` (list/show/approve/deny), `ntm guards`.

**Configuration location (user-level policy file):** `~/.ntm/policy.yaml` (per README “User-Level” config section).

Source: https://raw.githubusercontent.com/Dicklesworthstone/ntm/main/README.md (section “Safety Policy and Approvals”, “Configuration and Project Assets”)

---

## YAML pipelines

- **Pipelines** are described as **executable multi-step agent workflows** with **variables**, **dependencies**, **resume**, and **cleanup**.
- **Project-local** pipeline definitions live under **`.ntm/pipelines/`**.
- Examples from README:

  ```bash
  ntm pipeline run .ntm/pipelines/review.yaml --session payments
  ntm pipeline status run-20241230-123456-abcd
  ntm pipeline list
  ntm pipeline resume run-20241230-123456-abcd
  ntm pipeline cleanup --older=7d
  ```

- Related orchestration assets (also in README): **recipes**, **workflows** (e.g. pipeline, ping-pong, review-gate patterns), **templates**, **session-templates**.

Source: https://raw.githubusercontent.com/Dicklesworthstone/ntm/main/README.md (section “Pipelines, Templates, Recipes, and Workflow Assets”)

---

## API / “robot” automation (context for guardrails and auditing)

- **`ntm serve`**: local server; README lists REST under `/api/v1`, SSE at `/events`, WebSocket at `/ws`, health at `/health`, OpenAPI at `docs/openapi.json`.
- **`ntm openapi generate`** refreshes the spec.
- **`ntm --robot-*`**: snapshot, capabilities, send, tail, mail-check, etc. — documented as the preferred local scripting surface vs. long-lived HTTP integrations.

Source: https://raw.githubusercontent.com/Dicklesworthstone/ntm/main/README.md (“Robot Mode and Local API”)

---

## Releases and maintenance (snapshot)

- **Releases page:** https://github.com/Dicklesworthstone/ntm/releases  
- The releases listing (as fetched 2026-04-03) includes **detailed release notes** for tagged versions (e.g. **v1.9.0** with a long feature changelog including agent types, robot/attention feed, dashboard, checkpoint restore, pipelines/session resolution, etc.). Example tag link: https://github.com/Dicklesworthstone/ntm/releases/tag/v1.9.0  
- The same page’s quick-install snippets referenced **`go install ...@v1.11.0`** and **`@v1.10.0`** in the HTML snapshot — treat **GitHub Releases + Tags** as the source of truth for the latest tag; the README’s version badge tracks GitHub releases: `https://img.shields.io/github/v/release/Dicklesworthstone/ntm?include_prereleases` (embedded in README at repo root).

---

## Issues and contributions

- **Issues:** https://github.com/Dicklesworthstone/ntm/issues  
- README **“About Contributions”** states the maintainer generally **does not merge outside contributions** but **welcomes bug reports** and may use `gh` + agents to review; PRs may be used to illustrate fixes without guarantee of merge.  
- **CONTRIBUTING.md:** https://github.com/Dicklesworthstone/ntm/blob/main/CONTRIBUTING.md  

---

## Third-party commentary (non-official)

- Example blog review (feature overview, not authoritative for behavior): https://vibecoding.app/blog/ntm-review  

For implementation-accurate behavior, prefer the **README**, **`ntm --help`**, and **repository source** over third-party summaries.

---

## Search log (subagent budget: 4 / 5)

1. `Dicklesworthstone ntm Named Tmux Manager GitHub`  
2. `ntm tmux manager policy engine audit logging YAML pipelines`  
3. `github Dicklesworthstone ntm swarm orchestration agent sessions`  
4. `site:github.com/Dicklesworthstone/ntm issues`  

Additional evidence: direct fetch of **raw README** and **GitHub releases** HTML (not counted as web “searches”).
