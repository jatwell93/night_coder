# Pilot trial configuration

Per-environment configuration for overnight trial runs. Files in this directory tune orchestrator
behaviour, guardrail policy overrides, DTU fixtures, and judge scenario references for a given
environment (local development, VPS pilot, CI).

## Scope

This directory holds **runtime configuration only** — not secrets, not code, not scenarios.

| Belongs here | Does not belong here |
|--------------|----------------------|
| Budget caps, timeouts, retry counts | API keys, tokens (see Doppler, T059) |
| DTU fixture toggles, scenario feature flags | Scenario content (see `../scenarios/`, T062) |
| Model policy overrides, provider preferences | Runbook text (see `../runbooks/`) |
| Environment-specific path overrides | Source code (see `../../../../src/`) |

## Layout (planned)

Files are added incrementally as user-story tasks land. Current structure:

```text
docs/superpowers/pilot/config/
└── README.md          ← this file (T002)
```

Expected additions as tasks ship:

| Task | File | Purpose |
|------|------|---------|
| T018 | `guardrail-policy.yaml` | NTM policy baseline referenced by guardrail loader. |
| T023 | `run-profiles.yaml` | `offline` / `online` execution profile definitions. |
| T029 | `judge-config.yaml` | External judge harness configuration. |
| T037 | `dtu-manifest.yaml` | DTU dependency readiness manifest. |
| T041 | `run-manifest.template.json` | Run manifest template seed. |
| T050 | `model-policy.yaml` | Model/provider role-policy mapping. |

## Conventions

- **Format preference:** YAML for human-edited config, JSON for machine-generated artifacts.
- **Naming:** lowercase-kebab-case filenames. Suffix with the consumer's domain
  (`guardrail-policy.yaml`, not `policy.yaml`).
- **Overrides:** environment-specific overrides go in `config/<env>/` subdirectories, for example
  `config/vps/guardrail-policy.yaml`. The loader picks the base file first, then applies the
  environment override on top.
- **Secrets rule:** if a field contains a credential, move it to Doppler and reference the env
  var name here (e.g. `api_key_env: OPENROUTER_API_KEY`). Never inline the value.
- **Schema:** every new config file must ship with a matching `*.schema.json` (or inline JSON
  Schema comment block) so the loader can validate it at startup.

## Related references

- [`../runbooks/README.md`](../runbooks/README.md) — Runbook index.
- [`../DECISIONS.md`](../DECISIONS.md) — Stack decisions that constrain config shape.
- [`../../../../specs/001-overnight-vps-system/tasks.md`](../../../../specs/001-overnight-vps-system/tasks.md) —
  Task list (source of truth for which config files land with which task).
