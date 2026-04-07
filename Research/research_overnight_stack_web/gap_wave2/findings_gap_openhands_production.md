# Gap: OpenHands production / VPS hardening

**Research scope:** Headless `always-approve` behavior, Docker sandbox agent server, secrets and local config files, official security posture, GitHub advisories/issues, sandbox-related risk discussion, deployment patterns (systemd, reverse proxy, avoiding public agent exposure).

**Method:** Web search (5 queries) plus targeted fetches of official docs and GitHub security pages for verification.

---

## 1. Headless mode and `always-approve`

Official CLI documentation states that **headless mode always runs in `always-approve` mode**: the agent executes actions **without confirmation**, and this **cannot be changed**—`--llm-approve` is **not** available in headless mode.

- **Source:** [Headless Mode — OpenHands Docs](https://docs.openhands.dev/openhands/usage/run-openhands/headless-mode)

**Production implications:**

- Treat headless runs as **fully autonomous code execution** with the same privileges as the runtime (host process, mounted volumes, or sandbox container, depending on setup).
- For auditability, docs recommend **`--json`** for JSONL event streams (CI parsing, logging, integration).
- **Contrast (SDK):** The Software Agent SDK documents separate confirmation policies (`AlwaysConfirm`, `NeverConfirm`, `ConfirmRisky`) for programmatic control—relevant when you **do not** use CLI headless and instead drive `Conversation` yourself.

- **Source:** [Security & Action Confirmation — OpenHands SDK](https://docs.openhands.dev/sdk/guides/security)

---

## 2. Docker sandbox and agent server

**Docker sandbox (SDK):** `DockerWorkspace` runs the agent server in an isolated container; docs describe this as isolation from the host and suitable for production, testing, and untrusted code. Pre-built images (e.g. `ghcr.io/openhands/agent-server:latest-python`) are recommended; `DockerDevWorkspace` builds on demand. The sandbox Dockerfile is called out as defining secure defaults and services (e.g. VS Code, VNC) on defined ports.

- **Source:** [Docker Sandbox — OpenHands Docs](https://docs.openhands.dev/sdk/guides/agent-server/docker-sandbox)
- **Dockerfile (referenced in docs):** [software-agent-sdk … agent_server/docker/Dockerfile](https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-agent-server/openhands/agent_server/docker/Dockerfile)

**Agent server architecture:** FastAPI HTTP + WebSocket, workspace/Docker lifecycle, per-user containers, documented API key auth pattern (`Authorization: Bearer`), health/metrics endpoints.

- **Source:** [Agent Server Package — OpenHands Docs](https://docs.openhands.dev/sdk/arch/agent-server)
- **Source code tree:** [github.com/OpenHands/software-agent-sdk … openhands/agent_server](https://github.com/OpenHands/software-agent-sdk/tree/main/openhands-agent-server/openhands/agent_server)

**Docs also describe optional workspace networking restrictions** (e.g. `network_mode: none` or `allowed_hosts`) under “Network Security” on the same agent-server page—useful for egress control discussions on VPS deployments.

---

## 3. Secrets, API keys, and local settings files

**OpenHands Cloud (UI):**

- **Secrets:** Stored via **Settings → Secrets**; injected as **environment variables** in the agent runtime; secret **values** cannot be viewed or edited in place (delete and recreate to rotate).
- **Source:** [Secrets Management — OpenHands Docs](https://docs.all-hands.dev/openhands/usage/settings/secrets-settings)

- **API keys:** OpenHands LLM key vs programmatic OpenHands API key (cloud only); LLM key requires cloud billing threshold per docs.
- **Source:** [API Keys Settings — OpenHands Docs](https://docs.openhands.dev/openhands/usage/settings/api-keys-settings)

**CLI / self-hosted configuration (files and env):**

| File | Purpose |
|------|---------|
| `~/.openhands/agent_settings.json` | LLM config (model, api_key, base_url, etc.) |
| `~/.openhands/cli_config.json` | CLI preferences |
| `~/.openhands/mcp.json` | MCP server configs |
| `~/.openhands/conversations/` | Conversation history |

- **Source:** [Command Reference — OpenHands Docs](https://docs.openhands.dev/openhands/usage/cli/command-reference)

**Environment overrides:** `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL` with **`--override-with-envs`**; overrides are **not persisted**—prefer this or a secrets manager over committing keys.

- **Same source:** [Command Reference](https://docs.openhands.dev/openhands/usage/cli/command-reference)

**`openhands web` binding:** Default host is **`0.0.0.0`** (all interfaces); docs show hardening example **`--host 127.0.0.1`** for local-only bind.

- **Same source:** [Command Reference](https://docs.openhands.dev/openhands/usage/cli/command-reference)

**Self-hosted / local run (broader setup):**

- **Source:** [Local Setup — OpenHands Docs](https://docs.all-hands.dev/openhands/usage/run-openhands/local-setup)

---

## 4. Official security policy and GitHub security artifacts

**GitHub Security tab:** As of fetch, the repository states **no `SECURITY.md`** (“This project has not set up a SECURITY.md file yet”) with a link to **report a vulnerability** via GitHub’s private advisory flow.

- **Source:** [Security overview — OpenHands/OpenHands](https://github.com/OpenHands/OpenHands/security)

**Published GitHub Security Advisory (example):**

- [GHSA-7h8w-hj9j-8rjw — Command Injection in Git Diff Handler](https://github.com/OpenHands/OpenHands/security/advisories/GHSA-7h8w-hj9j-8rjw) (listed on the security page; severity **High** per GitHub UI at time of fetch)

**Third-party advisory index (for CVE cross-reference):**

- [GitLab Advisory Database — openhands / CVE-2026-33718](https://advisories.gitlab.com/pkg/pypi/openhands/CVE-2026-33718/) (summarizes authenticated command injection via git diff API path handling in sandbox context—verify details against the official GHSA and fixed versions)

**Discussion: unsafe deserialization (state restore):**

- [Issue #13583 — Security: Unsafe pickle deserialization in state restoration (CWE-502)](https://github.com/OpenHands/OpenHands/issues/13583)

**Future / alternative isolation (not production guidance per se):**

- [Issue #13203 — QEMU microVM runtime backend (exec-sandbox) as alternative to Docker](https://github.com/OpenHands/OpenHands/issues/13203)

---

## 5. Known risks and “sandbox escape” framing

**OWASP-style static assessment (GitHub issue, not a CVE):** [OWASP Agentic AI Security Assessment — OpenHands · Issue #13378](https://github.com/OpenHands/OpenHands/issues/13378)

Highlights from that issue (paraphrased; see issue for exact table):

- **Unsafe execution (CRITICAL):** subprocess / shell execution inside containers.
- **Inadequate sandboxing (HIGH):** Docker isolates from host, but agent may run with **broad capability inside the container** (e.g. package installs, system changes).
- **Excessive agency (HIGH):** autonomous code, tests, PRs, dependency installs.

The author explicitly notes this is **not** a vulnerability disclosure and that **Docker sandboxing is intentional**; mitigations suggested include **network restrictions**, **package allowlisting**, **review gates before git push/PR**, **credential isolation in sandbox**, and **audit logging**.

**Interpretation for “sandbox escape”:** Public materials emphasize **host isolation via Docker** while warning that **inside-container** power is large; “escape” in the wild usually means **kernel/container breakout** or **misconfiguration** (e.g. Docker socket mounting, privileged containers)—those specifics were not deeply covered in the five search budget; prioritize **official GHSA/Issues** and **SDK agent-server hardening** sections for actionable items.

---

## 6. Recommended deployment patterns (VPS / production)

**From official agent-server docs:**

- **Single-server / VPS example** shows `openhands-agent-server --host 0.0.0.0 --port 8000` with **systemd/supervisor** mentioned as the process manager pattern.
- **Hardening alignment:** Pair **TLS**, **firewall**, **rate limiting**, and **API key auth** as documented; consider **restricting workspace egress** via documented `WORKSPACE_CONFIG` network options.
- **Source:** [Agent Server Package — OpenHands Docs](https://docs.openhands.dev/sdk/arch/agent-server)

**Do not expose the agent API blindly to the internet:**

- Prefer **binding the backend to loopback** (or private network) and fronting with a **reverse proxy** (TLS termination, auth, rate limits). Official docs illustrate `https://agent-server.example.com` and Bearer tokens—implying a controlled edge, not raw port exposure.
- **Source:** [Agent Server Package](https://docs.openhands.dev/sdk/arch/agent-server) — authentication and deployment sections.

**CLI `openhands web`:** Use **`--host 127.0.0.1`** when a reverse proxy on the same host should be the only public entrypoint.

- **Source:** [Command Reference](https://docs.openhands.dev/openhands/usage/cli/command-reference)

**Community write-up (non-official):** Hardened Docker Compose ideas (pinned images, resource limits, health checks, localhost-oriented patterns) appear in third-party blogs; treat as **supplementary** and validate against your OpenHands version.

- **Example:** [Fixing OpenHands: Hardened Docker Compose for Production — interconnectd.com](https://interconnectd.com/blog/31/fixing-openhands-hardened-docker-compose-for-production/)

**systemd:** Official text references **systemd/supervisor** alongside the agent-server binary; no first-party unit file was located in this pass—typical pattern is `ExecStart=` with explicit `--host 127.0.0.1` or firewalled `0.0.0.0`, plus `Restart=`, `User=`, and **no secrets in unit files** (use `EnvironmentFile=` with root-only permissions or your orchestrator’s secret store).

---

## 7. Synthesis checklist (production / VPS)

1. **Assume headless = full auto-approval**; scope tasks, filesystem mounts, and network access accordingly; use **`--json`** for audit trails.
2. **Prefer env / secret injection** over long-lived keys in `~/.openhands/agent_settings.json`; use **`--override-with-envs`** when you want non-persistent overrides.
3. **Agent server:** TLS + auth at the edge, **least-privilege firewall**, consider **workspace network restrictions** from SDK docs; avoid advertising Docker socket to untrusted users.
4. **Monitor GitHub Security advisories and issues**; there is **no project SECURITY.md** at time of research—process is via **GitHub “Report a vulnerability”**.
5. **Treat OWASP-style findings as design-risk context**, not a substitute for version-specific CVE review before each deploy.

---

## 8. URL index (full links)

- https://docs.openhands.dev/openhands/usage/run-openhands/headless-mode  
- https://docs.openhands.dev/sdk/guides/security  
- https://docs.openhands.dev/sdk/guides/agent-server/docker-sandbox  
- https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-agent-server/openhands/agent_server/docker/Dockerfile  
- https://docs.openhands.dev/sdk/arch/agent-server  
- https://github.com/OpenHands/software-agent-sdk/tree/main/openhands-agent-server/openhands/agent_server  
- https://docs.all-hands.dev/openhands/usage/settings/secrets-settings  
- https://docs.openhands.dev/openhands/usage/settings/api-keys-settings  
- https://docs.openhands.dev/openhands/usage/cli/command-reference  
- https://docs.all-hands.dev/openhands/usage/run-openhands/local-setup  
- https://github.com/OpenHands/OpenHands/security  
- https://github.com/OpenHands/OpenHands/security/advisories/GHSA-7h8w-hj9j-8rjw  
- https://advisories.gitlab.com/pkg/pypi/openhands/CVE-2026-33718/  
- https://github.com/OpenHands/OpenHands/issues/13378  
- https://github.com/OpenHands/OpenHands/issues/13583  
- https://github.com/OpenHands/OpenHands/issues/13203  
- https://interconnectd.com/blog/31/fixing-openhands-hardened-docker-compose-for-production/  
- https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ (cited from issue #13378)

---

*End of findings (wave 2 gap: OpenHands production hardening).*
