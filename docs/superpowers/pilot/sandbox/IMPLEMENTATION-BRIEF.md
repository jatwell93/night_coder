# Execution Sandbox Implementation Brief

Decision reference: `dec-20260407-001`  
Selected approach: **OCI container per task (Docker/Podman) with named offline/online profiles**  
Research: [`research_execution_sandbox/`](../../../../research_execution_sandbox/) (plan, findings, report)

## Goal

Give every agent task a **deterministic contract** for filesystem, network, and process isolation on a solo VPS, without defaulting to VM-per-task or privileged containers.

## Scope

**In scope**

- Two (or more) **named profiles**, at minimum: **offline** (default-deny egress, workspace mount) and **online** (documented allowlist or bridge network policy).
- **Non-root** user in the image; **no** `--privileged` for routine work.
- Runner integration: how Ralph (or the host wrapper) invokes `docker run` / `podman run` (or compose target) so NTM and sandbox stack consistently.
- Pinned base image digest or tag in repo.
- Evidence: one pilot run completes inside offline profile; egress test shows deny/allow behavior.

**Out of scope (defer)**

- gVisor/Kata as **default** lane (exceptional trust only).
- Firejail/bubblewrap **unless** you explicitly add a second lane for RAM-critical tasks.

## Checklist

1. Document image name, non-root UID, bind mounts (workspace only writable).
2. Document offline profile: network mode / firewall / `--network none` equivalent.
3. Document online profile: when package installs or external APIs are allowed.
4. Verify orchestrator does not bypass the wrapper (absolute paths to binaries, nested Docker without policy).
5. Capture marginal RAM for 1–2 concurrent tasks.

## Rollback

Remove container wrapper; rely on host execution + NTM per `dec-20260407-001`.
