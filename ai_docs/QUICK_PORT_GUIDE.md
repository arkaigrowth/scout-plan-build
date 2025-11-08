# Quick Port Guide - Scout Plan Build to New Repository

**Time Required:** 15 minutes (minimal) to 2 hours (customized)

## Prerequisites Checklist

- [ ] Git repository initialized with GitHub remote
- [ ] `gh` CLI installed and authenticated (`gh auth login`)
- [ ] `uv` installed (Python package manager)
- [ ] Python 3.10+ installed
- [ ] Anthropic API key obtained

---

## 15-Minute Minimal Setup

### Step 1: Copy System Files (2 minutes)

```bash
# From scout_plan_build_mvp directory
SOURCE_DIR=/Users/alexkamysz/AI/scout_plan_build_mvp
TARGET_DIR=/path/to/your/new-repo

# Copy core workflow system
cp -r $SOURCE_DIR/adws/ $TARGET_DIR/

# Copy slash commands
mkdir -p $TARGET_DIR/.claude
cp -r $SOURCE_DIR/.claude/commands/ $TARGET_DIR/.claude/

# Copy environment template
cp $SOURCE_DIR/.env.sample $TARGET_DIR/.env

# Copy documentation (optional)
cp $SOURCE_DIR/ai_docs/PORTABILITY_ANALYSIS.md $TARGET_DIR/docs/
```

### Step 2: Configure Environment (3 minutes)

```bash
cd $TARGET_DIR

# Edit .env file
nano .env
```

**Required settings:**
```bash
# Your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# Your GitHub repository
GITHUB_REPO_URL=https://github.com/your-org/your-repo

# Claude Code configuration
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=true

# Claude Code path (if not in PATH)
CLAUDE_CODE_PATH=claude  # or /full/path/to/claude
```

### Step 3: Create Required Directories (1 minute)

```bash
# Create standard directory structure
mkdir -p specs       # Implementation plans
mkdir -p agents      # Agent state and logs (auto-created)
mkdir -p ai_docs     # AI-generated documentation
```

### Step 4: Verify Installation (5 minutes)

```bash
# Load environment
source .env  # or: export $(cat .env | xargs)

# Run health check
uv run adws/adw_tests/health_check.py

# Expected output:
# ✅ Claude Code CLI found
# ✅ GitHub CLI authenticated
# ✅ Git repository detected
# ✅ All required environment variables set
```

### Step 5: Test Basic Workflow (4 minutes)

```bash
# Create a test GitHub issue first (via web UI or gh CLI):
gh issue create --title "Test ADW Integration" --body "Testing the workflow system"

# Get the issue number (e.g., #1)
ISSUE_NUMBER=1

# Run planning phase
uv run adws/adw_plan.py $ISSUE_NUMBER

# Check results
ls -la specs/  # Should see plan file
git status     # Should see new branch and committed plan
```

**Done!** Your system is operational.

---

## 2-Hour Custom Setup

### Additional Configuration Options

#### Option 1: Custom Directory Structure

If your repo uses different directories:

```bash
# Your structure:
# new-repo/
# ├── planning/      # Instead of specs/
# ├── logs/          # Instead of agents/
# └── documentation/ # Instead of ai_docs/

# Create configuration file
cat > .adw_config.json << 'EOF'
{
  "allowed_paths": [
    "planning/",
    "logs/",
    "documentation/",
    "src/",
    "tests/"
  ],
  "specs_dir": "planning",
  "state_dir": "logs/adw",
  "scout_output_dir": "logs/scout",
  "docs_dir": "documentation"
}
EOF

# Update validators.py to use config
nano adws/adw_modules/validators.py
```

**In validators.py**, replace lines 30-38:
```python
# OLD:
ALLOWED_PATH_PREFIXES = [
    "specs/",
    "agents/",
    "ai_docs/",
    ...
]

# NEW:
import json
from pathlib import Path

def load_allowed_paths():
    config_file = Path(".adw_config.json")
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
            return config.get("allowed_paths", DEFAULT_PATHS)
    return DEFAULT_PATHS

DEFAULT_PATHS = ["specs/", "agents/", "ai_docs/", "docs/", "scripts/", "adws/", "app/"]
ALLOWED_PATH_PREFIXES = load_allowed_paths()
```

#### Option 2: Remove Original Repo Checks

```bash
# Edit health check to remove disler-specific warnings
nano adws/adw_tests/health_check.py

# Find and remove/comment out (around line 121):
# is_disler_repo = "disler" in repo_path.lower()
# Replace with:
is_disler_repo = False  # Disabled for new repo
```

#### Option 3: Customize Memory Hooks

```bash
# If using memory system, update project name
nano adws/adw_modules/memory_hooks.py

# Update project identifier to match your repo:
# OLD: "project_scout_mvp"
# NEW: "project_tax_prep" (or whatever your repo name is)
```

#### Option 4: Add Custom Slash Commands

```bash
# Create repo-specific commands
cd .claude/commands

# Example: Tax-specific command
cat > tax_calculation.md << 'EOF'
# Tax Calculation Command

# Purpose
Implement tax calculation logic with IRS compliance validation.

# Variables
TAX_YEAR: $1
FILING_STATUS: $2
INCOME_DATA: $3

# Workflow
1. Validate tax year and filing status
2. Load IRS tax brackets for specified year
3. Calculate federal tax liability
4. Apply credits and deductions
5. Generate compliance report
6. Create test cases for edge cases

# Output
- Path to implementation plan
EOF
```

---

## Common Issues and Solutions

### Issue 1: "Command not found: uv"

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with homebrew
brew install uv
```

### Issue 2: "gh authentication failed"

```bash
# Re-authenticate with GitHub
gh auth login

# Verify authentication
gh auth status
```

### Issue 3: "ANTHROPIC_API_KEY not set"

```bash
# Verify .env is loaded
echo $ANTHROPIC_API_KEY

# If empty, load it:
export $(cat .env | grep -v '^#' | xargs)

# Or source it
source .env
```

### Issue 4: "No permission to create branch"

```bash
# Check git remote
git remote -v

# Ensure you have write access to the repository
gh repo view  # Should show your repo details
```

### Issue 5: "Path validation failed"

```bash
# Check allowed paths in validators.py
grep -A10 "ALLOWED_PATH_PREFIXES" adws/adw_modules/validators.py

# Either:
# 1. Use standard directories (specs/, agents/, ai_docs/)
# 2. Create .adw_config.json with your paths
# 3. Modify ALLOWED_PATH_PREFIXES directly
```

### Issue 6: "Plan file not found"

```bash
# Check plan was created
ls -la specs/

# Verify state file
cat agents/*/adw_state.json | jq .

# Manually specify plan file if needed
uv run adws/adw_build.py $ISSUE_NUMBER $ADW_ID
```

---

## Verification Checklist

After setup, verify these work:

### Core Functionality
- [ ] Health check passes
- [ ] Can create GitHub issue
- [ ] Can run planning phase
- [ ] Plan file created in correct location
- [ ] Git branch created
- [ ] Changes committed
- [ ] Can run build phase
- [ ] State persists between phases

### Git Operations
- [ ] Branch creation works
- [ ] Commits have proper messages
- [ ] Can push to remote
- [ ] Pull request creation works (if configured)

### GitHub Integration
- [ ] Can fetch issues
- [ ] Can post comments
- [ ] Issue classification works
- [ ] Branch names generated correctly

### File System
- [ ] State files saved correctly
- [ ] Logs generated in proper location
- [ ] Scout output saved
- [ ] All paths validated properly

---

## Next Steps

### 1. Customize for Your Domain

```bash
# Add domain-specific slash commands
cd .claude/commands

# Example for tax-prep:
# - /tax_validation.md
# - /irs_compliance.md
# - /audit_trail.md
```

### 2. Configure Agent Personas

```bash
# Create specialized agents
nano .claude/commands/implement.md

# Customize for your tech stack:
# - Python/Django for tax-prep
# - React for frontend
# - PostgreSQL for database
```

### 3. Set Up Continuous Integration

```bash
# Add GitHub Actions workflow
mkdir -p .github/workflows
cat > .github/workflows/adw.yml << 'EOF'
name: ADW Workflow
on:
  issues:
    types: [opened, labeled]
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: uv run adws/adw_plan.py ${{ github.event.issue.number }}
EOF
```

### 4. Add Monitoring

```bash
# Track workflow success rate
cat > scripts/adw_metrics.sh << 'EOF'
#!/bin/bash
# Count successful vs failed workflows
echo "=== ADW Metrics ==="
echo "Plans created: $(ls specs/*.md | wc -l)"
echo "Builds completed: $(find agents -name 'execution.log' | wc -l)"
echo "Active branches: $(git branch | grep 'feature\|bug\|chore' | wc -l)"
EOF

chmod +x scripts/adw_metrics.sh
```

---

## Advanced Customization

### Multi-Language Support

```python
# adws/adw_modules/language_config.py
LANGUAGE_CONFIGS = {
    "python": {
        "test_framework": "pytest",
        "linter": "ruff",
        "formatter": "black",
    },
    "typescript": {
        "test_framework": "jest",
        "linter": "eslint",
        "formatter": "prettier",
    },
    "rust": {
        "test_framework": "cargo test",
        "linter": "clippy",
        "formatter": "rustfmt",
    }
}

def get_language_config(project_path):
    """Auto-detect language and return config."""
    # Check for language indicators
    if Path(project_path / "Cargo.toml").exists():
        return LANGUAGE_CONFIGS["rust"]
    elif Path(project_path / "package.json").exists():
        return LANGUAGE_CONFIGS["typescript"]
    else:
        return LANGUAGE_CONFIGS["python"]
```

### Monorepo Support

```bash
# Set workspace subdirectory
export ADW_WORKSPACE=packages/tax-prep

# Update config to prepend workspace
# In .adw_config.json:
{
  "workspace": "packages/tax-prep",
  "allowed_paths": [
    "packages/tax-prep/specs/",
    "packages/tax-prep/src/"
  ]
}
```

### Custom Integrations

```python
# adws/adw_modules/integrations/jira.py
"""JIRA integration for issue tracking."""

def fetch_jira_issue(issue_key: str) -> Issue:
    """Fetch JIRA issue instead of GitHub."""
    # Implementation here
    pass

# Use in adw_plan.py:
if os.getenv("ISSUE_PROVIDER") == "jira":
    from adw_modules.integrations.jira import fetch_jira_issue as fetch_issue
else:
    from adw_modules.github import fetch_issue
```

---

## Support Resources

### Documentation
- `ai_docs/PORTABILITY_ANALYSIS.md` - Detailed portability analysis
- `CLAUDE.md` - System instructions and patterns
- `docs/WORKFLOW_ARCHITECTURE.md` - Architecture overview

### Testing
```bash
# Run full test suite
uv run pytest adws/adw_tests/

# Run specific tests
uv run pytest adws/adw_tests/test_validators.py
uv run pytest adws/adw_tests/test_agents.py
```

### Debugging
```bash
# Enable debug logging
export ANTHROPIC_LOG=debug

# Check agent logs
tail -f agents/*/*/execution.log

# Validate state
cat agents/*/adw_state.json | jq .

# Check git status
git log --oneline --graph --all
```

---

## Summary

**Minimal Setup** (15 min):
1. Copy files: `adws/`, `.claude/commands/`
2. Create `.env` with API keys and repo URL
3. Create directories: `specs/`, `agents/`, `ai_docs/`
4. Run health check
5. Test with sample issue

**Custom Setup** (2 hours):
1. Complete minimal setup
2. Create `.adw_config.json` for custom paths
3. Update validators for custom structure
4. Remove original repo checks
5. Add domain-specific commands
6. Test full workflow

**Result**: Fully functional AI developer workflow system customized for your repository!
