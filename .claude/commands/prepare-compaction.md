<!-- risk: mutate-local -->
<!-- auto-invoke: gated -->

# Prepare for Compaction

Prepare the session for context compaction by saving state and creating resume artifacts.

**When to use:** Before running `/compact` when context is getting low (~20-30% remaining).

## Execution Steps

### 1. Gather Session State

Collect information about the current session:
- What was accomplished (check recent git commits)
- What's pending (any uncommitted work, stated goals)
- Which files were created/modified
- Current branch and commit status

### 2. Update Handoff Document

Create or update the handoff file at `ai_docs/sessions/handoffs/handoff-{DATE}.md` with:

```markdown
# Session Handoff - {YYYY-MM-DD}

**Branch:** {current branch}
**Last Commit:** {commit hash} - {commit message}
**Context at Handoff:** {approximate % remaining}

## Accomplished This Session
- {List of completed items}

## Pending Items
| Priority | Item | Route | Effort |
|----------|------|-------|--------|
| 1 | {item} | {Quick/ADW} | {time} |

## Key Files Modified
- {list of important files}

## Next Steps
{Clear instructions for continuation}
```

### 3. Update Compaction Prompt

Update `ai_docs/sessions/COMPACTION_PROMPT.md` with:
- Current branch and commit info
- Critical files to read first
- Accomplished items
- Pending action items with routing
- Reference file paths
- Quick start commands

The compaction prompt should be copy-paste ready for use after `/compact`.

### 4. Commit Everything

Stage and commit all session artifacts:

```bash
git add ai_docs/sessions/ specs/ .claude/commands/
git add -u  # Stage modified tracked files
git commit -m "chore: Prepare session for compaction - {brief summary}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 5. Report Ready Status

Output a clear summary:

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPACTION READY                          │
└─────────────────────────────────────────────────────────────┘

✅ Handoff updated: ai_docs/sessions/handoffs/handoff-{DATE}.md
✅ Compaction prompt ready: ai_docs/sessions/COMPACTION_PROMPT.md
✅ All changes committed: {commit hash}

NEXT STEPS:
1. Run: /compact
2. Open: ai_docs/sessions/COMPACTION_PROMPT.md
3. Copy everything below the "---" line
4. Paste as your first message in the new context

The new session will have full context of:
- What was accomplished
- What's pending
- Which files to read
- Exact next steps
```

## Important Notes

- Always commit before compaction to preserve work
- The compaction prompt is designed to be token-efficient
- Handoff files accumulate (don't delete old ones - they're history)
- After compaction, Claude should read the handoff FIRST

## Framework Integration

This command supports the session lifecycle:
```
Session Start → Work → /prepare-compaction → /compact → Resume
      ↑                                                    │
      └────────────────────────────────────────────────────┘
```

Related commands:
- `/sc:save` - Serena MCP session save (if available)
- `/sc:load` - Serena MCP session load (if available)
