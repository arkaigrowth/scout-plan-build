# Skill Specifications Alignment Review

## Executive Summary

**Status:** ⚠️ **MISALIGNED** - Specs are solving the wrong problems in the wrong order

The 5 skill specs are well-written but miss the **foundational problem**: Scout is non-deterministic and broken. This creates a critical gap in the implementation strategy.

---

## Critical Finding: Scout Determinism Gap 🚨

### The Problem

**Current specs assume Scout works reliably.** It doesn't:

1. **Non-deterministic**: Glob/grep results come in random order
   - Same task run twice = different file discovery order
   - This cascades to Plan phase getting different context
   - Build phase produces different results

2. **Broken**: External tools don't exist
   - `gemini`, `opencode`, `codex` commands don't exist
   - Scout commands fail or fall back to degraded mode
   - No 4-level fallback strategy documented

3. **Not Addressed in Specs**:
   - No skill-000 for Scout determinism
   - Implementation plan says "4 broken scout commands (CRITICAL)" but ignores them
   - Workflow orchestration skills depend on Scout working well

### Impact

Building skills on top of non-deterministic Scout is like building on sand:
- Tests pass once, fail next time (flaky)
- Workflows unreproducible
- Hard to debug "why did it work yesterday?"
- Memory/learning system useless if inputs vary

---

## Phase Ordering is Backwards

### What Specs Propose

```
Week 1:  workflow-orchestrator, validating-inputs, managing-state
Week 2:  adw-orchestrating (consolidate 6 scripts)
Week 3:  Error handling, integration testing
```

### What Should Happen (Recommended Order)

```
Phase 1 (2 weeks):  🚨 Scout Determinism [MISSING - CREATE THIS FIRST]
├─ Fix Scout to sort results alphabetically
├─ Implement 4-level fallback strategy
├─ Add determinism testing
└─ Make Scout reproducible

Phase 2 (2 weeks):  Foundation Skills
├─ skill-002: validating-inputs ✅ (ready)
├─ skill-003: managing-state ✅ (ready)
└─ skill-005: handling-errors ✅ (ready)

Phase 3 (2 weeks):  Orchestration Skills
├─ skill-004: adw-orchestrating ✅ (ready, but depends on Phase 1)
└─ skill-001: workflow-orchestrator ⚠️ (generic, can wait)

Phase 4 (1 week):   Testing & Validation
├─ Determinism tests for ALL skills
├─ Brittleness tests (intentional failures)
└─ Integration tests (Scout → Plan → Build)
```

---

## Spec-by-Spec Alignment Assessment

### ✅ EXCELLENT: skill-002 (validating-inputs)

**Alignment**: 95% - Ready to implement
**Status**: No changes needed
**Why**: Already addressing critical security gap, perfect first-week skill

**Metrics**:
- Security coverage: 100%
- False positive rate: <1%
- Aligns with Phase 2 exactly

---

### ✅ EXCELLENT: skill-003 (managing-state)

**Alignment**: 95% - Ready to implement
**Status**: No changes needed
**Why**: Multi-backend support, atomic operations, exactly what workflows need

**Metrics**:
- Code reduction: 650 lines
- Recovery success: 99%+
- Essential for Phase 2

---

### ✅ GOOD: skill-005 (handling-errors)

**Alignment**: 85% - Minor improvements needed
**Status**: Good addition, order it earlier
**Issues**:
- Learning system underspecified
- No examples of learned patterns
- Recovery success rates assumed, not proven

**Improvement**: Add section showing "How learning evolves recovery rates" with concrete examples

---

### ⚠️ MISALIGNED: skill-004 (adw-orchestrating)

**Alignment**: 70% - Depends on Scout being fixed first
**Status**: Hold until Phase 3
**Issues**:
1. Assumes Scout is reliable → it's not
2. Tries to consolidate 6 scripts with broken foundation
3. Should wait until Scout determinism is solved

**Improvement**: Add prerequisite section:
```yaml
prerequisites:
  - scout-determinism (must fix first)
  - validating-inputs (input safety)
  - managing-state (workflow state)
```

---

### ❌ WRONG PRIORITY: skill-001 (workflow-orchestrator)

**Alignment**: 60% - Generic, non-urgent, low leverage
**Status**: Defer to Phase 3 or later
**Issues**:
1. Generic patterns that scripts don't yet use
2. Low immediate impact (why consolidate 6 different scripts if they're being replaced?)
3. Distracts from higher-leverage work
4. Depends on Scout being reliable

**Recommendation**: Move to Phase 3, after Scout is fixed and other skills deployed

---

## Missing: skill-000 (Scout Determinism) 🚨

**Priority**: CRITICAL (Phase 1)
**Effort**: 2 weeks
**Impact**: Unblocks all other skills

**What it must address:**
1. Sort all file discovery results (alphabetically, consistently)
2. Implement 4-level fallback when tools fail:
   - Level 1: Full intelligent scout with memory
   - Level 2: Basic scout with native tools (Glob, Grep)
   - Level 3: Minimal file listing only
   - Level 4: Valid empty structure (no files found)
3. Seed all randomness for reproducibility
4. Add determinism tests (run 10x, verify identical output)
5. Document that it's the foundation for everything else

---

## Testing Strategy Gap

### What's Missing

**Determinism tests** - Critical for "production-ready MVP"

```python
def test_scout_determinism():
    """Same input must produce same output"""
    results_1 = scout("task description")
    results_2 = scout("task description")
    assert results_1 == results_2  # Not just "similar", exactly equal
```

### All Skills Need

1. **Determinism test**: Run 10x, verify identical output
2. **Brittleness test**: Intentionally break dependencies, verify graceful degradation
3. **Integration test**: Full chain (Scout → Plan → Build) with failures at each stage

**Recommendation**: Add "Testing Strategy" section to all specs requiring:
- Determinism: ✅ Same input → exact same output
- Brittleness: ✅ Broken deps → graceful fallback
- Performance: ✅ Before/after benchmarks

---

## Production Readiness Assessment

### File Size Violations

3 specs exceed the 500-line SKILL.md recommended limit:

| Spec | Lines | Issue |
|------|-------|-------|
| skill-001 | 601 | Workflow orchestrator too detailed |
| skill-004 | 602 | ADW orchestrator has duplicate examples |
| skill-005 | 623 | Error handler overly comprehensive |

**Fix**: Use "Progressive Disclosure" more aggressively:
- Main SKILL.md: <400 lines with overview
- Details in `references/` subdirectory
- Examples in `references/examples.md`

### Determinism Not Emphasized

**Current approach**: Assume determinism works

**Needed**: Make determinism a first-class concern:
- Document sorting/seeding strategy
- Include determinism tests
- Explain fallback levels
- Prove reproducibility

---

## Recommended Revised Implementation Plan

### Week 1: Scout Foundation (🚨 NEW - CRITICAL)

**skill-000: Scout Determinism**
- Sort all file discovery (glob/grep results alphabetically)
- Implement 4-level fallback strategy
- Add determinism testing framework
- Prerequisite for all other skills

**Hours**: 40 hours (2 weeks)

### Week 2-3: Foundation Skills

**skill-002: Validating Inputs** ✅ (no changes)
**skill-003: Managing State** ✅ (no changes)
**skill-005: Handling Errors** ⚠️ (add learning examples)

**Hours**: 40 hours (2 weeks)

### Week 4-5: Orchestration Skills

**skill-004: ADW Orchestrating** ⚠️ (update prerequisites)
- Add "Requires scout-determinism" to prerequisites
- Update Phase 2 section to reference Scout fixes
- Add section proving Scout reliability before this skill

**skill-001: Workflow Orchestrator** ➡️ (defer or reduce scope)
- Option A: Defer to Phase 6 (optional polish)
- Option B: Reduce scope to 1 generic example only

**Hours**: 40 hours (2 weeks)

### Week 6: Testing & Validation

**All Skills**:
- Determinism testing (run 10x, verify identical)
- Brittleness testing (break deps, test fallbacks)
- Integration testing (full Scout → Plan → Build)
- Performance benchmarking

**Hours**: 20 hours (1 week)

**Total Timeline**: 8 weeks (vs 6 weeks in original plan)

---

## Action Items

### IMMEDIATE (This Week)

- [ ] Create **skill-000-scout-determinism.md** spec
  - Address sorting, seeding, fallback levels
  - Define determinism testing framework
  - Explain how it unblocks other skills

- [ ] Update **skill-004-adw-orchestrating.md**
  - Add prerequisites section
  - Change Phase 2 to Phase 3
  - Add dependency note: "Requires scout-determinism"

- [ ] Update **SKILLS_IMPLEMENTATION_PLAN.md**
  - Reorder phases to match recommendation
  - Add skill-000 as Phase 1 (critical)
  - Show how each skill builds on previous

### WEEK 1

- [ ] Reduce file sizes for specs >500 lines
  - Move details to `references/` subdirectory
  - Tighten main SKILL.md content
  - Use progressive disclosure more

- [ ] Add determinism testing to ALL specs
  - Every spec needs "same input → same output" test
  - Every spec needs fallback/brittleness test
  - Document success criteria

### WEEK 2+

- [ ] Implement skills in new order
- [ ] Validate determinism at each phase
- [ ] Test integration between phases

---

## Summary: What to Change

| Spec | Change | Why | Effort |
|------|--------|-----|--------|
| (none) | **CREATE skill-000** | Scout determinism is foundation | 2 weeks |
| skill-001 | Defer to Phase 3 or later | Low priority, can wait | N/A |
| skill-002 | ✅ Keep as-is | Excellent, ready to implement | None |
| skill-003 | ✅ Keep as-is | Excellent, ready to implement | None |
| skill-004 | Add prerequisites section | Depends on Scout being fixed | 2 hours |
| skill-005 | Add learning examples | Underspecified learning system | 4 hours |
| Plan | Reorder phases | Implement in right order | 1 hour |

---

## Key Insights

`★ Insight ─────────────────────────────────────`
**The specs are well-written but fix the wrong problem first.** It's like optimizing a car's aerodynamics when the engine doesn't work. Scout determinism is the engine—fix that first, everything else becomes reliable. Once Scout produces consistent results, the orchestration skills can confidently build sophisticated workflows on top.
`─────────────────────────────────────────────────`

**Bottom Line**:
- Specs 2, 3, 5: Ready to implement ✅
- Spec 4: Defer until Scout is fixed ⚠️
- Spec 1: Nice-to-have, defer to Phase 3 ➡️
- **Missing**: Scout determinism skill (CRITICAL) 🚨

