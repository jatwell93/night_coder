# Ralph orchestrator (pilot) — T058

Install **Ralph Orchestrator** on the overnight VPS and verify **CLI health** before wiring Doppler (T059), DTU mocks (T060), and unattended schedules (T063).

**Orchestration choice:** Ralph — see `.quint/decisions/dec-20260406-001.md` and `docs/superpowers/plans/2026-04-03-overnight-agent-vertical-slice-pilot.md` (Appendix A).

**Prerequisites**

- [`vps-bootstrap.md`](./vps-bootstrap.md) — hardened Ubuntu 24.04, `deploy` user.  
- [`vps-container-runtime.md`](./vps-container-runtime.md) — **Path A** (rootless Podman + linger + `podman-compose`) for this pilot.

**Not a prerequisite here:** a `night_coder` git checkout on the VPS (Ralph installs from upstream). You **will** need [`vps-bootstrap.md` §12](./vps-bootstrap.md#12-pilot-repository-checkout-on-the-vps) before **T060** and other runbooks that read files under `docs/superpowers/pilot/`.

Do **not** commit API keys, provider tokens, or `ralph.yml` secrets; use env injection / Doppler (T059).

---

## 1. What you are installing

Upstream Ralph is distributed as the **`ralph`** CLI (current generation). The old **Python `ralph_orchestrator.py`** flow is **legacy v1** and is no longer the recommended install path.

**Official docs:** [Installation](https://mikeyobrien.github.io/ralph-orchestrator/getting-started/installation/) · [Quick start](https://mikeyobrien.github.io/ralph-orchestrator/getting-started/quick-start/) · [CLI reference](https://mikeyobrien.github.io/ralph-orchestrator/guide/cli-reference/)

**This task (T058)** stops at **CLI verification** (`ralph --version`, help, preset list). A full **agent loop** also needs at least one **AI CLI** (Claude Code, Gemini CLI, OpenCode, etc.) and credentials — document installs separately or defer until T059/T060 when secrets are available.

---

## 2. Pick an install method (VPS-friendly)

| Method | Best when | Needs |
|--------|-----------|--------|
| **A — GitHub release installer** | Minimal toolchain on the Droplet; no global npm layout to manage. | `curl`, `sh`; installs `ralph` onto `PATH` per script output. |
| **B — npm global** | You already standardize on Node for other pilot tools. | **Node.js ≥ 18**, npm. |
| **C — Cargo** | Rust already installed for other reasons. | Rust toolchain, `cargo install ralph-cli`. |

**Recommendation for this pilot:** try **A** first; fall back to **B** if the installer fails or you prefer npm upgrades.

---

## 3. Method A — GitHub Releases installer

As `deploy` (or with `sudo` only if the script instructs you):

```bash
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/mikeyobrien/ralph-orchestrator/releases/latest/download/ralph-cli-installer.sh | sh
```

Follow any on-screen **PATH** instructions (often `~/.local/bin` or `~/.cargo/bin`). Open a **new shell** or `source ~/.bashrc` after editing profile.

```bash
command -v ralph
ralph --version
```

---

## 4. Method B — npm global

### 4.1 Node.js 18+ on Ubuntu 24.04

Check stock packages first:

```bash
apt-cache policy nodejs
nodejs --version 2>/dev/null || true
```

If the version is **&lt; 18**, install a current LTS via [NodeSource](https://github.com/nodesource/distributions) or another supported channel, then:

```bash
sudo apt update
sudo apt install -y nodejs
node --version   # expect v18.x or newer
```

### 4.2 User-writable global prefix (required as non-root `deploy`)

Default npm global root is `/usr/local/lib/node_modules` → **`EACCES`** without sudo. **Do not** use `sudo npm install -g` (root-owned globals). Use a prefix under `$HOME`:

```bash
mkdir -p "$HOME/.npm-global"
npm config set prefix "$HOME/.npm-global"
grep -q 'npm-global/bin' "$HOME/.bashrc" || echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> "$HOME/.bashrc"
export PATH="$HOME/.npm-global/bin:$PATH"
```

### 4.3 Install Ralph CLI

```bash
npm install -g @ralph-orchestrator/ralph-cli
which ralph
ralph --version
```

If `ralph` is not found in a **new** SSH session, ensure `~/.bashrc` is sourced (`export PATH="$HOME/.npm-global/bin:$PATH"`).

### 4.4 Smoke without global install (optional)

```bash
npx @ralph-orchestrator/ralph-cli --version
```

---

## 5. Method C — Cargo

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
cargo install ralph-cli
ralph --version
```

**Note:** Compiling on a **4 GB** Droplet is possible but slow; prefer **A** or **B** unless you already need Rust.

---

## 6. T058 — CLI health checks (required)

Run as **`deploy`** after `ralph` resolves on `PATH`:

```bash
ralph --version
ralph --help
ralph init --list-presets
```

**Expected**

- `--version` prints a version string (no traceback).  
- `--help` exits 0 and shows subcommands.  
- `init --list-presets` exits 0 and lists preset names (may be empty only if upstream changes; any non-error output is acceptable).

If you see **“no AI agents detected”** only when running `ralph run`, that is **expected** until you install an AI CLI (next section). T058 is still satisfied if the three commands above succeed.

---

## 7. Optional — install one AI CLI (for first real `ralph run`)

Pick **one** aligned with your provider and budget. Examples from upstream docs:

```bash
# Claude Code (npm)
npm install -g @anthropic-ai/claude-code

# Gemini CLI (npm) — upstream currently wants Node **>= 20** (see `npm WARN EBADENGINE`)
npm install -g @google/gemini-cli

# OpenCode (shell installer; also available via npm per upstream)
# curl -fsSL https://opencode.ai/install | bash
```

Configure API keys via **environment variables** or **Doppler** (T059); never commit `.env` with live keys.

**Dry orientation** (after backend + secrets exist):

```bash
cd ~
mkdir -p ~/ralph-smoke && cd ~/ralph-smoke
ralph init --backend opencode   # or gemini / claude per `ralph init --help`
# Then follow upstream quick-start for a tiny prompt / plan path
```

### 7.1 `ralph doctor` and “Claude” failures when you use Gemini / OpenCode

`ralph doctor` reads **`ralph.yml` from the current working directory** unless you pass **`-c` / `--config`**. If you run it from **`~`** and your project lives in **`~/ralph-smoke`**, you will see:

```text
Config file "ralph.yml" not found, using defaults
```

In that mode Ralph still runs **default preflight checks**, which include **`backend:claude`** — so **`claude` missing** and **`ANTHROPIC_API_KEY`** warnings appear even though your real project uses **OpenCode** or **Gemini**.

**Fix:** run doctor **in the project directory** or point at the config file:

```bash
cd ~/ralph-smoke
ralph doctor -c ralph.yml
```

If upstream still lists Claude as a checked backend when your `ralph.yml` only enables OpenCode/Gemini, treat that as a **tooling quirk** (or report upstream); your **smoke test with `ralph init --backend opencode` + `ralph run`** is the authoritative check for your chosen backends.

### 7.2 Using Gemini **and** OpenCode (two backends)

`ralph init --backend …` creates **one** default `cli.backend` in `ralph.yml`. It will **not** merge a second backend; re-running init without `--force` errors because the file already exists.

**Ways to use both CLIs:**

1. **Switch per run (simplest for trials)** — keep `ralph.yml` as-is and override on the CLI:

   ```bash
   ralph run -c ralph.yml --backend gemini
   ralph run -c ralph.yml --backend opencode
   ```

   (Exact flag spelling: `ralph run --help` if `--backend` differs by version.)

2. **Edit `ralph.yml`** — change the single default:

   ```yaml
   cli:
     backend: "gemini"   # or "opencode"
   ```

3. **True “both at once”** — use **hat mode**: default `cli.backend` plus **per-hat `backend:`** (e.g. planner on `gemini`, coder on `opencode`). Requires `starting_event`, `triggers`, `publishes`, and hat definitions. See [Backends — per-hat override](https://mikeyobrien.github.io/ralph-orchestrator/guide/backends/#per-hat-backend-override) and [Configuration — hats](https://mikeyobrien.github.io/ralph-orchestrator/guide/configuration/).

**`ralph doctor` auth WARN for OpenCode:** upstream accepts **`OPENCODE_API_KEY`**, **`ANTHROPIC_API_KEY`**, or **`OPENAI_API_KEY`** depending on provider; set the one that matches how you use `opencode` (and **`GEMINI_API_KEY`** when exercising Gemini). Warnings are hints until keys are injected (e.g. T059 / Doppler).

Keep smoke dirs **outside** the git repo or add to `.gitignore` if under `night_coder`.

---

## 8. `ralph web` and heavy dependencies (defer)

The upstream **web dashboard** (`ralph web`) pulls **Rust RPC + Node frontend** and is **not** required for T058. On a small VPS, defer until you need UI observability; see [README — Web Dashboard](https://github.com/mikeyobrien/ralph-orchestrator/blob/main/README.md).

---

## 9. Troubleshooting

| Symptom | Action |
|---------|--------|
| `ralph: command not found` | Fix `PATH` (npm prefix, `~/.local/bin`, `~/.cargo/bin`); open new SSH session. |
| `EACCES` on `/usr/local/lib/node_modules` | Set npm `prefix` to `$HOME/.npm-global` (§4.2); never `sudo npm install -g` for routine use. |
| Old `ralph` from legacy pip | [Migrate off v1](https://mikeyobrien.github.io/ralph-orchestrator/reference/migration-v1/); `which -a ralph` to see duplicates. |
| `ralph doctor` fails on **Claude** but you use **Gemini/OpenCode** | Run from the directory that contains `ralph.yml`, or `ralph doctor -c /path/to/ralph.yml` (see §7.1). |
| `EBADENGINE` for **gemini-cli** | Upgrade to **Node 20+** (NodeSource or `nvm install 20`). |
| `ralph.yml already exists` when changing backend | Edit `cli.backend` in `ralph.yml`, use `ralph run --backend …`, or `ralph init --force` (overwrites config). See §7.2. |

---

## 10. T058 completion checklist

- [ ] One install method (**A**, **B**, or **C**) completed successfully.  
- [ ] `ralph --version`, `ralph --help`, and `ralph init --list-presets` all succeed.  
- [ ] (Optional) One AI CLI installed; `ralph run` smoke deferred until secrets (T059) if preferred.  
- [ ] No API keys or tokens committed to `night_coder`.

---

## 11. Hand-off

- **T059:** Doppler + env injection for provider keys and Ralph-related secrets.  
- **T060:** WireMock / compose — use `podman-compose` from T057.  
- **T063:** `tmux` or systemd for detached runs — see pilot plan Appendix A pattern.

---

## References

- [Ralph Orchestrator — Installation](https://mikeyobrien.github.io/ralph-orchestrator/getting-started/installation/)  
- [Ralph — Quick start](https://mikeyobrien.github.io/ralph-orchestrator/getting-started/quick-start/)  
- Prior steps: [`vps-bootstrap.md`](./vps-bootstrap.md), [`vps-container-runtime.md`](./vps-container-runtime.md)

---

## Revision

| Date | Notes |
|------|--------|
| 2026-04-11 | Initial T058 runbook: installer / npm / cargo paths; CLI health checks; optional AI CLI; align with current upstream Ralph CLI (not legacy Python v1). |
| 2026-04-12 | §7.1: `ralph doctor` cwd / `-c ralph.yml` vs default Claude checks; Gemini CLI Node 20+ note; troubleshooting rows. |
| 2026-04-12 | §7.2: two backends via `ralph run --backend` / edit `ralph.yml` / hat overrides; `init --force` note; OpenCode auth env hints. |
| 2026-04-12 | Prerequisites: note that repo checkout (`vps-bootstrap.md` §12) is not required for Ralph install but is required before T060+. |
