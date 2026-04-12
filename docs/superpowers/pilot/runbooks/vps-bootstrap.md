# VPS bootstrap (pilot)

Reproducible baseline for the overnight VPS coding system pilot. **Provider used:** DigitalOcean. **OS:** Ubuntu 24.04 LTS (noble), x86_64.

Do not commit SSH private keys, API tokens, or passwords. Use placeholders below.

---

## 1. Instance profile

| Item | Choice (pilot) |
|------|----------------|
| Provider | DigitalOcean Droplets |
| Plan | Basic — **4 GiB RAM / 2 vCPU** (~USD 24/mo cap); Regular SSD |
| Region | **Sydney** (`syd1`) — pick nearest/low-latency region for operator |
| Auth | SSH public key only at create time (no password login for `root` in panel) |
| Backups | Off for pilot (enable later if needed) |

**Why this size:** Enough RAM for OS + container runtime + orchestration without constant OOM pressure; stays under typical student/credit budgets.

---

## 2. SSH keys (operator workstation)

Generate a key pair on the machine you use to connect (**not** on the Droplet):

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
ssh-keygen -t ed25519 -C "night-coder-do" -f ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
```

Add **only** the **public** key (`~/.ssh/id_ed25519.pub`) in DigitalOcean: **Account → Settings → Security → SSH keys**.

**Connect from the same user account that owns the private key**, or specify identity explicitly:

```bash
ssh -i ~/.ssh/id_ed25519 deploy@YOUR_DROPLET_IPV4
```

**Common mistake:** Running `ssh` as a different local user looks for keys under *that* user’s `~/.ssh/`. If `Permission denied (publickey)`, use `-i` pointing at the correct private key, or run SSH as the user who owns the key.

Use full path if needed:

```bash
/usr/bin/ssh-keygen -t ed25519 -C "night-coder-do" -f "$HOME/.ssh/id_ed25519"
```

---

## 3. Networking: Cloud Firewall (DigitalOcean)

Create a **Cloud Firewall** and attach the Droplet.

**Inbound (typical pilot):**

| Type | Ports | Sources |
|------|-------|---------|
| SSH | 22/TCP | **Your public IP only** (refresh if your ISP changes IP) |
| HTTP/HTTPS | 80, 443/TCP | Only if serving web traffic from this host |

**Outbound:** Permissive (all TCP/UDP to IPv4/IPv6) is acceptable for a dev pilot so `apt`, `git`, HTTPS APIs, and Docker pulls work. Tighten egress later if policy requires it.

**Reserved IP:** Optional IPv4 reserved address for a stable endpoint when replacing Droplets; not required for first bootstrap.

---

## 4. First login and non-root operator

1. SSH as `root` once (key-based): `ssh root@YOUR_DROPLET_IPV4`
2. Create sudo user (example name `deploy`):

```bash
adduser deploy
usermod -aG sudo deploy
```

3. Install **same** authorized key for `deploy`:

```bash
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
cp /root/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
chown deploy:deploy /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys
```

4. **Before** closing `root` session: open a **second** terminal on your workstation and verify:

```bash
ssh -i ~/.ssh/id_ed25519 deploy@YOUR_DROPLET_IPV4
sudo whoami   # expect: root
```

---

## 5. SSH daemon hardening

Edit `/etc/ssh/sshd_config` (and snippets under `/etc/ssh/sshd_config.d/` if present):

- `PasswordAuthentication no`
- `KbdInteractiveAuthentication no`
- Optional: `PermitRootLogin no` **after** `deploy` key login works

Validate and apply:

```bash
sudo sshd -t
sudo systemctl restart ssh
```

On Ubuntu the unit is usually `ssh` (try `sshd` if `restart ssh` fails).

---

## 6. Host firewall (UFW)

Align with Cloud Firewall; defense in depth.

```bash
sudo apt update
sudo apt install -y ufw
sudo ufw allow OpenSSH
# If serving HTTP/S from this host:
# sudo ufw allow 80/tcp
# sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

**Critical:** Allow **OpenSSH** before `ufw enable`, or you can lock out SSH.

---

## 7. OS updates and automatic security patches

```bash
sudo apt update
sudo apt upgrade -y
```

Optional reboot after kernel updates:

```bash
sudo reboot
```

**Unattended security updates (Ubuntu 24.04):**

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

Confirm periodic config exists (`/etc/apt/apt.conf.d/20auto-upgrades`) and dry-run is clean:

```bash
sudo unattended-upgrades --dry-run --debug
```

---

## 8. Recovery: `Connection refused` on port 22 after reboot

Usually **`sshd` not listening** (failed start) or still booting.

1. Wait 1–3 minutes and retry SSH from your workstation.
2. Use **DigitalOcean Droplet Console** (browser) — does not need SSH.
3. On the Droplet:

```bash
sudo systemctl status ssh --no-pager
sudo journalctl -u ssh -b --no-pager -n 80
sudo ss -tlnp | grep ':22'
sudo sshd -t && sudo systemctl start ssh && sudo systemctl enable ssh
```

Fix any `sshd_config` error until `sshd -t` passes, then `sudo systemctl restart ssh`.

---

## 9. Agent hand-off (follow-up)

Next agent should complete these **without** storing secrets in git:

| # | Action |
|---|--------|
| 1 | From operator workstation, confirm `ssh deploy@YOUR_DROPLET_IPV4` (or `-i` as documented) succeeds; document any operator-specific quirk in a local note (not committed). |
| 2 | Mark **T055** satisfied in `specs/001-overnight-vps-system/tasks.md` if not already; proceed to **T056** (runtime prerequisites) using commands recorded in this file’s companion sections as needed. |
| 3 | Append **T056** install commands to this runbook as they are executed (Python 3.12+, git, tmux, curl, jq) per tasks list. |
| 4 | Verify billing alerts enabled in DO for credit/card safety (user setting; do not paste thresholds in repo). |
| 5 | Before **T060** (WireMock / pilot `dtu/` compose), complete **[§12](#12-pilot-repository-checkout-on-the-vps)** so the Droplet has a checkout of this repo (Ralph **T058** alone does not clone it). |

**References (external):**

- [DigitalOcean Droplet pricing](https://www.digitalocean.com/pricing/droplets)
- [DigitalOcean billing alerts](https://docs.digitalocean.com/platform/billing/billing-alerts/)
- [Ubuntu unattended-upgrades](https://help.ubuntu.com/community/AutomaticSecurityUpdates)

---

## 10. Operator SSH verification

### 10.1 End-to-end check (your Droplet)

Use the same identity and host pattern as in [§4](#4-first-login-and-non-root-operator). Replace `YOUR_DROPLET_IPV4` with your Droplet public IPv4 **only on the command line** — do not commit real addresses, keys, or tokens to git.

```bash
ssh -i ~/.ssh/id_ed25519 deploy@YOUR_DROPLET_IPV4
sudo whoami   # expect: root
exit
```

If you see `Permission denied (publickey)`, use `-i` with the path to the private key for this pilot, or run SSH as the user who owns `~/.ssh/id_ed25519` (see [§2](#2-ssh-keys-operator-workstation)).

### 10.2 Operator workstation sanity (local, no remote host required)

These checks confirm the **operator machine** has an SSH client and the expected key path before connecting. They do **not** replace §10.1.

```bash
ssh -V
test -f ~/.ssh/id_ed25519 && echo "identity key present"
```

**Example output (Ubuntu 24.04 operator):** `OpenSSH_9.6p1` (or similar) and `identity key present`.

---

## 11. T056 — Runtime prerequisites (Python 3.12+, git, tmux, curl, jq)

Run **on the VPS** as a user with `sudo` (e.g. `deploy`) after SSH from the operator machine succeeds.

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip git tmux curl jq
```

Validate installs:

```bash
python3.12 --version
python3.12 -m pip --version
git --version
tmux -V
curl --version | head -n1
jq --version
```

**Expected:** `python3.12` reports 3.12.x or newer; `git`, `tmux`, `curl`, and `jq` print version strings without errors.

---

## 12. Pilot repository checkout on the VPS

**Why this section exists:** **T055–T059** (SSH, packages, Podman, Ralph CLI, Doppler) can all be completed **without** a copy of this repository on the Droplet — Ralph installs from upstream release/npm/cargo, not from `night_coder` paths. **T060 and later pilot runbooks** expect files that live **in git** here (for example `docs/superpowers/pilot/dtu/docker-compose.wiremock.yml`). If those paths are missing on the VPS, **nothing earlier in the runbook set failed**; the gap is simply **no checkout yet**.

**When:** After [§11](#11-t056--runtime-prerequisites-python-312-git-tmux-curl-jq) (`git` works). **Before** [`vps-dependency-smoke-tests.md`](./vps-dependency-smoke-tests.md) (T060).

**What “checkout” means:** A normal **`git clone`** (or `git pull` into an existing clone) of **this** repo — **not** `git init` on an empty folder.

### 12.1 Clone into a predictable directory

As `deploy` on the Droplet, clone the **same remote you use on your laptop** (the canonical `night_coder` repo if you own it — **no GitHub fork is required**). Use a **fork’s URL** only if that is already your normal workflow (e.g. PRs into an upstream you do not own). Use **SSH** or **HTTPS** depending on how the Droplet authenticates to GitHub.

```bash
cd ~
# Example — replace with your real clone URL (user/org repo is fine; fork URL only if you use forks):
git clone --depth 1 https://github.com/YOUR_USER_OR_ORG/night_coder.git night_coder
```

**Private repository:** use a [deploy key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys/deploy-keys) (read-only) or HTTPS with a **credential helper / token** — never commit keys or embed tokens in the clone URL inside this repo’s docs.

### 12.2 Verify paths used by later runbooks

```bash
export NIGHT_CODER_ROOT="$HOME/night_coder"
test -f "$NIGHT_CODER_ROOT/docs/superpowers/pilot/dtu/docker-compose.wiremock.yml" \
  && echo "OK: WireMock compose present"
```

**Expected:** `OK: WireMock compose present`.

Optional — persist the variable for interactive shells:

```bash
grep -q 'NIGHT_CODER_ROOT=' ~/.bashrc 2>/dev/null || echo 'export NIGHT_CODER_ROOT="$HOME/night_coder"' >> ~/.bashrc
```

### 12.3 Updating the checkout

**`git pull` must be run inside the clone**, not from `$HOME`. From `~` you will see `fatal: not a git repository` — that is expected until you `cd` into the repo.

```bash
cd "$HOME/night_coder"   # or: cd "$NIGHT_CODER_ROOT" after sourcing ~/.bashrc
git status               # optional: confirm you are on the branch you expect
git pull
```

Pilot runbooks assume you can **`git pull`** (or your approved update mechanism) when compose files or mappings change on `main` / your tracking branch.

---

## Revision

| Date | Notes |
|------|--------|
| 2026-04-11 | Initial pilot bootstrap from DigitalOcean + Ubuntu 24.04 operator setup. |
| 2026-04-11 | §10 operator SSH verification; §11 T056 runtime prerequisites (apt + version checks). |
| 2026-04-12 | §12 pilot repository checkout on the VPS (prerequisite for T060+ paths); §9 hand-off row 5. |
| 2026-04-12 | §12.1: clarify clone canonical repo when you own it; fork URL only if that is your workflow. |
| 2026-04-12 | §12.3: explicit `cd` into clone before `git pull`; note fatal error from `~`. |
