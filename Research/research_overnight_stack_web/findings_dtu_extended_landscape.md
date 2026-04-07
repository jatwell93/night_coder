# DTU / mocks — extended landscape (web research, April 2026)

Synthesized options **beyond** Mockoon, Keploy, and MSW for **standalone HTTP mocks**, **spec-driven stubs**, **multi-protocol** imposters, and **async** virtualization. Use with [`Research_Summary_Table.md`](../Research_Summary_Table.md) §1.

**Related:** [`findings_dtu_mockoon_keploy_msw.md`](./findings_dtu_mockoon_keploy_msw.md) · gap wave 2 AWS/browser: [`gap_wave2/findings_gap_dtu_localstack_browserless.md`](./gap_wave2/findings_gap_dtu_localstack_browserless.md)

---

## A. Standalone HTTP mock servers (out-of-process; Docker-friendly)

| Tool | Summary | Official |
|------|---------|----------|
| **WireMock** | Matching, templating, faults, **record/replay**; standalone, embedded, Docker; ecosystem includes **WireMock MCP** for agent workflows | [wiremock.org](https://www.wiremock.org/) · [WireMock MCP post](https://www.wiremock.io/post/wiremock-mcp-ai-coding-agents) · [CLI recording](https://www.wiremock.io/post/local-api-recording-with-wiremock-cli) |
| **Hoverfly** | Go **proxy + simulate**; capture traffic, export simulations, latency/fault injection | [docs.hoverfly.io](https://docs.hoverfly.io/en/latest) · [SpectoLabs/hoverfly](https://github.com/SpectoLabs/hoverfly) |
| **MockServer** | Java Netty HTTP(S) mock + **proxy**; Docker `mockserver/mockserver` | [mock-server.com](https://www.mock-server.com/) |
| **Mountebank** | **Multi-protocol** imposters (HTTP, TCP, SMTP, …); stubs via REST API | [mountebank-testing/mountebank](https://github.com/mountebank-testing/mountebank) |
| **Mockoon** | CLI/Desktop/Docker; quick static routes | [mockoon.com/docs](https://mockoon.com/docs/) |

---

## B. Spec- and contract-driven mocks

| Tool | Summary | Official |
|------|---------|----------|
| **Prism** | Mock + validate from **OpenAPI** (v2/v3) and **Postman collections** | [stoplightio/prism](https://github.com/stoplightio/prism/) |
| **Pact stub server** | Serves interactions from **Pact** files (local dir, URL, or Broker) | [Pact stub server](https://docs.pact.io/implementation_guides/cli/pact-stub-server) · [pact-foundation/pact-stub-server](https://github.com/pact-foundation/pact-stub-server) |
| **Microcks** | Platform: OpenAPI, **AsyncAPI**, gRPC, GraphQL, SOAP; K8s/Helm; async (e.g. Kafka) tutorials | [microcks.io](https://microcks.io/documentation/getting-started/) |

---

## C. Scriptable / JVM / queue-aware

| Tool | Summary | Official |
|------|---------|----------|
| **Imposter** | Scriptable mocks (JS/Groovy/Java); OpenAPI, SOAP, Salesforce shapes | [imposter-project/imposter](https://github.com/imposter-project/imposter) |
| **Karate** (Netty) | Standalone JAR mock server; stateful behavior; proxy mode | [Karate test doubles](https://docs.karatelabs.io/extensions/test-doubles/) |
| **Mockintosh** | REST mocks + **Kafka/RabbitMQ** scenarios | [mockintosh.io](https://mockintosh.io/) |

---

## D. Record-replay (OS / kernel)

| Tool | Summary | Official |
|------|---------|----------|
| **Keploy** | eBPF capture; HTTP + DBs + queues; see `Research/keploy.md` | [keploy.io/docs](https://keploy.io/docs/) |

---

## E. Agent-adjacent (MCP, not HTTP DTU)

| Tool | Summary | Official |
|------|---------|----------|
| **Agent VCR** | Record/replay **MCP** JSON-RPC for deterministic agent-tool tests | [Medium: Agent VCR](https://medium.com/@pramod_cbz/introducing-agent-vcr-record-replay-and-diff-mcp-server-interactions-08e22495e01a) |

Use for **tooling** tests; does not stub Stripe/Slack-style HTTP APIs.

---

## Shortlist heuristic (overnight pilot)

1. **HTTP + minimal ops:** Mockoon, WireMock, Hoverfly.  
2. **OpenAPI is source of truth:** Prism.  
3. **Pact contracts exist:** Pact stub server.  
4. **Async / Kafka / many specs:** Microcks, Mockintosh.  
5. **Non-HTTP wire protocols:** Mountebank.  
6. **Real traffic → offline:** Keploy, Hoverfly capture, WireMock record.

---

## Limitations

Star counts, release tags, and commercial tiers (e.g. WireMock Cloud) change often; confirm on each project’s GitHub and docs before locking versions.

**Method:** Web search synthesis (April 2026); not a substitute for hands-on pilot compose files.
