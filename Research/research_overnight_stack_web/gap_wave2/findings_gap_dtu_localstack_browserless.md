# Gap: Digital Twin / Local Dependency Mocking — LocalStack & Headless Browser Services (Browserless, Playwright)

Research focus: **LocalStack** (AWS API emulation) and **Browserless** (and close alternatives: Playwright in Docker, `playwright run-server`, CDP/WebSocket) for autonomous coding agents, CI, and “digital twin” style local dependency mocking.

**Method:** Five broad web searches (LocalStack, Browserless, OpenHands/browser automation, LocalStack–AWS parity, Playwright Docker); one extra site-restricted query refined OpenHands doc links. Official pages were fetched for citation accuracy.  
**Date:** 2026-04-03

---

## 1. LocalStack — AWS service emulation

### Official documentation (full URLs)

- **Installation (CLI, Docker Compose, Docker CLI, Helm, Desktop):** https://docs.localstack.cloud/getting-started/installation/
- **AWS quickstart:** https://docs.localstack.cloud/aws/getting-started/quickstart/
- **Configuration reference:** https://docs.localstack.cloud/aws/capabilities/config/configuration
- **Docker images overview:** https://docs.localstack.cloud/aws/capabilities/config/docker-images
- **Auth token (required for current image workflow):** https://docs.localstack.cloud/getting-started/auth-token/ (linked from installation)
- **Auth tokens in workspace:** https://app.localstack.cloud/workspace/auth-tokens
- **Pricing:** https://www.localstack.cloud/pricing
- **Integrations (AWS CLI, frameworks, tooling):** https://docs.localstack.cloud/aws/integrations
- **Networking troubleshooting:** https://docs.localstack.cloud/aws/capabilities/networking/
- **Parity / how LocalStack compares to AWS (blog):** https://blog.localstack.cloud/2022-08-04-parity-explained/
- **Kubernetes deployment limitations (service-level gaps):** https://docs.localstack.cloud/aws/enterprise/kubernetes/limitations/
- **Third-party Docker guide (contextual):** https://docs.docker.com/guides/localstack

### Docker / self-host

- LocalStack runs **in Docker**; the installation doc describes **LocalStack CLI**, **Docker Compose**, raw **`docker run`**, **Helm** (`https://helm.localstack.cloud`), **LocalStack Desktop**, and the **Docker Desktop extension**.
- Current docs state a move to a **single authenticated LocalStack for AWS image** requiring an **auth token**; compose examples show image `localstack/localstack-pro`, gateway port **4566**, optional **4510–4559** for external services, **443** for HTTPS gateway (Pro), **`LOCALSTACK_AUTH_TOKEN`**, persistence via **`/var/lib/localstack`**, and often **`/var/run/docker.sock`** for Lambda and related execution.
- **Validate compose:** `localstack config validate` (recommended in docs).

### Wiring to E2E, tests, and agent-style workflows

- **Endpoint redirection:** Point AWS SDKs, `boto3`, Terraform, CDK, Serverless, etc. at the LocalStack gateway (typically `http://localhost:4566`) using vendor integration guides under **Integrations** (see URL above).
- **`awslocal`:** Wrapper around AWS CLI for local endpoints (documented under integrations).
- **Pattern for “digital twin”:** Replace real AWS dependencies (S3, SQS, DynamoDB, Lambda, API Gateway, IAM-shaped behavior, etc.) in dev/CI with LocalStack so agents or pipelines run without touching production accounts—same idea as contract tests against a local cloud-shaped surface.

### Limitations vs real AWS

- **Parity is explicit but incomplete:** LocalStack’s own parity article explains **simplifying assumptions** versus distributed AWS systems; many services prioritize **CRUD and common paths** over full production semantics. They track parity via **AWS Server Framework (ASF)**, **snapshot tests** against AWS, and **parity metrics** (see parity blog URL above).
- **Concrete gaps:** Tooling like CDK/Terraform can break on **small response differences** (e.g., exception message text, schema types)—LocalStack’s blog gives CDK/Terraform examples.
- **Kubernetes-specific limitations** doc lists **unsupported** services (e.g., SageMaker, Bedrock, EKS, CodeBuild in that doc) and **partial** implementations (e.g., ECS, EC2 userdata, RDS/MySQL versions, persistence caveats for some data stores).
- **Not “real” multi-AZ behavior:** No substitute for **real latency, quotas, edge IAM policies, or regional differences** unless you add separate testing on AWS.

### Cost / licensing notes

- **Auth token required** for the documented **authenticated** image workflow (see installation + auth token docs).
- **Plans and pricing:** https://www.localstack.cloud/pricing (detail lives on that page; tiers/features change over time—verify before procurement).
- **Pro image** appears in official compose/`docker run` examples (`localstack/localstack-pro`), signaling **paid/pro features** tied to subscription rather than anonymous pull for advanced scenarios.

---

## 2. Browserless — managed headless browser / CDP-style service

### Official documentation (full URLs)

- **Docs home:** https://docs.browserless.io/
- **Docker configuration reference (env vars, OSS vs Enterprise):** https://docs.browserless.io/baas/docker/config
- **Enterprise deployment / enterprise image:** https://docs.browserless.io/enterprise/docker/enterprise-image
- **Docker quick start (enterprise path):** https://docs.browserless.io/enterprise/docker/quickstart
- **Cloud → self-hosted migration:** https://docs.browserless.io/enterprise/docker/cloud-to-self-hosted
- **NGINX / load balancing (EXTERNAL URL):** https://docs.browserless.io/enterprise/docker/nginx-load-balancing
- **OpenTelemetry (enterprise Docker):** https://docs.browserless.io/enterprise/docker/opentelemetry
- **GitHub (upstream project):** https://github.com/browserless/browserless

### Docker / self-host

- **Enterprise image** example from docs: `registry.browserless.io/browserless/browserless/enterprise:latest` (registry auth typically required).
- **License vs API auth:** **`KEY`** = enterprise **license**; **`TOKEN`** = **API authentication** for clients. Docs warn not to confuse them.
- **Operational knobs:** `CONCURRENT` / `MAX_CONCURRENT_SESSIONS`, `QUEUED`, `TIMEOUT`, `PORT`, `EXTERNAL` (critical behind reverse proxies), health checks, metrics path, optional **OpenTelemetry**.
- **Security defaults:** CORS off; **`DISABLE_BLOCKLIST`** can allow navigation to localhost/private IPs/metadata endpoints—relevant when agents need to hit **local apps** (evaluate carefully).
- **Open-source Chromium image** is referenced in Browserless documentation ecosystem (e.g., **GHCR**-style distribution in vendor materials); confirm current image name and license in **Docker config** doc above before pinning in production.

### Wiring to E2E or agent tools

- **Playwright / Puppeteer:** Vendor pricing/marketing states **quick endpoint change** to connect existing scripts (hosted or self-hosted).
- **CDP / WebSocket:** Docker config doc describes **CDP WebSocket** reconnect behavior, **`webSocketDebuggerUrl`**, and session listings—agents or harnesses that speak **Chrome DevTools Protocol** or **Browserless REST/BrowserQL** can target the service URL instead of launching a local browser binary.
- **CI pattern:** Run Browserless as a **sidecar** or **shared service**; tests/agents connect over **`ws://`/`wss://`** to pooled browsers instead of installing Chrome on every runner.

### Limitations vs real browser / real user environment

- Still **Chromium-family** (or configured engines)—**not identical** to every user’s Safari/Firefox/Chrome versions unless you test those separately.
- **Bot detection, fonts, GPU, extensions, and media codecs** differ from typical end-user machines; vendor markets add-ons (e.g., captcha/residential proxy) for some of these gaps.
- **Session isolation and timeouts** are **server-enforced**; long autonomous agent loops need tuning (`TIMEOUT`, concurrency, queue) to avoid **429** under load.

### Cost / licensing notes

- **Hosted pricing:** https://www.browserless.io/pricing — at time of fetch, tiers included **Free** (low concurrency, unit/month caps, session time limits), **Prototyping** (~$25/mo annual), **Starter** (~$140/mo annual), **Scale** (~$350/mo annual), and **Enterprise** (custom). **Units** are time-chunked (vendor defines ~30s blocks per connection in FAQ on that page).
- **Self-hosted Enterprise:** Described as **license-based** (not the same as metered cloud units); contact sales for **commercial self-hosting**.
- **Compliance marketing:** Enterprise page sections reference **SOC 2, GDPR, DPA, HIPAA** (verify current attestations for your procurement).

---

## 3. Close alternative: Playwright official Docker image & remote server

### Official documentation (full URLs)

- **Docker:** https://playwright.dev/docs/docker
- **Continuous Integration:** https://playwright.dev/docs/ci
- **Microsoft Artifact Registry (image catalog):** https://mcr.microsoft.com/en-us/product/playwright/about
- **Dockerfile reference (Noble):** https://github.com/microsoft/playwright/blob/main/utils/docker/Dockerfile.noble
- **`browserType.connect` API:** https://playwright.dev/docs/api/class-browsertype#browser-type-connect

### Docker / self-host

- Image example from docs: `mcr.microsoft.com/playwright:v1.58.2-noble` (pin versions; mismatch breaks browser discovery).
- **Recommendations:** `--init`, `--ipc=host` for Chromium; separate user + **seccomp** profile for **untrusted** sites; image disclaimer: **testing/development**, not recommended for untrusted browsing as root.
- **Remote server pattern:** Run `playwright run-server` in container, connect from host or another container via **`PW_TEST_CONNECT_WS_ENDPOINT`** or `browserType.connect('ws://...')` (see Docker doc).

### Wiring to E2E / agents

- **Same as standard Playwright tests**, but browser runs in a **container** or **remote server**—suitable for **agent harnesses** already built on Playwright.
- **Contrast with Browserless:** Playwright’s path is **first-party Microsoft images + connect**; Browserless adds **pooling, REST/BrowserQL, enterprise ops features**, and commercial hosting.

### Limitations vs real browser

- Same class of limitations as any **headless automation** stack: environment differences, sandbox flags when running as root, no full fidelity to all desktop browser installs.

### Cost / licensing notes

- **Playwright** is open source (Apache 2.0); **Docker images** are Microsoft-published. No per-minute Browserless-style meter for self-hosted Playwright—**cost is your infra + CI minutes**.

---

## 4. OpenHands (example: in-runtime browser vs external Browserless)

### Official documentation (full URLs)

- **Runtime architecture (browser initialized inside sandbox):** https://docs.all-hands.dev/usage/architecture/runtime
- **Key features (Browser tab / agent-driven browsing):** https://docs.all-hands.dev/usage/key-features
- **Local setup:** https://docs.all-hands.dev/openhands/usage/local-setup

### Wiring note (conceptual)

- OpenHands’ documented runtime **initializes a Browser component inside the Docker sandbox** alongside bash, plugins, and Jupyter; the **backend talks to the action execution server over REST**, not over the same Socket.IO channel clients use.
- For **external** Browserless/Playwright-as-a-service, a harness would typically **configure the agent tool or test driver** to use a **remote WebSocket/CDP endpoint** (pattern described for Playwright/Browserless above). That is an **integration choice** on top of OpenHands’ default in-container browser model—verify in current OpenHands source (`openhands/runtime/...`, browser-related modules) for your version.

---

## 5. Synthesis for autonomous coding agents

| Layer | Tool | Best for | Tradeoff |
|--------|------|----------|----------|
| **AWS-shaped APIs** | LocalStack | S3/SQS/Dynamo/Lambda-shaped local dev, CI without AWS spend | Parity and auth/pricing model; not a full cloud replica |
| **Pooled remote browsers** | Browserless (cloud or licensed self-host) | Shared browser fleet, CDP/REST, ops features | Cost/licensing; tune timeouts/concurrency |
| **Playwright-native** | `mcr.microsoft.com/playwright` + `run-server` / CI image | Teams already on Playwright; minimal vendor lock | You operate pooling/quotas yourself |

---

## Sources (indexed)

1. https://docs.localstack.cloud/getting-started/installation/
2. https://www.localstack.cloud/pricing
3. https://docs.localstack.cloud/aws/capabilities/config/docker-images
4. https://blog.localstack.cloud/2022-08-04-parity-explained/
5. https://docs.localstack.cloud/aws/enterprise/kubernetes/limitations/
6. https://docs.browserless.io/baas/docker/config
7. https://www.browserless.io/pricing
8. https://playwright.dev/docs/docker
9. https://playwright.dev/docs/ci
10. https://docs.all-hands.dev/usage/architecture/runtime
11. https://docs.docker.com/guides/localstack
