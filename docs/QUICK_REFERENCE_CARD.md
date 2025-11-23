# Scout Plan Build - Quick Reference Card
*Print this and keep it handy!*

## 🚀 Essential Commands

### Starting a New Feature
```bash
# 1. Create feature branch (ALWAYS FIRST!)
git checkout -b feature/issue-XXX-description

# 2. Scout for files
Task(subagent_type="explore", prompt="Find files for: [your feature]")

# 3. Create plan
/plan_w_docs "[feature description]" "[docs-url]" "scout_outputs/relevant_files.json"

# 4. Build with parallel testing (FASTEST!)
uv run adws/adw_sdlc.py [issue] [adw-id] --parallel

# 5. Push and create PR
git push origin feature/issue-XXX-description
gh pr create --title "feat: description" --body "Implements #XXX"
```

## ⚡ Speed Tips

| Task | Slow Way | Fast Way | Time Saved |
|------|----------|----------|------------|
| Scout | `/scout` (broken) | `Task(explore)` | Actually works |
| Test+Review | Sequential | `--parallel` flag | 40-50% |
| Multiple files | Edit one by one | MultiEdit | 70% |

## 📁 Where Things Live

```
scout_outputs/relevant_files.json   ← Current scout results
specs/issue-XXX-adw-YYY.md         ← Plans go here
ai_docs/build_reports/              ← Build outputs
ai_docs/outputs/latest/             ← Most recent task outputs
agents/ADW-ID/adw_state.json       ← Persistent state
```

## ⚠️ Common Fixes

| Problem | Solution |
|---------|----------|
| "Command not found: gemini" | Use `Task(explore)` instead of `/scout` |
| "Token limit exceeded" | Check: `echo $CLAUDE_CODE_MAX_OUTPUT_TOKENS` (should be 32768) |
| "Cannot commit to main" | Run: `git checkout -b feature/name` |
| "Scout results missing" | Check: `ls scout_outputs/` and `ai_docs/outputs/latest/` |
| "Build takes forever" | Add `--parallel` flag to adw_sdlc.py |

## 🔧 Environment Check

```bash
# Run this to verify setup:
echo "API Key: $(echo $ANTHROPIC_API_KEY | cut -c1-10)..."
echo "Tokens: $CLAUDE_CODE_MAX_OUTPUT_TOKENS"
echo "Branch: $(git branch --show-current)"
echo "Scout: $(ls scout_outputs/relevant_files.json 2>/dev/null || echo 'Missing')"
```

## 🎯 Workflow Patterns

### Simple Feature (5-8 min)
```bash
Task(explore) → /plan_w_docs → /build_adw → git push → gh pr create
```

### Complex Feature with Testing (8-11 min)
```bash
Task(explore) → /plan_w_docs → uv run adw_sdlc.py --parallel → gh pr create
```

### Experimental Feature (with undo)
```bash
./scripts/worktree_manager.sh create experiment main
cd worktrees/experiment
# Try stuff...
./scripts/worktree_manager.sh undo 3  # If it fails
./scripts/worktree_manager.sh merge experiment main  # If it works
```

## 🚄 Parallel Execution

```bash
# ALWAYS use for test/review/document:
uv run adws/adw_sdlc.py 123 ADW-001 --parallel

# What runs in parallel:
# - adw_test.py ─┐
# - adw_review.py ├─ All at once!
# - adw_document.py ─┘
```

## 💡 Pro Commands

```bash
# Clean up scattered files
uv run adws/adw_modules/file_organization.py setup

# Check worktree status
./scripts/worktree_manager.sh list

# Undo last 3 changes (worktree only)
./scripts/worktree_manager.sh undo 3

# See all ADW states
ls -la agents/*/adw_state.json

# Find latest outputs
ls -la ai_docs/outputs/latest/
```

## 📞 Getting Help

- **Docs**: `docs/TEAM_ONBOARDING_PRESENTATION.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING_AND_INTERNALS.md`
- **Quick Facts**: `ai_docs/ADW_QUICK_REFERENCE.md`
- **Architecture**: `ai_docs/ADW_SYSTEM_ANALYSIS.md`
- **Slack**: #ai-development
- **Issues**: GitHub Issues page

## ✅ Daily Checklist

- [ ] On feature branch (not main)
- [ ] Environment vars set
- [ ] Using `--parallel` for speed
- [ ] Scout outputs organized
- [ ] Tests passing before PR

---

*Framework Version: 1.0 | Updated: Nov 2024*