---
description: Parallel Scout Squadron - Multiple agents exploring simultaneously
argument-hint: [task] [scale]
---

<!-- risk: read-only -->
<!-- auto-invoke: safe -->

# Scout Parallel - The Missing Piece!

**Finally!** Parallel discovery using the same pattern that made Test/Review/Document 40-50% faster.

## What This Does

Launches multiple scout workers in parallel, each with a different search strategy:
- **Implementation Scout**: Finds source code and main logic
- **Test Scout**: Discovers test files and patterns
- **Config Scout**: Locates configuration and settings
- **Architecture Scout**: Identifies patterns and structure
- **Dependencies Scout**: Finds packages and imports
- **Documentation Scout**: Discovers docs and READMEs

## Variables
- `USER_PROMPT`: $1 - The task/feature to scout for
- `SCALE`: $2 (defaults to 4) - Number of parallel workers

## Workflow

Execute the parallel scout via Bash:

```bash
python adws/adw_scout_parallel.py "$USER_PROMPT" --scale $SCALE
```

**What this script does:**
1. Launches `SCALE` parallel workers using subprocess.Popen()
2. Each worker uses native Glob/Grep (guaranteed to work)
3. Enforces 60-second timeout per worker
4. Aggregates results from all workers
5. Git safety: stash uncommitted changes, restore after
6. Returns sorted file list for determinism

## Performance

```
Sequential Scout: 3-5 minutes (one search at a time)
Parallel Scout: 30-60 seconds (all searches concurrent!)

Speedup: 4-6x faster!
```

## Output

Saves to standard locations:
- `scout_outputs/relevant_files.json` - Main output for plan phase
- `scout_outputs/{focus}_report.json` - Individual scout reports

## Example Workflow

```bash
# 1. Parallel Scout (30 seconds instead of 3 minutes!)
/scout_parallel "implement user authentication"

# 2. Generate Plan
/plan_w_docs_improved "implement user authentication" "https://docs.auth0.com" "scout_outputs/relevant_files.json"

# 3. Build
/build_adw "specs/issue-XXX-adw-YYY-auth.md"
```

## The Complete Pipeline

```
/scout_parallel → /plan_w_docs → /build_adw → [test||review||document]
     ⚡              →     📋      →    🔨     →         ⚡

Total speedup: 60-70% (vs 40-50% without parallel scout)
```

## Notes

- Git safety included (stash/restore if needed)
- Deterministic output (sorted files)
- Aggregated insights from multiple perspectives
- Uses same subprocess pattern as Test/Review/Document

**"We parallelized the finish line but forgot about the starting blocks!"** - This fixes that.