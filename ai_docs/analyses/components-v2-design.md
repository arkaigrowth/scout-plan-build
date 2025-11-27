# Components v2 - Enhanced Installation Manifest

**Created**: 2025-11-26
**Location**: `/scripts/components-v2.yaml`
**Purpose**: Granular, selectable component installation for Scout-Plan-Build framework

## Overview

The v2 manifest transforms the monolithic installation approach into a fine-grained, composable system where users can select exactly what they need.

## Key Enhancements

### 1. Installation Profiles

Four pre-configured profiles for common use cases:

| Profile | Size | Use Case | Components |
|---------|------|----------|------------|
| **Minimal** | 300KB | Quick start, learning | Core commands only |
| **Standard** | 400KB | Production use (recommended) | Commands + hooks + skills |
| **Full** | 1.7MB | Advanced/contributors | Everything including Python modules |
| **Custom** | Variable | Specific needs | User-selected components |

### 2. Granular Slash Commands

Commands are now organized into **6 categories** with subcomponents:

#### Workflow (120KB)
- `core`: Scout → Plan → Build trinity (recommended)
- `all`: All workflow variants
- `legacy`: Deprecated commands (for migration)

#### Git (48KB)
- `basic`: Commit, branch, pull request
- `worktree`: Parallel development system
- `checkpoint`: Undo/redo system
- `all`: Complete git automation

#### Testing (32KB)
- `basic`: Test execution commands
- `resolution`: Failure debugging commands
- `e2e_suites`: E2E test definitions
- `all`: Complete testing suite

#### Session (24KB)
- `all`: Prime, resume, prepare-compaction, start

#### Analysis (36KB)
- `core`: Review and documentation
- `classification`: Issue routing
- `all`: Complete analysis suite

#### Utilities (24KB)
- `minimal`: Just tools and docs
- `standard`: Including install and prepare_app
- `all`: Including setup wizard

### 3. Categorized Hooks

Hooks separated by function with clear recommendations:

#### Recommended (Default)
- `session_start.py`: Auto-load project context
- `pre_compact.py`: Auto-save before compaction

#### Optional
- `user_prompt_submit.py`: Prompt validation
- `notification.py`: Desktop notifications
- `stop.py`: Cleanup on exit

#### Development
- `pre_tool_use.py`: Tool usage logging
- `post_tool_use.py`: Output validation
- `subagent_stop.py`: Agent lifecycle tracking

### 4. Selection Metadata

Each component includes:

```yaml
component:
  default: true/false          # Auto-selected in profile
  recommended: true/false      # Show recommendation badge
  depends_on: []               # Auto-install dependencies
  size_estimate: "120KB"       # Download size
  description: "..."           # User-facing explanation
```

### 5. Dependency Matrix

Explicit dependency tracking prevents broken installations:

```yaml
dependencies:
  slash_commands.git.worktree:
    requires: [scripts.worktree]
    reason: "Worktree commands use worktree_manager.sh"
    optional: false
```

### 6. Core Modules Breakdown

Python modules now have three installation options:

- `all`: Complete framework (1MB)
- `orchestrators_only`: SDLC without agents
- `minimal`: Just scout_simple.py for /build_adw

## Component Architecture

```
Scout-Plan-Build Framework
├── Installation Profiles (quick-select)
│   ├── minimal (300KB)
│   ├── standard (400KB) ← recommended
│   ├── full (1.7MB)
│   └── custom (user-selected)
│
├── Core Modules (1MB)
│   ├── all
│   ├── orchestrators_only
│   └── minimal
│
├── Slash Commands (284KB)
│   ├── workflow (120KB)
│   │   ├── core (recommended)
│   │   ├── all
│   │   └── legacy
│   ├── git (48KB)
│   │   ├── basic
│   │   ├── worktree
│   │   ├── checkpoint
│   │   └── all
│   ├── testing (32KB)
│   │   ├── basic
│   │   ├── resolution
│   │   ├── e2e_suites
│   │   └── all
│   ├── session (24KB)
│   ├── analysis (36KB)
│   │   ├── core
│   │   ├── classification
│   │   └── all
│   └── utilities (24KB)
│       ├── minimal
│       ├── standard
│       └── all
│
├── Hooks (60KB)
│   ├── recommended (session_start, pre_compact)
│   ├── optional (notifications, validation)
│   ├── development (logging, debugging)
│   └── all
│
├── Skills (32KB)
│   ├── all (recommended)
│   └── core
│
├── Scripts (396KB)
│   ├── essential (validate, workflow)
│   ├── worktree
│   ├── utilities
│   └── all
│
└── Directories
    ├── essential (specs, scout_outputs, build_reports)
    ├── standard (+ memory, state, reviews)
    ├── research (videos, articles, papers)
    └── all
```

## Usage Examples

### Example 1: Minimal Installation
```yaml
# Install only core commands
profile: minimal
components:
  - slash_commands.workflow.core
  - slash_commands.utilities.minimal
  - directories.essential
```

### Example 2: Standard Team Setup
```yaml
# Recommended for teams
profile: standard
components:
  - slash_commands.workflow.all
  - slash_commands.git.basic
  - slash_commands.git.worktree
  - slash_commands.testing.basic
  - slash_commands.session.all
  - hooks.recommended
  - skills.all
```

### Example 3: Custom Selection
```yaml
# Just workflow + git, no testing
profile: custom
components:
  - slash_commands.workflow.core
  - slash_commands.git.basic
  - slash_commands.git.worktree
  - directories.standard
```

## Validation System

Profile-specific validation ensures installations are complete:

### Minimal Profile
- Core workflow commands exist
- Essential directories created

### Standard Profile
- All command categories present
- Session commands installed
- Recommended hooks installed
- Memory/state directories created

### Full Profile
- Python modules installed and importable
- All scripts executable
- Complete directory structure
- All command categories present

## Migration from v1

### Breaking Changes
1. Command directory structure reorganized by category
2. Hooks separated by function (recommended/optional/development)
3. Component selection now granular instead of all-or-nothing

### Migration Steps
```bash
# Backup existing installation
cp -r .claude .claude.backup
cp -r adws adws.backup

# Uninstall v1 (preserves data)
./scripts/uninstall.sh --preserve-data

# Install v2 with desired profile
./scripts/install.sh --profile=standard

# Verify migration
python test_installation.py
```

## Component Selection Guidelines

### When to use Minimal
- Learning the framework
- Simple projects (1-3 files)
- Quick prototyping
- Resource-constrained environments

### When to use Standard (Recommended)
- Team collaboration
- Production development
- Multi-file projects (4-10 files)
- Need automation and persistence

### When to use Full
- Contributing to framework
- Custom workflow development
- Advanced automation needs
- Working with orchestrators directly

### When to use Custom
- Specific tool needs
- Incremental adoption
- Existing workflow integration
- Performance optimization

## Size Estimates

| Component Category | Size | Files |
|-------------------|------|-------|
| Core Modules | 1.0MB | ~50 Python files |
| Slash Commands | 284KB | ~40 markdown files |
| Hooks | 60KB | 8 Python files |
| Skills | 32KB | 3 markdown files |
| Scripts | 396KB | ~15 shell/Python scripts |
| **Total Framework** | **1.7MB** | **~116 files** |

## Dependency Graph

```
core_modules.minimal
    ↑
slash_commands.workflow.core
    ↑
directories.essential
    ↑
configurations (always required)

scripts.worktree
    ↑
slash_commands.git.worktree

directories.standard
    ↑
hooks.recommended
```

## Installation UI Recommendations

### Profile Selection Screen
```
┌─────────────────────────────────────────────┐
│ Select Installation Profile                 │
├─────────────────────────────────────────────┤
│ ○ Minimal (300KB)                           │
│   Just commands - Quick start               │
│                                             │
│ ● Standard (400KB) [RECOMMENDED]            │
│   Commands + automation - Production ready  │
│                                             │
│ ○ Full (1.7MB)                              │
│   Everything - For contributors             │
│                                             │
│ ○ Custom                                    │
│   Pick individual components                │
└─────────────────────────────────────────────┘
```

### Component Selection Screen (Custom)
```
┌─────────────────────────────────────────────┐
│ Select Components                           │
├─────────────────────────────────────────────┤
│ Workflow (120KB)                            │
│   ☑ core [RECOMMENDED]                      │
│   ☐ all variants                            │
│   ☐ legacy                                  │
│                                             │
│ Git (48KB)                                  │
│   ☑ basic [RECOMMENDED]                     │
│   ☑ worktree [RECOMMENDED]                  │
│   ☐ checkpoint                              │
│                                             │
│ Hooks (60KB)                                │
│   ☑ recommended [RECOMMENDED]               │
│   ☐ optional                                │
│   ☐ development                             │
└─────────────────────────────────────────────┘
```

## Next Steps

1. **Implement installer** that reads components-v2.yaml
2. **Add interactive UI** for component selection
3. **Create migration script** from v1 to v2
4. **Update documentation** with new structure
5. **Add validation** for component dependencies

## Benefits

- **Flexibility**: Install only what you need
- **Clarity**: Components clearly categorized
- **Efficiency**: Smaller installations for simple use cases
- **Maintainability**: Clear dependency tracking
- **Extensibility**: Easy to add new components
- **Documentation**: Self-documenting with metadata

## Technical Notes

### Installer Implementation
The installer should:
1. Parse component dependencies
2. Validate selections (check requires/depends_on)
3. Install in dependency order
4. Run profile-specific validation
5. Generate .adw_config.json with installed components

### Uninstaller Enhancement
Track installed components in `.adw_install_manifest.json`:
```json
{
  "version": "2.0.0",
  "profile": "standard",
  "components": [
    "slash_commands.workflow.core",
    "slash_commands.git.basic",
    "hooks.recommended"
  ],
  "installed_at": "2025-11-26T10:30:00Z"
}
```

This enables surgical uninstallation of specific components.

---

**Status**: Design complete, ready for installer implementation
**Impact**: Transforms framework from monolithic to modular
**Effort**: ~8 hours for installer + UI + migration script
