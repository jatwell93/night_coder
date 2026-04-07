# Secrets / IAM — Research Report

**Question:** How should API keys and provider auth be handled for overnight agents, with **Doppler** as the named candidate?

## Answer

- **Pilot-minimal:** One Doppler **project**, configs per trust boundary (e.g. `pilot` / `ci`), **read-only service token per config**. CI stores only `DOPPLER_TOKEN`; agents start via `doppler run -- …`. No API keys in workflow YAML or committed `.env`.
- **v1 with Doppler:** RBAC by team/service, **rotated secrets** where supported (two-credential patterns), webhooks / sync to GitHub Actions so platform secrets stay aligned. Alternatives at edges: AWS Secrets Manager (IAM/OIDC), 1Password if org standard, Vault if enterprise already runs it, SOPS for git-encrypted static bundles.
- **Boundaries:** Treat logs/traces as **secret-excluding** by policy; be aware of Doppler CLI **cache behavior** after token revocation — prefer fail-closed on auth errors.

## Sources

Findings: [`findings_secrets.md`](findings_secrets.md) — [Doppler service tokens](https://docs.doppler.com/docs/service-tokens), [rotation](https://docs.doppler.com/docs/secrets-rotation), [1Password CLI](https://developer.1password.com/docs/cli/secrets-config-files), [Vault Agent](https://developer.hashicorp.com/vault/docs/agent/autoauth), [SOPS](https://github.com/getsops/sops), [AWS Secrets Manager + GitHub](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_github.html).

## Gaps

Plan-specific Doppler limits (retention, SIEM) should be confirmed in current vendor docs before production.
