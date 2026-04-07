# Gap wave 2 — synthesis (April 2026)

Follow-up research closing items from [../research_report.md](../research_report.md) § *Gaps and limitations* and the DTU / production hardening follow-ups.

**Plan:** [research_plan_gaps_wave2.md](./research_plan_gaps_wave2.md)

---

## Answers (actionable)

### 1. OpenJudge — canonical install

| Use | Value |
| --- | ----- |
| **PyPI** | `pip install py-openjudge` (not `pip install openjudge`) |
| **Import** | `openjudge` |
| **Canonical repo** | [github.com/agentscope-ai/OpenJudge](https://github.com/agentscope-ai/OpenJudge) |
| **Docs** | [agentscope-ai.github.io/OpenJudge](https://agentscope-ai.github.io/OpenJudge/) |
| **Latest checked** | `0.2.3` (2026-03-04 per PyPI JSON) |

[modelscope/OpenJudge](https://github.com/modelscope/OpenJudge) exists with similar branding but is **not** linked from PyPI `project_urls` for `py-openjudge` — treat AgentScope org as distribution source of truth.

**Collision:** PyPI package **`openjudge`** is an unrelated LAN contest judge ([pypi.org/project/openjudge](https://pypi.org/project/openjudge/)).

**Detail:** [findings_gap_openjudge_canonical.md](./findings_gap_openjudge_canonical.md)

---

### 2. oh-my-opencode vs oh-my-openagent

- **Single project, renamed.** `github.com/code-yeongyu/oh-my-opencode` **301 redirects** to **`code-yeongyu/oh-my-openagent`**.
- **Default branch:** `dev` (not `main`).
- Migration: [PR #2417](https://github.com/code-yeongyu/oh-my-openagent/pull/2417); breaking configs: [issue #2823](https://github.com/code-yeongyu/oh-my-openagent/issues/2823).

**Detail:** [findings_gap_opencode_ruflo_gastown.md](./findings_gap_opencode_ruflo_gastown.md)

---

### 3. Ruflo daemon / scheduler (#1335)

- **Closed** 2026-03-17; maintainer: fixes in **`@claude-flow/cli` v3.5.22+**, implementation tied to [claude-flow#1365](https://github.com/ruvnet/claude-flow/pull/1365).
- If you pinned `3.5.15`, **upgrade** before trusting overnight daemon metrics/scheduling.

**Detail:** [findings_gap_opencode_ruflo_gastown.md](./findings_gap_opencode_ruflo_gastown.md)

---

### 4. Gas Town cost tracking (#24) and org

- Issue links may resolve under **`gastownhall/gastown`** ([#24](https://github.com/gastownhall/gastown/issues/24)) — still **open** as umbrella enhancement.
- **PR #292** merged (wisp/digest design); tmux capture failed for TUI cost → **$0.00**; later **[PR #941](https://github.com/gastownhall/gastown/pull/941)** (2026-01-26) reads **token usage from Claude Code transcript JSONL** under `~/.claude/projects/...`.
- **`CLAUDE_SESSION_COST`** etc. remain **requested upstream** behaviors, not confirmed Claude Code API in that thread.

**Detail:** [findings_gap_opencode_ruflo_gastown.md](./findings_gap_opencode_ruflo_gastown.md)

---

### 5. OpenHands — production / VPS

- **Headless** = fixed **`always-approve`**; cannot use `--llm-approve` in that mode — treat as full-trust execution ([headless docs](https://docs.openhands.dev/openhands/usage/run-openhands/headless-mode)).
- **SDK** offers `AlwaysConfirm` / `NeverConfirm` / `ConfirmRisky` when not using CLI headless ([security guide](https://docs.openhands.dev/sdk/guides/security)).
- **Config files:** `~/.openhands/agent_settings.json`, `cli_config.json`, `mcp.json`; use **`--override-with-envs`** for non-persisted env overrides ([command reference](https://docs.openhands.dev/openhands/usage/cli/command-reference)).
- **`openhands web`:** default bind **0.0.0.0** — docs show **`--host 127.0.0.1`** for local-only; pair with reverse proxy + TLS for remote access.
- **Security signals:** GitHub [security tab](https://github.com/OpenHands/OpenHands/security); advisory **GHSA-7h8w-hj9j-8rjw** / CVE-2026-33718 (PyPI openhands); issues on pickle/CWE-502, QEMU microVM, OWASP-style assessment — read before exposing agent server to the internet.

**Detail:** [findings_gap_openhands_production.md](./findings_gap_openhands_production.md)

---

### 6. DTU — LocalStack + Browserless (+ Playwright)

- **LocalStack:** Official install/auth-token workflow, gateway **4566**, integrations hub, parity limits and K8s enterprise limitations — good **AWS-shaped DTU**; not a substitute for full multi-AZ AWS. Pricing/auth tied to [localstack.cloud](https://www.localstack.cloud/pricing).
- **Browserless:** Enterprise Docker/registry image, **`KEY` (license) vs `TOKEN` (API)`**, CDP/WebSocket APIs; compare to **Playwright** official Docker (`mcr.microsoft.com/playwright`) and **`run-server`** / `connect` for CI.
- **OpenHands:** Browser runs **inside sandbox** per runtime docs; external Browserless/Playwright is a harness-level integration choice if you want shared browser pools.

**Detail:** [findings_gap_dtu_localstack_browserless.md](./findings_gap_dtu_localstack_browserless.md)

---

## Remaining gaps (not closed by web pass)

- **Legal/compliance** for self-hosted stacks (Langfuse, Keploy, LocalStack license tier) — still your review.
- **LocalStack vs AWS** parity for *your* exact services — verify against [parity](https://blog.localstack.cloud/2022-08-04-parity-explained/) + service list before betting overnight runs on it.
- **OpenHands** security evolves — re-check advisories before each production bump.

---

## Findings files (wave 2)

| File |
| ---- |
| [findings_gap_openjudge_canonical.md](./findings_gap_openjudge_canonical.md) |
| [findings_gap_opencode_ruflo_gastown.md](./findings_gap_opencode_ruflo_gastown.md) |
| [findings_gap_openhands_production.md](./findings_gap_openhands_production.md) |
| [findings_gap_dtu_localstack_browserless.md](./findings_gap_dtu_localstack_browserless.md) |
