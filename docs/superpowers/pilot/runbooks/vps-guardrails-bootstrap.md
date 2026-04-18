# Guardrail runtime and baseline policies (pilot) — T061

Install **NTM** (Named Tmux Manager) as the **PATH-level command interception** layer (Leash pillar) and **DCG** (Destructive Command Guard) as a **defense-in-depth hook** that suggests **safer alternatives** when blocking. Configure a baseline overnight policy that uses **block + allow only** (no `approval_required`) so the agent can run unattended. Document **SLB** (Simultaneous Launch Button) as a V1 stepping stone for two-agent approval workflows.

**OS:** Ubuntu 24.04 LTS (noble), x86_64. **Operator user:** `deploy` (sudo-capable), per [`vps-bootstrap.md`](./vps-bootstrap.md).

**Prerequisites**

- [`vps-bootstrap.md`](./vps-bootstrap.md) — tmux, git, curl; repo checkout (§12) for `.ntm/` project assets.
- [`vps-container-runtime.md`](./vps-container-runtime.md) — Podman/Docker (DCG can guard container commands).
- [`vps-secrets-bootstrap.md`](./vps-secrets-bootstrap.md) — Doppler configured (NTM/DCG do not use secrets themselves, but the agent they protect does).

**Decisions and briefs**

- Guardrails (Leash): NTM — [`../DECISIONS.md`](../DECISIONS.md) §"Guardrails (Leash) → NTM"; no separate Quint decision file (inline in DECISIONS.md).
- Execution sandbox: [`../sandbox/IMPLEMENTATION-BRIEF.md`](../sandbox/IMPLEMENTATION-BRIEF.md) — NTM + container profiles compose together.
- DCG integration: NTM README lists DCG as an optional integration (`ntm deps -v` checks for it).

Do **not** commit secrets, API keys, or Doppler tokens. NTM policy files and DCG config are safe to commit (they contain patterns, not credentials).

---

## 1. Goals

| Layer | Goal of this runbook |
|-------|----------------------|
| **NTM** | Install the Go binary; configure `~/.ntm/policy.yaml` with a **block + allow** baseline for overnight mode; verify `ntm safety status`, `ntm safety check`, and audit trail. |
| **DCG** | Install the Rust binary; verify it blocks a test command **with a safer-alternative tip**; confirm it coexists with NTM as defense-in-depth. |
| **SLB** | Document as a **V1 stepping stone** for two-agent approval; do **not** install or configure for the pilot. |

---

## 2. NTM installation

NTM is a **Go binary**. Multiple install paths are available; pick one.

### 2.1 Method A — install script (recommended for pilot)

```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/ntm/main/install.sh?$(date +%s)" | bash -s -- --easy-mode
```

Follow any on-screen PATH instructions. Then open a **new shell** or:

```bash
source ~/.bashrc   # or ~/.profile, depending on what the installer updated
```

### 2.2 Method B — `go install` (if Go ≥ 1.25 is on the VPS)

```bash
go install github.com/Dicklesworthstone/ntm/cmd/ntm@latest
```

Ensure `$(go env GOPATH)/bin` is on PATH.

### 2.3 Verify

```bash
ntm --version
ntm deps -v
```

**Expected:** version string; `deps -v` shows `tmux` found (required) and lists optional integrations (DCG will show missing until §4).

### 2.4 Shell integration (optional but useful)

```bash
eval "$(ntm shell bash)"
```

To persist, add to `~/.bashrc`:

```bash
grep -q 'ntm shell bash' ~/.bashrc 2>/dev/null || echo 'eval "$(ntm shell bash)"' >> ~/.bashrc
```

---

## 3. Baseline overnight policy

### 3.1 Design principle

For **unattended overnight** runs, NTM's policy must use only **`block`** and **`allow`** tiers — **no `approval_required`** tier, because there is no human to approve at 3 AM. The DECISIONS.md invariant states:

> Policy engine must be configured with `block` and `allow` tiers only (no `approval_required`) for overnight mode.

### 3.2 Create / edit the policy file

NTM's user-level policy lives at **`~/.ntm/policy.yaml`**. Create the directory and file:

```bash
mkdir -p ~/.ntm
```

Write the baseline policy. This is a **starter set** aligned with the DECISIONS.md blocked-command examples; extend as you discover patterns during pilot runs.

```yaml
# ~/.ntm/policy.yaml — overnight pilot baseline
# Tiers: block (hard deny) and allow (permit). No approval_required for unattended mode.
#
# Extend blocked patterns as pilot runs reveal risky commands.
# NTM evaluates top-down; first match wins.

blocked:
  # --- Git: destructive history rewrites ---
  - pattern: "git reset --hard"
    reason: "Destroys uncommitted changes; use 'git stash' first"
  - pattern: "git push --force"
    reason: "Rewrites remote history; use --force-with-lease if needed"
  - pattern: "git push.*--force"
    reason: "Rewrites remote history"
  - pattern: "git clean -fd"
    reason: "Removes untracked files permanently"

  # --- Filesystem: broad destructive commands ---
  - pattern: "rm -rf /"
    reason: "System-wide recursive delete"
  - pattern: "rm -rf /*"
    reason: "System-wide recursive delete"
  - pattern: "rm -rf ~"
    reason: "Deletes entire home directory"
  - pattern: "rm -rf ."
    reason: "Deletes current directory tree"
  - pattern: "chmod -R 777"
    reason: "Opens all permissions recursively"
  - pattern: "chown -R"
    reason: "Recursive ownership change — review manually"

  # --- Database: destructive SQL ---
  - pattern: "DROP DATABASE"
    reason: "Destroys entire database"
  - pattern: "DROP TABLE"
    reason: "Destroys table and data"
  - pattern: "TRUNCATE"
    reason: "Deletes all rows without logging"

  # --- Container: broad destructive commands ---
  - pattern: "docker system prune"
    reason: "Removes all unused containers, images, networks"
  - pattern: "podman system prune"
    reason: "Removes all unused containers, images, networks"

allowed:
  # Explicitly permit common safe operations so NTM does not
  # accidentally block normal development workflow.
  - pattern: "git add"
  - pattern: "git commit"
  # Do not add a bare "git push" here: allowed rules run before blocked rules,
  # so a broad match would permit "git push --force" before force-push blocks apply.
  # Ordinary "git push" is implicitly allowed when no rule matches.
  - pattern: "git pull"
  - pattern: "git stash"
  - pattern: "git diff"
  - pattern: "git log"
  - pattern: "git status"
  - pattern: "git branch"
  - pattern: "pytest"
  - pattern: "python"
  - pattern: "pip install"
  - pattern: "curl"
  - pattern: "podman-compose"
  - pattern: "podman run"
  - pattern: "podman stats"
  - pattern: "podman ps"
```

### 3.3 Validate the policy

```bash
ntm policy validate
ntm policy show --all
```

**Expected:** no validation errors; all blocked and allowed patterns listed.

### 3.4 Install PATH wrappers

NTM intercepts commands via PATH-level wrapper scripts. Install them:

```bash
ntm safety install
ntm safety status
```

**Expected:** `ntm safety status` reports safety system active with wrapper scripts on PATH.

**Weakest link reminder** (from DECISIONS.md): PATH-based interception can be bypassed if the orchestrator uses **absolute paths** to binaries or runs commands **inside containers** without NTM's wrappers. The pilot must verify Ralph's execution path goes through NTM's interception layer.

---

## 4. DCG installation (defense-in-depth)

[DCG](https://github.com/Dicklesworthstone/destructive_command_guard) adds a second safety layer that hooks into agent tool-use events. When it blocks a command, it prints a **reason** and a **safer-alternative tip** — which the agent can read and act on.

### 4.1 Install via script

```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/destructive_command_guard/main/install.sh?$(date +%s)" | bash -s -- --easy-mode
```

Verify:

```bash
dcg --version
```

### 4.2 Default packs

DCG ships with **core packs** enabled by default (`core.filesystem`, `core.git`, `database.postgresql`, `containers.docker`). For the pilot, defaults are sufficient. Enable more packs later via `~/.config/dcg/config.toml` as needed.

### 4.3 Smoke: explain mode

```bash
dcg explain "git reset --hard HEAD~5"
```

**Expected:** output explains **why** the command is blocked and suggests a **safer alternative** (e.g. "Consider using `git stash` first").

### 4.4 Smoke: blocked command with tip

Use **`dcg test`** (CLI name in current DCG releases; it evaluates the command against enabled packs).

The **`core.filesystem`** pack deliberately **allows** `rm -rf` under **`/tmp`**, **`/var/tmp`**, and **`$TMPDIR`** so normal cleanup is not blocked. A path like `/tmp/important-data` therefore often returns **ALLOWED** — that is expected, not a failed install.

Run a path **outside** those temp locations first:

```bash
dcg test "rm -rf ./src"
```

**Expected:** blocked (or otherwise non-allow) with reason and safer-alternative guidance (exact wording varies by DCG version).

Optional sanity check that the temp exception is active:

```bash
dcg test "rm -rf /tmp/important-data"
```

**Expected:** **ALLOWED** (temp-directory exception).

### 4.5 NTM + DCG coexistence

After DCG is installed, re-run:

```bash
ntm deps -v
```

**Expected:** `dcg` now shows as found/available in the optional integrations list.

NTM and DCG operate at **different layers**:
- **NTM:** PATH-level wrapper scripts — intercepts when the shell resolves a command name.
- **DCG:** Agent hook — intercepts at the tool-use/pre-execution event inside the agent CLI.

Both can fire on the same command. This is intentional defense-in-depth: if one layer misses a pattern, the other catches it.

---

## 5. NTM smoke tests

### 5.1 Safety status

```bash
ntm safety status
```

**Expected:** reports active, wrappers installed, policy loaded.

### 5.2 Check a blocked command

```bash
ntm safety check -- git reset --hard
```

**Expected:** blocked with the reason from `policy.yaml` ("Destroys uncommitted changes; use 'git stash' first").

### 5.3 Check an allowed command

```bash
ntm safety check -- git status
```

**Expected:** allowed / no block.

### 5.4 View blocked history

```bash
ntm safety blocked --hours 24
```

**Expected:** lists any commands blocked in the last 24 hours (may be empty if no agent has run yet; that is fine for the smoke test).

### 5.5 Audit trail

If you created a session for testing:

```bash
ntm audit show <session-name>
```

Or if no session exists yet, confirm the command does not error fatally:

```bash
ntm audit show test 2>&1 || echo "no session yet — expected"
```

---

## 6. SLB — V1 stepping stone (do not install for pilot)

[SLB (Simultaneous Launch Button)](https://github.com/Dicklesworthstone/slb) implements a **two-person rule** for destructive commands: when an agent requests a risky operation, a **second agent** (or human) must review and approve before execution.

### 6.1 Why defer to V1

| Concern | Pilot | V1 |
|---------|-------|----|
| **Who approves overnight?** | No one — pilot is single-agent, single-orchestrator | Second agent with different model/context can review |
| **Complexity** | Adds SQLite state, daemon, session management | Justified when multi-agent swarms are running |
| **NTM compatibility** | NTM already references SLB-style approvals in its policy engine | Wire `ntm approve` → SLB when multi-agent is live |

### 6.2 What SLB provides (for future reference)

- **Risk tiers:** CRITICAL (2+ approvals), DANGEROUS (1 approval), CAUTION (auto-approve after 30s), SAFE (skip).
- **Command hash binding:** approvals bind to exact command via SHA-256.
- **Agent Mail integration:** notify reviewers via NTM's coordination layer.
- **TUI dashboard:** human morning review of what was approved/rejected.
- **Install:** `go install github.com/Dicklesworthstone/slb/cmd/slb@latest` or `brew install dicklesworthstone/tap/slb`.

### 6.3 Activation trigger

Add SLB to the stack when:
- Multi-agent swarms are running (more than one coding agent per overnight session).
- The `approval_required` tier is re-enabled in `~/.ntm/policy.yaml`.
- A Quint decision record is created for the two-person rule boundary.

---

## 7. Resource check

After NTM + DCG are installed and PATH wrappers are active:

```bash
free -h
which ntm && ntm --version
which dcg && dcg --version
```

NTM and DCG are **small Go/Rust binaries** with negligible idle RAM. They should not measurably change the memory profile vs. pre-install.

---

## 8. T061 completion checklist

- [ ] NTM installed; `ntm --version` succeeds.
- [ ] `ntm deps -v` shows `tmux` found.
- [ ] `~/.ntm/policy.yaml` created with **block + allow** baseline (no `approval_required`).
- [ ] `ntm policy validate` passes.
- [ ] `ntm safety install` completes; `ntm safety status` reports active.
- [ ] `ntm safety check -- git reset --hard` reports **blocked**.
- [ ] `ntm safety check -- git status` reports **allowed**.
- [ ] DCG installed; `dcg --version` succeeds.
- [ ] `dcg explain "git reset --hard HEAD~5"` prints reason + safer alternative.
- [ ] `ntm deps -v` shows DCG as available.
- [ ] SLB documented as V1 stepping stone; **not** installed.
- [ ] Revision row added below when the operator finishes the checklist.

---

## 9. References

- NTM repository: [https://github.com/Dicklesworthstone/ntm](https://github.com/Dicklesworthstone/ntm)
- NTM install: `curl -fsSL ... | bash -s -- --easy-mode` or `go install github.com/Dicklesworthstone/ntm/cmd/ntm@latest`
- DCG repository: [https://github.com/Dicklesworthstone/destructive_command_guard](https://github.com/Dicklesworthstone/destructive_command_guard)
- SLB repository: [https://github.com/Dicklesworthstone/slb](https://github.com/Dicklesworthstone/slb)
- Prior steps: [`vps-dependency-smoke-tests.md`](./vps-dependency-smoke-tests.md) (T060)
- Next: [`scenario-catalog.md`](./scenario-catalog.md) (T062) or [`vps-scheduler.md`](./vps-scheduler.md) (T063)

---

## Revision

| Date | Notes |
|------|-------|
| 2026-04-15 | Initial T061 runbook: NTM install + overnight baseline policy (block+allow only); DCG install + safer-alternative tips; SLB as V1 stepping stone. |
