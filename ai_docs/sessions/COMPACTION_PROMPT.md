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

## QUICK RESUME - 2024-11-23

**Branch:** main | **Commit:** 9ac852b | **Handoff:** `ai_docs/sessions/handoffs/handoff-2024-11-23.md`

### Done This Session
- Git cleanup: .DS_Store, ARCHIVE_OLD, logs (131MB freed)
- Doc audit: 131 files → ~115 files (16 deleted/consolidated)
- Phase 1+3: Skills docs (3→1), parallelization (4→1), config (3→2)

### Next Priority: Phase 4 Diagrams
- 8 files in docs/ need diagrams
- 22 files in ai_docs/ need diagrams
- Key targets: INSTALLATION_GUIDE, SKILLS_ARCHITECTURE, TEAM_ONBOARDING

### Framework Validated
ADW workflow used 3x successfully. Use `/plan_w_docs_improved` → `/build_adw` pattern.
