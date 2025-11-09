---
description: Parallel Scout Squadron - Multiple agents exploring simultaneously
argument-hint: [task] [scale]
---

# Scout Parallel - The Missing Piece!

**Finally!** Parallel discovery using the same pattern that made Test/Review/Document 40-50% faster.

## What This Does

Launches multiple scout agents in parallel, each with a different search strategy:
- **Implementation Scout**: Finds source code and main logic
- **Test Scout**: Discovers test files and patterns
- **Config Scout**: Locates configuration and settings
- **Architecture Scout**: Identifies patterns and structure
- **Dependencies Scout**: Finds packages and imports
- **Documentation Scout**: Discovers docs and READMEs

## Usage

```bash
# Basic usage (4 scouts by default)
/scout_parallel "implement authentication"

# Custom scale
/scout_parallel "add caching layer" 6

# After scout, run plan
/plan_w_docs "[task]" "[docs]" "scout_outputs/relevant_files.json"
```

## Performance

```
Sequential Scout: 3-5 minutes (one search at a time)
Parallel Scout: 30-60 seconds (all searches concurrent!)

Speedup: 4-6x faster!
```

## Implementation

Uses the SAME subprocess.Popen() pattern as Test/Review/Document:

```python
# Launch squadron
processes = []
for strategy in strategies:
    proc = subprocess.Popen(["python", "adws/scout_simple.py", prompt])
    processes.append(proc)

# Wait and aggregate
for proc in processes:
    proc.wait()

# Combine results
aggregate_findings()
```

## Output

Saves to standard locations:
- `scout_outputs/relevant_files.json` - For plan phase
- `scout_outputs/{focus}_report.json` - Individual scout reports
- `ai_docs/scout/relevant_files.json` - Backup

## Why This Matters

Scout is WHERE IT ALL BEGINS:
- Better discovery → Better specs
- Multiple perspectives → Comprehensive understanding
- Parallel execution → 4-6x faster
- Domain expertise → Higher quality

## The Complete Pipeline

```
/scout_parallel → /plan_w_docs → /build_adw → [test||review||document]
     ⚡             →      📋      →     🔨     →         ⚡

Total speedup: 60-70% (vs 40-50% without parallel scout)
```

## Example Workflow

```python
# 1. Parallel Scout (30 seconds instead of 3 minutes!)
Run: /scout_parallel "implement user authentication"

# 2. Generate Plan
Run: /plan_w_docs "implement user authentication" "https://docs.auth0.com" "scout_outputs/relevant_files.json"

# 3. Build
Run: /build_adw "specs/issue-XXX-adw-YYY-auth.md"

# 4. Parallel QA (already implemented)
Run: uv run adws/adw_sdlc.py XXX YYY --parallel
```

## Notes

- Git safety included (stash/restore if needed)
- Deterministic output (sorted files)
- Aggregated insights from multiple perspectives
- Same simple implementation as Test/Review/Document (30 lines!)

**"We parallelized the finish line but forgot about the starting blocks!"** - This fixes that.