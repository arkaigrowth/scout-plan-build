# Scout Plan Build MVP - Command Router v4

**Your role**: Execute deterministic workflows through slash commands. Pick the right tool for the task.

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

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `Grep/Glob` | Find files/content | Always start here for searching |
| `/sc:analyze` | Analyze code | Code review, understanding |
| `/sc:explain` | Explain code | Documentation needs |
| `/sc:design` | Design architecture | Planning phase |
| `/compare-worktrees` | Compare branches | After parallel work |

### 🟡 Local Changes (Require Approval)

| Command | Purpose | Example | Risk |
|---------|---------|---------|------|
| `/plan_w_docs_improved` | Create spec | `/plan_w_docs_improved "Add auth" "" "files.json"` | Creates spec file |
| `/build_adw` | Build from spec | `/build_adw "specs/auth.md"` | Modifies code |
| `/sc:implement` | Implement feature | `/sc:implement` | Creates/edits files |
| `/sc:test` | Run tests | `/sc:test` | Executes pytest |
| `/init-parallel-worktrees` | Create branches | `/init-parallel-worktrees feature 3` | Creates git branches |

### 🔴 External Changes (Never Auto-invoke)

| Command | Purpose | Risk | Manual Only |
|---------|---------|------|-------------|
| `/sc:git` | Git operations | Can push to remote | ✓ |
| `/sc:spawn` | Spawn agents | Resource consumption | ✓ |
| `/merge-worktree` | Merge branches | Affects main branch | ✓ |
| `/scout_improved` | External AI | API costs, security | ✓ |

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

### Pattern 4: Analysis & Improvement
```bash
# 1. Understand current code
/sc:analyze

# 2. Design improvements
/sc:design

# 3. Implement with approval
/sc:implement  # Requires user confirmation

# 4. Validate
/sc:test
```

## ⚠️ Known Issues & Workarounds

| Issue | Workaround |
|-------|------------|
| `/scout` commands fail (missing Task tool) | Use native Grep/Glob instead |
| Token limit errors | Set `CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768` |
| Can't auto-chain commands | Use output hints for next steps |
| External tools missing (gemini, codex) | Use native Claude capabilities |

## 🛡️ Safety Rules (From Chad's Framework)

1. **Read-only by default** - Start with analysis, not changes
2. **Explicit approval for mutations** - User confirms before file changes
3. **Never auto-invoke external** - No git push, API calls, or spawning without permission
4. **Scope fencing** - Commands declare their blast radius
5. **Audit trail** - Document what was run and why

## 📁 Output Locations (SSOT)

| Output Type | Location | Never |
|------------|----------|-------|
| Scout results | `scout_outputs/relevant_files.json` | Don't scatter |
| Specs | `specs/issue-XXX-adw-YYY-*.md` | Not in root |
| Build reports | `ai_docs/build_reports/` | Not in docs/ |
| Reviews | `ai_docs/reviews/` | Not mixed with code |
| Test results | `test_reports/` | Not in git |

## 🎓 Command Decision Helper

**Not sure which command?** Answer these:

1. **How many files?**
   - 1-3 → Just do it
   - 4-10 → Standard pattern
   - 11+ → Parallel exploration

2. **How clear is the task?**
   - Crystal clear → Standard pattern
   - Some ambiguity → /sc:design first
   - Multiple valid approaches → Parallel worktrees

3. **What's the risk?**
   - Read-only → Use any green command
   - Local changes → Get approval first
   - External changes → Manual only

## 🚀 Quick Start Examples

### "Find all auth files"
```bash
Grep -l "auth" --type py
```

### "Plan a new login feature"
```bash
/plan_w_docs_improved "Add OAuth login" "https://docs.oauth.com" ""
```

### "Not sure how to implement X"
```bash
/init-parallel-worktrees explore-x 3
/run-parallel-agents "specs/explore-x.md" explore-x
/compare-worktrees explore-x
```

---

**Remember**: Commands are deterministic. The LLM suggests, the user decides, the command executes predictably.