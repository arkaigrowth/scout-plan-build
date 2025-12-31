# Task: Create Comprehensive ARCHITECT_GUIDE.md

**Goal**: Create a single, authoritative document that enables any AI architect agent to understand, install, and leverage the Scout-Plan-Build framework when building new projects.

**Output Location**: `ai_docs/architecture/ARCHITECT_GUIDE.md`

---

## Context

We have 90+ markdown files scattered across this repo, but no single comprehensive guide for architects. This document will be THE source of truth for:
1. Understanding what SPB is and when to use it
2. How the components work together
3. How to install and configure it
4. Workflow patterns and best practices
5. Command reference for common operations

The target audience is an AI agent (Claude, GPT, etc.) that's been tasked with architecting a new project and wants to leverage SPB from day one.

---

## Research Strategy (Phase 1)

### Parallel Exploration

Launch 4 Task agents simultaneously to divide research:

```
Task 1: "Core Documentation"
  subagent_type: Explore
  prompt: |
    Analyze these files for framework overview, philosophy, and quick-start info:
    - README.md (philosophy, quick start, workflow decision tree)
    - INSTALL.md (installation mechanics, what gets installed)
    - CLAUDE.md (command router, task patterns)

    Extract: Core value prop, installation steps, primary workflows
    Return: Structured summary with key quotes

Task 2: "Architecture & Components"
  subagent_type: Explore
  prompt: |
    Explore ai_docs/architecture/ directory for:
    - System architecture diagrams/descriptions
    - Component relationships
    - Data flow patterns
    - Integration points

    Also check: adws/ directory structure, .claude/ organization
    Return: Component map with relationships

Task 3: "Learnings & Best Practices"
  subagent_type: Explore
  prompt: |
    Search ai_docs/analyses/ and ai_docs/reviews/ for:
    - Framework dogfooding learnings
    - Common pitfalls and solutions
    - Performance patterns
    - What works vs what doesn't

    Also check: archive/research/ for workflow patterns
    Return: Consolidated best practices list

Task 4: "Commands & Skills Reference"
  subagent_type: Explore
  prompt: |
    Analyze .claude/commands/ and .claude/skills/ for:
    - Available commands by category
    - Most important/frequently used commands
    - Command chaining patterns
    - Skill building blocks

    Return: Categorized command reference with examples
```

### Context Management

- Each Task agent has isolated context → won't pollute main session
- Main agent receives summaries → synthesizes into guide
- Budget: ~60% for research, ~30% for writing, ~10% for validation

---

## Document Structure (Phase 2)

Write the guide with these sections:

### 1. Executive Summary (~50 lines)
```markdown
## What is Scout-Plan-Build?
[One paragraph explaining the core problem and solution]

## Core Value Proposition
- Structured workflows that ship
- Traceable decisions and outputs
- Canonical file organization
- Session continuity across breaks

## When to Use This Framework
[Decision matrix: project size, complexity, team context]
```

### 2. Architecture Overview (~100 lines)
```markdown
## Directory Structure
[Annotated tree showing what each directory does]

## Component Relationships
adws/ (Python workflows) ↔ .claude/commands/ (triggers) ↔ scripts/ (utilities)
     ↓                           ↓                            ↓
specs/ (outputs)          agent_runs/ (state)          ai_docs/ (knowledge)

## Data Flow
Scout → relevant_files.json → Plan → spec.md → Build → code changes → Review
```

### 3. Installation & Configuration (~80 lines)
```markdown
## Prerequisites
- Claude Code CLI or compatible agent
- Python 3.11+
- Git

## Quick Install
[Copy from INSTALL.md, keep concise]

## Required Environment Variables
[Table format with descriptions]

## Post-Install Validation
[python test_installation.py + what to check]
```

### 4. Workflow Patterns (~100 lines)
```markdown
## Pattern Selection
[Decision tree from README.md]

## Simple Pattern (1-3 files)
Just edit directly. No framework needed.

## Standard Pattern (4-10 files)
1. Grep/Glob to find relevant files
2. /plan_w_docs_improved "description" "" "scout_outputs/files.json"
3. /build_adw "specs/issue-XXX.md"

## Complex Pattern (11+ files or uncertain)
1. /init-parallel-worktrees feature-name 3
2. Try different approaches in each worktree
3. /compare-worktrees feature-name
4. /merge-worktree best-approach

## Research Pattern
- Task(Explore) for codebase understanding
- Grep/Glob for targeted searches
- Context7 for library documentation
```

### 5. Command Quick Reference (~80 lines)
```markdown
## Most Used Commands
| Command | Purpose | Example |
|---------|---------|---------|
| /plan_w_docs_improved | Create spec | `"Add auth" "" "files.json"` |
| /build_adw | Execute spec | `"specs/feature.md"` |
| /sc:test | Run tests | - |
| /sc:analyze | Code review | - |

## By Category
### Planning: /plan_w_docs_improved, /feature, /bug, /chore
### Workflow: /build_adw, /implement, /scout_improved
### Git: /commit, /pull_request, /init-parallel-worktrees
### Testing: /test, /test_e2e, /resolve_failed_test
```

### 6. Best Practices (~100 lines)
```markdown
## Output Organization (CRITICAL)
NEVER write to repo root. Use canonical paths:
- specs/ → Specifications
- ai_docs/analyses/ → Analysis outputs
- ai_docs/build_reports/ → Build reports
- scout_outputs/ → Scout phase outputs

## Context Management
- Delegate research to Task agents
- Use /compact before exhaustion
- Checkpoint with git commits

## Session Lifecycle
- Start: Check git status, understand current state
- Work: TodoWrite for tracking, incremental commits
- End: /compact or handoff document

## Parallel Execution
- Use git worktrees for approach exploration
- Spawn Task agents for independent research
- Batch tool calls when no dependencies
```

### 7. Integration Checklist (~50 lines)
```markdown
## Pre-Build Checklist (New Project)
- [ ] Run install script
- [ ] Configure .env with API keys
- [ ] Run test_installation.py
- [ ] Review CLAUDE.md for command reference
- [ ] Create initial git branch

## Common Issues
| Issue | Cause | Fix |
|-------|-------|-----|
| Token limit | Default 8192 | Set CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768 |
| Scout fails | Missing deps | Use native Grep/Glob |
| Files in root | No path enforcement | Use canonical paths |
```

---

## Quality Criteria (Phase 3)

Before marking complete, verify:

1. **Completeness**: All 7 sections present and substantive
2. **Accuracy**: Code examples actually work
3. **Clarity**: New agent could follow without prior knowledge
4. **Conciseness**: ~500-600 lines, not bloated
5. **Cross-references**: Links to detailed docs where appropriate

### Self-Review Checklist
- [ ] Can an architect agent install SPB from this doc alone?
- [ ] Are workflow patterns clear with concrete examples?
- [ ] Are best practices actionable, not vague?
- [ ] Is command reference complete but not overwhelming?

---

## Execution Notes

### TodoWrite Usage
Track progress with sections as todos:
1. Research Phase - Core Docs
2. Research Phase - Architecture
3. Research Phase - Learnings
4. Research Phase - Commands
5. Writing Phase - Sections 1-3
6. Writing Phase - Sections 4-5
7. Writing Phase - Sections 6-7
8. Validation Phase

### Git Checkpoints
Commit after each major phase:
- "docs: Add ARCHITECT_GUIDE.md skeleton"
- "docs: Complete research phase for ARCHITECT_GUIDE"
- "docs: Complete ARCHITECT_GUIDE.md v1"

### Output Location
Write to: `ai_docs/architecture/ARCHITECT_GUIDE.md`

Do NOT write to repo root or create new top-level files.

---

## Success Definition

The task is complete when:
1. ARCHITECT_GUIDE.md exists at canonical path
2. All 7 sections are substantive (not stubs)
3. Self-review checklist passes
4. Committed to git with descriptive message

---

## Start Command

Begin by reading these 3 files in parallel to orient yourself:
- README.md
- INSTALL.md
- CLAUDE.md

Then launch the 4 parallel Task agents as described in Research Strategy.

Good luck! 🚀
