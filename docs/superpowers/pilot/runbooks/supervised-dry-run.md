# Supervised Dry Run Checklist (T094)

Checklist for a human-supervised run before enabling live unattended schedule.

**Paths** assume repo root `~/night_coder` and operator user `deploy` (adjust if yours differ).

---

## VPS command order (run top to bottom)

Use this exact sequence on VPS; each step assumes the previous one already passed.

1. Doppler env verification
2. Repo + venv baseline
3. Policy + NTM checks
4. DTU assets + WireMock startup
5. Real HTTP proof against WireMock
6. Local state/traces prep
7. Lock scenario catalog for run window
8. Launch `run_overnight` checks
9. Capture results and post-run decision

---

## Preflight (in execution order)

- [ ] **Doppler injects required Night Coder config** (from repo root):

    **If a `doppler run -- … "$(cat <<'PY' …` block hangs with a `>` prompt:** the closing `PY` line was indented. In bash, the heredoc **terminator must start at column 0** (no leading spaces). Copy-paste from Markdown often adds spaces — use the **printenv loop** below instead (no heredoc).

    Do **not** pipe a heredoc into `doppler run -- python3 -` — many Doppler versions do not forward stdin to the child, so `python3 -` hangs.

    ```bash
    cd ~/night_coder
    doppler run -- /bin/sh -c '
    ok=0
    for k in NIGHT_CODER_ARTIFACTS_ROOT NIGHT_CODER_SCENARIO_CATALOG NIGHT_CODER_PROFILE NIGHT_CODER_GUARDRAIL_POLICY NIGHT_CODER_MODEL_POLICY; do
      v=$(printenv "$k")
      if [ -z "$v" ]; then echo "$k=MISSING"; ok=1; else echo "$k=SET"; fi
    done
    if [ "$ok" -ne 0 ]; then echo FAIL; exit 1; fi
    echo OK
    '
    ```

- [ ] **Python venv** (recommended on VPS):

    ```bash
    cd ~/night_coder
    test -x .venv/bin/python || python3 -m venv .venv
    source .venv/bin/activate
    pip install -q -e ".[dev]"
    ```

- [ ] **Guardrail + model policy files exist**:

    ```bash
    test -f ~/night_coder/docs/superpowers/pilot/config/guardrail-policy.yaml
    test -f ~/night_coder/docs/superpowers/pilot/config/model-policy.yaml
    ```

- [ ] **NTM policy validates**:

    ```bash
    ntm policy validate
    ```

- [ ] **DTU mappings/profiles present** for target scenarios (WireMock JSON under repo):

    ```bash
    ls ~/night_coder/docs/superpowers/pilot/dtu/mappings/
    ls ~/night_coder/docs/superpowers/pilot/dtu/profiles/
    ```

- [ ] **WireMock up** (pilot DTU — maps host `3000` → container `8080`):

    **Why `docker compose` *and* `podman compose` can both fail:** if the log says `Executing external compose provider "/usr/bin/docker-compose"`, Podman is **not** running containers itself — it is spawning **Compose v1** (`docker-compose`), which only talks to the **Docker** socket (`/var/run/docker.sock`). On a Podman-only host that socket usually **does not exist** → `FileNotFoundError` / `Error while fetching server API version`. **`compose down` does not fix that**; you need a different invocation (below).

    **Option A — `podman run` (recommended):** no Compose provider, only needs working `podman`:

    ```bash
    cd ~/night_coder/docs/superpowers/pilot/dtu
    podman rm -f wiremock-pilot 2>/dev/null || true
    podman run -d --name wiremock-pilot -p 3000:8080 \
      -v "$PWD/mappings:/home/wiremock/mappings:ro" \
      docker.io/wiremock/wiremock:latest
    ```

    **Option B — `podman-compose`** (hyphen — **different** from `podman compose`): Python helper that drives **Podman**, not Docker’s socket. Install if missing: `sudo apt install -y podman-compose` (`vps-container-runtime.md` §3.5).

    ```bash
    cd ~/night_coder/docs/superpowers/pilot/dtu
    podman-compose -f docker-compose.wiremock.yml up -d
    ```

    **Option C — real Docker Engine** (`dockerd` + `/var/run/docker.sock`): only then use:

    ```bash
    cd ~/night_coder/docs/superpowers/pilot/dtu
    docker compose -f docker-compose.wiremock.yml up -d
    ```

    Smoke the stub (shell check — not passed through `run_overnight`):

    ```bash
    curl -sS "http://127.0.0.1:3000/api/status"
    ```

    Expect JSON like `{"status":"ok"}` when mappings include `pilot-status.json` / happy-path stubs. Admin UI: `http://127.0.0.1:3000/__admin/`.

    **Troubleshooting — “name already in use” / “port 3000 … already in use”:** `podman-compose` names containers like `dtu_wiremock-pilot_1` (project `dtu` + service name). If a first `up` created that container, a second `up` can error until you **`podman rm -f dtu_wiremock-pilot_1`** or **`podman start dtu_wiremock-pilot_1`** when you only need it running again. If you then run **Option A** (`wiremock-pilot` on port 3000), Podman errors with **address already in use** because **the compose container still holds `3000`**. Pick **one** method: either use the existing compose container and smoke-test with `curl`, or **`podman stop` / `podman rm`** all WireMock containers (`podman ps -a | grep -i wiremock`) before starting the other style.

- [ ] **Live HTTP client proof** (`run_overnight` **does not execute** `--command` strings; it only scores them against guardrails). Run this **after** WireMock is healthy so traffic actually hits the mock (one line — avoids bash heredoc terminator pitfalls):

    ```bash
    cd ~/night_coder
    UPSTREAM_URL=http://127.0.0.1:3000 python3 -c "import json,os,urllib.request as u; b=os.environ.get('UPSTREAM_URL','http://127.0.0.1:3000').rstrip('/'); r=u.urlopen(b+'/api/status',timeout=15); d=json.load(r); print('SATISFIED' if d.get('status')=='ok' else 'FAIL')"
    ```

    Expect `SATISFIED` on stdout. (`guardrail-policy.yaml` blocks `curl http://...` inside launcher `--command` text, so use **Python** for the allowlisted probe string if you duplicate this snippet there.)

    **If `curl` shows `{"status":"ok"` without a closing `}` or Python raises `JSONDecodeError`:** WireMock matched **`scn-pilot-003-malformed-json.json`** (intentionally invalid JSON for SCN-003). Mappings use **priority** so happy-path stubs win for default dry runs; after changing mappings, restart the container (`podman restart dtu_wiremock-pilot_1` or your container name). On VPS, `git pull` in `~/night_coder` if priorities were added in repo.

    **If `curl` returns `Connection reset by peer` right after `podman restart`:** WireMock may still be starting or the container exited. Wait a few seconds, then check status and logs before retrying:

    ```bash
    podman ps -a --filter name=wiremock
    podman logs --tail 80 dtu_wiremock-pilot_1
    sleep 5
    curl -sS "http://127.0.0.1:3000/api/status"
    ```

    If `podman ps` shows **Exited**, recreate (from `~/night_coder/docs/superpowers/pilot/dtu`):

    ```bash
    podman-compose -f docker-compose.wiremock.yml down
    podman-compose -f docker-compose.wiremock.yml up -d
    sleep 8
    curl -sS "http://127.0.0.1:3000/api/status"
    ```

- [ ] **Memory sqlite path** (pilot local store):

    ```bash
    mkdir -p ~/night_coder/.state/memory/logs
    python3 -c "import os,sqlite3; h=os.path.expanduser('~'); db=os.path.join(h,'night_coder','.state','memory','memory.sqlite3'); c=sqlite3.connect(db); c.execute('CREATE TABLE IF NOT EXISTS healthcheck (id INTEGER PRIMARY KEY, ts TEXT)'); c.commit(); print('memory OK')"
    ```

- [ ] **OTEL / traces directory** writable (Phase 1 file export):

    ```bash
    mkdir -p ~/night_coder/artifacts/traces
    test -w ~/night_coder/artifacts/traces
    ```

- [ ] **Budget / fallback** reviewed (`budget-policy.md`).

- [ ] **Scenario catalog locked read-only** for the run window (run this immediately before launch; must target catalog directory only):

    ```bash
    chmod -R a-w ~/night_coder/docs/superpowers/pilot/scenarios
    ls -la ~/night_coder/docs/superpowers/pilot/scenarios
    ```

    Do **not** run `chmod -R a-w` without a path — that can lock the whole tree.

---

## Launch

- [ ] **Supervised terminal** attached (tmux/SSH session you can watch).

- [ ] **Minimal launcher** (guardrail **evaluation** only — commands are not run; default probe is allowed `python -m pytest -q`):

    ```bash
    cd ~/night_coder
    source .venv/bin/activate
    doppler run -- python -m cli.run_overnight --json
    ```

- [ ] **WireMock-aware guardrail check** (blocked + allowed + upstream-shaped **Python** command text). Run after WireMock smoke and **Live HTTP client proof**.

    Under **`offline`** profile, the command string must **not** contain `http://` or `https://` literals — `run_profile_service` treats those as network egress. Pass the base URL **only** via `UPSTREAM_URL` and read it with `os.environ['UPSTREAM_URL']` in the probe:

    ```bash
    cd ~/night_coder
    source .venv/bin/activate
    UPSTREAM_URL=http://127.0.0.1:3000 doppler run -- python -m cli.run_overnight --json \
      --command "sudo true" \
      --command "python -c \"import json,os,urllib.request;b=os.environ['UPSTREAM_URL'].rstrip('/');r=urllib.request.urlopen(b+'/api/status',timeout=15);d=json.load(r);print('SATISFIED' if d.get('status')=='ok' else 'FAIL')\"" \
      --command "python -m pytest -q"
    ```

    Expect `blocked_count >= 1`, `allowed_count >= 2`, and `blocked_events` only for `sudo`. The middle `--command` must stay one shell token (single-line `python -c "..."`).

    Alternative: `--profile online` if you intentionally allow network-shaped command text in the summary (still does not execute commands).

- [ ] **Stronger guardrail check** (no DTU) — same as before if you skip WireMock:

    ```bash
    cd ~/night_coder
    source .venv/bin/activate
    doppler run -- python -m cli.run_overnight --json \
      --command "sudo true" \
      --command "python -m pytest -q"
    ```

    Expect `blocked_count >= 1` and non-empty `blocked_events` for the denied command.

- [ ] **Optional — Ralph** (orchestrator smoke; requires files in **repo root** `~/night_coder`):

    `run_overnight --execute-ralph` runs `ralph` with **working directory** = parent of `NIGHT_CODER_ARTIFACTS_ROOT` (usually `~/night_coder`). It expects **`~/night_coder/ralph.yml`** and **`~/night_coder/PROMPT.md`**. Logs like `Config file "ralph.yml" not found` or `Prompt file 'PROMPT.md' not found` mean those files are missing in that directory.

    **One-time bootstrap** (pick the backend you installed per `vps-ralph-install.md` — `opencode`, `gemini`, or `claude`):

    ```bash
    cd ~/night_coder
    ralph init --backend opencode
    cp docs/superpowers/pilot/templates/PROMPT.smoke.md PROMPT.md
    doppler run -- ralph doctor -c ralph.yml
    doppler run -- ralph run -c ralph.yml -P PROMPT.md --max-iterations 3 -q
    ```

    When manual `ralph run` succeeds, wire through the launcher:

    ```bash
    cd ~/night_coder
    source .venv/bin/activate
    doppler run -- python -m cli.run_overnight --json --execute-ralph
    ```

    Templates (no secrets): `docs/superpowers/pilot/templates/ralph.yml.example`, `PROMPT.smoke.md`. Do **not** commit API keys in `ralph.yml`; use Doppler for env.

- [ ] **Capture** `run_id` and start timestamp from JSON output.


- [ ] **Note:** `run_overnight` returns a JSON summary of guardrail decisions; it does **not** run the shell commands in `--command`, and it does **not** write `manifest.json` / verdict files unless you run separate finalize/judge pipelines (see `us3-dtu-memory-loop.md`). Empty `artifacts/` after `--json` only is expected for the minimal path.

---

## In-flight checks

- [ ] At least one **allowed** command path (e.g. default pytest or explicit allowlisted command).
- [ ] At least one **blocked** command with reason code (use `--command` probes as above).
- [ ] If DTU is in scope: responses match selected WireMock profile.
- [ ] Telemetry / logs: confirm events or OTEL sink as wired for your environment.

---

## Completion checks

- [ ] JSON summary shows expected `status`, `blocked_count`, `allowed_count`.
- [ ] If you ran judge/manifest steps separately: verdict artifact(s) and schema-valid manifest (see `trial-e2e.md` / `us3-dtu-memory-loop.md`).
- [ ] Morning review notes captured (`morning-review-template.md`).

---

## Post-run decision

- [ ] Findings written to `dry-run-results.md`.
- [ ] Risks triaged using `troubleshooting.md`.
- [ ] Recommendation ready for T096 go/no-go.

---

## Optional: enable unattended timer (only after go/no-go)

Do **not** conflate this with catalog locking. Scheduler setup lives in `vps-scheduler.md`. Example:

```bash
systemctl --user enable night-coder-run.timer
systemctl --user start  night-coder-run.timer
systemctl --user status night-coder-run.timer
```
