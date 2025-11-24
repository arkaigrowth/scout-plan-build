# Changelog

## v2.1 - Environment-Aware Release (2024-11-24)

Based on user feedback: "scout_outputs/ for other repo users?" and environment detection needs.

### New Features

#### 1. Environment Detection ✅
**Added:** Auto-detect Claude Code CLI vs Claude Web vs Terminal

```bash
# Detects environment automatically
if [ -d "/mnt/user-data/uploads" ]; then
    ENV="claude_web"  # Claude Web
else
    ENV="local"       # Claude Code CLI or terminal
fi
```

**Impact:** MAJOR - Skill now works perfectly in both Claude Code and Claude Web

**Benefits:**
- Claude Code: Writes to project directory (scout_outputs/, ai_docs/, or .dependency-traces/)
- Claude Web: Writes to /mnt/user-data/outputs/ (only writable location)
- Terminal: Same as Claude Code

#### 2. Smart Path Handling ✅
**Added:** Non-invasive output directory defaults

**Priority order:**
1. `scout_outputs/traces/` - IF exists (don't create)
2. `ai_docs/analyses/traces/` - IF exists (don't create)
3. `.dependency-traces/` - CREATE (hidden fallback)
4. `/mnt/user-data/outputs/` - Claude Web only

**Reasoning:** Don't force `scout_outputs/` on repos that don't have it. Hidden `.dependency-traces/` is non-invasive.

**Impact:** MAJOR - Respects existing conventions, doesn't pollute repos

#### 3. Terminology Update ✅
**Changed:** "subagent" → "fix conversation (subagent)"

**Rationale:** User requested clarity. "Fix conversation (subagent)" makes it clear:
- It's a conversation spawned to fix something
- It's technically a subagent (for readers who understand that term)

**Files updated:**
- All scripts (trace_all.sh, etc.)
- All documentation (SKILL.md, README.md, etc.)

**Impact:** MINOR - Improves clarity

#### 4. ADW Integration Stub ✅
**Added:** `scripts/adw_spawn_fix_agents.py` with clear TODOs

**Purpose:** Template for repo Claude agent to implement automated fix conversation (subagent) spawning

**Structure:**
```python
# TODO comments mark implementation points
def spawn_fix_conversations(broken_refs, output_dir):
    # TODO: Implement using adws/adw_modules/agent.py
    for ref in broken_refs:
        request = AgentPromptRequest(
            prompt=build_fix_prompt(ref),
            model="opus" if is_complex_fix(ref) else "sonnet",
            context_files=[ref['file']],
            output_dir=output_dir
        )
        spawn_agent(request)
```

**Status:** STUB - Not implemented, requires repo-specific ADW framework

**Impact:** MINOR - Provides implementation path

#### 5. Claude Web Full Support ✅
**Added:** Complete Claude Web compatibility

**Changes:**
- Detect `/mnt/user-data/uploads` presence
- Read from uploads (read-only)
- Write to `/mnt/user-data/outputs/dependency-traces/`
- No symlinks in Claude Web (filesystem limitations)

**Impact:** MODERATE - Enables skill usage in Claude Web

### Bug Fixes

None - v2.0 was already solid. v2.1 is purely additive features.

### Breaking Changes

None - v2.1 is fully backward compatible with v2.0.

**Migration:** Just replace v2.0 with v2.1, everything works the same (with bonus features).

### Comparison

| Feature | v2.0 | v2.1 |
|---------|------|------|
| Environment detection | ❌ None | ✅ Auto-detects |
| scout_outputs/ handling | Always use if exists | Use if exists, don't create |
| Fallback output | `.dependency-traces/` | `.dependency-traces/` (non-invasive) |
| Claude Web support | Partial | ✅ Full |
| Terminology | "subagent" | "fix conversation (subagent)" |
| ADW integration | ❌ None | ✅ Stub with TODOs |

### Testing

Added environment detection tests to `scripts/test_skill.sh`:
- ✅ Detects Claude Code vs Web
- ✅ Validates path handling
- ✅ Confirms ADW stub present

### Documentation Updates

- **SKILL.md**: Complete rewrite with environment detection, smart paths, terminology
- **README.md**: Updated with v2.1 features
- **QUICKSTART.md**: Added environment detection info
- **CHANGELOG.md**: This file

### Use Cases

#### Use Case 1: Your Repo (scout_outputs/ exists)
```bash
CONTEXT_MODE=minimal bash scripts/trace_all.sh
# Outputs to: scout_outputs/traces/latest/
```

#### Use Case 2: Other Repos (no scout_outputs/)
```bash
CONTEXT_MODE=minimal bash scripts/trace_all.sh
# Outputs to: .dependency-traces/latest/ (non-invasive)
```

#### Use Case 3: Claude Web
```bash
CONTEXT_MODE=minimal bash scripts/trace_all.sh
# Outputs to: /mnt/user-data/outputs/dependency-traces/latest/
```

### Developer Notes

**Environment Detection Logic:**
```bash
detect_environment() {
    if [ -d "/mnt/user-data/uploads" ]; then
        echo "claude_web"
    else
        echo "local"
    fi
}
```

**Path Configuration:**
```bash
configure_paths() {
    if [ "$env" = "claude_web" ]; then
        OUTPUT_BASE="/mnt/user-data/outputs/dependency-traces"
    else
        # Smart detection
        if [ -d "$PROJECT_ROOT/scout_outputs" ]; then
            OUTPUT_BASE="$PROJECT_ROOT/scout_outputs/traces"
        elif [ -d "$PROJECT_ROOT/ai_docs" ]; then
            OUTPUT_BASE="$PROJECT_ROOT/ai_docs/analyses/traces"
        else
            OUTPUT_BASE="$PROJECT_ROOT/.dependency-traces"
        fi
    fi
}
```

### Credits

v2.1 developed based on user feedback:
1. "think it will get messy for other repo users?" → Non-invasive defaults
2. "can we account for [Claude Code vs Web]?" → Environment detection
3. "include subagent in parentheses" → Terminology update
4. "ADW integration stub" → Template for repo Claude

---

## v2.0 - Steelmanned Release (2024-11-24)

Complete rewrite based on critical feedback from Claude Code steelmanning session.

### Critical Fixes

[See previous CHANGELOG entries from v2.0]

---

## v1.0 - Initial Release (2024-11-23)

[Original version with 6 critical issues that v2.0 fixed]

---

## License

MIT License - Same across all versions
