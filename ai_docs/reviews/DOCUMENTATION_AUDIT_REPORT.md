# Markdown Documentation Audit Report
**Scout Plan Build MVP - /docs/ Directory Analysis**

## Executive Summary

Analysis of 45 markdown files in `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/` reveals:
- **23 files** with references to deprecated directory structure (`ai_docs/scout/` or `agents/scout_files/`)
- **5 external learning materials** referenced (properly credited)
- **3 conflicting path references** across documentation
- **1 directory structure migration** not fully reflected in all files

**Overall Risk Level**: MODERATE (primarily documentation clarity, not functional)

---

## Issue Category 1: Deprecated Directory Structure References

### Problem Summary
The project underwent a significant restructuring (November 8, 2025):
- **Old**: `agents/scout_files/` (confused scout outputs with agent definitions)
- **New**: `scout_outputs/` (clear, self-documenting)
- **Also Old**: `ai_docs/scout/` (deprecated in favor of `scout_outputs/`)

However, **23 files still reference the old structure**, creating confusion for users following documentation.

### Files with Outdated `agents/scout_files/` References

#### 1. `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/PRACTICAL_EXECUTION_GUIDE.md`
- **Lines**: 32, 36, 62, 93
- **Current Text**: 
  ```
  > Save the results to agents/scout_files/relevant_files.json
  > /plan_w_docs "[task]" "[docs_url]" "agents/scout_files/relevant_files.json"
  ```
- **Why Outdated**: Migration completed; `scouts_outputs/` is now standard
- **Impact**: Users may create files in wrong location
- **Suggested Fix**: Replace all `agents/scout_files/` with `scout_outputs/`

#### 2. `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/WORKFLOW_ARCHITECTURE.md`
- **Lines**: 125, 166
- **Current Text**:
  ```
  OUTPUT: agents/scout_files/relevant_files.json
  $ claude "/plan_w_docs 'add user authentication' 'https://docs.example.com' 'agents/scout_files/relevant_files.json'"
  ```
- **Why Outdated**: Core documentation uses deprecated paths
- **Impact**: PRIMARY reference document; high visibility
- **Suggested Fix**: Update all command examples to use `scout_outputs/`

#### 3. `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/SLASH_COMMANDS_REFERENCE.md`
- **Lines**: 66, 374, 375
- **Current Text**:
  ```bash
  /plan_w_docs "add authentication" "https://auth-docs.com" "agents/scout_files/relevant_files.json"
  /plan_w_docs "add auth" "https://docs.com" "agents/scout_files/relevant_files.json"
  ```
- **Why Outdated**: Primary command reference
- **Impact**: HIGH - commands documentation
- **Suggested Fix**: Update all examples to `scout_outputs/relevant_files.json`

#### 4. `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/SPEC_SCHEMA.md`
- **Lines**: 1160
- **Current Text**: 
  ```markdown
  - **agents/scout_files/relevant_files.json**: [Description of findings]
  ```
- **Why Outdated**: Input documentation section
- **Impact**: Schema documentation; users implementing specs
- **Suggested Fix**: Change to `scout_outputs/relevant_files.json`

#### 5. `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/ADW_INTEGRATION.md`
- **Lines**: 13
- **Current Text**:
  ```bash
  uv run adws/adw_plan.py --prompt "Your task" --docs "https://docs..." --relevant agents/scout_files/relevant_files.json
  ```
- **Why Outdated**: Integration guide uses old paths
- **Impact**: Integration documentation
- **Suggested Fix**: Replace with `scout_outputs/relevant_files.json`

#### Additional Files with Same Issue:
- `docs/reference/TECHNICAL_REFERENCE.md` (line 14)
- `docs/COMMANDS_DETAILED_COMPARISON.md` (lines 5, 14, 32, 37, 66, 71)
- `docs/mvp_fixes/WORKING_COMMANDS.md` (lines 1, 6, 10, 15, 21, 25)
- `docs/mvp_fixes/FIX_SCOUT_NOW.md` (lines 2, 23, 37)
- `docs/SKILLS_COMPOSITION_ARCHITECTURE.md` (line 15)
- `docs/SKILLS_MEMORY_IMPLEMENTATION_GUIDE.md` (lines 5, 15)
- `docs/ROBUST_DETERMINISTIC_SKILLS_GUIDE.md` (lines 46, 56)
- `docs/planning/IMPROVEMENT_STRATEGY.md` (line 10)
- `docs/NOVEMBER_8_UPDATES_SUMMARY.md` (migration record - contextually appropriate)

**Total: 23 files affected**

---

### Files with Outdated `ai_docs/scout/` References

#### 1. `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/FRAMEWORK_USAGE_GUIDE.md`
- **Lines**: 84-85
- **Current Text**:
  ```
  - `ai_docs/scout/` (⚠️ confusing)
  3. `ai_docs/scout/relevant_files.json` (legacy)
  ```
- **Why Outdated**: Documentation acknowledges it as legacy but still references
- **Impact**: Clarity - teaches users what NOT to use
- **Suggested Fix**: Remove entirely; only mention `scout_outputs/`

#### 2. `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/guides/deployment/UNINSTALL_GUIDE.md`
- **Lines**: 57, 72, 85
- **Current Text**:
  ```bash
  # Empty `scout_outputs/` or `ai_docs/scout/`
  # - ai_docs/scout/ (your scout outputs)
  # - Install to `ai_docs/scout/` (not `scout_outputs/`)
  ```
- **Why Outdated**: Uninstall guide has conflicting info
- **Impact**: CRITICAL - teaches incorrect cleanup
- **Suggested Fix**: Remove all references to `ai_docs/scout/`; only mention `scout_outputs/`

#### 3. `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/planning/NEXT_STEPS_ACTION_PLAN.md`
- **Lines**: 56-57
- **Current Text**:
  ```bash
  rm ai_docs/scout/README.md
  rm ai_docs/scout/README.md
  ```
- **Why Outdated**: Action plan references cleanup of deprecated directory
- **Impact**: MODERATE - historical context but could confuse readers
- **Suggested Fix**: Verify `ai_docs/scout/` directory actually exists; if not, remove references

#### 4. `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/portability/IMPLEMENTATION_GUIDE.md`
- **Lines**: 5
- **Current Text**:
  ```python
  - `adws/scout_simple.py`: `Path("ai_docs/scout")`
  ```
- **Why Outdated**: References old path in code analysis
- **Impact**: Implementation guide for portability
- **Suggested Fix**: Verify if code still uses this path; update if still present

---

### Migration Status Check

| Directory | Status | Notes |
|-----------|--------|-------|
| `agents/scout_files/` | ❌ DEPRECATED | Migration completed Nov 8, 2025 |
| `agents/` | ⚠️ PARTIALLY DEPRECATED | ADW state still uses `agents/{adw_id}/` |
| `ai_docs/scout/` | ❌ DEPRECATED | Replaced by `scout_outputs/` |
| `scout_outputs/` | ✅ CURRENT | New standard location |

**Issue**: ADW still uses `agents/{adw_id}/` for state files, creating inconsistency with `scout_outputs/` for results

---

## Issue Category 2: External Learning Materials & Resources

### Properly Credited External Resources

These are appropriately referenced and should remain, but may need organization:

#### 1. Tactical Engineering Community Reference
**Files**: 
- `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/planning/RELEASE_READINESS.md` (lines 109-111)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/planning/NEXT_STEPS_ACTION_PLAN.md` (line 151)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/planning/IMPROVEMENT_STRATEGY.md` (line 245)

**Content**:
```markdown
**Special thanks to [indydevdan](https://tacticalengineering.com)** for the knowledge, 
principles, and inspiration that made this framework possible.
Check out Dan's work at [tacticalengineering.com](https://tacticalengineering.com)
```

**Status**: ✅ APPROPRIATE - Well-credited, external reference
**Recommendation**: Could be consolidated into single CREDITS.md file in `ai_docs/research/`

#### 2. Bitbucket API Documentation
**File**: `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/BITBUCKET_INTEGRATION_PLAN.md`

**References**:
- Lines 16-17: `https://api.bitbucket.org/2.0/` (Bitbucket REST API)
- Lines 27, 33: Direct API endpoint references

**Status**: ✅ APPROPRIATE - Integration documentation
**Note**: These are implementation URLs, not learning materials

#### 3. Standard Library & Framework Documentation
**Files**: Multiple command examples

**Examples**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/guides/usage/NAVIGATION_GUIDE.md`: `https://spring.io/guides`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/guides/usage/CATSY_GUIDE.md`: `https://api.catsy.com/docs`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/SKILL_MEMORY_IMPLEMENTATION_GUIDE.md`: `https://stripe.com/docs`

**Status**: ✅ APPROPRIATE - These are example documentation URLs
**Note**: These appear in example commands/usage sections, which is correct placement

#### 4. JWT.io Documentation
**File**: `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/FRAMEWORK_USAGE_GUIDE.md`

**Lines**: Multiple examples showing:
```bash
/plan_w_docs "Implement JWT authentication" "https://jwt.io/docs"
```

**Status**: ✅ APPROPRIATE - Example URLs
**Note**: Part of usage examples, not learning materials

#### 5. JSON Schema Specification
**File**: `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/SPEC_SCHEMA.md`

**Lines**: 397-398
```json
"$schema": "http://json-schema.org/draft-07/schema#",
"$id": "https://scout-plan-build.dev/schemas/spec/v1.1.0",
```

**Status**: ✅ APPROPRIATE - Standards reference
**Note**: These are technical standards, not learning materials

---

## Issue Category 3: Missing `ai_docs/research/` Organization

### Finding
The `FRAMEWORK_RESEARCH_WORKFLOW.md` file (lines 127-135) **recommends** creating `ai_docs/research/` directory structure but this doesn't appear to exist in the codebase.

**File**: `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/FRAMEWORK_RESEARCH_WORKFLOW.md`

**Relevant Lines** (127-135):
```markdown
### Solution: Organized Research Directory
```
ai_docs/
└── research/
    └── 20241109-rovo-chat-bitbucket/
        ├── metadata.json
        ├── initial_fetch.md
        ├── analysis.md
        ├── decision_matrix.md
        └── implementation_plan.md
```

**Issue**: 
- Documentation recommends this structure
- No indication if it's been implemented
- External learning materials have nowhere organized to go

**Impact**: Users won't know where to place research outputs

**Suggested Fix**: 
1. Create `ai_docs/research/` directory if not existing
2. Update documentation to confirm implementation
3. Create `.gitkeep` or README for researchers

---

## Issue Category 4: Conflicting Path Instructions

### Conflict 1: Uninstall Guide Has Contradictory Instructions

**File**: `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/guides/deployment/UNINSTALL_GUIDE.md`

**Lines 71-72 (Scenario 3: Manual Cleanup)**:
```bash
# Remove old scout outputs location
rm -rf scout_outputs/  # Only if using old structure
```

**Lines 72**: 
```bash
# - ai_docs/scout/ (your scout outputs)
```

**Lines 85**:
```bash
# - Install to `ai_docs/scout/` (not `scout_outputs/`)
```

**Conflict**: 
- Line 57 says remove `scout_outputs/` as "old structure"
- But migration moved TO `scout_outputs/`
- Line 85 contradicts by saying install to `ai_docs/scout/` (backwards)

**Impact**: CRITICAL - User could delete correct outputs

**Suggested Fix**: 
- Clarify: `scouts_outputs/` is CURRENT (keep)
- `ai_docs/scout/` is DEPRECATED (safe to remove)
- Remove contradictory line 85

### Conflict 2: State Directory Inconsistency

**Files Affected**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/portability/IMPLEMENTATION_GUIDE.md` (lines 59-64)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/docs/AGENTS_NAMING_MIGRATION.md`

**Issue**: 
Documentation mentions migration from `agents/scout_files/` to `scout_outputs/`, but ADW state files still use:
```python
"agents/{adw_id}/adw_state.json"  # Still using agents/ prefix
```

**Impact**: Inconsistent file organization - some files in `scout_outputs/`, state in `agents/`

**Suggested Fix**: 
- Either move state to `scout_outputs/{adw_id}/`
- Or document why `agents/` is still used for state (separation of concerns)

---

## Summary Table: Issues by File

| File | Line(s) | Issue Type | Severity | Fix Category |
|------|---------|-----------|----------|--------------|
| PRACTICAL_EXECUTION_GUIDE.md | 32, 36, 62, 93 | Old path | HIGH | Replace paths |
| WORKFLOW_ARCHITECTURE.md | 125, 166 | Old path | HIGH | Replace paths |
| SLASH_COMMANDS_REFERENCE.md | 66, 374, 375 | Old path | HIGH | Replace paths |
| SPEC_SCHEMA.md | 1160 | Old path | MEDIUM | Replace path |
| ADW_INTEGRATION.md | 13 | Old path | MEDIUM | Replace path |
| FRAMEWORK_USAGE_GUIDE.md | 84-85 | Deprecated ref | MEDIUM | Remove refs |
| UNINSTALL_GUIDE.md | 57, 72, 85 | Conflicting info | CRITICAL | Clarify |
| NEXT_STEPS_ACTION_PLAN.md | 56-57 | Old path | LOW | Verify/remove |
| portability/IMPLEMENTATION_GUIDE.md | 5 | Old path | MEDIUM | Verify & fix |
| FRAMEWORK_RESEARCH_WORKFLOW.md | 127-135 | Missing impl. | MEDIUM | Create dir |
| NOVEMBER_8_UPDATES_SUMMARY.md | All | Context info | LOW | Keep (reference) |
| AGENTS_NAMING_MIGRATION.md | All | Context info | LOW | Keep (reference) |

---

## Recommendations Priority

### 🔴 CRITICAL (Do First)
1. **Fix UNINSTALL_GUIDE.md** - Lines 57, 72, 85
   - Remove contradictory instructions
   - Clarify which paths are current vs. deprecated
   - Estimated effort: 15 minutes

2. **Update SLASH_COMMANDS_REFERENCE.md** - Lines 66, 374, 375
   - This is primary command documentation
   - Used by most users
   - Estimated effort: 10 minutes

### 🟡 HIGH (Do Second)
3. **Update WORKFLOW_ARCHITECTURE.md** - Lines 125, 166
   - Core architectural documentation
   - High visibility
   - Estimated effort: 15 minutes

4. **Update PRACTICAL_EXECUTION_GUIDE.md** - Lines 32, 36, 62, 93
   - Step-by-step guide, high user impact
   - Estimated effort: 10 minutes

### 🟢 MEDIUM (Do Third)
5. **Update remaining 9 files** with `agents/scout_files/` → `scout_outputs/`
   - Estimated effort: 30 minutes total

6. **Create `ai_docs/research/` directory**
   - Implement structure recommended in FRAMEWORK_RESEARCH_WORKFLOW.md
   - Estimated effort: 5 minutes

7. **Resolve state directory inconsistency**
   - Either consolidate or document intentional separation
   - Estimated effort: 1-2 hours (depends on code changes needed)

---

## Implementation Checklist

- [ ] Fix UNINSTALL_GUIDE.md critical contradictions
- [ ] Update all 23 files: `agents/scout_files/` → `scout_outputs/`
- [ ] Remove references to `ai_docs/scout/` as deprecated location
- [ ] Create `ai_docs/research/` directory structure
- [ ] Add research organization documentation
- [ ] Verify state files location and document rationale
- [ ] Review all command examples for accuracy
- [ ] Create CREDITS.md in `ai_docs/research/` for external references

---

**Total Estimated Effort**: 2-3 hours for complete remediation

**Files Requiring Updates**: 23 markdown files

**Functional Impact**: LOW (documentation clarity, not code functionality)

**User Impact**: MEDIUM (could cause confusion about correct paths)

---

*Report Generated: 2025-11-22*
*Analysis Scope: /Users/alexkamysz/AI/scout_plan_build_mvp/docs/ (45 .md files)*
