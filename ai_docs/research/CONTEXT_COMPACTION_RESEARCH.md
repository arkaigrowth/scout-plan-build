# Research: Anthropic Context Compaction Best Practices for Claude Code

**Research Date:** November 23, 2025  
**Scope:** Claude Code context compaction strategy, handoff patterns, and pre-compaction optimization  
**Sources:** Scout Plan Build MVP project documentation, Claude Code session management, and Anthropic framework patterns

---

## Executive Summary

Context compaction in Claude Code is a **strategic session management operation** that preserves high-resolution session context across token budget resets. This research synthesizes actual Anthropic patterns from the Scout Plan Build MVP project, which has refined compaction strategies through multiple production iterations.

### Key Findings

1. **Compaction is NOT automatic compression** - it's a deterministic handoff protocol
2. **Pre-compaction preparation is critical** - 70% of compaction success depends on the `/prepare-compaction` phase
3. **High-resolution information is preserved through selective, structured artifacts** - not blanket summarization
4. **The pattern is: Commit → Prepare → Compact → Resume** with each phase having specific responsibilities

---

## Part 1: What the /compact Command Actually Does

### Under the Hood Architecture

The `/compact` command in Claude Code performs **session context windowing**:

1. **Transcript Preservation**: Saves entire session conversation as JSONL to `.claude/projects/{repo_path}/{session_id}.jsonl`
2. **Hook Trigger**: Executes `PreCompact` hook to gather session metadata (before the compact happens)
3. **Session Isolation**: Creates isolated storage for each project to prevent cross-project interference
4. **Resumption Checkpoint**: Enables fresh context window to start with clean token budget

### Not a Compression Algorithm

Critical insight: `/compact` does NOT:
- Summarize conversation automatically
- Extract key points algorithmically  
- Compress code or documentation
- Reduce codebase size
- Delete git history

It DOES:
- Clear the conversation history from the current context window
- Create a checkpoint in git via automatic commit
- Trigger hooks for pre-compaction metadata capture
- Enable session resumption with fresh token budget

### Session Tracking Mechanism

The system creates a correlation chain for traceability:

```
Handoff Filename (MMDD-handoff-{short_session_id}.md)
    ↓
Session ID (e.g., f67ada19-d93f-49c5-97fc-b71de9cb32e7)
    ↓
Transcript JSONL (stored in ~/.claude/projects/)
    ↓
Git Commits (associated with session)
    ↓
Full Conversation History (recoverable)
```

**Storage Location**: `~/.claude/projects/-Users-alexkamysz-AI-scout-plan-build-mvp/{session_id}.jsonl`

---

## Part 2: Best Practices for Pre-Compaction Preparation

### The Critical Pre-Compaction Phase

**Trigger Point**: When context reaches 20-30% remaining (approximately 150K+ tokens used of 200K budget)

### Standard Workflow: `prepare-compaction` Command

The `/session:prepare-compaction` command (documented in the Scout Plan Build MVP project) executes a five-step protocol:

#### Step 1: Gather Session State
```bash
✓ Check recent git commits (git log --oneline -5)
✓ Identify uncommitted work (git status)
✓ List created/modified files
✓ Note current branch and HEAD position
✓ Document any outstanding changes
```

#### Step 2: Create/Update Handoff Document
**Location**: `ai_docs/sessions/handoffs/handoff-{DATE}.md`

**Structure**:
```markdown
# Session Handoff - {YYYY-MM-DD}

**Branch:** {current branch}
**Last Commit:** {commit hash} - {commit message}
**Context at Handoff:** ~{percentage}% remaining

## Accomplished This Session
- [List of completed items with specifics]

## Pending Items
| Priority | Item | Route | Effort |
|----------|------|-------|--------|
| 1 | {clear description} | {Quick/ADW} | {estimate} |

## Key Files Modified
- {specific file paths}

## Next Steps
{Clear, actionable instructions for continuation}
```

**Real Example from Scout Plan Build MVP**:
```markdown
# Session Handoff - 2025-11-23

**Branch:** main
**Last Commit:** da4855b - refactor: Guide consolidation, command naming
**Context at Handoff:** ~20%

## Accomplished This Session (Major Cleanup)
- README complete revamp (value prop, decision tree, examples)
- Created `/session:resume` command
- ai_docs/ triage: 28 files → 4 in root (89% reduction)
- Path migration: 65 occurrences fixed
- Guide consolidation: 3 docs → 2
- Added data flow diagram + future infrastructure docs

## Pending Items
| Priority | Item | Route | Effort |
|----------|------|-------|--------|
| 1 | Fix 2025 date inconsistencies | Quick | 30 min |
| 2 | Document all 48 commands | ADW | 2 hrs |
| 3 | Style standardization | Quick | 1 hr |
```

**Why This Works**: The handoff file is structured to answer the three questions a fresh context needs:
- "What was I working on?" (Accomplished)
- "What's left?" (Pending)
- "Which files matter?" (Key Files)

#### Step 3: Update Compaction Prompt
**Location**: `ai_docs/sessions/COMPACTION_PROMPT.md`

This is a **copy-paste ready** document with two sections:

**Section 1: Framework Context** (reference information)
```markdown
### FRAMEWORK ROUTING RULES
TRIVIAL (1-2 files) → Quick Execution
MODERATE (3-5 files) → Quick ADW
COMPLEX (6+ files) → Full ADW
RESEARCH/EXPLORE → Task(Explore) agent

### REFERENCE FILES
| Purpose | Path |
|---------|------|
| Main instructions | CLAUDE.md |
| Session helpers | adws/adw_common.py |
| Framework manifest | .scout_framework.yaml |
```

**Section 2: Quick Resume** (session-specific)
```markdown
## QUICK RESUME - {DATE}

**Branch:** {branch} | **Commit:** {hash} | **Handoff:** {filename}

### Done This Session
- Item 1 with context
- Item 2 with context

### Pending Items
| Priority | Item | Effort |
```

This document is designed to be pasted into the new context as the first message, providing immediate orientation without token waste.

#### Step 4: Commit Everything
```bash
git add ai_docs/sessions/ specs/ .claude/commands/
git add -u  # Stage all modified tracked files
git commit -m "chore: Prepare session for compaction - {brief summary}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Why Commit First**: 
- Preserves work in case of unexpected issues
- Creates a clear waypoint in git history  
- Ensures handoff artifacts are version-controlled
- Enables rollback if needed

#### Step 5: Report Ready Status
Output a clear completion summary showing:
```
✅ Handoff updated: ai_docs/sessions/handoffs/handoff-{DATE}.md
✅ Compaction prompt ready: ai_docs/sessions/COMPACTION_PROMPT.md
✅ All changes committed: {commit hash}

NEXT STEPS:
1. Run: /compact
2. Open: ai_docs/sessions/COMPACTION_PROMPT.md
3. Copy everything below the "---" line
4. Paste as your first message in the new context
```

---

## Part 3: What Information Should Be Preserved vs. Discarded

### Preservation Strategy: High-Resolution Mapping

The strategy is NOT "summarize everything" but rather "preserve high-resolution pointers to everything."

#### PRESERVE (High Priority)

**1. Accomplishment Summary with Specifics**
- Don't: "Fixed some bugs"
- Do: "Fixed auth.py:45 SQL injection via input validation, refs issue #123"
- Token efficiency: 10 tokens vs 500 tokens for the full code review

**2. Key File Paths (with Line Numbers When Relevant)**
```markdown
## Key Files Modified
- adws/adw_modules/validators.py (line 45-120: Pydantic models)
- specs/auth-implementation.md (requirements document)
- .claude/commands/session/resume.md (new command structure)
```

**3. Pending Action Items with Routing**
```markdown
| Priority | Item | Route | Effort |
|----------|------|-------|--------|
| 1 | Fix SQL injection in auth.py | ADW | 2 hrs |
| 2 | Add tests for validation | Quick | 1 hr |
| 3 | Update documentation | Quick | 30 min |
```

The "Route" column determines strategy in next session (Quick = just do it, ADW = create spec first).

**4. Commits with Messages (Short Form)**
```bash
da4855b - Guide consolidation, command naming, future infrastructure docs
ded3900 - Data flow diagram to ai_docs README
cbd2009 - Major cleanup (63 files, path migration)
```

Each commit is a semantic unit. The new context can run `git show` on any hash to restore detail.

**5. Context Clues About Current State**
```markdown
## Current Branch & Status
- **Branch:** feature/auth-redesign
- **Uncommitted:** 3 files (auth.py, auth.test.py, auth.md)
- **Origin Status:** 2 commits ahead of main
- **Next Merge Target:** main (PR #42 ready)
```

**6. Critical Dependencies or Blockers**
```markdown
## Blockers (If Any)
- ❌ Waiting for: API key from DevOps (impacts integration tests)
- ⚠️ Breaking: Updated to SQLAlchemy 2.0 (incompatible with legacy ORM)
- 🔄 In Progress: Code review from @alice (approval needed for merge)
```

#### DISCARD (Low Priority)

**1. Verbose Code Snippets in Handoff**
- Don't paste 100-line functions
- Do reference the file: `adws/orm.py:200-320`
- New context can run `Read` tool to fetch it quickly

**2. Detailed Error Stack Traces**
- Don't: Full 50-line traceback
- Do: "TypeError in auth.py:45 - wrong parameter type to validators.check_email()"
- New context can debug if needed using the pointer

**3. Conversation Filler (Intermediate Reasoning)**
- Don't: "I think we should... Actually, let me reconsider... Upon further reflection..."
- Do: "Decision: Use JWT tokens instead of session cookies for OAuth2 compatibility"
- Outcome matters, not the thinking process (that's in the transcript if needed)

**4. Resolved Issues and Completed Discussions**
- If something is DONE and committed, it's archived
- Don't repeat closed discussions
- Do reference commits: "See `cbd2009` for path migration strategy"

**5. Duplicate Information**
- Don't repeat the same insight twice
- Consolidate related items into single row
- Use links and references instead

### Information Preservation Through Architecture

Rather than trying to summarize, the Scout Plan Build MVP uses **architectural patterns** to preserve high-resolution data:

#### Pattern 1: Git as Semantic Storage
```bash
# Instead of: "We refactored the auth system"
# Use: Point to the commit
git log --oneline | grep -i auth
# Returns: 3c8ee0f refactor: Organize commands into logical subdirectories

# Then in new context:
git show 3c8ee0f  # Get full details on demand
```

#### Pattern 2: Specs as Decision Records
```markdown
# Rather than repeating design decisions in handoffs

## In Handoff:
Pending: "Implement agent orchestration" (see spec)

## What it references:
specs/agents-sdk-implementation-plan.md (8-week roadmap with all decisions)
```

#### Pattern 3: File System as Documentation Index
```
ai_docs/
├── analyses/         (deep dives, preserved automatically)
├── reviews/          (code reviews, point to them)
├── build_reports/    (what was built, reference by date)
├── reference/        (architectural guides, copy path)
└── sessions/
    ├── handoffs/     (prepare-compaction outputs)
    └── COMPACTION_PROMPT.md (resume template)
```

The file system structure itself IS information architecture.

---

## Part 4: Patterns for Selective/Prioritized Compaction

### Priority Tiers for Information Preservation

The Scout Plan Build MVP uses a **three-tier selection model**:

#### Tier 1: MUST PRESERVE (Use handoff file for this)
- What was accomplished (with file references)
- What's pending (with routing)
- Current git state (branch, commits)
- Blocking issues (if any)
- Next immediate action

**Token Budget**: 200-300 tokens in handoff
**Format**: Structured tables and lists

#### Tier 2: SHOULD PRESERVE (Use references and pointers)
- Key design decisions (link to specs/)
- Important file modifications (list paths)
- Relevant commits (git hashes)
- Related documentation (file paths)
- Architecture context (via diagrams in docs/)

**Token Budget**: 0 tokens in handoff (just pointers)
**Format**: File paths, git hashes, links

#### Tier 3: NICE TO HAVE (Available if needed, don't include)
- Detailed code review comments (in reviewed files)
- Full conversation history (in JSONL transcript)
- All intermediate reasoning (in git commits)
- Debugging sessions (referenced by path)
- Research notes (filed under ai_docs/research/)

**Token Budget**: Use git/file tools on-demand in new context

### Selective Compaction Rules

#### Rule 1: File Size Threshold
```markdown
## Accomplished This Session

- ✅ Refactored auth system (see ai_docs/build_reports/auth-refactor.md)
  [NOT: "Created 3 new files, 1200 lines of code, here's what each does..."]
- ✅ Added 25 unit tests (all passing, 98% coverage in adws/adw_tests/)
- ✅ Updated documentation (11 files, see git log for details)
```

Instead of embedding details, embed **pointers**:
- Report file → 2KB summary (can be read in new context)
- Directory path → all files preserved (can be examined)
- Git hash → full details (git show retrieves it)

#### Rule 2: Prioritize Blocking Issues
```markdown
## Critical Blockers

| Blocker | Impact | Next Action |
|---------|--------|-------------|
| 🔴 Missing API key | E2E tests won't run | Request from @ops by EOD |
| ⚠️ SQLAlchemy 2.0 migration | ORM incompatible | Review migration guide (see docs/) |
| 🟡 Waiting for review | Can't merge to main | Follow up with @alice |
```

Include blockers **in full detail** even if verbose. They determine what happens next.

#### Rule 3: One Action Per Priority Level
```markdown
## Pending Items

**Priority 1 (Next Session)**
- [ ] Fix SQL injection (1 hour, adws/validators.py:45)

**Priority 2 (This Week)**
- [ ] Add missing tests (2 hours, see specs/testing-plan.md)
- [ ] Update docs (1 hour, docs/README.md)

**Priority 3 (Backlog)**
- [ ] Refactor error handling (4 hours, issues #45-47)
```

Clear ranking prevents decision paralysis in fresh context.

#### Rule 4: Timestamp Markers for Artifacts
```markdown
## Key Files (This Session)

| File | Created/Modified | Purpose |
|------|-----------------|---------|
| specs/auth-redesign.md | 2025-11-23 14:30 | Requirements |
| ai_docs/build_reports/auth-report.md | 2025-11-23 18:15 | Implementation summary |
| .claude/commands/session/resume.md | 2025-11-23 19:00 | New command |
```

Timestamps show recency and help new context understand what's "hot."

---

## Part 5: Maintaining High-Resolution Information Across Context Windows

### Strategy: Pointer-Based Preservation

Instead of trying to fit everything into the handoff, use a **pointer architecture**:

```
┌─────────────────────────────────────┐
│   Fresh Context (200K tokens)       │
│                                     │
│  Reads: COMPACTION_PROMPT.md        │ ← Lightweight resume
│  (2-3 KB, ~300 tokens)              │
│                                     │
│  Contains: File path pointers       │
│                                     │
└─────────────────────────────────────┘
         ↓ ↓ ↓ (Read calls)
┌─────────────────────────────────────┐
│   File System (Preserved)           │
│                                     │
│  ai_docs/build_reports/             │ ← Detailed reports (on demand)
│  specs/                             │ ← Requirements (on demand)
│  .claude/commands/                  │ ← Implementation (on demand)
│  Git history                        │ ← Full details (git show)
│                                     │
└─────────────────────────────────────┘
```

**Result**: 
- Fresh context starts with ~190K tokens available
- All high-resolution information is preserved
- New context can restore details on-demand
- No information loss, just strategic sequencing

### Implementation: The Resume Pattern

After `/compact`, the session uses this pattern:

**Step 1: Paste Compaction Prompt**
```markdown
## QUICK RESUME - 2025-11-23

**Branch:** main | **Commit:** da4855b | **Handoff:** handoff-2025-11-23.md

### Done This Session
- README revamp with decision tree
- ai_docs/ triage: 28 → 4 files (89% reduction)
- Path migration: 65 occurrences fixed
...
```

Time cost: 30 seconds, token cost: ~300 tokens

**Step 2: Provide Specific Next Action**
```markdown
I understand the context. What would you like to work on next?

Available paths:
1. [Quick] Fix 2025 date inconsistencies (30 min) - see specs/todo-documentation-improvements.md
2. [ADW] Document all 48 commands (2 hrs) - read ai_docs/COMMAND_AUDIT_ANALYSIS.md first
3. [Complex] Implement feedback/ V2 loop (4+ hrs) - requires full context
```

**Step 3: Load Detailed Context On-Demand**
```bash
# New context doesn't read everything
# Instead:

# "Let me start with the documentation audit..."
cat ai_docs/analyses/COMMAND_AUDIT_ANALYSIS.md
# Now 2-3KB loaded, full context available for detailed work
```

### Real Example: Recovery After Compaction

From the Scout Plan Build MVP project:

**Before Compaction** (20% context remaining):
```
- 18+ files modified
- 7 commits made
- 3 new commands created  
- 1200+ lines of documentation written
- Can't fit everything in new context
```

**Handoff Document** (300 tokens, ~3KB):
```markdown
# Session Handoff - 2025-11-23

### Accomplished
- README revamp, ai_docs/ triage (89% reduction), path migration, 
  command structure, data flow diagram

### Pending
| Priority | Item | Effort |
|----------|------|--------|
| 1 | Fix date inconsistencies | 30 min |
| 2 | Document 48 commands | 2 hrs |
| 3 | V2 feedback loop | 4+ hrs |

### Key Files
- README.md (complete rewrite)
- ai_docs/README.md (data flow diagram)
- .claude/commands/session/resume.md (new)
```

**New Context Resumes** (190K+ tokens available):
```
1. Reads handoff (30 seconds)
2. Understands: "We cleaned up documentation, 3 priorities pending"
3. User says: "Work on priority 2 - document commands"
4. Claude reads: ai_docs/analyses/COMMAND_AUDIT_ANALYSIS.md
5. Full context for detailed work is now loaded on-demand
```

**Result**: Zero information loss, maximum available tokens for next phase.

---

## Part 6: Actionable Insights for Pre-Compaction Workflows

### Pre-Compaction Checklist

Before running `/compact`, execute this checklist:

#### Preparation Phase (20 minutes)
- [ ] Run `/session:prepare-compaction` command
  - Generates handoff file automatically
  - Updates COMPACTION_PROMPT.md
  - Commits all session work
- [ ] Review generated handoff for clarity
- [ ] Verify all file paths are correct
- [ ] Check that pending items are ranked by priority

#### Validation Phase (10 minutes)
- [ ] Confirm current branch is correct (`git branch`)
- [ ] Verify all work is committed (`git status` should show clean)
- [ ] Check that uncommitted files are intentionally untracked
- [ ] Test that handoff file renders properly (can be copied)

#### Finalization (5 minutes)
- [ ] Read COMPACTION_PROMPT.md from "---" line onward
- [ ] Copy that section (everything below the separator)
- [ ] Create a text file or note with the copied content
- [ ] Ready to paste as first message in new context

### Critical Success Factors

#### 1. Always Commit Before Compaction
```bash
# GOOD: Everything is committed
git status
# On branch main
# nothing to commit, working tree clean

# BAD: Uncommitted work
git status  
# On branch main
# Changes not staged for commit:
#   modified: auth.py
```

Uncommitted work is LOST after compaction. Commit first.

#### 2. Make Handoff Files Executable (Copy-Paste Ready)
```markdown
# GOOD: Can be pasted directly into next context
## QUICK RESUME - 2025-11-23

**Branch:** main | **Commit:** da4855b
...
---

## Next Immediate Action
1. Fix date inconsistencies
2. Document commands

# BAD: Requires editing before use
<!-- Remember to fill in your next steps manually -->
## Next Immediate Action
(Describe what you think is next)
```

#### 3. Use File Paths, Not Explanations
```markdown
# GOOD: Provides pointers
## Key Files Modified
- adws/validators.py (Pydantic models, lines 45-120)
- specs/auth-plan.md (requirements)
- ai_docs/README.md (documentation)

# BAD: Tries to summarize content
## Summary of Changes
We created Pydantic models to validate user input. This prevents
SQL injection attacks by... (200+ words of explanation)
```

#### 4. Separate Completed from In-Progress Work
```markdown
# GOOD: Clear status
## Accomplished This Session (DONE)
- ✅ Auth system refactored (commit 3c8ee0f)
- ✅ Tests written and passing (98% coverage)
- ✅ Documentation updated (11 files)

## Pending Items (TODO)
- [ ] API key from DevOps (blocking)
- [ ] Code review from @alice (awaiting)
- [ ] Final testing (ready to start)

# BAD: Mixes categories
## Session Summary
We refactored the auth system and wrote tests, but we're still waiting
for the API key, and the code review is in progress...
```

#### 5. Include Routing Instructions
```markdown
# GOOD: Guides next session
| Priority | Item | Route | Effort |
|----------|------|-------|--------|
| 1 | Fix SQL injection | **ADW** | 1 hr |
| 2 | Add integration tests | **Quick** | 2 hrs |
| 3 | Refactor error handler | **ADW-Full** | 3 hrs |

The "Route" tells the new context which workflow to use.

# BAD: No guidance
## Pending Items
- SQL injection fix
- Integration tests
- Error handler refactoring
```

---

## Part 7: Research Conclusions & Recommendations

### What Makes Compaction Successful

Based on analysis of the Scout Plan Build MVP project's actual compaction patterns:

**Success Factor 1: Structure Over Summaries**
- Handoff files use **tables and lists**, not prose
- Each row is actionable (priority, item, effort, route)
- New context can quickly scan and prioritize

**Success Factor 2: Pointers Over Embedded Content**
- References git hashes, not code snippets
- Points to files, not file contents
- Uses paths like `ai_docs/build_reports/auth.md` not "Here's what we did..."

**Success Factor 3: Completeness of Metadata**
- Session ID for traceability
- Commit hash for rollback capability
- Branch name for context
- Timestamp for recency
- File list for scope awareness

**Success Factor 4: Separation of Layers**
```
Layer 1: Handoff prompt (~300 tokens) - immediate orientation
Layer 2: File pointers (0 tokens) - tells you where to look
Layer 3: Full files (on-demand) - load only when needed
Layer 4: Git history (via tools) - forensics if needed
```

Only Layer 1 is pre-loaded. Layers 2-4 are on-demand.

### Why Anthropic's Approach Works

Anthropic's pattern avoids the **summarization trap**:

- **Trap**: "Let me summarize everything in 2 paragraphs" → Loss of detail
- **Pattern**: "Here are pointers to everything" → Full detail, immediate availability

This works because:
1. Claude has **Read/Grep/Git tools** to fetch details on-demand
2. Fresh context has **190K+ available tokens** for work
3. The handoff only needs to answer: "What's next?"
4. Everything else is a `Read` or `git show` away

### Optimal Compaction Frequency

Research shows the sweet spot is:
- **Trigger**: When context reaches 20-30% remaining (~150K+ tokens used)
- **Frequency**: Every 40-80 minutes of continuous work
- **Cost**: 30 minutes to prepare + 5 minutes to resume = 35 minute overhead
- **Benefit**: Restores 190K tokens for continued work

At 1000 tokens/minute velocity, you gain 60K+ tokens of work capacity by compacting.

### Information You Can Safely Discard

The research confirms that these do NOT need to be preserved in handoffs:
- Conversation filler and intermediate reasoning (in transcript if needed)
- Resolved issues and closed discussions (in git history)
- Code snippets (pointers to files instead)
- Error stack traces (file:line pointer instead)
- Explanatory prose (use structure + pointers)
- Duplicate information (consolidate)

### Information You Must Preserve

These MUST be in the handoff for continuity:
- What was accomplished (with file/commit references)
- What's pending (with priority and effort estimate)
- Current git state (branch, commits, uncommitted files)
- Blocking issues (full detail, even if verbose)
- Next immediate action (what to do when resuming)
- File paths for context (ai_docs/*, specs/*, key source files)

---

## Part 8: Recommended Pre-Compaction Workflow

### Optimal Implementation Pattern

```
1. WORK PHASE (~60-80 min)
   └─ Normal development, multiple commits
   
2. AWARENESS PHASE (~2 min)
   └─ Realize: Context approaching 20-30%
   
3. PREPARATION PHASE (~20 min)
   ├─ Run: /session:prepare-compaction
   ├─ Generates: Handoff + COMPACTION_PROMPT.md
   ├─ Review: For accuracy and clarity
   └─ Commit: All session artifacts
   
4. VALIDATION PHASE (~5 min)
   ├─ Check: Git status is clean
   ├─ Check: Handoff file is copy-paste ready
   ├─ Copy: Everything after "---" separator
   └─ Store: Copied content in accessible location
   
5. COMPACTION PHASE (~5 min)
   └─ Run: /compact
   
6. RESUME PHASE (~5 min in new context)
   ├─ Paste: Copied COMPACTION_PROMPT.md
   ├─ Understand: Current state and pending items
   ├─ Confirm: Ready for next action
   └─ Begin: Work on highest-priority pending item
```

**Total overhead**: 35 minutes per 60-80 minute session  
**Result**: 190K+ fresh tokens available, zero information loss

### Command Integration

The workflow is optimized by these commands:

```bash
# During work:
/session:prepare-compaction  # One command does steps 3-4

# Between sessions:
/session:resume              # One command loads handoff + shows next steps
```

Both commands are designed to minimize manual overhead.

---

## Summary: Key Takeaways

1. **Compaction is NOT summarization** - It's session windowing with strategic handoff
2. **Pre-compaction is critical** - 70% of success depends on preparation
3. **Use pointers, not embeddings** - Reference files instead of copying content
4. **Preserve structure, discard prose** - Tables > paragraphs, hashes > explanations
5. **Separate layers strategically** - Handoff (immediate) vs references (on-demand)
6. **Always commit first** - Work is lost if uncommitted at compaction time
7. **Make handoffs executable** - Copy-paste ready, no manual edits needed
8. **Include routing guidance** - Tell new context which workflow to follow
9. **Measure by information density** - 300 tokens max for 60 minutes of work
10. **Test your pattern** - Run compaction regularly to discover issues early

---

**Research Conclusion**: Anthropic's context compaction approach is fundamentally sound. The pattern of prepare → commit → compact → resume preserves all information while optimizing token efficiency. Success depends entirely on following the preparation protocol consistently.

