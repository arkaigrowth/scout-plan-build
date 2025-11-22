# Compaction Resume Prompt

**Use this after `/compact` to restore session context.**

Copy everything below the line and paste as your first message:

---

## SESSION RESUME - Scout-Plan-Build Framework

**Branch:** `feature/bitbucket-integration`
**Last Commit:** `0559753` - Git worktree parallelization + research + feedback
**Date:** 2024-11-22

### CRITICAL FILES TO READ FIRST

```
1. ai_docs/sessions/handoffs/handoff-2024-11-22-final.md  ← Full session summary
2. ai_docs/reviews/agentic-primitives-v2-review.md        ← V2 adoption roadmap
3. specs/git-worktree-parallel-agents.md                  ← Worktree spec
```

### WHAT WAS ACCOMPLISHED

✅ **Research Infrastructure** - `ai_docs/research/` created with videos/, articles/, etc.
✅ **Git Worktree Parallelization** - 4 new slash commands:
   - `/init-parallel-worktrees` `/run-parallel-agents` `/compare-worktrees` `/merge-worktree`
✅ **V2 Primitives Review** - Full architectural review with adoption recommendations
✅ **Feedback Structure** - `ai_docs/feedback/{predictions,outcomes,corrections}/` created
✅ **All committed** to `feature/bitbucket-integration` branch

### PENDING ACTION ITEMS (Prioritized)

| Priority | Item | Route | Effort |
|----------|------|-------|--------|
| 1 | Add CLAUDE.md routing decision tree | Quick | 30 min |
| 2 | Langfuse observability integration | ADW-Full | 2-3 hrs |
| 3 | Multi-model router spec | ADW-Plan | 1 hr |
| 4 | Test worktree commands | Quick | 15 min |

### FRAMEWORK ROUTING RULES

```
TRIVIAL (1-2 files, obvious)  → Quick Execution (just do it)
MODERATE (3-5 files)          → Quick ADW (/plan + /build)
COMPLEX (6+ files, new)       → Full ADW (/scout + /plan + /build)
RESEARCH/EXPLORE              → Task(Explore) agent
MULTIPLE APPROACHES           → /init-parallel-worktrees
```

### KEY INSIGHT FROM SESSION

The framework needs a **deterministic router** in CLAUDE.md showing which workflow to use based on task complexity. This makes the framework portable and reduces token waste.

### QUICK START COMMANDS

```bash
# Test worktree commands
/init-parallel-worktrees test-feature 2

# Or enhance CLAUDE.md with routing
# Add decision tree section showing task→workflow mapping

# Or start Langfuse ADW
/scout "Langfuse observability integration for adws modules"
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
