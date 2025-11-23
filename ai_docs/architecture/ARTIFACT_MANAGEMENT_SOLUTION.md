# Artifact Management Solution

**Date**: 2025-11-22
**Problem**: Agent outputs dumping in repo root causing chaos
**Solution**: Enforce existing infrastructure + simple improvements

## Executive Summary

The framework ALREADY HAS good artifact management (`FileOrganizer`, canonical paths in `constants.py`).
The problem is **enforcement**, not missing features. This solution enforces existing patterns + adds minimal enhancements.

## The Problem (Quantified)

- **12 files** misplaced in repo root (171KB)
- **7 should be in ai_docs/**
- **2 should be in docs/**
- **2 should be in specs/**
- Main offenders: Analysis agents, scout workflows, ad-hoc creation

## The Solution: 3-Layer Approach

### Layer 1: Enforce Existing Canonical Paths (Immediate)

The framework already defines these in `adws/adw_modules/constants.py`:

```python
# These paths ALREADY EXIST - just use them!
SCOUT_OUTPUT_FILE = "scout_outputs/relevant_files.json"
SPECS_DIR = "specs"
BUILD_REPORTS_DIR = "ai_docs/build_reports"
REVIEWS_DIR = "ai_docs/reviews"
ANALYSES_DIR = "ai_docs/analyses"
ARCHITECTURE_DIR = "ai_docs/architecture"
```

**Action**: Update agent prompts to ALWAYS specify output paths:

```python
# BAD (creates in root)
Write("ANALYSIS_REPORT.md", content)

# GOOD (uses canonical location)
Write("ai_docs/analyses/analysis-report.md", content)
```

### Layer 2: Enhanced Agent Output Directory (Short-term)

Create a dedicated transient output area:

```
agent_outputs/
├── 2025-11-22/              # Date-based for easy cleanup
│   ├── 0930-auth-scout.json # Time prefix for sorting
│   ├── 0945-auth-plan.md
│   ├── 1015-auth-build/     # Multi-file outputs
│   │   ├── report.md
│   │   └── metrics.json
│   └── parallel/            # Parallel agent outputs
│       ├── wt1-auth.json
│       ├── wt2-auth.json
│       └── wt3-auth.json
└── .gitkeep

# Canonical imports get copied/moved to proper locations
# Transient outputs can be bulk cleaned after 48h
```

### Layer 3: Simple Slug Pattern (Use Existing)

The framework already has `slugify()` in `adws/adw_common.py`:

```python
def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9-]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')
```

**Enhanced pattern for agent outputs**:
```
{HHMMSS}-{slugify(task)}-{type}.{ext}

Examples:
093045-auth-debug-scout.json
094512-auth-debug-plan.md
101523-auth-debug-build.md
```

## Implementation Plan

### Step 1: Immediate Cleanup (5 min)

```bash
# Move misplaced files to canonical locations
mv ANALYSIS_SUMMARY.md ai_docs/analyses/
mv SCOUT_FRAMEWORK_DEEP_ANALYSIS.md ai_docs/analyses/
mv FRAMEWORK_ANALYSIS_INDEX.md ai_docs/analyses/
mv FRAMEWORK_ARCHITECTURE_PATTERNS.md ai_docs/architecture/
mv DOCUMENTATION_AUDIT_REPORT.md ai_docs/reviews/
mv OUTDATED_REFERENCES_AUDIT.md ai_docs/reviews/
mv GIT_WORKTREE_PARALLELIZATION_SCOUT_REPORT.md ai_docs/analyses/
mv INSTALLATION_GUIDE.md docs/
mv CLAUDE_v4_PROPOSED.md specs/claude-v4-proposed.md

# Clean up
rm -f run_log.md  # Should be in logs/ or .gitignored
```

### Step 2: Update .gitignore (2 min)

Add these patterns:
```gitignore
# Agent outputs (should use canonical paths)
/*_REPORT.md
/*_ANALYSIS.md
/*_AUDIT.md
/CLAUDE_v*.md
/run_log.md

# Transient outputs
/agent_outputs/*/
!/agent_outputs/.gitkeep

# Keep worktrees but ignore their outputs
/trees/*/ai_docs/
/trees/*/agent_outputs/
```

### Step 3: Update Agent Prompts (10 min)

Create a standard header for all agent prompts:

```markdown
## Output Rules (CRITICAL)
- NEVER write files to repository root
- Use these canonical paths:
  - Analyses: ai_docs/analyses/{slug}.md
  - Reviews: ai_docs/reviews/{slug}.md
  - Reports: ai_docs/build_reports/{slug}.md
  - Specs: specs/{slug}.md
  - Temp work: agent_outputs/{date}/{time}-{slug}.{ext}
```

### Step 4: Create Helper Function (5 min)

Add to `adws/adw_common.py`:

```python
def get_output_path(output_type: str, task_name: str, ext: str = "md") -> str:
    """Get canonical output path for agent artifacts."""
    from datetime import datetime

    slug = slugify(task_name)
    timestamp = datetime.now().strftime("%H%M%S")
    date = datetime.now().strftime("%Y-%m-%d")

    paths = {
        "analysis": f"ai_docs/analyses/{slug}-analysis.{ext}",
        "review": f"ai_docs/reviews/{slug}-review.{ext}",
        "report": f"ai_docs/build_reports/{slug}-report.{ext}",
        "spec": f"specs/{slug}-spec.{ext}",
        "temp": f"agent_outputs/{date}/{timestamp}-{slug}.{ext}",
        "scout": f"scout_outputs/{slug}.json"
    }

    return paths.get(output_type, f"agent_outputs/{date}/{timestamp}-{slug}.{ext}")
```

## Benefits

1. **Uses existing infrastructure** - No new systems to learn
2. **Backward compatible** - Existing paths unchanged
3. **Simple slug pattern** - HHMMSS prefix for sorting
4. **Clean repo root** - Everything has a home
5. **Easy cleanup** - Date-based directories for bulk deletion
6. **Parallel-friendly** - Agent ID prefixes prevent collisions

## Migration Strategy

1. **Phase 1** (Today): Move existing files, update .gitignore
2. **Phase 2** (This week): Update agent prompts with output rules
3. **Phase 3** (Next week): Add helper functions to framework
4. **Phase 4** (Future): Enforce via pre-commit hooks

## Success Metrics

- Zero `.md` files in repo root (except README.md)
- All agent outputs in canonical or `agent_outputs/` paths
- Clean `git status` after agent runs
- Easy to find artifacts by type and date

---

**Next Step**: Execute Step 1 (cleanup) and Step 2 (.gitignore) immediately.