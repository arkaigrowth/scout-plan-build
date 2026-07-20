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

### Natural Language Approach (Recommended)

Just describe what you want in plain English - the framework handles the rest:

```
You: "Add OAuth2 login to the authentication system"

Claude automatically:
1. Scouts for relevant auth files
2. Creates a detailed specification
3. Implements the feature
4. Runs tests and validates
```

See [Natural Language Guide](docs/NATURAL_LANGUAGE_GUIDE.md) for examples and patterns.

📋 **[Quick Reference](docs/QUICK_REFERENCE.md)** - One-page cheatsheet for commands, troubleshooting, and workflows.

### Command-Driven Approach

For more control, use explicit commands:

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

## 🚀 High-Leverage Skills

**Operationalized tools that provide 100x leverage through automation.**

> **Philosophy**: Instead of manually tracing dependencies across 100 files (2 hours), run a single command (5 seconds). Instead of downloading and analyzing videos manually (30 minutes each), automate the entire pipeline. High-leverage tools turn repetitive expert work into deterministic scripts.

### How Tools Work Together

```
dependency-tracer → Identifies broken imports (compact summaries)
        ↓
Coach Mode → Shows transparent analysis process (~15% overhead)
        ↓
/plan_w_docs_improved → Creates fix specification
        ↓
/workflow:build_adw → Implements fixes automatically
```

### dependency-tracer: Token-Efficient Dependency Analysis

Trace Python imports and file references with compact, context-friendly summary modes:

```bash
# Trace all dependencies (compact summary instead of a raw dump)
CONTEXT_MODE=minimal bash scripts/dependency-tracer/scripts/trace_all.sh

# Generate ASCII dependency diagrams
python scripts/dependency-tracer/scripts/generate_ascii_diagrams.py \
  scout_outputs/traces/latest/python_imports.json

# View results
cat scout_outputs/traces/latest/summary.md
```

**Visual Output Example:**
```
Total Imports: 324
├─ ✓ Valid: 316 (97%)
└─ ✗ Broken: 8 (2%)

├─ ✓ adw_build.py (13 imports, 0 broken)
│  ├─ ✓ sys [import] (installed)
│  └─ ✓ adw_modules.state [from] (local)
└─ ✗ adw_fix.py (8 imports, 1 broken)
   └─ ✗ **missing_module** [from] (BROKEN)
```

**Key Features:**
- Environment-aware (Claude Code CLI, Claude Web, terminal)
- Fix-conversation optimized (spawn targeted agents per broken import)
- Non-invasive defaults (respects existing project structure)
- Zero MCP overhead (native CLI tools only)

→ **[Full Guide](scripts/dependency-tracer/README.md)** | [Quick Start](scripts/dependency-tracer/QUICKSTART.md)

### video-ops: Multi-Platform Video Download & Processing

Download videos and audio from 1000+ platforms (YouTube, Vimeo, etc.) with quality selection, caption extraction, and playlist support:

```bash
# Download video
/video-download https://youtube.com/watch?v=...

# Audio-only extraction
/video-download --audio-only https://...

# Batch download with filtering
/video-download --playlist https://... --filter "tutorial"
```

→ **[Available as Skill](scripts/video-download/)** (user skill, gitignored)

---

## 🎓 Coach Mode

**Learn as Claude works.** Coach Mode makes AI decision-making transparent:

```bash
/coach          # Toggle coaching on/off (balanced ~15% overhead)
/coach minimal  # Symbols only (~5% overhead)
/coach full     # Maximum transparency (~30% overhead)
```

**What You'll See:**

```
┌─────────────────────────────────────────────────┐
│ 📍 Journey: Implement OAuth2                    │
│ [▶ Scout] → [Plan] → [Build] → [Test]          │
│ 🎯 Goal: Add OAuth2 login flow                 │
└─────────────────────────────────────────────────┘

🤔 Decision: Which auth library?
   → Choosing: next-auth (matches your stack)

⚙️ Using: Grep → Found 3 auth files
📊 Progress: 2/4 complete
```

See journey progress, decision explanations, and tool insights in real-time.

→ **[Full Guide](docs/COACH_MODE.md)**

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

The framework includes **48 slash commands** organized into functional groups:

### Planning & Design
| Command | Purpose |
|---------|---------|
| `/plan_w_docs_improved` | Create a spec from requirements with documentation |
| `/planning:feature` | Plan a new feature implementation |
| `/planning:bug` | Plan a bug fix with root cause analysis |
| `/planning:chore` | Plan maintenance tasks |
| `/planning:patch` | Create focused patch plan for review issues |
| `/sc:design` | Design system architecture and APIs |

### Building & Implementation
| Command | Purpose |
|---------|---------|
| `/workflow:build_adw` | Execute a specification (preferred) |
| `/workflow:implement` | Quick inline implementation |
| `/sc:implement` | Feature implementation with persona activation |
| `/sc:build` | Build, compile, and package projects |

### Git & Version Control
| Command | Purpose |
|---------|---------|
| `/git:commit` | Smart commit with formatted message |
| `/git:pull_request` | Create PR from branch with context |
| `/git:generate_branch_name` | Generate standardized branch names |
| `/git:init-parallel-worktrees` | Create N parallel branches |
| `/git:merge-worktree` | Merge best worktree approach |
| `/git:compare-worktrees` | Compare all parallel implementations |
| `/git:worktree_checkpoint` | Create undo point in worktree |
| `/git:worktree_undo` | Undo N checkpoints |

### Testing & Analysis
| Command | Purpose |
|---------|---------|
| `/sc:test` | Execute comprehensive validation tests |
| `/sc:analyze` | Multi-domain code analysis |
| `/testing:test_e2e` | Run E2E tests with Playwright |
| `/testing:resolve_failed_test` | Fix failing tests systematically |
| `/analysis:review` | Review work against specification |
| `/analysis:classify_issue` | Classify and route GitHub issues |

### Session & Context Management
| Command | Purpose |
|---------|---------|
| `/session:resume` | Restore context after compaction |
| `/session:prepare-compaction` | Create handoff before compacting |
| `/sc:save` | Save session context to Serena MCP |
| `/sc:load` | Load project context from Serena MCP |
| `/coach` | Toggle transparent workflow mode |

### Discovery & Documentation
| Command | Purpose |
|---------|---------|
| `/workflow:scout_improved` | Search codebase for task files |
| `/sc:explain` | Explain code, concepts, and behavior |
| `/sc:document` | Generate focused documentation |
| `/analysis:document` | Document implemented features |

<details>
<summary>All 48 commands by category</summary>

See [SLASH_COMMANDS_REFERENCE.md](docs/SLASH_COMMANDS_REFERENCE.md) for the complete categorized list with usage examples.

**Categories**: Planning (6), Building (4), Git (8), Testing (5), Session (5), Discovery (3), Utilities (7), E2E Tests (5), Workflow (5)

</details>

---

## Why This Works

**Parallel Execution**: Test, review, and document phases run simultaneously.
- Sequential: 12-17 minutes
- Parallel: 8-11 minutes (40-50% faster)

**Token Efficiency**: Smart tools minimize context consumption.
- Traditional: 60,000 tokens for dependency analysis
- dependency-tracer: 3,100 tokens (95% reduction)

**Session Continuity**: Handoff documents capture context. Resume with `/session:resume` after any break.

**Canonical Locations**: Every output has a home. Specs go in `specs/`, reports in `ai_docs/build_reports/`, scout results in `scout_outputs/`.

**Natural Language First**: Just describe your intent - the framework routes to the right tools and commands automatically. See [Natural Language Guide](docs/NATURAL_LANGUAGE_GUIDE.md).

**Validated Through Use**: This framework was built using itself. Every feature was spec'd, built, and refined through the ADW workflow.

---

## Example Workflows

### Adding a Feature

**Natural Language (Simple):**
```
You: "Add 2FA support to the login flow"
→ Claude handles Scout → Plan → Build automatically
```

**Command-Driven (Control):**
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

### Analyzing Dependencies

```bash
# Trace all dependencies with minimal context (compact summaries instead of full graph dumps)
CONTEXT_MODE=minimal bash scripts/dependency-tracer/scripts/trace_all.sh

# Generate visual ASCII diagrams
python scripts/dependency-tracer/scripts/generate_ascii_diagrams.py \
  scout_outputs/traces/latest/python_imports.json summary

# View broken imports summary
cat scout_outputs/traces/latest/summary.md

# Spawn fix agents for each broken import
python scripts/dependency-tracer/scripts/adw_spawn_fix_agents.py \
  scout_outputs/traces/latest/python_imports.json
```

**Result:** Instead of loading 50K+ tokens of dependency data, you get:
- 100 tokens for main summary
- 300 tokens per fix-conversation (only for broken imports)
- Visual ASCII diagrams for pattern recognition

---

## Status

| Component | Status | Notes |
|-----------|--------|-------|
| Natural Language | ✅ Working | Primary interface (see [guide](docs/NATURAL_LANGUAGE_GUIDE.md)) |
| Scout (file discovery) | ⚠️ Use native | Grep/Glob work better than `/scout` commands |
| Plan (spec generation) | ✅ Working | `/plan_w_docs_improved` functional |
| Build (implementation) | ✅ Working | `/workflow:build_adw` functional |
| Parallel execution | ✅ Working | 40-50% speedup confirmed |
| Session continuity | ✅ Working | `/session:resume` functional |
| Coach Mode | ✅ Working | Transparent workflows with 3 levels |
| dependency-tracer | ✅ Working | Compact summaries, ASCII diagrams |
| Portability | 🟡 85% | Some paths hardcoded, improving |

> **Note**: The `/scout` slash commands are deprecated in favor of native Grep/Glob tools for file discovery. Natural language interface is the recommended starting point for all tasks.

---

## Documentation

### Core Guides
| Doc | Purpose |
|-----|---------|
| [CLAUDE.md](CLAUDE.md) | Command router and quick reference |
| [NATURAL_LANGUAGE_GUIDE.md](docs/NATURAL_LANGUAGE_GUIDE.md) | How to use natural language effectively |
| [COACH_MODE.md](docs/COACH_MODE.md) | Transparent workflow learning |
| [SLASH_COMMANDS_REFERENCE.md](docs/SLASH_COMMANDS_REFERENCE.md) | All 48 commands |

### Technical References
| Doc | Purpose |
|-----|---------|
| [PORTABLE_DEPLOYMENT_GUIDE.md](PORTABLE_DEPLOYMENT_GUIDE.md) | Detailed installation |
| [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) | Architecture deep-dive |
| [dependency-tracer/README.md](scripts/dependency-tracer/README.md) | Token-efficient dependency analysis |

### Skills & Extensions
| Skill | Purpose |
|-------|---------|
| [adw-scout](/.claude/skills/adw-scout.md) | Intelligent scout with memory |
| [adw-complete](/.claude/skills/adw-complete.md) | Complete workflow orchestrator |
| [dependency-tracer](scripts/dependency-tracer/) | Trace imports and file refs with compact summaries |
| [video-download](.claude/skills/) | Download from 1000+ platforms (user skill) |

---

**Status**: Actively developed
**Last Updated**: 2026-07-19
