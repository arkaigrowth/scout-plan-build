# Context Compaction Quick Reference

**For developers implementing pre-compaction workflows in Claude Code projects**

---

## What /compact Actually Does

NOT:
- Summarize automatically
- Compress code/docs
- Delete git history
- Reduce codebase

DOES:
- Clear conversation history
- Create checkpoint in git  
- Save transcript as JSONL
- Enable fresh 200K token context

---

## The 5-Step Preparation Protocol

### 1. Gather Session State (5 min)
```bash
git log --oneline -5
git status
git branch
```

### 2. Create Handoff Document (5 min)
**Path**: `ai_docs/sessions/handoffs/handoff-{DATE}.md`

```markdown
# Session Handoff - {DATE}

**Branch:** {branch} | **Commit:** {hash}
**Context at Handoff:** ~{percentage}%

## Accomplished This Session
- Item 1 (with file references)
- Item 2 (with commit hashes)

## Pending Items
| Priority | Item | Route | Effort |
|----------|------|-------|--------|
| 1 | Action 1 | Quick/ADW | 30 min |
| 2 | Action 2 | ADW | 2 hrs |

## Key Files Modified
- ai_docs/build_reports/...
- specs/auth.md
- src/auth.py (lines 45-120)
```

### 3. Update Compaction Prompt (5 min)
**Path**: `ai_docs/sessions/COMPACTION_PROMPT.md`

Keep framework context at top, session-specific at bottom.
Design for copy-paste into fresh context.

### 4. Commit Everything (3 min)
```bash
git add ai_docs/sessions/ specs/ .claude/commands/
git add -u
git commit -m "chore: Prepare session for compaction - {summary}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 5. Report Ready Status (2 min)
Show:
- Handoff file created
- Commit hash
- Next steps (run /compact)

---

## What to Preserve vs Discard

### PRESERVE (Use in Handoff)
- Accomplishments with file:line references
- Pending items ranked by priority
- Current git state (branch, commits)
- Critical blockers (full detail)
- Next immediate action

**Token budget**: 200-300 tokens

### DISCARD (Not in Handoff)
- Code snippets → Use file paths instead
- Error traces → Use file:line pointers
- Conversation filler → Use decision outcomes
- Resolved issues → Link to git commits
- Duplicate info → Consolidate to one row

---

## Information Preservation Strategy

**Don't summarize. Use pointers.**

```
Handoff (300 tokens)
  ↓
Points to files (ai_docs/build_reports/...)
  ↓
File contents loaded on-demand (fresh context reads as needed)
  ↓
Git history (git show {hash} when needed)
```

Result: Zero information loss, maximum available tokens.

---

## Pre-Compaction Checklist

```
Preparation (20 min)
  [ ] Run /session:prepare-compaction
  [ ] Review handoff for clarity
  [ ] Verify file paths are correct
  
Validation (10 min)
  [ ] git branch (confirm correct branch)
  [ ] git status (must be clean)
  [ ] Handoff file is copy-paste ready

Finalization (5 min)
  [ ] Copy everything after "---" separator
  [ ] Store in accessible location
  [ ] Ready for /compact
```

---

## Critical Rules

1. **ALWAYS COMMIT FIRST** - Uncommitted work is lost
2. **Make handoffs copy-paste ready** - No manual edits needed
3. **Use file paths, not explanations** - Point to files
4. **Include routing column** - Tell next context which workflow
5. **Separate completed from pending** - Clear status

---

## After Compaction (/compact)

In new context:

1. Paste the COMPACTION_PROMPT.md section (30 sec)
2. Read handoff summary (2 min)
3. Understand pending items (1 min)
4. Load detailed context on-demand:
   ```bash
   cat ai_docs/build_reports/...
   cat specs/feature.md
   git show {hash}
   ```

**Result**: Full context available without token waste.

---

## Real Example

**Before Compaction** (20% remaining):
- 7 commits made
- 18 files modified
- 1200+ lines written
- Can't fit in new context

**Handoff** (300 tokens):
```markdown
# Session Handoff - 2025-11-23

**Branch:** main | **Commit:** da4855b
**Context:** ~20%

## Accomplished
- README revamp (new structure, diagrams)
- ai_docs/ triage (28 → 4 files, 89% reduction)
- Path migration (65 occurrences, see commits: cbd2009, ded3900)

## Pending
| 1 | Fix date inconsistencies | Quick | 30 min |
| 2 | Document 48 commands | ADW | 2 hrs |
| 3 | V2 feedback loop | ADW-Full | 4 hrs |

## Key Files
- README.md (rewritten)
- ai_docs/README.md (data flow)
- .claude/commands/session/resume.md (new)
```

**New Context** (190K+ tokens available):
- Reads handoff (30 sec)
- Understands state
- Loads detailed context on-demand
- Works on priority 1

---

## Why This Works

1. **Structure matters more than prose** - Tables > paragraphs
2. **Pointers scale infinitely** - File path costs ~5 tokens, contains 1000x info
3. **Fresh context is valuable** - 190K+ tokens beats rich summary
4. **Git is already there** - Full history via `git show`
5. **Files are organized** - File system structure IS information

---

## Optimal Frequency

- **Trigger**: 20-30% context remaining (~150K tokens used)
- **Frequency**: Every 60-80 minutes
- **Overhead**: 35 minutes (prep + resume)
- **Benefit**: 190K fresh tokens available

At 1000 tokens/minute velocity, you gain 60K+ tokens of work capacity.

---

## Success Metrics

- [ ] Zero information loss
- [ ] Fresh context can work immediately (no ramp-up)
- [ ] All pending items are actionable
- [ ] No redundant information
- [ ] File paths are accurate
- [ ] Routing guidance is clear
- [ ] Handoff is copy-paste ready

