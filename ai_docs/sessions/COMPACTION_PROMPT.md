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

## Template: Copy Below Line After /compact

---

## SESSION RESUME - Scout-Plan-Build Framework

**Session:** `{SESSION_SHORT_ID}` (full: `{FULL_SESSION_ID}`)
**Branch:** `{BRANCH_NAME}`
**Last Commit:** `{GIT_HASH}` - {COMMIT_MESSAGE}
**Date:** {DATE}

### CRITICAL FILES TO READ FIRST

```text
1. ai_docs/sessions/handoffs/{MMDD}-handoff-{SESSION_SHORT}.md  ← This session's handoff
2. .current_session                                              ← Session metadata (JSON)
3. CLAUDE.md                                                     ← Framework v4 routing
```

### SESSION PROVENANCE

Check `.current_session` for:
```json
{
  "session_id": "{FULL_UUID}",
  "short_id": "{8_CHARS}",
  "git_hash": "{SHORT_HASH}",
  "git_branch": "{BRANCH}",
  "timestamp": "{ISO8601}"
}
```

### FRAMEWORK ROUTING RULES

```text
TRIVIAL (1-2 files, obvious)  → Quick Execution (just do it)
MODERATE (3-5 files)          → Quick ADW (/plan + /build)
COMPLEX (6+ files, new)       → Full ADW (/scout + /plan + /build)
RESEARCH/EXPLORE              → Task(Explore) agent
MULTIPLE APPROACHES           → /init-parallel-worktrees
```

### QUICK VERIFICATION COMMANDS

```bash
# Check current session info
cat .current_session | python3 -m json.tool

# Test provenance helpers
python3 -c "from adws.adw_common import get_current_session, get_provenance_block; print(get_provenance_block('markdown'))"

# Generate handoff filename
python3 -c "from adws.adw_common import generate_handoff_filename; print(generate_handoff_filename())"
```

### REFERENCE FILES

| Purpose | Path |
|---------|------|
| Main instructions | `CLAUDE.md` |
| Session helpers | `adws/adw_common.py` (get_current_session, get_provenance_block) |
| Hook that writes session | `.claude/hooks/user_prompt_submit.py` |
| Agent run templates | `agent_runs/.template/` |
| Framework manifest | `.scout_framework.yaml` |

---

**Please read the latest handoff file first, then ask what I'd like to work on next.**
