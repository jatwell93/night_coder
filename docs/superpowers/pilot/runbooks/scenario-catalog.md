# Scenario catalog — external read-only boundary (pilot) — T062

Define and protect the **scenario catalog** that the overnight judge consumes. Scenarios are the **immutable source of truth** for "what does success look like?" — the coding agent must never be able to modify them, because the judge reads them to decide whether the agent satisfied the run goal.

**OS:** Ubuntu 24.04 LTS (noble). **Operator user:** `deploy` (sudo-capable).

**Prerequisites**

- [`vps-bootstrap.md`](./vps-bootstrap.md) — VPS provisioned, repo cloned to VPS (`~deploy/night_coder/`).
- [`vps-guardrails-bootstrap.md`](./vps-guardrails-bootstrap.md) — NTM policy active (read-only enforcement via PATH policy is in place).

**Decision references**

- Judge & scenarios decision: `dec-20260406-003` in [`DECISIONS.md`](../DECISIONS.md).
- Artifact registry decision: `dec-20260407-003` — scenarios are not artifacts; they live outside the run output tree.
- T071 (agent follow-up): Implement `src/services/scenario_catalog_service.py` — read-only loader that consumes the path established here.

---

## 1. Goals

| Concern | Goal |
|---------|------|
| **Immutability** | Coding agent cannot edit, create, or delete scenario files during a run. |
| **Judge access** | Judge process can read scenario files without special privilege. |
| **Change control** | Scenario updates require an explicit human operator action (pull request or manual copy). |
| **Pilot simplicity** | No second repo or object store required; in-repo path + OS permissions is sufficient for pilot. |

---

## 2. T062 [USER] decision: where does the catalog live?

Three options are admissible. **Option A** is recommended for the pilot. Record your choice in the table at the end of this runbook.

### Option A — in-repo read-only path (recommended for pilot)

Scenarios live at **`docs/superpowers/pilot/scenarios/`** inside this repo (already referenced in `DECISIONS.md`). The directory is made OS-level read-only for the `deploy` user during autonomous run windows, and write-accessible only for the operator.

**Why:** Zero extra infrastructure. Scenarios travel with the repo. The operator commits changes via normal pull-request flow. Read-only enforcement is a two-command chmod or bind mount.

**Trade-off:** Any process running as `deploy` can modify files outside the run window (when permissions are restored). Sufficient for pilot; revisit for multi-agent production.

### Option B — separate git repo, read-only clone on VPS

Scenarios live in a separate repository (e.g. `night_coder_scenarios`). The VPS has a read-only clone at `/opt/scenarios/` (separate OS user, no `deploy` write access). The `night_coder` repo references the catalog path via env variable `SCENARIO_CATALOG_PATH`.

**Why:** Cleanest boundary — even with full `deploy` shell access, scenario repo origin is independent. Best for multi-agent or production.

**Trade-off:** Extra repo to manage; requires a deploy key or PAT with read-only scope.

### Option C — in-repo path, bind-mounted read-only into agent container

If the coding agent runs inside a container (sandbox profile from `dec-20260407-001`), the scenario directory is bind-mounted read-only into the container: `--mount type=bind,src=$(pwd)/docs/superpowers/pilot/scenarios,dst=/scenarios,readonly`. The host directory remains writable for the operator.

**Why:** Strongest guarantee during an active run; enforcement is in the container spec, not OS chmod.

**Trade-off:** Requires container sandbox to be active (T063 and sandbox profile). Deferred to US2/US3 wiring.

---

## 3. Catalog directory structure

Create the directory and first scenario file. This applies regardless of which Option you chose above.

```bash
mkdir -p ~/night_coder/docs/superpowers/pilot/scenarios
```

### 3.1 Scenario file naming convention

```
SCN-<PROJECT>-<NNNNN>-<slug>.md
```

Examples:
- `SCN-PILOT-001-upstream-ok.md`
- `SCN-PILOT-002-db-migration-safe.md`

Each file is standalone markdown. The judge reads it directly as the `{scenario}` template input.

### 3.2 Scenario file schema

Every scenario file must contain these sections (in order):

```markdown
# <ID>: <Title>

## Goal
One sentence: what the agent must achieve.

## Given
Starting state — files, environment, DTU stubs active.

## When
The action the agent takes (or is expected to take).

## Then
Observable outcomes that constitute **satisfaction**:
- [ ] Outcome 1 (verifiable, deterministic where possible)
- [ ] Outcome 2

## Grading notes
Guidance for the judge (LLMGrader template hints, FunctionGrader checks).

## Out of scope
What the agent is explicitly NOT expected to do in this scenario.
```

### 3.3 Seed scenario: SCN-PILOT-001

```bash
cat > ~/night_coder/docs/superpowers/pilot/scenarios/SCN-PILOT-001-upstream-ok.md << 'EOF'
# SCN-PILOT-001: Upstream dependency returns ok

## Goal
The agent calls the upstream dependency and correctly handles a healthy response.

## Given
- WireMock stub is active: `GET /api/status` → `200 {"status":"ok"}`
- `UPSTREAM_URL` environment variable points to the WireMock container base URL.
- No authentication required.

## When
The agent executes the task that calls `GET ${UPSTREAM_URL}/api/status`.

## Then
- [ ] HTTP response status is 200.
- [ ] Response body contains `{"status": "ok"}` (or equivalent JSON key).
- [ ] Agent stdout or structured output includes the word `SATISFIED`.
- [ ] No error or exception is logged.

## Grading notes
- Use `FunctionGrader` to check stdout for `SATISFIED`.
- Use `LLMGrader` to confirm the agent correctly interpreted the upstream response.
- Trajectory check: no retry loop should appear (single successful call expected).

## Out of scope
- Upstream failure or timeout paths (see SCN-PILOT-002+).
- Authentication flows.
EOF
```

Verify:

```bash
cat ~/night_coder/docs/superpowers/pilot/scenarios/SCN-PILOT-001-upstream-ok.md
```

---

## 4. Read-only boundary (Option A — in-repo path)

Follow this section for **Option A**. For Option B or C, skip to §5 and adjust paths accordingly.

### 4.1 Understand the two modes

| Mode | Who can write | When |
|------|--------------|------|
| **Operator mode** | `deploy` (normal) | Outside run window — editing/reviewing scenarios |
| **Run mode** | No one (read-only chmod) | During an autonomous overnight run |

### 4.2 Lock the catalog before a run

```bash
chmod -R a-w ~/night_coder/docs/superpowers/pilot/scenarios/
```

Verify it is now read-only:

```bash
ls -la ~/night_coder/docs/superpowers/pilot/scenarios/
```

**Expected:** All files show no write bits (e.g. `-r--r--r--`).

Smoke test — confirm a write attempt is rejected:

```bash
echo "test" >> ~/night_coder/docs/superpowers/pilot/scenarios/SCN-PILOT-001-upstream-ok.md && echo "FAIL: write succeeded" || echo "OK: write blocked"
```

**Expected:** `OK: write blocked`

### 4.3 Restore for operator editing

After the run window ends and you need to update scenarios:

```bash
chmod -R u+w ~/night_coder/docs/superpowers/pilot/scenarios/
```

### 4.4 NTM policy layer (defense-in-depth)

The NTM policy at `~/.ntm/policy.yaml` can add a pattern-level block as a second layer against accidental writes to the scenario path. Add to the `blocked` section:

```yaml
  # --- Scenario catalog: agent must not modify scenarios ---
  - pattern: "scenarios/"
    reason: "Scenario catalog is read-only — changes require operator action outside run window"
```

Validate after editing:

```bash
ntm policy validate
```

---

## 5. Change-control policy (USER approval required)

The operator must agree to a minimal change-control process before the first pilot run. Choose a policy that fits your workflow:

### Option 1 — PR-only (recommended)

All scenario changes go through a pull request in this repo. No direct push to `main` for files under `docs/superpowers/pilot/scenarios/`. Review includes: does the new/changed scenario still satisfy the judge-grading notes? Does the DTU stub need a corresponding update?

### Option 2 — Operator-only write window

Scenarios are only edited when the filesystem is explicitly unlocked (§4.3). Changes are committed immediately and pushed before the next run window opens.

### Option 3 — Separate repo with PR (for Option B)

All scenario changes go through a PR in the dedicated scenarios repo. The VPS clone is updated by the operator (`git -C /opt/scenarios pull`) before the next run window.

**Record your choice in the revision table at the end of this runbook.**

---

## 6. Environment variable

The scenario catalog path must be injectable via environment variable so the code does not hard-code a path. Set this in the Doppler `night_coder` project (or `.env` for local dev):

```
SCENARIO_CATALOG_PATH=/home/deploy/night_coder/docs/superpowers/pilot/scenarios
```

Verify (operator shell):

```bash
export SCENARIO_CATALOG_PATH=/home/deploy/night_coder/docs/superpowers/pilot/scenarios
echo "${SCENARIO_CATALOG_PATH:-not set}"
ls "${SCENARIO_CATALOG_PATH}"
```

**Expected:** The directory lists `SCN-PILOT-001-upstream-ok.md`.

---

## 7. Catalog loader contract (agent follow-up: T071)

This section documents the interface that `src/services/scenario_catalog_service.py` (T071) must honour. The operator does not need to implement this now — it is here so the requirement is captured alongside the path decision.

### 7.1 Expected behaviour

- Opens every `.md` file under `SCENARIO_CATALOG_PATH` as read-only (`open(..., "r")`).
- Never writes, creates, renames, or deletes files in that directory.
- Raises `PermissionError` (or equivalent) immediately if it detects write access to the catalog path.
- Returns a `dict[str, str]` mapping scenario ID → file contents.

### 7.2 Immutability boundary check

The loader must assert read-only status at startup:

```python
import os, stat

catalog_path = os.environ["SCENARIO_CATALOG_PATH"]
st = os.stat(catalog_path)
if st.st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH):
    raise RuntimeError(
        f"Scenario catalog at {catalog_path!r} has write bits set. "
        "Lock the catalog before starting a run: chmod -R a-w <path>"
    )
```

This check provides the integration-test surface for T026 (`test_judge_immutability_boundary.py`).

---

## 8. Validation checklist

Run through these steps before marking T062 complete.

### 8.1 Directory and seed file

```bash
ls ~/night_coder/docs/superpowers/pilot/scenarios/
```

**Expected:** `SCN-PILOT-001-upstream-ok.md` present.

### 8.2 Read-only lock and write rejection

```bash
chmod -R a-w ~/night_coder/docs/superpowers/pilot/scenarios/
echo "test" >> ~/night_coder/docs/superpowers/pilot/scenarios/SCN-PILOT-001-upstream-ok.md \
  && echo "FAIL" || echo "OK: write blocked"
```

**Expected:** `OK: write blocked`

### 8.3 Judge can read

```bash
cat ~/night_coder/docs/superpowers/pilot/scenarios/SCN-PILOT-001-upstream-ok.md | head -5
```

**Expected:** First lines of the scenario print without error.

### 8.4 Env variable

```bash
ls "${SCENARIO_CATALOG_PATH}"
```

**Expected:** Scenario file listed.

### 8.5 NTM policy validates (if §4.4 applied)

```bash
ntm policy validate
```

**Expected:** no errors.

### 8.6 Restore write access for operator

```bash
chmod -R u+w ~/night_coder/docs/superpowers/pilot/scenarios/
```

**Expected:** operator can edit scenarios again between run windows.

---

## 9. T062 completion checklist

- [ ] Catalog option chosen (A / B / C) and recorded in revision table below.
- [ ] `docs/superpowers/pilot/scenarios/` directory created on VPS.
- [ ] `SCN-PILOT-001-upstream-ok.md` committed to repo and present on VPS.
- [ ] Scenario file follows required schema (Goal / Given / When / Then / Grading notes).
- [ ] `chmod -R a-w` lock tested; write attempt rejected.
- [ ] `SCENARIO_CATALOG_PATH` env variable set in Doppler (or `.env`) and readable.
- [ ] NTM policy updated with scenario-path block pattern (defense-in-depth) and validated.
- [ ] Change-control policy chosen (PR-only / operator-only / separate-repo PR) and recorded.
- [ ] §7 loader contract reviewed and accepted as the T071 interface spec.

---

## 10. References

- Judge decision: `dec-20260406-003` in [`../DECISIONS.md`](../DECISIONS.md)
- Judge implementation brief: [`../judge/IMPLEMENTATION-BRIEF.md`](../judge/IMPLEMENTATION-BRIEF.md)
- DTU decision (WireMock stub for SCN-PILOT-001): `dec-20260406-002` in [`../DECISIONS.md`](../DECISIONS.md)
- Artifact registry (where run outputs go, separate from scenarios): [`../artifact-registry/IMPLEMENTATION-BRIEF.md`](../artifact-registry/IMPLEMENTATION-BRIEF.md)
- T071: `src/services/scenario_catalog_service.py` — read-only catalog loader (Phase 5 / US3)
- T026: `tests/integration/test_judge_immutability_boundary.py` — integration test for boundary
- Prior: [`vps-guardrails-bootstrap.md`](./vps-guardrails-bootstrap.md) (T061)
- Next: [`vps-scheduler.md`](./vps-scheduler.md) (T063)

---

## Revision

| Date | Option chosen | Change-control policy | Notes |
|------|-------------|----------------------|-------|
| | | | |
