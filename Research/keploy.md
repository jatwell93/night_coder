#digitall-twin-universe 
# DeepWiki Q&A with Code Context for Repository: keploy/keploy
## Q1
Yes. Keploy is designed to record real external dependency calls (e.g., Slack, Stripe, databases, queues) and then replay tests using those recorded mocks, so you can run thousands of scenarios without hitting live services, incurring costs, or hitting rate limits

### How it works
- **Record**: Keploy captures outgoing network calls to external services and stores them as mocks in YAML.
- **Replay (Test)**: During test mode, Keploy intercepts outgoing calls and responds with the stored mocks instead of contacting real services. The Replayer loads these mocks and injects them via the instrumentation layer
- **Infra virtualization**: Beyond HTTP, it supports databases (Postgres, MySQL, MongoDB), streaming/queues (Kafka, RabbitMQ), and more, enabling fully offline test runs

### Implications for scale and cost
- Because tests use recorded mocks, you can run thousands of scenarios locally or in CI without external dependencies, avoiding costs and rate limits.
- The tool is language-agnostic and uses eBPF for capture, requiring no code changes

## Notes
- Keploy’s unit-test generator (ut-gen) is a separate feature that sends code to an LLM; it is not required for the record-replay workflow described above
- During replay, if a mock is not found, the proxy can emit an error; ensure your recordings cover the scenarios you intend to test

### Citations

**File:** README.md (L51-55)
```markdown
Just run your app with `keploy record`. Real API + integration flows are automatically captured as tests and mocks. *(Keploy uses eBPF under the hood to capture traffic, so you **don’t need** to add any SDKs or modify code.)* 

## 📹 Record and Replay complex Flows
Keploy can record and replay complex, distributed API flows as mocks and stubs.  It's like having a very light-weight time machine for your tests—saving you tons of time!

```

**File:** README.md (L60-65)
```markdown
## 🐇 Complete Infra‑Virtualization (beyond HTTP mocks)

Unlike tools that only mock HTTP endpoints, Keploy records **databases** (Postgres, MySQL, MongoDB), **streaming/queues** (Kafka, RabbitMQ), external APIs, and more. 

It replays them deterministically so you can run tests without re‑provisioning infra.

```

**File:** README.md (L144-145)
```markdown
Because Keploy intercepts at the **network layer (eBPF)**, it works with **any language, framework, or runtime**—no SDK required. 
> Note: Some of the dependencies are not open-source by nature because their protocols and parsings are not open-sourced. It's not supported in Keploy enterprise. 
```

**File:** pkg/agent/proxy/proxy.go (L624-635)
```go
		case models.MODE_TEST:
			err := matchedParser.MockOutgoing(parserCtx, srcConn, dstCfg, m.(*MockManager), rule.OutgoingOptions)
			if err != nil && err != io.EOF && !errors.Is(err, context.Canceled) {
				utils.LogError(logger, err, "failed to mock the outgoing message")
				// Send specific error type to error channel for external monitoring
				proxyErr := models.ParserError{
					ParserErrorType: models.ErrMockNotFound,
					Err:             err,
				}
				p.SendError(proxyErr)
				return err
			}
```

**File:** pkg/service/replay/replay.go (L914-934)
```go
	var loopErr error
	utils.TemplatizedValues = conf.Template
	utils.SecretValues = conf.Secret

	// Add secret files to .gitignore if they exist
	if len(utils.SecretValues) > 0 {
		err = utils.AddToGitIgnore(r.logger, r.config.Path, "/*/secret.yaml")
		if err != nil {
			r.logger.Warn("Failed to add secret files to .gitignore", zap.Error(err))
		}
	}

	var actualTestMockMappings = make(map[string][]string)
	var consumedMocks []models.MockState
	consumedMocks, err = HookImpl.GetConsumedMocks(runTestSetCtx) // Getting mocks consumed during initial setup
	if err != nil {
		utils.LogError(r.logger, err, "failed to get consumed filtered mocks")
	}
	for _, m := range consumedMocks {
		totalConsumedMocks[m.Name] = m
	}
```

**File:** README-UnitGen.md (L223-225)
```markdown
2. Does Keploy send your private data to any cloud server for test generation?<br>
    - No, Keploy does not send any user code to remote systems, except when using the unit test generation feature. When using the UT gen feature, only the source code and the unit test code will be sent to the Large Language Model (LLM) you are using. By default, Keploy uses - litellm to support vast number of LLM backends. Yes, if your organization has its own LLM(a private one), you can use it with Keploy. This ensures that data is not sent to any external systems.

```

---

## Official / 2026 links

- [Keploy docs](https://keploy.io/docs/) · [GitHub `keploy/keploy`](https://github.com/keploy/keploy)
- [`findings_dtu_mockoon_keploy_msw.md`](research_overnight_stack_web/findings_dtu_mockoon_keploy_msw.md)
- [LocalStack](https://docs.localstack.cloud/getting-started/installation/) · [Browserless](https://docs.browserless.io/) — [`findings_gap_dtu_localstack_browserless.md`](research_overnight_stack_web/gap_wave2/findings_gap_dtu_localstack_browserless.md)
