---
description: Search the codebase for files needed to complete the task
argument-hint: [user-prompt] [scale]
model: claude-sonnet-4-5-20250929
---

<!-- risk: read-only -->
<!-- auto-invoke: safe -->

# Scout Improved

## Purpose
Search the codebase for files needed to complete the task using native tools.

## Variables
- `USER_PROMPT`: $1 - The task/feature to scout for
- `SCALE`: $2 (defaults to 4) - Number of parallel workers
- Output directory: `scout_outputs/`

## Workflow

Execute the parallel scout via Bash:

```bash
python adws/adw_scout_parallel.py "$USER_PROMPT" --scale $SCALE
```

**What this does:**
1. Launches `SCALE` parallel scout agents (each with different focus: implementation, tests, config, architecture, dependencies, documentation)
2. Uses native Glob/Grep tools (guaranteed to work - no external dependencies)
3. Enforces 60-second timeout per scout
4. Aggregates results from all scouts
5. Handles git safety (stash/restore uncommitted changes)
6. Returns sorted file list for determinism

## Performance
```
Sequential Scout: 3-5 minutes (one search at a time)
Parallel Scout: 30-60 seconds (all searches concurrent!)
Speedup: 4-6x faster!
```

## Output Format
Results saved to `scout_outputs/relevant_files.json`:
```json
{
  "task": "[USER_PROMPT]",
  "timestamp": "ISO-8601 timestamp",
  "duration_seconds": 45.2,
  "scout_count": 4,
  "files": ["path/to/file1.py", "path/to/file2.py"],
  "file_count": 25,
  "performance": {
    "sequential_estimate": 120,
    "parallel_actual": 45.2,
    "speedup": "2.7x"
  }
}
```

## Next Steps
After scouting, run plan:
```bash
/plan_w_docs_improved "$USER_PROMPT" "" "scout_outputs/relevant_files.json"
```