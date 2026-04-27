# Memory Service Bootstrap (T089)

Bootstrap `mcp-memory-service` in sqlite_vec mode for the overnight pilot.

---

## 1) Purpose

Establish a local-first memory layer that:

- persists cross-run learning entries,
- supports deterministic health checks at startup,
- provides a reproducible service contract for US3 flows.

This runbook focuses on the pilot baseline only (sqlite_vec backend).

---

## 2) Prerequisites

- VPS baseline complete (T055-T063)
- Python 3.12+ available
- Repo checkout present at `~/night_coder`
- Operator shell under `deploy` user

---

## 3) Service paths and contract

Use these canonical pilot paths:

- Memory DB: `/home/deploy/night_coder/.state/memory/memory.sqlite3`
- Memory logs: `/home/deploy/night_coder/.state/memory/logs/`
- Config env file: `/home/deploy/night_coder/.state/memory/memory.env`

Minimum startup contract:

- Service starts without cloud credentials.
- Read/write operations succeed against sqlite_vec DB path.
- Health check returns non-error status within 3 seconds.

---

## 4) Bootstrap steps

```bash
mkdir -p /home/deploy/night_coder/.state/memory/logs
touch /home/deploy/night_coder/.state/memory/memory.env
```

Create environment file:

```bash
cat > /home/deploy/night_coder/.state/memory/memory.env << 'EOF'
MEMORY_BACKEND=sqlite_vec
MEMORY_DB_PATH=/home/deploy/night_coder/.state/memory/memory.sqlite3
MEMORY_NAMESPACE=pilot
EOF
```

Start memory service (example):

```bash
set -a
source /home/deploy/night_coder/.state/memory/memory.env
set +a
mcp-memory-service > /home/deploy/night_coder/.state/memory/logs/service.log 2>&1
```

---

## 5) Health check

Expected startup health check command pattern:

```bash
python - <<'PY'
import sqlite3
db = "/home/deploy/night_coder/.state/memory/memory.sqlite3"
conn = sqlite3.connect(db)
conn.execute("CREATE TABLE IF NOT EXISTS healthcheck (id INTEGER PRIMARY KEY, ts TEXT)")
conn.execute("INSERT INTO healthcheck (ts) VALUES (datetime('now'))")
conn.commit()
print("ok")
PY
```

Expected output: `ok`

---

## 6) Backup and restore (pilot)

Backup:

```bash
cp /home/deploy/night_coder/.state/memory/memory.sqlite3 \
  /home/deploy/night_coder/.state/memory/memory.sqlite3.bak
```

Restore test:

```bash
cp /home/deploy/night_coder/.state/memory/memory.sqlite3.bak \
  /home/deploy/night_coder/.state/memory/memory.sqlite3.restore-test
sqlite3 /home/deploy/night_coder/.state/memory/memory.sqlite3.restore-test ".tables"
```

---

## 7) Validation checklist

- [ ] sqlite_vec memory DB path exists and is writable by `deploy`.
- [ ] Memory service process starts with no cloud credentials.
- [ ] Health check completes successfully.
- [ ] One write + one read operation confirmed.
- [ ] Backup file created and restore drill executed.

---

## 8) References

- `docs/superpowers/pilot/memory/IMPLEMENTATION-BRIEF.md`
- `specs/001-overnight-vps-system/tasks.md` (`T089`)
