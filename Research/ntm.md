# DeepWiki Q&A with Code Context for Repository: Dicklesworthstone/ntm
## Q1
I'm working on a autonomous agent scaffold so I can run agents at night and review work in the morning. Would ntm assist in managing the pieces I have thus far? Would this be a good fit to build upon my desired workflow? Why/why not? 1. **Attractor (Orchestrator)**: A minimal guide that takes the agents through structured phases (e.g., design → implement → test → refactor), acting as a high‑level blueprint for autonomous execution. 2. **CXDB (Context & Trace Store)**: A database that records every agent action, tool call, and execution trace, providing a shared memory for agents and a complete audit trail for human review. 3. **Leash (Guardrails)**: A safety layer that intercepts and restricts dangerous commands (e.g., `rm -rf /`, excessive API calls), preventing agents from damaging the project or environment. 4. **Digital Twin Universe (DTU)**: High‑fidelity, in‑memory clones of external services (like Okta, Slack) used to run thousands of scenarios safely and scalably, eliminating dependency on live APIs and preventing reward hacking. 5. **LLM Judge**: An evaluator that reviews execution outcomes against human‑written scenarios and specs, producing a probabilistic “satisfaction” score rather than relying on easily gamed tests. These components work together to enable **non‑interactive development**—the system can iterate overnight, with you only reviewing the final results and satisfaction reports in the morning.
### Answer
# Assessment: ntm as Foundation for Autonomous Agent Scaffold

Based on my analysis of the `ntm` codebase, here's how it maps to your autonomous agent scaffold components:

## Strong Matches (2/5 components)

### ✅ CXDB (Context & Trace Store) - Excellent Fit

ntm provides comprehensive audit trail and state management capabilities:

- **Tamper-evident audit logging**: Every significant action (spawn, send, state change) is logged with timestamps, correlation IDs, and hash-chain integrity ntm:1-50 

- **Complete session state capture**: Records agents, panes, layout, git context, and can restore sessions from snapshots ntm:1-50 

- **Timeline tracking**: Records agent state transitions (idle→working→error) with duration metrics and event details ntm:1-50 

- **Queryable audit logs**: CLI commands for searching and verifying audit history ntm:1-30 

This provides the complete execution trace and shared memory your CXDB component requires.

### ✅ Leash (Guardrails) - Excellent Fit

ntm has a multi-layered safety system specifically designed to prevent dangerous commands:

- **Policy engine**: Defines blocked, approval-required, and allowed commands using regex patterns ntm:1-50 

- **Protected patterns**: Blocks `git reset --hard`, `git push --force`, `rm -rf /`, `DROP DATABASE`, etc. ntm:1-50 

- **PATH-based interception**: Wrapper scripts that check commands before execution ntm:17-19 

- **Destructive Command Guard integration**: Additional external safety layer ntm:1-30 

This directly addresses your Leash requirement for restricting dangerous operations.

## Partial Match (1/5 components)

### ⚠️ Attractor (Orchestrator) - Partial Fit

ntm has orchestration capabilities, but they're not designed for autonomous phase-based workflows:

- **Pipeline orchestrator**: Executes YAML/TOML-defined workflows through phases (initialization → dependency resolution → step execution → finalization) ntm:1-50 

- **Swarm orchestrator**: Coordinates agent swarms through session creation → agent launch → prompt injection phases ntm:1-50 

However, these orchestrators are built for *coordinating multiple agents* rather than *guiding agents through development phases* (design → implement → test → refactor). The orchestration is more about session management than workflow progression.

## No Match (2/5 components)

### ❌ DTU (Digital Twin Universe) - Not Available

ntm does not provide any service virtualization, mocking, or test environment capabilities. It operates on real systems with real agents.

### ❌ LLM Judge - Not Available

ntm has no evaluation or outcome judging system. It focuses on orchestration and monitoring, not on assessing quality or satisfaction scores.

## Critical Incompatibility: Non-Interactive Development

The fundamental issue is that **ntm is designed for human-in-the-loop interactive workflows**, not autonomous overnight execution:

- The core value proposition is "spawn, manage, and coordinate Claude Code, OpenAI Codex, and Google Gemini CLI agents across tiled tmux panes" ntm:17-19 

- The typical workflow involves human operators sending prompts, monitoring dashboards, copying outputs, and intervening as needed ntm:1900-1997 

- While it has robot mode (`--robot-*` flags) for programmatic control ntm:30-44 , this is primarily for agent-to-agent coordination, not for fully autonomous execution frameworks.

## Recommendation: **Not a Good Foundation**

### Why Not:

1. **Missing critical components**: No test environment virtualization (DTU), no evaluation system (LLM Judge)
2. **Wrong execution model**: Built for interactive human oversight, not autonomous overnight runs
3. **Scope mismatch**: ntm is a tmux session manager with agent orchestration, not an autonomous development framework

### What ntm IS Good For:

- Managing multiple AI coding agents in parallel during development
- Providing safety guardrails during interactive coding sessions  
- Recording audit trails and session state for later review
- Coordinating agent-to-agent communication (via Agent Mail integration)

### Better Approach:

You would likely benefit more from building your scaffold using:
- A proper workflow engine (Temporal, Airflow, Prefect) for your Attractor
- Your own CXDB implementation (SQLite, PostgreSQL with event sourcing)
- ntm's safety patterns as *reference* for your Leash component
- Custom DTU and Judge implementations specific to your needs

ntm could potentially be used as a *component* for managing agent sessions within your larger framework, but it's not architected to be the foundation for autonomous overnight execution.

## Notes

ntm excels at what it's designed for: providing a "multi-agent command center" for interactive development with strong safety and audit capabilities. However, your requirements for fully autonomous overnight execution with phase-based workflows, service virtualization, and outcome evaluation represent a different problem domain that ntm wasn't built to solve. The architectural assumptions (interactive tmux sessions, human oversight, real-time monitoring) are fundamentally at odds with your "run at night, review in morning" model.
### Citations
**File:** internal/audit/logger.go (L1-50)
```go
package audit

import (
	"bufio"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/Dicklesworthstone/ntm/internal/privacy"
	"github.com/Dicklesworthstone/ntm/internal/redaction"
)

// EventType represents the type of audit event
type EventType string

const (
	EventTypeCommand     EventType = "command"
	EventTypeSpawn       EventType = "spawn"
	EventTypeSend        EventType = "send"
	EventTypeResponse    EventType = "response"
	EventTypeError       EventType = "error"
	EventTypeStateChange EventType = "state_change"
)

// Actor represents who performed the action
type Actor string

const (
	ActorUser   Actor = "user"
	ActorAgent  Actor = "agent"
	ActorSystem Actor = "system"
)

// AuditEntry represents a single audit log entry
type AuditEntry struct {
	Timestamp   time.Time              `json:"timestamp"`
	SessionID   string                 `json:"session_id"`
	EventType   EventType              `json:"event_type"`
	Actor       Actor                  `json:"actor"`
	Target      string                 `json:"target"`
	Payload     map[string]interface{} `json:"payload"`
	Metadata    map[string]interface{} `json:"metadata"`
```
**File:** internal/session/capture.go (L1-50)
```go
package session

import (
	"os"
	"os/exec"
	"strings"
	"time"

	"github.com/Dicklesworthstone/ntm/internal/audit"
	"github.com/Dicklesworthstone/ntm/internal/tmux"
)

// Capture captures the current state of a tmux session.
func Capture(sessionName string) (state *SessionState, err error) {
	correlationID := audit.NewCorrelationID()
	auditStart := time.Now()
	_ = audit.LogEvent(sessionName, audit.EventTypeCommand, audit.ActorSystem, "session.capture", map[string]interface{}{
		"phase":          "start",
		"session":        sessionName,
		"correlation_id": correlationID,
	}, nil)
	defer func() {
		payload := map[string]interface{}{
			"phase":          "finish",
			"session":        sessionName,
			"success":        err == nil,
			"duration_ms":    time.Since(auditStart).Milliseconds(),
			"correlation_id": correlationID,
		}
		if state != nil {
			payload["panes"] = len(state.Panes)
			payload["agents"] = state.Agents.Total()
			payload["layout"] = state.Layout
			payload["work_dir"] = state.WorkDir
		}
		if err != nil {
			payload["error"] = err.Error()
		}
		_ = audit.LogEvent(sessionName, audit.EventTypeCommand, audit.ActorSystem, "session.capture", payload, nil)
	}()

	session, err := tmux.GetSession(sessionName)
	if err != nil {
		return nil, err
	}

	panes, err := tmux.GetPanes(sessionName)
	if err != nil {
		return nil, err
	}
```
**File:** internal/state/timeline.go (L1-50)
```go
// Package state provides durable SQLite-backed storage for NTM orchestration state.
// This file implements agent state event tracking for timeline visualization.
package state

import (
	"fmt"
	"sync"
	"time"

	"github.com/Dicklesworthstone/ntm/internal/audit"
)

// TimelineState represents the operational state of an agent in the timeline.
// This differs from AgentStatus as it includes additional states for timeline tracking.
type TimelineState string

const (
	// TimelineIdle indicates the agent is idle with no active work.
	TimelineIdle TimelineState = "idle"
	// TimelineWorking indicates the agent is actively processing a task.
	TimelineWorking TimelineState = "working"
	// TimelineWaiting indicates the agent is waiting for user input or external resource.
	TimelineWaiting TimelineState = "waiting"
	// TimelineError indicates the agent encountered an error.
	TimelineError TimelineState = "error"
	// TimelineStopped indicates the agent/pane was terminated.
	TimelineStopped TimelineState = "stopped"
)

// String returns the string representation of TimelineState.
func (s TimelineState) String() string {
	return string(s)
}

// MarkerType represents the type of discrete event marker on the timeline.
type MarkerType string

const (
	// MarkerPrompt indicates a prompt was sent to the agent (▶).
	MarkerPrompt MarkerType = "prompt"
	// MarkerCompletion indicates the agent finished a task (✓).
	MarkerCompletion MarkerType = "completion"
	// MarkerError indicates an error occurred (✗).
	MarkerError MarkerType = "error"
	// MarkerStart indicates session/agent start (◆).
	MarkerStart MarkerType = "start"
	// MarkerStop indicates session/agent stop (◆).
	MarkerStop MarkerType = "stop"
)

```
**File:** internal/cli/audit.go (L1-30)
```go
package cli

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/spf13/cobra"

	"github.com/Dicklesworthstone/ntm/internal/audit"
	"github.com/Dicklesworthstone/ntm/internal/tui/theme"
)

func newAuditCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "audit",
		Short: "Query and verify audit logs",
		Long: `Query, search, and verify tamper-evident audit logs.

Audit logs record all significant NTM actions with hash-chain integrity.

Examples:
  ntm audit show myproject                  # Show audit log for session
  ntm audit search "spawn"                  # Search all logs
  ntm audit search --type=error --days=7    # Errors in last week
```
**File:** internal/policy/policy.go (L1-50)
```go
// Package policy provides destructive command protection through pattern matching.
package policy

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"gopkg.in/yaml.v3"
)

// DefaultPolicyPath is the default location for the policy file.
const DefaultPolicyPath = ".ntm/policy.yaml"

// Action represents what should happen when a command matches a pattern.
type Action string

const (
	ActionBlock   Action = "block"
	ActionApprove Action = "approve" // requires approval
	ActionAllow   Action = "allow"
)

// Rule represents a single policy rule.
type Rule struct {
	Pattern string `yaml:"pattern"`
	Reason  string `yaml:"reason,omitempty"`
	SLB     bool   `yaml:"slb,omitempty"` // Requires SLB two-person approval
	regex   *regexp.Regexp
}

// AutomationConfig controls automatic operations.
type AutomationConfig struct {
	AutoPush     bool   `yaml:"auto_push"`     // Allow automatic git push
	AutoCommit   bool   `yaml:"auto_commit"`   // Allow automatic git commit
	ForceRelease string `yaml:"force_release"` // "never", "approval", "auto"
}

// Policy represents the complete policy configuration.
type Policy struct {
	Version          int              `yaml:"version"`
	Blocked          []Rule           `yaml:"blocked"`
	ApprovalRequired []Rule           `yaml:"approval_required"`
	Allowed          []Rule           `yaml:"allowed"`
	Automation       AutomationConfig `yaml:"automation"`
}

// Match represents a matched policy rule.
```
**File:** internal/cli/safety.go (L1-50)
```go
package cli

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/charmbracelet/lipgloss"
	"github.com/spf13/cobra"

	"github.com/Dicklesworthstone/ntm/internal/output"
	"github.com/Dicklesworthstone/ntm/internal/policy"
	"github.com/Dicklesworthstone/ntm/internal/tools"
)

func newSafetyCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "safety",
		Short: "Manage destructive command protection",
		Long: `Manage NTM's destructive command protection system.

The safety system blocks or warns about dangerous commands like:
  - git reset --hard (loses uncommitted changes)
  - git push --force (overwrites remote history)
  - rm -rf / (catastrophic deletion)

Use 'ntm safety status' to see current protection status.
Use 'ntm safety blocked' to view blocked command history.
Use 'ntm safety check <command>' to test a command against the policy.`,
	}

	cmd.AddCommand(
		newSafetyStatusCmd(),
		newSafetyBlockedCmd(),
		newSafetyCheckCmd(),
		newSafetyInstallCmd(),
		newSafetyUninstallCmd(),
	)

	return cmd
}

func newSafetyStatusCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "status",
		Short: "Show safety system status",
		RunE:  runSafetyStatus,
```
**File:** README.md (L17-19)
```markdown
**A powerful tmux session management tool for orchestrating multiple AI coding agents in parallel.**

Spawn, manage, and coordinate Claude Code, OpenAI Codex, and Google Gemini CLI agents across tiled tmux panes with simple commands and a stunning TUI featuring animated gradients, visual dashboards, and a beautiful command palette.
```
**File:** README.md (L30-44)
```markdown

## 🤖 Agent Quickstart (Robot Mode)

**Use `--robot-*` output for automation.** stdout = JSON, stderr = diagnostics, exit 0 = success.

```bash
# Triage status (machine-readable)
ntm --robot-status

# List sessions (machine-readable)
ntm --robot-list

# Send prompt to a session (robot API)
ntm --robot-send=myproject --message "Summarize this repo and propose next steps."
```
```
**File:** README.md (L1900-1997)
```markdown

### Workflow Cookbook

#### First run (10 minutes)

1) Install + shell integration (zsh example):

```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/ntm/main/install.sh?$(date +%s)" | bash -s -- --easy-mode
echo 'eval "$(ntm shell zsh)"' >> ~/.zshrc && source ~/.zshrc
```

2) Sanity check + quick orientation:

```bash
# 2) Sanity check + quick orientation
ntm deps -v
ntm tutorial

# 3) Spawn a session and bind the palette popup key (F6 by default)
ntm spawn myapi --cc=2 --cod=1
ntm bind
```

#### Daily loop (attach → palette → send → dashboard → copy/save → detach)

```bash
ntm attach myapi

# Inside the dashboard/palette: press ? for key hints
ntm dashboard myapi
ntm palette myapi

# Useful capture loop
ntm copy myapi --cc --last 200
ntm save myapi -o ~/logs/myapi

# Detach from tmux (agents keep running): Ctrl+B, then D
```

#### SSH flow (remote-first)

```bash
ssh user@host

# Sessions persist on the server
ntm list
ntm attach myapi

# Inside tmux, these auto-select the current session:
ntm dashboard
ntm palette

# If clipboard isn't available on the remote, save to a file instead:
ntm copy myapi --cc --output out.txt
```

#### Troubleshooting patterns (fast fixes)

- No sessions exist: `ntm spawn <name>`
- Icons drift/misaligned gutters: `export NTM_ICONS=ascii`
- Too much motion/flicker: `export NTM_REDUCE_MOTION=1`
- Need plain output / low-color terminal: `export NTM_THEME=plain` (or `export NO_COLOR=1`)
- Copy complains about non-interactive mode: pass a session explicitly (e.g. `ntm copy myapi --cc`)

### Starting a New Project

```bash
# 1. Check if agent CLIs are installed
ntm deps -v

# 2. Create project scaffold (optional)
ntm quick myapi --template=go

# 3. Spawn agents
ntm spawn myapi --cc=3 --cod=2

# 4. You're now attached to the session with 5 agents + 1 user pane
```

### During Development

```bash
# Send task to all Claude agents
ntm send myapi --cc "implement the /users endpoint with full CRUD operations"

# Send different task to Codex agents
ntm send myapi --cod "write comprehensive unit tests for the users module"

# Check status
ntm status myapi

# Zoom to a specific agent to see details
ntm zoom myapi 2

# View all panes
ntm view myapi
```
```
**File:** internal/tools/dcg.go (L1-30)
```go
package tools

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"os/exec"
	"strings"
	"sync"
	"time"
)

// DCGAdapter provides integration with the Destructive Command Guard (dcg) tool.
// DCG blocks dangerous commands like rm -rf, git reset --hard, DROP DATABASE, etc.
// and provides safety guardrails for agent operations.
type DCGAdapter struct {
	*BaseAdapter
}

// NewDCGAdapter creates a new DCG adapter
func NewDCGAdapter() *DCGAdapter {
	return &DCGAdapter{
		BaseAdapter: NewBaseAdapter(ToolDCG, "dcg"),
	}
}

// Detect checks if dcg is installed
func (a *DCGAdapter) Detect() (string, bool) {
```
**File:** internal/pipeline/executor.go (L1-50)
```go
// Package pipeline provides workflow execution for AI agent orchestration.
// executor.go implements the core execution engine for running workflows.
package pipeline

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"log"
	"math"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/Dicklesworthstone/ntm/internal/robot"
	"github.com/Dicklesworthstone/ntm/internal/status"
	"github.com/Dicklesworthstone/ntm/internal/tmux"
	"github.com/Dicklesworthstone/ntm/internal/util"
)

// ExecutorConfig configures the executor behavior
type ExecutorConfig struct {
	Session          string        // Required: tmux session name
	ProjectDir       string        // Optional: project root for .ntm state
	WorkflowFile     string        // Optional: workflow file path for state persistence
	DefaultTimeout   time.Duration // Default step timeout (default: 5m)
	GlobalTimeout    time.Duration // Maximum workflow runtime (default: 30m)
	ProgressInterval time.Duration // Interval for progress updates (default: 1s)
	DryRun           bool          // If true, validate but don't execute
	Verbose          bool          // Enable verbose logging
	RunID            string        // Optional: pre-generated run ID (if empty, one is generated)
}

// MinProgressInterval is the minimum allowed progress interval to prevent ticker panics.
// time.NewTicker requires a positive duration.
const MinProgressInterval = 100 * time.Millisecond

// DefaultExecutorConfig returns sensible defaults
func DefaultExecutorConfig(session string) ExecutorConfig {
	return ExecutorConfig{
		Session:          session,
		DefaultTimeout:   5 * time.Minute,
		GlobalTimeout:    30 * time.Minute,
		ProgressInterval: 1 * time.Second,
		DryRun:           false,
		Verbose:          false,
	}
```
**File:** internal/swarm/orchestrator.go (L1-50)
```go
package swarm

import (
	"context"
	"fmt"
	"log/slog"
	"time"

	"github.com/Dicklesworthstone/ntm/internal/tmux"
)

// SessionOrchestrator handles creation and management of tmux sessions
// for the weighted multi-project swarm system.
//
// The orchestrator uses an explicit tmux binary path (via tmux.BinaryPath())
// to avoid issues with shell plugins (e.g., zsh tmux plugins) that may
// intercept or modify tmux commands when relying on PATH resolution.
type SessionOrchestrator struct {
	// TmuxClient is the tmux client used for session operations.
	// If nil, the default tmux client is used.
	TmuxClient *tmux.Client

	// StaggerDelay is the delay between pane creations to avoid rate limits.
	StaggerDelay time.Duration
}

// NewSessionOrchestrator creates a new SessionOrchestrator with default settings.
func NewSessionOrchestrator() *SessionOrchestrator {
	return &SessionOrchestrator{
		TmuxClient:   nil, // Use default client
		StaggerDelay: 300 * time.Millisecond,
	}
}

// NewSessionOrchestratorWithClient creates a SessionOrchestrator with a custom tmux client.
func NewSessionOrchestratorWithClient(client *tmux.Client) *SessionOrchestrator {
	return &SessionOrchestrator{
		TmuxClient:   client,
		StaggerDelay: 300 * time.Millisecond,
	}
}

// NewRemoteSessionOrchestrator creates a SessionOrchestrator configured for remote SSH execution.
// The host parameter should be in the format "user@host" (e.g., "ubuntu@192.168.1.100").
// All tmux operations will be executed on the remote host via SSH.
func NewRemoteSessionOrchestrator(host string) *SessionOrchestrator {
	return &SessionOrchestrator{
		TmuxClient:   tmux.NewClient(host),
		StaggerDelay: 300 * time.Millisecond,
	}
```

---

## Official / 2026 links

- [GitHub `Dicklesworthstone/ntm`](https://github.com/Dicklesworthstone/ntm) — Named Tmux Manager
- [`research_overnight_stack_web/findings_guardrails_ntm.md`](research_overnight_stack_web/findings_guardrails_ntm.md)
