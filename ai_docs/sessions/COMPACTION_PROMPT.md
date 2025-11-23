# Compaction Resume Prompt

**Use this after `/compact` to restore session context.**

## How Session Tracking Works

Handoffs now use **Claude session IDs** for traceability:

| Component | Source | Example |
|-----------|--------|---------|
| Session ID | `.current_session` file (auto-updated) | `f67ada19-d93f-49c5-97fc-b71de9cb32e7` |
| Short ID | First 8 chars of session | `f67ada19` |
| Git Hash | Current commit | `35c29af` |
| Filename | `MMDD-handoff-{short_id}.md` | `1123-handoff-f67ada19.md` |

**Correlation chain**: Handoff filename → Session ID → Transcript JSONL → Full conversation

## How to Resume After /compact

**Option 1: Slash Command (Recommended)**
```
/session:resume
```
This automatically loads session metadata, finds the latest handoff, and restores context.

**Option 2: Manual Resume**
Just paste the quick resume section below into your next message.

---

### FRAMEWORK ROUTING RULES

```text
TRIVIAL (1-2 files, obvious)  → Quick Execution (just do it)
MODERATE (3-5 files)          → Quick ADW (/plan + /build)
COMPLEX (6+ files, new)       → Full ADW (/scout + /plan + /build)
RESEARCH/EXPLORE              → Task(Explore) agent
MULTIPLE APPROACHES           → /init-parallel-worktrees
```

### REFERENCE FILES

| Purpose | Path |
|---------|------|
| Main instructions | `CLAUDE.md` |
| Session helpers | `adws/adw_common.py` |
| Hook that writes session | `.claude/hooks/user_prompt_submit.py` |
| Framework manifest | `.scout_framework.yaml` |

---

## QUICK RESUME - 2025-11-23

**Branch:** main | **Commit:** da4855b | **Handoff:** `ai_docs/sessions/handoffs/handoff-2025-11-23.md`

### Done This Session (Major Cleanup)

- README complete revamp (value prop, decision tree, examples)
- Created `/session:resume` command
- ai_docs/ triage: 28 files → 4 in root (89% reduction)
- Path migration: 65 occurrences fixed (`agents/` → `scout_outputs/`)
- Guide consolidation: 3 docs → 2 (FRAMEWORK_USAGE archived)
- Added data flow diagram + future infrastructure docs
- Command naming standardized to colon notation
- Added hero banner image

### Pending Items

| Priority | Item | Effort |
|----------|------|--------|
| 1 | Fix 2025 date inconsistencies | 30 min |
| 2 | Document all 48 commands | 2 hrs |
| 3 | Style standardization | 1 hr |
| 4 | Implement feedback/ V2 loop | 4+ hrs |

### Key Insight

feedback/ folder is **future infrastructure** for V2 Feedback Loop (Agentic Primitives V2).
Don't delete empty predictions/ and outcomes/ folders - they're scaffolding.

### Framework Validated

ADW + parallel subagents used throughout. Pattern: `/plan_w_docs_improved` → `/workflow:build_adw`
