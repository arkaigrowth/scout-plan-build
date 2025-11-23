# Command Audit Analysis & Risk Classification

**Date**: 2025-11-22
**Audit Method**: 4 parallel agents testing in isolated git worktrees
**Test Task**: "Add debug logging to authentication module"

## Executive Summary

- **32 commands audited** across 4 categories
- **Critical finding**: Scout commands broken due to missing `Task` tool
- **Safety finding**: SuperClaude commands well-designed with appropriate risk gates
- **Recommendation**: Use native tools + implement risk-based auto-invoke rules

## Risk Classification Matrix

### 🟢 READ-ONLY (Safe for Auto-Invoke)

| Command | Purpose | Works? | Notes |
|---------|---------|--------|-------|
| Native Grep/Glob | File search | ✅ YES | Always available, fast |
| `/sc:analyze` | Code analysis | ✅ YES | Falls back gracefully if MCP missing |
| `/sc:explain` | Code explanation | ✅ YES | Pure prompt expansion |
| `/sc:design` | Architecture design | ✅ YES | Generates specs only |
| `/compare-worktrees` | Diff worktrees | ✅ YES | Shows comparisons |
| `/sc:brainstorm` | Requirements | ✅ YES | Interactive discovery |
| `/sc:estimate` | Effort estimation | ✅ YES | Analysis only |

### 🟡 MUTATE-LOCAL (Require User Approval)

| Command | Purpose | Works? | Risk Details |
|---------|---------|--------|--------------|
| `/plan_w_docs_improved` | Create spec | ✅ YES | Creates spec files |
| `/build_adw` | Build from spec | ✅ YES | Modifies code files |
| `/scout` variants | Find files | ❌ NO | Missing Task tool |
| `/sc:implement` | Feature implementation | ✅ YES | Creates/modifies files |
| `/sc:test` | Run tests | ✅ YES | Executes pytest |
| `/sc:document` | Generate docs | ✅ YES | Creates doc files |
| `/prepare-compaction` | Session prep | ✅ YES | Updates multiple files |
| `/init-parallel-worktrees` | Create worktrees | ✅ YES | Creates branches |
| `/sc:cleanup` | Code cleanup | ✅ YES | Deletes/modifies files |
| `/sc:improve` | Code improvements | ✅ YES | Refactors code |

### 🔴 MUTATE-EXTERNAL (Never Auto-Invoke)

| Command | Purpose | Works? | Risk Details |
|---------|---------|--------|--------------|
| `/scout_improved` | External AI scout | ⚠️ PARTIAL | Calls external APIs (gemini, codex) |
| `/sc:git` | Git operations | ✅ YES | Can push to remote |
| `/sc:spawn` | Create agents | ✅ YES | Spawns sub-agents |
| `/merge-worktree` | Merge branches | ✅ YES | Can merge to main |
| `/sc:build` | Build/deploy | ✅ YES | Runs arbitrary commands |

## Key Findings

### 1. Scout Commands Broken
**Root Cause**: All scout commands assume a `Task` tool that doesn't exist in standard Claude Code.
```python
# This fails in all scout commands:
Task(subagent_type="explore", prompt=prompt)
```
**Solution**: Use native tools or fix to use available Task tool from Claude Code.

### 2. SuperClaude Integration Safe
- No namespace conflicts with existing commands
- Appropriate risk separation (read vs write)
- Graceful MCP fallbacks
- **Recommendation**: Keep but add risk headers

### 3. Command Chaining Limited
- Slash commands CANNOT directly invoke other slash commands
- Chaining happens through:
  1. Output patterns (command suggests next step)
  2. Claude interpretation (reads output, runs next)
  3. Workflow hints in command text
- **Safe pattern**: READ → USER → MUTATE-LOCAL → USER → MUTATE-EXTERNAL

### 4. Working Pipeline Identified
```bash
# This pipeline WORKS:
Native tools (Grep/Glob) → /plan_w_docs_improved → /build_adw
```

## Recommendations

### Immediate Actions (Priority 1)
1. **Fix scout commands** to use available Task tool
2. **Add risk headers** to all slash commands:
   ```markdown
   <!-- risk: read-only|mutate-local|mutate-external -->
   <!-- auto-invoke: safe|gated|never -->
   ```
3. **Update CLAUDE.md** with working commands only

### Short-term (Priority 2)
1. **Create router command** that classifies task complexity
2. **Implement dry-run flags** for mutation commands
3. **Document command dependencies** clearly

### Long-term (Priority 3)
1. **Unify scout implementations** into one reliable command
2. **Add command composition** framework
3. **Create approval hooks** for mutation commands

## Command Consolidation Proposal

### Keep These (Working + Useful)
- `/plan_w_docs_improved` - Works perfectly
- `/build_adw` - Works with validation
- `/sc:analyze`, `/sc:explain`, `/sc:design` - Safe read-only
- `/sc:implement`, `/sc:test` - Powerful but gated
- Worktree commands - Excellent for parallel work

### Fix These (Broken but Valuable)
- `/scout_fixed` - Update to use correct Task tool
- `/scout_parallel` - Fix JSON bug in line 123

### Remove These (Redundant/Dangerous)
- `/scout` - Broken, redundant with scout_fixed
- `/scout_improved` - External tool dependencies

## Safe Command Patterns

### Pattern 1: Analysis → Plan → Build
```
/sc:analyze → /plan_w_docs_improved → /build_adw
```

### Pattern 2: Parallel Exploration
```
/init-parallel-worktrees → /run-parallel-agents → /compare-worktrees → /merge-worktree
```

### Pattern 3: Iterative Improvement
```
/sc:analyze → /sc:design → /sc:implement → /sc:test → /sc:improve
```

## Security Recommendations (Per Chad's Framework)

1. **Approval Gates**: All mutate commands need explicit user confirmation
2. **Scope Fences**: Commands must declare allowed paths/operations
3. **Output Schemas**: Stable, predictable output formats
4. **Blast Radius**: Limit scope of mutations to specific directories
5. **Audit Trail**: Log all command invocations with parameters

---

**Conclusion**: The framework has solid bones but needs the Task tool fixed and risk classifications added. The SuperClaude integration is safe and valuable. Native tools are the most reliable fallback.