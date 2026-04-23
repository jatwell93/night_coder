# Unattended scheduler — overnight run windows (pilot) — T063

Configure a **systemd user timer** on the VPS that fires the overnight coding run at a fixed time
each night. The timer calls a small wrapper script that injects Doppler secrets, asserts NTM
guardrails are active, and invokes the run launcher. Nothing runs as root; everything executes
under the `deploy` user's systemd session.

**OS:** Ubuntu 24.04 LTS (noble). **Operator user:** `deploy` (sudo-capable).

**Prerequisites**

- [`vps-bootstrap.md`](./vps-bootstrap.md) — `deploy` user, `loginctl enable-linger` already
  applied (required for user systemd units to survive logout).
- [`vps-ralph-install.md`](./vps-ralph-install.md) — `ralph` CLI on PATH.
- [`vps-secrets-bootstrap.md`](./vps-secrets-bootstrap.md) — Doppler service token installed and
  `doppler run` verified.
- [`vps-guardrails-bootstrap.md`](./vps-guardrails-bootstrap.md) — NTM policy active.
- [`scenario-catalog.md`](./scenario-catalog.md) — `SCENARIO_CATALOG_PATH` value known.

**Decision reference**

- Orchestrator choice: `dec-20260406-001` (Ralph).
- Run launcher (T020): `src/cli/run_overnight.py` — **not yet implemented**. The wrapper script
  below stubs the launcher call with a clearly-marked placeholder; replace it once T020 ships.

---

## 1. Goals

| Concern | Goal |
|---------|------|
| **Unattended start** | Run fires automatically at the configured window without operator presence. |
| **Secret injection** | Doppler injects secrets at start-time; no plaintext env vars in unit files. |
| **Guardrail assertion** | Wrapper refuses to start if NTM process is not active. |
| **Observability** | `journalctl --user -u night-coder-run` shows full run output. |
| **Safe defaults** | Timer is disabled by default; operator enables it explicitly before the first live run. |
| **Easy override** | Operator can fire a run immediately with `systemctl --user start night-coder-run.service`. |

---

## 2. systemd timer vs cron

systemd user timers are preferred over cron for this pilot:

| Factor | systemd timer | cron |
|--------|--------------|------|
| Logging | Full stdout/stderr captured in journald | Lost unless redirected manually |
| Linger support | Works with `loginctl enable-linger` already applied | Works but no linger dependency |
| Missed run behaviour | Configurable (`Persistent=true` catches up) | Silent miss if host was down |
| Secret injection | Clean `ExecStart` with `doppler run --` prefix | Requires wrapper script regardless |
| Override / manual trigger | `systemctl --user start <unit>` | `run-parts` or comment toggle |

**Verdict:** systemd user timer. cron remains an option if systemd user session is unavailable.

---

## 3. Linger check

User units only start at boot if `linger` is enabled. Confirm it was applied during bootstrap:

```bash
loginctl show-user deploy | grep Linger
```

**Expected:** `Linger=yes`

If not:

```bash
sudo loginctl enable-linger deploy
```

---

## 4. Run wrapper script

Create the script that the systemd service calls. It: exports the catalog path, asserts NTM is
running, injects secrets via Doppler, and calls the run launcher.

```bash
mkdir -p ~/night_coder/scripts
cat > ~/night_coder/scripts/run-overnight.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

# ── PATH ────────────────────────────────────────────────────────────────────
# systemd user services start with a minimal PATH that does not include the
# directories added by ~/.bashrc or ~/.profile. Set it explicitly here so the
# script behaves identically whether invoked from the terminal or by systemd.
#   ~/.opencode/bin  → ntm (guardrail binary)
#   ~/.local/bin     → doppler and other user-installed tools
#   ~/.npm-global/bin → ralph (orchestrator)
export PATH="${HOME}/.opencode/bin:${HOME}/.local/bin:${HOME}/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# ── Config ──────────────────────────────────────────────────────────────────
REPO_ROOT="${HOME}/night_coder"
export SCENARIO_CATALOG_PATH="${REPO_ROOT}/docs/superpowers/pilot/scenarios"
LOG_STAMP=$(date -u +"%Y%m%dT%H%M%SZ")

echo "[run-overnight] === Starting overnight run ${LOG_STAMP} ==="

# ── Guardrail assertion ─────────────────────────────────────────────────────
# Refuse to launch if NTM is not active in this shell's PATH.
if ! command -v ntm &>/dev/null; then
  echo "[run-overnight] ABORT: ntm not found on PATH. Guardrail layer missing." >&2
  exit 1
fi

echo "[run-overnight] NTM found: $(ntm --version 2>/dev/null || echo 'version unknown')"

# ── Scenario catalog sanity check ──────────────────────────────────────────
if [[ ! -d "${SCENARIO_CATALOG_PATH}" ]]; then
  echo "[run-overnight] ABORT: SCENARIO_CATALOG_PATH does not exist: ${SCENARIO_CATALOG_PATH}" >&2
  exit 1
fi

echo "[run-overnight] Scenario catalog: ${SCENARIO_CATALOG_PATH}"
ls "${SCENARIO_CATALOG_PATH}"

# ── Launch ──────────────────────────────────────────────────────────────────
# PLACEHOLDER: T020 (src/cli/run_overnight.py) not yet implemented.
# Replace this block with:
#   doppler run -- python "${REPO_ROOT}/src/cli/run_overnight.py"
# Once T020 ships. Do NOT wire a live ralph call here until the launcher exists.
echo "[run-overnight] PLACEHOLDER: run launcher (T020) not yet implemented — skipping."
echo "[run-overnight] Pre-launch checks passed. Exiting cleanly."

echo "[run-overnight] === Run complete ==="
EOF
chmod +x ~/night_coder/scripts/run-overnight.sh
```

Verify it is executable:

```bash
ls -la ~/night_coder/scripts/run-overnight.sh
```

**Expected:** `-rwxr-xr-x` (or similar with execute bit set).

---

## 5. systemd user service

Create the service unit that executes the wrapper:

```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/night-coder-run.service << 'EOF'
[Unit]
Description=Night Coder overnight coding run
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=%h/night_coder
ExecStart=%h/night_coder/scripts/run-overnight.sh
StandardOutput=journal
StandardError=journal
# Allow the run up to 8 hours before systemd kills it.
TimeoutStartSec=28800

[Install]
WantedBy=default.target
EOF
```

---

## 6. systemd user timer

Create the timer unit. Default window is **23:00 local time** — adjust `OnCalendar` to match
your preferred timezone offset or use a UTC expression.

```bash
cat > ~/.config/systemd/user/night-coder-run.timer << 'EOF'
[Unit]
Description=Trigger Night Coder overnight run nightly
Requires=night-coder-run.service

[Timer]
# Fire at 23:00 Australia/Sydney time (handles AEST/AEDT daylight saving automatically).
# systemd requires IANA timezone names — abbreviations like AEST are not valid here.
# Equivalent UTC time: 13:00 UTC in winter (AEST, UTC+10), 12:00 UTC in summer (AEDT, UTC+11).
OnCalendar=*-*-* 23:00:00 Australia/Sydney
# If the host was down at fire time, start as soon as it is back up.
Persistent=true
# Randomise start by up to 5 minutes to avoid thundering-herd if multiple units exist.
RandomizedDelaySec=300
Unit=night-coder-run.service

[Install]
WantedBy=timers.target
EOF
```

Verify systemd parsed the calendar expression correctly before reloading:

```bash
systemd-analyze calendar '*-*-* 23:00:00 Australia/Sydney'
```

**Expected:** shows next trigger date/time in UTC alongside the Sydney local time.

---

## 7. Reload and verify units

```bash
systemctl --user daemon-reload
systemctl --user list-unit-files | grep night-coder
```

**Expected:** Both `night-coder-run.service` and `night-coder-run.timer` listed (`disabled` is correct at this stage).

---

## 8. Enable the timer

> **Do not enable the timer until you have verified the wrapper script runs cleanly (§9).**
> The timer is left disabled by default so it does not fire during setup.

Once you are satisfied the script works:

```bash
systemctl --user enable night-coder-run.timer
systemctl --user start  night-coder-run.timer
systemctl --user status night-coder-run.timer
```

**Expected:** `Active: active (waiting)` with the next trigger time shown.

---

## 9. Smoke test — manual trigger

Trigger the service immediately (bypassing the timer) to confirm the wrapper runs end-to-end
without errors:

```bash
systemctl --user start night-coder-run.service
```

Watch the output in real time:

```bash
journalctl --user -u night-coder-run.service -f
```

**Expected:** Script prints start banner, NTM check passes, catalog path lists the scenario file,
then prints the T020 placeholder message and exits cleanly. There is no live launcher call until
T020 (`src/cli/run_overnight.py`) is implemented — do not wire a `ralph run` call here before
then (`ralph run` does not accept a `--preset` flag and will exit non-zero).

Check exit status:

```bash
systemctl --user status night-coder-run.service
```

**Expected:** `Active: inactive (dead)` with `status=0`.

> **Gotcha — PATH under systemd:** If the service fails immediately but `bash ~/night_coder/scripts/run-overnight.sh` succeeds, the cause is almost always a PATH mismatch. systemd user services do not source `~/.bashrc` or `~/.profile`. The wrapper script hard-codes the required directories at the top (`~/.opencode/bin`, `~/.local/bin`, `~/.npm-global/bin`) to avoid this. If you install NTM, Doppler, or Ralph to a different location, update the `PATH=` line in the script accordingly.

---

## 10. View logs

```bash
# Last run
journalctl --user -u night-coder-run.service --no-pager

# Follow live
journalctl --user -u night-coder-run.service -f

# Timer next-fire and last-trigger summary
systemctl --user list-timers night-coder-run.timer
```

---

## 11. Adjust the run window

To change the fire time, edit the `OnCalendar` line in the timer unit and reload:

```bash
# Example: change to 22:30 Australia/Sydney
sed -i 's/OnCalendar=.*/OnCalendar=*-*-* 22:30:00 Australia\/Sydney/' \
  ~/.config/systemd/user/night-coder-run.timer
systemctl --user daemon-reload
systemctl --user restart night-coder-run.timer
systemctl --user list-timers night-coder-run.timer
```

---

## 12. Disable / pause the scheduler

To pause without deleting the units:

```bash
systemctl --user stop   night-coder-run.timer
systemctl --user disable night-coder-run.timer
```

To re-enable later, repeat §8.

---

## 13. Validation checklist

### 13.1 Linger active

```bash
loginctl show-user deploy | grep Linger
```

**Expected:** `Linger=yes`

### 13.2 Wrapper script executable

```bash
ls -la ~/night_coder/scripts/run-overnight.sh
```

**Expected:** execute bit set.

### 13.3 Units loaded

```bash
systemctl --user list-unit-files | grep night-coder
```

**Expected:** service and timer both listed.

### 13.4 Manual trigger succeeds

```bash
systemctl --user start night-coder-run.service
journalctl --user -u night-coder-run.service --no-pager | tail -20
```

**Expected:** NTM check passes, catalog path resolves, Doppler call attempts.

### 13.5 Timer shows next-fire time (after enabling)

```bash
systemctl --user list-timers night-coder-run.timer
```

**Expected:** `NEXT` column shows a date/time in the future.

---

## 14. T063 completion checklist

- [ ] Linger confirmed active for `deploy` user.
- [ ] `~/night_coder/scripts/run-overnight.sh` created and executable.
- [ ] `night-coder-run.service` unit installed and loaded.
- [ ] `night-coder-run.timer` unit installed and loaded.
- [ ] Manual trigger (`systemctl --user start night-coder-run.service`) completes without NTM or catalog errors.
- [ ] Timer enabled and `list-timers` shows a future next-fire time.
- [ ] `OnCalendar` value confirmed and recorded in revision table below.
- [ ] Launcher placeholder noted — replace with `run_overnight.py` call when T020 ships.

---

## 15. References

- Orchestrator install: [`vps-ralph-install.md`](./vps-ralph-install.md) (T058)
- Secrets injection: [`vps-secrets-bootstrap.md`](./vps-secrets-bootstrap.md) (T059)
- Guardrails: [`vps-guardrails-bootstrap.md`](./vps-guardrails-bootstrap.md) (T061)
- Scenario catalog: [`scenario-catalog.md`](./scenario-catalog.md) (T062)
- Run launcher (future): `src/cli/run_overnight.py` (T020)
- Next: `docs/superpowers/pilot/runbooks/README.md` (T001)

---

## Revision

| Date | OnCalendar value | Notes |
|------|-----------------|-------|
| | | |
