# Documentation Improvement Todo List

Generated from marketing/consistency review on 2024-11-23.

## High Priority (Blocking/Confusing Users)

### Path Migration
- [ ] **Complete `agents/` to `scout_outputs/` migration** - 50+ files still reference deprecated paths
  - Files: TROUBLESHOOTING_AND_INTERNALS.md (was PRACTICAL_EXECUTION_GUIDE.md), WORKFLOW_ARCHITECTURE.md, SLASH_COMMANDS_REFERENCE.md, TECHNICAL_REFERENCE.md, COMMANDS_DETAILED_COMPARISON.md, SPEC_SCHEMA.md, adw-complete.md skill
  - Impact: Users following docs get "file not found" errors

### Date Fixes
- [ ] **Fix future dates (2025)** - Multiple docs have impossible dates
  - INSTALLATION_GUIDE.md: "November 8, 2025" → "November 8, 2024"
  - NOVEMBER_8_UPDATES_SUMMARY.md: Future date
  - TECHNICAL_REFERENCE.md: "2025-01-20"
  - SPEC_SCHEMA.md: "2025-01-20"
  - SKILLS_ARCHITECTURE.md: "2025-01-23"

### Consistency
- [ ] **Reconcile Scout status** - README says "Working", other docs say "Broken"
- [ ] **Verify README command names exist** - `/planning:feature`, `/git:commit` may not be real
- [ ] **Standardize command naming** - colons vs slashes vs underscores

## Medium Priority (Quality/Professionalism)

### Value Proposition
- [ ] Add "Why This Matters" section to SPEC_SCHEMA.md
- [ ] Add context to ADW_INTEGRATION.md (what is ADW?)
- [ ] Add context to E2E-TESTS.md
- [ ] Add context to PATCH_INTEGRATION.md
- [ ] Reframe ADW_QUICK_REFERENCE.md positively (currently leads with "broken")

### Consolidation
- [x] Consider merging: FRAMEWORK_USAGE_GUIDE.md + PRACTICAL_EXECUTION_GUIDE.md + TEAM_ONBOARDING_PRESENTATION.md
  - COMPLETED (2025-11-23): Merged into TEAM_ONBOARDING_PRESENTATION.md
  - FRAMEWORK_USAGE_GUIDE.md archived to docs/archive/
  - PRACTICAL_EXECUTION_GUIDE.md renamed to TROUBLESHOOTING_AND_INTERNALS.md
- [ ] Create canonical paths reference document
- [ ] Add VERSION file with proper versioning scheme

### Organization
- [ ] Move archive files outside main docs structure
- [ ] Review ai_docs/ root files (27 files need triage)

## Low Priority (Polish)

### Style
- [ ] Standardize heading emoji usage (consistent or none)
- [ ] Add "Last Updated" date to all docs
- [ ] Add static image fallbacks for Mermaid diagrams

### Cleanup
- [ ] Fix WHERE_ARE_THE_PLANS.md shell variable `$(date +%Y-%m-%d)`
- [ ] Update SLASH_COMMANDS_REFERENCE.md date from "2024-01-20"

## Quick Wins (< 5 min each)

1. [ ] Update README.md date to specific "2024-11-23"
2. [ ] Fix INSTALLATION_GUIDE.md line 414, 487-488 dates
3. [ ] Fix SLASH_COMMANDS_REFERENCE.md line 431 date
4. [ ] Make ai_docs/README.md deprecation note more prominent
5. [ ] Clarify Scout status in README.md
6. [ ] Update TEAM_ONBOARDING_PRESENTATION.md roadmap dates
7. [ ] Fix WHERE_ARE_THE_PLANS.md shell variable

---

## Diagrams Added (Completed 2024-11-23)

| File | Diagram Type |
|------|--------------|
| INSTALLATION_GUIDE.md | Flow diagram |
| TEAM_ONBOARDING_PRESENTATION.md | Learning path |
| BITBUCKET_INTEGRATION_PLAN.md | Gantt timeline |
| TROUBLESHOOTING_AND_INTERNALS.md | Workaround flow |
| SCOUT_PLAN_BUILD_WORKFLOW.md | Sequence diagram |
| SKILLS_ARCHITECTURE.md | Architecture layers |

---
*Generated: 2024-11-23*
*Source: Marketing/consistency review by parallel subagents*
