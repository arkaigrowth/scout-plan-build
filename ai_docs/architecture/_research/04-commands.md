# Commands & Skills Research

**Agent**: Explore (very thorough)
**Date**: 2025-12-24
**Directories Analyzed**: .claude/commands/, .claude/skills/

---

## Command Inventory

**Total: 50 commands across 9 categories**

### Workflow (9)
- `/scout` - Basic search (deprecated)
- `/scout_improved` - Enhanced parallel search ⭐
- `/scout_fixed` - Fixed Python implementation
- `/scout_parallel` - Parallel execution
- `/scout_plan_build` - Three-step workflow
- `/scout_plan_build_improved` - Improved SPB ⭐
- `/build` - Implement from plan
- `/build_adw` - ADW Python build ⭐
- `/implement` - Direct implementation

### Planning (6)
- `/plan_w_docs` - Plan with doc scraping
- `/plan_w_docs_improved` - Concise plan ⭐
- `/feature` - Feature plan from issue
- `/bug` - Bug fix plan
- `/chore` - Maintenance plan
- `/patch` - Focused patch plan

### Analysis (5)
- `/analyze` - Code analysis
- `/classify_issue` - Route issues ⭐
- `/classify_adw` - Extract ADW commands
- `/review` - Review against spec
- `/document` - Generate docs

### Testing (5)
- `/test` - Run validation suite ⭐
- `/test_e2e` - E2E tests
- `/resolve_failed_test` - Fix unit tests
- `/resolve_failed_e2e_test` - Fix E2E tests
- Plus 7 E2E test command files

### Git & Worktree (11)
- `/init-parallel-worktrees` - Create N worktrees ⭐
- `/run-parallel-agents` - Execute in parallel ⭐
- `/compare-worktrees` - Compare implementations
- `/merge-worktree` - Merge best approach
- `/worktree_create` - Create single
- `/worktree_checkpoint` - Save state
- `/worktree_undo` - Undo changes
- `/worktree_redo` - Redo changes
- `/commit` - Formatted commit ⭐
- `/generate_branch_name` - Generate branch
- `/pull_request` - Create PR ⭐

### Session (6)
- `/start` - Start servers
- `/resume` - Resume from compaction
- `/prime` - Load context
- `/prepare-compaction` - Prep for compaction
- `/install` - Initialize project
- `/prepare_app` - Reset database

### Utilities (6)
- `/init-framework` - Setup wizard
- `/conditional_docs` - Docs guide
- `/research-add` - Add research
- `/tools` - List tools
- `/coach` - Toggle coach mode

---

## Most Important Commands (Top 10)

| # | Command | Purpose | Risk |
|---|---------|---------|------|
| 1 | `/scout_plan_build_improved` | End-to-end delivery | 🟡 |
| 2 | `/plan_w_docs_improved` | Create specs | 🟡 |
| 3 | `/build_adw` | Execute specs | 🟡 |
| 4 | `/scout_improved` | Parallel search | 🟢 |
| 5 | `/test` | Run validation | 🟢 |
| 6 | `/init-parallel-worktrees` | Parallel branches | 🟡 |
| 7 | `/run-parallel-agents` | Parallel execution | 🟡 |
| 8 | `/commit` | Formatted commit | 🔴 |
| 9 | `/pull_request` | Create PR | 🔴 |
| 10 | `/classify_issue` | Route issues | 🟢 |

---

## Command Syntax Examples

### Full Workflow
```bash
/scout_plan_build_improved "Add user authentication" ""
# Executes: scout → plan → build
```

### Step by Step
```bash
# Scout
/scout_improved "Add user authentication" "4"
# Output: scout_outputs/relevant_files.json

# Plan
/plan_w_docs_improved "Add auth" "" "scout_outputs/relevant_files.json"
# Output: specs/user-authentication.md

# Build
/build_adw "specs/user-authentication.md"
# Creates branch, implements, commits
```

### Parallel Development
```bash
/init-parallel-worktrees feature-auth 3
/run-parallel-agents "specs/auth.md" feature-auth
/compare-worktrees feature-auth
/merge-worktree trees/feature-auth-2
```

### GitHub Issue Flow
```bash
/classify_issue { "title": "Add dark mode", "body": "..." }
# Returns: /feature

/feature 123 DARK-MODE '{"title": "Add dark mode", "body": "..."}'
# Output: specs/issue-123-adw-DARK-MODE-feature.md

/build_adw "specs/issue-123-adw-DARK-MODE-feature.md"
```

---

## Command Chaining Patterns

### Pattern 1: Simple (1-3 files)
```
No commands → Direct edit/test/commit
```

### Pattern 2: Standard (4-10 files)
```
Native tools → /scout_improved → /plan_w_docs_improved → /build_adw → /test
```

### Pattern 3: Complex (11+ files)
```
/scout_plan_build_improved → /test
```

### Pattern 4: Multiple Approaches
```
/init-parallel-worktrees → /run-parallel-agents → /compare-worktrees → /merge-worktree
```

### Pattern 5: GitHub Issue to PR
```
Issue → /classify_issue → /feature|bug|chore → /build_adw → /document → /commit → /pull_request
```

---

## Risk Levels

### 🟢 Safe (14 commands)
Read-only, auto-invokable:
- `/scout_improved`, `/scout`, `/scout_fixed`, `/scout_parallel`
- `/test`, `/test_e2e`
- `/analyze`, `/classify_issue`, `/classify_adw`, `/review`
- `/conditional_docs`, `/prime`, `/tools`, `/coach`

### 🟡 Local Changes (33 commands)
Requires approval:
- All planning commands
- All build commands
- All worktree commands
- Session management
- Test resolution

### 🔴 External Changes (3 commands)
Never auto-invoke:
- `/commit`
- `/generate_branch_name`
- `/pull_request`

---

## 🚩 Issues Found

### 1. Scout Commands Need Consolidation
- `/scout` deprecated, `/scout_fixed` workaround, `/scout_parallel` unclear
- Recommendation: Consolidate to `/scout_improved`

### 2. Plan Commands Overlap
- `/plan_w_docs` vs `/plan_w_docs_improved` similar
- `/feature`, `/bug`, `/chore`, `/patch` parallel to main commands
- Recommendation: Clarify when to use each

### 3. Build Command Variants
- `/build` (generic), `/build_adw` (specialized), `/implement` (direct)
- Recommendation: Use `/build_adw` for specs

### 4. Worktree Commands Scattered
- 8 commands, no consolidated workflow doc
- Recommendation: Add worktree workflow guide

### 5. Test Resolution Incomplete
- No clear examples of failure diagnosis
- Recommendation: Add failure resolution workflow

### 6. E2E Test Files Unclear
- 7 files appear to be test cases, not commands
- Recommendation: Clarify purpose

### 7. Session Commands Mixed
- Some app-specific, some generic
- Recommendation: Separate clearly

### 8. Coach Mode Underdocumented
- Works but not in main CLAUDE.md
- Recommendation: Add to decision tree

### 9. Missing Documentation Reader
- `/conditional_docs` is guide, not executable
- Recommendation: Consider skill-based doc selection

### 10. SuperClaude Commands Referenced
- `/sc:analyze`, `/sc:explain` in CLAUDE.md
- Not in `.claude/commands/` (external)
- Recommendation: Clarify distinction

---

## Summary Stats

| Metric | Value |
|--------|-------|
| Total Commands | 50 |
| Safe (🟢) | 14 |
| Gated (🟡) | 33 |
| External (🔴) | 3 |
| Categories | 9 |
| Fully Documented | ~70% |
| Issues Found | 10 |
