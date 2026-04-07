# Findings: mcp-memory-service vs YAMS (Memory Pillar Candidates)

## Scope

Comparison focused on:
- persistence model
- retrieval capabilities
- operational burden
- fit for self-hosted overnight agent workflows

## Candidate A: mcp-memory-service

### Persistence model
- Multi-backend architecture with `sqlite_vec`, `cloudflare`, `hybrid`, plus `http_client`; `chroma` is marked deprecated for removal in a future major release.
- `sqlite_vec` is local-first persistence (SQLite + vector extension), with configurable DB path and pragmas.
- `hybrid` combines local SQLite reads with Cloudflare-backed sync/backup semantics for multi-device continuity.
- Environment-driven configuration with OS-default base dirs and auto-created data paths.

### Retrieval capabilities
- Exposes semantic retrieval (`retrieve_memory`), time-based recall (`recall_memory`), tag search, and exact-match-style debug retrieval interfaces.
- Designed around embedding-based memory lookup plus metadata/tag filtering.
- Includes export/import and DB health/optimization operations useful for lifecycle maintenance.

### Operational burden
- Higher configuration surface area than purely local tools (backend selection, optional HTTP/API key, optional TLS, optional mDNS, optional Cloudflare credentials).
- Potentially lower day-2 burden if run in local-only SQLite mode; higher burden in hybrid/cloud modes due to external service dependencies and secret management.
- Built-in HTTP/web dashboard and multi-client options can simplify observability/access but add runtime components.

### Fit for self-hosted overnight agents
- Strong fit when you need durable cross-run semantic memory with optional multi-device sync and richer service-style interfaces.
- Better for workflows needing memory as an MCP/API service shared across tools/processes.
- Trade-off: more moving parts than a single local binary, especially if cloud/hybrid features are enabled.

## Candidate B: YAMS

### Persistence model
- Content-addressed storage (SHA-256) with block-level dedupe and WAL-backed durability claims.
- Local storage root is explicit/configurable (`YAMS_STORAGE` / `--storage`) and initialized via `yams init`.
- Snapshot model (Merkle-tree diffs, snapshot listing/history) emphasizes versioned corpus state, useful for project-memory evolution.
- Project currently labels itself experimental / not production-ready in README.

### Retrieval capabilities
- Hybrid search model (keyword/FTS5 + semantic + fuzzy options), regex search (`grep`), hash retrieval (`get`), list/snapshot operations.
- MCP surface intentionally compressed into 3 composite tools (`query`, `execute`, `session`) with many operations behind them.
- Includes context-suggestion and semantic dedupe-oriented operations in MCP docs/CLI docs.

### Operational burden
- Local-first deployment is straightforward (`yams serve` or Docker `serve`) with stdio MCP transport.
- Requires initial indexing/ingestion discipline (`yams add`, optional watch/session lifecycle) to maintain high retrieval quality.
- Plugin ecosystem (embeddings/storage/extraction) adds flexibility but increases operational complexity when enabled.
- Experimental maturity warning increases risk for unattended overnight production workloads.

### Fit for self-hosted overnight agents
- Strong fit as a local memory substrate for code/document corpora with strong dedupe + snapshot semantics.
- Good for single-node/self-hosted workflows prioritizing local control and retrieval breadth (search/grep/hash/snapshots).
- Risk factor: experimental status; best treated as a promising v1/v1.5 substrate with guardrails, backups, and rollback plan.

## Direct comparison against selection criteria

### Persistence model
- **mcp-memory-service:** service-oriented semantic memory with backend abstraction and optional cloud sync.
- **YAMS:** local content-addressed corpus memory with snapshot/version semantics and dedupe.
- **Implication:** choose mcp-memory-service for "memory service" behavior; choose YAMS for "memory filesystem/database" behavior.

### Retrieval capabilities
- **mcp-memory-service:** memory-native semantic/time/tag retrieval APIs.
- **YAMS:** broader corpus retrieval toolbox (hybrid search, regex, hash get, snapshots), less "memory primitive"-centric.
- **Implication:** if temporal recall and memory-centric ops are core, mcp-memory-service is more direct; if corpus exploration/reconstruction is central, YAMS is stronger.

### Operational burden
- **mcp-memory-service:** broader config/runtime surface; can be light in local SQLite mode, heavier in hybrid/cloud/server modes.
- **YAMS:** simpler local runtime, but indexing/session discipline and plugin management matter; experimental status is an operational risk multiplier.

### Overnight self-hosted fit
- **Safer conservative pick today:** mcp-memory-service in local `sqlite_vec` mode (minimal external dependencies) if you need semantic memory service semantics now.
- **High-upside local substrate pick:** YAMS if your overnight agents are heavily codebase/document-centric and you can tolerate experimental churn with strict operational guardrails.

## Suggested v1 decision framing

- **Primary candidate (service-style memory pillar):** mcp-memory-service (`sqlite_vec` first, evaluate hybrid later).
- **Fallback / parallel pilot (local corpus memory pillar):** YAMS in a constrained, non-critical lane until stability confidence improves.
- **No-go trigger for YAMS:** unacceptable breakage/churn due to experimental changes during unattended runs.
- **No-go trigger for mcp-memory-service hybrid mode:** cloud dependency/credential issues causing overnight reliability regressions.

## Key source URLs

### mcp-memory-service
- GitHub repo: https://github.com/doobidoo/mcp-memory-service
- README: https://raw.githubusercontent.com/doobidoo/mcp-memory-service/main/README.md
- Architecture: https://raw.githubusercontent.com/doobidoo/mcp-memory-service/main/docs/architecture.md
- Configuration guide: https://raw.githubusercontent.com/doobidoo/mcp-memory-service/main/docs/mastery/configuration-guide.md

### YAMS
- GitHub repo: https://github.com/trvon/yams
- README: https://raw.githubusercontent.com/trvon/yams/main/README.md
- MCP guide: https://yamsmemory.ai/user_guide/mcp/
- CLI guide: https://yamsmemory.ai/user_guide/cli/
