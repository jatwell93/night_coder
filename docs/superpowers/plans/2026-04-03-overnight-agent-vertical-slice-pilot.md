# Overnight Agent Vertical Slice Pilot — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lock non‑negotiables and constraints; use **Quint** to choose winners across **all** tool rows in `[Research/Research_Summary_Table.md](../../Research/Research_Summary_Table.md)` (by pillar); then run one minimal StrongDM-style **vertical slice** (one repo, one external scenario, one judge path, one DTU stub, one orchestrator spine) for a **time-boxed weekend overnight pilot** with a defined morning review.

**Architecture:** Treat the pilot as a **closed loop**: an **external** scenario file (agent must not edit it) defines success; a **WireMock** container stubs one HTTP dependency (Quint `dec-20260406-002`); a **tiny sandbox app** in-repo is the only code the coding agent may change; after the run, a **Python judge** scores a bundled **trace artifact** (JSONL or log file) against the scenario.

**Stack selection rule (Quint winner, full research table):** Before locking `DECISIONS.md`, run the comparison workflow in `[qunit_code_workflows](../../../qunit_code_workflows)` (deep path: `/q-frame` → `/q-char` → `/q-explore` → `/q-compar` → `/q-decide` → `/q-apply`). **Every candidate below** comes from `[Research/Research_Summary_Table.md](../../Research/Research_Summary_Table.md)` §1 *Master index*; Quint must compare **fairly across pillars** (same pilot goals, same evaluation budget per variant), not pick an orchestrator in isolation.

**Candidates to consider (by pillar)**


| Pillar                            | Topics to compare (all rows in the summary table for that pillar)                                                                                                                                                                                                                             |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Reference (principles)**        | StrongDM Software Factory (use as *target architecture* / rubric, not a drop-in OSS substitute)                                                                                                                                                                                               |
| **Orchestration (Attractor)**     | OpenHands, AG2 (AutoGen), Deer Flow, CrewAI, AgentFlow *(research / Flow-GRPO line — not vendor “agent flow” UIs)*, Gas Town, oh-my-openagent *(rename of oh-my-opencode)*, Ralph orchestrator, Ruflo (claude-flow), Agent Flywheel (ACFS)                                                    |
| **Guardrails / sessions (Leash)** | NTM; also note orchestrator-native limits (Ralph, Ruflo sandbox modes, oh-my-openagent hooks) as *partial* leash                                                                                                                                                                              |
| **DTU / mocks**                   | Mockoon, Keploy, MSW — plus gap-wave extras in research: LocalStack, Browserless / Playwright *(see `[research_overnight_stack_web/gap_wave2/findings_gap_dtu_localstack_browserless.md](../../Research/research_overnight_stack_web/gap_wave2/findings_gap_dtu_localstack_browserless.md)`)* |
| **Judge & scenarios**             | OpenJudge (`py-openjudge`), Dify *(usually rejected as embedded judge — still compare explicitly)*, AgentScope *(eval / judge patterns)*, build-yourself harness *(custom scenario store + LLM judge — no product)*                                                                           |
| **Observability / CXDB**          | Langfuse, OpenLLMetry; Ralph/NTM file or audit trails where applicable                                                                                                                                                                                                                        |
| **Complementary**                 | Aider *(optional worker next to orchestrator)*                                                                                                                                                                                                                                                |


**Exclude from “tool pick”:** `Table.md`, `questions.md` (meta only).

**Quint winners recorded:** **Ralph** (orchestrator, `dec-20260406-001`), **WireMock** (DTU, `dec-20260406-002`), **NTM** (leash), **OpenJudge** (judge). Detached execution uses `tmux` or `systemd`. **Appendix A** documents **Ralph** as the orchestrator; add further appendices when other components need copy-paste runbooks.

**Tech Stack:** Python 3.12+, Docker + Docker Compose, WireMock Docker image (`wiremock/wiremock`), `openai` Python SDK for the pilot judge, Ralph orchestrator, `tmux`, `git`. Reference research: `[Research/Research_Summary_Table.md](../../Research/Research_Summary_Table.md)`, `[Research/research_overnight_stack_web/research_report.md](../../Research/research_overnight_stack_web/research_report.md)`.

---

## File structure (created by this plan)

All paths relative to repository root `/home/ja/night_coder`:


| Path                                                            | Responsibility                                                                                                      |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `docs/superpowers/pilot/CONSTRAINTS.md`                         | Non‑negotiables, budget, risk, data handling — single source of truth for the pilot                                 |
| `docs/superpowers/pilot/DECISIONS.md`                           | Locked stack choices (orchestrator, DTU, judge, leash, observability, models, window) — signed off before execution |
| `docs/superpowers/pilot/scenarios/SCN-PILOT-001-upstream-ok.md` | **External** scenario spec + YAML frontmatter (holdout-style)                                                       |
| `docs/superpowers/pilot/dtu/docker-compose.wiremock.yml`        | WireMock service exposing stub API on port 3000 (Quint `dec-20260406-002`)                                          |
| `docs/superpowers/pilot/dtu/mappings/pilot-status.json`         | WireMock mapping: GET /api/status → `{"status":"ok"}`                                                               |
| `docs/superpowers/pilot/sandbox-app/ping_upstream.py`           | Deliberately incomplete starter — agent completes it                                                                |
| `docs/superpowers/pilot/sandbox-app/README.md`                  | What the agent is allowed to touch                                                                                  |
| `docs/superpowers/pilot/traces/.gitkeep`                        | Directory for post-run trace uploads                                                                                |
| `docs/superpowers/pilot/judge/requirements.txt`                 | Judge dependencies                                                                                                  |
| `docs/superpowers/pilot/judge/pilot_judge.py`                   | LLM judge CLI (scenario + trace → score JSON)                                                                       |
| `docs/superpowers/pilot/fixtures/sample_trace.txt`              | Fixture for judge unit test                                                                                         |
| `docs/superpowers/pilot/runbooks/PILOT-WEEKEND.md`              | Exact commands, start/stop, morning checklist                                                                       |
| `docs/superpowers/pilot/tests/test_pilot_judge_output.py`       | Pytest: judge returns valid JSON schema on fixture                                                                  |


**Interface contract:** `ping_upstream.py` reads `UPSTREAM_URL` (default `http://127.0.0.1:3000`), performs `GET /api/status`, expects JSON body `{"status":"ok"}`, prints exactly `SATISFIED` or `FAIL` to stdout.

---

### Task 1: Create `CONSTRAINTS.md` (non‑negotiables + pilot boundaries)

**Files:**

- Create: `docs/superpowers/pilot/CONSTRAINTS.md`
- Modify: (none)
- **Step 1: Create directory**

Run:

```bash
mkdir -p /home/ja/night_coder/docs/superpowers/pilot
```

- **Step 2: Write `CONSTRAINTS.md`**

Create `docs/superpowers/pilot/CONSTRAINTS.md` with the following content. **Edit the bracketed lines** to match your real budget, provider, and policy before locking `DECISIONS.md`.

```markdown
# Pilot constraints (edit before overnight run)

## Non‑negotiables
1. **External scenarios:** `docs/superpowers/pilot/scenarios/*.md` are read-only for the coding agent; only the human and the judge process may use them as authority.
2. **Headless execution:** No interactive approval during the overnight window; orchestrator runs in fully autonomous mode.
3. **Secret handling:** API keys only via environment variables or the **selected orchestrator’s** documented config path (e.g. `~/.openhands/agent_settings.json` for OpenHands fallback) — never committed.
4. **Network boundary:** The stub upstream runs in Docker; sandbox app uses `UPSTREAM_URL` — no live third-party APIs in the pilot.
5. **Morning review:** Human reads judge JSON + git diff + orchestrator log; no merging without explicit sign-off.

## Budget and time
- **Monthly LLM cap for pilot (AUD):** [50]
- **VPS provider / size:** [Hetzner CX22]
- **Pilot window:** One weekend night, max wall-clock **10 hours** unattended (hard stop via `timeout` or orchestrator max runtime).

## Compliance / data
- **Traces may contain:** [e.g. file paths, code snippets — no customer PII]
- **Judge model data retention:** [e.g. OpenAI API — per vendor policy]

## Rollback
- **Git:** Pilot work on branch `pilot/overnight-slice-001`; discard or merge only after review.
```

- **Step 3: Commit**

```bash
cd /home/ja/night_coder
git add docs/superpowers/pilot/CONSTRAINTS.md
git commit -m "docs(pilot): add CONSTRAINTS for overnight vertical slice"
```

---

### Task 2: Lock decisions in `DECISIONS.md`

**Files:**

- Create: `docs/superpowers/pilot/DECISIONS.md`
- **Step 0: Run Quint across the full research table**

Follow `[qunit_code_workflows](../../../qunit_code_workflows)` **deep architecture** path so each pillar’s alternatives are **characterized** (`/q-char`), **explored** (`/q-explore`), **compared** (`/q-compar`), and **decided** (`/q-decide`) with parity rules and a written decision contract. The candidate lists are fixed by the plan header *Stack selection rule* (sourced from `[Research_Summary_Table.md](../../Research/Research_Summary_Table.md)` §1).

- **Step 1: Create `DECISIONS.md`**

Create `docs/superpowers/pilot/DECISIONS.md`:

```markdown
# Pilot decisions (fill before run)

Source of truth for "Choice" fields: Quint comparison workflow in `[qunit_code_workflows](../../../qunit_code_workflows)`, evaluating **all** candidates listed for each pillar in `[Research/Research_Summary_Table.md](../../Research/Research_Summary_Table.md)` §1 (see plan header *Stack selection rule*). Record the **winner per pillar** and link to `/q-decide` output or `quint-code board` reference.

| Decision | Choice | Rationale (one line) |
|----------|--------|----------------------|
| Reference rubric | StrongDM-style principles (scenarios, DTU, satisfaction) — yes/no and how strict | |
| Orchestration (Attractor) | One of: OpenHands, AG2, Deer Flow, CrewAI, AgentFlow (research), Gas Town, oh-my-openagent, Ralph, Ruflo, Agent Flywheel | Quint winner + weakest-link note |
| Guardrails (Leash) | NTM and/or harness-native limits; or none for pilot | |
| DTU / mocks | Mockoon, Keploy, MSW, and/or LocalStack / Browserless / Playwright per research | |
| Judge & scenarios | OpenJudge, Dify, AgentScope patterns, and/or build-yourself; scenario storage path | |
| Observability (CXDB) | Langfuse, OpenLLMetry, and/or file-based (Ralph/NTM) | |
| Complementary | Aider yes/no | |
| Coding model (LLM for agent) | | |
| Judge model (LLM for judge) | | |
| Host | Laptop OR VPS hostname | |
| Start time (local) | | |
| Hard stop time | | |

**Sign-off:** I accept CONSTRAINTS.md and will not intervene until the stop time: _________________ (initials/date)
```

- **Step 2: Commit**

```bash
git add docs/superpowers/pilot/DECISIONS.md
git commit -m "docs(pilot): add DECISIONS worksheet"
```

---

### Task 3: Author external scenario `SCN-PILOT-001`

**Files:**

- Create: `docs/superpowers/pilot/scenarios/SCN-PILOT-001-upstream-ok.md`
- **Step 1: Write scenario file**

Create `docs/superpowers/pilot/scenarios/SCN-PILOT-001-upstream-ok.md`:

```markdown
---
id: SCN-PILOT-001
name: Upstream status OK
tags: [pilot, http, dtu]
prerequisites:
  - WireMock serves GET http://127.0.0.1:3000/api/status with JSON body {"status":"ok"}
  - Environment variable UPSTREAM_URL points at the mock base URL (e.g. http://127.0.0.1:3000)
mocks:
  - wiremock-pilot (see docs/superpowers/pilot/dtu/)
---

# Scenario: Read upstream health

## Narrative
As an operator,
I want `sandbox-app/ping_upstream.py` to verify the upstream `/api/status` endpoint,
So that we know the integration path is wired before expanding the factory.

## Expected outcomes
- Running `python ping_upstream.py` with `UPSTREAM_URL=http://127.0.0.1:3000` prints exactly `SATISFIED` on stdout when the upstream returns `{"status":"ok"}`.
- When the upstream returns any other JSON or non-200, the script prints exactly `FAIL`.
- No secrets or tokens are printed to stdout.

## Validation notes for judge
- Treat trace + final stdout as primary evidence.
- Partial string matches are insufficient: stdout must be exactly `SATISFIED` or `FAIL` with trailing newline optional.
```

- **Step 2: Commit**

```bash
git add docs/superpowers/pilot/scenarios/SCN-PILOT-001-upstream-ok.md
git commit -m "docs(pilot): add SCN-PILOT-001 external scenario"
```

---

### Task 4: WireMock DTU stub (Docker Compose + mapping file)

> **Quint decision:** `dec-20260406-002` — WireMock standalone selected over Mockoon, Hoverfly, Mountebank for MCP-native agent operability + REST Admin API.

**Files:**

- Create: `docs/superpowers/pilot/dtu/docker-compose.wiremock.yml`
- Create: `docs/superpowers/pilot/dtu/mappings/pilot-status.json`
- **Step 1: Write WireMock mapping file**

Create `docs/superpowers/pilot/dtu/mappings/pilot-status.json`:

```json
{
  "request": {
    "method": "GET",
    "url": "/api/status"
  },
  "response": {
    "status": 200,
    "jsonBody": { "status": "ok" },
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

- **Step 2: Write Compose file**

Create `docs/superpowers/pilot/dtu/docker-compose.wiremock.yml`:

```yaml
services:
  wiremock-pilot:
    image: wiremock/wiremock:latest
    ports:
      - "3000:8080"
    volumes:
      - ./mappings:/home/wiremock/mappings:ro
```

- **Step 3: Verify stub responds**

Run:

```bash
cd /home/ja/night_coder/docs/superpowers/pilot/dtu
docker compose -f docker-compose.wiremock.yml up -d
sleep 10  # JVM startup
curl -sS http://127.0.0.1:3000/api/status
```

Expected stdout: `{"status":"ok"}`

Verify Admin API is accessible:

```bash
curl -sS http://127.0.0.1:3000/__admin/mappings | python3 -m json.tool
```

- **Step 4: Commit**

```bash
cd /home/ja/night_coder
git add docs/superpowers/pilot/dtu/docker-compose.wiremock.yml docs/superpowers/pilot/dtu/mappings/pilot-status.json
git commit -m "feat(pilot): add WireMock DTU stub for SCN-PILOT-001 (dec-20260406-002)"
```

---

### Task 5: Sandbox app starter (incomplete — agent completes)

**Files:**

- Create: `docs/superpowers/pilot/sandbox-app/ping_upstream.py`
- Create: `docs/superpowers/pilot/sandbox-app/README.md`
- **Step 1: Write README**

Create `docs/superpowers/pilot/sandbox-app/README.md`:

```markdown
# Sandbox app (pilot)

**Allowed edits:** Only files in this directory (`docs/superpowers/pilot/sandbox-app/`).

**Forbidden:** Do not edit `../scenarios/` or `../dtu/` during autonomous coding.

**Run:** `UPSTREAM_URL=http://127.0.0.1:3000 python ping_upstream.py`
```

- **Step 2: Write intentionally broken starter**

Create `docs/superpowers/pilot/sandbox-app/ping_upstream.py`:

```python
import os
import sys


def main() -> None:
    # TODO (agent): implement GET {UPSTREAM_URL}/api/status and print SATISFIED or FAIL per SCN-PILOT-001
    print("FAIL")
    sys.exit(1)


if __name__ == "__main__":
    main()
```

- **Step 3: Prove starter fails against running WireMock**

With WireMock up from Task 4:

```bash
cd /home/ja/night_coder/docs/superpowers/pilot/sandbox-app
UPSTREAM_URL=http://127.0.0.1:3000 python ping_upstream.py
```

Expected: prints `FAIL`, exit code 1.

- **Step 4: Commit**

```bash
git add docs/superpowers/pilot/sandbox-app/README.md docs/superpowers/pilot/sandbox-app/ping_upstream.py
git commit -m "feat(pilot): add sandbox-app starter for agent completion"
```

---

### Task 6: Pilot judge (Python + OpenAI-compatible API)

**Files:**

- Create: `docs/superpowers/pilot/judge/requirements.txt`
- Create: `docs/superpowers/pilot/judge/pilot_judge.py`
- Create: `docs/superpowers/pilot/fixtures/sample_trace.txt`
- Create: `docs/superpowers/pilot/traces/.gitkeep`
- **Step 1: Create `requirements.txt`**

Create `docs/superpowers/pilot/judge/requirements.txt`:

```
openai>=1.40.0
pytest>=8.0.0
```

- **Step 2: Create fixture trace**

Create `docs/superpowers/pilot/fixtures/sample_trace.txt`:

```text
[agent] read ping_upstream.py
[agent] edited ping_upstream.py to call GET /api/status
[stdout] SATISFIED
```

- **Step 3: Implement `pilot_judge.py`**

Create `docs/superpowers/pilot/judge/pilot_judge.py`:

```python
#!/usr/bin/env python3
"""Pilot judge: scenario markdown + trace text -> JSON score via chat completions."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from openai import OpenAI

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "satisfied": {"type": "boolean"},
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "reasoning": {"type": "string"},
    },
    "required": ["satisfied", "score", "reasoning"],
    "additionalProperties": False,
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", required=True, type=Path)
    p.add_argument("--trace", required=True, type=Path)
    args = p.parse_args()

    scenario_text = args.scenario.read_text(encoding="utf-8")
    trace_text = args.trace.read_text(encoding="utf-8")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        return 2

    client = OpenAI(api_key=api_key)
    model = os.environ.get("PILOT_JUDGE_MODEL", "gpt-4o-mini")

    prompt = (
        "You are an impartial judge. Given the scenario specification and an execution trace, "
        "decide whether the expected outcomes in the scenario are satisfied. "
        "Respond ONLY with JSON matching the schema.\n\n"
        f"SCENARIO:\n{scenario_text}\n\nTRACE:\n{trace_text}\n"
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "pilot_verdict",
                "schema": JUDGE_SCHEMA,
                "strict": True,
            },
        },
    )
    content = resp.choices[0].message.content
    if not content:
        print("ERROR: empty judge response", file=sys.stderr)
        return 3
    data = json.loads(content)
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- **Step 4: Install deps and run judge on fixture**

```bash
cd /home/ja/night_coder/docs/superpowers/pilot/judge
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
python pilot_judge.py \
  --scenario ../scenarios/SCN-PILOT-001-upstream-ok.md \
  --trace ../fixtures/sample_trace.txt
```

Expected: valid JSON on stdout with `"satisfied": true` (approximately; if model disagrees, widen fixture trace wording once).

- **Step 5: Commit**

```bash
cd /home/ja/night_coder
git add docs/superpowers/pilot/judge/requirements.txt docs/superpowers/pilot/judge/pilot_judge.py \
  docs/superpowers/pilot/fixtures/sample_trace.txt docs/superpowers/pilot/traces/.gitkeep
git commit -m "feat(pilot): add LLM judge CLI and sample trace"
```

---

### Task 7: Pytest for judge output shape

**Files:**

- Create: `docs/superpowers/pilot/tests/test_pilot_judge_output.py`
- **Step 1: Write test that mocks OpenAI**

Create `docs/superpowers/pilot/tests/test_pilot_judge_output.py`:

```python
import contextlib
import io
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
JUDGE_DIR = ROOT / "judge"
sys.path.insert(0, str(JUDGE_DIR))

import pilot_judge  # noqa: E402

SCENARIO = ROOT / "scenarios" / "SCN-PILOT-001-upstream-ok.md"
TRACE = ROOT / "fixtures" / "sample_trace.txt"


def test_main_outputs_schema_json(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    fake_payload = {
        "satisfied": True,
        "score": 0.95,
        "reasoning": "Stdout shows SATISFIED per scenario.",
    }

    class FakeCompletions:
        def create(self, *args, **kwargs):
            return MagicMock(
                choices=[MagicMock(message=MagicMock(content=json.dumps(fake_payload)))]
            )

    class FakeClient:
        def __init__(self, **kwargs):
            self.chat = MagicMock()
            self.chat.completions = FakeCompletions()

    monkeypatch.setattr(pilot_judge, "OpenAI", FakeClient)
    monkeypatch.setattr(
        sys,
        "argv",
        ["pilot_judge.py", "--scenario", str(SCENARIO), "--trace", str(TRACE)],
    )

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = pilot_judge.main()
    assert code == 0
    parsed = json.loads(buf.getvalue())
    assert parsed["satisfied"] is True
    assert 0 <= parsed["score"] <= 1
    assert "reasoning" in parsed
```

- **Step 2: Run pytest**

```bash
cd /home/ja/night_coder/docs/superpowers/pilot/judge
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt pytest
cd /home/ja/night_coder/docs/superpowers/pilot/tests
pytest test_pilot_judge_output.py -v
```

Expected: `1 passed`.

- **Step 3: Commit**

```bash
git add docs/superpowers/pilot/tests/test_pilot_judge_output.py
git commit -m "test(pilot): judge emits schema-shaped JSON"
```

---

### Task 8: Weekend runbook (time-box; orchestrator + stack per `DECISIONS.md`)

**Files:**

- Create: `docs/superpowers/pilot/runbooks/PILOT-WEEKEND.md`
- **Step 1: Write runbook**

Create `docs/superpowers/pilot/runbooks/PILOT-WEEKEND.md`:

```markdown
# Weekend overnight pilot — runbook

## Preconditions
- [ ] `CONSTRAINTS.md` edited for your environment
- [ ] `DECISIONS.md` filled and signed (**all pillars** from `Research_Summary_Table.md` decided via Quint, or explicit “pilot uses fallbacks” documented)
- [ ] Branch: `git checkout -b pilot/overnight-slice-001`
- [ ] DTU up and verified (WireMock per `dec-20260406-002`): `curl http://127.0.0.1:3000/api/status`

## Friday evening — start DTU
```bash
cd /home/ja/night_coder/docs/superpowers/pilot/dtu
docker compose -f docker-compose.wiremock.yml up -d
sleep 10  # JVM startup
curl -sS http://127.0.0.1:3000/api/status
```

## Friday evening — start orchestrator (per `DECISIONS.md`)

**Task file** the agent sees (no scenario text — keep scenario external):

Create `/tmp/openhands-pilot-task.txt`:

```
You are running a bounded pilot. Work only under docs/superpowers/pilot/sandbox-app/.
Implement ping_upstream.py per the behavior described in the project README in that folder.
Run: UPSTREAM_URL=http://127.0.0.1:3000 python ping_upstream.py
Do not edit docs/superpowers/pilot/scenarios/ or docs/superpowers/pilot/dtu/.
Commit your changes to git with message "feat(pilot): complete ping_upstream".
Write a short summary to docs/superpowers/pilot/traces/AGENT_SUMMARY.md including stdout from the test command.
```

**Detach run (10h cap):** Use the orchestrator command selected in `DECISIONS.md`. The OpenHands command below is the fallback/default.

```bash
tmux new -s pilot_oh
cd /home/ja/night_coder
timeout 10h openhands --headless --json -f /tmp/openhands-pilot-task.txt > docs/superpowers/pilot/traces/openhands.jsonl
# Ctrl+b then d to detach
```

**Note:** If `openhands` is not on PATH, install per OpenHands CLI docs, then re-run.

## Saturday morning — collect evidence

```bash
cd /home/ja/night_coder/docs/superpowers/pilot/sandbox-app
UPSTREAM_URL=http://127.0.0.1:3000 python ping_upstream.py | tee ../traces/final_stdout.txt
cd ../judge
. .venv/bin/activate
python pilot_judge.py --scenario ../scenarios/SCN-PILOT-001-upstream-ok.md --trace ../traces/combined.txt
```

Create `traces/combined.txt` manually by concatenating `openhands.jsonl` (or human summary), `AGENT_SUMMARY.md`, and `final_stdout.txt`.

## Stop / cleanup

```bash
cd /home/ja/night_coder/docs/superpowers/pilot/dtu
docker compose -f docker-compose.wiremock.yml down
```

## Pilot retrospective (15 min)

- Did stdout satisfy SCN-PILOT-001?
- Judge `satisfied` true?
- What broke (cost, time, tool errors)?

```

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/pilot/runbooks/PILOT-WEEKEND.md
git commit -m "docs(pilot): add weekend runbook for pilot orchestrator"
```

---

### Task 9: Pilot retrospective note (after first run)

**Files:**

- Create: `docs/superpowers/pilot/RETROSPECTIVE.md` (template only before run)
- **Step 1: Create template**

Create `docs/superpowers/pilot/RETROSPECTIVE.md`:

```markdown
# Pilot retrospective (fill after morning review)

## Outcomes
- SCN-PILOT-001 satisfied (yes/no):
- Judge score:
- Wall-clock duration:

## What worked

## What failed

## Stack decision delta (what we would swap for v2)
```

- **Step 2: Commit template**

```bash
git add docs/superpowers/pilot/RETROSPECTIVE.md
git commit -m "docs(pilot): add RETROSPECTIVE template"
```

---

## Appendix A — Ralph Orchestrator instead of OpenHands (one orchestrator winner)

If `DECISIONS.md` selects **Ralph**, replace the **Detach run** block in `PILOT-WEEKEND.md` with your Ralph loop targeting the same task file, for example:

```bash
# Example only — align PROMPT.md / hats with Ralph Orchestrator docs
tmux new -s pilot_ralph
cd /home/ja/night_coder
# Follow https://mikeyobrien.github.io/ralph-orchestrator/quick-start/
# Ensure max_runtime_seconds and max_cost_usd match CONSTRAINTS.md
```

Keep scenario + DTU + judge consistent with `DECISIONS.md` (this plan’s **locked choices** are WireMock per `dec-20260406-002`; judge: OpenJudge per DECISIONS.md).

**Further appendices:** Add **Appendix B, C, …** as you lock winners for Deer Flow, CrewAI+LangGraph, Gas Town, Ruflo, oh-my-openagent, etc., each with a copy-paste **detach** block and trace filename — do not let the main runbook imply OpenHands is the only long-term path.

---

## Self-review (plan author)

**1. Spec coverage**


| Requirement                                                                                             | Task                                                       |
| ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| (1) Non‑negotiables + constraints                                                                       | Task 1                                                     |
| (2) One vertical slice: repo, scenario, judge, DTU, orchestrator + **full-table Quint stack selection** | Task 2 (DECISIONS) + Tasks 3–6 + runbook Task 8            |
| (3) Time-boxed weekend overnight                                                                        | CONSTRAINTS + runbook `timeout 10h` + retrospective Task 9 |


**2. Placeholder scan:** No `TBD`/`TODO` in committed artifacts except intentional `TODO (agent)` inside `ping_upstream.py` starter.

**3. Type consistency:** Judge JSON schema keys stable across `pilot_judge.py` and test expectations.

---

## Plan complete

**Saved to:** `docs/superpowers/plans/2026-04-03-overnight-agent-vertical-slice-pilot.md`

**Two execution options:**

1. **Subagent-driven (recommended)** — Dispatch a fresh subagent per task; review between tasks. **REQUIRED SUB-SKILL:** superpowers:subagent-driven-development.
2. **Inline execution** — Run tasks in this session with checkpoints. **REQUIRED SUB-SKILL:** superpowers:executing-plans.

**Which approach do you want?**