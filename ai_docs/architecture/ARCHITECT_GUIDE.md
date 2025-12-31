# Scout-Plan-Build: Architect Guide

**Version**: 4.0
**Last Updated**: 2025-12-24
**Audience**: AI architect agents integrating SPB into new projects

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Installation & Configuration](#3-installation--configuration)
4. [Workflow Patterns](#4-workflow-patterns)
5. [Command Quick Reference](#5-command-quick-reference)
6. [Best Practices](#6-best-practices)
7. [Integration Checklist](#7-integration-checklist)

---

## 1. Executive Summary

### What is Scout-Plan-Build?

Scout-Plan-Build (SPB) is a structured workflow framework for AI-assisted software development. It transforms chaotic AI conversations into **deterministic, traceable, resumable** development processes.

**Core Problem Solved**: AI coding assistants are powerful but chaotic—without structure, they create sprawling conversations that lose context, dump files in random locations, and can't resume after breaks.

**Core Solution**: Enforce a three-phase workflow (Scout → Plan → Build) with canonical file organization, state persistence, and session continuity.

### Core Value Proposition

| Benefit | Metric |
|---------|--------|
| **Structured workflows** | Deterministic Scout → Plan → Build pattern |
| **Speed improvement** | 40-50% faster with parallel execution |
| **Token efficiency** | 95% reduction on dependency analysis |
| **Session continuity** | Handoff documents enable resumption |
| **Traceable outputs** | Every artifact has a canonical location |

### When to Use This Framework

```
┌─────────────────────────────────────────────────────────┐
│ USE SPB WHEN:                                           │
├─────────────────────────────────────────────────────────┤
│ ✅ Project has 4+ files to modify                       │
│ ✅ Requirements need formal specification               │
│ ✅ Work spans multiple sessions                         │
│ ✅ Multiple approaches need exploration                 │
│ ✅ Traceability and reproducibility matter              │
├─────────────────────────────────────────────────────────┤
│ SKIP SPB WHEN:                                          │
├─────────────────────────────────────────────────────────┤
│ ❌ Simple 1-3 file changes                              │
│ ❌ Quick fixes with obvious solutions                   │
│ ❌ One-off scripts or experiments                       │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Overview

### Directory Structure

```
your-project/
│
├── CLAUDE.md                    # Command router - START HERE
│
├── .claude/                     # Claude Code configuration
│   ├── settings.json           # Permissions, hooks
│   ├── commands/               # 50 slash commands
│   │   ├── workflow/           # /scout, /plan, /build
│   │   ├── planning/           # /feature, /bug, /chore
│   │   ├── testing/            # /test, /resolve_failed_test
│   │   └── git/                # /commit, /pull_request
│   └── hooks/                  # Lifecycle hooks
│
├── adws/                       # AI Developer Workflow system
│   ├── adw_plan.py            # Planning phase
│   ├── adw_build.py           # Build phase
│   ├── adw_test.py            # Testing phase
│   ├── adw_review.py          # Review phase
│   ├── adw_sdlc.py            # Full SDLC orchestration
│   └── adw_modules/           # Core library
│       ├── agent.py           # Claude CLI subprocess
│       ├── state.py           # ADWState persistence
│       ├── workflow_ops.py    # Core operations
│       ├── git_ops.py         # Git operations
│       └── github.py          # GitHub API
│
├── specs/                      # Implementation specifications
├── agents/                     # Workflow state & outputs
│   └── {adw_id}/              # Per-workflow namespace
│       ├── adw_state.json     # Persistent state
│       └── planner/           # Phase outputs
├── scout_outputs/              # Scout phase results
├── ai_docs/                    # Architecture & reference
│   ├── architecture/          # System docs
│   ├── analyses/              # Code analyses
│   ├── reviews/               # Review docs
│   └── sessions/              # Session handoffs
└── scripts/                    # Utility scripts
```

### Component Relationships

```
                    USER / CLI
                        │
        ┌───────────────┴───────────────┐
        │                               │
    GitHub Issues              Claude Code CLI
        │                               │
        ▼                               ▼
    ┌─────────────────────────────────────┐
    │     .claude/commands/               │
    │     (Slash Commands Router)         │
    └──────────────────┬──────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────┐
    │     adws/ (Python Workflows)        │
    │     ├─ adw_plan.py                  │
    │     ├─ adw_build.py                 │
    │     └─ adw_modules/ (core library)  │
    └──────────────────┬──────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    specs/        agents/       scout_outputs/
    (Plans)       (State)       (Discovery)
```

### Data Flow: Scout → Plan → Build

```
INPUT: GitHub Issue #123 or User Prompt
         │
         ▼
    ┌─────────┐
    │  SCOUT  │ → Find relevant files
    └────┬────┘
         │ scout_outputs/relevant_files.json
         ▼
    ┌─────────┐
    │  PLAN   │ → Create specification
    └────┬────┘
         │ specs/{adw_id}_plan_spec.md
         │ agents/{adw_id}/adw_state.json
         ▼
    ┌─────────┐
    │  BUILD  │ → Implement changes
    └────┬────┘
         │ Code committed to feature branch
         ▼
    ┌─────────┐
    │  TEST   │ → Validate (optional)
    └────┬────┘
         ▼
    ┌─────────┐
    │ REVIEW  │ → Check compliance (optional)
    └────┬────┘
         ▼
    PR READY FOR MERGE
```

### State Persistence

The framework uses JSON-based state that survives across sessions:

```python
# State stored at: agents/{adw_id}/adw_state.json
{
  "adw_id": "a1b2c3d4",
  "issue_number": 123,
  "branch_name": "feat-123-a1b2c3d4-add-auth",
  "plan_file": "specs/issue-123-adw-AUTH-feature.md",
  "issue_class": "/feature"
}
```

**State Flow Pattern**:
```bash
adw_plan.py 123 | adw_build.py | adw_test.py
# Each script: load state → modify → save → pass to next
```

---

## 3. Installation & Configuration

### Prerequisites

- **Git repository** (must have `.git/` directory)
- **Python 3.9+** (3.10+ recommended)
- **Bash shell** (for installation script)
- **uv** package manager (recommended) or pip

### Quick Install (30 seconds)

```bash
# 1. Run installer
./scripts/install_to_new_repo.sh /path/to/your/repo

# 2. Configure environment
cd /path/to/your/repo
cp .env.template .env
# Edit .env with your API keys

# 3. Install Python dependencies
uv sync  # or: pip install -e .

# 4. Validate installation
python test_installation.py
```

### Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | Claude API key (`sk-ant-...`) |
| `GITHUB_PAT` | ✅ | GitHub Personal Access Token |
| `GITHUB_REPO_URL` | ✅ | Repository URL |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | ✅ | Set to `32768` (prevents token limit errors) |
| `GEMINI_API_KEY` | ❌ | For research synthesis (optional) |
| `E2B_API_KEY` | ❌ | For E2B sandbox (optional) |

```bash
# .env example
ANTHROPIC_API_KEY=sk-ant-api03-...
GITHUB_PAT=ghp_...
GITHUB_REPO_URL=https://github.com/owner/repo
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
```

### What Gets Installed

| Component | Location | Purpose |
|-----------|----------|---------|
| Slash commands | `.claude/commands/` | 50 workflow commands |
| Lifecycle hooks | `.claude/hooks/` | Session tracking |
| ADW modules | `adws/` | Core Python workflows |
| Directory structure | `specs/`, `agents/`, `ai_docs/` | Canonical output locations |
| Validation script | `test_installation.py` | Post-install check |

### Post-Install Validation

```bash
python test_installation.py
```

Expected output:
```
✅ Directory exists: specs
✅ Directory exists: agents
✅ Directory exists: ai_docs
✅ Directory exists: .claude/commands
✅ Directory exists: adws
✅ Core modules installed
✅ Slash commands installed
✨ Installation successful!
```

---

## 4. Workflow Patterns

### Pattern Selection Decision Tree

```
What's your task?
│
├─ Simple (1-3 files, obvious fix)
│   └─ Just do it. No framework needed.
│
├─ Standard (4-10 files, clear requirements)
│   └─ /plan_w_docs_improved → /build_adw
│
├─ Complex (11+ files, new feature)
│   └─ Scout first → /plan_w_docs_improved → /build_adw
│
├─ Uncertain (multiple valid approaches)
│   └─ /init-parallel-worktrees → try each → /merge-worktree
│
└─ Research (exploring unknown codebase)
    └─ Task(Explore) or native Grep/Glob
```

### Pattern 1: Simple Feature (1-3 files)

No framework needed. Direct implementation:
```
Edit files → Test → Commit
```

### Pattern 2: Standard Feature (4-10 files)

```bash
# Step 1: Find relevant files (use native tools)
Grep "auth" --type py
Glob "**/auth*.py"

# Step 2: Create specification
/plan_w_docs_improved "Add user authentication" "" "scout_outputs/files.json"
# Output: specs/user-authentication.md

# Step 3: Build from spec
/build_adw "specs/user-authentication.md"
# Creates branch, implements, commits
```

### Pattern 3: Complex Feature (11+ files)

```bash
# One command does Scout → Plan → Build
/scout_plan_build_improved "Add OAuth2 authentication system" ""

# Then validate
/test
```

### Pattern 4: Multiple Approaches (Uncertain)

Use git worktrees for parallel exploration:

```bash
# Step 1: Create 3 parallel branches
/init-parallel-worktrees feature-auth 3
# Creates: trees/feature-auth-1, trees/feature-auth-2, trees/feature-auth-3

# Step 2: Create spec
/plan_w_docs_improved "Add authentication" "" ""

# Step 3: Run parallel agents (each tries different approach)
/run-parallel-agents "specs/add-authentication.md" feature-auth

# Step 4: Compare implementations
/compare-worktrees feature-auth

# Step 5: Merge best version
/merge-worktree trees/feature-auth-2
```

### Pattern 5: GitHub Issue Workflow

```bash
# Step 1: Classify the issue
/classify_issue { "title": "Add dark mode", "body": "..." }
# Returns: /feature

# Step 2: Create plan from issue
/feature 123 DARK-MODE '{"title": "Add dark mode"}'
# Output: specs/issue-123-adw-DARK-MODE-feature.md

# Step 3: Build
/build_adw "specs/issue-123-adw-DARK-MODE-feature.md"

# Step 4: Document
/document

# Step 5: Create PR
/commit
/pull_request
```

### Pattern 6: Session Resumption

```bash
# Before leaving (or context limit approaching)
/prepare-compaction

# After returning (new session)
/resume
# Reads handoff, restores context, prompts for next step
```

---

## 5. Command Quick Reference

### Most Used Commands

| Command | Purpose | Risk | Example |
|---------|---------|------|---------|
| `/scout_plan_build_improved` | Full workflow | 🟡 | `"Add auth" ""` |
| `/plan_w_docs_improved` | Create spec | 🟡 | `"Add auth" "" "files.json"` |
| `/build_adw` | Execute spec | 🟡 | `"specs/feature.md"` |
| `/scout_improved` | Find files | 🟢 | `"auth" "4"` |
| `/test` | Run tests | 🟢 | - |
| `/init-parallel-worktrees` | Parallel branches | 🟡 | `feature 3` |
| `/commit` | Git commit | 🔴 | - |
| `/pull_request` | Create PR | 🔴 | - |

### Commands by Category

**Planning** (🟡 Gated)
- `/plan_w_docs_improved` - Create implementation spec
- `/feature` - Plan from GitHub issue (feature)
- `/bug` - Plan from GitHub issue (bug fix)
- `/chore` - Plan from GitHub issue (maintenance)
- `/patch` - Quick targeted fix

**Building** (🟡 Gated)
- `/build_adw` - Execute spec via ADW Python system
- `/build` - Execute generic plan
- `/implement` - Direct inline implementation
- `/scout_plan_build_improved` - Full 3-step workflow

**Testing** (🟢 Safe)
- `/test` - Run comprehensive test suite
- `/test_e2e` - Run E2E tests
- `/resolve_failed_test` - Fix failing tests

**Git Operations** (🔴 External)
- `/commit` - Create formatted commit
- `/pull_request` - Create GitHub PR
- `/init-parallel-worktrees` - Create parallel branches
- `/merge-worktree` - Merge best approach

**Session** (🟡 Gated)
- `/resume` - Resume from compaction
- `/prepare-compaction` - Prep for context limit
- `/prime` - Load key project files

### Risk Levels

| Level | Meaning | Action |
|-------|---------|--------|
| 🟢 Safe | Read-only, no side effects | Auto-invokable |
| 🟡 Gated | Local file changes | Requires approval |
| 🔴 External | Git push, GitHub API | Manual only |

---

## 6. Best Practices

### Output Organization (CRITICAL)

**NEVER write to repository root.** Use canonical paths:

| Output Type | Location |
|------------|----------|
| Specifications | `specs/` |
| Build reports | `ai_docs/build_reports/` |
| Analyses | `ai_docs/analyses/` |
| Reviews | `ai_docs/reviews/` |
| Scout results | `scout_outputs/` |
| Session handoffs | `ai_docs/sessions/` |
| Workflow state | `agents/{adw_id}/` |

### Git Workflow

1. **Always check status first**: `git status && git branch`
2. **Feature branches only**: Never work on main/master
3. **Branch naming**: `{type}-{issue}-{adw_id}-{slug}`
4. **Incremental commits**: Commit frequently, meaningful messages
5. **Create restore points**: Commit before risky operations

### Context Management

- **Delegate research** to Task(Explore) agents
- **Use `/compact`** before context exhaustion
- **Checkpoint with commits** for recovery
- **Session handoffs** for multi-session work

### Performance Optimization

| Technique | Benefit |
|-----------|---------|
| Parallel worktrees | 1.4-10x speedup on exploration |
| Task agents | Isolated context, no pollution |
| Native tools (Grep/Glob) | Faster than external scout |
| Memory + parallelization | 8.5x combined speedup |

**When to Parallelize**:
- Tasks >2 minutes
- Independent operations
- Multiple valid approaches

**When NOT to Parallelize**:
- Tasks <1 minute (overhead exceeds benefit)
- Sequential dependencies
- Resource constrained (<4 cores, <8GB RAM)

### Common Pitfalls to Avoid

| Pitfall | Solution |
|---------|----------|
| Scout assumes external tools | Use native Grep/Glob |
| Writing to repo root | Use canonical paths |
| Working on main branch | Create feature branch first |
| Skipping validation | Run tests before commit |
| Stateless subprocess loops | Use sessions with memory |
| Trusting external output | Validate at every boundary |

---

## 7. Integration Checklist

### Pre-Build Checklist (New Project)

```
[ ] Run install script
[ ] Configure .env with API keys
[ ] Run test_installation.py
[ ] Review CLAUDE.md for command reference
[ ] Create initial feature branch
[ ] Verify git status clean
```

### Per-Feature Checklist

```
[ ] Create feature branch (never main)
[ ] Scout or search for relevant files
[ ] Create spec with /plan_w_docs_improved
[ ] Build with /build_adw
[ ] Run /test to validate
[ ] Commit with /commit
[ ] Create PR with /pull_request
```

### Session Lifecycle

```
[ ] Start: Check git status, load context with /prime
[ ] Work: Use TodoWrite, incremental commits
[ ] Checkpoint: Commit every 30 min or after milestones
[ ] End: /prepare-compaction or handoff document
```

### Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Token limit errors | Default 8192 limit | Set `CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768` |
| Scout fails | Missing external tools | Use native Grep/Glob instead |
| Files in repo root | No path enforcement | Use canonical paths from table |
| Subprocess auth fails | Env not inherited | Configure .env, run `export $(grep -v '^#' .env \| xargs)` |
| State not persisting | Wrong adw_id | Check `agents/{adw_id}/adw_state.json` |

### Validation Commands

```bash
# Check installation
python test_installation.py

# Check directory structure
ls -la specs/ agents/ ai_docs/ .claude/commands/

# Check environment
echo $ANTHROPIC_API_KEY | head -c 10
echo $CLAUDE_CODE_MAX_OUTPUT_TOKENS

# Run tests
/test
```

---

## Appendix: Quick Start Example

Complete example: Adding authentication to a new project.

```bash
# 1. Install framework
./scripts/install_to_new_repo.sh /path/to/my-app
cd /path/to/my-app

# 2. Configure
cp .env.template .env
# Edit .env with keys
uv sync
python test_installation.py

# 3. Create feature branch
git checkout -b feat-add-auth

# 4. Find relevant files
Grep "user" --type py
Glob "**/auth*.py"
# → Save results mentally or to scout_outputs/

# 5. Create spec
/plan_w_docs_improved "Add JWT authentication with login/logout endpoints" "" ""
# → Creates specs/add-jwt-authentication.md

# 6. Review spec (important!)
Read specs/add-jwt-authentication.md
# Make adjustments if needed

# 7. Build
/build_adw "specs/add-jwt-authentication.md"
# → Implements all changes

# 8. Validate
/test
# Fix any failures with /resolve_failed_test

# 9. Commit and PR
/commit
/pull_request
# → PR ready for review
```

---

## Document Info

- **Source Research**: `ai_docs/architecture/_research/`
- **Framework Version**: 4.0
- **Generated**: 2025-12-24
- **For Issues**: See research docs for 30+ identified improvement opportunities
