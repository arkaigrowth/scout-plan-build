# Dependency Tracer v2.1

**Zero MCP overhead. Zero context bloat. Environment-aware. Fix conversation (subagent)-optimized. Portable everywhere.**

Traces file references and Python imports using deterministic CLI tools. Context-aware with surgical summary modes (100 tokens vs 50K+).

## What's New in v2.1

✅ **Environment Detection** - Auto-detects Claude Code CLI vs Claude Web
✅ **Smart Paths** - Non-invasive defaults (`.dependency-traces/` fallback)
✅ **scout_outputs/ Respect** - Uses if exists, doesn't force on other repos
✅ **Terminology** - "fix conversation (subagent)" for clarity
✅ **ADW Stub** - Python template for repo Claude to implement
✅ **Claude Web** - Full support with `/mnt/user-data/outputs/`
✅ **ASCII Diagrams** - Visual dependency trees and broken reference maps  

## Quick Start

```bash
# 1. Install tools (5 min, one-time)
bash scripts/setup.sh

# 2. Test installation
bash scripts/test_skill.sh

# 3. Trace dependencies (minimal context - 100 tokens)
CONTEXT_MODE=minimal bash scripts/trace_all.sh

# 4. Read summary (not full JSON!)
cat scout_outputs/traces/latest/summary.md
# or .dependency-traces/latest/summary.md

# 5. Generate ASCII diagrams (NEW!)
python scripts/generate_ascii_diagrams.py scout_outputs/traces/latest/python_imports.json
```

## Architecture: Data Producer, Not Context Consumer

**The Problem:**
```
Script → JSON → Claude reads full JSON → 50K tokens wasted
```

**The Solution:**
```
Script → JSON + Summary → Claude reads summary → 100 tokens
                       └→ Spawns fix conversations (subagents) → N × 300 tokens
```

**Token Efficiency:**
- Traditional MCP + full JSON: **60,000 tokens**
- v2.1 minimal + fix conversations (10 broken refs): **3,100 tokens**
- **Savings: 95%+**

## ASCII Dependency Diagrams

Generate visual representations of your dependencies without leaving the terminal:

```bash
python scripts/generate_ascii_diagrams.py trace_results.json [output.md]
```

**Four Diagram Types:**

### 1. Import Statistics
```
Total Imports: 324
├─ ✓ Valid: 316 (97%)
└─ ✗ Broken: 8 (2%)
```

### 2. Dependency Tree
```
├─ ✓ adw_build.py (13 imports, 0 broken)
│  ├─ ✓ sys [import] (installed)
│  ├─ ✓ adw_modules.state [from] (local)
│  └─ ✓ adw_modules.git_ops [from] (local)
└─ ✗ adw_fix_dependencies.py (8 imports, 1 broken)
   ├─ ✓ json [import] (installed)
   └─ ✗ **adws.adw_modules.state** [from] (BROKEN)
```

### 3. Broken Reference Map
```
BROKEN MODULES
│
├─ ✗ schedule (1 file)
│  └─ trigger_cron.py
└─ ✗ pytest (1 file)
   └─ test_validators.py
```

### 4. Module Hierarchy
```
Local Module Structure:
│
├─ ✓ adw_modules
│  ├─ ✓ agent
│  ├─ ✓ data_types
│  └─ ✓ utils
└─ ✓ scripts
   └─ ✓ dependency-tracer
```

## Output Structure

**Local (Claude Code or terminal):**
```
your-project/
├── scout_outputs/traces/      # IF scout_outputs/ exists
│   └── latest/ → ...
├── ai_docs/analyses/traces/   # IF ai_docs/ exists
│   └── latest/ → ...
└── .dependency-traces/        # Hidden fallback (non-invasive)
    └── 2024-11-23_183045/
        ├── command_refs.json
        ├── python_imports.json
        └── summary.md
```

**Claude Web:**
```
/mnt/user-data/outputs/dependency-traces/
└── 2024-11-23_183045/
    ├── command_refs.json
    ├── python_imports.json
    └── summary.md
```

## Context Modes

| Mode | Tokens | Use When |
|------|--------|----------|
| **minimal** | 100 | Just need counts, spawn fix conversations (subagents) |
| **summary** | 500-2K | Need to see broken refs for triage |
| **full** | 5-50K | Avoid! Use only in fix conversations (subagents) |

```bash
# Recommended: minimal mode
CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws

# Moderate: summary mode
CONTEXT_MODE=summary bash scripts/trace_python_imports.sh adws

# Danger: full mode (avoid in main conversation!)
CONTEXT_MODE=full bash scripts/trace_python_imports.sh adws
```

## Use Cases

### 1. Trace File References in `.claude/commands/`
```bash
CONTEXT_MODE=minimal bash scripts/trace_command_refs.sh .claude/commands
```

Finds broken links to scripts, configs, other files.

### 2. Trace Python Imports in `adws/`
```bash
CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws
```

Finds missing packages, broken imports, validates local modules.

### 3. Build Dependency Graph
```bash
python3 scripts/build_dep_graph.py \
  scout_outputs/traces/latest/python_imports.json \
  scout_outputs/traces/latest/dep_graph.json
```

Shows circular deps, criticality scores, orphaned files.

### 4. Automate Fixes via ADW (Stub)
```bash
# TODO: Implement with repo Claude
python3 scripts/adw_spawn_fix_agents.py \
  scout_outputs/traces/latest/python_imports.json
```

Spawns one fix conversation (subagent) per broken reference using ADW framework.

## Fix Conversation (Subagent) Workflow

**Main Conversation (100 tokens):**
```bash
CONTEXT_MODE=minimal bash scripts/trace_all.sh
```

Receives:
```json
{
  "total_valid": 161,
  "total_broken": 9,
  "message": "Found 9 broken imports. Read summary_file for details."
}
```

**Spawn Fix Conversations (Subagents) (300 tokens each):**
```
For each broken reference:
  1. Fix conversation (subagent) reads ONE entry from full JSON
  2. Suggests fix
  3. Writes to traces/latest/fixes/fix_X.md
```

**Total:** 100 + (9 × 300) = **2,800 tokens** (vs 50K+)

## Environment Detection

| Environment | Detection | Output Location |
|-------------|-----------|-----------------|
| **Claude Code CLI** | No `/mnt/user-data/` | Smart defaults (scout_outputs/, ai_docs/, or `.dependency-traces/`) |
| **Claude Web** | `/mnt/user-data/uploads` exists | `/mnt/user-data/outputs/dependency-traces/` |
| **Terminal** | No `/mnt/user-data/` | Smart defaults |

## IDE Integration

### IntelliJ IDEA
```bash
# Terminal (⌥F12)
CONTEXT_MODE=minimal bash scripts/trace_all.sh
cat scout_outputs/traces/latest/summary.md
```

Or configure External Tool:
- Settings → Tools → External Tools → Add
- Program: `bash`
- Arguments: `$ProjectFileDir$/scripts/trace_all.sh`

### VSCode
Add to `.vscode/tasks.json`:
```json
{
  "label": "Trace Dependencies",
  "type": "shell",
  "command": "CONTEXT_MODE=minimal bash scripts/trace_all.sh"
}
```

## CI/CD Integration

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws > result.json
broken=$(jq '.broken' result.json)

if [ "$broken" -gt 0 ]; then
  echo "❌ Found $broken broken imports"
  cat .dependency-traces/latest/summary.md
  exit 1
fi
```

### GitHub Actions
```yaml
- name: Validate Dependencies
  run: |
    CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws > result.json
    broken=$(jq '.broken' result.json)
    [ "$broken" -eq 0 ] || exit 1
```

## Files

```
dependency-tracer-v2.1/
├── SKILL.md                          # Complete documentation
├── README.md                         # This file
├── QUICKSTART.md                     # 5-minute guide
├── CHANGELOG.md                      # Version history
├── LICENSE.txt                       # MIT license
├── scripts/
│   ├── setup.sh                      # Install tools
│   ├── test_skill.sh                 # Validate installation
│   ├── trace_command_refs.sh         # Trace .claude/commands
│   ├── trace_python_imports.sh       # Trace Python imports
│   ├── trace_all.sh                  # Fix conversation (subagent)-optimized wrapper
│   ├── build_dep_graph.py            # Build dependency graph
│   └── adw_spawn_fix_agents.py       # ADW integration stub (TODO)
└── examples/
    ├── minimal_output.json           # Example minimal mode
    ├── summary_output.json           # Example summary mode
    └── README.md                     # Examples explained
```

## Best Practices

1. ✅ Always use `CONTEXT_MODE=minimal` for main conversation
2. ✅ Read `summary.md`, not JSON files
3. ✅ Spawn fix conversations (subagents) for fixes (one per broken ref)
4. ✅ Use timestamps for history tracking
5. ❌ Never `cat` full JSON in main conversation
6. ❌ Never use `CONTEXT_MODE=full` in main conversation

## Comparison

| Dimension | v2.0 | v2.1 |
|-----------|------|------|
| Environment detection | None | Auto-detects |
| scout_outputs/ | Always use | Use if exists |
| Fallback output | `.dependency-traces/` | `.dependency-traces/` |
| Claude Web | Partial | Full support |
| Terminology | "subagent" | "fix conversation (subagent)" |
| ADW integration | None | Stub with TODOs |

## Next Steps

1. `bash scripts/setup.sh` - Install tools
2. `bash scripts/test_skill.sh` - Validate
3. `CONTEXT_MODE=minimal bash scripts/trace_all.sh` - Run
4. `cat scout_outputs/traces/latest/summary.md` - Review
5. Spawn fix conversations (subagents) for fixes (if needed)
6. Add to CI/CD pipeline
7. Implement ADW stub (optional)

## License

MIT License - See LICENSE.txt

## Credits

Built based on feedback from Claude Code steelmanning session.
Implements "data producer, not context consumer" architecture.
v2.1 adds environment detection and non-invasive defaults.
