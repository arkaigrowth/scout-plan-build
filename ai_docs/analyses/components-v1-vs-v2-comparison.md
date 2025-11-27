# Components v1 vs v2 - Comparison

**Date**: 2025-11-26

## Quick Comparison

| Aspect | v1 (Current) | v2 (Enhanced) |
|--------|--------------|---------------|
| **Granularity** | 5 components | 50+ subcomponents |
| **Profiles** | None (all or nothing) | 4 profiles (minimal/standard/full/custom) |
| **Selection** | Binary (install/skip) | Hierarchical (category → subcomponent) |
| **Size Control** | Install all 1.7MB | Choose from 300KB to 1.7MB |
| **Dependencies** | Implicit | Explicit tracking with validation |
| **Metadata** | Basic description | default, recommended, size_estimate, depends_on |
| **Validation** | Generic checks | Profile-specific validation |
| **Command Organization** | Flat list | 6 categories with subcategories |
| **Hooks Organization** | All or none | Recommended/Optional/Development |

## Installation Size Comparison

### v1: One Size Fits All
```
┌────────────────────────────────┐
│ Full Installation: 1.7MB       │
├────────────────────────────────┤
│ ✓ Core modules (1MB)           │
│ ✓ All commands (284KB)         │
│ ✓ All hooks (60KB)             │
│ ✓ All skills (32KB)            │
│ ✓ All scripts (396KB)          │
└────────────────────────────────┘
```

### v2: Choose Your Size
```
Minimal: 300KB                Standard: 400KB             Full: 1.7MB
┌──────────────────┐          ┌──────────────────┐        ┌──────────────────┐
│ Core commands    │          │ All commands     │        │ Python modules   │
│ Essential dirs   │          │ + Hooks          │        │ + All commands   │
│                  │          │ + Skills         │        │ + All hooks      │
│                  │          │ + Directories    │        │ + All skills     │
│                  │          │                  │        │ + All scripts    │
└──────────────────┘          └──────────────────┘        └──────────────────┘
    Quick start                  Recommended                  Everything
```

## Component Structure Comparison

### v1: Flat Structure
```
components:
  - core_modules (all or nothing)
  - slash_commands (all or nothing)
  - hooks (all or nothing)
  - skills (all or nothing)
  - scripts (all or nothing)
```

### v2: Hierarchical Structure
```
components:
  core_modules:
    - all
    - orchestrators_only
    - minimal

  slash_commands:
    workflow:
      - core
      - all
      - legacy
    git:
      - basic
      - worktree
      - checkpoint
      - all
    testing:
      - basic
      - resolution
      - e2e_suites
      - all
    session:
      - all
    analysis:
      - core
      - classification
      - all
    utilities:
      - minimal
      - standard
      - all

  hooks:
    - recommended
    - optional
    - development
    - all

  skills:
    - all
    - core

  scripts:
    - essential
    - worktree
    - utilities
    - all
```

## User Experience Comparison

### v1: Limited Flexibility
```bash
# Install everything or nothing
./install.sh

# Want just commands? Edit manifest manually
# Want to skip hooks? Edit manifest manually
# Want minimal install? Not supported
```

### v2: Fine-Grained Control
```bash
# Quick profiles
./install.sh --profile=minimal      # 300KB, just commands
./install.sh --profile=standard     # 400KB, recommended
./install.sh --profile=full         # 1.7MB, everything

# Custom selection
./install.sh --custom \
  --select=slash_commands.workflow.core \
  --select=slash_commands.git.basic \
  --select=hooks.recommended

# Interactive mode
./install.sh --interactive
# Shows UI for component selection
```

## Dependency Handling

### v1: Implicit Dependencies
```yaml
# No dependency tracking
# If you install git.worktree but skip scripts.worktree
# Commands will fail at runtime
```

### v2: Explicit Dependencies
```yaml
dependencies:
  slash_commands.git.worktree:
    requires: [scripts.worktree]
    reason: "Worktree commands use worktree_manager.sh"
    optional: false

# Installer validates and auto-installs dependencies
# Or warns if required dependency is not selected
```

## Validation Comparison

### v1: Generic Validation
```yaml
validation:
  checks:
    - "Core modules directory exists"
    - "Plan command installed"
    - "Build command installed"
    - "Config file exists"
    # Same checks for all installations
```

### v2: Profile-Specific Validation
```yaml
validation:
  profiles:
    minimal:
      checks:
        - "Core workflow commands exist"

    standard:
      checks:
        - "Workflow commands installed"
        - "Session commands installed"
        - "Essential directories created"
        - "Recommended hooks installed"

    full:
      checks:
        - "Python modules installed"
        - "All command categories present"
        - "Scripts executable"
        # More comprehensive checks
```

## Use Case Mapping

### Scenario 1: "I just want to try the framework"
**v1**: Install 1.7MB, figure out what you need later
**v2**: `--profile=minimal` → 300KB, core commands only

### Scenario 2: "I need parallel development with worktrees"
**v1**: Install everything, hope dependencies are met
**v2**: `--select=slash_commands.git.worktree` → Auto-installs scripts.worktree

### Scenario 3: "I want automation but not Python modules"
**v1**: Edit manifest manually, remove core_modules
**v2**: `--profile=standard` → Gets commands + hooks + skills (no Python)

### Scenario 4: "I only need workflow commands, no git/testing"
**v1**: Install everything, ignore what you don't need
**v2**: `--custom --select=slash_commands.workflow.core`

### Scenario 5: "I want to contribute to the framework"
**v1**: Install everything
**v2**: `--profile=full` → Clear intent, validated installation

## Migration Path

### From v1 to v2

```bash
# Step 1: Backup current installation
cp -r .claude .claude.v1.backup
cp -r adws adws.v1.backup

# Step 2: Check what you have
./scripts/analyze_installation.sh
# Output: "You have: core_modules, slash_commands, hooks"

# Step 3: Uninstall v1
./scripts/uninstall.sh --preserve-data

# Step 4: Install v2 with equivalent profile
./scripts/install.sh --profile=standard

# Step 5: Validate
python test_installation.py
```

## Metadata Enhancement

### v1: Basic Metadata
```yaml
slash_commands:
  source: ".claude/commands/"
  destination: ".claude/commands/"
  description: "Workflow slash commands"
  required: true
```

### v2: Rich Metadata
```yaml
slash_commands:
  description: "Workflow automation slash commands"
  default: true              # Auto-selected in standard profile
  recommended: true          # Show recommendation badge
  size_estimate: "284KB"     # For download estimation

  subcomponents:
    workflow:
      description: "Scout → Plan → Build workflow commands"
      default: true
      recommended: true
      size_estimate: "120KB"

      components:
        core:
          description: "Essential workflow trinity"
          default: true
          recommended: true   # Shows ⭐ RECOMMENDED badge
          files: [...]
```

## Benefits Summary

### For Beginners
- **v1**: Overwhelming (install 116 files, figure out what they do)
- **v2**: Guided (start with minimal, grow as needed)

### For Teams
- **v1**: One-size-fits-all (everyone gets everything)
- **v2**: Flexible (teams choose what they need)

### For Contributors
- **v1**: Unclear what's essential vs optional
- **v2**: Clear categorization and dependencies

### For Maintainers
- **v1**: Hard to test different configurations
- **v2**: Profile-based testing (test minimal, standard, full)

## File Count Comparison

### v1: Binary Choice
- Install: 116 files (1.7MB)
- Don't install: 0 files

### v2: Flexible Options
- Minimal: ~15 files (300KB)
- Standard: ~45 files (400KB)
- Full: ~116 files (1.7MB)
- Custom: Variable

## Uninstall Comparison

### v1: All or Nothing
```bash
# Remove everything
./uninstall.sh

# Can't remove just hooks or just skills
```

### v2: Surgical Removal
```bash
# Remove specific components
./uninstall.sh --remove=hooks.optional
./uninstall.sh --remove=slash_commands.testing

# Remove by profile
./uninstall.sh --profile=minimal
# Keeps only what's in minimal profile
```

## Conclusion

**v2 advantages**:
- 80% smaller for simple use cases (minimal)
- Hierarchical organization (easier to understand)
- Explicit dependencies (prevents broken installations)
- Profile-based validation (ensures correctness)
- Fine-grained control (install only what you need)
- Better documentation (metadata explains everything)

**Migration complexity**: Low
- v1 manifest remains compatible
- Migration script handles conversion
- Data preservation guaranteed

**Recommendation**: Adopt v2 for 3.0 release
- Major version bump (breaking change in structure)
- Migration guide included
- Backward compatibility mode available

---

**Impact**: Transforms user experience from "all or nothing" to "choose your adventure"
**Risk**: Low (v1 manifest can coexist during transition)
**Effort**: ~8 hours for implementation + testing
