# Plan: Documentation Marketing Revamp

## Summary

Transform the Scout-Plan-Build documentation from functional but dry technical docs into compelling, clear documentation that communicates value proposition and makes the framework approachable.

## Problem Statement

Current documentation issues:
- **README is generic** - Looks like every other tool's README
- **No clear "why use this"** - Missing compelling value proposition
- **No visual command reference** - 48 slash commands with no visual guide
- **Emoji overuse** - Was tacky, now fixed but needs cohesive style
- **No real examples** - Abstract descriptions instead of concrete workflows
- **No hero section** - Missing visual identity and quick wins

## Goals

1. **Clarity** - Anyone should understand what this does in 30 seconds
2. **Appeal** - Make developers want to try it
3. **Utility** - Provide actionable examples and visual guides
4. **Professionalism** - Clean, minimal design without marketing fluff

## Architecture/Approach

### README Structure (New)

```
1. Hero Section (with banner image placeholder)
   - One-liner value prop
   - 3 key benefits as badges or icons

2. The Problem This Solves
   - Pain point: AI coding assistants lack structure
   - Solution: Scout-Plan-Build enforces workflow

3. Quick Demo (GIF or code example)
   - Show the magic in 30 seconds

4. Installation (collapsed by default)
   - Keep it simple

5. Core Workflow Visual
   - Mermaid diagram: Scout → Plan → Build
   - When to use each phase

6. Command Reference
   - Organized by category with visual cues
   - Most-used commands highlighted

7. Why This Works
   - Parallel execution stats
   - Real metrics from dogfooding

8. Getting Help
   - Links to detailed docs
```

### Visual Assets Needed

| Asset | Purpose | Format |
|-------|---------|--------|
| Hero banner | Repo identity | PNG (user to create) |
| Workflow diagram | Core concept | Mermaid in README |
| Command flowchart | Decision guide | Mermaid or ASCII |
| Before/After | Value demo | Side-by-side text |

### Command Visual Reference

Create a visual decision tree:

```
What do you need?
│
├─ Find files → Grep/Glob (native tools)
├─ Plan feature → /plan_w_docs_improved
├─ Build from spec → /build_adw
├─ Try approaches → /init-parallel-worktrees
├─ Session mgmt → /session:resume, /session:prepare-compaction
└─ Git ops → /git:commit, /git:pull_request
```

### Cookbook Approach

Instead of listing all 48 commands, show 5 common workflows:

1. **"Add a feature"** - Scout → Plan → Build
2. **"Fix a bug"** - Quick execution pattern
3. **"Explore unknown codebase"** - Research pattern
4. **"Try multiple approaches"** - Parallel worktrees
5. **"Resume after break"** - Session continuity

## Implementation Steps

### Step 1: Create Value Proposition Section

Write a compelling "why" section that addresses:
- What pain does this solve?
- Who is this for?
- What makes it different?

### Step 2: Add Mermaid Workflow Diagram

```mermaid
graph LR
    A[Task] --> B{Complexity?}
    B -->|1-2 files| C[Just Do It]
    B -->|3-5 files| D[/plan → /build]
    B -->|6+ files| E[Scout → Plan → Build]
    B -->|Uncertain| F[Parallel Worktrees]
```

### Step 3: Create Command Quick Reference

Reorganize from alphabetical dump to:
- Most Used (5 commands)
- Planning (4 commands)
- Building (3 commands)
- Git (6 commands)
- Session (3 commands)
- Advanced (rest collapsed)

### Step 4: Add Concrete Examples

Replace abstract descriptions with real scenarios:
- "Adding OAuth to a Flask app"
- "Migrating React class components to hooks"
- "Fixing a CI pipeline bug"

### Step 5: Style Guide

- Minimal emojis (status indicators only: working/broken)
- Code examples over descriptions
- Mermaid diagrams over ASCII where supported
- Collapsible sections for dense info
- Badge-style stats (e.g., "40-50% faster with parallel")

## Files to Modify

| File | Changes |
|------|---------|
| `README.md` | Complete restructure per above |
| `docs/SLASH_COMMANDS_REFERENCE.md` | Add visual decision tree |
| `CLAUDE.md` | Already has router, keep as-is |
| `docs/TEAM_ONBOARDING_PRESENTATION.md` | Add cookbook section |

## Success Criteria

- [ ] README communicates value in first 30 seconds
- [ ] Workflow diagram visible without scrolling
- [ ] At least 3 concrete examples included
- [ ] Command reference is visual, not just a list
- [ ] No marketing fluff, honest about status
- [ ] Hero banner placeholder ready for user's image

## Estimated Effort

- Step 1 (Value prop): 15 min
- Step 2 (Mermaid diagram): 10 min
- Step 3 (Command reference): 20 min
- Step 4 (Examples): 30 min
- Step 5 (Style cleanup): 15 min
- **Total: ~90 minutes**

---
*Spec created: 2024-11-23*
*Framework: Using ADW to improve ADW (dogfooding)*
