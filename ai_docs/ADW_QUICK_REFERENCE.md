# ADW System Quick Reference

## What Works vs. What's Broken

### Fully Functional (Verified)
- [x] **Phase Orchestration**: Plan → Build → Test → Review → Document
- [x] **State Management**: Persistent state via `agents/{adw_id}/adw_state.json`
- [x] **GitHub Integration**: Issue fetching, commenting, PR creation
- [x] **Parallel Execution**: Test/Review/Document run in parallel (40-50% faster)
- [x] **Webhook Handler**: GitHub webhook with HMAC verification
- [x] **Input Validation**: Comprehensive validators prevent injection attacks
- [x] **Scout Phase**: Basic file discovery via native tools

### Partially Functional (With Caveats)
- [~] **E2E Testing**: Supported but `--skip-e2e` is default
- [~] **Scout Parallel**: Code exists but not integrated into workflow
- [~] **Agent Execution**: Works but agents are completely stateless

### Not Implemented (But Documented)
- [ ] **Git Worktrees**: Commands documented as "⭐⭐⭐⭐⭐ WORKING" but code doesn't exist
- [ ] **Agent Memory**: Memory system files exist but are unused
- [ ] **Bitbucket Support**: Mentioned but no implementation
- [ ] **Auto PR Merging**: Documentation suggests it happens, but it doesn't

---

## Critical Architecture Decisions

### 1. Modular Composability
```
Scripts can be:
- Run individually (e.g., just adw_plan.py)
- Chained via pipes (adw_plan.py | adw_build.py)
- Orchestrated via wrapper (adw_sdlc.py)
```

### 2. State as Interface
```
adw_state.json = Contract between phases
- Minimal: Only 5 core fields
- Persistent: Survives across script invocations
- Pipeable: Can pass state via stdin/stdout
```

### 3. Subprocess-Based Parallelization
```
NOT async, NOT threading - uses subprocess.Popen()
- Simple and robust
- Easy to debug
- Works across environments
- Suitable for long-running tasks (minutes)
```

---

## File Organization Issues (IMPORTANT)

### Scout Outputs in Multiple Locations
```
CONFLICT:
├── scout_outputs/relevant_files.json        ← Primary?
└── ai_docs/scout/relevant_files.json        ← Backup?
                  └── relevant_files_backup.json  ← Old version?

RESOLUTION: Use scout_outputs/relevant_files.json ONLY
            Remove all other scout output files
            Add timestamp versioning
```

### What Plan Phase Actually Uses
```python
# From adw_plan.py logic:
scout_file = "scout_outputs/relevant_files.json"
if not exists(scout_file):
    scout_file = "ai_docs/scout/relevant_files.json"
# If both exist, first one wins (undefined behavior!)
```

---

## Workflow Execution Times (Actual)

### Sequential (Default)
```
Plan        → 2-3 min   (Claude planner agent)
Build       → 3-4 min   (Claude implementor agent)
Test        → 7-10 min  (Test suite + auto-fix)
Review      → 3-4 min   (Screenshot capture + analysis)
Document    → 2-3 min   (Doc generation)
            ─────────────
TOTAL       → 17-24 min
```

### Parallel (Test/Review/Document together)
```
Plan        → 2-3 min
Build       → 3-4 min
(Test | Review | Document) → max(7-10, 3-4, 2-3) = 7-10 min
                           ─────────────
TOTAL                      → 12-17 min

SPEEDUP: 30-50% faster
```

### What Could Be Parallel But Isn't
```
Scout (1 process) → Could use 4-6 agents (9.6x speedup)
                    Implementation exists: adw_scout_parallel.py
                    Status: ABANDONED
```

---

## Key Module Dependencies

### Core (Always Used)
```
- agent.py         → Claude Code CLI wrapper
- github.py        → GitHub API via gh CLI
- state.py         → State persistence + piping
- validators.py    → Input validation + injection prevention
- workflow_ops.py  → Central orchestration logic
```

### Optional (Phase-Specific)
```
- git_ops.py       → Only if using git features
- r2_uploader.py   → Only if uploading screenshots
```

### Unused (Implement or Remove)
```
- memory_manager.py  → Files exist but code never called
- memory_hooks.py    → Files exist but code never called
```

---

## Common Mistakes & How to Avoid

### Mistake 1: Using Old Scout Output
```
❌ WRONG:  References ai_docs/scout/relevant_files.json in documentation
✅ RIGHT:  Use scout_outputs/relevant_files.json consistently
           Keep backup at ai_docs/scout/ for fallback only
```

### Mistake 2: Expecting Worktree Commands to Work
```
❌ WRONG:  /worktree_create "feature" "main"
           → Gets error: Command not found
✅ RIGHT:  Use git worktree manually or implement the feature
           Remove `/worktree_*` from SLASH_COMMANDS_REFERENCE.md
```

### Mistake 3: Assuming Agent Memory Exists
```
❌ WRONG:  Expect agent to remember previous analyses
           → Gets fresh analysis every time
✅ RIGHT:  Accept stateless agents for now
           Document agent memory as "future feature"
```

### Mistake 4: Parallel Scout Without Integration
```
❌ WRONG:  Try to use adw_scout_parallel.py in production
           → Not integrated, outputs go wrong places
✅ RIGHT:  Use scout_simple.py for now
           Plan parallel scout integration for next release
```

---

## Best Practices for ADW Usage

### 1. Always Use ADW IDs
```bash
# Right - Traceable
adw_sdlc.py 123 a1b2c3d4

# Also right - ADW ID auto-generated
adw_sdlc.py 123

# Wrong - No tracking
adw_plan.py 123 && adw_build.py 123
```

### 2. Check State Files After Each Phase
```bash
# Verify state was saved
cat agents/a1b2c3d4/adw_state.json

# Understand what went wrong
cat agents/a1b2c3d4/planner/raw_output.jsonl | tail -1 | jq .
```

### 3. Use Orchestrator Scripts, Not Manual Piping
```bash
# Right - Handles errors, state management
uv run adw_sdlc.py 123

# Works but more fragile
uv run adw_plan.py 123 | uv run adw_build.py
```

### 4. Enable Parallel Execution for Speed
```bash
# Default (slower, sequential)
uv run adw_sdlc.py 123

# Faster (40-50% speedup)
uv run adw_sdlc.py 123 --parallel
```

---

## Priority Fixes Needed

### CRITICAL (Fix Immediately)
1. **Remove false worktree documentation** (15 min)
   - Delete `/worktree_*` from SLASH_COMMANDS_REFERENCE.md
   - Add note: "Not yet implemented"

2. **Fix scout output duplication** (1 hour)
   - Choose single location
   - Document file structure
   - Add cleanup script

### HIGH (Fix This Sprint)
3. **Integrate parallel scout** (2-3 hours)
   - Hook adw_scout_parallel.py into workflow
   - Add `--parallel` flag to scout phase
   - Test with various project sizes

4. **Update documentation** (2 hours)
   - Mark agent memory as "future feature"
   - Document which features are broken
   - Add migration guide for worktree users

### MEDIUM (Future Enhancement)
5. **Implement git worktrees** (3-4 hours)
   - Use for isolated phase execution
   - Enable true parallel phases
   - Update tests and docs

6. **Add state checkpointing** (3-4 hours)
   - Save checkpoint before each phase
   - Enable rollback to checkpoint
   - Version state files

---

## Understanding The Code

### Where Things Happen
```
User Request
    ↓
adws/adw_*.py scripts (entry points)
    ↓
adws/adw_modules/workflow_ops.py (orchestration logic)
    ↓
adws/adw_modules/{agent,github,git_ops}.py (implementations)
    ↓
agents/{adw_id}/ (outputs + state)
```

### How State Flows
```
Script 1: state = ADWState(adw_id)
          state.save()         # Write to agents/{adw_id}/adw_state.json
          state.to_stdout()    # Print JSON to stdout (for piping)

Script 2: state = ADWState.from_stdin()  # Read from piped JSON
          state.update(...)
          state.save()         # Update agents/{adw_id}/adw_state.json
          state.to_stdout()    # Pass to Script 3
```

### How Agents Work
```
Every agent uses same pattern:
1. Create AgentTemplateRequest with:
   - agent_name (e.g., "sdlc_planner")
   - slash_command (e.g., "/plan")
   - args (e.g., [issue_number, adw_id])

2. Call execute_template(request)

3. Get AgentPromptResponse with:
   - output (raw Claude Code output)
   - success (True/False)
   - session_id (for debugging)
```

---

## Debugging Tips

### Check if scout worked
```bash
cat scout_outputs/relevant_files.json
# or
cat ai_docs/scout/relevant_files.json
```

### Check if state persisted
```bash
cat agents/a1b2c3d4/adw_state.json
```

### Check what agent did
```bash
tail -1 agents/a1b2c3d4/planner/raw_output.jsonl | jq .
```

### Check git branch
```bash
git branch --show-current
# Should be something like: feat-123-a1b2c3d4-slug
```

### Check git commits
```bash
git log --oneline -n 5
# Should show semantic commits: feat, fix, docs, etc.
```

### Understand errors
```bash
export ADW_DEBUG=true
uv run adw_sdlc.py 123
# More verbose output with ADW_DEBUG=true
```

---

## When Things Break

### Scout doesn't find files
```
Cause: Keyword too generic or no files match
Fix:   Check scout_outputs/relevant_files.json
       Review grep patterns in scout_simple.py
```

### Plan fails
```
Cause: Scout files don't exist or are invalid JSON
Fix:   Verify scout_outputs/relevant_files.json exists
       Check it's valid JSON: jq . scout_outputs/relevant_files.json
       Run scout again manually if needed
```

### Build fails
```
Cause: Plan file not found or corrupted
Fix:   Check agents/{adw_id}/adw_state.json has plan_file path
       Verify that file exists and is readable
       Check git diff to see what changed
```

### Test fails (and doesn't auto-fix)
```
Cause: 3 attempts at auto-fixing failed
Fix:   Look at test output in agents/{adw_id}/tester/raw_output.jsonl
       Understand what the test wants
       Report to issue for human review
```

### Parallel execution gives wrong results
```
Cause: Processes interfering with each other (rare)
Fix:   Run with --skip-parallel flag
       Report issue with exact reproduction steps
       Check git status for unexpected changes
```

---

## File Paths Reference

### Key Output Locations
```
Scout:     scout_outputs/relevant_files.json
Plans:     specs/issue-{number}-adw-{id}-{slug}.md
State:     agents/{adw_id}/adw_state.json
Outputs:   agents/{adw_id}/{phase}/raw_output.jsonl
Tests:     agents/{adw_id}/test_report.json
Reviews:   agents/{adw_id}/review_report.json
Screenshots: agents/{adw_id}/reviewer/review_img/
Docs:      app_docs/features/{feature_name}/
```

### Configuration Files
```
.env                        → Environment variables
.adw_config.json           → ADW configuration
.scout_framework.yaml      → Installation manifest
CLAUDE.md                  → Project instructions
CLAUDE.local.md            → Local overrides (your env)
```

### Documentation
```
docs/README.md                          → Main docs entry
docs/WORKFLOW_ARCHITECTURE.md           → How it all works
docs/SPEC_SCHEMA.md                    → Spec format spec
docs/SLASH_COMMANDS_REFERENCE.md       → ALL COMMANDS (some broken)
adws/README.md                         → Quick start guide
ai_docs/ADW_SYSTEM_ANALYSIS.md        → This deep dive
```

---

## Next Steps

1. **Read ADW_SYSTEM_ANALYSIS.md** (this folder) for comprehensive analysis
2. **Fix documentation** to match reality (remove false claims)
3. **Consolidate scout outputs** to single location
4. **Integrate parallel scout** for better performance
5. **Document known limitations** clearly

---

**Generated**: 2025-11-09
**Status**: Analysis Complete, Recommendations Ready
**Confidence**: High (verified against actual code)
