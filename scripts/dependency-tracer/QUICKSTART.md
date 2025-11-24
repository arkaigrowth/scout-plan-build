# Dependency Tracer v2.1 - Quick Start

## 1-Minute Install

```bash
# Install tools
bash scripts/setup.sh

# Test it works
bash scripts/test_skill.sh
```

## 3-Minute First Run

```bash
# Trace dependencies (minimal context - 100 tokens)
CONTEXT_MODE=minimal bash scripts/trace_all.sh

# Read results
cat scout_outputs/traces/latest/summary.md
# or .dependency-traces/latest/summary.md
# or /mnt/user-data/outputs/dependency-traces/latest/summary.md (Claude Web)
```

## Context Modes (Critical!)

```bash
# ✅ RECOMMENDED: Minimal (100 tokens)
CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws

# 🟡 MODERATE: Summary (500-2K tokens)
CONTEXT_MODE=summary bash scripts/trace_python_imports.sh adws

# ❌ AVOID: Full (5-50K tokens) - use only in fix conversations (subagents)!
CONTEXT_MODE=full bash scripts/trace_python_imports.sh adws
```

## Fix Conversation (Subagent) Pattern

**Main Conversation:**
```bash
CONTEXT_MODE=minimal bash scripts/trace_all.sh
```

Receives: `{total: 128, broken: 9, message: "Read summary_file"}`

**Spawn Fix Conversations (Subagents):**
```
For each broken ref:
  - Read ONE entry from output_file
  - Suggest fix
  - Write to traces/latest/fixes/
```

**Token usage:** 100 + (9 × 300) = **2,800 tokens** (vs 50K+)

## Environment Detection

v2.1 auto-detects where you're running:

**Claude Code CLI or Terminal:**
- Outputs to: `scout_outputs/traces/` (if exists), `ai_docs/analyses/traces/` (if exists), or `.dependency-traces/` (fallback)

**Claude Web:**
- Outputs to: `/mnt/user-data/outputs/dependency-traces/`

## Output Structure

```
scout_outputs/traces/       # or .dependency-traces/ or /mnt/user-data/outputs/
├── latest/                # ← Read this
│   ├── summary.md         # ← Start here
│   ├── command_refs.json  # Don't load in conversation!
│   └── python_imports.json # Don't load in conversation!
└── 2024-11-23_183045/     # Timestamped history
```

## Key Rules

1. ✅ Always use `CONTEXT_MODE=minimal`
2. ✅ Read `summary.md`, NOT JSON files
3. ✅ Spawn fix conversations (subagents) for fixes
4. ❌ Never `cat` full JSON in main conversation

## IDE Integration

**IntelliJ (⌥F12):**
```bash
CONTEXT_MODE=minimal bash scripts/trace_all.sh
cat scout_outputs/traces/latest/summary.md
```

**VSCode:**
Add task, bind to `⌘⇧B`

## What Changed from v2.0?

- ✅ Environment detection (Claude Code vs Web)
- ✅ Non-invasive defaults (doesn't force scout_outputs/ on other repos)
- ✅ Updated terminology ("fix conversation (subagent)")
- ✅ ADW integration stub
- ✅ Full Claude Web support

## Next Steps

1. Run minimal trace
2. Read summary.md
3. Spawn fix conversations (subagents) for fixes (if needed)
4. Add to CI/CD

Done. 🚀
