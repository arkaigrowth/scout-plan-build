# Portability Guide - Scout Plan Build System

**Portability Score:** 85% (Highly Portable)
**Setup Time:** 15 minutes (minimal) to 2 hours (customized)

## Quick Start

| Goal | Action | Time |
|------|--------|------|
| **Quick Test** | `./scripts/port_to_new_repo.sh /tmp/test-repo` | 5 min |
| **Standard Setup** | Follow Minimal Setup below | 15 min |
| **Full Customization** | Follow Custom Setup section | 2 hrs |

## Prerequisites

- [ ] Git repository initialized with GitHub remote
- [ ] `gh` CLI installed and authenticated (`gh auth login`)
- [ ] `uv` installed (Python package manager)
- [ ] Python 3.10+ installed
- [ ] Anthropic API key obtained

---

## Portability Overview

| Component | Status | Notes |
|-----------|--------|-------|
| **Core Logic** | 100% Portable | No modifications needed |
| **Git Operations** | 100% Portable | Universal |
| **GitHub Integration** | 100% Portable | Works with any repo |
| **Workflow Scripts** | 95% Portable | Minor config needed |
| **Slash Commands** | 90% Portable | Flexible |
| **Path Validators** | 60% Portable | May need config file |

### What's Portable As-Is

**Core System:**
- `adws/adw_modules/` - All core modules
- `adws/adw_plan.py` - Planning workflow
- `adws/adw_build.py` - Build workflow
- `.claude/commands/` - All slash commands

### What Needs Configuration

- `.env` - API keys and repo URL
- Directory structure (or use `.adw_config.json`)
- Optional: Remove original repo checks in health_check.py

---

## 15-Minute Minimal Setup

### Step 1: Copy System Files (2 min)

```bash
SOURCE_DIR=/path/to/scout_plan_build_mvp
TARGET_DIR=/path/to/your/new-repo

# Copy core workflow system
cp -r $SOURCE_DIR/adws/ $TARGET_DIR/

# Copy slash commands
mkdir -p $TARGET_DIR/.claude
cp -r $SOURCE_DIR/.claude/commands/ $TARGET_DIR/.claude/

# Copy environment template
cp $SOURCE_DIR/.env.sample $TARGET_DIR/.env
```

### Step 2: Configure Environment (3 min)

Edit `.env` with your settings:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
GITHUB_REPO_URL=https://github.com/your-org/your-repo

# Recommended
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIR=true
```

### Step 3: Create Required Directories (1 min)

```bash
mkdir -p specs       # Implementation plans
mkdir -p agents      # Agent state and logs
mkdir -p ai_docs     # AI-generated documentation
```

### Step 4: Verify Installation (5 min)

```bash
source .env
uv run adws/adw_tests/health_check.py
```

### Step 5: Test Workflow (4 min)

```bash
# Create test issue
gh issue create --title "Test ADW Integration" --body "Testing the workflow"

# Run planning phase
uv run adws/adw_plan.py 1

# Verify results
ls -la specs/
git status
```

---

## 2-Hour Custom Setup

### Custom Directory Structure

If your repo uses different directories:

```json
// .adw_config.json
{
  "allowed_paths": [
    "planning/",
    "logs/",
    "documentation/",
    "src/"
  ],
  "specs_dir": "planning",
  "state_dir": "logs/adw",
  "docs_dir": "documentation"
}
```

Update `adws/adw_modules/validators.py` to load from config:

```python
import json
from pathlib import Path

def load_allowed_paths():
    config_file = Path(".adw_config.json")
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
            return config.get("allowed_paths", DEFAULT_PATHS)
    return DEFAULT_PATHS

DEFAULT_PATHS = ["specs/", "agents/", "ai_docs/", "docs/", "scripts/", "adws/"]
ALLOWED_PATH_PREFIXES = load_allowed_paths()
```

### Remove Original Repo Checks

In `adws/adw_tests/health_check.py`, around line 121:

```python
# Comment out or replace:
# is_disler_repo = "disler" in repo_path.lower()
is_disler_repo = False  # Disabled for new repo
```

### Custom Slash Commands

Create repo-specific commands in `.claude/commands/`:

```markdown
<!-- .claude/commands/your_command.md -->
# Your Custom Command

# Purpose
Description of what this command does.

# Variables
PARAM1: $1
PARAM2: $2

# Workflow
1. First step
2. Second step
3. Third step
```

---

## Common Issues and Solutions

### "Command not found: uv"
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "gh authentication failed"
```bash
gh auth login
gh auth status
```

### "ANTHROPIC_API_KEY not set"
```bash
source .env
# or
export $(cat .env | grep -v '^#' | xargs)
```

### "Path validation failed"
```bash
# Option 1: Use standard directories
mkdir -p specs agents ai_docs

# Option 2: Create config file
cat > .adw_config.json << 'EOF'
{"allowed_paths": ["your/", "custom/", "paths/"]}
EOF
```

### "Plan file not found"
```bash
ls -la specs/
cat agents/*/adw_state.json | jq .
```

---

## Verification Checklist

### Core Functionality
- [ ] Health check passes
- [ ] Can create GitHub issue
- [ ] Can run planning phase
- [ ] Plan file created in correct location
- [ ] Git branch created and committed

### Git Operations
- [ ] Branch creation works
- [ ] Commits have proper messages
- [ ] Can push to remote

### File System
- [ ] State files saved correctly
- [ ] Logs generated in proper location
- [ ] All paths validated properly

---

## Advanced Configuration

### Multi-Language Support

```python
# adws/adw_modules/language_config.py
LANGUAGE_CONFIGS = {
    "python": {"test_framework": "pytest", "linter": "ruff"},
    "typescript": {"test_framework": "jest", "linter": "eslint"},
    "rust": {"test_framework": "cargo test", "linter": "clippy"},
}
```

### Monorepo Support

```bash
export ADW_WORKSPACE=packages/your-package
```

```json
{
  "workspace": "packages/your-package",
  "allowed_paths": ["packages/your-package/specs/", "packages/your-package/src/"]
}
```

### Integration Adapters

For non-GitHub issue trackers (Jira, GitLab):

```python
# adws/adw_modules/integrations/jira.py
if os.getenv("ISSUE_PROVIDER") == "jira":
    from adw_modules.integrations.jira import fetch_jira_issue as fetch_issue
else:
    from adw_modules.github import fetch_issue
```

---

## Debugging

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

**Automated Setup:**
```bash
./scripts/port_to_new_repo.sh /path/to/new/repo
```

---

*Consolidated from PORTABILITY_INDEX.md, PORTABILITY_SUMMARY.md, and QUICK_PORT_GUIDE.md*
