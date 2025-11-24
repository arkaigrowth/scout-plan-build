---
description: Prepare session for context compaction with intelligent extraction and user-controlled selection.
argument-hint: (no arguments)
---

<!-- risk: mutate-local -->
<!-- auto-invoke: gated -->

# Prepare for Compaction (v2 - Interactive Selective)

Prepare the session for context compaction with **intelligent extraction** and **user-controlled selection** of what to preserve in the handoff.

**When to use:** Before running `/compact` when context is getting low (~20-30% remaining).

**Key improvement:** Uses exclusion-first UX - everything included by default, user removes what's not needed.

---

## Phase 1: Extract Session Actions (Haiku Agent)

Spawn a lightweight agent to analyze session activity without burning main context:

```
Task(
  subagent_type="Explore",
  description="Extract session actions for compaction",
  prompt="Analyze the session activity in this project. Read these sources:

  1. run_log.md (if exists) - contains timestamped tool calls
  2. git log --oneline -20 - recent commits
  3. git diff --stat HEAD~5 - files changed recently

  Extract and categorize into JSON:
  {
    \"code_changes\": [
      {\"path\": \"file.py\", \"operation\": \"Write|Edit\", \"summary\": \"brief description\"}
    ],
    \"research\": [
      {\"type\": \"Grep|Read|WebFetch\", \"target\": \"what was searched\", \"count\": N}
    ],
    \"decisions\": [
      {\"commit\": \"abc123\", \"message\": \"decision made\", \"impact\": \"high|medium|low\"}
    ],
    \"tasks\": [
      {\"agent_type\": \"Explore|general-purpose\", \"description\": \"what it did\"}
    ],
    \"token_estimates\": {
      \"code_changes\": 1500,
      \"research\": 800,
      \"decisions\": 400,
      \"tasks\": 600
    }
  }

  Focus on accuracy over completeness. Group similar items.
  Return ONLY the JSON, no explanation."
)
```

Store the result for Phase 2.

---

## Phase 2: User Selection (Exclusion-First)

Present the extracted data to user with **exclusion-first** UX (include everything by default):

### Question 1: Category-Level Exclusions

```
AskUserQuestion([
  {
    "question": "Exclude any categories entirely from handoff?",
    "header": "Exclude",
    "multiSelect": true,
    "options": [
      {
        "label": "Code changes",
        "description": "{N} files, ~{tokens} tokens - File modifications and creations"
      },
      {
        "label": "Research activities",
        "description": "{N} operations, ~{tokens} tokens - Searches and reads"
      },
      {
        "label": "Decisions/commits",
        "description": "{N} items, ~{tokens} tokens - Git commits and choices made"
      },
      {
        "label": "Task delegations",
        "description": "{N} agents, ~{tokens} tokens - Subagent work"
      }
    ]
  }
])
```

**Default behavior:** If user selects nothing, ALL categories are included.

### Question 2: Item-Level Exclusions (Largest Items)

Based on Phase 1 extraction, identify the 3-4 largest token consumers:

```
AskUserQuestion([
  {
    "question": "Exclude any specific large items?",
    "header": "Large Items",
    "multiSelect": true,
    "options": [
      {
        "label": "{largest_file.md}",
        "description": "~{tokens} tokens - {brief context}"
      },
      {
        "label": "{second_largest}",
        "description": "~{tokens} tokens - {brief context}"
      },
      {
        "label": "{third_largest}",
        "description": "~{tokens} tokens - {brief context}"
      },
      {
        "label": "Include all",
        "description": "Don't exclude any individual items"
      }
    ]
  }
])
```

### Question 3: Next Session Priority

```
AskUserQuestion([
  {
    "question": "Priority focus for next session?",
    "header": "Priority",
    "multiSelect": false,
    "options": [
      {
        "label": "Continue current",
        "description": "Resume exactly where we left off"
      },
      {
        "label": "New feature",
        "description": "Start fresh feature work"
      },
      {
        "label": "Fixes/debt",
        "description": "Address bugs or tech debt"
      },
      {
        "label": "Docs/cleanup",
        "description": "Documentation or code cleanup"
      }
    ]
  }
])
```

---

## Phase 3: Generate Filtered Handoff

Based on user selections, create the handoff document.

### 3.1 Gather Git State

```bash
git status
git log --oneline -5
git branch --show-current
```

### 3.2 Create Handoff Document

Write to `ai_docs/sessions/handoffs/handoff-{YYYY-MM-DD}.md`:

```markdown
# Session Handoff - {YYYY-MM-DD}

**Branch:** {current branch}
**Last Commit:** {hash} - {message}
**Context at Handoff:** ~{N}% remaining
**Priority for Next Session:** {user's selection from Q3}

## Accomplished This Session
{Only items from categories NOT excluded in Q1}
{Exclude specific items selected in Q2}

### Code Changes
- `{file:line}` - {brief description}

### Decisions Made
- {commit hash}: {decision summary}

### Research Completed
- Searched for: {patterns} → Found: {results summary}

## Pending Items
| Priority | Item | Route | Effort |
|----------|------|-------|--------|
| 1 | {item} | Quick/ADW | {est} |

## Key File Pointers
{Use file:line references, NOT inline code}
- `adws/adw_modules/agent.py:31-58` - Model selection mapping
- `ai_docs/research/COMPACTION_RESEARCH.md` - Full research doc

## Quick Start for Next Session
1. Run: `/session:resume`
2. Or manually read this file + CLAUDE.md
3. First action: {based on priority selection}
```

### 3.3 Update COMPACTION_PROMPT.md

Write to `ai_docs/sessions/COMPACTION_PROMPT.md`:

```markdown
# Post-Compaction Resume Prompt

Copy everything below this line after running /compact:

---

I'm resuming a compacted session. Please:

1. Read `ai_docs/sessions/handoffs/handoff-{DATE}.md`
2. Read `CLAUDE.md` for framework routing
3. Check `git status` and `git log --oneline -3`

**Priority:** {user's selection}

**Key context:**
- Branch: {branch}
- Last commit: {hash}
- {2-3 bullet accomplishments}

**Next action:** {specific first step based on priority}
```

---

## Phase 4: Commit and Report

### 4.1 Stage and Commit

```bash
git add ai_docs/sessions/
git add -u  # Modified tracked files
git commit -m "chore: Prepare session for compaction

Included: {categories kept}
Excluded: {categories/items removed}
Priority: {next session focus}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 4.2 Report Ready Status

```
┌─────────────────────────────────────────────────────────────┐
│              COMPACTION READY (Selective v2)                │
└─────────────────────────────────────────────────────────────┘

📊 Extraction Summary:
   • Code changes: {N} items ({included|excluded})
   • Research: {N} items ({included|excluded})
   • Decisions: {N} items ({included|excluded})
   • Tasks: {N} items ({included|excluded})

📝 Handoff created: ai_docs/sessions/handoffs/handoff-{DATE}.md
📋 Resume prompt: ai_docs/sessions/COMPACTION_PROMPT.md
✅ Committed: {hash}

🎯 Next Session Priority: {user's selection}

NEXT STEPS:
1. Run: /compact
2. In new context, run: /session:resume
   (Or paste from COMPACTION_PROMPT.md)

Token estimate saved: ~{N} tokens (from exclusions)
```

---

## Important Notes

- **Exclusion-first UX**: Everything included by default, user removes noise
- **Haiku extraction**: Offloads parsing to preserve main context
- **file:line pointers**: References instead of inline code (infinite scalability)
- **Always commit before compact**: Uncommitted work is lost!
- **Handoff history**: Don't delete old handoffs - they're useful history

## Fallback: Non-Interactive Mode

If AskUserQuestion is unavailable or user wants quick compaction:

```bash
/prepare-compaction --quick
```

Skips user selection, includes everything, generates standard handoff.

---

## Framework Integration

```
Session Lifecycle (v2):
┌─────────┐    ┌──────────────────────────────────┐    ┌─────────┐
│ Session │───→│ /prepare-compaction              │───→│/compact │
│  Start  │    │  1. Haiku extracts actions       │    │ (wipe)  │
└─────────┘    │  2. User selects what to keep    │    └────┬────┘
               │  3. Filtered handoff generated   │         │
               └──────────────────────────────────┘         │
                                                            ▼
               ┌──────────────────────────────────┐    ┌─────────┐
               │ /session:resume                  │←───│   New   │
               │ Reads handoff, restores context  │    │ Context │
               └──────────────────────────────────┘    └─────────┘
```

Related commands:
- `/session:resume` - Restore context after compaction
- `/session:start` - Initialize new session
- `/sc:save` - Serena MCP session save (if available)
