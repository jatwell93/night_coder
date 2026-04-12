# DTU / judge / observability smoke tests (pilot) — T060

Install and **smoke-test** the dependencies that sit beside Ralph on the overnight VPS: **WireMock** (DTU), **OpenJudge** (`py-openjudge`), and **OpenLLMetry** (`traceloop-sdk`) with **Langfuse-oriented export hooks** (Phase 1 vs Phase 2 per observability decision).

**OS:** Ubuntu 24.04 LTS (noble), x86_64. **Operator user:** `deploy` (sudo-capable), per [`vps-bootstrap.md`](./vps-bootstrap.md).

**Prerequisites**

- [`vps-bootstrap.md`](./vps-bootstrap.md) — Python 3.12+, `curl`, `jq`, and **[§12 — pilot repository checkout on the VPS](./vps-bootstrap.md#12-pilot-repository-checkout-on-the-vps)** so `docs/superpowers/pilot/dtu/` exists on the Droplet (not implied by T055–T059 alone).  
- [`vps-container-runtime.md`](./vps-container-runtime.md) — Podman (recommended) or Docker; `podman-compose` available.  
- [`vps-secrets-bootstrap.md`](./vps-secrets-bootstrap.md) — Doppler (or equivalent) for **LLM keys** used by OpenJudge smoke beyond import-only; optional Langfuse keys for Phase 2 OTLP smoke.

**Decisions and briefs**

- DTU: WireMock — [`../DECISIONS.md`](../DECISIONS.md), Quint `dec-20260406-002`; compose [`../dtu/docker-compose.wiremock.yml`](../dtu/docker-compose.wiremock.yml).  
- Judge: OpenJudge — [`../judge/IMPLEMENTATION-BRIEF.md`](../judge/IMPLEMENTATION-BRIEF.md), Quint `dec-20260406-003`.  
- Observability: Langfuse phased + OpenLLMetry — [`../observability/IMPLEMENTATION-BRIEF.md`](../observability/IMPLEMENTATION-BRIEF.md), Quint `dec-20260406-004`.

Do **not** commit API keys, Doppler tokens, or populated `.env` files. Use `doppler run` or a throwaway venv outside the git tree for ad hoc installs.

---

## 1. Goals

| Pillar | Goal of this runbook |
|--------|----------------------|
| **DTU** | Pull and run WireMock with pilot mappings; HTTP stub and Admin API reachable on **loopback only**. |
| **Judge** | Install `py-openjudge` in a venv; prove import/version; optional grader smoke when an LLM key is available. |
| **CXDB** | Install `traceloop-sdk`; prove `Traceloop.init()` and at least one exported span (console OTLP is enough for VPS smoke). |
| **Langfuse hooks** | Document **Phase 1** (no Langfuse containers on the 4 GiB pilot box) vs **Phase 2** (self-hosted Langfuse OTLP endpoint + env vars). Optional `curl` health check when a Langfuse base URL exists. |

---

## 2. Paths on the VPS

If you have not cloned this repo on the Droplet yet, do **[`vps-bootstrap.md` §12](./vps-bootstrap.md#12-pilot-repository-checkout-on-the-vps)** first.

Set a convenience variable to that checkout (adjust if you cloned elsewhere):

```bash
export NIGHT_CODER_ROOT="$HOME/night_coder"   # example; must match §12
```

Pilot WireMock assets live under:

```text
$NIGHT_CODER_ROOT/docs/superpowers/pilot/dtu/
```

---

## 3. WireMock (DTU)

### 3.1 Security note (firewall + inbound)

**Cloud firewall:** Inbound **only SSH (22)** and **no** inbound rule for **3000** is the right shape for this pilot: WireMock stays off the public internet even though the container maps `3000` on the host. **Outbound** “all TCP/UDP” (or permissive egress) matches [`vps-bootstrap.md`](./vps-bootstrap.md) and allows `apt`, `git`, and image pulls.

**SSH sources:** If SSH is allowed from **all IPv4 / all IPv6**, that is common but noisier than restricting to **your home / bastion IP** (recommended in the bootstrap firewall table). Keep **key-based SSH only**; do not enable password auth.

The pilot compose file publishes **host** port `3000`. Ensure the provider firewall still **does not** add a public rule for 3000. For defense in depth you may change the port mapping to **loopback only** (example: `127.0.0.1:3000:8080` in `docker-compose.wiremock.yml`).

WireMock’s **Admin API** (`/__admin/...`) must never be intentionally exposed on a public interface (`dec-20260406-002`).

### 3.2 Start the stack

```bash
cd "$NIGHT_CODER_ROOT/docs/superpowers/pilot/dtu"
podman-compose -f docker-compose.wiremock.yml pull
podman-compose -f docker-compose.wiremock.yml up -d
```

If you use Docker instead of Podman, replace `podman-compose` with `docker compose` and the same `-f` path.

### 3.2.1 Troubleshooting: `short-name "wiremock/wiremock" did not resolve` (Podman)

Ubuntu’s default Podman has **no** unqualified-search registries, so `wiremock/wiremock:latest` is ambiguous. The compose file uses **`docker.io/wiremock/wiremock:latest`**. If you still see this error, confirm the `image:` line in [`../dtu/docker-compose.wiremock.yml`](../dtu/docker-compose.wiremock.yml) and run `git pull` in `~/night_coder`.

**Alternative (host-wide):** add unqualified search registries in `/etc/containers/registries.conf` (see `man containers-registries.conf`). Prefer the fully qualified image in compose so the stack stays explicit.

### 3.3 Smoke: stubbed upstream

Pilot mapping serves `GET /api/status` → JSON `{"status":"ok"}` (see [`../dtu/mappings/pilot-status.json`](../dtu/mappings/pilot-status.json)).

```bash
curl -fsS "http://127.0.0.1:3000/api/status" | jq .
```

**Expected:** `{"status":"ok"}` (or equivalent JSON with `status` == `"ok"`).

### 3.4 Smoke: Admin API (mappings loaded)

```bash
curl -fsS "http://127.0.0.1:3000/__admin/mappings" | jq '.mappings | length'
```

**Expected:** at least **1** mapping.

### 3.5 Tear down (when finished)

```bash
cd "$NIGHT_CODER_ROOT/docs/superpowers/pilot/dtu"
podman-compose -f docker-compose.wiremock.yml down
```

### 3.6 WireMock MCP (stretch)

Agent-side **WireMock MCP** is a stretch goal from `dec-20260406-002`. If you add it later, document the exact MCP server package, config path, and a single `list_tools`-style smoke in a private operator note—do not commit tokens.

---

## 4. OpenJudge (judge)

Ubuntu’s system Python is **PEP 668**–managed: use a **venv** (or `pipx`) for `py-openjudge`, not `pip install` onto `/usr`.

### 4.1 Create a pilot venv

```bash
python3 -m venv "$HOME/.venvs/night-coder-pilot"
source "$HOME/.venvs/night-coder-pilot/bin/activate"
python -m pip install -U pip
python -m pip install "py-openjudge>=0.2"
```

**Package vs import name:** install **`py-openjudge`**; import **`openjudge`** (see [`Research/research_overnight_stack_web/gap_wave2/findings_gap_openjudge_canonical.md`](../../../../Research/research_overnight_stack_web/gap_wave2/findings_gap_openjudge_canonical.md)).

### 4.2 Smoke: import and version

```bash
source "$HOME/.venvs/night-coder-pilot/bin/activate"
python -c "import openjudge; import importlib.metadata as m; print('py-openjudge', m.version('py-openjudge'))"
```

**Expected:** no `ImportError`; printed version string.

### 4.3 Smoke: grader path (optional; needs LLM credentials)

Only after [`vps-secrets-bootstrap.md`](./vps-secrets-bootstrap.md) provides keys (for example `OPENAI_API_KEY` or provider-specific variables OpenJudge expects):

```bash
doppler run --config pilot -- bash -lc 'source "$HOME/.venvs/night-coder-pilot/bin/activate" && python - <<"PY"
# Minimal check: SDK loads; replace with LLMGrader quickstart from upstream when wiring pilot_judge.
import openjudge
print("openjudge OK", openjudge)
PY'
```

Follow the official quickstart for **`LLMGrader`** / **`FunctionGrader`** when you connect real scenarios: [OpenJudge quickstart](https://agentscope-ai.github.io/OpenJudge/get_started/quickstart/).

**Langfuse write-back** from OpenJudge is **optional** in Phase 1 and aligns with Phase 2 Langfuse (`../judge/IMPLEMENTATION-BRIEF.md`).

---

## 5. OpenLLMetry (`traceloop-sdk`)

Install into the **same** pilot venv (or a dedicated `venv-otel` if you prefer smaller images).

```bash
source "$HOME/.venvs/night-coder-pilot/bin/activate"
python -m pip install "traceloop-sdk>=0.30"
```

Upstream install and init pattern: [OpenLLMetry Python getting started](https://www.traceloop.com/docs/openllmetry/getting-started-python).

### 5.1 Smoke: init + console trace export

`Traceloop.init()` defaults to the Traceloop Cloud endpoint and **requires** `TRACELOOP_API_KEY` unless you pass a **custom span exporter** or change `TRACELOOP_BASE_URL` with matching auth (for example Langfuse in §6). For a **local, keyless** pilot smoke, pass OpenTelemetry’s **`ConsoleSpanExporter`** (pulled in with `traceloop-sdk`).

```bash
source "$HOME/.venvs/night-coder-pilot/bin/activate"
python - <<'PY'
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow

Traceloop.init(
    disable_batch=True,
    app_name="night-coder-pilot-smoke",
    exporter=ConsoleSpanExporter(),
)

@workflow(name="t060_smoke")
def t060_smoke():
    return {"ok": True}

t060_smoke()
print("t060_smoke_done")
PY
```

**Expected:** `t060_smoke_done` on stdout and **one JSON object** per span printed (includes `traceloop.workflow.name` / `traceloop.span.kind` attributes). If you instead see “Missing Traceloop API key”, you are not using a custom exporter—use the script above verbatim.

### 5.2 Content tracing

For overnight forensics, keep prompt/response capture **on** unless policy forbids it. OpenLLMetry documents **`TRACELOOP_TRACE_CONTENT`** (default captures content; set to `false` only if you intentionally strip bodies). See [`Research/openllmetry.md`](../../../../Research/openllmetry.md).

### 5.3 Decorators (“hooks”) for non-LLM tools

Shell, `git`, and raw subprocesses are **not** auto-instrumented. Plan explicit **`@tool`** (or equivalent) decorators on high-value commands when the orchestrator wiring lands (`../observability/IMPLEMENTATION-BRIEF.md`).

---

## 6. Langfuse export hooks (no full stack on pilot VPS in Phase 1)

**Hard rule (`dec-20260406-004`):** do **not** run the full Langfuse compose stack on the **same 4 GiB** pilot VPS as the agent during **Phase 1**.

| Phase | On pilot VPS | Smoke |
|-------|----------------|-------|
| **1** | File/console OTLP-style review; Ralph JSONL + OpenJudge verdict | §5.1 console exporter; disk sizing notes in [`../observability/IMPLEMENTATION-BRIEF.md`](../observability/IMPLEMENTATION-BRIEF.md) |
| **2** | Self-hosted Langfuse on a **sized** host (≥4 GiB for the Langfuse stack alone is a starting point—validate against upstream compose) | OTLP HTTP to Langfuse’s public OTEL path |

### 6.1 Phase 2 — environment template (self-hosted)

When Langfuse is available on a **private** base URL (example placeholder `https://langfuse.internal`), OpenLLMetry can send OTLP using the pattern from [Langfuse + OpenLLMetry](https://www.traceloop.com/docs/openllmetry/integrations/langfuse): set `TRACELOOP_BASE_URL` to your **`/api/public/otel`** endpoint and supply Basic auth via `TRACELOOP_HEADERS` derived from `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` (store keys in Doppler per [`vps-secrets-bootstrap.md`](./vps-secrets-bootstrap.md)).

**Never** point the pilot at Langfuse Cloud if that violates your org **self-hosted-only** policy (`dec-20260406-004`).

Example **non-secret** structural smoke (fails fast if host wrong); run with real keys via Doppler:

```bash
# Example only — replace HOST with your self-hosted Langfuse
curl -fsS -o /dev/null -w "%{http_code}\n" "https://langfuse.internal/api/public/health" || true
```

Interpret **HTTP 200** (or upstream-documented health behavior) as “endpoint exists”; OTLP acceptance is verified with a real `Traceloop.init()` export from §5 with `TRACELOOP_BASE_URL` set.

### 6.2 Authority boundary

**OpenJudge** remains the **authoritative** judge. Langfuse LLM-as-judge features are **supplementary only** if explicitly enabled (`../observability/IMPLEMENTATION-BRIEF.md`).

---

## 7. Resource sanity check (recommended)

After WireMock is **up** and the Python venv is ready, on the Droplet run:

```bash
free -h
podman stats --no-stream   # or docker stats --no-stream
```

**Expectation:** total used memory still leaves headroom for Ralph + agent workloads on a **4 GiB** machine. If WireMock plus idle services leaves little free RAM, capture numbers for the observability Phase 1 sizing checklist (`dec-20260406-004`).

---

## 8. T060 completion checklist

- [ ] WireMock compose **pull** and **up** succeed from `docs/superpowers/pilot/dtu`.  
- [ ] `curl http://127.0.0.1:3000/api/status` returns `{"status":"ok"}`.  
- [ ] `curl http://127.0.0.1:3000/__admin/mappings` shows **≥1** mapping.  
- [ ] Inbound **3000/tcp** is **not** open to the world on the cloud firewall.  
- [ ] `py-openjudge` installs in a venv; `import openjudge` succeeds.  
- [ ] `traceloop-sdk` installs; §5.1 script prints **JSON span** output from `ConsoleSpanExporter`.  
- [ ] Phase 1: **no** Langfuse stack on the 4 GiB pilot VPS; Langfuse OTLP smoke deferred to Phase 2 **or** documented on the separate host.  
- [ ] Optional: OpenJudge grader smoke with `doppler run` and real provider keys.  
- [ ] Revision row added below when the operator finishes the checklist.

---

## 9. References

- WireMock Docker image: [https://hub.docker.com/r/wiremock/wiremock](https://hub.docker.com/r/wiremock/wiremock)  
- OpenJudge / `py-openjudge`: [https://pypi.org/project/py-openjudge/](https://pypi.org/project/py-openjudge/)  
- OpenLLMetry Python: [https://www.traceloop.com/docs/openllmetry/getting-started-python](https://www.traceloop.com/docs/openllmetry/getting-started-python)  
- Langfuse OpenTelemetry: [https://langfuse.com/docs/opentelemetry](https://langfuse.com/docs/opentelemetry)  
- Prior steps: [`vps-container-runtime.md`](./vps-container-runtime.md), [`vps-secrets-bootstrap.md`](./vps-secrets-bootstrap.md)  
- Next: [`vps-guardrails-bootstrap.md`](./vps-guardrails-bootstrap.md) (T061)

---

## Revision

| Date | Notes |
|------|-------|
| 2026-04-12 | Initial T060 runbook: WireMock compose smoke, OpenJudge venv smoke, OpenLLMetry console export smoke, Langfuse Phase 1/2 hooks and boundaries. |
| 2026-04-12 | Prerequisites + §2: explicit `vps-bootstrap.md` §12 repo checkout before paths under `docs/superpowers/pilot/`. |
| 2026-04-12 | §3.1: cloud firewall + SSH scope; §3.2.1 Podman short-name fix (`docker.io/...` in compose). |
