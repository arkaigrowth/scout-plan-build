# Compaction Resume Prompt

**Use this after `/compact` to restore session context.**

Copy everything below the line and paste as your first message:

---

## SESSION RESUME - Scout-Plan-Build Framework

**Branch:** `feature/bitbucket-integration`
**Last Commit:** `35c29af` - Phase 1 Agent Box state management foundation
**Date:** 2025-11-23

### CRITICAL FILES TO READ FIRST

```text
1. ai_docs/sessions/handoffs/1123-handoff-565e274.md      ← Today's full session
2. ai_docs/architecture/AGENT_BOX_INTEGRATION_DECISION.md ← Phase 2/3 plan
3. specs/phase1-agent-box-state-management.md             ← What we implemented
4. CLAUDE.md                                              ← Framework v4 routing
```

### WHAT WAS ACCOMPLISHED

✅ **Framework v4** - Deterministic routing, risk classification (🟢🟡🔴), command audit
✅ **Phase 1 State Management** - Run IDs (`MMDD-slug-hash`), agent_runs/ directory, templates
✅ **Duplicate Directories Fixed** - Consolidated ai_docs/scout/ → scout_outputs/archive/
✅ **Agent Box Research** - Integration decision doc, implementation spec
✅ **All committed** - 2 major commits to `feature/bitbucket-integration`

### PENDING ACTION ITEMS (Prioritized)

| Priority | Item | Route | Effort |
|----------|------|-------|--------|
| 1 | Create RunManager class | Direct implementation | 30 min |
| 2 | Create /init-framework command | Direct or ADW | 20 min |
| 3 | Integrate handoffs with RunManager | Quick enhancement | 15 min |
| 4 | Fix scout commands (Task tool) | Investigation + fixes | 1 hr |
| 5 | Add risk headers to commands | Quick edits | 20 min |

**Future**: Wrap handoff process in state management (track sessions with RunManager)

### FRAMEWORK ROUTING RULES

```text
TRIVIAL (1-2 files, obvious)  → Quick Execution (just do it)
MODERATE (3-5 files)          → Quick ADW (/plan + /build)
COMPLEX (6+ files, new)       → Full ADW (/scout + /plan + /build)
RESEARCH/EXPLORE              → Task(Explore) agent
MULTIPLE APPROACHES           → /init-parallel-worktrees
```

### KEY INSIGHTS FROM SESSION

1. **Scout commands broken** - They reference a Task tool that doesn't exist in standard Claude Code
2. **ADW needs state** - Build command expects state files from plan phase
3. **Run ID format matters** - We chose `MMDD-slug-hash` for user-friendliness vs Agent Box's long format
4. **Framework v4 working** - Deterministic routing reduces token waste and ambiguity

### QUICK START COMMANDS

```bash
# Test the run ID generation we built
python3 -c "from adws.adw_common import generate_run_id; print(generate_run_id('test', 'resume'))"

# Continue with RunManager implementation
vim agents/supervisor.py  # Create from spec Step 3

# Or test parallel worktrees
/init-parallel-worktrees test-feature 2
```

### REFERENCE FILES

| Purpose | Path |
|---------|------|
| Main instructions | `CLAUDE.md` |
| Framework manifest | `.scout_framework.yaml` |
| Directory structure | `DIRECTORY_STRUCTURE.md` |
| V2 primitives | `ai_docs/reference/AGENTIC_ENGINEERING_PRIMITIVES_V2.md` |
| Worktree spec | `specs/git-worktree-parallel-agents.md` |
| V2 review | `ai_docs/reviews/agentic-primitives-v2-review.md` |
| Full handoff | `ai_docs/sessions/handoffs/handoff-2024-11-22-final.md` |

---

**Please read the handoff file first, then ask what I'd like to work on next.**
