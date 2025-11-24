<!--
README.beautified.md - Marketing/Product Style
Generated: 2025-11-23
Style: Benefits-first, problem→solution narrative, persuasive
Changes from original:
- Added compelling hero section
- Restructured as problem→solution narrative
- Emphasized outcomes over features
- Added "before/after" comparisons
- Focused on emotional pain points
-->

<div align="center">

# 🚀 Scout-Plan-Build

### **Stop Herding AI. Start Shipping.**

*The structured workflow framework that turns chaotic AI coding sessions into predictable, resumable development.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Framework-8A2BE2.svg)](https://claude.ai)

[Quick Start](#-quick-start) • [How It Works](#-how-it-works) • [Features](#-features) • [Documentation](#-documentation)

</div>

---

## 😤 The Problem

You've been there. You start a coding session with an AI assistant, and within 20 minutes:

- 📂 **Files everywhere** — Code dumped in random locations with no organization
- 🧠 **Context amnesia** — After a break, you're re-explaining everything from scratch
- 🎲 **Chaotic exploration** — No separation between "figuring it out" and "building it"
- ⏱️ **Time sink** — What should take an hour takes three because of backtracking

**AI coding assistants are powerful. But without structure, they're chaos engines.**

---

## ✨ The Solution

**Scout-Plan-Build** gives your AI assistant a workflow:

```
🔍 Scout  →  📋 Plan  →  🔨 Build
```

Every feature follows this pattern. Every output has a canonical location. Every session can be resumed.

---

## 🎯 What You Get

### ⚡ Ship Faster

| Without Framework | With Scout-Plan-Build |
|-------------------|----------------------|
| Start coding immediately | Scout relevant files first |
| Discover missing context mid-build | Spec captures everything upfront |
| 12-17 minutes per feature | **8-11 minutes** (40-50% faster) |

### 🧠 Never Lose Context

```bash
# Before your meeting
/session:prepare-compaction

# After lunch, new terminal, even new day
/session:resume
# → Handoff loaded. You were working on OAuth2. Continue?
```

Your AI remembers where you left off. Always.

### 🌳 Try Multiple Approaches

Can't decide between Redis and SQLite caching? Don't guess:

```bash
/git:init-parallel-worktrees cache-strategy 3
# Three parallel branches, three approaches, one winner
```

Build all options. Compare. Merge the best.

---

## 🚀 Quick Start

**60 seconds to structured AI development:**

```bash
# Install alongside your existing code
./scripts/install_to_new_repo.sh /path/to/your/project

# Configure
cp .env.template .env
# Add your ANTHROPIC_API_KEY

# Start building
Grep "authentication" --type py           # Scout
/plan_w_docs_improved "Add OAuth login"   # Plan
/workflow:build_adw "specs/oauth.md"      # Build
```

Your existing code is untouched. The framework installs alongside it.

---

## 🔄 How It Works

### Phase 1: Scout 🔍

Find the files that matter:

```bash
Grep "user_auth" --type py
# Found: auth.py, middleware.py, routes.py, tests/test_auth.py
```

No more "I didn't know that file existed" surprises mid-build.

### Phase 2: Plan 📋

Create a specification before writing code:

```bash
/plan_w_docs_improved "Add two-factor authentication" "" "scout_outputs/files.json"
# Creates: specs/issue-001-adw-2FA-authentication.md
```

The spec captures requirements, affected files, test cases, and edge cases. **Before you write a single line of code.**

### Phase 3: Build 🔨

Execute the spec with parallel validation:

```bash
/workflow:build_adw "specs/issue-001-adw-2FA-authentication.md"
```

The build phase runs **tests, review, and documentation in parallel** — not sequentially. That's where the 40-50% time savings come from.

---

## ✅ Features

### 📁 Canonical Output Locations

Every output has a home:

| Output Type | Location |
|-------------|----------|
| Specifications | `specs/` |
| Build reports | `ai_docs/build_reports/` |
| Code reviews | `ai_docs/reviews/` |
| Session handoffs | `ai_docs/sessions/handoffs/` |

No more hunting for that file Claude created "somewhere."

### 🎓 Coach Mode

**Learn as you go.** Toggle transparency into AI decision-making:

```bash
/coach full
```

See why the AI chose certain approaches, what alternatives it considered, and where you are in the workflow.

### 🪝 Lifecycle Hooks

Customize behavior at every stage:

- **SessionStart** — Auto-detect available handoffs
- **PreToolUse** — Log every tool invocation
- **Stop** — Checkpoint before ending

### 🔀 48 Slash Commands

From `/planning:feature` to `/git:merge-worktree`, there's a command for every workflow stage. All documented, all discoverable.

---

## 📊 By The Numbers

| Metric | Value |
|--------|-------|
| Slash commands | 48 |
| Lifecycle hooks | 8 |
| Time savings | 40-50% |
| Session types | Resumable |
| Installation time | < 60 seconds |

---

## 🆚 Alternatives

| Tool | Focus | Trade-off |
|------|-------|-----------|
| **Cursor** | IDE integration | Less workflow structure |
| **Aider** | Code edits | No planning phase |
| **Continue.dev** | Extensions | No session persistence |
| **Scout-Plan-Build** | **Workflow** | Requires Claude Code |

---

## 📚 Documentation

| Guide | For |
|-------|-----|
| [CLAUDE.md](CLAUDE.md) | Quick command reference |
| [PORTABLE_DEPLOYMENT_GUIDE.md](PORTABLE_DEPLOYMENT_GUIDE.md) | Installation |
| [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) | Architecture |
| [docs/COACH_MODE.md](docs/COACH_MODE.md) | Learning mode |

---

## 🗺️ Roadmap

- [ ] **MCP Integration** — Semantic code search via Serena
- [ ] **Multi-repo support** — Monorepo and cross-repo workflows
- [ ] **VS Code extension** — GUI for command discovery
- [ ] **Team workflows** — Shared specs and handoffs

---

## 🤝 Join the Workflow

**Built by developers who got tired of AI chaos.**

This framework was built using itself. Every feature was spec'd through `/plan_w_docs_improved` and built through `/workflow:build_adw`. It's not theory — it's validated through daily use.

```bash
# Ready to stop herding AI?
./scripts/install_to_new_repo.sh /path/to/your/project
```

---

<div align="center">

**MIT License** • **v4.0** • **Built on Claude Code**

⭐ **Star this repo** if structured AI development sounds good to you.

</div>
