# Example Outputs

This directory shows what different context modes return.

## minimal_output.json (100 tokens)

**Use when:** You just need counts. Spawn subagents for details.

```json
{
  "total": 128,
  "broken": 5,
  "message": "Found 5 broken imports. Read summary_file."
}
```

**Token count:** ~100 tokens

**When to use:**
- Main agent initial triage
- Quick validation checks
- CI/CD pass/fail determination
- Before spawning subagents

## summary_output.json (500-2000 tokens)

**Use when:** You need to see which imports are broken for triage.

Shows:
- Stats (total, valid, broken, local, installed)
- List of broken imports with file + line numbers
- List of broken modules (unique)
- File paths for full details

**Token count:** ~500-2000 tokens (depends on # of broken refs)

**When to use:**
- Manual triage/prioritization
- Deciding which subagents to spawn
- Generating fix plan
- Summary reports

## full_output.json (5000-50000 tokens)

**NOT included** - this would dump ALL imports (valid + broken) into context.

**Avoid in main context!** Only use:
- In isolated subagent context
- For single-file analysis
- When absolutely necessary

## Subagent Pattern

**Main Agent (minimal mode):**
```bash
CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws
```

Output: `{total: 128, broken: 5, message: "Read summary_file"}`

**Spawn Fix Subagents:**
```
For each broken import:
  1. Main agent: "Fix broken import X in file Y"
  2. Subagent context:
     - ONE broken import entry from output_file
     - Relevant file content (lines around the import)
     - ~300 tokens total
  3. Subagent suggests fix
  4. Subagent writes to scout_outputs/traces/latest/fixes/fix_X.md
```

**Token efficiency:**
- Main: 100 tokens
- 5 subagents: 5 × 300 = 1,500 tokens
- **Total: 1,600 tokens** (vs 50K+ for full dump)

## Token Comparison

| Mode | Tokens | Use Case |
|------|--------|----------|
| minimal | 100 | Main agent triage |
| summary | 500-2K | Manual review |
| full | 5-50K | Avoid! Subagents only |
| **Subagent pattern** | **100 + N×300** | **Optimal** |

## Best Practice

```bash
# 1. Main agent uses minimal
CONTEXT_MODE=minimal bash scripts/trace_python_imports.sh adws

# 2. Main agent reads summary.md (not JSON!)
cat scout_outputs/traces/latest/summary.md

# 3. Main agent spawns subagents
# Each subagent:
#   - Reads ONE entry from full JSON
#   - Context: 300 tokens
#   - Suggests fix
#   - Writes to fixes/

# Total: 100 + (5 × 300) = 1,600 tokens ✅
# vs 50,000+ tokens for full dump ❌
```
