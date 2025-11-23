# Scout-Plan-Build

**Structured AI development workflows that actually ship.**

![Scout-Plan-Build](assets/hero-banner.png)

---

## The Problem

AI coding assistants are powerful but chaotic. Without structure, you get:
- Sprawling conversations that lose context
- No clear separation between planning and building
- Files dumped in random locations
- No way to resume after a break

**Scout-Plan-Build** enforces a workflow: discover relevant files, create a spec, then build from that spec. Every step is traceable, every output has a canonical location.

---

## Quick Start

```bash
# Find files relevant to your task
Grep "authentication" --type py

# Create a specification
/plan_w_docs_improved "Add OAuth2 login" "" "scout_outputs/relevant_files.json"

# Build from the spec
/workflow:build_adw "specs/issue-001-oauth2.md"
```

That's the core loop: **Scout → Plan → Build**.

---

## When to Use What

```
What's your task?
│
├─ Simple (1-2 files, obvious fix)
│   └─ Just do it. No framework needed.
│
├─ Standard (3-5 files, clear requirements)
│   └─ /plan_w_docs_improved → /workflow:build_adw
│
├─ Complex (6+ files, new feature)
│   └─ Scout first → /plan_w_docs_improved → /workflow:build_adw
│
├─ Uncertain (multiple valid approaches)
│   └─ /git:init-parallel-worktrees → try each → /git:merge-worktree best one
│
└─ Research (exploring unknown codebase)
    └─ Task(Explore) or Grep/Glob directly
```

---

## Installation

```bash
./scripts/install_to_new_repo.sh /path/to/your/repo
cd /path/to/your/repo
cp .env.template .env  # Add your ANTHROPIC_API_KEY
```

Your existing code is untouched. The framework installs alongside it.

<details>
<summary>What gets installed</summary>

```
your-repo/
├── adws/                # Core workflow modules
├── specs/               # Generated specifications
├── scout_outputs/       # Scout phase outputs
├── ai_docs/             # AI-generated documentation
│   ├── build_reports/   # Build execution reports
│   ├── reviews/         # Code reviews
│   └── sessions/        # Handoffs for session continuity
└── .claude/commands/    # Slash commands
```

</details>

---

## Core Commands

### Planning
| Command | Purpose |
|---------|---------|
| `/plan_w_docs_improved` | Create a spec from requirements |
| `/planning:feature` | Plan a new feature |
| `/planning:bug` | Plan a bug fix |

### Building
| Command | Purpose |
|---------|---------|
| `/workflow:build_adw` | Execute a spec |
| `/workflow:implement` | Quick implementation |

### Git Operations
| Command | Purpose |
|---------|---------|
| `/git:commit` | Smart commit with message |
| `/git:pull_request` | Create PR from branch |
| `/git:init-parallel-worktrees` | Create parallel branches |
| `/git:merge-worktree` | Merge best approach |

### Session Management
| Command | Purpose |
|---------|---------|
| `/session:resume` | Restore context after compaction |
| `/session:prepare-compaction` | Create handoff before compacting |

<details>
<summary>All 48 commands</summary>

See [SLASH_COMMANDS_REFERENCE.md](docs/SLASH_COMMANDS_REFERENCE.md) for the complete list.

</details>

---

## Why This Works

**Parallel Execution**: Test, review, and document phases run simultaneously.
- Sequential: 12-17 minutes
- Parallel: 8-11 minutes (40-50% faster)

**Session Continuity**: Handoff documents capture context. Resume with `/session:resume` after any break.

**Canonical Locations**: Every output has a home. Specs go in `specs/`, reports in `ai_docs/build_reports/`, scout results in `scout_outputs/`.

**Validated Through Use**: This framework was built using itself. Every feature was spec'd, built, and refined through the ADW workflow.

---

## Example Workflows

### Adding a Feature

```bash
# 1. Scout for relevant code
Grep "user_auth" --type py
# Found: auth.py, middleware.py, routes.py

# 2. Create specification
/plan_w_docs_improved "Add 2FA support to login flow" "" "scout_outputs/relevant_files.json"
# Creates: specs/issue-001-2fa-support.md

# 3. Build from spec
/workflow:build_adw "specs/issue-001-2fa-support.md"
# Implements, tests, documents
```

### Trying Multiple Approaches

```bash
# 1. Create parallel worktrees
/git:init-parallel-worktrees cache-strategy 3

# 2. Each worktree tries a different approach
# tree-1: Redis caching
# tree-2: In-memory LRU
# tree-3: SQLite cache

# 3. Compare results
/git:compare-worktrees cache-strategy

# 4. Merge the winner
/git:merge-worktree trees/cache-strategy-2
```

### Resuming After a Break

```bash
# Before leaving
/session:prepare-compaction

# After returning (even in new session)
/session:resume
# Reads handoff, restores context, asks what's next
```

---

## Status

| Component | Status |
|-----------|--------|
| Scout (file discovery) | Use native tools (Grep/Glob) |
| Plan (spec generation) | Working |
| Build (implementation) | Working |
| Parallel execution | Working (40-50% speedup) |
| Session continuity | Working |
| Portability | 85% (some paths hardcoded) |

> **Note**: The `/scout` slash commands are partially broken. Use native Grep/Glob tools or Task(Explore) agents for file discovery instead.

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [CLAUDE.md](CLAUDE.md) | Command router and quick reference |
| [PORTABLE_DEPLOYMENT_GUIDE.md](PORTABLE_DEPLOYMENT_GUIDE.md) | Detailed installation |
| [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) | Architecture deep-dive |
| [SLASH_COMMANDS_REFERENCE.md](docs/SLASH_COMMANDS_REFERENCE.md) | All commands |

---

**Version**: MVP
**Last Updated**: 2024-11-23
