# Secrets / IAM for AI coding agents — research findings

**Scope:** API keys, rotation, CI and headless injection for agents and servers. **Primary deep dive:** Doppler. **Alternatives covered:** 1Password CLI, HashiCorp Vault Agent (injector/sidecar), Mozilla SOPS, AWS Secrets Manager.

Sources below are official docs or vendor blogs unless noted. All URLs are full strings for copy/paste.

---

## 1. Doppler

### How agents and servers get secrets

- **CLI injection:** The Doppler CLI can run a process with secrets in the environment via `doppler run -- your-command` (typical pattern for local dev, VMs, and scripts). Service tokens can be passed as `DOPPLER_TOKEN` or configured persistently per machine/directory.
- **Service tokens:** A **Service Token** is **read-only** access to **one config** inside **one project** (least privilege for apps/CI vs personal/CLI tokens that have write scope). Create from dashboard (Project → Config → Access) or CLI (`doppler configs tokens create …`).
- **Ephemeral tokens:** CLI supports **ephemeral** service tokens with `--max-age` (e.g. one minute) for temporary access (e.g. short-lived containers).
- **Kubernetes / Docker:** Docs describe injecting `DOPPLER_TOKEN` into deployments and using `doppler run` with the token in containers.
- **Integrations:** Doppler can **sync** secrets to external systems (e.g. GitHub Actions repository secrets); when values change (including rotation), syncs update downstream stores.

**URLs**

- Service tokens: https://docs.doppler.com/docs/service-tokens  
- Secrets rotation overview: https://docs.doppler.com/docs/secrets-rotation  
- GitHub Actions / CI patterns (blog): https://www.doppler.com/blog/managing-secrets-ci-cd-environments-github-actions-advanced-techniques  
- Rotation + GitHub Actions (blog): https://www.doppler.com/blog/automated-secrets-rotation-with-doppler-and-github-actions  
- Dynamic / rotated secrets tutorial (blog, includes RBAC mention): https://www.doppler.com/blog/dynamic-secrets-in-action  

### Rotation

- **Automated rotation** supports **API rotation** (public API of the target service) and **proxied rotation** (e.g. AWS Lambda-based agents; Doppler describes rotation agents as **open source** and auditable, with audit history in the customer cloud for proxied flows).
- **Zero-downtime pattern:** Documentation emphasizes a **two-secret / two-instance** model where the target system can keep **two active credentials** while one is rotated.
- **Downstream effects:** Rotations can trigger **webhooks**, **Kubernetes Operator** redeploys (when configured), **integration syncs** (e.g. push updated values to CI), and **activity log** / SIEM-style notifications (e.g. Slack, Teams, Splunk — plan-dependent per docs excerpt).
- **Limitation called out in blog:** Example given that **GitHub Personal Access Tokens** are **not** supported for rotation via GitHub’s API constraints (product/marketing content — verify against current Doppler UI if you rely on this).

**URLs:** same as rotation doc and blogs above.

### Teams, access control, and audit

- Multi-environment workflows use **projects** and **configs** (e.g. dev/staging/prod). **RBAC** and **scoped API keys** are described in Doppler’s rotation/security guidance (see dynamic secrets blog).
- **Activity log** entries on rotation and access support operational and compliance visibility (details and retention vary by plan — confirm in product docs for your tier).

**URL:** https://www.doppler.com/blog/dynamic-secrets-in-action  

### CI / headless notes for AI agents

- Store **one** long-lived bootstrap secret in CI (e.g. GitHub encrypted secret): the **Doppler service token** for the agent’s config — not individual provider API keys.
- Agent job installs Doppler CLI, sets `DOPPLER_TOKEN`, runs `doppler run -- agent-entrypoint` (or uses sync if you intentionally mirror into GitHub Secrets).
- **Caveat from service token docs:** If a token is **revoked**, CLI behavior may still expose **last successfully fetched** secrets from cache/fallback in some cases — design agents to fail closed on auth errors where possible.

---

## 2. 1Password CLI (alternative)

### Model

- **Secret references** in templates (`op://vault/item/field`) so repos hold **references**, not plaintext.
- **`op inject`:** Renders a templated file into a resolved file with secrets substituted.  
- **`op run`:** Runs commands with secrets loaded (similar ergonomic to `doppler run` for shell workflows).

**URLs**

- Secret references / config templates: https://developer.1password.com/docs/cli/secrets-config-files  
- `op inject` reference: https://developer.1password.com/docs/cli/reference/commands/inject  

### Headless / server / CI

- **1Password Connect:** For servers and CI, deploy **Connect** and set `OP_CONNECT_HOST` and `OP_CONNECT_TOKEN`; then `op inject`, `op run`, `op read`, and `op item get` work against Connect without interactive sign-in.
- **Service accounts:** Documented for **least privilege** (restrict CLI/automation to specific vaults). GitHub Actions can use **`OP_SERVICE_ACCOUNT_TOKEN`** without Connect.

**URLs**

- Connect + CLI: https://developer.1password.com/docs/connect/cli/  
- GitHub Actions: https://developer.1password.com/docs/ci-cd/github-actions  
- Action repo: https://github.com/1password/load-secrets-action  

### Rotation

- Rotation is **not** a single built-in “rotate my RDS password on a schedule” product surface like Doppler/AWS SM; teams typically **update items in 1Password** and rely on **automation fetching current values** via references. OAuth / vendor portals may still need separate lifecycle tooling.

### Fit for AI agents

- Strong when org **already** standardizes on 1Password; **`load-secrets-action@v4`** maps secret references to env vars for agent steps. Requires **either** Connect infrastructure **or** service account token stored in CI.

---

## 3. HashiCorp Vault Agent & Kubernetes injector (alternative)

### Model

- **Vault Agent** handles **authentication**, **token renewal**, and **secret rendering** (e.g. Consul Template) so applications can stay **Vault-unaware** and read files or env populated by the agent.
- **Auto-auth:** Pairs an **auth method** (AWS, Kubernetes, AppRole, JWT, etc.) with **sinks** (e.g. file token path). Agent **renews** tokens until Vault denies renewal.

**URL:** https://developer.hashicorp.com/vault/docs/agent/autoauth  

### Kubernetes sidecar / injector

- **Vault Agent Injector** is a **mutating admission webhook** that adds **init** and/or **sidecar** containers; secrets render to a **shared volume** (e.g. `/vault/secrets`). **Sidecar** continues to renew/update secrets while the pod runs.
- Annotations such as `vault.hashicorp.com/agent-inject: "true"` and `vault.hashicorp.com/agent-inject-secret-<name>: "<path>"` request secret files.

**URLs**

- Injector concept: https://developer.hashicorp.com/vault/docs/deploy/kubernetes/injector  
- Sidecar tutorial: https://developer.hashicorp.com/vault/tutorials/kubernetes/kubernetes-sidecar  
- Kubernetes auto-auth method: https://developer.hashicorp.com/vault/docs/agent-and-proxy/autoauth/methods/kubernetes  

### CI / bare-metal agents

- Vault is **flexible** but **heavier**: you run and harden a Vault cluster, configure auth for runners (AppRole, JWT/OIDC, etc.), and use Agent or direct API. Common for enterprises; **higher ops burden** than Doppler/1Password SaaS for small teams.

### Rotation

- Vault supports **dynamic secrets** and **lease** renewal (database creds, etc.). Consumer must respect lease lifetimes; Agent helps with renewal for file-rendered secrets.

---

## 4. Mozilla SOPS (alternative — git-native encryption)

### Model

- **SOPS** encrypts **values** in YAML, JSON, ENV, INI (keys often remain visible) so diffs stay reviewable. Backends include **age**, **PGP**, **AWS KMS**, **GCP KMS**, **Azure Key Vault**, and others.
- **`.sops.yaml`** at repo root defines **creation rules** (which keys apply to which paths). Multiple master keys support DR and multi-party decrypt.

**URLs**

- Repository (getsops): https://github.com/getsops/sops  
- Flux + SOPS guide (ecosystem): https://v2-0.docs.fluxcd.io/flux/guides/mozilla-sops  

### CI / agents

- Pipeline needs a **decryption capability**: e.g. `SOPS_AGE_KEY` / `SOPS_AGE_KEY_FILE`, or cloud credentials with **KMS Decrypt**. Then `sops -d` or export dotenv from decrypted files.
- **Rotation** = **re-encrypt** or **change material** in Git with normal PR review; **no** centralized automatic API-key rotation unless you orchestrate it yourself.

### Fit for AI agents

- Good for **infra GitOps** and **static bundles** of config; **weak** for “fetch latest API key from central store every run” unless paired with KMS + tight IAM. **Risk:** decrypted material on disk in CI — treat runner as trusted and ephemeral.

---

## 5. AWS Secrets Manager (cloud SM alternative)

### Model

- Central store for **API keys, tokens, DB creds**; integrates with **IAM** for access. **Automatic rotation** often implemented via **Lambda** (AWS templates for RDS; custom functions for other secret types).

**URLs**

- Rotation (non-database / generic Lambda pattern): https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_turn-on-for-other.html  
- Rotation schedule / CLI: https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_turn-on-cli.html  
- Lambda execution role permissions for rotation: https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets-required-permissions-function.html  
- **GitHub Actions:** `aws-actions/aws-secretsmanager-get-secrets@v2` with **`configure-aws-credentials`** and **OIDC**-assumed roles (avoid long-lived access keys): https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_github.html  
- Rotation windows / frequency (blog): https://aws.amazon.com/blogs/security/how-to-configure-rotation-windows-for-secrets-stored-in-aws-secrets-manager/  

### Fit for AI agents

- Excellent when workloads already on **AWS** and IAM/OIDC to GitHub is approved. **Rotation** is strong but **Lambda + IAM** policy work is non-trivial. **GCP Secret Manager** / **Azure Key Vault** are analogous (not searched in this pass to stay within search budget; same pattern: IAM + OIDC + fetch step).

---

## Comparison snapshot (agents + CI)

| Dimension | Doppler | 1Password CLI | Vault Agent / Injector | SOPS | AWS Secrets Manager |
|-----------|---------|---------------|------------------------|------|---------------------|
| **Injection style** | CLI `doppler run`, env, sync to integrations | `op run` / `op inject`, GH Action | Files on volume / templates | Decrypt files in CI | Fetch via AWS API / GH Action |
| **Bootstrap secret in CI** | Service token | Service account token or Connect token | Vault auth (e.g. JWT/AppRole) | age key or AWS creds for KMS | None if OIDC to IAM role |
| **Rotation** | Built-in rotated secrets + sync | Manual / procedural | Dynamic secrets + leases | Operational (re-encrypt) | Managed rotation + Lambda |
| **Ops complexity** | Low (SaaS) | Low–medium (Connect optional) | High | Low tool, medium key hygiene | Medium (IAM + rotation) |

---

## Pilot-minimal posture vs v1 (Doppler as primary candidate)

### Pilot-minimal posture

- **One** Doppler **project** with **two configs** (e.g. `dev` / `pilot` and `ci`) and **one service token per trust boundary** (read-only, single config).
- **CI:** Store `DOPPLER_TOKEN` in GitHub (or your runner) as an encrypted secret; install CLI; use **`doppler run --`** to start the agent so **no API keys** live in workflow YAML or repo files.
- **Local / human devs:** Personal login or separate dev service token; never commit `.env` with real keys.
- **Rotation:** **Manual** updates in Doppler UI/CLI for pilot; enable **ephemeral** tokens for any **shared** ephemeral runner experiments.
- **Audit:** Rely on Doppler **activity log** for “who touched what”; defer webhooks/SIEM and automated rotation until v1.

**Rationale:** Minimizes moving parts, proves agent + CI path, keeps blast radius small with per-config service tokens.

### v1 with Doppler as primary

- **Team structure:** Projects aligned to **teams** or **services**; **configs** per environment; **RBAC** so only break-glass roles can rotate production-class secrets.
- **Rotation:** Turn on **Doppler rotated secrets** for supported targets (DB/IAM/API-backed); use **two-instance** strategy where required; wire **webhooks** or **K8s operator** so agents/pods pick up new values without stale caches.
- **CI integration:** **GitHub Actions sync** (or equivalent) so GitHub env secrets stay updated when Doppler changes — reduces drift between “source of truth” and platform-native secret stores.
- **Alternatives on the edges:** Keep **AWS Secrets Manager** (or cloud SM) for **AWS-native** dynamic creds if required by security; use **1Password** if corporate mandate for human + machine vault; use **Vault** if existing enterprise standard; use **SOPS** only for **git-stored** infra secrets that must stay in-repo encrypted.

**Rationale:** Doppler maps cleanly to **agent ergonomics** (`doppler run`), **CI bootstrap** (single service token), **team scaling** (projects/RBAC), and a credible **rotation + sync** story without operating Vault or Lambda rotation in the first iteration.

---

*Research conducted with web search (5 queries). Product behaviors and plan limits change — validate critical controls in current vendor documentation before production.*
