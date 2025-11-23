# Command Audit Specification

**Date**: 2025-11-22
**Purpose**: Test and classify all slash commands for functionality, safety, and risk level

## Test Task

Each agent will attempt to implement: **"Add debug logging to the authentication module"**

This task is chosen because it:
- Requires finding files (tests scout commands)
- Needs planning (tests plan commands)
- Involves code changes (tests build commands)
- Is reversible (safe for testing)
- Has clear success criteria (logging added)

## Agent Assignments

### Agent 1 (trees/command-audit-1): Scout Commands
Test these scout variants:
- `/scout "authentication files" "3"`
- `/scout_improved "authentication files" "medium"`
- `/scout_fixed "authentication files" "medium"`
- `/scout_parallel "authentication files" "3"`
- Native: `Task(subagent_type="explore", prompt="Find authentication files")`

### Agent 2 (trees/command-audit-2): Plan/Build Commands
Test the pipeline:
- `/plan_w_docs "Add debug logging to auth" "" "scout_outputs/relevant_files.json"`
- `/build_adw "specs/[created-spec].md"`
- `/scout_plan_build "Add debug logging to auth" ""`

### Agent 3 (trees/command-audit-3): SuperClaude Commands
Test with EXTREME CAUTION (read-only first):
- `/sc:analyze` - Analyze existing auth code
- `/sc:explain` - Explain auth module
- `/sc:design` - Design logging approach
- `/sc:implement` - ONLY if safe, implement logging
- `/sc:test` - Test the changes

### Agent 4 (trees/command-audit-4): Worktree & Meta Commands
Test our new commands:
- `/compare-worktrees command-audit` (after others finish)
- `/prepare-compaction` (read-only, safe)
- Test chaining: scout → plan in sequence

## Risk Assessment Criteria

For each command, document:

### 1. Functionality
- ✅ Works as expected
- ⚠️ Partially works (document issues)
- ❌ Fails completely (document error)

### 2. Risk Level (Per Chad's Framework)
- 🟢 **read-only**: No file/state mutations
- 🟡 **mutate-local**: Changes files locally
- 🔴 **mutate-external**: Pushes/deploys/spawns

### 3. Auto-Invoke Safety
- **safe**: Can be auto-invoked by LLM
- **gated**: Needs user approval
- **never**: Should never be auto-invoked

### 4. Dependencies
- What tools does it assume exist?
- What environment variables?
- What file structures?

### 5. Failure Modes
- How does it fail?
- Is failure graceful?
- Can it corrupt state?

## Output Format

Each agent creates: `trees/command-audit-N/AUDIT_RESULTS.md`

```markdown
# Command Audit Results - Agent N

## Commands Tested

### /command-name
- **Status**: ✅/⚠️/❌
- **Risk**: 🟢/🟡/🔴
- **Auto-invoke**: safe/gated/never
- **Dependencies**: [list]
- **Failure modes**: [describe]
- **Output**:
  ```
  [paste actual output]
  ```
- **Recommendation**: [use/fix/remove]

## Summary
- Working commands: [list]
- Broken commands: [list]
- Dangerous commands: [list]
```

## Execution Instructions

1. Each agent works in their assigned worktree
2. Test commands in order listed
3. Document everything (success AND failure)
4. Create AUDIT_RESULTS.md in worktree root
5. DO NOT push changes or create PRs
6. If command seems dangerous, document but don't execute

## Safety Rules

- NEVER run commands that might push to git
- STOP if a command tries to spawn unlimited agents
- DOCUMENT suspicious behavior
- Default to read-only testing when unsure