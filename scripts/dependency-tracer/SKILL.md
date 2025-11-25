---
name: dependency-tracer
description: Trace file references in .claude/commands/ and Python imports in adws/ using direct CLI tools. Environment-aware (Claude Code vs Web), context-optimized with surgical summary mode. Non-invasive output defaults. Fix conversation (subagent)-ready architecture.
version: 2.1
---

# Dependency Tracer v2.1

**Zero MCP overhead. Zero zombie processes. Zero context bloat. Environment-aware. Portable everywhere.**

Traces file references and import statements using deterministic CLI tools. Designed for token efficiency with surgical context modes (minimal: 100 tokens, summary: 500-2K tokens, full: 5-50K tokens).

## What's New in v2.1

✅ **Environment Detection**: Auto-detects Claude Code CLI vs Claude Web
✅ **Smart Path Handling**: Non-invasive defaults (`.dependency-traces/` fallback)
✅ **scout_outputs/ Respect**: Uses if exists, doesn't create if missing
✅ **Terminology Update**: "fix conversation (subagent)" for clarity
✅ **ADW Integration Stub**: Python template for repo Claude to implement
✅ **Claude Web Support**: Outputs to `/mnt/user-data/outputs/` when needed
✅ **ASCII Diagram Generation**: Visual dependency trees and broken reference maps  

## Architecture Principle

> **"The skill should be a data producer, not a context consumer."**

Traditional approach:
```
Script → JSON → Claude reads full JSON → 50K tokens wasted
```

This approach:
```
Script → JSON + Summary → Claude reads summary → 100 tokens
                       └→ Spawns fix conversations (subagents) → N × 300 tokens
```

**Result:** 100 + (N × 300) tokens instead of 50K+

## Environment Detection

The skill auto-detects where it's running:

| Environment | Detection | Project Root | Output Location |
|-------------|-----------|--------------|-----------------|
| **Claude Code CLI** | No `/mnt/user-data/` | Actual project dir | Smart defaults (see below) |
| **Claude Web** | `/mnt/user-data/uploads` exists | `/mnt/user-data/uploads` (read-only) | `/mnt/user-data/outputs/dependency-traces/` |
| **Terminal** | No `/mnt/user-data/` | Current directory | Smart defaults (see below) |

### Smart Output Defaults (Local Environment)

**Priority order** (non-invasive):
1. `scout_outputs/traces/` - IF directory already exists
2. `ai_docs/analyses/traces/` - IF directory already exists
3. `.dependency-traces/` - Created as hidden fallback (doesn't pollute repo)

**Key principle:** Don't create `scout_outputs/` unless it already exists. This respects your repo convention while not forcing it on others.

## Prerequisites

```bash
# macOS or Linux
brew install ripgrep ast-grep jq

# Verification
which rg ast-grep jq python3
```

## Core Workflow

### Phase 1: Discovery (0 tokens - deterministic)
CLI tools extract all references, imports, patterns → structured JSON

### Phase 2: Validation (0 tokens - deterministic)
File existence checks, Python import validation → status per reference

### Phase 3: Summary Generation (0 tokens - deterministic)
Statistics, broken refs, suggested fixes → human-readable summary.md

### Phase 4: Context Delivery (100-500 tokens - surgical)
Main conversation reads ONLY summary. Spawns fix conversations (subagents) for detailed analysis.

## Output Structure

**Local (Claude Code or terminal):**
```
your-project/
├── scout_outputs/traces/         ← IF scout_outputs/ exists
│   └── latest/ → 2024-11-23.../
├── ai_docs/analyses/traces/      ← IF ai_docs/ exists
│   └── latest/ → 2024-11-23.../
└── .dependency-traces/           ← Fallback (hidden)
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

## Context Modes (Token Management)

### MINIMAL (100 tokens) - Default, recommended
```bash
CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws
```
Returns: `{total, valid, broken, output_file, message}`

**Use when:** You just need counts. Spawn fix conversations (subagents) for details.

### SUMMARY (500-2000 tokens) - Moderate use
```bash
CONTEXT_MODE=summary bash scripts/trace_python_imports.sh adws
```
Returns: `{stats, broken_imports: [...], broken_modules: [...]}`

**Use when:** You need to see which imports are broken to triage.

### FULL (5000-50000 tokens) - Avoid in main conversation!
```bash
CONTEXT_MODE=full bash scripts/trace_python_imports.sh adws
```
Returns: Complete JSON with all references.

**Use when:** Absolutely necessary, or in isolated fix conversation (subagent) context.

## Use Case 1: Trace File References in `.claude/commands/`

### Script: `trace_command_refs.sh`

**What it does:**
- Extracts all file paths from markdown files
- Validates file existence
- Outputs to smart location (respects environment)

**Portability:**
- Uses ripgrep (fast) with sed fallback (portable)
- No `grep -oP` (macOS incompatible)
- Works on Linux, macOS, any Unix-like system

**Usage:**
```bash
# Minimal context (recommended)
CONTEXT_MODE=minimal bash scripts/trace_command_refs.sh .claude/commands

# Summary context
CONTEXT_MODE=summary bash scripts/trace_command_refs.sh .claude/commands

# Custom output directory
bash scripts/trace_command_refs.sh .claude/commands /path/to/output
```

**Output (minimal):**
```json
{
  "total": 42,
  "valid": 38,
  "broken": 4,
  "output_file": "scout_outputs/traces/latest/command_refs.json",
  "message": "Found 4 broken references. Read summary_file for details."
}
```

## Use Case 2: Generate ASCII Dependency Diagrams

### Script: `generate_ascii_diagrams.py`

**What it does:**
- Visualizes import dependencies as ASCII trees
- Highlights broken references with visual indicators
- Groups imports by file and module
- Shows statistics and module hierarchy

**Diagram Types:**
1. **Import Statistics Summary** - Overview with percentages
2. **Import Dependency Tree** - File-by-file import listing
3. **Broken Reference Map** - Focused view of problems
4. **Module Hierarchy** - Package structure visualization

**Usage:**
```bash
# Generate diagrams from trace results
python scripts/generate_ascii_diagrams.py scout_outputs/traces/latest/python_imports.json

# Save to file
python scripts/generate_ascii_diagrams.py scout_outputs/traces/latest/python_imports.json diagrams.md

# For command references
python scripts/generate_ascii_diagrams.py scout_outputs/traces/latest/command_refs.json
```

**Sample Output:**
```
# Import Statistics Summary
Total Imports: 324
├─ ✓ Valid: 316 (97%)
└─ ✗ Broken: 8 (2%)

# Broken Reference Map
BROKEN MODULES
│
├─ ✗ schedule (1 file)
│  └─ trigger_cron.py
└─ ✗ pytest (1 file)
   └─ test_validators.py
```

## Use Case 3: Trace Python Imports in `adws/`

### Script: `trace_python_imports.sh`

**What it does:**
- Extracts imports with ast-grep
- Validates with Python introspection
- Detects local vs installed modules
- Suggests fixes (pip install commands)

**Improvements:**
- ✅ Fixed jq bug (proper cross-reference join)
- ✅ Distinguishes local modules from packages
- ✅ Auto-generates fix suggestions
- ✅ Environment-aware output paths

**Usage:**
```bash
# Minimal context (recommended)
CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws

# Summary context (see broken imports)
CONTEXT_MODE=summary bash scripts/trace_python_imports.sh adws

# Custom output
bash scripts/trace_python_imports.sh adws /path/to/output
```

**Output (minimal):**
```json
{
  "total": 128,
  "valid": 123,
  "broken": 5,
  "output_file": ".dependency-traces/2024-11-23_183045/python_imports.json",
  "summary_file": ".dependency-traces/2024-11-23_183045/summary.md",
  "message": "Found 5 broken imports. Read summary_file for details."
}
```

## Advanced: Dependency Graph

### Script: `build_dep_graph.py`

**What it does:**
- Builds directed dependency graph
- Finds circular dependencies
- Calculates criticality scores (how many files depend on each module)
- Identifies orphaned files, leaf nodes, root nodes

**Usage:**
```bash
# Local environment
python3 scripts/build_dep_graph.py \
  scout_outputs/traces/latest/python_imports.json \
  scout_outputs/traces/latest/dep_graph.json

# Claude Web environment
python3 scripts/build_dep_graph.py \
  /mnt/user-data/outputs/dependency-traces/latest/python_imports.json \
  /mnt/user-data/outputs/dependency-traces/latest/dep_graph.json
```

## Fix Conversation (Subagent)-Optimized Workflow

### Pattern: Main Conversation + Fix Conversations (Subagents)

```bash
# Run wrapper (returns minimal context to main conversation)
bash scripts/trace_all.sh
```

**Main conversation receives (100 tokens):**
```json
{
  "total_valid": 161,
  "total_broken": 9,
  "workflow": "fix-conversation-subagent-optimized",
  "instructions": "Spawn one fix conversation (subagent) per broken reference"
}
```

**Fix conversation (subagent) workflow:**
```
For each broken reference:
  1. Main conversation: "Fix broken import X"
  2. Fix conversation (subagent) spawned with context:
     - ONE broken reference from output_file
     - Relevant file content
  3. Fix conversation (subagent) suggests fix
  4. Fix conversation (subagent) writes to traces/latest/fixes/fix_X.md
  5. Main conversation aggregates fixes
```

**Token efficiency:**
- Main context: 100 tokens
- Each fix conversation (subagent): 300 tokens (one reference + fix)
- Total for 10 broken refs: 100 + (10 × 300) = 3,100 tokens
- vs Traditional: 50,000+ tokens (full JSON in main context)

**Savings: 94%+ token reduction**

## ADW Framework Integration (Stub)

### Script: `adw_spawn_fix_agents.py`

**Status:** STUB - Repo Claude agent should implement

**Purpose:** Automate spawning fix conversations (subagents) via ADW framework

**TODO for repo Claude:**
1. Import `AgentPromptRequest` from `adws/adw_modules/agent.py`
2. Read trace results JSON
3. Spawn one fix conversation (subagent) per broken reference
4. Use `model="opus"` for complex fixes, `model="sonnet"` for simple ones
5. Write fixes to `traces/latest/fixes/`

**Usage (when implemented):**
```bash
python3 scripts/adw_spawn_fix_agents.py \
  scout_outputs/traces/latest/python_imports.json
```

**Expected behavior:**
```
Found 5 broken imports
Spawning fix conversation (subagent) 1/5: nonexistent_package
Spawning fix conversation (subagent) 2/5: deprecated_lib
...
Token efficiency with this pattern:
  - Main conversation: 100 tokens
  - 5 fix conversations (subagents): 5 × 300 = 1,500 tokens
  - Total: 1,600 tokens
  vs Traditional: 50,000+ tokens (97% savings)
```

**Integration pattern:**
```python
# Example implementation for repo Claude (in adw_spawn_fix_agents.py)
from adw_modules.agent import AgentPromptRequest, spawn_agent

for ref in broken_refs:
    request = AgentPromptRequest(
        prompt=build_fix_prompt(ref),
        model="opus" if is_complex_fix(ref) else "sonnet",
        context_files=[ref['file']],
        output_dir="scout_outputs/traces/latest/fixes/"
    )
    spawn_agent(request)
```

## Integration with IDEs

### IntelliJ IDEA (Catsy Team)

**Option 1: Terminal (immediate)**
```bash
# In IntelliJ terminal (⌥F12)
bash scripts/trace_python_imports.sh adws
cat scout_outputs/traces/latest/summary.md
```

**Option 2: External Tool (persistent)**
1. Settings → Tools → External Tools → Add
2. Name: "Trace Python Imports"
3. Program: `bash`
4. Arguments: `$ProjectFileDir$/scripts/trace_python_imports.sh adws`
5. Working directory: `$ProjectFileDir$`
6. Output: Check "Open console for tool output"

Bind to keyboard shortcut (e.g., `⌥⌘T`)

### VSCode

Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Trace Dependencies",
      "type": "shell",
      "command": "bash scripts/trace_python_imports.sh adws",
      "problemMatcher": [],
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

Run: `⌘⇧B` or `⌘⇧P` → "Run Task"

## CI/CD Integration

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws > result.json
broken=$(jq '.broken' result.json)

if [ "$broken" -gt 0 ]; then
  echo "❌ Found $broken broken imports. Review traces/latest/summary.md"
  exit 1
fi

echo "✅ All imports valid"
```

### GitHub Actions

```yaml
name: Validate Dependencies
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install tools
        run: brew install ripgrep ast-grep jq
      
      - name: Trace dependencies
        run: |
          CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws > result.json
          broken=$(jq '.broken' result.json)
          
          if [ "$broken" -gt 0 ]; then
            echo "::error::Found $broken broken imports"
            cat .dependency-traces/latest/summary.md
            exit 1
          fi
```

## Troubleshooting

**Issue: grep -oP not found (macOS)**
- Solution: Script auto-detects and uses ripgrep or sed fallback
- Verify: `which rg` should show `/opt/homebrew/bin/rg`

**Issue: jq not found**
```bash
brew install jq
```

**Issue: ast-grep not found**
```bash
brew install ast-grep
```

**Issue: Output goes to /tmp/ instead of expected location**
- Verify v2.1: `grep "version: 2.1" SKILL.md`
- Check environment: Script shows "Environment: local" or "claude_web"

**Issue: Context window still exploding**
- Always use `CONTEXT_MODE=minimal` or `CONTEXT_MODE=summary`
- Never `cat` full JSON files in main conversation
- Read summary.md or spawn fix conversations (subagents)

**Issue: scout_outputs/ not being used**
- Check if `scout_outputs/` exists: `ls -la scout_outputs/`
- If it doesn't exist, script uses `.dependency-traces/` (by design)
- To use scout_outputs/: create it first (`mkdir -p scout_outputs/`)

## Token Budget Comparison

| Approach | Main Context | Fix Conversations (Subagents) | Total | Notes |
|----------|--------------|-------------------------------|-------|-------|
| **MCP + Full JSON** | 10K + 50K | N/A | 60K | Tool schemas + full data dump |
| **This skill (full mode)** | 5K-50K | N/A | 5-50K | Still too much! |
| **This skill (summary mode)** | 500-2K | N/A | 0.5-2K | Better, but wasteful for many refs |
| **This skill (minimal mode)** | 100 | N/A | 100 | Counts only, spawn fix conversations (subagents) |
| **Fix conversation (subagent)-optimized** | 100 | N × 300 | 100 + N × 300 | **Optimal** |

**Example:** 10 broken refs
- Traditional: 60,000 tokens
- Fix conversation (subagent)-optimized: 3,100 tokens
- **Savings: 95%**

## Best Practices

1. **Always use minimal context mode for main conversation**
   ```bash
   CONTEXT_MODE=minimal bash scripts/trace_all.sh
   ```

2. **Read summary.md, not JSON files**
   ```bash
   cat scout_outputs/traces/latest/summary.md
   # or .dependency-traces/latest/summary.md
   # or /mnt/user-data/outputs/dependency-traces/latest/summary.md
   ```

3. **Spawn fix conversations (subagents) for fixes**
   - Main conversation: sees 100-token summary
   - Fix conversation (subagent) per broken ref: reads ONE entry, suggests fix
   - Aggregate fixes in main context

4. **Use timestamps for history**
   ```bash
   ls scout_outputs/traces/  # or .dependency-traces/
   # 2024-11-23_183045/
   # 2024-11-23_190122/
   # latest/ -> 2024-11-23_190122/
   ```

5. **Add to .gitignore if desired**
   ```
   # If using hidden fallback
   .dependency-traces/
   
   # If using scout_outputs (optional)
   scout_outputs/traces/*
   !scout_outputs/traces/.gitkeep
   ```

## What's Fixed in v2.1 (vs v2.0)

| Feature | v2.0 | v2.1 |
|---------|------|------|
| Environment detection | None | Auto-detects Claude Code vs Web |
| scout_outputs/ handling | Always use if exists | Use if exists, don't create |
| Fallback output | `.dependency-traces/` | `.dependency-traces/` (non-invasive) |
| Claude Web support | Partial | Full support (/mnt/user-data/outputs/) |
| Terminology | "subagent" | "fix conversation (subagent)" |
| ADW integration | None | Stub with clear TODOs |

## Next Steps

1. Install tools: `brew install ripgrep ast-grep jq`
2. Run trace: `CONTEXT_MODE=minimal bash scripts/trace_all.sh`
3. Read summary: `cat scout_outputs/traces/latest/summary.md` (or `.dependency-traces/latest/summary.md`)
4. Spawn fix conversations (subagents) for fixes (if broken refs found)
5. Apply fixes, re-validate
6. Add to CI/CD pipeline
7. (Optional) Implement ADW integration for automated fix conversation (subagent) spawning

## License

MIT License - See LICENSE.txt
