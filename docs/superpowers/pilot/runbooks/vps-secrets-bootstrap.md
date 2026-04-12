# VPS secrets bootstrap (pilot) — T059

Configure **[Doppler](https://www.doppler.com/)** with **read-only service tokens** and a documented **`doppler run`** injection path for the overnight VPS run environment. This satisfies the human part of **T059** and gives you a repeatable checklist for token minting, scope approval, verification, and rotation.

**Decisions and briefs**

- Quint: [`.quint/decisions/dec-20260407-002.md`](../../../../.quint/decisions/dec-20260407-002.md) — Doppler as secrets/IAM pillar.  
- Pilot brief: [`../secrets/IMPLEMENTATION-BRIEF.md`](../secrets/IMPLEMENTATION-BRIEF.md).  
- Deeper comparison: [`../../../../research_secrets_iam/findings_secrets.md`](../../../../research_secrets_iam/findings_secrets.md).

**Prerequisites**

- [`vps-bootstrap.md`](./vps-bootstrap.md) — Ubuntu 24.04, non-root `deploy`, SSH hardening.  
- [`vps-ralph-install.md`](./vps-ralph-install.md) — Ralph CLI installed; **provider API keys** are intentionally **not** required until this runbook is complete.  
- **Optional for T059 alone:** a local `night_coder` git checkout on the VPS is **not** required to configure Doppler. You **will** need it before T060+ (see [`vps-bootstrap.md` §12](./vps-bootstrap.md#12-pilot-repository-checkout-on-the-vps)) when runbooks reference paths under `docs/superpowers/pilot/`.

Do **not** commit `DOPPLER_TOKEN`, service tokens, provider API keys, Langfuse keys, or a populated `.env`. Use placeholders in notes; store values only in Doppler (or another approved vault), and inject at runtime.

---

## 1. What you are establishing

| Deliverable | Why it matters |
|-------------|----------------|
| **Doppler org + project** | Single place of record for pilot secrets; separates personal tokens from machine/CI access. |
| **Configs** (e.g. `pilot`, `ci`) | Lets you scope **different service tokens** per trust boundary (VPS vs CI) without sharing one mega-token. |
| **Service token** (read-only, **one config**) | Long-lived bootstrap credential for the host or runner; replaces scattering raw API keys in files. See [Service tokens](https://docs.doppler.com/docs/service-tokens). |
| **`doppler run -- <command>`** | Process inherits secrets as **environment variables** only for that process tree — aligns with `dec-20260407-002` and the implementation brief. |
| **Documented rotation** | When keys or tokens leak, you can revoke/replace without guessing which file on disk was canonical. |

---

## 2. Approve secret-scope policy (do this before minting tokens)

Answer these explicitly (even if the answer is “not used in this pilot”). That approval is part of **T059 [USER]**.

**In scope for the overnight pilot config (suggested names: `pilot` on the VPS, `ci` in automation)**

| Category | Example Doppler secret keys (env names) | Notes |
|----------|----------------------------------------|--------|
| LLM / agent backends | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `OPENCODE_API_KEY` | Ralph/OpenCode/Gemini/Claude expectations are summarized in [`vps-ralph-install.md`](./vps-ralph-install.md) (optional AI CLI section). Store only the keys you actually use. |
| Orchestration / tooling | Keys required by any **non-git** pilot script (e.g. registry pull if not using public images) | Keep the set **minimal**; prefer narrow tokens from the provider where possible. |
| Observability | Langfuse-style **`LANGFUSE_PUBLIC_KEY`**, **`LANGFUSE_SECRET_KEY`** (or the exact names your OTLP/trace client expects) | Do not log raw values; align with later redaction tasks (T064/T065). |

**Out of scope or forbidden**

| Item | Policy |
|------|--------|
| SSH private keys, `kubeconfig`, disk encryption passphrases | **Not** in Doppler for this pilot unless your org mandates a single vault for everything — default is **host-native** handling only. |
| Same service token across **unrelated** projects | **Rejected** per `dec-20260407-002` — one token per trust boundary/config. |
| Writing secrets from the VPS into the **git repo** | **Rejected** — manifests and code stay in git; secrets stay in Doppler (or operator-managed env files **outside** the repo). |

**Operator ownership**

- Who may create/revoke Doppler tokens?  
Only the user/project maintainer
- Rotation cadence for the pilot? **Manual** updates in Doppler are acceptable for the pilot. V1 should move to automated rotation; **3 months**.  

---

## 3. Create the Doppler project and configs

Performed in the **[Doppler dashboard](https://dashboard.doppler.com/)** or via [Doppler CLI](https://docs.doppler.com/docs/install-cli) on a **trusted workstation** (recommended for first-time setup).

### 3.1 Environments vs config slugs

New Doppler projects include three **[environments](https://docs.doppler.com/docs/default-environments)** with root configs: **`dev`**, **`stg`**, **`prd`**. Additional configs are usually **[branch configs](https://docs.doppler.com/docs/branch-configs)** created **inside** one of those environments.

The CLI’s [`configs create`](https://docs.doppler.com/reference/configs-create) API requires:

1. **`--environment`** — the **environment** slug only: **`dev`**, **`stg`**, or **`prd`**.  
   - If you pass a **config** name here (e.g. `dev_pilot`), you get **`Invalid environment id`**.  
   - If you omit `--environment`, you get **`you must specify an environment`**.

2. **Config name** (first positional argument) — for the Development environment, Doppler requires the **full branch name** including the prefix, e.g. **`dev_pilot`**, not the bare suffix `pilot`.  
   - If you use `pilot` with `--environment dev`, you get: **`Config name must start with "dev_" (ex: dev_backend)`**.

So the working pattern is **`dev`** + **`dev_pilot`**, not `dev` + `pilot`, and not `dev_pilot` as the environment.

After creation, `-c` / `--config` / `DOPPLER_CONFIG` match that same slug (e.g. **`dev_pilot`**). You can still run `doppler configs --project …` to confirm before minting tokens.

**Suggested layout (matches `dec-20260407-002` pre-conditions)**

| Role | `--environment` | **Config name** at `configs create` | Same value for `-c` / `DOPPLER_CONFIG` | Service token |
|------|-----------------|-------------------------------------|----------------------------------------|----------------|
| VPS / overnight | `dev` | `dev_pilot` | `dev_pilot` | Token A — read-only, **this config only** |
| CI / automation | `dev` | `dev_ci` | `dev_ci` | Token B — read-only, **this config only** |

You can instead put CI under **`stg`**: `--environment stg` and config name **`stg_ci`** (name must start with `stg_` in that environment).

**Create branch configs** (CLI example; project name is illustrative — substitute yours):

```bash
# After `doppler login` on the workstation (one-time human auth)
doppler projects create night-coder-pilot   # skip if project already exists
doppler configs create dev_pilot --project night-coder-pilot --environment dev
doppler configs create dev_ci --project night-coder-pilot --environment dev
```

**Confirm the exact config slugs** (use these everywhere: secrets, tokens, `DOPPLER_CONFIG`):

```bash
doppler configs --project night-coder-pilot
```

Add secrets in the dashboard **or** (replace `dev_pilot` with the slug from the list above):

```bash
doppler secrets set ANTHROPIC_API_KEY="REPLACE_ME" --project night-coder-pilot --config dev_pilot
# repeat for each approved key — never commit this history to shell logs in shared environments
```

**Simpler alternative (no branch configs):** use the built-in root configs **`dev`** and **`stg`** as your two trust boundaries (`-c dev` on the VPS, `-c stg` in CI) and skip `doppler configs create` entirely. Service tokens are still scoped per config (`dev` vs `stg`).

Use **placeholder** values until you are ready to paste real keys; rotate immediately if a placeholder was ever exposed.

---

## 4. Mint a read-only service token (VPS / pilot config)

**Goal:** exactly **one** long-lived secret on the machine: `DOPPLER_TOKEN` with **read** access to **only** the VPS config (example slug **`dev_pilot`** — use yours from section 3).

**Dashboard path (typical)**

1. Open the project → **Development** (or your chosen environment) → select the branch config (e.g. **`dev_pilot`**).  
2. **Access** → **Service Tokens** → create token with **read** permissions only.  
3. Copy the token **once**; you cannot retrieve it again after closing the dialog.

**CLI path** (replace `dev_pilot` with your slug from `doppler configs`):

```bash
doppler configs tokens create pilot-vps-deploy --project night-coder-pilot --config dev_pilot --access read
```

Official reference: [Service tokens](https://docs.doppler.com/docs/service-tokens).

**CI token** (e.g. config **`dev_ci`**): repeat with a **different** token name and attach only to that CI config. Do not reuse the VPS token in GitHub Actions or vice versa.

---

## 5. Install Doppler CLI on the VPS

SSH as `deploy` per [`vps-bootstrap.md`](./vps-bootstrap.md), then install the CLI (official installer):

```bash
curl -Ls --tlsv1.2 --proto "=https" https://cli.doppler.com/install.sh | sh
```

Open a **new** shell or `hash -r`, then:

```bash
doppler --version
```

Documentation: [Install CLI](https://docs.doppler.com/docs/install-cli).

---

## 6. Provide the token to the VPS without committing it

**6.A** is the short-lived option. **6.B** and **6.C** target **different consumers**: the Doppler **CLI** in your SSH sessions vs **`systemd` units**. Doing **both 6.B and 6.C** is **not** a functional mistake — you simply store the bootstrap material in **two places** (CLI config + env file). The tradeoff is **duplication**: when you **rotate** the service token, update **both** unless you standardize on one path. Optional cleanup: keep **6.B** for day-to-day SSH; remove **6.C** files until you define a real **`EnvironmentFile=`** unit, or drop **6.B** and only use **6.C** plus `source` when you need the CLI (less ergonomic).

| Section | Token lives where | Typical use |
|---------|-------------------|-------------|
| **6.A** | Only in that shell’s environment until you disconnect | Quick smoke tests |
| **6.B** | Written into the Doppler **CLI config** for `deploy` under `$HOME` (still not in git) | Interactive `doppler` / `doppler run` over SSH |
| **6.C** | An **`EnvironmentFile`** on the VPS read by **`systemd`** for a unit | Unattended timers/services (T063); not loaded into your login shell unless you add that yourself |

All avoid putting the token in the `night_coder` git tree.

### 6.A Ephemeral shell (smoke tests only)

From an **interactive** SSH session (token visible only in that session’s memory):

```bash
export DOPPLER_TOKEN="dp.st.xxxxx.replace-with-real-token"
export DOPPLER_PROJECT="night-coder-pilot"
export DOPPLER_CONFIG="dev_pilot"   # must match `doppler configs` slug (not necessarily `pilot`)
```

**Do not** paste tokens into shared screen recordings, CI logs, or issue trackers.

### 6.B Persistent **user** scope for `deploy` (common for a dedicated pilot box)

Still **no** git commit: store the token in Doppler’s CLI config under `deploy`’s home directory (the CLI reads it on each `doppler` invocation so you do not need `export DOPPLER_TOKEN` in every new shell).

1. SSH as `deploy`.  
2. **Put the service token in the shell once** (same idea as 6.A, but only the token line is required for 6.B). This is where the **actual secret value** enters the process — the next step copies it from `$DOPPLER_TOKEN` into the saved CLI config:

```bash
export DOPPLER_TOKEN='dp.st.xxxxx.paste-your-service-token-here'
```

Use **single quotes** so the shell does not mangle special characters. Prefer pasting from a password manager over leaving the token in shell history (see your shell’s `HISTCONTROL` / `histignorespace` if you prefix the line with a space).

3. **Persist** that value and your default project/config for this user:

```bash
doppler configure set token "$DOPPLER_TOKEN" --scope "$HOME"
doppler configure set project night-coder-pilot --scope "$HOME"
doppler configure set config dev_pilot --scope "$HOME"   # use your actual config slug
unset DOPPLER_TOKEN
```

The important line is **`doppler configure set token "$DOPPLER_TOKEN"`**: it reads the variable you set in step 2 and writes the token into the scoped config store (under your Doppler CLI config directory for `--scope "$HOME"`). After `unset`, the token is no longer in the shell environment but remains available to the CLI from disk.

4. Confirm the CLI works **without** exporting the token in new shells:

```bash
doppler me
doppler secrets --only-names
```

If your team policy forbids disk-stored tokens, skip this and use **6.A** plus **6.C** for scheduled jobs only.

### 6.B.1 Reset and redo **6.B** cleanly

**Clear shell overrides** (optional but avoids confusion):

```bash
unset DOPPLER_TOKEN DOPPLER_PROJECT DOPPLER_CONFIG 2>/dev/null || true
```

**Remove the saved home scope** (token + project + config for `deploy`’s default CLI use):

```bash
doppler configure unset token --scope "$HOME"
doppler configure unset project --scope "$HOME"
doppler configure unset config --scope "$HOME"
```

Confirm nothing stale: `doppler configure debug` (expect missing token / project / config for that scope).

**Last resort** if something still looks wrong: [`doppler configure reset`](https://docs.doppler.com/docs/cli-troubleshooting) clears **all** CLI configuration for this user — use only when targeted `unset` is not enough.

**Redo 6.B:** run steps **2–4** in **§6.B** once. Use the **VPS** service token minted for **`dev_pilot`** and **`doppler configure set config dev_pilot`**.

**Do not** run **6.B twice** for **`dev_ci`** then **`dev_pilot`** hoping “last wins.” There is only **one** stored token slot per scope — the second token **overwrites** the first, and a **CI-scoped** token **cannot** read **`dev_pilot`**. For occasional **`dev_ci`** use from the same account, use a **one-off** env for that command (e.g. `DOPPLER_TOKEN=…ci…` `DOPPLER_CONFIG=dev_ci` `doppler run …`) or a separate **`systemd`** unit with **`EnvironmentFile=`** (6.C), not a second chained **6.B**.

### 6.C `systemd` / unattended runs (forward-compatible with T063)

Create this file **on the VPS** at an **absolute path outside the `night_coder` git checkout** — e.g. under `/etc/…` or `/home/deploy/.config/…`. **`systemd` only reads paths on that machine**; it does not look inside your repo. Putting secrets under `~/night_coder/…` risks accidental commit, backup sync, or tooling that scans the tree — prefer a dedicated ops path.

For timers or services, use an **`EnvironmentFile=`** readable only by the service user (e.g. `/etc/night-coder/doppler.pilot.env` with mode `600` and owner `deploy`), containing:

```bash
DOPPLER_TOKEN=dp.st....
DOPPLER_PROJECT=night-coder-pilot
DOPPLER_CONFIG=dev_pilot
```

**Creating the files (paths must start with `/`)** — relative paths like `etc/night-coder` under `~` would create **`/home/deploy/etc/night-coder`**, which is **not** what you want and is easy to confuse with **`/etc/night-coder`**.

**Option A — under `/etc` (needs `sudo` once to create the dir and hand off ownership):**

```bash
sudo mkdir -p /etc/night-coder
sudo touch /etc/night-coder/doppler.pilot.env /etc/night-coder/doppler.ci.env
sudo chown deploy:deploy /etc/night-coder/doppler.pilot.env /etc/night-coder/doppler.ci.env
sudo chmod 600 /etc/night-coder/doppler.pilot.env /etc/night-coder/doppler.ci.env
```

**What those steps do:** `sudo touch` creates **empty** files as **root**. **`chown deploy:deploy`** *changes ownership* to `deploy` (it does not “create” ownership — root owned the new files until this step). **`chmod 600`** means **only the owner** may read/write (`rw-------`); **group** and **other** bits are off, so **other OS user accounts** (anything not running as `deploy`) cannot read the file via normal permissions. (The Unix **superuser** can still bypass that; file modes mainly contain **non-root** lateral movement.)

Then as **`deploy`**, edit each file (same folder; second file is for the **CI** service token and `DOPPLER_CONFIG=dev_ci`):

```bash
nano /etc/night-coder/doppler.pilot.env
nano /etc/night-coder/doppler.ci.env
```

Use **one `DOPPLER_TOKEN` per file** (VPS token in `pilot` env file, CI token in `ci` env file). `DOPPLER_PROJECT` can be the same; `DOPPLER_CONFIG` must match each token’s config (`dev_pilot` vs `dev_ci`).

**Option B — no `sudo` after install:** put files under **`$HOME/.config/night-coder/`** (mode `700` on the directory, `600` on each file), point **`EnvironmentFile=`** at e.g. `/home/deploy/.config/night-coder/doppler-pilot.env`.

Reference: systemd [EnvironmentFile=](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=).

Do **not** check this file into git. Restrict path ACLs the same way you would for an SSH key.

### 6.D Containers (Podman from T057)

**Only if** you run workloads with **`podman compose`** (or similar) and want the **host** to inject secrets into that process tree. **6.B does not replace 6.D** — they are unrelated unless your compose workflow explicitly wraps with `doppler run`. If you are not using compose on the VPS yet, **skip 6.D**.

Prefer **host** invocation:

```bash
doppler run -- podman compose -f /path/to/compose.yml up
```

so secrets enter the container **only** if the compose file maps `environment:` from the parent process or explicit `env` flags you control. Avoid baking tokens into image layers. See also [`vps-container-runtime.md`](./vps-container-runtime.md).

**Practice layout (optional):** if you create a directory under **`/`** (e.g. `/srv/night-coder/compose`), `sudo mkdir` leaves the directory **root-owned** — **`deploy`** cannot drop new files there until you **`sudo chown deploy:deploy`** on the **directory** (not only on `compose.yaml`). An **empty** `compose.yaml` is not enough for a meaningful `podman compose up`; use a minimal valid compose when you are ready to test. Prefer **`$HOME/…`** or **`/srv/…`** over inventing **`/podman/…`** unless you standardize that path in your ops docs.

---

## 7. Run commands under `doppler run`

**How the CLI picks project + config** (highest wins first; see [Configure CLI behavior](https://docs.doppler.com/docs/environment-based-configuration)):

1. **Flags** on the command, e.g. `doppler run -p night-coder-pilot -c dev_pilot -- …`  
2. **Environment variables** `DOPPLER_PROJECT`, `DOPPLER_CONFIG`, `DOPPLER_TOKEN` (e.g. injected by **`systemd` `EnvironmentFile=`** for a service — then `doppler run` uses those)  
3. **`doppler.yaml`** / directory setup if present  
4. **Saved CLI config** from **6.B** (`doppler configure set … --scope "$HOME"`)

So after **6.B**, a plain `doppler run -- cmd` in an SSH session uses the **stored** project/config until overridden by flags or env. After **6.C** only (no 6.B), an interactive shell does **not** automatically load `/etc/…` — that file is for units you configure with `EnvironmentFile=`. A **systemd**-started service that includes the file **does** pass `DOPPLER_*` into `doppler run`’s environment.

**`unset DOPPLER_TOKEN` after 6.B — why Doppler still works:** Step 3 already ran **`doppler configure set token "$DOPPLER_TOKEN"`**, which **copies** the secret into the CLI’s on-disk store for the scope you set (typically `--scope "$HOME"`). `unset` only removes the **shell copy** so `env` / subprocesses do not keep seeing the raw token in memory; the **`doppler`** binary still loads it from that store when it runs.

**`dev_pilot` vs `dev_ci` with one 6.B setup:** A **[service token](https://docs.doppler.com/docs/service-tokens)** is scoped to **one** config. Whatever token you pasted in 6.B only authorizes **that** config (e.g. **`dev_pilot`**). The line **`doppler configure set config dev_pilot`** must **match** the config that token was minted for — it is your **single default** for interactive CLI. You are **not** switching between two configs with one token; to use **`dev_ci`** interactively you need the **CI** service token and either run **`doppler configure set config dev_ci`** (and update the stored token to match) or pass **`-c dev_ci`** together with a token that is allowed to read `dev_ci` (usually the CI service token via env). The two **`EnvironmentFile`** files in **6.C** are for **two different systemd units** (each unit points at one file), not for teaching the same login shell two defaults at once.

**Pattern (canonical)**

```bash
cd /path/to/workspace   # optional; Doppler uses configured project/config if set
doppler run -- bash -lc 'your-command-here'
```

Examples:

```bash
doppler run -- bash -lc 'ralph doctor -c ~/ralph-smoke/ralph.yml'
doppler run -- bash -lc 'python3.12 -m pytest -q'
```

Any subprocess started **under** that `doppler run` inherits the injected environment until it exits.

**Non-interactive / scripts**

Set `DOPPLER_PROJECT` and `DOPPLER_CONFIG` in the same `EnvironmentFile` as `DOPPLER_TOKEN`, or pass via the process manager, so scripts do not need an interactive `doppler setup`.

---

## 8. Verify injection without printing secret values

Use **presence** checks, not `echo`:

```bash
doppler run -- bash -lc '
  for v in ANTHROPIC_API_KEY OPENAI_API_KEY GEMINI_API_KEY OPENCODE_API_KEY; do
    val=$(printenv "$v" 2>/dev/null || true)
    if [ -n "$val" ]; then echo "$v=set"; else echo "$v=missing"; fi
  done
'
```

Adjust the variable list to match what you stored in Doppler for your VPS config (e.g. `dev_pilot`).

### 8.1 “Missing” env but the secret exists in `dev_pilot`

**Confirm the CLI’s default** (project, config, token source — no secret values):

```bash
doppler configure debug
```

Look for **`config`** = `dev_pilot` (or whatever you expect) and **`project`** = `night-coder-pilot`.

**List secret *names* Doppler will inject** for that resolution (no values printed):

```bash
doppler secrets --only-names
```

If **`GEMINI_API_KEY`** does not appear in that list, the name in the dashboard does not match (e.g. `GEMINI_KEY`, typo, or different casing), or you are not on the config you think you are. Doppler maps **secret name → same env var name** by default.

**Force `dev_pilot` for one run** (bypasses wrong saved default; still needs a token scoped to `dev_pilot`):

```bash
doppler run -p night-coder-pilot -c dev_pilot -- bash -lc '
  val=$(printenv GEMINI_API_KEY 2>/dev/null || true)
  if [ -n "$val" ]; then echo GEMINI_API_KEY=set; else echo GEMINI_API_KEY=missing; fi
'
```

If this shows **set** but the plain `doppler run` loop still shows **missing**, your saved default config is not `dev_pilot` — run **`doppler configure set config dev_pilot --scope "$HOME"`** (and ensure the persisted service token was minted for `dev_pilot`).

**Empty value:** if the secret exists but its value is blank, `printenv` is set but `[ -n "$val" ]` fails — check the value in Doppler (dashboard) or use `doppler run -- bash -lc 'echo -n "${#GEMINI_API_KEY}"'` (prints length only, not the key).

**CLI / auth sanity**

```bash
doppler me
doppler secrets download --no-file --format json --silent >/dev/null && echo "doppler fetch: ok"
```

If fetch fails after a token was revoked, treat prior success as **possibly stale cache** for security decisions — fix auth first, then rerun. The research note in `findings_secrets.md` calls out that revoked tokens may still interact poorly with cached material; **fail closed** (stop the run) when in doubt.

---

## 9. Rotation and updates

### 9.1 Rotating a **provider API key**

1. Add the new value in Doppler (your VPS config, e.g. `dev_pilot`) for the affected secret.  
2. Restart any **long-lived** process that cached the old environment (systemd service, `tmux` session, user shell that exported vars manually).  
3. Remove/disable the old key at the provider when traffic has moved.

### 9.2 Rotating **`DOPPLER_TOKEN`**

1. Create a **new** service token for the same config in the dashboard.  
2. Update the VPS `EnvironmentFile` or `doppler configure set token` (see section 6).  
3. **Revoke** the old token in Doppler.  
4. Run section 8 checks again.

### 9.3 Emergency rollback (Doppler unavailable)

Per `dec-20260407-002` consequences: fall back to **static** environment variables supplied through the same secure channels you would use for break-glass (e.g. operator-managed `EnvironmentFile` with direct `ANTHROPIC_API_KEY=…`), then remove Doppler from that entrypoint until service is restored. Document any break-glass usage in private ops notes.

---

## 10. Agent follow-up (outside this USER runbook)

The following are tracked as **agent** work in `tasks.md` for T059; complete them after this runbook’s USER steps work on the VPS:

- Implement `doppler run` in run scripts where appropriate.  
- Add startup checks for required keys and clear **missing-secret** error messages.  
- Keep rotation steps **here** as the operator-facing source of truth.

---

## 11. T059 completion checklist

**USER (this document)**

- [ ] Doppler **project** exists with two configs for VPS vs CI (e.g. branch slugs **`dev_pilot`** and **`dev_ci`**, or root **`dev`** / **`stg`** — names must match `doppler configs`).  
- [ ] **Secret-scope policy** approved: table in section 2 reflects what you will (and will not) store.  
- [ ] **Service token** created for the **VPS** config with **read-only** access to that config only; token **not** in git.  
- [ ] Doppler **CLI** installed on the VPS; `doppler me` succeeds.  
- [ ] Token configured via **6.A**, **6.B**, or **6.C** (or equivalent approved pattern).  
- [ ] `doppler run --` smoke command succeeds; section 8 shows **set** for every key you require for the next milestone (e.g. first `ralph run`).  
- [ ] Rotation path understood (sections 9.1–9.3).

**Agent / repo (separate tasks)**

- [ ] Run scripts use `doppler run` where secrets are required.  
- [ ] Missing-secret failures are explicit and safe (no silent partial runs).

---

## 12. Hand-off

- **T058:** Ralph CLI — [`vps-ralph-install.md`](./vps-ralph-install.md).  
- **T060:** DTU / WireMock / judge smoke — `vps-dependency-smoke-tests.md` (when added).  
- **T063:** Schedulers should wrap the same `doppler run --` entrypoint you validated here.

---

## References

- [Doppler — Service tokens](https://docs.doppler.com/docs/service-tokens)  
- [Doppler — Install CLI](https://docs.doppler.com/docs/install-cli)  
- [Doppler — Secrets rotation overview](https://docs.doppler.com/docs/secrets-rotation)  
- Prior steps: [`vps-bootstrap.md`](./vps-bootstrap.md), [`vps-container-runtime.md`](./vps-container-runtime.md), [`vps-ralph-install.md`](./vps-ralph-install.md)

---

## Revision

| Date | Notes |
|------|-------|
| 2026-04-12 | Initial T059 runbook: Doppler project/config layout, service tokens, VPS CLI install, injection patterns (`doppler run`, systemd, containers), verification without leaking values, rotation/rollback, completion checklist. |
| 2026-04-12 | Section 3: Doppler **environments** + required `--environment` on `configs create`; config slugs like `dev_pilot`; `doppler configs` verification; optional root `dev`/`stg` alternative. |
| 2026-04-12 | Section 3.1: CLI requires **prefixed** config names (`dev_pilot`, not `pilot` under `--environment dev`); clarify **`Invalid environment id`** vs config slug. |
| 2026-04-12 | Section 6: **6.A / 6.B / 6.C** as alternatives (not sequential); 6.B steps show explicit `export DOPPLER_TOKEN=…` and explain **`configure set token "$DOPPLER_TOKEN"`** as where the token is persisted. |
| 2026-04-12 | Section 6.C: clarify **`EnvironmentFile`** lives **on the VPS** outside the git checkout, not in `night_coder`. |
| 2026-04-12 | Prerequisites: optional note — repo checkout (bootstrap §12) not required for T059 alone; required before T060+. |
| 2026-04-12 | Section 6.C: **`/etc/…` vs relative `etc/…`**, `sudo` + `chown`/`chmod`, two env files in one dir; **`$HOME/.config/…`** option without sudo. |
| 2026-04-12 | Section 6: **6.B + 6.C** complementary (rotation/update both); **chown** vs **chmod 600**; **6.D** conditional; section 7 **config resolution** order. |
| 2026-04-12 | Section 7: **`unset` vs persisted token**; **one service token ↔ one config**; **6.D** practice note (**chown** parent dir, empty compose). |
| 2026-04-12 | Section **8.1**: debug default config (`configure debug`), **`secrets --only-names`**, explicit **`-p`/`-c`**, empty-secret note. |
| 2026-04-12 | Section **6.B.1**: **`configure unset`** + redo; do **not** chain two **6.B** for `dev_ci` then `dev_pilot`. |
