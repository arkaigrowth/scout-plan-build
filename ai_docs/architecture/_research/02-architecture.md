# Architecture Research

**Agent**: Explore (very thorough)
**Date**: 2025-12-24
**Directories Analyzed**: ai_docs/architecture/, adws/, .claude/, scripts/, specs/

---

## Directory Structure

```
scout_plan_build_mvp/
│
├── CLAUDE.md                     # Main instruction router - START HERE
├── CLAUDE.local.md              # Local environment overrides
│
├── .claude/                      # Claude Code configuration
│   ├── settings.json            # Permissions, hooks, lifecycle
│   ├── commands/                # Slash commands (48 total)
│   │   ├── analysis/            # /analyze, /design, etc.
│   │   ├── git/                 # /commit, /pull_request, etc.
│   │   ├── planning/            # /plan_w_docs, /feature, etc.
│   │   ├── testing/             # /test, /resolve_failed_test
│   │   ├── utilities/           # /install, /prepare_app
│   │   └── workflow/            # /scout, /build, /scout_plan_build
│   ├── hooks/                   # Lifecycle hooks
│   └── skills/                  # Skill definitions
│
├── adws/                        # AI Developer Workflow system - CORE
│   ├── adw_plan.py              # Planning phase
│   ├── adw_build.py             # Build phase
│   ├── adw_test.py              # Testing phase
│   ├── adw_review.py            # Review phase
│   ├── adw_document.py          # Documentation phase
│   ├── adw_sdlc.py              # Complete SDLC orchestration
│   ├── adw_modules/             # Core library
│   │   ├── agent.py             # Claude Code CLI integration
│   │   ├── state.py             # ADWState persistence
│   │   ├── workflow_ops.py      # Core operations
│   │   ├── git_ops.py           # Git operations
│   │   ├── github.py            # GitHub API
│   │   └── validators.py        # Input validation
│   └── adw_triggers/            # Automation (cron, webhook)
│
├── ai_docs/                     # Architecture & reference
│   ├── architecture/            # System architecture
│   ├── analyses/                # Code analyses
│   ├── reviews/                 # Review documents
│   └── sessions/                # Session handoffs
│
├── specs/                       # Implementation specifications
├── agents/                      # Workflow state & outputs
├── scout_outputs/               # Scout phase results
├── scripts/                     # Utility scripts (40+)
└── tests/                       # Test suite
```

---

## Component Map

```
                    USER / CLI
                        |
        ┌───────────────┴───────────────┐
        |                               |
    GitHub Issues              Claude Code CLI
        |                               |
        v                               v
    ┌─────────────────────────────────────┐
    │  .claude/commands/ (Slash Commands) │
    └──────────────────┬──────────────────┘
                       |
        ┌──────────────┴──────────────┐
        |                             |
        v                             v
    adws/                    .claude/hooks/
    ADW System               Lifecycle Mgmt
    (Python)
        |
        v
    adw_modules/ (Core Library)
    ├─ agent.py (subprocess)
    ├─ state.py (JSON persistence)
    ├─ workflow_ops.py
    ├─ git_ops.py
    └─ github.py
        |
        v
    Infrastructure
    ├─ Git (branches, commits)
    ├─ GitHub (issues, PRs)
    └─ Anthropic API
```

---

## Data Flow: Scout → Plan → Build Pipeline

```
INPUT: GitHub Issue or User Prompt
    |
    v
[SCOUT] → scout_outputs/relevant_files.json
    |
    v
[PLAN] → specs/{adw_id}_plan_spec.md + agents/{adw_id}/adw_state.json
    |
    v
[BUILD] → Code changes committed to branch
    |
    v
[TEST] → Test results (optional)
    |
    v
[REVIEW] → Review report + screenshots (optional)
    |
    v
[DOCUMENT] → app_docs/features/ (optional)
    |
    v
COMPLETE: PR ready for merge
```

---

## State Flow (Persistence)

```
Script Execution Pattern:
1. Check stdin for piped state
2. If not found, load from file
3. If not found, create new state
4. Perform workflow operations
5. Save to agents/{adw_id}/adw_state.json
6. Output to stdout as JSON

Piping Example:
adw_plan.py 123 | adw_build.py | adw_test.py
```

---

## Key Files by Directory

**Core Orchestration**
- `adws/adw_sdlc.py` - Full SDLC (30 lines, subprocess-based)
- `adws/adw_modules/workflow_ops.py` - Core workflow logic

**State & Persistence**
- `adws/adw_modules/state.py` - ADWState class
- `agents/{adw_id}/adw_state.json` - Persistent state

**Integration**
- `adws/adw_modules/agent.py` - Claude Code subprocess
- `adws/adw_modules/github.py` - GitHub API

---

## 🚩 Issues Found

### 1. Hardcoded Directory Paths (HIGH)
- `specs/`, `agents/`, `ai_docs/` hardcoded throughout
- Cannot run on different structure or in monorepo

### 2. GitHub-Only VCS Provider (HIGH)
- All VCS operations hardcoded for GitHub (`gh` CLI)
- Cannot use with GitLab, Bitbucket

### 3. External Tool Dependencies Broken (MEDIUM)
- `gemini_search.py` assumes Google Gemini CLI available
- Scout phase fails when external tools not installed

### 4. No Configuration System (MEDIUM)
- All config via environment variables
- No `adw_config.yaml` or settings module

### 5. Unclear Scout Phase Integration (MEDIUM)
- Multiple implementations: `scout_simple.py`, `adw_scout_parallel.py`, Gemini
- Confusing which to use

### 6. State Management Race Conditions (LOW)
- Multi-user access to same state file can cause conflicts

### 7. Incomplete Agent Cleanup (LOW)
- `agents/` contains incomplete workflows and legacy attempts

### 8. Orphaned Scripts (LOW)
- Many scripts in `scripts/` appear incomplete or experimental

### 9. Hook System Not Documented (LOW)
- Hooks work but lack documentation

### 10. Missing Test Coverage (MEDIUM)
- `adws/adw_tests/` appears incomplete

### 11. Ambiguous SPB vs ADW Terminology (LOW)
- Documentation uses both terms interchangeably

### 12. No Dependency Abstraction (MEDIUM)
- Only Claude AI provider supported; not pluggable
