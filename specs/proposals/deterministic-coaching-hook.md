# Proposal: Deterministic Coaching Hook

**Status**: Parked (awaiting decision)
**Priority**: Low
**Effort**: Small (1-2 hours)
**Created**: 2025-11-26

---

## Problem

Coach mode is defined in `CLAUDE.md` under "Output Style: Coach" - but this is prompt-based, meaning Claude decides whether to follow it.

**Current reliability**: ~60%
**Symptom**: Claude sometimes forgets to use journey framing, decision boxes, or progress updates.

## Proposed Solution

Add a `UserPromptSubmit` hook that injects a coaching reminder at the start of every interaction.

### Implementation

**File**: `.claude/settings.json` (or `.claude/settings.local.json` for local-only)

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo '🎯 COACH MODE: Use journey framing (┌─ boxes), decision points (🤔), progress updates (📊), completion summaries (✅).'"
          }
        ]
      }
    ]
  }
}
```

### Expected Improvement

| Approach | Reliability |
|----------|-------------|
| Prompt only (current) | ~60% |
| Prompt + Hook reminder | ~80% |

## Open Questions

1. **Always-on or toggleable?**
   - Could check for a `.coach-mode` file to conditionally enable
   - Or use environment variable `COACH_MODE=1`

2. **Reminder format?**
   - Single line (current proposal)
   - Full box template
   - Just emoji triggers

3. **Performance impact?**
   - Hook fires on every prompt
   - Echo is fast, should be negligible

## Alternatives Considered

| Alternative | Why Not |
|-------------|---------|
| Output post-processor | Complex, needs middleware layer |
| Template-based responses | Kills Claude's flexibility |
| More verbose CLAUDE.md | Already tried, still ~60% |

## Next Steps

- [ ] Decide if we want this feature
- [ ] Choose always-on vs toggleable
- [ ] Implement hook in settings.json
- [ ] Test reliability improvement over 10+ interactions
- [ ] Document in framework if successful

---

## References

- Research: Session 2025-11-26, "Deterministic Command Patterns" discussion
- Related: `ai_docs/reference/AGENTIC_ENGINEERING_PRIMITIVES_V2.md` Section 15
- Pattern: Same principle as Pattern C (Bash Wrapper) but for style, not actions
