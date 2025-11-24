<!--
README.beautified.md - Clean Developer Style
Generated: 2025-11-23
Style: Quick-start focused, code examples, badges, efficient
Changes from original:
- Added prominent badges
- Restructured for faster time-to-first-command
- Added collapsible sections for depth
- Emphasized CLI examples
- Added "copy-paste ready" code blocks
-->

# Scout-Plan-Build

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Framework-8A2BE2.svg)](https://claude.ai)
[![Commands](https://img.shields.io/badge/commands-48-green.svg)](#all-commands)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **Structured AI development workflows that actually ship.**

Turn chaotic AI coding sessions into predictable, resumable workflows. Scout files → Plan specs → Build features.

---

## ⚡ 30-Second Start

```bash
# 1. Install to your project
./scripts/install_to_new_repo.sh /path/to/your/repo
cd /path/to/your/repo

# 2. Configure
cp .env.template .env
# Add your ANTHROPIC_API_KEY

# 3. Use it
Grep "authentication" --type py          # Scout
/plan_w_docs_improved "Add OAuth"        # Plan
/workflow:build_adw "specs/oauth.md"     # Build
```

That's it. Your AI assistant now has structure.

---

## 🎯 The Core Loop

```
Scout → Plan → Build
```

Every feature follows this pattern:

```bash
# SCOUT: Find relevant files
Grep "user_auth" --type py
# Output: auth.py, middleware.py, routes.py

# PLAN: Create a specification
/plan_w_docs_improved "Add 2FA to login" "" "scout_outputs/files.json"
# Output: specs/issue-001-2fa.md

# BUILD: Implement from spec
/workflow:build_adw "specs/issue-001-2fa.md"
# Output: Code changes + tests + docs
```

---

## 📋 When to Use What

| Task Size | Files | Approach |
|-----------|-------|----------|
| Trivial | 1-2 | Just do it |
| Standard | 3-5 | `Plan → Build` |
| Complex | 6+ | `Scout → Plan → Build` |
| Uncertain | Any | Parallel worktrees |

<details>
<summary><b>Parallel worktrees example</b></summary>

```bash
# Try 3 different caching approaches
/git:init-parallel-worktrees cache-strategy 3

# Work in each worktree with different approaches
# tree-1: Redis
# tree-2: In-memory LRU
# tree-3: SQLite

# Compare results
/git:compare-worktrees cache-strategy

# Merge the winner
/git:merge-worktree trees/cache-strategy-2
```

</details>

---

## 🛠️ Essential Commands

### Planning

```bash
/plan_w_docs_improved "description" "docs_url" "files.json"
/planning:feature   # New feature spec
/planning:bug       # Bug fix spec
```

### Building

```bash
/workflow:build_adw "specs/your-spec.md"
/workflow:implement "inline plan text"
```

### Git Operations

```bash
/git:commit "agent_name" "issue_class" '{"title":"..."}'
/git:pull_request "branch" '{"title":"..."}' "spec.md" "ADW-123"
/git:init-parallel-worktrees feature-name 3
/git:merge-worktree trees/feature-name-2
```

### Session Management

```bash
/session:prepare-compaction  # Before taking a break
/session:resume              # After returning
/coach                       # Toggle learning mode
```

<details>
<summary><b>All 48 commands</b></summary>

| Category | Commands |
|----------|----------|
| Analysis | `/analysis:classify_issue`, `/analysis:classify_adw`, `/analysis:review`, `/analysis:document` |
| Planning | `/planning:feature`, `/planning:bug`, `/planning:chore`, `/planning:patch`, `/plan_w_docs_improved`, `/plan_w_docs` |
| Workflow | `/workflow:build_adw`, `/workflow:implement`, `/workflow:scout`, `/workflow:scout_improved`, `/workflow:scout_plan_build` |
| Git | `/git:commit`, `/git:pull_request`, `/git:init-parallel-worktrees`, `/git:merge-worktree`, `/git:compare-worktrees`, `/git:worktree_checkpoint`, `/git:worktree_undo`, `/git:worktree_redo` |
| Testing | `/testing:test`, `/testing:test_e2e`, `/testing:resolve_failed_test`, `/testing:resolve_failed_e2e_test` |
| Session | `/session:resume`, `/session:prepare-compaction`, `/session:start`, `/session:prime` |
| E2E Tests | `/e2e:test_basic_query`, `/e2e:test_complex_query`, `/e2e:test_sql_injection`, `/e2e:test_disable_input_debounce`, `/e2e:test_random_query_generator` |
| Utilities | `/utilities:tools`, `/utilities:research-add`, `/utilities:conditional_docs`, `/utilities:install`, `/utilities:init-framework`, `/utilities:prepare_app` |

See [SLASH_COMMANDS_REFERENCE.md](docs/SLASH_COMMANDS_REFERENCE.md) for details.

</details>

---

## 📂 Project Structure

```
your-repo/
├── adws/                    # Workflow engines
│   ├── adw_build.py         # Build orchestrator
│   ├── adw_plan.py          # Planning engine
│   └── adw_modules/         # Shared modules
├── specs/                   # Generated specifications
├── scout_outputs/           # Discovery results
├── ai_docs/                 # AI-generated docs
│   ├── build_reports/       # Execution reports
│   ├── reviews/             # Code reviews
│   └── sessions/handoffs/   # Session continuity
└── .claude/
    ├── commands/            # 48 slash commands
    ├── hooks/               # Lifecycle hooks
    └── settings.json        # Permissions & config
```

---

## 🔄 Session Continuity

Never lose context again:

```bash
# Before taking a break
/session:prepare-compaction
# Creates: ai_docs/sessions/handoffs/handoff-YYYY-MM-DD.md

# After returning (even new terminal)
/session:resume
# Reads handoff, restores context, suggests next steps
```

The SessionStart hook automatically detects available handoffs on startup.

---

## 🎓 Coach Mode

Learn how AI makes decisions:

```bash
/coach          # Toggle on/off (balanced)
/coach minimal  # Just symbols: 📍 Step 2/5 → ✅
/coach full     # Maximum transparency
```

See decision points, tool choices, and workflow progress in real-time.

---

## ⚡ Performance

| Execution | Time | Improvement |
|-----------|------|-------------|
| Sequential (test→review→doc) | 12-17 min | baseline |
| Parallel | 8-11 min | **40-50% faster** |

Achieved through parallel subagent execution in build phase.

---

## 📊 Status

| Component | Status | Notes |
|-----------|--------|-------|
| Native tools (Grep/Glob) | ✅ 100% | Always use these for scouting |
| Plan commands | ✅ 80% | Working, minor edge cases |
| Build commands | ✅ 90% | Production ready |
| Scout commands | ⚠️ 40% | Use native tools instead |
| Session management | ✅ 90% | Handoffs working |
| Hooks | ✅ 100% | All lifecycle events |

---

## 🤝 Contributing

```bash
# Fork and clone
git clone https://github.com/yourname/scout_plan_build_mvp

# Create feature branch
git checkout -b feature/your-feature

# Use the framework to build your feature!
/plan_w_docs_improved "Your feature description"
/workflow:build_adw "specs/your-feature.md"

# Submit PR
/git:pull_request "feature/your-feature" '{"title":"..."}' "specs/..." "ADW-XXX"
```

---

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Command router & quick reference
- **[PORTABLE_DEPLOYMENT_GUIDE.md](PORTABLE_DEPLOYMENT_GUIDE.md)** - Installation details
- **[TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)** - Architecture deep-dive
- **[docs/COACH_MODE.md](docs/COACH_MODE.md)** - Coach mode guide

---

## License

MIT © 2024

---

<p align="center">
  <b>Built with Scout-Plan-Build, using Scout-Plan-Build.</b><br>
  <sub>Every feature in this framework was spec'd and built through ADW workflows.</sub>
</p>
