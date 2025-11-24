---
description: Resume a compacted session by reading handoff files and restoring context. Use after /compact.
argument-hint: (no arguments)
---

# Session Resume

Automatically restore context after `/compact` by reading handoff files.

## Instructions

You are resuming a compacted session. Follow these steps:

### 1. Load Session Metadata

```bash
cat .current_session | python3 -m json.tool
```

Read this to understand:
- `session_id` - Current session UUID
- `short_id` - 8-char identifier for handoff filename
- `git_hash` - Last known commit
- `git_branch` - Current branch

### 2. Find and Read Latest Handoff

Look in `ai_docs/sessions/handoffs/` for the most recent handoff file.
The naming pattern is `MMDD-handoff-{short_id}.md` or `handoff-YYYY-MM-DD.md`.

Read the latest handoff file to understand:
- What was accomplished in the previous session
- What pending items remain
- Key files that were modified
- Framework insights and validation status

### 3. Check Git State

```bash
git status
git log --oneline -5
git branch
```

Verify the current state matches what the handoff describes.

### 4. Review CLAUDE.md

Read `CLAUDE.md` for the current framework routing rules and command menu.

### 5. Summarize and Ask

After loading context, provide a brief summary:
- Session ID and branch
- Last accomplishments (2-3 bullets)
- Pending priorities (2-3 bullets)

Then ask: "What would you like to work on next?"

## Automatic Context Loading

This command replaces the manual "copy paste after /compact" workflow.
Simply run `/session:resume` after compaction to restore full context.
