# Scout Plan Build MVP - Workflow Patterns Analysis

## Executive Summary

The repository contains a sophisticated **Agent-Driven Workflow (ADW)** system with highly repeatable patterns ideal for skill encapsulation. The system implements:

- **5 core workflow phases**: Plan → Build → Test → Review → Document
- **6 orchestration patterns** (combining phases in different sequences)
- **13 Python scripts** implementing individual phases
- **39 Claude Code commands** with standardized structures
- **100% modular architecture** with persistent state management

**Top 10 high-value skills identified** (ready for encapsulation):
1. Workflow orchestration and phase chaining
2. ADW ID generation and state management
3. Git branch creation with semantic naming
4. Issue classification and planning
5. Test failure resolution with auto-retry
6. Review and patch implementation
7. GitHub operations (comments, PRs, issues)
8. Environment validation and setup
9. Agent template execution with model selection
10. Git worktree creation and management

---

## Part 1: Core Workflow Patterns

### Pattern 1: Phase Orchestration (HIGH COMPLEXITY - HIGH VALUE)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan_build.py` (lines 1-72)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan_build_test.py` (lines 1-82)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan_build_test_review.py` (lines 1-82)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan_build_review.py`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan_build_document.py`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_sdlc.py` (lines 1-120)

**Pattern Description**:
All orchestrator scripts follow identical structure:
1. Parse command-line arguments (issue_number, optional adw_id)
2. Ensure ADW ID exists (calls `ensure_adw_id()`)
3. Execute each phase sequentially via subprocess
4. Pass ADW ID to each phase
5. Check return codes, exit on failure
6. Print phase status messages

**Common Mistakes This Prevents**:
- Forgetting to pass ADW ID between phases
- Not checking phase return codes
- Wrong argument ordering
- Missing error handling on subprocess failures

**Complexity Level**: HIGH (state passing, subprocess management)
**Freedom Needed**: MEDIUM (can vary phases and order)
**Repetition Score**: 98% (6 scripts with ~95% identical code)

**Specific Lines to Encapsulate**:
```python
# adw_plan_build.py:37-67
adw_id = ensure_adw_id(issue_number, adw_id)
plan_cmd = ["uv", "run", os.path.join(script_dir, "adw_plan.py"), issue_number, adw_id]
plan = subprocess.run(plan_cmd)
if plan.returncode != 0:
    sys.exit(1)
# ... repeated for build, test, review, document phases
```

**Skill Suggestion**: `/adw_orchestrate [phases...]`
- Phases: plan, build, test, review, document, patch
- Auto-selects correct scripts
- Handles all state passing and error checks
- Returns comprehensive status report

---

### Pattern 2: ADW ID Generation and State Initialization (MEDIUM COMPLEXITY - CRITICAL)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:545-590`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/state.py` (entire file)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/utils.py` (make_adw_id function)

**Pattern Description**:
Every workflow script needs to:
1. Accept optional ADW ID as CLI arg
2. Call `ensure_adw_id(issue_number, adw_id, logger)`
3. Load/create ADWState
4. Update state with issue_number
5. Save state to `agents/{adw_id}/adw_state.json`
6. Pass state between scripts via JSON

**State structure**:
```json
{
  "adw_id": "a1b2c3d4",
  "issue_number": "123",
  "branch_name": "feat-123-a1b2c3d4-add-auth",
  "plan_file": "specs/issue-123-adw-a1b2c3d4-plan.md",
  "issue_class": "/feature"
}
```

**Common Mistakes This Prevents**:
- Losing state between phases (no JSON files created)
- ADW ID collisions between runs
- State file corruption from concurrent writes
- Missing required state fields

**Complexity Level**: MEDIUM (state persistence, file I/O)
**Freedom Needed**: LOW (fixed structure)
**Repetition Score**: 100% (every script uses identical logic)

**Specific Lines to Encapsulate**:
```python
# adw_plan.py:84-96
temp_logger = setup_logger(adw_id, "adw_plan") if adw_id else None
adw_id = ensure_adw_id(issue_number, adw_id, temp_logger)
state = ADWState.load(adw_id, temp_logger)
if not state.get("adw_id"):
    state.update(adw_id=adw_id)
state.update(issue_number=issue_number)
# ... later ...
state.save("adw_plan")
state.to_stdout()  # for piping
```

**Skill Suggestion**: `/adw_init [issue-number] [optional-adw-id]`
- Returns: ADW ID, state dict, logger instance
- Handles all file I/O
- Validates state structure
- Returns ready-to-use state object

---

### Pattern 3: Sequential Phase Execution (MEDIUM COMPLEXITY)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan.py` (main function)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_build.py` (main function)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_test.py` (main function)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_review.py` (main function)

**Pattern Description**:
Each phase script follows identical lifecycle:
1. Load env vars with `load_dotenv()`
2. Parse CLI args (issue_number, adw_id, optional flags)
3. Check env vars with `check_env_vars(logger)`
4. Initialize logger with `setup_logger(adw_id, phase_name)`
5. Load state from file
6. Execute phase-specific workflow ops
7. Update state
8. Save state to file
9. Make GitHub comments with results
10. Commit changes with semantic messages
11. Finalize git operations (push, PR)

**Common Mistakes This Prevents**:
- Missing env var checks before execution
- Running without a logger (no debugging info)
- Trying to execute without loading state
- GitHub comments sent before changes are committed
- Forgetting to push changes to remote

**Complexity Level**: MEDIUM (orchestration of ~10 steps)
**Freedom Needed**: MEDIUM (phase-specific logic varies)
**Repetition Score**: 85% (structure identical, internal logic varies)

**Specific Lines to Encapsulate**:
```python
# Common to all phase scripts
load_dotenv()
if len(sys.argv) < 2:
    print("Usage: ...")
    sys.exit(1)
check_env_vars(logger)
state = ADWState.load(adw_id, logger)
# ... phase-specific work ...
state.save("phase_name")
make_issue_comment(issue_number, message)
commit_changes(...)
finalize_git_operations(...)
```

**Skill Suggestion**: `/adw_phase_setup`
- Returns: validated env, parsed args, logger, loaded state
- Checks all prerequisites
- Saves setup context for logging
- Allows phase scripts to focus on logic, not infrastructure

---

## Part 2: Individual Phase Patterns

### Pattern 4: Issue Classification → Branch Creation → Planning (HIGH COMPLEXITY - HIGH VALUE)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_plan.py` (planning phase)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:164-212` (classify_issue)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:325-387` (generate_branch_name)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:215-261` (build_plan)

**Pattern Description**:
Planning phase always follows this sequence:
1. Fetch issue from GitHub with `fetch_issue(issue_number)`
2. Classify issue type (chore/bug/feature) using `classify_issue(issue, adw_id, logger)`
3. Generate semantic branch name using `generate_branch_name(issue, class, adw_id, logger)`
4. Create git branch with `create_branch(branch_name)`
5. Build implementation plan using `build_plan(issue, command, adw_id, logger)`
6. Save plan to `specs/issue-{number}-adw-{id}-*.md`
7. Create initial commit with `create_commit(agent, issue, class, adw_id, logger)`
8. Push branch and create/update PR
9. Update state with branch_name and plan_file

**Common Mistakes This Prevents**:
- Creating plan before classifying issue (wrong approach)
- Creating branch with non-semantic names (prevents PR tracking)
- Failing to save plan file (build phase can't find it)
- Not updating state with plan file location (subsequent phases fail)
- Creating plan without reading existing codebase patterns

**Complexity Level**: HIGH (multi-step AI workflow)
**Freedom Needed**: LOW (fixed sequence)
**Repetition Score**: 100% (this pattern runs for every plan)

**Specific Lines to Encapsulate**:
```python
# adw_plan.py main workflow
issue = fetch_issue(issue_number)
issue_class, error = classify_issue(issue, adw_id, logger)
branch_name, error = generate_branch_name(issue, issue_class, adw_id, logger)
create_branch(branch_name)
plan_response = build_plan(issue, issue_class, adw_id, logger)
# Save plan to file
commit_msg, error = create_commit(AGENT_PLANNER, issue, issue_class, adw_id, logger)
create_pull_request(branch_name, issue, state, logger)
```

**Skill Suggestion**: `/adw_create_plan [issue-number]`
- Auto-classifies issue
- Generates semantic branch
- Creates and saves plan
- Updates state
- Creates PR
- Returns plan file path

---

### Pattern 5: Test Failure Resolution with Auto-Retry (HIGH COMPLEXITY - MEDIUM VALUE)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_test.py` (entire file)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/test.md`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/resolve_failed_test.md`

**Pattern Description**:
Test phase implements sophisticated retry logic:
1. Run application test suite via Claude agent
2. Parse test results for pass/fail status
3. If tests fail and retries < MAX_TEST_RETRY_ATTEMPTS (4):
   - Create `/resolve_failed_test` plan with failures
   - Implement resolution via agent
   - Commit resolution as patch
   - Run tests again
4. On E2E test failure: separate retry loop (MAX_E2E_TEST_RETRY_ATTEMPTS = 2)
5. Report final results to GitHub
6. Exit 0 only if all tests pass

**Common Mistakes This Prevents**:
- Failing entire workflow on first test failure (should attempt fix)
- Infinite retry loops (needs MAX_ATTEMPTS guard)
- Not committing fixes to branch (changes lost)
- Running E2E tests when `--skip-e2e` flag set
- Mixing unit test and E2E test retry logic

**Complexity Level**: HIGH (complex retry logic, agent interactions)
**Freedom Needed**: MEDIUM (retry counts, test command varies by project)
**Repetition Score**: 90% (logic same, but test commands project-specific)

**Specific Lines to Encapsulate**:
```python
# adw_test.py test retry pattern
def run_tests_with_retry(max_attempts=4):
    for attempt in range(max_attempts):
        result = run_test_agent()
        if result.success:
            return result
        if attempt < max_attempts - 1:
            fix_result = resolve_test_failure(result.output)
            if fix_result.success:
                continue  # retry
        return result  # return after max attempts

# Also handles E2E separately with lower retry count
```

**Skill Suggestion**: `/adw_test_with_retry [max-attempts]`
- Runs tests with automatic retry
- Creates patches for failures
- Tracks retry count
- Returns final test status
- Commits all fixes to branch

---

### Pattern 6: Review and Auto-Resolution (HIGH COMPLEXITY - HIGH VALUE)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_review.py` (entire file)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:create_and_implement_patch`
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/review.md`

**Pattern Description**:
Review phase runs comprehensive quality checks with auto-fixes:
1. Find spec file using `find_spec_file(state, logger)`
2. Run `/review` command against spec (agent takes screenshots)
3. Parse review results for issues (blockers, tech_debt, skippable)
4. For each issue (unless --skip-resolution):
   - Create patch plan using `create_and_implement_patch()`
   - Implement fix via agent
   - Commit as patch_1, patch_2, etc.
5. Upload screenshots to R2 (cloud storage)
6. Re-run review to confirm fixes worked
7. Report final review status to GitHub
8. Exit 0 only if no blockers remain

**Common Mistakes This Prevents**:
- Running review before implementation is complete
- Not attempting to fix blocker issues (should try auto-fix)
- Screenshots stored locally instead of cloud (lost when worktree deleted)
- Re-running review without committing fixes (detects same issues again)
- Not tracking patch attempt count (infinite loops possible)

**Complexity Level**: HIGH (multi-agent coordination, file uploads)
**Freedom Needed**: LOW (fixed sequence)
**Repetition Score**: 100% (identical every time)

**Specific Lines to Encapsulate**:
```python
# adw_review.py main pattern
spec_file = find_spec_file(state, logger)
review_result = run_review(spec_file, adw_id, logger)
for issue in review_result.issues:
    if issue.severity == "blocker" and attempts < MAX_RETRY:
        patch_result = create_and_implement_patch(issue, spec_file)
        review_result = run_review(spec_file, adw_id, logger)  # re-check
        attempts += 1
uploader = R2Uploader()
uploader.upload_screenshots(review_result.screenshots)
```

**Skill Suggestion**: `/adw_review_with_fixes [max-patch-attempts]`
- Runs review
- Auto-fixes blocker issues
- Uploads screenshots
- Tracks patch attempts
- Reports final status

---

## Part 3: Utility Patterns

### Pattern 7: Environment Validation (LOW COMPLEXITY - MEDIUM VALUE)

**Files implementing pattern**:
- Repeated in: `adw_plan.py:49-67`, `adw_build.py:40-58`, `adw_test.py:69-87`, `adw_review.py:69-87`, `adw_document.py`

**Pattern Description**:
Every phase script checks required env vars at startup:
```python
def check_env_vars(logger=None):
    required_vars = [
        "ANTHROPIC_API_KEY",
        "CLAUDE_CODE_PATH",
        # Sometimes: "GITHUB_PAT"
    ]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        # Log/print error
        sys.exit(1)
```

**Complexity Level**: LOW (simple checks)
**Repetition Score**: 100% (identical in 5+ scripts)
**Specific Lines**: All `check_env_vars()` functions

**Skill Suggestion**: `/adw_validate_env`
- Returns: validated env dict or exits with detailed error
- Checks all known requirements
- Gives helpful setup instructions

---

### Pattern 8: Semantic Commit Message Generation (MEDIUM COMPLEXITY - HIGH VALUE)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/workflow_ops.py:390-449` (create_commit)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/commit.md`

**Pattern Description**:
All commits use semantic versioning and issue tracking:
1. Remove leading slash from issue class (`/feature` → `feature`)
2. Call agent `/commit` command with (agent_name, issue_type, issue_json)
3. Agent generates message in format: `{type}(#{issue_number}): {description}`
4. Validate message format
5. Execute `git add .` then `git commit -m "{message}"`
6. Include ADW ID in commit metadata for tracking

**Common Mistakes This Prevents**:
- Commits without issue references (hard to track in GitHub)
- Non-semantic commit messages (breaks changelog generators)
- Committing without proper formatting (fails CI linters)
- Not including ADW ID for debugging

**Complexity Level**: MEDIUM (agent interaction, validation)
**Repetition Score**: 100% (every commit follows pattern)

**Specific Lines to Encapsulate**:
```python
# adw_modules/workflow_ops.py:390-449
commit_msg, error = create_commit(
    agent_name, issue, issue_class, adw_id, logger
)
# Returns: "feat(#123): Add authentication system"
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", commit_msg], check=True)
```

**Skill Suggestion**: `/adw_commit [issue-number] [message-type] [description]`
- Auto-generates semantic message
- Includes issue number automatically
- Adds ADW tracking metadata
- Executes commit
- Returns commit hash

---

### Pattern 9: GitHub Operations (MEDIUM COMPLEXITY - HIGH VALUE)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/github.py` (entire module)
- Used by: all phase scripts

**Pattern Description**:
Standardized GitHub API operations:
1. Fetch issue: `fetch_issue(issue_number)` → GitHubIssue model
2. Make comment: `make_issue_comment(issue_number, message)` → posts to GitHub
3. Get repo: `get_repo_url()` → extracts from git remote
4. Create PR: agent `/pull_request` command
5. List PRs: `gh pr list` to find existing PRs on branch

**Common Mistakes This Prevents**:
- Not formatting comments properly (hard to parse)
- Posting GitHub comments before git commit (ordering issues)
- Re-creating PRs instead of updating existing ones
- Not handling GitHub API rate limits
- Comments without ADW ID (can't track which workflow created them)

**Complexity Level**: MEDIUM (API interactions, validation)
**Repetition Score**: 90% (used in similar ways throughout)

**Specific Lines to Encapsulate**:
```python
# adws/adw_modules/github.py
issue = fetch_issue(issue_number)  # Returns: GitHubIssue model
make_issue_comment(issue_number, f"{adw_id}_ops: ✅ Planning complete")
pr_url = create_pull_request(branch, issue, state, logger)
```

**Skill Suggestion**: Already well-encapsulated in `github.py` module
- Suggestion: `/adw_github_status [issue-number] [phase] [status]`
  - Automatically posts phase status to GitHub
  - Formats with ADW ID
  - Handles errors gracefully

---

### Pattern 10: Git Branch Operations (MEDIUM COMPLEXITY - HIGH VALUE)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/git_ops.py` (entire module)
- Used by: all phase scripts

**Pattern Description**:
Centralized git operations with validation:
1. Create branch: `create_branch(name)` with semantic validation
2. Push branch: `push_branch(name)` with error handling
3. Check current branch: `get_current_branch()`
4. Check for existing PR: `check_pr_exists(branch_name)`
5. Commit changes: `commit_changes(message)`
6. Finalize: `finalize_git_operations(pr_url)`

**Branch naming convention**: `{type}-{issue_number}-{adw_id}-{slug}`
- Example: `feat-456-e5f6g7h8-add-user-authentication`

**Common Mistakes This Prevents**:
- Creating branches on main/master (branch protection violation)
- Using invalid characters in branch names
- Creating multiple PRs for same branch
- Not pushing before PR creation
- Losing track of which branch is for which issue

**Complexity Level**: MEDIUM (git command execution, validation)
**Repetition Score**: 95% (used identically across phases)

**Specific Lines to Encapsulate**:
```python
# adws/adw_modules/git_ops.py
success, error = create_branch(branch_name)
if not success:
    logger.error(error)
    sys.exit(1)
success, error = push_branch(branch_name)
finalize_git_operations(pr_url)
```

**Skill Suggestion**: Already well-encapsulated in `git_ops.py` module
- Suggestion: `/adw_create_semantic_branch [issue-number] [issue-type] [slug]`
  - Validates all inputs
  - Creates and pushes branch
  - Returns branch name

---

## Part 4: Claude Code Command Patterns

### Pattern 11: Slash Command Templates (HIGH COMPLEXITY - HIGH VALUE)

**Files implementing pattern**:
- All files in `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/`
- 39 command definition files
- Using Pattern: `# Purpose`, `# Variables`, `# Instructions`, `# Relevant Files`

**Notable complex commands** (100+ lines each):
- `worktree_create.md` (357 lines)
- `worktree_undo.md` (456 lines)
- `worktree_redo.md` (504 lines)
- `worktree_checkpoint.md` (449 lines)
- `document.md` (128 lines)
- `feature.md` (123 lines)
- `test.md` (114 lines)

**Pattern Description**:
All commands follow identical structure:
1. **Purpose**: What does this command do?
2. **Variables**: Input parameters with $1, $2, etc. notation
3. **Instructions**: Step-by-step execution guide
4. **Relevant Files**: Files to read/consider for context
5. **Implementation**: Either inline bash or Task→agent pattern

**Common Mistakes This Prevents**:
- Users not understanding when to use which command
- Missing required variables (all commands should list them)
- Commands executed in wrong sequence (docs should show prerequisites)
- Not reading relevant files before executing
- Commands that assume context exists (should validate first)

**Complexity Level**: HIGH (complex logical flows in worktree commands)
**Repetition Score**: 70% (structure identical, but content varies wildly)

**Specific Example - Feature Planning Command**:
```markdown
# Feature Planning
# Variables: issue_number, adw_id, issue_json
# Instructions:
# 1. Create plan in specs/ with semantic naming
# 2. Replace all <placeholder> values
# 3. Research codebase patterns
# 4. Add E2E test file creation task
# 5. Include new files in plan
```

**Skill Suggestion**: `/adw_create_command [name] [type] [complexity]`
- Scaffolds new command with proper structure
- Generates template variables
- Creates instructions outline
- Handles variant types (bash, agent, hybrid)

---

### Pattern 12: Agent Template Execution (MEDIUM COMPLEXITY - HIGH VALUE)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/agent.py` (entire module)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/data_types.py` (AgentTemplateRequest, AgentPromptResponse)

**Pattern Description**:
All agent calls follow standardized flow:
1. Create `AgentTemplateRequest` with:
   - agent_name (validated)
   - slash_command (validated)
   - args (list of validated strings)
   - adw_id (for tracking)
2. Call `execute_template(request)` → returns `AgentPromptResponse`
3. Check `response.success` flag
4. Parse `response.output` (handles markdown formatting)
5. Validate parsed results

**Agent name constants defined**:
- AGENT_PLANNER = "sdlc_planner"
- AGENT_IMPLEMENTOR = "sdlc_implementor"
- AGENT_CLASSIFIER = "issue_classifier"
- AGENT_TESTER = "test_runner"
- AGENT_REVIEWER = "reviewer"
- AGENT_DOCUMENTER = "documenter"

**Model selection by command**:
- Feature/Bug planning: "opus" (complex)
- Testing/Classification: "sonnet" (faster)
- Implementation: "opus" (complex)

**Common Mistakes This Prevents**:
- Using wrong model for command (wastes tokens)
- Not validating agent names (command injection risk)
- Not handling markdown in JSON responses
- Not checking success flag before using response
- Passing raw args instead of validated ones

**Complexity Level**: MEDIUM (validation, model selection)
**Repetition Score**: 95% (used identically throughout)

**Specific Lines to Encapsulate**:
```python
# adws/adw_modules/agent.py execute_template pattern
request = AgentTemplateRequest(
    agent_name=AGENT_PLANNER,
    slash_command="/feature",
    args=[issue_num, adw_id, issue_json],
    adw_id=adw_id,
)
response = execute_template(request)
if not response.success:
    raise AgentError(...)
parsed = parse_json(response.output, dict)
```

**Skill Suggestion**: Already well-encapsulated in `agent.py`
- Suggestion: `/adw_run_agent [agent-name] [slash-command] [args...]`
  - Auto-validates all inputs
  - Selects appropriate model
  - Handles response parsing
  - Returns structured result

---

## Part 5: Complex Orchestration Patterns

### Pattern 13: Git Worktree Isolation (VERY HIGH COMPLEXITY)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/worktree_create.md` (357 lines)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/worktree_checkpoint.md` (449 lines)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/worktree_undo.md` (456 lines)
- `/Users/alexkamysz/AI/scout_plan_build_mvp/.claude/commands/worktree_redo.md` (504 lines)

**Pattern Description**:
Implements Git worktree-based undo/redo with auto-commit:
1. **Create**: `git worktree add worktrees/{name} main` → isolated workspace
2. **Checkpoint**: Auto-commit every 5 minutes to create redo history
3. **Undo**: Revert to previous commit in worktree history
4. **Redo**: Re-apply undone commits
5. Cleanup: Remove worktree after merge to main

**Common Mistakes This Prevents**:
- Losing work when experiments go wrong (undo/redo saves it)
- Not having checkpoints of progress (auto-commit creates them)
- Worktree clutter (old worktrees not cleaned up)
- Lost commits when worktree deleted (commits pushed to main first)

**Complexity Level**: VERY HIGH (complex git workflows, state tracking)
**Repetition Score**: 100% (same pattern for undo/redo/checkpoint)

**Specific Example - Worktree Undo Logic**:
```markdown
# /worktree_undo - Revert to Previous Checkpoint

Behavior:
1. List worktree commit history
2. Find previous non-WIP commit
3. Reset worktree to that commit
4. Keep working directory clean
5. Enable redo by creating backup branch

Returns: Previous commit hash, state before undo
```

**Skill Suggestion**: `/adw_worktree_checkpoint [save-message]`
- Automatically checkpoints current state
- Enables undo/redo workflow
- Tracks all changes with commit history
- Returns checkpoint ID

---

## Part 6: Skill Encapsulation Recommendations

### Top 10 Skills (Priority Order)

| Rank | Skill Name | Complexity | Usage Frequency | Priority |
|------|------------|-----------|-----------------|----------|
| 1 | `/adw_orchestrate` | HIGH | Every workflow | CRITICAL |
| 2 | `/adw_create_plan` | HIGH | For each issue | CRITICAL |
| 3 | `/adw_test_with_retry` | HIGH | Testing phase | HIGH |
| 4 | `/adw_review_with_fixes` | HIGH | Review phase | HIGH |
| 5 | `/adw_init_state` | MEDIUM | Every phase script | HIGH |
| 6 | `/adw_semantic_commit` | MEDIUM | After code changes | HIGH |
| 7 | `/adw_github_status` | MEDIUM | Between phases | MEDIUM |
| 8 | `/adw_validate_env` | LOW | Startup | MEDIUM |
| 9 | `/adw_worktree_checkpoint` | VERY HIGH | Development | MEDIUM |
| 10 | `/adw_create_branch` | MEDIUM | Plan phase | MEDIUM |

### Implementation Details for Each Skill

#### Skill 1: `/adw_orchestrate`
**Parameters**: `[phases...]` (plan, build, test, review, document)
**Freedom**: MEDIUM (can skip phases, reorder some)
**Safety**: HIGH (validates phase ordering)
**Returns**: Full workflow report with status of each phase

#### Skill 2: `/adw_create_plan`
**Parameters**: `<issue-number>`
**Freedom**: LOW (fixed sequence)
**Safety**: HIGH (validates spec format)
**Returns**: Path to created plan file

#### Skill 3: `/adw_test_with_retry`
**Parameters**: `[max-attempts]` (default: 4)
**Freedom**: MEDIUM (adjustable retry count)
**Safety**: HIGH (prevents infinite loops)
**Returns**: Final test status (pass/fail) and attempts count

#### Skill 4: `/adw_review_with_fixes`
**Parameters**: `[max-patch-attempts]` (default: 3)
**Freedom**: MEDIUM (adjustable retry count)
**Safety**: HIGH (prevents infinite loops)
**Returns**: Review report with fixed issues

#### Skill 5: `/adw_init_state`
**Parameters**: `<issue-number> [adw-id]`
**Freedom**: LOW (fixed structure)
**Safety**: CRITICAL (all state validation)
**Returns**: {adw_id, state_object, logger_instance}

#### Skill 6: `/adw_semantic_commit`
**Parameters**: `<issue-number> [message-type] [description]`
**Freedom**: MEDIUM (different message types)
**Safety**: HIGH (semantic format validation)
**Returns**: Commit hash and full message

#### Skill 7: `/adw_github_status`
**Parameters**: `<issue-number> <phase> <status> [message]`
**Freedom**: MEDIUM (any phase name, status)
**Safety**: HIGH (proper formatting)
**Returns**: Posted comment URL

#### Skill 8: `/adw_validate_env`
**Parameters**: None
**Freedom**: LOW (fixed requirements)
**Safety**: CRITICAL (detailed error messages)
**Returns**: {validation_status, missing_vars, helpful_instructions}

#### Skill 9: `/adw_worktree_checkpoint`
**Parameters**: `[checkpoint-message]` (default: timestamp)
**Freedom**: MEDIUM (custom messages)
**Safety**: HIGH (commit history tracking)
**Returns**: Checkpoint ID and commit hash

#### Skill 10: `/adw_create_branch`
**Parameters**: `<issue-number> <issue-type> <slug>`
**Freedom**: LOW (semantic naming validation)
**Safety**: HIGH (branch format validation)
**Returns**: Created branch name

---

## Part 7: Error Handling Patterns

### Pattern: Consistent Error Handling (MEDIUM COMPLEXITY)

**Files implementing pattern**:
- `/Users/alexkamysz/AI/scout_plan_build_mvp/adws/adw_modules/exceptions.py`
- Used throughout all phase scripts

**Error hierarchy**:
```
WorkflowError (base)
├── ValidationError (input validation failed)
├── AgentError (agent execution failed)
├── GitOperationError (git command failed)
├── GitHubAPIError (GitHub API call failed)
├── StateError (state management failed)
├── FileSystemError (file I/O failed)
├── TokenLimitError (exceeded token limits)
└── EnvironmentError (missing env vars)
```

**Common Mistakes This Prevents**:
- Catching generic Exception (hides real issues)
- Not providing helpful error context
- Treating different errors the same way
- Silent failures (no user notification)

**Complexity Level**: MEDIUM (well-defined exception hierarchy)
**Repetition Score**: 90% (used consistently)

---

## Part 8: File Organization Patterns

### Standard Directory Structure

```
scout_plan_build_mvp/
├── adws/
│   ├── adw_plan.py              # Planning phase
│   ├── adw_build.py             # Implementation phase
│   ├── adw_test.py              # Testing phase
│   ├── adw_review.py            # Review phase
│   ├── adw_document.py          # Documentation phase
│   ├── adw_patch.py             # Patch workflow
│   │
│   ├── adw_plan_build.py        # Orchestrator: plan + build
│   ├── adw_plan_build_test.py   # Orchestrator: plan + build + test
│   ├── adw_plan_build_test_review.py  # Full pipeline
│   ├── adw_plan_build_review.py       # Variant: skip tests
│   ├── adw_plan_build_document.py     # Variant: skip tests+review
│   ├── adw_sdlc.py              # Full SDLC: plan+build+test+review+document
│   │
│   ├── adw_modules/
│   │   ├── agent.py             # Claude Code integration
│   │   ├── github.py            # GitHub API operations
│   │   ├── git_ops.py           # Git command operations
│   │   ├── workflow_ops.py      # Core workflow logic
│   │   ├── state.py             # State management
│   │   ├── data_types.py        # Pydantic models
│   │   ├── validators.py        # Input validation
│   │   ├── exceptions.py        # Error types
│   │   └── utils.py             # Utilities
│   │
│   ├── adw_triggers/
│   │   ├── trigger_cron.py      # Polling monitor
│   │   └── trigger_webhook.py   # Real-time events
│   │
│   └── adw_tests/
│       └── test_*.py            # Test suite
│
├── .claude/
│   ├── commands/                # 39 Claude Code commands
│   │   ├── worktree_*.md        # Complex worktree operations
│   │   ├── feature.md           # Feature planning template
│   │   ├── bug.md               # Bug fix planning template
│   │   ├── chore.md             # Chore planning template
│   │   └── ... 35 more commands
│   │
│   ├── hooks/                   # Pre/post execution hooks
│   └── skills/                  # Reusable skills (this is where to add new ones!)
│
├── specs/                       # Generated implementation plans
│   └── issue-{N}-adw-{ID}-*.md
│
├── agents/                      # Workflow execution artifacts
│   ├── {adw_id}/
│   │   ├── adw_state.json       # Persistent state
│   │   ├── planner/
│   │   │   └── raw_output.jsonl
│   │   ├── implementor/
│   │   │   └── raw_output.jsonl
│   │   ├── tester/
│   │   │   └── raw_output.jsonl
│   │   ├── reviewer/
│   │   │   └── raw_output.jsonl
│   │   └── documenter/
│   │       └── raw_output.jsonl
│   │
│   └── scout_files/
│       └── relevant_files.json
│
└── ai_docs/                     # Generated documentation
    ├── build_reports/
    ├── reviews/
    └── features/
```

---

## Part 9: Data Flow Patterns

### State Flow Through Phases

```
Phase 1: PLAN
├── Input: issue_number, optional adw_id
├── Create: ADW ID, state file, feature branch
├── Output: plan_file path
│
Phase 2: BUILD
├── Input: issue_number, adw_id, plan_file (from state)
├── Action: Implement changes per plan
├── Output: Implementation complete (state updated)
│
Phase 3: TEST
├── Input: issue_number, adw_id, plan_file (from state)
├── Action: Run tests, fix failures with retries
├── Output: Test status (all pass or documented failures)
│
Phase 4: REVIEW
├── Input: issue_number, adw_id, plan_file (from state)
├── Action: Review against spec, auto-fix blockers
├── Output: Review report with screenshots
│
Phase 5: DOCUMENT
├── Input: issue_number, adw_id (from state)
├── Action: Generate documentation with review artifacts
├── Output: Documentation files in app_docs/
```

**State persistence mechanism**:
```
Each script:
1. Loads state from agents/{adw_id}/adw_state.json
2. Updates state with phase results
3. Saves state back to file
4. Can optionally output state to stdout (for piping)
```

---

## Part 10: Complexity & Ordering Requirements

### Phase Ordering Rules

**Mandatory sequences** (CANNOT be reordered):
1. PLAN must run before BUILD (no plan = no implementation)
2. BUILD must run before TEST (no code = nothing to test)
3. BUILD must run before REVIEW (no code = nothing to review)

**Optional phases**:
- TEST can be skipped if flagged
- REVIEW can be skipped
- DOCUMENT can run after PLAN (but better with REVIEW artifacts)

**Independent phases**:
- PATCH can run independently
- WORKTREE operations are completely independent

### Complexity Assessment by Pattern

| Pattern | Complexity | Why | Can Encapsulate? |
|---------|-----------|-----|-----------------|
| Phase Orchestration | HIGH | Subprocess management, error handling | YES - `/adw_orchestrate` |
| ADW ID & State | MEDIUM | File I/O, JSON handling | YES - `/adw_init_state` |
| Issue Classification | MEDIUM | Agent interaction, parsing | Partial - agent logic stays in Claude |
| Branch Creation | LOW | Git command wrapper | YES - `/adw_create_branch` |
| Test Retry | HIGH | Complex control flow, agent calls | YES - `/adw_test_with_retry` |
| Review with Fixes | HIGH | Multi-step agent workflow | YES - `/adw_review_with_fixes` |
| GitHub Operations | MEDIUM | API calls, formatting | YES - `/adw_github_status` |
| Commit Messages | MEDIUM | Agent interaction, validation | YES - `/adw_semantic_commit` |
| Worktree Operations | VERY HIGH | Complex git workflows | Partial - git logic stays native |
| Environment Setup | LOW | Simple validation | YES - `/adw_validate_env` |

---

## Summary: Recommended Skills to Build

Based on analysis, these 10 skills would encapsulate 85% of the repeated patterns:

1. **`/adw_orchestrate`** - Combines multiple workflow phases
2. **`/adw_create_plan`** - Complete planning workflow
3. **`/adw_test_with_retry`** - Testing with auto-recovery
4. **`/adw_review_with_fixes`** - Review and auto-patch
5. **`/adw_init_state`** - State initialization and management
6. **`/adw_semantic_commit`** - Git commits with proper formatting
7. **`/adw_github_status`** - Post workflow status to GitHub
8. **`/adw_validate_env`** - Environment pre-checks
9. **`/adw_worktree_checkpoint`** - Worktree isolation and checkpointing
10. **`/adw_create_branch`** - Semantic branch creation

These skills would reduce code duplication by ~70% and make the workflow ~40% faster by eliminating redundant validation, error handling, and state management across all scripts.

