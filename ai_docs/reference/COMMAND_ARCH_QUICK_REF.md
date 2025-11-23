# ADW Command Architecture — Quick Reference

## 1️⃣ SCOUT: Search + Structure

### Original → Improved Changes
| Aspect | Original | Improved |
|--------|----------|----------|
| Subagent spawn | Implicit | **Task tool** (lines 26-31) |
| Output format | List | **JSON** (lines 54-72) |
| Timeout | Mentioned | **Explicit 3min** (line 37) |
| Git cleanup | None | **`git reset --hard`** (line 48) |
| Lines | 27 | **73** |

**Files**:
- `.claude/commands/scout.md` (original, 27L)
- `.claude/commands/scout_improved.md` (enhanced, 73L)

**Output Schema**:
```json
{
  "files": [
    { "path": "src/auth.py", "offset": 15, "limit": 100, "reason": "..." }
  ],
  "key_findings": { "summary": "...", "gaps": "...", "recommendations": "..." }
}
```

---

## 2️⃣ PLAN: Template + Parallelism

### Original → Improved Changes
| Aspect | Original | Improved |
|--------|----------|----------|
| Model spec | None | **Frontmatter** (lines 1-4) |
| Analysis phase | Basic | **THINK HARD** (line 32) |
| Doc scraping | Sequential | **Parallel Task** (line 33) |
| Template | Vague | **8-section** (lines 44-87) |
| Validation | None | **Input checks** (lines 20-21) |
| Lines | 20 | **92** |

**Files**:
- `.claude/commands/plan_w_docs.md` (original, 20L)
- `.claude/commands/plan_w_docs_improved.md` (enhanced, 92L)

**Plan Output Template**:
```markdown
# Plan: [Title]
## Summary
## Problem Statement
## Inputs (scout results + doc refs)
## Architecture/Approach
## Implementation Steps
## Testing Strategy
## Risks and Mitigation
## Success Criteria
```

---

## 3️⃣ AGENT SPAWNING: Task → Bash → Tool

```
┌─ /scout "task" "4" [Slash Command]
│
├─ [Claude Code] Interprets command
│
├─ Task tool (parallel) → Spawn 4 subagents
│  ├─ Task #1: Bash → gemini -p "..." --model ...
│  ├─ Task #2: Bash → opencode run ... --model ...
│  ├─ Task #3: Bash → codex exec ...
│  └─ Task #4: Bash → claude -p "..."
│
└─ Aggregate → Write scout_outputs/relevant_files.json
```

**Key Code**:
- **Agent executor**: `adws/adw_modules/agent.py:175-299`
  - `prompt_claude_code()` — execute via Claude Code CLI (stream-json + verbose)
  - `execute_template()` — map slash command to model, build prompt
- **Template mapper**: `adws/adw_modules/agent.py:27-52`
  - `/bug`, `/feature` → **opus** (complex)
  - `/chore`, `/test` → **sonnet** (standard)

---

## 4️⃣ DATA FLOW: Scout → Plan → Build

```
┌─ SCOUT ─────────────────────────────────────┐
│ INPUT:  USER_PROMPT, SCALE                  │
│ Task tool (parallel) → External agents      │
│ Aggregate + git safety check                │
│ OUTPUT: scout_outputs/relevant_files.json
└─────────────────────────────────────────────┘
  │
  ▼
┌─ PLAN ──────────────────────────────────────┐
│ INPUT:  USER_PROMPT, DOCS, relevant_files.json
│ THINK HARD analysis                         │
│ Task tool (parallel) → Scrape docs          │
│ Design + write 8-section spec               │
│ OUTPUT: specs/<kebab-case>.md               │
└─────────────────────────────────────────────┘
  │
  ▼
┌─ BUILD ─────────────────────────────────────┐
│ INPUT:  specs/<kebab-case>.md, adw_id       │
│ Load state → Parse plan → /implement        │
│ Commit + Push + Create/update PR            │
│ OUTPUT: ai_docs/build_reports/<slug>.md     │
└─────────────────────────────────────────────┘
```

---

## 5️⃣ SAFETY: Timeouts + Validation + Git

### Timeout Strategy
| Layer | Timeout | Behavior |
|-------|---------|----------|
| Subagent (Task) | **3 min** | Skip, don't retry (scout_improved.md:37) |
| Claude Code CLI | **5 min** | Return error response (agent.py:252) |
| Subprocess | **N/A** | Catch exception (agent.py:78-79) |

### Validation Layers
1. **Input check** (plan_w_docs_improved.md:20-21)
   - Stop if USER_PROMPT, DOCS, or FILES missing
2. **Format check** (scout_improved.md:40-46)
   - Skip malformed subagent output (no auto-fix)
3. **State check** (adw_plan.py:203-220)
   - Validate plan file exists
4. **Git safety** (adw_modules/git_ops.py:78-100)
   - Check changes before commit
   - `git diff --stat && git reset --hard` after scout (scout_improved.md:48)

---

## 6️⃣ KEY FILES BY FUNCTION

### Slash Commands (.claude/commands/)
```
scout.md (27L)                    → Original, basic
scout_improved.md (73L)           → Enhanced parallel + JSON
plan_w_docs.md (20L)              → Original, simple
plan_w_docs_improved.md (92L)     → Enhanced template + parallel docs
scout_plan_build.md               → Composite (scout → plan → build)
scout_plan_build_improved.md      → Enhanced reporting
```

### ADW Shims (adws/adw_*.py)
```
adw_plan.py                       → GitHub issue → plan file
  ├─ classify_issue → build_plan → commit → finalize_git
adw_build.py                      → plan file → implementation
  ├─ load_state → implement_plan → commit → finalize_git
adw_test.py                       → run tests
adw_review.py                     → peer review
adw_document.py                   → generate docs
adw_plan_build.py, ...            → Composite workflows
```

### Core Modules (adws/adw_modules/)
```
agent.py:175-299
  ├─ prompt_claude_code()         → Execute via Claude Code CLI
  └─ execute_template()           → Map slash command → model → prompt

workflow_ops.py:1-50
  ├─ build_plan()                 → Call /feature, /bug, /chore
  ├─ implement_plan()             → Call /implement
  ├─ classify_issue()             → Call /classify_issue
  ├─ AGENT_PLANNER                → Agent name constant
  └─ SLASH_COMMAND_MODEL_MAP      → Model selection

git_ops.py:15-80+
  ├─ create_branch()              → git checkout -b (with fallback)
  ├─ commit_changes()             → git add -A && commit
  ├─ push_branch()                → git push -u origin
  └─ check_pr_exists()            → gh pr list

github.py
  ├─ fetch_issue()                → Get issue details
  ├─ make_issue_comment()         → Post bot comment
  └─ ADW_BOT_IDENTIFIER           → Prevent webhook loops

state.py
  ├─ ADWState.load()              → Load from agents/{adw_id}/state.json
  └─ ADWState.save()              → Persist workflow state

data_types.py:27-46
  ├─ SlashCommand                 → All CLI commands
  ├─ ADWWorkflow                  → Composite phases
  └─ GitHubIssue                  → GitHub API model
```

---

## 7️⃣ MODEL SELECTION STRATEGY

**File**: `adws/adw_modules/agent.py:27-52`

```python
SLASH_COMMAND_MODEL_MAP = {
    # Complex tasks → opus
    "/bug": "opus",
    "/feature": "opus",
    "/implement": "opus",
    "/review": "opus",
    "/patch": "opus",

    # Standard tasks → sonnet
    "/chore": "sonnet",
    "/classify_issue": "sonnet",
    "/generate_branch_name": "sonnet",
    "/test": "sonnet",
    "/document": "sonnet",
    "/commit": "sonnet",
}
```

**Rationale**:
- **Opus** for architectural decisions, complex implementations, code reviews
- **Sonnet** for classification, testing, documentation, utility tasks

---

## 8️⃣ Composite Workflows

### Execution Chain
```
adw_plan.py              → Creates plan, commits, pushes PR
  ↓ (if triggered by webhook)
adw_build.py             → Implements plan, commits, updates PR
  ↓ (if enabled)
adw_test.py              → Runs tests
  ↓ (if enabled)
adw_review.py            → Generates peer review
  ↓ (if enabled)
adw_document.py          → Generates documentation
```

### Pre-Composed Workflows
```
adw_plan_build.py                 → plan + build
adw_plan_build_test.py            → plan + build + test
adw_plan_build_test_review.py     → plan + build + test + review
adw_sdlc.py                       → plan + build + test + review + document
```

---

## 🎯 Implementation Checklist

- [ ] **Deploy improved commands** (scout_improved.md, plan_w_docs_improved.md)
- [ ] **Test parallel execution** (verify Task tool spawns 4 agents concurrently)
- [ ] **Validate JSON output** (scout results parse correctly)
- [ ] **Test timeout recovery** (3-min timeout skip on subagent #4)
- [ ] **Verify git safety** (git reset --hard works after scout)
- [ ] **Check model selection** (opus for /feature, sonnet for /chore)
- [ ] **Test state persistence** (ADWState saved/loaded correctly)
- [ ] **Validate plan template** (8 sections present in output)
- [ ] **Test end-to-end** (scout → plan → build workflow)
- [ ] **Add error logging** (capture malformed subagent outputs)

---

**Quick Ref Last Updated**: 2025-10-20
**Command Version**: scout_improved.md (73L), plan_w_docs_improved.md (92L)
**Module Version**: agent.py:v175-299, workflow_ops.py:v1-50, git_ops.py:v15-80+
