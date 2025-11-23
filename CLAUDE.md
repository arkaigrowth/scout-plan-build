# Scout Plan Build MVP - Command Router v4

**Your role**: Execute deterministic workflows through slash commands. Pick the right tool for the task.
**Date Updated**: 2025-11-22
**Framework Version**: 4.0

## 🎯 Task Router - START HERE

```mermaid
What do you need?
│
├─ 🔍 EXPLORE/RESEARCH ──→ Native tools (Grep/Glob)
│                           └─ Fallback: /sc:analyze
│
├─ 📋 PLAN A FEATURE ────→ Have files? → /plan_w_docs_improved
│                           └─ Need files? → Native tools first
│
├─ 🔨 BUILD CODE ────────→ Have spec? → /build_adw
│                           └─ No spec? → /plan_w_docs_improved first
│
├─ 🧪 TEST/ANALYZE ──────→ /sc:test (runs pytest)
│                           └─ /sc:analyze (code review)
│
└─ 🚀 TRY MULTIPLE WAYS ─→ /init-parallel-worktrees
                            └─ Then: /run-parallel-agents
```

## 📊 Command Menu with Risk Levels

### 🟢 Safe Commands (Auto-invokable)
<!-- risk: read-only -->
<!-- auto-invoke: safe -->

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `Grep/Glob/Read` | Find files/content | Always start here for searching |
| `/sc:analyze` | Analyze code | Code review, understanding |
| `/sc:explain` | Explain code | Documentation needs |
| `/sc:design` | Design architecture | Planning phase |
| `/compare-worktrees` | Compare branches | After parallel work |

### 🟡 Local Changes (Require Approval)
<!-- risk: mutate-local -->
<!-- auto-invoke: gated -->

| Command | Purpose | Example |
|---------|---------|---------|
| `/plan_w_docs_improved` | Create spec | `/plan_w_docs_improved "Add auth" "" "files.json"` |
| `/build_adw` | Build from spec | `/build_adw "specs/auth.md"` |
| `/sc:implement` | Implement feature | `/sc:implement` |
| `/sc:test` | Run tests | `/sc:test` |
| `/init-parallel-worktrees` | Create branches | `/init-parallel-worktrees feature 3` |

### 🔴 External Changes (Never Auto-invoke)
<!-- risk: mutate-external -->
<!-- auto-invoke: never -->

| Command | Purpose | Risk |
|---------|---------|------|
| `/sc:git` | Git operations | Can push to remote |
| `/sc:spawn` | Spawn agents | Resource consumption |
| `/merge-worktree` | Merge branches | Affects main branch |

## 📁 Output Organization (CRITICAL)

**NEVER write files to repository root!** Use these canonical paths:

| Output Type | Location | Example |
|------------|----------|---------|
| Analyses | `ai_docs/analyses/` | `ai_docs/analyses/auth-analysis.md` |
| Reviews | `ai_docs/reviews/` | `ai_docs/reviews/code-review.md` |
| Reports | `ai_docs/build_reports/` | `ai_docs/build_reports/auth-report.md` |
| Specs | `specs/` | `specs/issue-001-adw-AUTH-login.md` |
| Scout | `scout_outputs/` | `scout_outputs/relevant_files.json` |
| Temp work | `agent_outputs/YYYY-MM-DD/` | `agent_outputs/2025-11-22/143052-auth.json` |

## 🔄 Workflow Patterns (Tested & Working)

### Pattern 1: Simple Feature (1-3 files)
```bash
# Just implement directly - no commands needed
Edit files → Test → Commit
```

### Pattern 2: Standard Feature (4-10 files)
```bash
# 1. Find relevant files
Grep "pattern" → Glob "**/*.py"

# 2. Create plan
/plan_w_docs_improved "Feature description" "" "scout_outputs/relevant_files.json"

# 3. Build
/build_adw "specs/feature.md"
```

### Pattern 3: Complex/Uncertain Feature
```bash
# 1. Parallel exploration
/init-parallel-worktrees feature-name 3

# 2. Each agent tries different approach
/run-parallel-agents "specs/feature.md" feature-name

# 3. Compare and merge best
/compare-worktrees feature-name
/merge-worktree trees/feature-name-2  # Best one
```

## ⚠️ Critical Setup

### Environment Variables (REQUIRED)
```bash
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768  # Prevents token limit errors
export ANTHROPIC_API_KEY="sk-ant-..."      # Your actual key
export GITHUB_PAT="ghp_..."                # For GitHub operations
export GITHUB_REPO_URL="https://github.com/owner/repo"
```

### Known Issues & Fixes

| Issue | Root Cause | Fix |
|-------|------------|-----|
| Scout commands fail | Missing Task tool | Use native Grep/Glob |
| Token limit errors | Default 8192 limit | Set env var above |
| Files in repo root | No path enforcement | Use canonical paths |
| Git on main | No branch check | Always create feature branch first |

## 🛡️ Safety Rules

1. **Git Safety**: ALWAYS create feature branch before changes
   ```bash
   git checkout -b feature/issue-XXX-adw-YYY
   ```

2. **Output Safety**: NEVER write to repo root
   ```python
   # BAD
   Write("REPORT.md", content)

   # GOOD
   Write("ai_docs/reports/report.md", content)
   ```

3. **Approval Gates**: Get user confirmation for:
   - Any file modifications (🟡 commands)
   - Any git push operations (🔴 commands)
   - Any agent spawning (🔴 commands)

## 🎓 Command Decision Helper

**Not sure which command?** Answer these:

1. **How many files?**
   - 1-3 → Just do it
   - 4-10 → Use `/plan_w_docs_improved` → `/build_adw`
   - 11+ → Use parallel worktrees

2. **How clear is the requirements?**
   - Crystal clear → Standard workflow
   - Need exploration → `/sc:analyze` → `/sc:design`
   - Multiple approaches → Parallel worktrees

3. **What's the risk level?**
   - Reading only → Use any 🟢 command freely
   - Changing files → Get approval for 🟡 commands
   - External changes → Manual only for 🔴 commands

## 📊 System Status (2025-11-22)

| Component | Status | Notes |
|-----------|--------|-------|
| **Native Tools** | ✅ 100% | Grep, Glob, Read always work |
| **Plan/Build** | ✅ 80% | Working, needs validation |
| **Scout Commands** | ❌ 40% | Broken - use native tools |
| **SuperClaude** | ✅ 90% | Working, well-designed |
| **Parallel Execution** | ✅ 100% | Worktrees fully functional |
| **Output Organization** | ✅ 70% | Infrastructure exists, needs enforcement |

## 🚀 Quick Examples

### "Find all auth files"
```bash
Grep -l "auth" --type py
Glob "**/auth*.py"
```

### "Plan a new feature"
```bash
# First find files
Grep "relevant_pattern" > temp_results

# Then plan
/plan_w_docs_improved "Feature description" "https://docs.example.com" "scout_outputs/relevant_files.json"

# Then build
/build_adw "specs/issue-001-adw-XXX-feature.md"
```

### "Try multiple approaches"
```bash
/init-parallel-worktrees explore-approaches 3
/run-parallel-agents "specs/exploration.md" explore-approaches
/compare-worktrees explore-approaches
/merge-worktree trees/explore-approaches-2
```

---

**Remember**: Commands are deterministic. The LLM suggests, the user decides, the command executes predictably.
**Never forget**: Always specify output paths. Never write to repo root.