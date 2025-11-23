# Root .md Files Cleanup Analysis

**Generated**: 2025-11-08
**Purpose**: Identify outdated/superseded root .md files for archival or deletion

---

## Executive Summary

Analyzed 5 target files in repository root. **Recommendation**: Archive 4 files, keep 1 updated reference.

| File | Status | Action | Reason |
|------|--------|--------|--------|
| `SESSION_CHECKPOINT.md` | **OUTDATED** | Archive | Session from Oct 24, 2024 - superseded |
| `HANDOFF.md` | **OUTDATED** | Archive | Session from Oct 20, 2024 - superseded by CLAUDE.md |
| `run_log.md` | **ACTIVE** | Move to logs/ | Still being updated (last: Nov 7, 2025) |
| `MCP_HOOKS_FIX_PLAN.md` | **COMPLETED** | Archive | Action items completed, docs exist |
| `WHERE_ARE_THE_PLANS.md` | **KEEP** | Update | Useful reference, needs refresh |

---

## Detailed Analysis

### 1. SESSION_CHECKPOINT.md ❌ ARCHIVE

**Last Modified**: Oct 25, 2024 (19:24)
**Size**: 1.5K

**Content Summary**:
- Session checkpoint from October 24, 2024
- Documents fixes to scout commands and pipeline validation
- References "next session" actions
- Status: "READY"

**Why Archive**:
- ✅ Session is complete (14+ days old)
- ✅ Scout command fixes documented in CLAUDE.md
- ✅ Validation scripts exist in `scripts/validate_pipeline.sh`
- ✅ Information superseded by current CLAUDE.md v3
- ✅ Historical context only - no active value

**Recommendation**: Move to `archive/sessions/2024-10-24-checkpoint.md`

---

### 2. HANDOFF.md ❌ ARCHIVE

**Last Modified**: Oct 20, 2024 (21:34)
**Size**: 4.9K

**Content Summary**:
- Comprehensive handoff summary from Jan 20, 2025 session (date in content)
- Repository analysis (28 Python files, 5,873 LOC)
- Token limit fix implementation
- File organization patterns
- Priority fixes (security, validation, error handling)

**Why Archive**:
- ✅ Session complete (18+ days old)
- ✅ Token limit fix now in `adws/adw_modules/utils.py` and documented
- ✅ File organization rules now in CLAUDE.md
- ✅ Priority fixes completed (Pydantic validation, exceptions, etc.)
- ✅ Information integrated into:
  - `CLAUDE.md` (v3 agent instructions)
  - `ai_docs/ANALYSIS_INDEX.md` (documentation index)
  - `TODO.md` (task tracking)

**Recommendation**: Move to `archive/sessions/2025-01-20-handoff.md`

**Note**: Contains valuable historical context about system evolution - worth preserving in archive.

---

### 3. run_log.md ⚠️ MOVE TO LOGS/

**Last Modified**: Nov 7, 2025 (22:55)
**Size**: 79K, 352 lines

**Content Summary**:
- Automated execution log from hooks system
- Tracks tool usage: Task, Write, Edit operations
- Date range: Oct 19, 2025 - Nov 7, 2025 (19 days of activity)
- Recent entries show active development

**Why Move (Not Archive)**:
- ✅ Still actively being appended to
- ❌ Belongs in `logs/` directory, not root
- ✅ Generated file, not documentation
- ✅ Follows pattern: generated artifacts → logs/

**Recommendation**:
```bash
# Move to logs with dated filename
mv run_log.md logs/run_log_2025-10-19_to_2025-11-07.md

# Or keep as current run log in logs/
mv run_log.md logs/run_log.md
```

**Action**: Update hooks to write to `logs/run_log.md` instead of root

---

### 4. MCP_HOOKS_FIX_PLAN.md ❌ ARCHIVE

**Last Modified**: Oct 25, 2024 (20:56)
**Size**: 6.7K

**Content Summary**:
- Action plan for MCP servers, hooks, and agent fixes
- Agent frontmatter fixes (interview-coach, vsl-director, outreach-orchestrator)
- MCP server recommendations (sequential-thinking, context7)
- Hooks installation instructions
- Configuration patterns

**Current Status Check**:
- ✅ Agent frontmatter - Fixed (no longer in git status)
- ✅ MCP servers - Documented in global CLAUDE.md
- ✅ Hooks - Exist in `.claude/hooks/` directory
- ✅ Configuration - Patterns documented in MCP_SETUP_GUIDE.md

**Why Archive**:
- ✅ All action items completed
- ✅ Knowledge captured in:
  - `~/.claude/ARCHON.md` (MCP integration)
  - `~/.claude/MCP_*.md` (individual server docs)
  - `MCP_SETUP_GUIDE.md` (setup instructions)
  - `HOOKS_SKILLS_ANALYSIS.md` (hooks analysis)
- ✅ Historical planning document, not active plan

**Recommendation**: Move to `archive/plans/2024-10-25-mcp-hooks-fix.md`

---

### 5. WHERE_ARE_THE_PLANS.md ✅ KEEP & UPDATE

**Last Modified**: Oct 29, 2024 (19:25)
**Size**: 5.9K

**Content Summary**:
- Quick reference to all documentation and plans
- Three-tier structure (Security/Automated/Strategic)
- File locations and current status
- Git branch status and recent commits

**Current Status**:
- ✅ Still useful as quick reference
- ⚠️ Information is 10 days old
- ⚠️ Git status outdated (references feature/simple-parallel-execution)
- ⚠️ Some referenced files may have moved

**Why Keep**:
- ✅ Serves as navigation/orientation document
- ✅ Helps onboarding and context recovery
- ✅ Unique value - consolidates status across repo
- ✅ Type: Reference guide (not session artifact)

**Required Updates**:
```markdown
1. Update git branch status (check current branch)
2. Verify file locations still accurate
3. Update "What's Implemented" section
4. Add date of last update at top
5. Remove completed TIER 2/3 items
6. Add new plans/specs created since Oct 29
```

**Recommendation**: **Update** to current state, keep in root

**Alternative**: If updates are too extensive, archive old version and create new `PROJECT_STATUS.md` or similar.

---

## Archive Structure Recommendation

```
archive/
├── sessions/
│   ├── 2024-10-24-checkpoint.md      (SESSION_CHECKPOINT.md)
│   └── 2025-01-20-handoff.md         (HANDOFF.md)
└── plans/
    └── 2024-10-25-mcp-hooks-fix.md   (MCP_HOOKS_FIX_PLAN.md)
```

**Rationale**:
- Sessions: Time-bound context checkpoints
- Plans: Completed action plans and strategies

---

## Execution Plan

### Phase 1: Create Archive Structure
```bash
mkdir -p archive/sessions
mkdir -p archive/plans
```

### Phase 2: Move Outdated Files
```bash
# Session artifacts
git mv SESSION_CHECKPOINT.md archive/sessions/2024-10-24-checkpoint.md
git mv HANDOFF.md archive/sessions/2025-01-20-handoff.md

# Completed plans
git mv MCP_HOOKS_FIX_PLAN.md archive/plans/2024-10-25-mcp-hooks-fix.md

# Active log to logs directory
mv run_log.md logs/run_log.md
```

### Phase 3: Update WHERE_ARE_THE_PLANS.md
```bash
# Manual update required - verify:
# - Current git branch
# - File locations
# - Completed vs pending items
# - Recent additions to specs/ and ai_docs/
```

### Phase 4: Update Hooks Configuration
```bash
# Update .claude/hooks/pre_tool_use.py to write to logs/run_log.md
# Or add to .gitignore if generated file should not be tracked
```

---

## Additional Root Files Check

Noticed during analysis - other root .md files to consider:

### High-Value Documentation (Keep)
- ✅ `README.md` - Main project readme
- ✅ `CLAUDE.md` - Agent instructions (current)
- ✅ `TODO.md` - Active task tracking
- ✅ `IMPROVEMENT_STRATEGY.md` - Strategic framework
- ✅ `NEXT_STEPS_ACTION_PLAN.md` - Current action plan

### Reference Guides (Evaluate)
- ⚠️ `TECHNICAL_REFERENCE.md` - Check if up to date
- ⚠️ `NAVIGATION_GUIDE.md` - Check if duplicates WHERE_ARE_THE_PLANS
- ⚠️ `CATSY_GUIDE.md` - Project-specific, verify relevance

### Analysis Reports (Consider Moving to ai_docs/)
- 📁 `SECURITY_AUDIT_REPORT.md` → `ai_docs/analyses/`
- 📁 `PUBLIC_RELEASE_READINESS_ASSESSMENT.md` → `ai_docs/analyses/`
- 📁 `PORTABILITY_*.md` (4 files) → `ai_docs/portability/`
- 📁 `RELEASE_READINESS.md` → `ai_docs/analyses/`
- 📁 `AGENTS_FOLDER_ANALYSIS.md` → `ai_docs/analyses/`
- 📁 `HOOKS_SKILLS_ANALYSIS.md` → `ai_docs/analyses/`
- 📁 `AI_DOCS_ORGANIZATION.md` → `ai_docs/meta/`

### Setup/Deployment Guides (Consider docs/)
- 📁 `MCP_SETUP_GUIDE.md` → `docs/setup/`
- 📁 `PORTABLE_DEPLOYMENT_GUIDE.md` → `docs/deployment/`
- 📁 `UNINSTALL_GUIDE.md` → `docs/setup/`

---

## Root Directory Organization Proposal

**Root .md Files Should Only Include**:

1. **Essential Documentation**
   - README.md (project overview)
   - CLAUDE.md (agent instructions)
   - LICENSE (legal)

2. **Active Planning**
   - TODO.md (current tasks)
   - PROJECT_STATUS.md (current state - rename/update WHERE_ARE_THE_PLANS)

3. **Strategic Frameworks**
   - IMPROVEMENT_STRATEGY.md (decision framework)
   - NEXT_STEPS_ACTION_PLAN.md (immediate actions)

**Everything Else**:
- Analyses → `ai_docs/analyses/`
- Setup guides → `docs/setup/`
- Reference docs → `docs/reference/`
- Portability docs → `ai_docs/portability/`
- Completed sessions → `archive/sessions/`
- Completed plans → `archive/plans/`

---

## Summary

### Immediate Actions (4 files)
1. ❌ Archive `SESSION_CHECKPOINT.md` → `archive/sessions/`
2. ❌ Archive `HANDOFF.md` → `archive/sessions/`
3. ❌ Archive `MCP_HOOKS_FIX_PLAN.md` → `archive/plans/`
4. 📁 Move `run_log.md` → `logs/run_log.md`

### Update & Keep (1 file)
5. ✅ Update `WHERE_ARE_THE_PLANS.md` with current status

### Follow-Up Work
- Broader root cleanup (move analyses to ai_docs/, guides to docs/)
- Update hooks to write logs to correct location
- Consider renaming WHERE_ARE_THE_PLANS → PROJECT_STATUS

---

**Total Files Analyzed**: 5
**Files to Archive**: 3
**Files to Move**: 1
**Files to Update**: 1
**Estimated Cleanup Time**: 15-20 minutes
