# Scout Plan Build MVP - Complete Usage Guide
*Version 1.0 - November 2024*

## 🚀 Quick Start: Your First Feature

### Step 0: Environment Setup (One-time)
```bash
# Required environment variables
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_PAT="ghp_..."
export GITHUB_REPO_URL="https://github.com/owner/repo"

# Optional: Configure file organization
export ADW_OUTPUT_DIR="${PWD}/ai_docs/outputs"
export ADW_TIMESTAMP_FORMAT="%Y%m%d-%H%M%S"
```

### Step 1: Scout for Files (Use Task Tool)
```python
# ❌ DON'T USE: /scout "implement auth" "4"  # External tools don't exist!

# ✅ USE THIS: Task tool with explore agent
Task(
    subagent_type="explore",
    prompt="Find all files for implementing JWT authentication: routes, middleware, config, tests",
    description="Scout auth files"
)

# Output goes to: scout_outputs/relevant_files.json
```

### Step 2: Plan Your Feature
```bash
# Using slash command (recommended)
/plan_w_docs "Implement JWT authentication" "https://jwt.io/docs" "scout_outputs/relevant_files.json"

# Or using ADW directly
uv run adws/adw_plan.py 123 ADW-AUTH-001

# Output: specs/issue-123-adw-AUTH-001-jwt-auth.md
```

### Step 3: Build the Feature
```bash
# Using slash command
/build_adw "specs/issue-123-adw-AUTH-001-jwt-auth.md"

# Or using ADW directly
uv run adws/adw_build.py 123 ADW-AUTH-001

# Output: ai_docs/build_reports/jwt-auth-build-report.md
```

### Step 4: Run Complete SDLC (Parallel)
```bash
# 🚄 FASTEST: Run test+review+document in parallel (40-50% faster)
uv run adws/adw_sdlc.py 123 ADW-AUTH-001 --parallel

# Sequential (slower but safer)
uv run adws/adw_sdlc.py 123 ADW-AUTH-001
```

### Step 5: Git Operations
```bash
# Always work on feature branches
git checkout -b feature/issue-123-jwt-auth
git add .
git commit -m "feat: implement JWT authentication"
git push origin feature/issue-123-jwt-auth

# Create PR
gh pr create --title "feat: JWT authentication" --body "Implements #123"
```

---

## 🗂️ File Organization Best Practices

### Problem: Scout outputs are scattered everywhere!
Currently, files end up in multiple locations:
- Root directory (❌ messy)
- `scout_outputs/` (✅ good)
- `ai_docs/scout/` (⚠️ confusing)
- Random `MEOW_LOADER_*.md` files (❌ no context)

### Solution: Standardized Output Structure
```
ai_docs/
├── outputs/                    # All ADW outputs with timestamps
│   ├── 20241109-143052-auth/   # Timestamp + task name
│   │   ├── scout.json          # Scout results
│   │   ├── plan.md             # Plan/spec
│   │   ├── build-report.md     # Build output
│   │   ├── test-results.json   # Test results
│   │   └── review.md           # Code review
│   └── latest/                 # Symlink to most recent
├── build_reports/              # Legacy location (kept for compatibility)
└── reviews/                    # Legacy location (kept for compatibility)

scout_outputs/                  # Primary scout location
├── relevant_files.json        # Current scout results
└── ADW-{ID}/                  # ADW-specific outputs
    └── iteration-{N}.json      # Scout iterations

specs/                          # Plan specifications
└── issue-{N}-adw-{ID}-{slug}.md

agents/                         # Agent state and memory
└── {ADW-ID}/
    ├── adw_state.json         # Persistent state
    └── memory/                # Future: agent memory
```

### Implementing Better File Organization

```python
# In your scout operations, use timestamped directories
from datetime import datetime

def organize_scout_output(task_name: str, output_data: dict):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = f"ai_docs/outputs/{timestamp}-{task_name}"

    # Create directory
    os.makedirs(output_dir, exist_ok=True)

    # Save with context
    with open(f"{output_dir}/scout.json", "w") as f:
        json.dump({
            "timestamp": timestamp,
            "task": task_name,
            "data": output_data
        }, f, indent=2)

    # Update latest symlink
    latest = "ai_docs/outputs/latest"
    if os.path.exists(latest):
        os.unlink(latest)
    os.symlink(output_dir, latest)
```

---

## 🔄 Git Worktree Integration (Advanced)

### What Are Git Worktrees?
Git worktrees allow multiple branches to be checked out simultaneously in different directories. Perfect for parallel development!

### Setting Up Worktrees
```bash
# Create a worktree for your feature
./scripts/worktree_manager.sh create jwt-auth main

# This creates:
# - worktrees/jwt-auth/ (separate working directory)
# - feature/jwt-auth branch
# - Auto-checkpoint every 5 minutes
# - Undo/redo capability

# Switch to the worktree
./scripts/worktree_manager.sh switch jwt-auth
```

### Parallel Development with Worktrees
```bash
# Create multiple worktrees for parallel work
./scripts/worktree_manager.sh create auth-backend main
./scripts/worktree_manager.sh create auth-frontend main
./scripts/worktree_manager.sh create auth-tests main

# Work on each independently
cd worktrees/auth-backend && /build_adw "specs/backend.md"
cd worktrees/auth-frontend && /build_adw "specs/frontend.md"
cd worktrees/auth-tests && /build_adw "specs/tests.md"

# Compare changes
./scripts/worktree_manager.sh diff auth-backend auth-frontend

# Merge when ready
./scripts/worktree_manager.sh merge auth-backend main
```

### Undo/Redo System
```bash
# Auto-checkpoint every 5 minutes (automatic)
# Or manual checkpoint
./scripts/worktree_manager.sh checkpoint "implemented login endpoint"

# Undo last 3 changes
./scripts/worktree_manager.sh undo 3

# Redo if you change your mind
./scripts/worktree_manager.sh redo

# View checkpoint history
git log --oneline --grep="^wip-"
```

---

## 🏃 End-to-End Workflow Examples

### Example 1: Simple Feature Addition
```bash
# 1. Scout for relevant files
claude> Task(subagent_type="explore", prompt="Find files for adding user profile page")

# 2. Create plan
claude> /plan_w_docs "Add user profile page" "" "scout_outputs/relevant_files.json"

# 3. Build feature
claude> /build_adw "specs/issue-001-adw-PROFILE-001-user-profile.md"

# 4. Test and review
claude> uv run adws/adw_test.py 001 PROFILE-001
claude> uv run adws/adw_review.py 001 PROFILE-001

# 5. Commit and push
claude> git checkout -b feature/user-profile
claude> git add . && git commit -m "feat: add user profile page"
claude> git push origin feature/user-profile
claude> gh pr create
```

### Example 2: Complex Feature with Parallel Execution
```bash
# 1. Scout multiple aspects in parallel
claude> Task(subagent_type="explore", prompt="Find auth models")
claude> Task(subagent_type="explore", prompt="Find auth routes")
claude> Task(subagent_type="explore", prompt="Find auth tests")

# 2. Combine scout results
cat scout_outputs/*.json | jq -s 'add' > scout_outputs/relevant_files.json

# 3. Plan comprehensive feature
/plan_w_docs "Complete auth system overhaul" "https://auth0.com/docs" "scout_outputs/relevant_files.json"

# 4. Run complete SDLC with parallelization
uv run adws/adw_sdlc.py 002 AUTH-OVERHAUL --parallel

# Time savings: 8-11 min instead of 12-17 min!
```

### Example 3: Using Worktrees for Experimentation
```bash
# Create experimental branch
./scripts/worktree_manager.sh create experiment-graphql main

# Try implementation
cd worktrees/experiment-graphql
/build_adw "specs/graphql-api.md"

# If it doesn't work, undo
./scripts/worktree_manager.sh undo 5

# Or if it works, merge
./scripts/worktree_manager.sh merge experiment-graphql main
```

---

## 🔌 Bitbucket Integration

### Current Status
- **GitHub**: ✅ Fully supported via `gh` CLI
- **Bitbucket**: ⚠️ Manual process (no direct CLI support)

### Bitbucket Workflow
```bash
# 1. Use standard git operations
git remote add bitbucket https://bitbucket.org/team/repo.git
git checkout -b feature/issue-123
# ... make changes ...
git push bitbucket feature/issue-123

# 2. Create PR manually via web UI
# Or use Bitbucket API:
curl -X POST https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests \
  -H "Authorization: Bearer $BITBUCKET_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Feature: JWT Auth",
    "source": {"branch": {"name": "feature/issue-123"}},
    "destination": {"branch": {"name": "main"}}
  }'
```

### Future Bitbucket Support
```python
# Planned implementation in adw_modules/vcs_ops.py
class BitbucketOps:
    def create_pr(self, title: str, body: str, branch: str):
        """Create Bitbucket pull request via API"""
        # Implementation pending
        pass
```

---

## ⚠️ Common Pitfalls & Solutions

### Pitfall 1: Scout Output Confusion
**Problem**: "Where did my scout results go?"
**Solution**: Always check these locations in order:
1. `scout_outputs/relevant_files.json` (primary)
2. `ai_docs/outputs/latest/scout.json` (if using new structure)
3. `ai_docs/scout/relevant_files.json` (legacy)

### Pitfall 2: Working on Main Branch
**Problem**: Accidentally modifying main/master
**Solution**: Add this to your `.bashrc`:
```bash
git() {
    if [[ "$1" == "commit" ]] && [[ $(command git branch --show-current) == "main" ]]; then
        echo "❌ ERROR: Cannot commit to main branch!"
        return 1
    fi
    command git "$@"
}
```

### Pitfall 3: Token Limit Errors
**Problem**: Agents fail with 8192 token limit
**Solution**: Already fixed, but verify:
```bash
echo $CLAUDE_CODE_MAX_OUTPUT_TOKENS  # Should be 32768
```

### Pitfall 4: External Tools Not Found
**Problem**: `/scout` fails with "command not found: gemini"
**Solution**: Use Task tool instead of slash commands for scouting

---

## 📊 Performance Benchmarks

| Operation | Sequential | Parallel | Speedup |
|-----------|------------|----------|---------|
| Scout (multiple aspects) | 3-4 min | 1-2 min | 2x |
| Test + Review + Document | 7-10 min | 3-4 min | 2.3x |
| Complete SDLC | 12-17 min | 8-11 min | 1.5x |
| Multi-feature build | 30 min | 10 min | 3x |

---

## 🎯 Best Practices Summary

1. **Always Use Feature Branches**: Never work on main/master
2. **Timestamp Your Outputs**: Include date/time in filenames
3. **Parallelize When Possible**: Use `--parallel` flag for 40-50% speedup
4. **Validate Before Building**: Check specs match schema v1.1.0
5. **Use Task Tool for Scouting**: Don't rely on external tools
6. **Checkpoint Regularly**: Use worktrees for undo capability
7. **Clean Up After Yourself**: Remove temp files and failed experiments

---

## 📚 Additional Resources

- **Architecture**: `ai_docs/ADW_SYSTEM_ANALYSIS.md`
- **Quick Reference**: `ai_docs/ADW_QUICK_REFERENCE.md`
- **Worktree Details**: `ai_docs/architecture/GIT_WORKTREE_UNDO_SYSTEM.md`
- **Spec Schema**: `docs/SPEC_SCHEMA.md`
- **Workflow Patterns**: `docs/WORKFLOW_ARCHITECTURE.md`

---

## 🚦 Ready to Start?

1. ✅ Environment variables set
2. ✅ On a feature branch
3. ✅ Scout outputs directory exists
4. ✅ ADW tools available (`uv` installed)

**Your first command:**
```python
Task(subagent_type="explore", prompt="Find files for: [your task here]")
```

Good luck! 🎉