<!-- risk: read-only -->
<!-- auto-invoke: safe -->

# Scout

## Purpose
Search the codebase for files needed to complete the task using native tools (Glob/Grep).

## Variables
- `USER_PROMPT`: $1 - The task/feature to scout for
- `SCALE`: $2 (defaults to 4) - Number of parallel workers

## Workflow

Execute the scout via Bash:

```bash
# For parallel scouts (recommended - 4-6x faster)
python adws/adw_scout_parallel.py "$USER_PROMPT" --scale $SCALE

# Or for single-threaded scout
python adws/scout_simple.py "$USER_PROMPT"
```

**What the script does:**
- Uses native Glob/Grep tools (guaranteed to work)
- Handles parallel execution via subprocess
- Saves results to `scout_outputs/relevant_files.json`
- Includes git safety (stash/restore uncommitted changes)
- Returns sorted file list for determinism

## Output
- Results saved to: `scout_outputs/relevant_files.json`
- Individual scout reports: `scout_outputs/{focus}_report.json`
- Path to `relevant_files.json` is returned for use in next step

## Next Steps
After scouting, run plan:
```bash
/plan_w_docs_improved "$USER_PROMPT" "" "scout_outputs/relevant_files.json"
```
