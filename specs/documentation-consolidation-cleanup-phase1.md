# Plan: Documentation Consolidation and Cleanup - Phase 1

## Summary
Clean up and consolidate the documentation structure based on comprehensive audit findings from parallel subagent analysis. This plan addresses 131 markdown files across `docs/` and `ai_docs/`, removing redundancy, consolidating overlapping content, and reorganizing output directories for clarity.

## Problem Statement
The documentation has grown organically with:
- **8 redundant/obsolete files** that should be deleted
- **3 overlapping skills docs** that should be consolidated into 1
- **Disorganized scout_outputs/** with mixed concerns (reports + workflows + discovery)
- **Missing/outdated indexes** that don't reflect current structure
- **28 root-level files in ai_docs/** without proper organization

## Inputs
- **Audit Results**: Parallel subagent analysis of 131 markdown files
- **docs/ audit**: 44 files, 65/100 health score
- **ai_docs/ audit**: 87 files, 62% current
- **Output folder analysis**: 3 directories with overlapping concerns

## Architecture/Approach

### Design Principles
1. **Single Source of Truth**: Each concept documented once
2. **Clear Hierarchy**: Root indexes link to organized subdirectories
3. **Semantic Separation**:
   - `scout_outputs/` = operational workflow artifacts
   - `ai_docs/` = human-readable documentation
   - `docs/` = user guides and references

### Directory Structure After Cleanup

```
docs/                              # User-facing documentation
├── README.md                      # Updated index
├── SKILLS_ARCHITECTURE.md         # NEW: Consolidated from 3 files
├── guides/
│   ├── setup/
│   ├── usage/                     # NAVIGATION_GUIDE.md removed (duplicate)
│   └── deployment/
├── planning/
├── portability/                   # QUICK_REFERENCE.md removed (duplicate)
├── reference/
└── archive/                       # mvp_fixes/ contents archived here

ai_docs/                           # AI-generated documentation
├── ROOT_INDEX.md                  # NEW: Index for 28 root files
├── analyses/
├── architecture/
├── feedback/
├── reference/
├── research/
├── reviews/
└── sessions/

scout_outputs/                     # Workflow artifacts
├── README.md                      # NEW: Structure documentation
├── relevant_files.json            # Primary scout output
├── reports/                       # NEW: Moved from root
│   ├── architecture_report.json
│   ├── configuration_report.json
│   ├── implementation_report.json
│   ├── tests_report.json
│   └── phase1-state-management.json
├── workflows/                     # NEW: Renamed from ADW-XXX
│   └── ADW-PARALLEL001/
├── archive/
└── temp/
```

## Implementation Steps

### Step 1: Delete Redundant Files (8 files)
**Files to remove:**
```bash
# docs/ deletions (5 files)
rm docs/test.md
rm -rf docs/mvp_fixes/  # Contains 3 files: FIX_SCOUT_NOW.md, SIMPLE_FIX.md, WORKING_COMMANDS.md
rm docs/guides/usage/NAVIGATION_GUIDE.md
rm docs/portability/QUICK_REFERENCE.md

# ai_docs/ deletions (3 files)
rm ai_docs/PORTABILITY_ANALYSIS.md
rm ai_docs/CONFIGURATION_REPORT_SUMMARY.txt
rm ai_docs/ANALYSIS_INDEX.md.backup 2>/dev/null || true
```

**Validation**: Verify files existed and were removed

### Step 2: Consolidate Skills Documentation (3 → 1)
**Source files:**
- `docs/SKILLS_AND_MEMORY_ARCHITECTURE.md` (6,353 bytes)
- `docs/SKILLS_COMPOSITION_ARCHITECTURE.md` (47,188 bytes) - PRIMARY
- `docs/SKILLS_MEMORY_IMPLEMENTATION_GUIDE.md` (9,669 bytes)

**Target file:** `docs/SKILLS_ARCHITECTURE.md`

**Consolidation strategy:**
1. Use SKILLS_COMPOSITION_ARCHITECTURE.md as base (most comprehensive)
2. Extract unique content from SKILLS_AND_MEMORY_ARCHITECTURE.md
3. Merge implementation details from SKILLS_MEMORY_IMPLEMENTATION_GUIDE.md
4. Remove source files after consolidation

**Structure:**
```markdown
# Skills Architecture

## Overview (from SKILLS_AND_MEMORY)
## Composition Patterns (from SKILLS_COMPOSITION)
## Memory Integration (from SKILLS_MEMORY)
## Implementation Guide (from SKILLS_MEMORY_IMPLEMENTATION)
```

### Step 3: Reorganize scout_outputs/
**Actions:**
```bash
# Create new subdirectories
mkdir -p scout_outputs/reports
mkdir -p scout_outputs/workflows

# Move report files
mv scout_outputs/architecture_report.json scout_outputs/reports/
mv scout_outputs/configuration_report.json scout_outputs/reports/
mv scout_outputs/implementation_report.json scout_outputs/reports/
mv scout_outputs/tests_report.json scout_outputs/reports/
mv scout_outputs/phase1-state-management.json scout_outputs/reports/

# Move workflow directories
mv scout_outputs/ADW-PARALLEL001 scout_outputs/workflows/
```

**Create README:**
```markdown
# scout_outputs/

Workflow artifacts and scout phase outputs.

## Structure
- `relevant_files.json` - Primary scout discovery output
- `reports/` - Analysis and execution reports
- `workflows/` - Per-workflow execution state (ADW-XXX directories)
- `archive/` - Historical backups
- `temp/` - Temporary working files

## Audience
- **AI consumers**: Plan/build phases read these as inputs
- **Human consumers**: Developers review for context and debugging
```

### Step 4: Update Indexes

#### 4a. Update docs/README.md
Remove references to deleted files:
- Remove mvp_fixes/ section
- Remove duplicate NAVIGATION_GUIDE reference
- Add SKILLS_ARCHITECTURE.md reference (replacing 3 files)

#### 4b. Create ai_docs/ROOT_INDEX.md
Index the 28 root-level files by category:
```markdown
# ai_docs Index

## Analysis & Reports
- ADW_ANALYSIS_INDEX.md
- ADW_QUICK_REFERENCE.md
- ADW_SYSTEM_ANALYSIS.md
...

## Configuration
- CONFIGURATION_ANALYSIS_INDEX.md
- CONFIGURATION_QUICK_REFERENCE.md
- CONFIGURATION_SETUP_PATTERNS.md

## Portability
- PORTABILITY_INDEX.md
- PORTABILITY_SUMMARY.md
- QUICK_PORT_GUIDE.md
...
```

#### 4c. Update DIRECTORY_STRUCTURE.md
Reflect new scout_outputs/ structure with reports/ and workflows/ subdirectories.

### Step 5: Verify No Broken Links
Check for references to deleted files:
```bash
grep -r "mvp_fixes" docs/ ai_docs/ --include="*.md"
grep -r "NAVIGATION_GUIDE" docs/ ai_docs/ --include="*.md"
grep -r "QUICK_REFERENCE.md" docs/ ai_docs/ --include="*.md"
grep -r "SKILLS_AND_MEMORY" docs/ ai_docs/ --include="*.md"
grep -r "SKILLS_COMPOSITION" docs/ ai_docs/ --include="*.md"
grep -r "SKILLS_MEMORY_IMPLEMENTATION" docs/ ai_docs/ --include="*.md"
```

Update any broken references found.

## Testing Strategy

### Validation Checklist
- [ ] All 8 target files deleted
- [ ] 3 skills docs consolidated to 1
- [ ] scout_outputs/reports/ contains 5 JSON files
- [ ] scout_outputs/workflows/ contains ADW-PARALLEL001/
- [ ] scout_outputs/README.md exists
- [ ] ai_docs/ROOT_INDEX.md exists
- [ ] No grep matches for deleted file references
- [ ] Git status shows expected changes

### Smoke Test
```bash
# Verify structure
find docs/ -name "*.md" | wc -l  # Should be ~39 (was 44)
find ai_docs/ -name "*.md" | wc -l  # Should be ~85 (was 87, +1 new index)
ls scout_outputs/reports/*.json | wc -l  # Should be 5
```

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Broken links to deleted files | Medium | Low | Grep scan and fix |
| Lost content in consolidation | Low | Medium | Keep originals until verified |
| Git conflicts | Low | Low | Working on feature branch |

### Rollback Plan
```bash
git checkout -- docs/ ai_docs/ scout_outputs/
```

## Success Criteria
- [ ] **8 redundant files deleted** (5 docs/, 3 ai_docs/)
- [ ] **3 skills docs consolidated to 1** (net -2 files)
- [ ] **scout_outputs/ reorganized** with reports/ and workflows/ subdirs
- [ ] **Indexes updated** (docs/README.md, ai_docs/ROOT_INDEX.md)
- [ ] **DIRECTORY_STRUCTURE.md updated** to match reality
- [ ] **No broken links** confirmed via grep
- [ ] **All changes committed** with descriptive message

## Estimated Effort
- Step 1 (Delete): 5 minutes
- Step 2 (Consolidate): 15 minutes
- Step 3 (Reorganize): 5 minutes
- Step 4 (Indexes): 20 minutes
- Step 5 (Verify): 10 minutes
- **Total: ~55 minutes**

---
*Plan created: 2024-11-23*
*Audit source: Parallel subagent analysis*
