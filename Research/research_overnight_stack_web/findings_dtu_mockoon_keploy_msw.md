# Mockoon vs Keploy vs MSW — comparison notes (web research, 2025–2026)

Short comparison of three tools that overlap around **API behavior in development and automated testing**, with different mechanisms: **standalone mock servers**, **in-process HTTP interception**, and **eBPF-backed record/replay**. Sources are official docs, project sites, and registries linked below.

---

## 1. Mockoon — CLI, Docker, local mock APIs

**Role:** Design and run **mock HTTP APIs** as real servers (desktop app for authoring; **CLI** and **Docker** for headless/CI and servers).

**Official entry points**

- Product / docs hub: [https://mockoon.com/docs/](https://mockoon.com/docs/) (includes “latest” docs path, e.g. [https://mockoon.com/docs/latest](https://mockoon.com/docs/latest))
- CLI (self-hosted mocks, flags, NPM/Docker patterns): [https://mockoon.com/cli/](https://mockoon.com/cli/)
- Tutorial-style CLI run: [https://mockoon.com/tutorials/run-mock-api-anywhere-cli/](https://mockoon.com/tutorials/run-mock-api-anywhere-cli/)
- Docker image: [https://hub.docker.com/r/mockoon/cli](https://hub.docker.com/r/mockoon/cli)
- Source (community): [https://github.com/mockoon/mockoon](https://github.com/mockoon/mockoon)

**CLI / Docker (typical local & CI pattern)**

- Global or project NPM: `@mockoon/cli`; start with a data file, e.g. `mockoon-cli start --data ./data-file.json` (see [CLI page](https://mockoon.com/cli/)).
- Docker: bind-mount the mock data file and publish ports; image `mockoon/cli` on Docker Hub documents usage (e.g. mount + `-p`); base image details appear on the Hub page.
- Docs note **version alignment**: desktop, CLI, and Docker share semantic versioning; keep **data file format** compatible with the CLI/Docker version in use ([docs](https://mockoon.com/docs/)).

**Open source**

- Described as **MIT-licensed** open source on the main GitHub org/repo ([mockoon/mockoon](https://github.com/mockoon/mockoon)).

**Comparison angle**

- **Out-of-process**: your app talks to a **real URL** (localhost/container) like a normal dependency. Good when you want **no test code changes** beyond configuration, or when multiple clients share one mock.

---

## 2. Keploy — eBPF, record/replay, test generation, OSS status

**Role:** **Language-agnostic** testing platform that records **real traffic** (APIs and dependencies) and replays with generated **mocks/stubs**; positioning emphasizes **minimal or no application code changes** via **eBPF** at the network layer.

**Official entry points**

- Docs: [https://keploy.io/docs/](https://keploy.io/docs/) and [https://docs.keploy.io/](https://docs.keploy.io/)
- eBPF concept page: [https://keploy.io/docs/concepts/what-is-keploy-ebpf/](https://keploy.io/docs/concepts/what-is-keploy-ebpf/)
- CLI commands: [https://keploy.io/docs/running-keploy/cli-commands](https://keploy.io/docs/running-keploy/cli-commands)
- Legal / policy hub: [https://keploy.io/legal](https://keploy.io/legal)
- Source: [https://github.com/keploy/keploy](https://github.com/keploy/keploy)

**eBPF, record/replay, and test generation (high level)**

- Docs describe capturing **requests/responses** and dependency calls, then **replaying** with captured mocks and handling “noisy” fields ([what-is-keploy-ebpf](https://keploy.io/docs/concepts/what-is-keploy-ebpf/)).
- Broader **infrastructure virtualization** narrative: HTTP plus databases, queues, external APIs, etc., as reflected on the GitHub project description and marketing/docs.
- **Test generation** from traffic and related flows is a core product claim (see [GitHub README](https://github.com/keploy/keploy) and docs); some doc paths also reference AI-assisted generation from OpenAPI/Postman/cURL (verify on current docs if you depend on that path).

**Open source**

- GitHub lists **Apache License 2.0** for [keploy/keploy](https://github.com/keploy/keploy).

**Comparison angle**

- **Kernel-assisted capture** vs hand-written mocks: strongest when you want **golden traffic** and **replay-based** integration/E2E style tests without maintaining Mockoon/MSW handlers manually. **Runtime and OS constraints** (eBPF availability, Linux-focused workflows) matter for adoption vs pure userland tools.

---

## 3. MSW (Mock Service Worker) — v2, Node.js, CI

**Role:** **In-process** mocking: intercepts outgoing HTTP(S) from the runtime (browser Service Worker; **Node** via patched `http`/`https`), so tests hit **real client code paths** without a separate mock server.

**Official entry points**

- Site: [https://mswjs.io/](https://mswjs.io/)
- **Node integration**: [https://mswjs.io/docs/integrations/node/](https://mswjs.io/docs/integrations/node/)
- **MSW 2.0 introduction**: [https://mswjs.io/blog/introducing-msw-2.0](https://mswjs.io/blog/introducing-msw-2.0)
- **Migration 1.x → 2.x**: [https://mswjs.io/docs/migrations/1.x-to-2.x/](https://mswjs.io/docs/migrations/1.x-to-2.x/)
- FAQ: [https://mswjs.io/docs/faq/](https://mswjs.io/docs/faq/)
- Source: [https://github.com/mswjs/msw](https://github.com/mswjs/msw)

**v2 + Node + CI**

- Node API: `setupServer` from `msw/node`, `server.listen()` / `server.resetHandlers()` / `server.close()` for **Jest, Vitest**, etc. ([Node docs](https://mswjs.io/docs/integrations/node/)).
- v2 unifies on **Fetch `Request`** semantics and changes handler signatures vs v1 ([intro post](https://mswjs.io/blog/introducing-msw-2.0), [migration guide](https://mswjs.io/docs/migrations/1.x-to-2.x/)).
- **Node.js ≥ 18** and **TypeScript ≥ 4.7** called out for v2 ([migration doc](https://mswjs.io/docs/migrations/1.x-to-2.x/)).

**Comparison angle**

- **Same process as tests/app**: excellent for **unit/integration tests** and fast feedback in CI **without** provisioning ports/containers. Less natural when the **system under test must call an external host** you cannot intercept (e.g. some native clients, or tests that intentionally bypass Node’s HTTP stack).

---

## Side-by-side (decision-oriented)

| Dimension | Mockoon | Keploy | MSW v2 |
|-----------|---------|--------|--------|
| **Where mocking runs** | Separate HTTP server (CLI/Docker/desktop) | OS-level capture + replay tooling | Inside Node (or browser SW) |
| **Typical setup cost** | Define/import routes (OpenAPI-friendly), run process | Install CLI/agent; record sessions | Handlers in JS/TS + test lifecycle hooks |
| **CI fit** | Start CLI/Docker, point `BASE_URL` at mock | Record/replay pipelines; kernel/env requirements | `setupServer` in test setup; no extra port |
| **Best when** | Stable contract mocks, multi-consumer mock, quick local dependency stand-in | Derive tests/mocks from **real** traffic | Tight test loops, full app HTTP client path in Node |

---

## Limitations of this note

- Star counts, exact latest release tags, and “AI generation” feature scope change frequently; confirm on [GitHub](https://github.com/mockoon/mockoon), [GitHub](https://github.com/keploy/keploy), and [GitHub](https://github.com/mswjs/msw) before locking versions into a build matrix.
- Keploy’s **platform requirements** (kernel, containers, cloud) should be validated against current install docs before production rollout.

**Research method:** up to **five** web searches (Mockoon CLI/Docker/docs; Keploy eBPF/OSS; MSW v2 Node/CI; Keploy license; Mockoon OSS/license), synthesized into this file.
