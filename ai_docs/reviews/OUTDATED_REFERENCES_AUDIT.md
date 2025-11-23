# Root-Level Markdown Files - Outdated References Audit Report

**Date**: 2025-11-22
**Scope**: Root-level .md files in `/Users/alexkamysz/AI/scout_plan_build_mvp`
**Analysis Focus**: External resource references, deprecated directory structures, outdated paths

---

## Executive Summary

**4 files require updates** for:
- **Deprecated path references** to `ai_docs/scout/` (removed in v2024.11.20, should use `scout_outputs/`)
- **Incorrect documentation links** pointing to non-existent files
- **Conflicting guidance** between old and new directory structures

**Status**: 
- CLAUDE.md: ✅ Clean
- DIRECTORY_STRUCTURE.md: ✅ Clean
- INSTALLATION_GUIDE.md: ⚠️ **3 issues found**
- README.md: ⚠️ **2 issues found**

---

## File-by-File Analysis

### 1. CLAUDE.md
**File Path**: `/Users/alexkamysz/AI/scout_plan_build_mvp/CLAUDE.md`
**Status**: ✅ CLEAN

**Assessment**: This file correctly uses `scout_outputs/` paths throughout and does not reference the deprecated `ai_docs/scout/` directory.

**Examples of correct usage**:
- Line 38: `"scout_outputs/relevant_files.json"` ✅
- Line 116: `"scout_outputs/"` ✅  
- Line 209: `"scout_outputs/relevant_files.json"` ✅

**Conclusion**: No changes needed.

---

### 2. DIRECTORY_STRUCTURE.md
**File Path**: `/Users/alexkamysz/AI/scout_plan_build_mvp/DIRECTORY_STRUCTURE.md`
**Status**: ✅ CLEAN

**Assessment**: This file is the definitive reference for the corrected directory structure. It explicitly documents deprecated locations and current canonical paths.

**Key sections correctly handled**:
- Lines 132-141: "DEPRECATED Locations" section clearly marks `ai_docs/scout/` as removed ✅
- Line 135: Notes removal date: "REMOVED in v2024.11.20" ✅
- Lines 319-320: Validation rules exclude `ai_docs/scout/` ✅
- Lines 336-337: Best practices warn against using deprecated paths ✅
- Lines 358-370: Migration guide provided ✅

**Conclusion**: No changes needed. This is the source of truth.

---

### 3. INSTALLATION_GUIDE.md
**File Path**: `/Users/alexkamysz/AI/scout_plan_build_mvp/INSTALLATION_GUIDE.md`
**Status**: ⚠️ **NEEDS UPDATES - 3 ISSUES FOUND**

#### Issue 3.1: Incorrect output path in scout documentation
**Line**: 184
**Current Text**:
```
📁 Saved to: ai_docs/scout/relevant_files.json
```
**Problem**: 
- References deprecated `ai_docs/scout/` path
- Should be `scout_outputs/relevant_files.json` per DIRECTORY_STRUCTURE.md v2024.11.20

**Suggested Fix**:
```
📁 Saved to: scout_outputs/relevant_files.json
```

---

#### Issue 3.2: Incorrect path in first test workflow
**Line**: 303
**Current Text**:
```bash
cat ai_docs/scout/relevant_files.json
```
**Problem**: 
- Shows deprecated path to users
- Should be `scout_outputs/relevant_files.json`
- This is in "First Workflow After Installation" section where users will actually test

**Suggested Fix**:
```bash
cat scout_outputs/relevant_files.json
```

---

#### Issue 3.3: Incorrect path in second test workflow
**Line**: 313
**Current Text**:
```bash
python adws/adw_plan.py \
  "Test framework installation" \
  "https://docs.python.org" \
  "ai_docs/scout/relevant_files.json"
```
**Problem**: 
- References deprecated `ai_docs/scout/` in actual workflow example
- Users will copy this exact command and it may fail if scout outputs go to `scout_outputs/`

**Suggested Fix**:
```bash
python adws/adw_plan.py \
  "Test framework installation" \
  "https://docs.python.org" \
  "scout_outputs/relevant_files.json"
```

---

#### Issue 3.4 (Bonus): Troubleshooting reference
**Line**: 453
**Current Text**:
```
| Can't find output | Check `scout_outputs/` and `ai_docs/scout/` |
```
**Problem**: 
- Lists both locations, suggesting both are valid
- Should only mention `scout_outputs/` as canonical location
- Removes confusion from users

**Suggested Fix**:
```
| Can't find output | Check `scout_outputs/relevant_files.json` |
```

---

### 4. README.md
**File Path**: `/Users/alexkamysz/AI/scout_plan_build_mvp/README.md`
**Status**: ⚠️ **NEEDS UPDATES - 2 ISSUES FOUND**

#### Issue 4.1: Deprecated path in quick workflow example
**Line**: 42
**Current Text**:
```bash
/plan_w_docs "Add OAuth2 support" "" "ai_docs/scout/relevant_files.json"
```
**Problem**: 
- This is the first code example users see after reading "Quick Workflow"
- Uses deprecated `ai_docs/scout/` path
- DIRECTORY_STRUCTURE.md removes this path in v2024.11.20
- Users will be confused if their scout outputs go to `scout_outputs/`

**Context**: Section "🎯 Quick Workflow (After Installation)"

**Suggested Fix**:
```bash
/plan_w_docs "Add OAuth2 support" "" "scout_outputs/relevant_files.json"
```

---

#### Issue 4.2: Outdated directory structure visualization
**Line**: 73-74
**Current Text**:
```
├── ai_docs/
│   ├── scout/         # Scout outputs
│   └── build_reports/ # Build reports
```
**Problem**: 
- Shows `ai_docs/scout/` as valid location for scout outputs
- Contradicts DIRECTORY_STRUCTURE.md which moved this to `scout_outputs/`
- Creates directory structure confusion

**Full context** (lines 70-77):
```
your-repo/
├── adws/              # Core workflow modules
├── ai_docs/
│   ├── scout/         # Scout outputs
│   └── build_reports/ # Build reports
├── specs/             # Generated specifications
├── .claude/commands/  # Workflow commands
└── scripts/           # Validation tools
```

**Suggested Fix**:
```
your-repo/
├── adws/                  # Core workflow modules
├── scout_outputs/         # Scout results (canonical)
│   └── relevant_files.json
├── specs/                 # Generated specifications
├── ai_docs/               # AI-generated documentation
│   └── build_reports/     # Build reports
├── .claude/commands/      # Workflow commands
└── scripts/               # Validation tools
```

---

### 5. CLAUDE_v4.md
**File Path**: `/Users/alexkamysz/AI/scout_plan_build_mvp/CLAUDE_v4.md`
**Status**: ⚠️ **MINOR ISSUE**

**Line**: 85
**Current Text**:
```
ai_docs/scout/              # Secondary scout location (confusing!)
```

**Note**: This file is labeled as v4 (newer version) and acknowledges the confusion about scout location. However, it still lists it as a valid location. This is a superseded file but should be updated for consistency.

**Suggested Fix**: Remove this line or mark as deprecated:
```
scout_outputs/               # Primary scout location (canonical)
ai_docs/scout/              # DEPRECATED - use scout_outputs/ instead
```

---

## External Resources Analysis

**Finding**: No external resource references requiring migration to `ai_docs/research/`

The files analyzed contain only:
- GitHub URLs (example: `https://github.com/owner/repo`)
- Documentation URLs (example: `https://docs.python.org` - placeholder)
- Standard CLI references

**None of the root-level files reference**:
- Video tutorials
- Blog articles
- Academic papers
- Learning resources
- External research materials

**Recommendation**: The `ai_docs/research/` directory can be used for documenting:
- Framework design decisions and research
- Architecture evaluation articles
- Security decision logs
- But this is future usage, not for these files

---

## Summary Table

| File | Line(s) | Issue Type | Severity | Fix Required |
|------|---------|-----------|----------|------------|
| CLAUDE.md | — | None | — | ✅ No |
| DIRECTORY_STRUCTURE.md | — | None | — | ✅ No |
| INSTALLATION_GUIDE.md | 184 | Deprecated path | High | Update to `scout_outputs/` |
| INSTALLATION_GUIDE.md | 303 | Deprecated path | High | Update to `scout_outputs/` |
| INSTALLATION_GUIDE.md | 313 | Deprecated path | High | Update to `scout_outputs/` |
| INSTALLATION_GUIDE.md | 453 | Deprecated path | Medium | Update guidance |
| README.md | 42 | Deprecated path | High | Update to `scout_outputs/` |
| README.md | 73-74 | Wrong structure | High | Update directory tree |
| CLAUDE_v4.md | 85 | Outdated reference | Low | Mark as deprecated |

---

## Migration Checklist

### Priority 1 (User-Facing Examples)
- [ ] Update README.md line 42: Scout path in quick workflow
- [ ] Update README.md lines 73-74: Directory structure visualization
- [ ] Update INSTALLATION_GUIDE.md line 313: Scout path in test workflow

### Priority 2 (Installation Guidance)
- [ ] Update INSTALLATION_GUIDE.md line 184: Output path documentation
- [ ] Update INSTALLATION_GUIDE.md line 303: Test command with correct path
- [ ] Update INSTALLATION_GUIDE.md line 453: Troubleshooting guidance

### Priority 3 (Consistency)
- [ ] Update CLAUDE_v4.md line 85: Mark scout location as deprecated (or remove file)

---

## Notes

1. **DIRECTORY_STRUCTURE.md is the source of truth** for directory locations (v2024.11.20)
2. **No external resource migration needed** - root files contain no external article/video/research links
3. **All deprecated paths trace back to v2024.11.20 reorganization** (agents/ → scout_outputs/, ai_docs/scout/ → scout_outputs/)
4. **These are all user-facing issues** - users following examples will use deprecated paths
5. **CLAUDE.md is already updated correctly** - use it as a reference for correct paths

---

**Report Generated**: 2025-11-22
**Files Scanned**: 9 root-level markdown files
**Issues Found**: 8 (3 critical, 4 high, 1 low)
**Files Requiring Changes**: 3 (README.md, INSTALLATION_GUIDE.md, CLAUDE_v4.md)

