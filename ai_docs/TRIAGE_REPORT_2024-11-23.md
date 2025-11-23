# ai_docs/ Root File Triage Report

**Date**: 2024-11-23
**Files Analyzed**: 28
**Method**: 4 parallel subagents

## Summary

| Action | Count | Files |
|--------|-------|-------|
| KEEP | 3 | README.md, ROOT_INDEX.md, ANALYSIS_INDEX.md |
| MOVE | 12 | Various → analyses/, reference/, research/ |
| ARCHIVE | 6 | Historical/client-specific analyses |
| CONSOLIDATE | 5 | Portability (3→1), Config (2→1) |
| DELETE | 1 | anthropic_quick_start.md (redundant) |
| CONVERT_TO_SPEC | 1 | TODO_DOCUMENTATION_IMPROVEMENTS.md |

---

## Detailed Recommendations

### KEEP (Stay in ai_docs/ root)

| File | Reason |
|------|--------|
| README.md | Directory structure definition |
| ROOT_INDEX.md | Navigation index for root files |
| ANALYSIS_INDEX.md | Master navigation for all analyses |

### MOVE to ai_docs/analyses/

| File | Notes |
|------|-------|
| ADW_ANALYSIS_INDEX.md | Part of ADW analysis suite |
| ADW_QUICK_REFERENCE.md | Part of ADW analysis suite |
| ADW_SYSTEM_ANALYSIS.md | Part of ADW analysis suite |
| COMMAND_SKILL_ANALYSIS_REPORT.md | Historical but valuable |
| ENGINEERING_ASSESSMENT.md | Historical assessment |
| FRAMEWORK_DOGFOODING_LEARNINGS.md | Case study |
| FRAMEWORK_IN_ACTION_BITBUCKET.md | Case study |

### MOVE to ai_docs/reference/

| File | Notes |
|------|-------|
| claude_code_cli_reference.md | External SDK docs |
| claude_code_sdk.md | External SDK docs |
| e2b.md | External integration docs |
| CONFIGURATION_QUICK_REFERENCE.md | Active reference |
| REPOSITORY_REFERENCE.md | System architecture |

### MOVE to ai_docs/architecture/skills/

| File | Notes |
|------|-------|
| SKILL_DECISION_TREE.md | Skills development reference |

### MOVE to ai_docs/research/articles/

| File | Notes |
|------|-------|
| openai_quick_start.md | External API reference |

### ARCHIVE (ai_docs/archive/)

| File | Reason |
|------|--------|
| AGENT_CLEANUP_ANALYSIS.md | One-time cleanup, executed |
| CATSY_CONTEXT_GAPS_ANALYSIS.md | Client-specific, historical |
| ROOT_MD_FILES_CLEANUP_ANALYSIS.md | One-time cleanup, executed |
| SKILL_OPPORTUNITIES_SUMMARY.md | Superseded by development |
| SKILLS_STRATEGIC_ALIGNMENT_REPORT.md | Point-in-time assessment |

### CONSOLIDATE

| Files | Into | Notes |
|-------|------|-------|
| PORTABILITY_INDEX.md, PORTABILITY_SUMMARY.md, QUICK_PORT_GUIDE.md | ai_docs/reference/PORTABILITY_GUIDE.md | Significant overlap |
| CONFIGURATION_ANALYSIS_INDEX.md | CONFIGURATION_QUICK_REFERENCE.md | Index is redundant |

### DELETE

| File | Reason |
|------|--------|
| anthropic_quick_start.md | Generic Anthropic docs, use official docs instead |

### CONVERT_TO_SPEC

| File | Reason |
|------|--------|
| TODO_DOCUMENTATION_IMPROVEMENTS.md | Contains actionable tasks, should be tracked properly |

---

## Execution Plan

### Phase 1: Quick Moves (Low Risk)
```bash
# Create directories if needed
mkdir -p ai_docs/archive/skills
mkdir -p ai_docs/architecture/skills

# Move to analyses/
mv ai_docs/ADW_*.md ai_docs/analyses/
mv ai_docs/FRAMEWORK_*.md ai_docs/analyses/
mv ai_docs/COMMAND_SKILL_ANALYSIS_REPORT.md ai_docs/analyses/
mv ai_docs/ENGINEERING_ASSESSMENT.md ai_docs/analyses/

# Move to reference/
mv ai_docs/claude_code_*.md ai_docs/reference/
mv ai_docs/e2b.md ai_docs/reference/
mv ai_docs/REPOSITORY_REFERENCE.md ai_docs/reference/

# Move to architecture/skills/
mv ai_docs/SKILL_DECISION_TREE.md ai_docs/architecture/skills/

# Move to research/articles/
mv ai_docs/openai_quick_start.md ai_docs/research/articles/
```

### Phase 2: Archives
```bash
# Archive historical analyses
mv ai_docs/AGENT_CLEANUP_ANALYSIS.md ai_docs/archive/
mv ai_docs/CATSY_CONTEXT_GAPS_ANALYSIS.md ai_docs/archive/
mv ai_docs/ROOT_MD_FILES_CLEANUP_ANALYSIS.md ai_docs/archive/
mv ai_docs/SKILL_OPPORTUNITIES_SUMMARY.md ai_docs/archive/skills/
mv ai_docs/SKILLS_STRATEGIC_ALIGNMENT_REPORT.md ai_docs/archive/skills/
```

### Phase 3: Consolidations (Requires Content Merge)
- Merge 3 portability docs → PORTABILITY_GUIDE.md
- Merge config index into config quick reference

### Phase 4: Deletions
```bash
rm ai_docs/anthropic_quick_start.md
```

### Phase 5: Update Indexes
- Update ROOT_INDEX.md with new locations
- Update ANALYSIS_INDEX.md with moved files

---

## Post-Triage State

After execution, ai_docs/ root will contain only:
1. README.md (directory guide)
2. ROOT_INDEX.md (navigation)
3. ANALYSIS_INDEX.md (master index)
4. TODO_DOCUMENTATION_IMPROVEMENTS.md (or moved to specs/)

**Result**: 28 files → 3-4 files in root (89% reduction)

---
*Generated: 2024-11-23*
*Method: 4 parallel Sonnet subagents*
