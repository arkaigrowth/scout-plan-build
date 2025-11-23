---
description: FIXED Scout - uses working Python scripts instead of broken external tools
argument-hint: [user-prompt] [scale]
---

<!-- risk: read-only -->
<!-- auto-invoke: safe -->

# Scout (FIXED VERSION)

## What Changed
- Removed ALL external tool calls (gemini, opencode, Task agents)
- Uses working Python scripts with native Glob/Grep
- Keeps all the good stuff: parallel execution, timeouts, git safety

## Variables
- `USER_PROMPT`: $1 - The task/feature to scout for
- `SCALE`: $2 (defaults to 3) - Number of parallel workers

## Workflow

Execute via Bash (this actually works!):

```bash
# Parallel scout (recommended)
python adws/adw_scout_parallel.py "$USER_PROMPT" --scale $SCALE

# Or single-threaded
python adws/scout_simple.py "$USER_PROMPT"
```

**What the scripts do:**
1. Launch parallel workers with different search strategies
2. Use native Glob/Grep (guaranteed to work)
3. Handle 60-second timeout per worker
4. Git safety (stash uncommitted changes, restore after)
5. Aggregate and sort results for determinism

## Why This Works
- Native tools (Glob/Grep) always available in Claude Code
- No external dependencies (no gemini, opencode, codex)
- No Task subagent syntax (which doesn't work as documented)
- Same parallel pattern as working Test/Review/Document commands

## Output
- Results: `scout_outputs/relevant_files.json`
- Individual reports: `scout_outputs/{focus}_report.json`

## Next Steps
```bash
/plan_w_docs_improved "$USER_PROMPT" "" "scout_outputs/relevant_files.json"
```