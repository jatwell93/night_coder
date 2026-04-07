# Execution Sandbox — Research Report

**Question:** What isolation policy fits shell, filesystem, and network per task for overnight agents on a budget Linux VPS?

## Answer

- **Pilot default:** One **disposable OCI container per task** (Docker or Podman), non-root, no `--privileged`, no host network, workspace-only mounts, **default-deny egress** with an explicit “online” profile when needed. Limit concurrency on ~4GB RAM.
- **Stricter v1:** Rootless engine where reliable, `no-new-privileges`, tighter seccomp/LSM, read-only rootfs when compatible, **named offline vs online profiles**. Reserve **gVisor** for exceptional trust boundaries; avoid **Kata-per-task** as default on small VPS (RAM cost).
- **Lightweight alternative:** **Bubblewrap** or **Firejail** suit low-RAM command sandboxes but require more hand-built policy; devcontainers are “Docker + metadata” — same hardening focus (minimal mounts, egress).

## Sources

Findings: [`findings_sandbox.md`](findings_sandbox.md) — Docker rootless/usulnet, [bubblewrap](https://github.com/containers/bubblewrap), Firejail man pages, [devcontainer reference](https://code.visualstudio.com/docs/devcontainers/devcontainerjson-reference), [Red Guild devcontainer security](https://blog.theredguild.org/where-do-you-run-your-code-part-ii-2/), gVisor/Kata comparisons (Northflank, SciTePress PDF).

## Gaps

Orchestrator-specific wiring (Ralph) not validated in this pass; measure real FUSE/slirp overhead on your VPS before committing to rootless-only.
