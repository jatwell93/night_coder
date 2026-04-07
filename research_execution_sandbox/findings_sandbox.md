# Execution sandbox research — autonomous coding agents on a budget Linux VPS

Scope: isolation mechanisms, per-task policy patterns, and trade-offs for a solo operator on ~4GB RAM. Sources drawn from up to five web searches (Apr 2026).

---

## 1) Common isolation options (high level)

### Docker (rootful vs rootless)

- Rootful Docker runs the daemon as root; a container escape can theoretically yield host-root impact; rootless mode runs daemon and containers under an unprivileged user via user namespaces, bounding escape impact to unprivileged host UIDs.  
  Sources: [Running Docker in Rootless Mode (usulnet)](https://articles.usulnet.com/articles/docker-rootless-mode.html), [Rootless and Standard Docker (overcast.blog)](https://overcast.blog/rootless-and-standard-docker-a-useful-comparison-6e07e19ab505)

- Rootless limitations called out in practice: no `--privileged`, no low ports (&lt;1024) without workarounds, cgroup v2 expectations, ICMP/`ping` issues, optional FUSE overlay (fuse-overlayfs) with reported ~5–15% disk I/O overhead vs native overlay2; user-space networking (e.g. slirp4netns) often cited ~10–20% network overhead vs native, with “pasta” cited as lower (~3–8%). CPU/memory overhead for many workloads described as small (&lt;1%) aside from those paths.  
  Source: [Running Docker in Rootless Mode (usulnet)](https://articles.usulnet.com/articles/docker-rootless-mode.html)

- Podman is often compared as daemonless and rootless-by-default; rootless networking still uses slirp4netns/pasta-class approaches, so similar network trade-offs; one comparison cites dockerd ~50MB vs no persistent daemon for Podman (operational memory shape differs).  
  Source: [Podman vs Docker: Rootless, Daemonless (usulnet)](https://articles.usulnet.com/articles/podman-vs-docker)

### Dev Containers (`devcontainer.json`)

- Dev Containers are **metadata on top of an OCI runtime** (typically Docker/Podman): they standardize how a dev environment is built, not a separate kernel-isolation layer. Security is mostly Docker’s namespaces/cgroups/seccomp/AppArmor (or equivalents) plus how you mount the workspace and which flags you pass.  
  Sources: [Dev Container metadata reference (VS Code)](https://code.visualstudio.com/docs/devcontainers/devcontainerjson-reference), [Development Container Specification (containers.dev)](https://containers.dev/implementors/spec)

- Hardening knobs exposed in metadata include `privileged` (default false), `capAdd`, `securityOpt` (e.g. `no-new-privileges`, seccomp profiles), and `runArgs` for read-only rootfs, labels, etc.; mounting strategy (minimal bind mounts, tmpfs workspace) reduces host filesystem exposure.  
  Sources: [Dev Container metadata reference](https://code.visualstudio.com/docs/devcontainers/devcontainerjson-reference), [Where do you run your code? part II — devcontainer security (The Red Guild)](https://blog.theredguild.org/where-do-you-run-your-code-part-ii-2/)

- Docker **Enhanced Container Isolation (ECI)** is a Docker Desktop admin feature using Sysbox to harden “privileged-looking” dev workflows; relevant mainly where Docker Desktop/sysbox is in play, not a generic Linux VPS default.  
  Source: [Enhanced Container Isolation (Docker Docs)](https://docs.docker.com/security/for-admins/hardened-desktop/enhanced-container-isolation/)

### Firejail

- Firejail is a **SUID-root helper** that sandboxes with Linux namespaces, seccomp-bpf, and capabilities; default profile mounts major system dirs read-only and leaves `/home` and `/tmp` writable unless overridden — policy is profile-driven.  
  Sources: [firejail(1) (manpages.org)](https://manpages.org/firejail), [firejail(1) (Ubuntu manpages)](https://manpages.ubuntu.com/manpages/jammy/man1/firejail.1.html)

- Network: `--net=none` / profile `net none` creates a new namespace with only loopback. Filesystem: `blacklist`, `read-only`, `tmpfs`, `bind`, `private` (tmpfs-backed home/root), `whitelist` patterns per `firejail-profile(5)`. Optional cgroup placement and rlimits exist in profiles.  
  Sources: [firejail-profile(5) (man7.org)](https://www.man7.org/linux/man-pages/man5/profile.5.html), [firejail-profile(5) (Ubuntu manpages)](https://manpages.ubuntu.com/manpages/xenial/en/man5/firejail-profile.5.html)

### Bubblewrap (`bwrap`)

- Bubblewrap is a **low-level, often unprivileged** sandbox constructor (used by Flatpak): starts from an empty tmpfs root in a new mount namespace; **security is entirely a function of the chosen flags**, not a single packaged policy.  
  Sources: [containers/bubblewrap (GitHub)](https://github.com/containers/bubblewrap), [bwrap(1) (Ubuntu manpages)](https://manpages.ubuntu.com/manpages/jammy/man1/bwrap.1.html)

- Namespace flags include `--unshare-net` (loopback-only netns), `--unshare-pid`, `--unshare-user`, etc.; filesystem is built with `--ro-bind`, `--bind`, `--tmpfs`, `--proc`, `--dev`. Optional `--seccomp FD` for syscall filtering; `--die-with-parent` for lifecycle binding to the supervisor.  
  Sources: [bwrap(1) (Ubuntu manpages)](https://manpages.ubuntu.com/manpages/jammy/man1/bwrap.1.html), [bwrap TLDR (Linux Command Library)](https://linuxcommandlibrary.com/man/bwrap)

### gVisor and Kata Containers (high level)

- **gVisor**: user-space kernel (“Sentry”) intercepts syscalls; adds **stronger logical isolation than shared-kernel runc** without a full VM per container; syscall-heavy / I/O-heavy workloads pay more overhead; integrates via `containerd`/`RuntimeClass` patterns in Kubernetes ecosystems.  
  Sources: [Kata vs Firecracker vs gVisor (Northflank)](https://northflank.com/blog/kata-containers-vs-firecracker-vs-gvisor), [gVisor / Kata / Firecracker comparison (Onidel)](https://onidel.com/blog/gvisor-kata-firecracker-2025)

- **Kata Containers**: each container (or pod) runs in a **lightweight VM** (guest kernel), giving hardware-level isolation vs host kernel; higher baseline memory and startup cost than runc; good when untrusted tenants justify VM boundaries.  
  Sources: [Northflank comparison](https://northflank.com/blog/kata-containers-vs-firecracker-vs-gvisor), [Quantitative comparison paper (SciTePress PDF)](https://www.scitepress.org/Papers/2021/104405/104405.pdf)

- Empirical paper (2021) reported **Docker smallest RAM footprint** among compared setups, **gVisor ~7× Docker** in one busybox measurement (~40MB gVisor vs ~few MB class for Docker in that experiment’s framing), **Kata ~88× Docker** due to QEMU/Firecracker guest stack — illustrates **steep RAM scaling** for VM-based per-task isolation on small VPS.  
  Source: [SciTePress PDF — comparative performance](https://www.scitepress.org/Papers/2021/104405/104405.pdf)

---

## 2) Practical patterns for per-task shell / filesystem / network policy

| Concern | Pattern | Notes |
|--------|---------|--------|
| **Shell / process** | Run agent-driven commands as **child of a supervisor** that sets namespaces and kills the whole tree (`bwrap --die-with-parent`, Firejail lifecycle, `docker run --rm`, systemd scope) | Avoid orphaned agent processes; pin cgroup limits per task. |
| **Filesystem** | **Whitelist mounts**: only project dir + toolchain read-only (`bwrap --ro-bind /usr /usr` + bind workspace); or Docker volume for workspace; avoid mounting `$HOME` or Docker socket | Red Guild pattern: tmpfs workspace or tightly scoped `workspaceMount`. [The Red Guild](https://blog.theredguild.org/where-do-you-run-your-code-part-ii-2/) |
| **Network** | **Offline by default**: `bwrap --unshare-net`, Firejail `--net=none`, Docker internal network / no `host` network / block egress with firewall or proxy allowlist | Add a second “online” task profile when package install or API calls are needed. |
| **Policy as code** | Firejail **profiles** per task type; **bwrap argv templates** generated by your runner; Docker **compose overrides** or `run` args per job | Same agent, different profiles: `build-offline`, `test-networked`, etc. |
| **Identity** | Non-root user in container; `--security-opt no-new-privileges`; drop caps; rootless daemon where feasible | [VS Code devcontainer.json reference](https://code.visualstudio.com/docs/devcontainers/devcontainerjson-reference) |

---

## 3) Trade-offs — solo operator, ~4GB RAM VPS

- **runc Docker/Podman (one container per task)** — Typical choice: predictable tooling, image cache amortizes disk; pay **daemon + shim + image working set** per concurrent task. Rootless avoids root daemon but can cost **network/FUSE** overhead on small VPS disks and NICs.  
  Sources: [usulnet rootless](https://articles.usulnet.com/articles/docker-rootless-mode.html), [usulnet Podman vs Docker](https://articles.usulnet.com/articles/podman-vs-docker)

- **Firejail / bubblewrap** — **Very low incremental RAM** vs full OS containers for simple command sandboxes; faster spin-up; you **engineer policy yourself** (especially bwrap). Firejail’s SUID model is powerful but is a different trust base than user-ns-only tools.  
  Sources: [bubblewrap README](https://github.com/containers/bubblewrap), [firejail man](https://manpages.ubuntu.com/manpages/jammy/man1/firejail.1.html)

- **gVisor** — Extra per-sandbox memory for Sentry; syscall overhead on I/O-heavy agent workflows (install, test, large git). Still far lighter than Kata for **many short-lived tasks** on 4GB.  
  Sources: [Northflank](https://northflank.com/blog/kata-containers-vs-firecracker-vs-gvisor), [Onidel](https://onidel.com/blog/gvisor-kata-firecracker-2025)

- **Kata / full microVM per task** — Strongest isolation; **poor fit for 4GB** if you need **multiple concurrent** sandboxes or large dev images — guest kernel + VMM overhead dominates. Better as rare “paranoid” lane than default.  
  Sources: [SciTePress PDF](https://www.scitepress.org/Papers/2021/104405/104405.pdf), [Northflank](https://northflank.com/blog/kata-containers-vs-firecracker-vs-gvisor)

- **Devcontainers** — Great for **reproducible dev stacks** and human IDE flows; for **untrusted agent code**, treat as “Docker with extra JSON,” focusing on **mount minimization**, **non-privileged** settings, and **network egress** policy.  
  Sources: [VS Code devcontainer reference](https://code.visualstudio.com/docs/devcontainers/devcontainerjson-reference), [The Red Guild](https://blog.theredguild.org/where-do-you-run-your-code-part-ii-2/)

---

## V1 recommendations (3 lines)

**Pilot:** One **disposable Docker/Podman container per task**, minimal image, **non-root**, no `--privileged`, no host network, **workspace-only** mount, **default-deny egress** (separate allowlisted step when needed), and **1–2 concurrent tasks max** on ~4GB; rootful single-tenant daemon is acceptable if rootless FUSE/slirp cost hurts your workload.

**Stricter v1:** Same shape, but **rootless** engine where reliable, **`no-new-privileges`** + tighter seccomp/LSM, **read-only rootfs** when compatible, explicit **offline vs online** run profiles; use **gVisor** (or a rare full VM) only for exceptional trust boundaries — **not Kata-per-task** as default on 4GB.

**Shared rule:** Implement policy as **named, versioned profiles** (generated `bwrap` argv, Firejail profile, or `docker run` preset) so every agent task gets a deterministic **fs + net + shell** contract.
