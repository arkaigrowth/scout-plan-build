# Skills Implementation Guide

## Quick Reference: 10 High-Value Skills to Build

This guide provides implementation priorities and concrete next steps for converting identified workflow patterns into reusable skills.

---

## Skill Implementation Priority Matrix

```
High Impact, Low Effort (IMPLEMENT FIRST)
┌─────────────────────────────────────┐
│ 5. /adw_init_state                  │
│ 8. /adw_validate_env                │
│ 10. /adw_create_branch              │
└─────────────────────────────────────┘

High Impact, Medium Effort (IMPLEMENT SECOND)
┌─────────────────────────────────────┐
│ 6. /adw_semantic_commit             │
│ 7. /adw_github_status               │
│ 2. /adw_create_plan                 │
└─────────────────────────────────────┘

High Impact, High Effort (IMPLEMENT THIRD)
┌─────────────────────────────────────┐
│ 1. /adw_orchestrate                 │
│ 3. /adw_test_with_retry             │
│ 4. /adw_review_with_fixes           │
│ 9. /adw_worktree_checkpoint         │
└─────────────────────────────────────┘
```

---

## Skill #1: `/adw_orchestrate` [CRITICAL PRIORITY]

**Problem it solves**: Eliminates 95% duplicate code across 6 orchestrator scripts

**Files to analyze**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan_build.py`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_sdlc.py`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan_build_test.py`

**What to extract**:
```python
# Extract the core pattern from adw_plan_build.py:27-72
def run_workflow_phases(issue_number, adw_id, phases):
    """
    Input:
      - issue_number: GitHub issue number
      - adw_id: Existing or new ADW ID
      - phases: List of phases to run (plan, build, test, review, document, patch)
    
    Process:
      1. Validate phase ordering
      2. For each phase:
         - Construct subprocess command
         - Pass ADW ID to preserve state
         - Check return code
         - Log phase status
      3. Return comprehensive report
    
    Output:
      - Phase completion status
      - Any errors encountered
      - Total execution time
    """
```

**Implementation approach**:
1. Create `.claude/skills/adw_orchestrate.md`
2. Document phase ordering rules and dependencies
3. Include error handling and retry logic
4. Return structured status report

**Expected impact**: 
- Reduce 6 files to 1 configurable skill
- Eliminate ~500 lines of duplicated code
- Standardize workflow orchestration

---

## Skill #2: `/adw_create_plan` [CRITICAL PRIORITY]

**Problem it solves**: Consolidates complex 9-step planning workflow

**Files to analyze**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan.py` (entire file)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:164-449` (all planning functions)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/feature.md` (planning template)

**What to extract**:
```python
# Consolidate the entire planning workflow from adw_plan.py
def create_plan_for_issue(issue_number, adw_id=None):
    """
    1. Initialize state and logger
    2. Fetch issue from GitHub
    3. Classify issue type (chore/bug/feature)
    4. Generate semantic branch name
    5. Create git branch
    6. Build implementation plan with agent
    7. Save plan to specs/
    8. Create initial commit
    9. Create/update PR
    10. Return plan file path and state
    """
```

**Implementation approach**:
1. Create `.claude/skills/adw_create_plan.md`
2. Document the 9-step sequence
3. Include error handling for each step
4. Return plan file path and state JSON

**Expected impact**:
- Single command replaces complex adw_plan.py logic
- Ensures consistent planning process
- Eliminates user confusion about planning steps

---

## Skill #3: `/adw_test_with_retry` [HIGH PRIORITY]

**Problem it solves**: Handles test failures with automatic retry and fixes

**Files to analyze**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_test.py` (lines 1-150, test retry logic)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/test.md`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/resolve_failed_test.md`

**What to extract**:
```python
# Extract retry loop logic from adw_test.py
def run_tests_with_auto_retry(max_attempts=4, skip_e2e=False):
    """
    1. Run application test suite
    2. If failures:
       - Parse failure output
       - Create fix plan
       - Implement fixes
       - Commit changes
       - Re-run tests
    3. Repeat until pass or max_attempts reached
    4. Return final test status
    """
```

**Implementation approach**:
1. Create `.claude/skills/adw_test_with_retry.md`
2. Document retry logic and MAX_ATTEMPTS constant
3. Include separate E2E retry logic (MAX_ATTEMPTS=2)
4. Return test results and attempt count

**Expected impact**:
- Automatic test recovery without user intervention
- Consistent test failure handling
- Better success rate for CI/CD pipelines

---

## Skill #4: `/adw_review_with_fixes` [HIGH PRIORITY]

**Problem it solves**: Reviews code and auto-fixes blocker issues

**Files to analyze**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_review.py` (entire file)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:create_and_implement_patch`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/review.md`

**What to extract**:
```python
# Extract review + auto-fix logic from adw_review.py
def run_review_with_fixes(spec_file, max_patch_attempts=3):
    """
    1. Run review against specification
    2. Parse issues (blocker/tech_debt/skippable)
    3. For each blocker:
       - Create patch plan
       - Implement fix
       - Commit as patch_N
    4. Re-run review to verify fixes
    5. Upload screenshots to cloud
    6. Return review report
    """
```

**Implementation approach**:
1. Create `.claude/skills/adw_review_with_fixes.md`
2. Document issue severity levels
3. Include screenshot upload to R2
4. Return final review status

**Expected impact**:
- Automatic blocker resolution
- Consistent review and remediation process
- Clear quality gates before merge

---

## Skill #5: `/adw_init_state` [HIGH PRIORITY - IMPLEMENT FIRST]

**Problem it solves**: Centralizes state initialization (repeated in every script)

**Files to analyze**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/state.py` (entire file)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:545-590` (ensure_adw_id)

**What to extract**:
```python
# Extract state initialization from adw_plan.py:84-96
def init_adw_state(issue_number, adw_id=None):
    """
    1. Generate ADW ID if not provided
    2. Load existing state or create new
    3. Initialize logger
    4. Update state with issue_number
    5. Save state to agents/{adw_id}/adw_state.json
    6. Return: {adw_id, state_dict, logger}
    """
```

**Implementation approach**:
1. Create `.claude/skills/adw_init_state.md`
2. Document state structure and file location
3. Include validation of state fields
4. Return ready-to-use state object

**Expected impact**:
- Eliminates 10+ lines per phase script
- Ensures state consistency across phases
- Simplifies phase script logic

---

## Skill #6: `/adw_semantic_commit` [HIGH PRIORITY]

**Problem it solves**: Generates semantic commit messages with ADW tracking

**Files to analyze**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:390-449` (create_commit)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/commit.md`

**What to extract**:
```python
# Extract commit message generation from workflow_ops.py
def create_semantic_commit(issue_number, message_type, description, adw_id):
    """
    1. Call agent /commit command
    2. Generate: {type}(#{issue}): {description}
    3. Include ADW ID in commit metadata
    4. Execute git add . && git commit
    5. Return commit hash
    """
```

**Implementation approach**:
1. Create `.claude/skills/adw_semantic_commit.md`
2. Document semantic versioning format
3. Include message type validation
4. Return commit hash and full message

**Expected impact**:
- Consistent commit formatting across all phases
- Automatic issue tracking in commits
- Compliance with semantic versioning

---

## Skill #7: `/adw_github_status` [MEDIUM PRIORITY]

**Problem it solves**: Posts phase status updates to GitHub consistently

**Files to analyze**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/github.py` (make_issue_comment)
- How it's used: in all phase scripts after major operations

**What to extract**:
```python
# Extract GitHub status posting pattern
def post_phase_status(issue_number, phase_name, status, adw_id, message=""):
    """
    1. Format message with ADW ID and phase name
    2. Post to GitHub issue as comment
    3. Return posted comment URL
    """
```

**Implementation approach**:
1. Create `.claude/skills/adw_github_status.md`
2. Document message formatting with ADW ID
3. Include status types: planning, building, testing, reviewing, documenting
4. Return comment URL

**Expected impact**:
- Consistent GitHub visibility of workflow progress
- Easy tracking of ADW runs via issue comments
- Better transparency to team members

---

## Skill #8: `/adw_validate_env` [MEDIUM PRIORITY - IMPLEMENT FIRST]

**Problem it solves**: Validates environment setup (repeated in every script)

**Files to analyze**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan.py:49-67` (check_env_vars)
- Similar functions in: adw_build.py, adw_test.py, adw_review.py

**What to extract**:
```python
# Extract environment validation from all phase scripts
def validate_adw_environment():
    """
    Check required env vars:
    - ANTHROPIC_API_KEY
    - CLAUDE_CODE_PATH
    - GITHUB_PAT (optional)
    - GITHUB_REPO_URL (optional)
    
    Return: {valid: bool, missing: [], helpful_instructions: str}
    """
```

**Implementation approach**:
1. Create `.claude/skills/adw_validate_env.md`
2. Document all required and optional variables
3. Include helpful setup instructions
4. Return validation result with detailed errors

**Expected impact**:
- Single pre-flight check for all workflows
- Clear error messages for setup issues
- Faster troubleshooting

---

## Skill #9: `/adw_worktree_checkpoint` [MEDIUM PRIORITY]

**Problem it solves**: Manages git worktree checkpointing with undo/redo

**Files to analyze**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/worktree_checkpoint.md` (449 lines)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/worktree_undo.md` (456 lines)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/worktree_redo.md` (504 lines)

**What to extract**:
```python
# Extract worktree checkpoint automation
def manage_worktree_checkpoint(action="checkpoint", message=""):
    """
    Actions:
    - checkpoint: Save current state with auto-commit
    - undo: Revert to previous checkpoint
    - redo: Re-apply undone changes
    
    Return: Checkpoint ID and commit hash
    """
```

**Implementation approach**:
1. Consolidate checkpoint, undo, redo logic
2. Document commit history management
3. Include auto-commit interval configuration
4. Return operation status

**Expected impact**:
- Easy undo/redo for experimental workflows
- Automatic checkpointing of progress
- Safe recovery from mistakes

---

## Skill #10: `/adw_create_branch` [MEDIUM PRIORITY]

**Problem it solves**: Creates semantic git branches with validation

**Files to analyze**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/git_ops.py:134-160` (create_branch)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:325-387` (generate_branch_name)

**What to extract**:
```python
# Extract branch creation logic
def create_semantic_branch(issue_number, issue_type, slug):
    """
    Format: {type}-{issue_number}-{adw_id}-{slug}
    Example: feat-456-e5f6g7h8-add-user-authentication
    
    1. Validate inputs
    2. Generate branch name
    3. Create git branch
    4. Push to remote
    5. Return branch name
    """
```

**Implementation approach**:
1. Create `.claude/skills/adw_create_branch.md`
2. Document semantic naming convention
3. Include validation of all inputs
4. Return branch name

**Expected impact**:
- Consistent branch naming across all workflows
- Automatic branch tracking in GitHub
- Easy to identify branch purpose from name

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- `/adw_validate_env` - Easy wins, used everywhere
- `/adw_init_state` - Core to all workflows
- `/adw_create_branch` - Needed before planning

### Phase 2: Core Workflows (Week 2-3)
- `/adw_create_plan` - Planning workflow consolidation
- `/adw_semantic_commit` - Commit standardization
- `/adw_github_status` - Progress visibility

### Phase 3: Advanced Features (Week 3-4)
- `/adw_orchestrate` - Orchestration consolidation
- `/adw_test_with_retry` - Test automation
- `/adw_review_with_fixes` - Review automation

### Phase 4: Polish (Week 4)
- `/adw_worktree_checkpoint` - Development isolation

---

## Testing Strategy

For each skill:

1. **Unit tests**: Validate individual functions
2. **Integration tests**: Test full workflow with skill
3. **Regression tests**: Ensure existing workflows still work
4. **Performance tests**: Benchmark vs. original implementation

---

## Success Metrics

After implementing all 10 skills:

- Code duplication: Reduced from ~70% to <30%
- Time to run workflow: Reduced by ~40% (eliminated validation overhead)
- User errors: Reduced by ~60% (centralized validation)
- Script complexity: Reduced by ~50% (delegated to skills)
- Maintenance burden: Reduced by ~70% (single source of truth)

---

## Files to Create

Create these 10 new files in `.claude/skills/`:

```
.claude/skills/
├── adw_orchestrate.md              # Workflow phase orchestration
├── adw_create_plan.md              # Planning workflow
├── adw_test_with_retry.md          # Test execution with retry
├── adw_review_with_fixes.md        # Review and auto-fix
├── adw_init_state.md               # State initialization
├── adw_semantic_commit.md          # Commit message generation
├── adw_github_status.md            # GitHub status posting
├── adw_validate_env.md             # Environment validation
├── adw_worktree_checkpoint.md      # Worktree management
└── adw_create_branch.md            # Branch creation
```

---

## Next Steps

1. Review `WORKFLOW_PATTERNS_ANALYSIS.md` for detailed pattern documentation
2. Start with Phase 1 implementation (3 foundation skills)
3. Create `.claude/skills/` directory if it doesn't exist
4. Implement skills in priority order
5. Update existing scripts to use new skills
6. Remove duplicated code from original scripts
7. Add tests for each skill
8. Document skill usage in README

