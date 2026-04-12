# Container runtime (pilot) — T057

Install and validate a **container runtime** on the overnight VPS for Docker/Podman-based tooling (orchestrator, DTU mocks, compose stacks).

**OS:** Ubuntu 24.04 LTS (noble), x86_64. **Operator user:** `deploy` (sudo-capable), per `vps-bootstrap.md`.

**Prerequisites:** T056 complete (Python 3.12+, git, tmux, curl, jq on the Droplet).

Do not commit registry passwords, `.env` files with secrets, or kubeconfigs to this repo.

---

## 1. Goals

| Goal | Detail |
|------|--------|
| **Runnable containers** | Pull a small image and run it without root login. |
| **Rootless-by-default** | Prefer **no** daemon running as root for routine pulls/runs (see paths below). |
| **Reproducible** | Commands below are copy-pasteable; record any host-specific fixes in a private note. |

---

## 2. Choose a path (pilot recommendation)

| Path | When to use | Notes |
|------|----------------|------|
| **A — Podman (rootless)** | **Default for this pilot.** Matches “rootless profile”; no `docker` group (root-equivalent socket) required. | Packages from Ubuntu; good fit for `deploy` user. |
| **B — Docker (rootless)** | You need Docker CLI/socket compatibility and true rootless. | Follow Docker’s rootless install; slightly more moving parts. |
| **C — Docker (daemon + `docker` group)** | You need classic `docker compose` and accept **group-based** access to the Docker socket. | **Security:** users in `docker` can effectively escalate to root; use only if you understand that tradeoff. |

**Recommendation:** Complete **Path A** first. Add B or C only if something in the stack hard-requires Docker.

---

## 3. Path A — Podman (rootless)

### 3.1 Install packages

SSH to the Droplet as `deploy`, then:

```bash
sudo apt update
sudo apt install -y podman slirp4netns uidmap fuse-overlayfs
```

- **slirp4netns** — user-mode networking for rootless containers.  
- **uidmap** — subordinate UIDs/GIDs for user namespaces.  
- **fuse-overlayfs** — overlay storage where needed.

### 3.2 Subordinate IDs (if `podman info` errors about subuid/subgid)

Ubuntu usually allocates `/etc/subuid` and `/etc/subgid` entries for new users. If not:

```bash
grep "^deploy:" /etc/subuid /etc/subgid
```

If missing (example only — IDs must not collide with existing entries):

```bash
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 deploy
```
(Use a free range; avoid overlapping existing entries in `/etc/subuid` / `/etc/subgid`.)

Then log out and SSH back in (or `newuidmap` / new session).

### 3.3 Enable lingering (recommended for unattended)

Allows user services (and sometimes rootless Podman) to run after logout:

```bash
sudo loginctl enable-linger deploy
loginctl show-user deploy | grep Linger
```

### 3.4 Validate

```bash
podman --version
podman info
```

Smoke test (pull + run):

```bash
podman run --rm quay.io/podman/hello
```

**Expected:** Hello message or successful exit code 0; no “permission denied” on the storage graph.

### 3.5 Compose

Multi-container definitions (WireMock, future stacks):

```bash
sudo apt install -y podman-compose
# or: pipx install podman-compose  (if you standardize on pipx later)
```

Validate:

```bash
podman-compose version
```

Use `podman-compose` / `podman play kube` per stack docs; keep compose files out of secret-bearing paths.

---

## 4. Path B — Docker (rootless)

Use when you must match Docker’s rootless model (official guide).

1. Install Docker Engine per [Rootless mode](https://docs.docker.com/engine/security/rootless/) (install script or packages).  
2. Configure systemd user services as documented (`dockerd-rootless-setuptool.sh install` or equivalent).  
3. Set `DOCKER_HOST` in operator shell profile if required:

```bash
export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock
```

4. Validate:

```bash
docker version
docker run --rm hello-world
```

**Expected:** `Hello from Docker!` style output.

---

## 5. Path C — Docker (daemon + `docker` group) — use with care

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker deploy
```

Log out and SSH back in so group membership applies.

```bash
docker run --rm hello-world
docker compose version
```

**Warning:** Any user in group `docker` can trivially obtain root on the host. Prefer Path A or B for guardrail-sensitive pilots.

---

## 6. DigitalOcean firewall reminder

Outbound HTTPS (443) must work for image pulls. Your Cloud Firewall should allow egress (pilot default). Inbound **only** SSH (and app ports you need); nothing extra required specifically for Podman/Docker unless you publish container ports.

---

## 7. Troubleshooting (short)

| Symptom | Things to check |
|---------|-------------------|
| `cannot clone: permission denied` (storage) | `podman system migrate` after subuid fix; disk space `df -h`. |
| Network timeout pulling images | DNS (`resolvectl status`), egress 443, registry status. |
| `cgroup` / `cgroups` errors | Ubuntu 24.04 uses cgroup v2; ensure no legacy cgroup v1 force. |
| Rootless Docker: socket not found | `DOCKER_HOST`, `systemctl --user status docker`. |

---

## 8. T057 completion checklist

- [x] Path chosen (A recommended) and packages installed.  
- [x] `podman info` succeeds as **`deploy`** without sudo.  
- [x] Pull/run smoke test succeeds (`quay.io/podman/hello` or equivalent).  
- [x] Linger enabled for user `deploy` (`loginctl enable-linger`).  
- [x] `podman-compose` installed and `podman-compose version` works.  
- [x] Pilot recorded in revision table below.

---

## 9. Agent / operator hand-off

- **Pilot stack:** Path **A** (rootless Podman) + **linger** + **podman-compose**. T058 (`vps-ralph-install.md`) assumes this runtime unless you switch to Docker.  
- Do not commit image pull secrets; use registry auth via env or Doppler inject (T059).

---

## References

- [Podman rootless tutorial (upstream)](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md)  
- [Docker rootless mode](https://docs.docker.com/engine/security/rootless/)  
- Prior step: [`vps-bootstrap.md`](./vps-bootstrap.md)

---

## Revision

| Date | Notes |
|------|--------|
| 2026-04-11 | Initial T057 runbook: Podman rootless (recommended), Docker rootless and docker.io alternatives, validation and troubleshooting. |
| 2026-04-11 | Pilot complete: Path A, `loginctl enable-linger deploy`, `podman-compose` installed; checklist §8 marked done. |

---

## Next runbook

- [T058 — Ralph orchestrator](./vps-ralph-install.md)
