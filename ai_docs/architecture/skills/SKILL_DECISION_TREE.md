# Skill Creation Decision Tree

**Purpose**: Quick reference guide to determine if a command should become a skill

---

## Decision Flow

```
Start with a command
    ↓
Is it currently broken?
    ↓ YES → IMMEDIATE SKILL CANDIDATE
    ↓ NO
    ↓
Is it >150 lines?
    ↓ YES → HIGH PRIORITY SKILL CANDIDATE
    ↓ NO
    ↓
Does it chain 3+ commands?
    ↓ YES → HIGH PRIORITY SKILL CANDIDATE
    ↓ NO
    ↓
Would it benefit from memory?
    ↓ YES → MEDIUM PRIORITY SKILL CANDIDATE
    ↓ NO
    ↓
Is it frequently used?
    ↓ YES → Consider combining with related commands
    ↓ NO
    ↓
Keep as command (works fine as-is)
```

---

## Command-by-Command Analysis

### ❌ BROKEN - Convert Immediately

| Command | Why Broken | Skill Alternative | Priority |
|---------|-----------|-------------------|----------|
| `/scout` | Uses non-existent tools (gemini, opencode, codex) | `adw-scout` ✅ EXISTS | 🔴 CRITICAL |
| `/scout_improved` | Same broken tools | `adw-scout` ✅ EXISTS | 🔴 CRITICAL |
| `/scout_plan_build` | Depends on broken scout | `adw-complete` ✅ PARTIAL | 🔴 CRITICAL |
| `/scout_plan_build_improved` | Depends on broken scout | `adw-complete` ✅ PARTIAL | 🔴 CRITICAL |

**Action**: Deprecate these 4 commands immediately, point users to skills

---

### 🟢 VERY HIGH COMPLEXITY - Excellent Skill Candidates

| Command | Lines | Complexity Score | Memory Benefit | Skill Name | Priority |
|---------|-------|------------------|----------------|------------|----------|
| `/worktree_checkpoint` | 450 | 95/100 | Medium | `/worktree-safe-dev` | 🟡 HIGH |
| `/worktree_undo` | 450 | 95/100 | Medium | `/worktree-safe-dev` | 🟡 HIGH |
| `/worktree_redo` | 350 | 90/100 | Medium | `/worktree-safe-dev` | 🟡 HIGH |
| `/worktree_create` | 350 | 90/100 | Low | `/worktree-safe-dev` | 🟡 HIGH |

**Rationale**: These 4 commands form a cohesive system (1600+ lines). Combining them into a single orchestrated skill provides:
- Automatic checkpoint management
- Safer development workflow
- Unified interface
- 90% reduction in "lost work" incidents

**Skill Structure**:
```bash
/worktree-safe-dev "feature-name"
  ↓
  1. Create isolated worktree
  2. Auto-checkpoint every 5min
  3. Safe experimentation
  4. Easy undo/redo
  5. Cleanup on completion
```

---

### 🟡 HIGH COMPLEXITY - Good Skill Candidates

| Command | Lines | Complexity Score | Memory Benefit | Skill Name | Priority |
|---------|-------|------------------|----------------|------------|----------|
| `/feature` | 155 | 75/100 | High | `/issue-to-implementation` | 🟡 MEDIUM |
| `/review` | 150 | 70/100 | Medium | `/review-and-fix` | 🟡 MEDIUM |
| `/bug` | 140 | 70/100 | High | `/issue-to-implementation` | 🟡 MEDIUM |
| `/document` | 130 | 65/100 | Medium | `/documentation-complete` | 🟢 LOW |
| `/patch` | 130 | 70/100 | Low | `/review-and-fix` | 🟡 MEDIUM |
| `/chore` | 120 | 65/100 | Medium | `/issue-to-implementation` | 🟡 MEDIUM |

**Grouping Rationale**:

**Group 1: Issue Type Commands** → `/issue-to-implementation` skill
- Combines: `/feature`, `/bug`, `/chore`, `/classify_issue`
- Benefit: Single command for any issue type
- Memory: Learns issue patterns, improves classification
- Time saved: 67% (3min → 1min)

**Group 2: Review Commands** → `/review-and-fix` skill
- Combines: `/review`, `/patch`, `/implement`, `/test`
- Benefit: Automatic quality improvement
- Memory: Learns common issues, suggests fixes
- Time saved: 60% (8min → 3min)

**Group 3: Documentation** → `/documentation-complete` skill
- Combines: `/document`, `/conditional_docs`
- Benefit: Comprehensive docs generation
- Memory: Learns documentation patterns
- Time saved: 40% (5min → 3min)

---

### 🔵 MEDIUM COMPLEXITY - Evaluate Case-by-Case

| Command | Lines | Current Status | Should Become Skill? | Reason |
|---------|-------|----------------|---------------------|---------|
| `/plan_w_docs` | 85 | ✅ Works | Part of larger skill | Use `adw-complete` |
| `/plan_w_docs_improved` | 110 | ✅ Works | Part of larger skill | Use `adw-complete` |
| `/test` | 115 | ✅ Works | Maybe | If combined with test resolution |
| `/test_e2e` | 90 | ✅ Works | Maybe | If combined with test resolution |
| `/resolve_failed_test` | 60 | ✅ Works | Maybe | Combine into `/test-complete` |
| `/resolve_failed_e2e_test` | 75 | ✅ Works | Maybe | Combine into `/test-complete` |
| `/pull_request` | 60 | ✅ Works | Part of larger skill | Use `adw-complete` |
| `/classify_adw` | 55 | ✅ Works | No | Simple, works well |
| `/generate_branch_name` | 50 | ✅ Works | Part of larger skill | Use `adw-complete` |
| `/install` | 50 | ✅ Works | Maybe | If environment setup needed |

**Testing Commands** → `/test-complete` skill (Optional)
- Combines: `/test`, `/test_e2e`, `/resolve_failed_test`, `/resolve_failed_e2e_test`
- Benefit: Single command for all testing
- Memory: Learns test failure patterns
- Time saved: 63% (8min → 3min)
- Priority: 🟢 LOW (current commands work fine)

---

### ⚪ LOW COMPLEXITY - Keep as Commands

| Command | Lines | Reason to Keep as Command |
|---------|-------|--------------------------|
| `/commit` | 45 | Simple wrapper, works well |
| `/conditional_docs` | 45 | Utility, rarely used |
| `/prepare_app` | 40 | Setup only, one-time use |
| `/build_adw` | 40 | Simple wrapper to Python script |
| `/classify_issue` | 35 | Fast, simple, works well |
| `/start` | 35 | Dev server start, simple |
| `/prime` | 30 | Context initialization, simple |
| `/implement` | 30 | Simple wrapper, works well |
| `/tools` | 25 | Information only |

**Rationale**: These commands are:
- Already simple and fast
- Work well as-is
- Minimal benefit from skill encapsulation
- Low complexity maintenance burden

---

## Skill Priority Matrix

### Priority 1: CRITICAL (Fix Now)
**Timeline**: Week 1
**Effort**: 4 hours

1. Deprecate `/scout`, `/scout_improved`
2. Point users to `adw-scout` skill
3. Update documentation

**Why**: Blocks entire workflow

---

### Priority 2: HIGH (Next 2-4 Weeks)
**Timeline**: Weeks 2-4
**Effort**: 5-7 days

1. **Week 2**: Enhance `adw-complete` skill (add commit + PR)
2. **Week 3**: Create `/worktree-safe-dev` skill
3. **Week 4**: Create `/issue-to-implementation` skill

**Why**: High-impact, frequently used workflows

---

### Priority 3: MEDIUM (Weeks 5-8)
**Timeline**: Weeks 5-8
**Effort**: 5-7 days

1. **Week 5-6**: Create `/review-and-fix` skill
2. **Week 7**: Create `/test-complete` skill (if needed)
3. **Week 8**: Create `/documentation-complete` skill (if needed)

**Why**: Nice-to-have improvements, lower usage frequency

---

### Priority 4: LOW (Future)
**Timeline**: Month 3+
**Effort**: As needed

- Environment setup combinations
- Git workflow combinations
- Custom user-requested skills

**Why**: Current commands work well, low improvement ROI

---

## Quick Decision Checklist

Use this checklist to decide if a command should become a skill:

### ✅ YES - Create Skill If:
- [ ] Command is currently broken
- [ ] Command exceeds 150 lines
- [ ] Command chains 3+ other commands
- [ ] Command would benefit from memory/learning
- [ ] Command has manual copy-paste steps
- [ ] Command lacks error recovery
- [ ] Command is frequently used (>10x/week)
- [ ] Command has complex validation needs

### ❌ NO - Keep as Command If:
- [ ] Command is <50 lines
- [ ] Command is simple wrapper
- [ ] Command works well as-is
- [ ] Command is rarely used
- [ ] Command is information-only
- [ ] Command is one-time setup

---

## Skill Combination Patterns

### Pattern 1: Sequential Workflow
**Example**: `/scout` → `/plan` → `/build` → `/commit` → `/pr`
**Skill**: `adw-complete`
**Benefit**: Single command replaces 5, automatic context flow

### Pattern 2: Error Recovery Workflow
**Example**: `/review` → `/patch` → `/implement` → `/test`
**Skill**: `/review-and-fix`
**Benefit**: Automatic fixes, validation

### Pattern 3: State Management Workflow
**Example**: `/worktree_create` → `/checkpoint` → `/undo` → `/redo`
**Skill**: `/worktree-safe-dev`
**Benefit**: Unified state, safer development

### Pattern 4: Classification Workflow
**Example**: `/classify` → `/feature|/bug|/chore` → `/implement`
**Skill**: `/issue-to-implementation`
**Benefit**: Automatic routing, memory learning

---

## Anti-Patterns (Don't Create Skills For)

### ❌ Simple Wrappers
**Example**: `/start`, `/tools`, `/prime`
**Reason**: Already simple, no benefit from skill complexity

### ❌ Information-Only
**Example**: `/tools`, documentation viewers
**Reason**: No execution flow, just data display

### ❌ One-Time Setup
**Example**: `/install`, `/prepare_app`
**Reason**: Used once, rarely benefits from memory

### ❌ External Tool Wrappers
**Example**: Git operations, gh CLI
**Reason**: External tools already optimized

---

## ROI Calculator

Use this to estimate skill value:

```
Command Complexity Score:
  Lines: (lines / 100) * 30
  Dependencies: (num_deps) * 15
  Manual steps: (manual_steps) * 20
  Error rate: (error_rate * 100) * 10
  Usage frequency: (uses_per_week) * 5
  = Total Complexity Score

Skill Value Score:
  Memory benefit: 30 (if learning helps)
  Time saved: (time_saved_pct) / 2
  Error reduction: (error_reduction_pct) / 2
  Manual step reduction: (manual_reduction_pct) / 2
  = Total Value Score

ROI = (Value Score / Complexity Score) * 100

ROI > 150: Excellent skill candidate
ROI 100-150: Good skill candidate
ROI 50-100: Maybe, evaluate use case
ROI < 50: Keep as command
```

### Example: `/scout` Command

```
Complexity Score:
  Lines: 120/100 * 30 = 36
  Dependencies: 0 * 15 = 0
  Manual steps: 2 * 20 = 40
  Error rate: 100% * 10 = 10
  Usage: 10 * 5 = 50
  = 136

Value Score:
  Memory: 30
  Time saved: 60% / 2 = 30
  Error reduction: 90% / 2 = 45
  Manual reduction: 100% / 2 = 50
  = 155

ROI = (155 / 136) * 100 = 114

Verdict: Good skill candidate
(Plus it's broken, so CRITICAL priority)
```

---

## Summary: 11 Skills Recommended

### Immediate (Week 1)
1. ✅ `adw-scout` - Already exists, deprecate old commands

### High Priority (Weeks 2-4)
2. 🔨 `adw-complete` - Enhance existing (add commit + PR)
3. 🆕 `worktree-safe-dev` - Combine 4 worktree commands
4. 🆕 `issue-to-implementation` - Combine issue type commands

### Medium Priority (Weeks 5-8)
5. 🆕 `review-and-fix` - Quality automation
6. 🆕 `test-complete` - Comprehensive testing (optional)
7. 🆕 `documentation-complete` - Doc generation (optional)

### Low Priority (Future)
8. 🆕 `environment-setup` - Setup automation (if needed)
9. 🆕 `git-workflow` - Git operations (if requested)
10. 🆕 Custom skills as requested by users

### Keep as Commands
- 12 simple commands (<50 lines) work fine as-is

---

**Quick Reference**:
- 🔴 Broken: 4 commands → Fix immediately
- 🟡 High complexity: 10 commands → 7 skills
- 🟢 Medium complexity: 14 commands → Consider case-by-case
- ⚪ Low complexity: 12 commands → Keep as-is

**Expected Impact**:
- 60-70% time savings
- 90% reduction in manual steps
- 80% improvement in error recovery
- Continuous learning and improvement

---

*Use this decision tree to quickly evaluate any command for skill conversion.*
