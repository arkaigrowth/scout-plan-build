# Plugin Conversion & Upgrade Strategy

**ADW ID**: PLUGIN-001
**Created**: 2025-11-25
**Status**: Planning
**Priority**: High

---

## Overview

This spec covers two related concerns:
1. **Plugin Conversion**: Converting Scout-Plan-Build to a Claude Code Plugin format
2. **Upgrade Strategy**: Safely upgrading existing repos from older framework versions

---

## Part 1: Plugin Conversion

### What is a Claude Code Plugin?

A plugin is a packaged bundle of:
- Slash commands (`.claude/commands/`)
- Hooks (`.claude/hooks/`)
- Skills (`.claude/skills/`)
- MCP servers (optional)
- Subagents (optional)

**Key file**: `plugin.json` - manifest describing the plugin

### Plugin.json Schema

```json
{
  "name": "scout-plan-build",
  "version": "1.0.0",
  "description": "Structured AI development workflows: Scout → Plan → Build",
  "author": "arkaigrowth",
  "license": "MIT",
  "homepage": "https://github.com/arkaigrowth/scout-plan-build",
  "keywords": ["workflow", "planning", "agentic", "development"],

  "commands": ".claude/commands/",
  "hooks": ".claude/hooks/",
  "skills": ".claude/skills/",

  "agents": {
    "description": "Subagent definitions",
    "path": "agents/"
  },

  "dependencies": {
    "python": ">=3.10",
    "required": ["pydantic", "python-dotenv", "gitpython"],
    "optional": ["anthropic", "boto3"]
  }
}
```

### Installation Method (After Conversion)

```bash
# Instead of curl installer:
/plugin install github:arkaigrowth/scout-plan-build

# Or from local path during development:
/plugin install /path/to/scout-plan-build
```

### State Management Considerations

The plugin format handles **static assets** (commands, hooks, skills) but NOT:
- Python modules (`adws/`)
- Directory structure (`specs/`, `ai_docs/`, `scout_outputs/`)
- Configuration files (`.adw_config.json`)

**Hybrid Approach Required**:
```
┌─────────────────────────────────────────────────────┐
│  PLUGIN (via /plugin install)                       │
│  ├─ .claude/commands/    ← Slash commands           │
│  ├─ .claude/hooks/       ← Event hooks              │
│  └─ .claude/skills/      ← SKILL.md files           │
├─────────────────────────────────────────────────────┤
│  POST-INSTALL SCRIPT (via install.sh --modules)     │
│  ├─ adws/                ← Python modules           │
│  ├─ specs/               ← Directory structure      │
│  ├─ ai_docs/             ← Directory structure      │
│  ├─ scout_outputs/       ← Directory structure      │
│  └─ .adw_config.json     ← Configuration            │
└─────────────────────────────────────────────────────┘
```

### Deterministic Guidance Flow

```
User: "I want to add OAuth to my app"
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  SKILL.md Activation (from plugin)                  │
│  Trigger: "add feature", "implement", "build"       │
│  Action: Guide to Scout → Plan → Build workflow     │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  Slash Command Execution                            │
│  1. /scout_improved "OAuth authentication"          │
│  2. /plan_w_docs_improved "..." "..." "files.json"  │
│  3. /build_adw "specs/oauth-spec.md"                │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  State Management (adws/)                           │
│  - ADWState tracks workflow progress                │
│  - agents/{adw_id}/ stores state.json               │
│  - Enables resume and audit                         │
└─────────────────────────────────────────────────────┘
```

### Implementation Tasks

| Task | Effort | Priority |
|------|--------|----------|
| Create `plugin.json` | 1 hr | P0 |
| Create `SKILL.md` for workflow activation | 2 hrs | P0 |
| Test `/plugin install` from local path | 1 hr | P0 |
| Update `install.sh` to support `--modules-only` mode | 2 hrs | P1 |
| Document hybrid installation flow | 1 hr | P1 |
| Publish to personal marketplace JSON | 1 hr | P2 |

---

## Part 2: Upgrade Strategy

### Current State of Existing Repos

| Repo | .claude/ | adws/ | Version | Notes |
|------|----------|-------|---------|-------|
| `meow_loader_v2` | 40 commands | ✅ Present | Old | settings.local.json exists |
| `refinery-data-refiner` | 6 commands | ✅ Present | Newer | settings.local.json exists |

### Files to PRESERVE (Never Delete)

```
.claude/settings.local.json    # User's local settings
.env                           # API keys, secrets
.adw_config.json              # IF user has customizations
specs/*.md                     # User's specification files
ai_docs/**/*.md               # User's documentation
CLAUDE.md                     # IF user has customizations (merge)
```

### Files to REPLACE (Framework Files)

```
adws/                         # Python modules (full replace)
.claude/commands/             # Slash commands (full replace)
.claude/hooks/                # Event hooks (full replace)
.claude/skills/               # Skills (full replace)
scripts/validate_pipeline.sh  # Validation script
scripts/install_to_new_repo.sh
.env.template                 # Template (don't touch .env)
```

### Files to CHECK for Conflicts

```
CLAUDE.md                     # May have user customizations
.adw_config.json             # May have custom paths
.gitignore                   # May need merging
```

### Upgrade Workflow

```
┌─────────────────────────────────────────────────────┐
│  PHASE 1: AUDIT                                     │
│  ├─ Check for .scout_install_info.json (version)    │
│  ├─ List files that will be replaced                │
│  ├─ List files that will be preserved               │
│  ├─ Detect potential conflicts                      │
│  └─ Show summary, ask for confirmation              │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 2: BACKUP                                    │
│  ├─ Create .scout_backup_{timestamp}/               │
│  ├─ Copy ALL .claude/ contents                      │
│  ├─ Copy adws/                                      │
│  ├─ Copy CLAUDE.md, .adw_config.json               │
│  └─ Record backup location                          │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 3: UNINSTALL OLD                             │
│  ├─ Remove adws/ (full directory)                   │
│  ├─ Remove .claude/commands/ contents               │
│  ├─ Remove .claude/hooks/ contents                  │
│  ├─ Remove .claude/skills/ contents                 │
│  ├─ KEEP .claude/settings.local.json               │
│  ├─ KEEP .claude/agents/ (if exists)               │
│  └─ KEEP .claude/memory/ (if exists)               │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 4: INSTALL NEW                               │
│  ├─ Run install.sh --full                           │
│  ├─ Restore .claude/settings.local.json             │
│  ├─ Merge CLAUDE.md if user had customizations      │
│  ├─ Preserve .adw_config.json customizations        │
│  └─ Create new .scout_install_info.json             │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 5: VALIDATE                                  │
│  ├─ Run test_installation.py                        │
│  ├─ Verify Python imports work                      │
│  ├─ Check slash commands available                  │
│  ├─ Compare with backup for unexpected changes      │
│  └─ Report success/warnings                         │
└─────────────────────────────────────────────────────┘
```

### Upgrade Command Design

```bash
# New flag for install.sh
curl -sL URL | bash -s -- /path/to/repo --upgrade

# What --upgrade does:
# 1. Detects existing installation
# 2. Runs backup phase
# 3. Runs uninstall phase
# 4. Runs install phase
# 5. Runs validation phase
```

### Conflict Detection Rules

| Conflict Type | Detection | Resolution |
|---------------|-----------|------------|
| Custom CLAUDE.md | Diff against template | Merge, keep user sections |
| Custom .adw_config.json | Check for non-default values | Preserve user values |
| Extra .claude/ folders | Check for unexpected dirs | Keep, warn user |
| Custom slash commands | Commands not in framework | Keep in separate dir |
| Different Python version | Check sys.version | Warn if < 3.10 |

### Testing Strategy

**Approach: Copy-then-test**

```bash
# 1. Create temp copy of existing repo
cp -r /path/to/meow_loader_v2 /tmp/meow_test

# 2. Run upgrade on copy
curl -sL URL | bash -s -- /tmp/meow_test --upgrade --dry-run

# 3. If dry-run looks good, run for real
curl -sL URL | bash -s -- /tmp/meow_test --upgrade

# 4. Validate
cd /tmp/meow_test && python scripts/test_installation.py

# 5. If all good, run on real repo
```

---

## Part 3: Implementation Plan

### Phase A: Update install.sh (2-3 hours)

Add these features:
1. `--upgrade` flag with backup/uninstall/install flow
2. `--dry-run` that works with --upgrade
3. Better conflict detection
4. Version tracking via `.scout_install_info.json`

### Phase B: Create Plugin Format (2-3 hours)

1. Create `plugin.json`
2. Create workflow `SKILL.md`
3. Test with `/plugin install` locally
4. Document hybrid installation

### Phase C: Test on Existing Repos (1-2 hours)

1. Test on copy of `meow_loader_v2`
2. Test on copy of `refinery-data-refiner`
3. Document any issues found
4. Fix upgrade script as needed

### Phase D: Documentation (1 hour)

1. Update QUICK_REFERENCE.md with upgrade info
2. Add "Upgrading from older versions" section
3. Document backup/restore process

---

## Agentic Engineering Best Practices Applied

### 1. Deterministic Workflow
- Spec defines exact phases and transitions
- Each phase has clear inputs/outputs
- Validation gates prevent partial states

### 2. State Management
- `.scout_install_info.json` tracks installation state
- `.scout_backup_{timestamp}/` enables rollback
- ADWState pattern extended to installation

### 3. Fail-Safe Design
- Backup before any destructive operation
- Dry-run mode for preview
- Validation after every phase

### 4. Incremental Approach
- Phase A can ship independently
- Phase B builds on A
- Each phase is testable

### 5. User File Preservation
- Explicit list of "never touch" files
- Merge strategy for configurable files
- Backup everything before changes

---

## Next Steps

1. [ ] Implement `--upgrade` flag in install.sh
2. [ ] Test upgrade on temp copies of existing repos
3. [ ] Create plugin.json and SKILL.md
4. [ ] Test hybrid plugin + modules installation
5. [ ] Update documentation
6. [ ] Run real upgrades on meow_loader_v2 and refinery

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| User loses customizations | Medium | High | Comprehensive backup |
| Upgrade leaves partial state | Low | High | Transaction-like phases |
| Plugin format doesn't support all features | Medium | Medium | Hybrid approach |
| Version mismatch causes issues | Low | Medium | Clear version tracking |

---

## Questions to Resolve

1. Should we support rollback to previous version?
2. How do we handle repos with very old versions (no .scout_install_info.json)?
3. Should plugin installation auto-run the modules installer?

