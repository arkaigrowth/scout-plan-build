# Refinery Data Refiner - Quick Migration Guide

**Framework**: v2024.11.8 → v4.0
**Date**: 2025-11-25

---

## Command Translation Table

### Core Workflows (Still Work!)

| Old Command | New Command | Status | Notes |
|------------|-------------|--------|-------|
| `/build_adw "spec.md"` | `/build_adw "spec.md"` | ✅ Same | Now in `workflow/` |
| `/plan_w_docs_improved` | `/plan_w_docs_improved` | ✅ Same | Now in `planning/` |
| `/scout "task"` | `/scout_improved "task"` | ⚠️ Enhanced | Multiple variants available |

### Deprecated

| Old Command | Replacement | Why |
|------------|-------------|-----|
| `/plan_w_docs` | `/plan_w_docs_improved` | Improved version exists |

### New Commands (v4.0)

| Command | Purpose | Example |
|---------|---------|---------|
| `/sc:analyze` | Code analysis | `/sc:analyze` |
| `/sc:git` | Git operations | `/sc:git` |
| `/sc:test` | Run tests | `/sc:test` |
| `/sc:load` | Load session | `/sc:load` |
| `/sc:save` | Save session | `/sc:save` |
| `/test_e2e` | E2E testing | `/test_e2e` |

---

## Workflow Changes

### Before (v2024.11.8)
```bash
# 1. Find files
/scout "implement auth"

# 2. Create plan
/plan_w_docs_improved "Add auth" "" "scout_outputs/files.json"

# 3. Build
/build_adw "specs/auth.md"
```

### After (v4.0) - Same + Enhanced
```bash
# 1. Load session context (NEW!)
/sc:load

# 2. Find files (multiple options now)
/scout_improved "implement auth"
# OR /scout_fixed (uses Python scripts)
# OR /scout_parallel (multiple agents)

# 3. Create plan (same)
/plan_w_docs_improved "Add auth" "" "scout_outputs/files.json"

# 4. Build (same)
/build_adw "specs/auth.md"

# 5. Test (NEW!)
/sc:test

# 6. Save session (NEW!)
/sc:save
```

---

## New Capabilities

### 1. Session Management
```bash
# Start of session
/sc:load  # Resume previous context

# During work
# ... your normal workflow ...

# End of session
/sc:save  # Persist for next time
```

### 2. Git Operations
```bash
# Git workflows now have dedicated commands
/sc:git  # Handles commits, branches, etc.

# Parallel development with worktrees
/init-parallel-worktrees feature-name 3
/run-parallel-agents "specs/feature.md" feature-name
/compare-worktrees feature-name
/merge-worktree trees/feature-name-2
```

### 3. E2E Testing
```bash
# Run E2E tests with Playwright
/test_e2e "auth" "frontend" "tests/e2e/auth.spec.ts"
```

### 4. Code Analysis
```bash
# Comprehensive analysis
/sc:analyze  # Quality, security, performance, architecture
```

---

## File Organization

### Output Locations (Enhanced)

```
refinery-data-refiner/
├── ai_docs/
│   ├── analyses/      ← Code analysis reports (NEW location)
│   ├── build_reports/ ← Build reports
│   ├── reviews/       ← Code reviews
│   └── scout/         ← Scout outputs
├── scout_outputs/     ← Legacy location (still works)
└── specs/             ← Implementation plans
```

**Best Practice**: Use `ai_docs/*` for new outputs, `scout_outputs/` maintained for compatibility.

---

## Custom Agents (Preserved!)

Your 7 custom agents are **fully preserved** in `.claude/agents/`:

```
AGENT_INTERACTIONS_GUIDE.md     - Still works
PLAYWRIGHT_USAGE_GUIDE.md       - Still works
SHADCN_MCP_GUIDE.md             - Still works
SHADCN_MCP_QUICKREF.md          - Still works
shadcn-frontend-architect.md    - Still works
shadcn-ui-expert.md             - Still works
shared-conventions.md           - Still works
```

**No changes needed** - agents use same activation mechanisms.

---

## Settings (Preserved!)

Your `.claude/settings.local.json` preserved:
```json
{
  "outputStyle": "Explanatory"
}
```

**No changes needed** - settings still apply.

---

## Breaking Changes

**None!** All your existing workflows continue to work. New commands are additive.

The only change is **command locations**:
- Old: Flat files in `.claude/commands/`
- New: Organized directories in `.claude/commands/`

But invocation is **identical**: `/build_adw` still works regardless of file location.

---

## Migration Checklist

- [x] ✅ Backup created
- [x] ✅ Framework upgraded
- [x] ✅ User files preserved (settings, agents)
- [x] ✅ Python imports validated
- [ ] Test your workflows
- [ ] Update any automation scripts
- [ ] Explore new session management
- [ ] Try new analysis commands

---

## Quick Test

```bash
cd /Users/alexkamysz/AI/refinery-data-refiner

# 1. Test Python imports
python3 -c "import sys; sys.path.insert(0, 'adws'); from adw_modules import utils; print('✅ OK')"

# 2. Test installation script
python3 scripts/test_installation.py

# 3. Try a simple workflow
# (In Claude Code)
# /scout_improved "find CSV parsing code"
```

---

## Need Help?

1. **Rollback instructions**: See main upgrade report
2. **Backup location**: `/Users/alexkamysz/AI/scout_plan_build_mvp/ai_docs/upgrades/refinery_backup_20251125_231038`
3. **Full report**: `refinery_upgrade_report.md`
4. **New CLAUDE.md**: Updated with v4.0 guidance

---

**TL;DR**: Everything you were doing still works. New commands available for session management, git operations, E2E testing, and analysis. Your custom agents and settings preserved. No breaking changes.
