# Gap wave 2: oh-my-opencode vs openagent, ruflo #1335, gastown cost tracking

Web research (≤5 searches) plus direct GitHub/API checks. Saved: 2026-04-03.

---

## 1. `code-yeongyu/oh-my-opencode` vs `code-yeongyu/oh-my-openagent`

**Conclusion:** One canonical repository, **renamed** on GitHub. The old slug is **not** a separate project; it **HTTP 301 redirects** to the new name.

| Check | Result |
|--------|--------|
| Redirect | `https://github.com/code-yeongyu/oh-my-opencode` → `301 Location: https://github.com/code-yeongyu/oh-my-openagent` (verified via `curl -sI`) |
| Canonical repo | `code-yeongyu/oh-my-openagent` ([repository](https://github.com/code-yeongyu/oh-my-openagent)) |
| Default branch | **`dev`** (GitHub API: not `main`) |

**Rename / migration context (docs & issues):**

- [PR #2417 — docs: update all GitHub URLs from oh-my-opencode to oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent/pull/2417)
- [Issue #2823 — Package rename from oh-my-opencode to oh-my-openagent breaks existing configurations](https://github.com/code-yeongyu/oh-my-openagent/issues/2823)

So: **same project**, **renamed** (product/package naming moved to “openagent”); old GitHub URL **redirects**. Users may still see old npm/config strings in the wild (see #2823).

---

## 2. `ruvnet/ruflo` issue **#1335** (daemon scheduler / workers / metrics)

**Conclusion:** **Closed** as completed (**2026-03-17**).

| Field | Value |
|--------|--------|
| Title | [Daemon workers don't update metric files and scheduler loop doesn't fire](https://github.com/ruvnet/ruflo/issues/1335) |
| State | **closed** (completed) |
| Fix version (maintainer) | **`v3.5.22`** — stated in issue timeline by [@ruvnet](https://github.com/ruvnet) on [issue #1335](https://github.com/ruvnet/ruflo/issues/1335) |
| Implementing PR | Maintainer cites **[PR #1365](https://github.com/ruvnet/claude-flow/pull/1365)** on **`ruvnet/claude-flow`** (daemon fixes: ESM `fs` import for logging, interval calculation, orphan process cleanup on timeout); references **ADR-064** in thread |

**Note:** Reported environment in the issue included `ruflo` / `@claude-flow/cli@3.5.15`; closure comment ties fixes to **3.5.22** and cross-repo PR above.

---

## 3. `steveyegge/gastown` issue **#24** (cost tracking / PR #292 / env vars)

**URLs:** Opening [https://github.com/steveyegge/gastown/issues/24](https://github.com/steveyegge/gastown/issues/24) presents the same issue under the canonical org **`gastownhall/gastown`** ([issue #24](https://github.com/gastownhall/gastown/issues/24)).

| Item | Status |
|------|--------|
| Issue **#24** | **Open** (labels include `kind/enhancement`, `status/accepted`, `priority/p3` as of fetched page) |
| [PR #292](https://github.com/gastownhall/gastown/pull/292) | **Merged** **2026-01-09** — *feat(costs): redesign session cost tracking with wisps and daily digests* (brief close/reopen in timeline; end state **merged**) |

**Resolution narrative (from issue comments):**

1. **PR #292** landed the wisp/digest cost architecture, but the **tmux `capture-pane`** approach **did not work**: Claude Code shows cost in the **TUI status bar**, not scrollback → regex saw nothing → **$0.00** everywhere.
2. **Cost tracking was disabled** (maintainer: commit **bd655f5**, deprecation on `gt costs`, Deacon `costs-digest` **DISABLED**) until a **real data source** exists.

**Environment variables for cost:** There is **no** documented **Claude Code–provided** env var confirmed in the issue. Maintainers **request** (feature ask to Claude Code), for example:

- **`$CLAUDE_SESSION_COST`** in the **Stop** hook environment (preferred in comments), and/or  
- a queryable file or CLI (e.g. `claude session cost`).

These are **proposed** names/behaviors for upstream, **not** stated as shipped Claude Code API in the thread.

**Follow-up (alternative data path):** [Comment on #24](https://github.com/gastownhall/gastown/issues/24) (2026-01-25): token **`usage`** in Claude Code **transcript JSONL** under `~/.claude/projects/.../*.jsonl`. **[PR #941](https://github.com/gastownhall/gastown/pull/941)** — *fix(costs): read token usage from Claude Code transcripts instead of tmux* — **`merged` 2026-01-26** (GitHub API: `merged_at` 2026-01-26T02:06:22Z). Issue **#24** remains **open** as the umbrella enhancement despite this merge (verify current CLI/docs in-repo for whether user-visible cost commands are fully enabled).

---

## Source URLs (quick index)

- https://github.com/code-yeongyu/oh-my-opencode (redirects)
- https://github.com/code-yeongyu/oh-my-openagent
- https://github.com/code-yeongyu/oh-my-openagent/pull/2417
- https://github.com/code-yeongyu/oh-my-openagent/issues/2823
- https://github.com/ruvnet/ruflo/issues/1335
- https://github.com/ruvnet/claude-flow/pull/1365
- https://github.com/steveyegge/gastown/issues/24
- https://github.com/gastownhall/gastown/issues/24
- https://github.com/gastownhall/gastown/pull/292
- https://github.com/gastownhall/gastown/pull/941
