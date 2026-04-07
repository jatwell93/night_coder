# Secrets / IAM Implementation Brief

Decision reference: `dec-20260407-002`  
Selected approach: **Doppler (service tokens + `doppler run`)**  
Research: [`research_secrets_iam/`](../../../../research_secrets_iam/) (plan, findings, report)

## Goal

Centralize provider keys with **one read-only service token per trust boundary** in CI and on the host, and ensure secrets do not appear in git, workflow YAML, or Langfuse payloads.

## Scope

**In scope**

- Doppler **project** with configs (e.g. `pilot`, `ci`); **service tokens** scoped to a single config each.
- Entrypoints: `doppler run -- <agent>` and same pattern for judge or CI job steps that need keys.
- Redaction policy for logs and traces (what fields to strip or hash).
- Rollback path: static GitHub encrypted secrets per provider.

**Out of scope (defer)**

- Automated rotation webhooks and multi-integration sync until v1 hardening.
- 1Password / Vault unless org mandate (`dec-20260407-002` rationale).

## Checklist

1. Create configs; mint tokens; store only `DOPPLER_TOKEN` (or per-env tokens) in CI secrets.
2. Replace raw `OPENAI_API_KEY`-style injection with Doppler-managed names; document variable mapping.
3. CI dry-run: confirm no secret values in job logs.
4. Document fail-closed behavior on auth errors (do not rely on stale CLI cache for security decisions).

## Alternatives (admissible)

- **1Password** — if already standard; use `op run` / `load-secrets-action`.
- **SOPS** — for small sets of git-reviewed encrypted config, not as sole dynamic secret store.
