# AI Developer Workflow (ADW) System

ADW automates software development by integrating GitHub issues with Claude Code CLI to classify issues, generate plans, implement solutions, and create pull requests.

## Key Concepts

### ADW ID
Each workflow run is assigned a unique 8-character identifier (e.g., `a1b2c3d4`). This ID:
- Tracks all phases of a workflow (plan → build → test → review → document)
- Appears in GitHub comments, commits, and PR titles
- Creates an isolated workspace at `agents/{adw_id}/`
- Enables resuming workflows and debugging

### State Management
ADW uses persistent state files (`agents/{adw_id}/adw_state.json`) to:
- Share data between workflow phases
- Enable workflow composition and chaining
- Track essential workflow data:
  - `adw_id`: Unique workflow identifier
  - `issue_number`: GitHub issue being processed
  - `branch_name`: Git branch for changes
  - `plan_file`: Path to implementation plan
  - `issue_class`: Issue type (`/chore`, `/bug`, `/feature`)

### Workflow Composition
Workflows can be:
- Run individually (e.g., just planning or just testing)
- Chained via pipes: `adw_plan.py 123 | adw_build.py`
- Combined in orchestrator scripts (e.g., `adw_sdlc.py` runs all phases)

## Quick Start

### 1. Set Environment Variables

```bash
export GITHUB_REPO_URL="https://github.com/owner/repository"
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export CLAUDE_CODE_PATH="/path/to/claude"  # Optional, defaults to "claude"
export GITHUB_PAT="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Optional, only if using different account than 'gh auth login'
```

### 2. Install Prerequisites

```bash
# GitHub CLI
brew install gh              # macOS
# or: sudo apt install gh    # Ubuntu/Debian
# or: winget install --id GitHub.cli  # Windows

# Claude Code CLI
# Follow instructions at https://docs.anthropic.com/en/docs/claude-code

# Python dependency manager (uv)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Authenticate GitHub
gh auth login
```

### 3. Run ADW

```bash
cd adws/

# Process a single issue manually (plan + build)
uv run adw_plan_build.py 123

# Process a single issue with testing (plan + build + test)
uv run adw_plan_build_test.py 123

# Process with review (plan + build + test + review)
uv run adw_plan_build_test_review.py 123

# Process with review but skip tests (plan + build + review)
uv run adw_plan_build_review.py 123

# Process with documentation but skip tests and review (plan + build + document)
uv run adw_plan_build_document.py 123

# Complete SDLC workflow (plan + build + test + review + document)
uv run adw_sdlc.py 123

# Run individual phases
uv run adw_plan.py 123     # Planning phase only
uv run adw_build.py 123 <adw-id>   # Build phase only (requires existing plan)
uv run adw_test.py 123 <adw-id>    # Test phase only
uv run adw_review.py 123 <adw-id>  # Review phase only
uv run adw_document.py 123 <adw-id>  # Documentation phase only

# Run continuous monitoring (polls every 20 seconds)
uv run adw_triggers/trigger_cron.py

# Start webhook server (for instant GitHub events)
uv run adw_triggers/trigger_webhook.py
```

## ADW Workflow Scripts

### Individual Phase Scripts

#### adw_plan.py - Planning Phase
Creates implementation plans for GitHub issues.

**Requirements:**
- GitHub issue number
- Issue must be open and accessible

**Usage:**
```bash
uv run adw_plan.py <issue-number> [adw-id]
```

**What it does:**
1. Fetches issue details from GitHub
2. Classifies issue type (`/chore`, `/bug`, `/feature`)
3. Creates feature branch with semantic naming
4. Generates detailed implementation plan
5. Commits plan as `{adw_id}_plan_spec.md`
6. Creates/updates pull request
7. Outputs state JSON for chaining

#### adw_build.py - Implementation Phase
Implements solutions based on existing plans.

**Requirements:**
- Existing plan file (from `adw_plan.py` or manual)
- Can receive state via stdin or find plan automatically

**Usage:**
```bash
# Standalone (finds plan automatically)
uv run adw_build.py

# With piped state
uv run adw_plan.py 456 | uv run adw_build.py

# With explicit arguments
uv run adw_build.py <issue-number> <adw-id>
```

**What it does:**
1. Locates existing plan file
2. Implements solution per plan specifications
3. Commits implementation changes
4. Updates pull request

#### adw_test.py - Testing Phase
Runs test suites and handles test failures.

**Requirements:**
- Working directory with test suite
- Optional: E2E test setup

**Usage:**
```bash
uv run adw_test.py <issue-number> [adw-id] [--skip-e2e]
```

**What it does:**
1. Runs application test suite
2. Optionally runs E2E tests (browser automation)
3. Auto-resolves test failures (up to 3 attempts)
4. Reports results to GitHub issue
5. Commits test results

#### adw_review.py - Review Phase
Reviews implementation against specifications.

**Requirements:**
- Existing specification file
- Completed implementation
- ADW ID is required

**Usage:**
```bash
uv run adw_review.py <issue-number> <adw-id> [--skip-resolution]
```

**What it does:**
1. Locates specification file
2. Reviews implementation for spec compliance
3. Captures screenshots of functionality
4. Identifies issues (blockers, tech debt, skippable)
5. Auto-resolves blockers (unless `--skip-resolution`)
6. Uploads screenshots to cloud storage
7. Posts detailed review report

#### adw_document.py - Documentation Phase
Generates comprehensive documentation.

**Requirements:**
- Completed review phase (needs review artifacts)
- ADW ID is mandatory

**Usage:**
```bash
uv run adw_document.py <issue-number> <adw-id>
```

**What it does:**
1. Analyzes implementation and review results
2. Generates technical documentation
3. Creates user-facing guides
4. Includes screenshots from review
5. Commits to `app_docs/` directory

#### adw_patch.py - Direct Patch Workflow
Quick patches triggered by 'adw_patch' keyword.

**Requirements:**
- Issue or comment containing 'adw_patch' keyword
- Clear change request in the content

**Usage:**
```bash
uv run adw_patch.py <issue-number> [adw-id]
```

**What it does:**
1. Searches for 'adw_patch' in issue/comments
2. Creates targeted patch plan
3. Implements specific changes
4. Commits and creates PR
5. Skips full planning phase

### Orchestrator Scripts

#### adw_plan_build.py - Plan + Build
Combines planning and implementation phases.

**Usage:**
```bash
uv run adw_plan_build.py <issue-number> [adw-id]
```

**Equivalent to:**
```bash
uv run adw_plan.py 456 | uv run adw_build.py
```

#### adw_plan_build_test.py - Plan + Build + Test
Full pipeline with automated testing.

**Usage:**
```bash
uv run adw_plan_build_test.py <issue-number> [adw-id]
```

**Phases:**
1. Planning (creates implementation spec)
2. Building (implements solution)
3. Testing (runs test suite, auto-fixes failures)


#### adw_plan_build_test_review.py - Plan + Build + Test + Review
Complete pipeline with quality review.

**Usage:**
```bash
uv run adw_plan_build_test_review.py <issue-number> [adw-id]
```

**Phases:**
1. Planning (creates implementation spec)
2. Building (implements solution)
3. Testing (ensures functionality)
4. Review (validates against spec, auto-fixes issues)

#### adw_plan_build_review.py - Plan + Build + Review
Pipeline with review but skipping tests.

**Usage:**
```bash
uv run adw_plan_build_review.py <issue-number> [adw-id]
```

**Phases:**
1. Planning (creates implementation spec)
2. Building (implements solution)
3. Review (validates against spec without test results)

**Note:** Review phase evaluates implementation against specification but without test verification. Best for non-critical changes or when testing is handled separately.

#### adw_plan_build_document.py - Plan + Build + Document
Fast documentation pipeline skipping tests and review.

**Usage:**
```bash
uv run adw_plan_build_document.py <issue-number> [adw-id]
```

**Phases:**
1. Planning (creates implementation spec)
2. Building (implements solution)
3. Document (generates documentation without screenshots)

**Warning:** Documentation quality may be limited without review artifacts (no screenshots). Consider using `adw_sdlc.py` for comprehensive documentation with visuals.

#### adw_sdlc.py - Complete SDLC
Full Software Development Life Cycle automation.

**Usage:**
```bash
uv run adw_sdlc.py <issue-number> [adw-id]
```

**Phases:**
1. **Plan**: Creates detailed implementation spec
2. **Build**: Implements the solution
3. **Test**: Runs comprehensive test suite
4. **Review**: Validates implementation vs spec
5. **Document**: Generates technical and user docs

**Output:**
- Feature implementation
- Passing tests
- Review report with screenshots
- Complete documentation in `app_docs/`

### Automation Triggers

#### trigger_cron.py - Polling Monitor
Continuously monitors GitHub for triggers.

**Usage:**
```bash
uv run adw_triggers/trigger_cron.py
```

**Triggers on:**
- New issues with no comments
- Any issue where latest comment is exactly "adw"
- Polls every 20 seconds

**Workflow selection:**
- Uses `adw_plan_build.py` by default
- Excludes `adw_build` (implementation-only) workflows

#### trigger_webhook.py - Real-time Events
Webhook server for instant GitHub event processing.

**Usage:**
```bash
uv run adw_triggers/trigger_webhook.py
```

**Configuration:**
- Default port: 8001
- Endpoints:
  - `/gh-webhook` - GitHub event receiver
  - `/health` - Health check
- GitHub webhook settings:
  - Payload URL: `https://your-domain.com/gh-webhook`
  - Content type: `application/json`
  - Events: Issues, Issue comments

**Security:**
- Validates GitHub webhook signatures
- Requires `GITHUB_WEBHOOK_SECRET` environment variable

## How ADW Works

1. **Issue Classification**: Analyzes GitHub issue and determines type:
   - `/chore` - Maintenance, documentation, refactoring
   - `/bug` - Bug fixes and corrections
   - `/feature` - New features and enhancements

2. **Planning**: `sdlc_planner` agent creates implementation plan with:
   - Technical approach
   - Step-by-step tasks
   - File modifications
   - Testing requirements

3. **Implementation**: `sdlc_implementor` agent executes the plan:
   - Analyzes codebase
   - Implements changes
   - Runs tests
   - Ensures quality

4. **Integration**: Creates git commits and pull request:
   - Semantic commit messages
   - Links to original issue
   - Implementation summary

## Common Usage Scenarios

### Process a bug report
```bash
# User reports bug in issue #789
uv run adw_plan_build.py 789
# ADW analyzes, creates fix, and opens PR
```

### Run full pipeline
```bash
# Complete pipeline with testing
uv run adw_plan_build_test.py 789
# ADW plans, builds, and tests the solution
```

### Run complete SDLC
```bash
# Full SDLC with review and documentation
uv run adw_sdlc.py 789
# ADW plans, builds, tests, reviews, and documents the solution
# Creates comprehensive documentation in app_docs/
```

### Run individual phases
```bash
# Plan only
uv run adw_plan.py 789

# Build based on existing plan
uv run adw_build.py

# Test the implementation
uv run adw_test.py 789
```

### Enable automatic processing
```bash
# Start cron monitoring
uv run adw_triggers/trigger_cron.py
# New issues are processed automatically
# Users can comment "adw" to trigger processing
```

### Deploy webhook for instant response
```bash
# Start webhook server
uv run adw_triggers/trigger_webhook.py
# Configure in GitHub settings
# Issues processed immediately on creation
```

## Troubleshooting

### Environment Issues
```bash
# Check required variables
env | grep -E "(GITHUB|ANTHROPIC|CLAUDE)"

# Verify GitHub auth
gh auth status

# Test Claude Code
claude --version
```

### Common Errors

**"Claude Code CLI is not installed"**
```bash
which claude  # Check if installed
# Reinstall from https://docs.anthropic.com/en/docs/claude-code
```

**"Missing GITHUB_PAT"** (Optional - only needed if using different account than 'gh auth login')
```bash
export GITHUB_PAT=$(gh auth token)
```

**"Agent execution failed"**
```bash
# Check agent output
cat agents/*/sdlc_planner/raw_output.jsonl | tail -1 | jq .
```

### Debug Mode
```bash
export ADW_DEBUG=true
uv run adw_plan_build.py 123  # Verbose output
```

## Configuration

### ADW Tracking
Each workflow run gets a unique 8-character ID (e.g., `a1b2c3d4`) that appears in:
- Issue comments: `a1b2c3d4_ops: ✅ Starting ADW workflow`
- Output files: `agents/a1b2c3d4/sdlc_planner/raw_output.jsonl`
- Git commits and PRs

### Model Selection
Edit `adw_modules/agent.py` line 129 to change model:
- `model="sonnet"` - Faster, lower cost (default)
- `model="opus"` - Better for complex tasks

### Modular Architecture
The system uses a modular architecture with composable scripts:

- **State Management**: `ADWState` class enables chaining workflows via JSON piping
- **Git Operations**: Centralized git operations in `git_ops.py`  
- **Workflow Operations**: Core business logic in `workflow_ops.py`
- **Agent Integration**: Standardized Claude Code CLI interface in `agent.py`

### Script Chaining
Scripts can be chained using pipes to pass state:
```bash
# Chain planning and building
uv run adw_plan.py 123 | uv run adw_build.py

# Chain full pipeline
uv run adw_plan.py 123 | uv run adw_build.py | uv run adw_test.py

# Or use the convenience script
uv run adw_plan_build_test.py 123

# State is automatically passed between scripts
```

### Workflow Output Structure

Each ADW workflow creates an isolated workspace:

```
agents/
└── {adw_id}/                     # Unique workflow directory
    ├── adw_state.json            # Persistent state file
    ├── {adw_id}_plan_spec.md     # Implementation plan
    ├── planner/                  # Planning agent output
    │   └── raw_output.jsonl      # Claude Code session
    ├── implementor/              # Implementation agent output
    │   └── raw_output.jsonl
    ├── tester/                   # Test agent output
    │   └── raw_output.jsonl
    ├── reviewer/                 # Review agent output
    │   ├── raw_output.jsonl
    │   └── review_img/           # Screenshots directory
    ├── documenter/               # Documentation agent output
    │   └── raw_output.jsonl
    └── patch_*/                  # Patch resolution attempts

app_docs/                         # Generated documentation
└── features/
    └── {feature_name}/
        ├── overview.md
        ├── technical-guide.md
        └── images/
```

## Security Best Practices

- Store tokens as environment variables, never in code
- Use GitHub fine-grained tokens with minimal permissions
- Set up branch protection rules
- Require PR reviews for ADW changes
- Monitor API usage and set billing alerts

## Technical Details

### Core Components
- `adw_modules/agent.py` - Claude Code CLI integration
- `adw_modules/data_types.py` - Pydantic models for type safety
- `adw_modules/github.py` - GitHub API operations
- `adw_modules/git_ops.py` - Git operations (branching, commits, PRs)
- `adw_modules/state.py` - State management for workflow chaining
- `adw_modules/workflow_ops.py` - Core workflow operations (planning, building)
- `adw_modules/utils.py` - Utility functions
- `adw_plan.py` - Planning phase workflow
- `adw_build.py` - Implementation phase workflow
- `adw_test.py` - Testing phase workflow
- `adw_review.py` - Review phase workflow
- `adw_document.py` - Documentation phase workflow
- `adw_plan_build.py` - Main workflow orchestration (plan & build)
- `adw_plan_build_test.py` - Full pipeline orchestration (plan & build & test)
- `adw_plan_build_test_review.py` - Complete pipeline with review (plan & build & test & review)
- `adw_plan_build_review.py` - Pipeline with review, skipping tests (plan & build & review)
- `adw_plan_build_document.py` - Documentation pipeline, skipping tests and review (plan & build & document)
- `adw_sdlc.py` - Complete SDLC workflow (plan & build & test & review & document)

### Branch Naming
```
{type}-{issue_number}-{adw_id}-{slug}
```
Example: `feat-456-e5f6g7h8-add-user-authentication`
