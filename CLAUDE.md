# Scout Plan Build MVP - Agent Instructions v3

**Your role:** Execute Scout→Plan→Build workflows using **working** patterns and tools.

## ⚠️ CRITICAL: What Actually Works vs. What's Documented

### ❌ Tools That DON'T Exist (Don't Use)
- `gemini` command - Not installed
- `opencode` command - Not installed
- `codex` command - Not installed
- External tools in scout commands - Will fail

### ✅ Tools That DO Work (Use These)
- `Task` tool with subagents (explore, python-expert, etc.)
- Native Claude Code tools (Read, Grep, Glob, Bash)
- `gh` CLI for GitHub operations
- `claude` command (when called correctly)

## 🚀 Quick Start (Verified Working)

### Environment Setup (REQUIRED)
```bash
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768  # Prevents token limit errors
export ANTHROPIC_API_KEY="sk-ant-..."      # Your actual key
export GITHUB_PAT="ghp_..."                # For GitHub operations
export GITHUB_REPO_URL="https://github.com/owner/repo"
```

### Working Workflow (Use This)

```bash
# 1. Scout - Use Task agents, NOT external tools
# Instead of: /scout "task" "4"
# Use native exploration:
Task(subagent_type="explore", prompt="Find files for: [task]")

# 2. Plan - This works as documented
/plan_w_docs "[TASK]" "[DOCS_URL]" "scout_outputs/relevant_files.json"
# Returns: specs/issue-{N}-adw-{ID}-{slug}.md

# 3. Build - This works as documented
/build_adw "specs/[plan-file].md"
# Returns: ai_docs/build_reports/{slug}-build-report.md

# 4. Git Operations - Manual but reliable
git checkout -b feature/issue-NNN-adw-XXX
git add .
git commit -m "feat: description"
git push origin feature/...

# 5. PR Creation - Works with gh CLI
gh pr create --title "Title" --body "Description"
```

### 🚄 Parallel Execution (NEW - 40-50% Faster!)

```bash
# Run complete SDLC with parallel Test+Review+Document
uv run adws/adw_sdlc.py <issue> <adw-id> --parallel

# What happens:
# 1. Plan (sequential) - 2-3 min
# 2. Build (sequential) - 3-4 min
# 3. Test + Review + Document (PARALLEL) - 3-4 min instead of 7-10 min
# 4. Single aggregated commit - avoids git conflicts

# Total time: 8-11 min instead of 12-17 min (40-50% speedup!)
```

**Implementation**: Simple 30-line subprocess.Popen() solution with --no-commit flags
**Lesson Learned**: We initially designed 150+ lines of async code. User feedback ("Are we overengineering?") led to this simple solution that delivers the same value.

## 📊 System Architecture (Reality Check)

```
What the Docs Say                     What Actually Happens
─────────────────                     ─────────────────────
/scout → external tools      ❌        /scout → tools fail → partial results
/plan → perfect spec         ⚠️        /plan → decent spec (needs validation)
/build → flawless code       ⚠️        /build → good code (needs testing)
/pr → automatic merge        ❌        /pr → creates PR (human reviews)
```

## 🔧 Common Issues & Solutions

### Issue 1: Scout Commands Fail
**Problem**: `/scout` tries to use gemini/opencode/codex that don't exist
**Solution**: Use Task agents instead:
```python
# Don't use slash command for scout
# Instead, use Task directly:
Task(
    subagent_type="explore",
    prompt="Find all files related to authentication, focusing on: routes, middleware, tests"
)
```

### Issue 2: Token Limit Errors
**Problem**: Subagents fail with 8192 token limit
**Solution**: Environment variable is set (already fixed in utils.py)
```bash
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
```

### Issue 3: Git Operations on Main
**Problem**: Accidentally working on main branch
**Solution**: ALWAYS create feature branch first
```bash
git checkout -b feature/issue-NNN-adw-XXX  # Do this FIRST
```

## 📁 File Organization (ENFORCED)

| Content Type | Location | Why |
|-------------|----------|-----|
| Scout results | `scout_outputs/relevant_files.json` | Standard location for plan phase |
| Plans/Specs | `specs/issue-NNN-adw-XXX-slug.md` | Versioned, trackable |
| Build reports | `ai_docs/build_reports/` | AI-generated documentation |
| Code changes | Feature branch only | Never on main/master |
| Reviews | `ai_docs/reviews/` | Post-build analysis |

## 🎯 Best Practices Workflow

### 1. Parallel Scout (Working Method)
```python
# Launch multiple explore agents in parallel
agents = [
    Task(subagent_type="explore", prompt=f"Find files for: {task} - focus on {aspect}")
    for aspect in ["models", "routes", "tests", "config"]
]
# Combine results into relevant_files.json
```

### 2. Validated Planning
```python
# After creating spec, validate it
spec = Read("specs/issue-001-adw-xxx.md")
validate_spec(spec)  # Check schema v1.1.0
```

### 3. Parallel Building (When Possible)
```python
# If tasks are independent, parallelize
independent_tasks = identify_independent_tasks(spec)
Task.run_parallel(independent_tasks)
```

### 4. Proper Git Flow
```bash
# ALWAYS follow this order
git status                         # Check current state
git checkout -b feature/...        # Create feature branch
# ... make changes ...
git add .                          # Stage changes
git diff --cached                  # Review what's staged
git commit -m "type: description"  # Semantic commit
git push origin feature/...        # Push to remote
gh pr create                       # Create PR
```

## ⚠️ Safety Rules (CRITICAL)

1. **Git Safety**:
   ```bash
   # After any scout operation
   git diff --stat     # Check for unwanted changes
   git reset --hard    # Reset if needed
   ```

2. **Branch Protection**:
   ```bash
   # NEVER do this on main/master
   if [[ $(git branch --show-current) == "main" ]]; then
     echo "ERROR: On main branch!"
     exit 1
   fi
   ```

3. **Validation First**:
   - Validate all inputs with Pydantic models (✅ implemented)
   - Check paths for traversal attempts (✅ implemented)
   - Sanitize commit messages (✅ implemented)

## 📊 Current System State (Honest Assessment)

| Component | Status | Reality |
|-----------|--------|---------|
| **Security** | ✅ 100% | Fixed with Pydantic validation |
| **Error Handling** | ✅ 90% | Structured exceptions implemented |
| **Scout Phase** | ⚠️ 40% | External tools don't work |
| **Plan Phase** | ✅ 80% | Works well with validation |
| **Build Phase** | ✅ 70% | Decent but needs testing |
| **Parallel Execution** | ✅ 100% | Test+Review+Document run in parallel (40-50% speedup) |
| **Agent Memory** | ❌ 0% | Completely stateless |
| **GitHub Integration** | ✅ 60% | Manual but functional |

## 🚀 Recommended Execution Pattern

For any new task, follow this pattern:

```python
# 1. Check environment
assert os.getenv("CLAUDE_CODE_MAX_OUTPUT_TOKENS") == "32768"
assert os.getenv("ANTHROPIC_API_KEY")
assert os.getenv("GITHUB_PAT")

# 2. Scout with working methods
results = Task(subagent_type="explore", prompt=task)
Write("scout_outputs/relevant_files.json", results)

# 3. Plan with validation
plan = SlashCommand("/plan_w_docs ...")
validate_spec(plan)

# 4. Build with safety
git_checkout_new_branch()
build_result = SlashCommand("/build_adw ...")
run_tests()

# 5. Push with review
git_push()
create_pr()
```

## 🎓 Learning Points

### Why Scout Fails
The scout commands assume external tools (gemini, opencode) that aren't part of the standard Claude Code environment. This is a **deployment assumption error** - the code assumes a specific environment that doesn't exist.

### Why Sequential is Bad
Current workflow: Scout (3min) → Plan (2min) → Build (5min) = 10min total
Parallel workflow: Scout + Plan + Build concurrent = 5min total (2x faster!)

### Why Memory Matters
Without memory, every agent call:
- Rediscovers the same patterns
- Repeats the same analysis
- Can't learn from failures
- Wastes tokens and time

## 📚 Key References (Accurate)

| Document | Purpose | Trust Level |
|----------|---------|-------------|
| `docs/WORKFLOW_ARCHITECTURE.md` | How it REALLY works | ✅ 100% Accurate |
| `docs/SPEC_SCHEMA.md` | Spec validation rules | ✅ 100% Accurate |
| `ai_docs/architecture/AGENTS_SDK_ARCHITECTURE.md` | Future architecture | 📝 Planned |
| Original `/scout` commands | External tool usage | ❌ Broken |

## 🔄 Migration Guide

### From Old Instructions → New Reality

| Old Way | New Way | Why |
|---------|---------|-----|
| `/scout` with external tools | `Task` with explore agent | Tools don't exist |
| Trust the workflow | Validate at each step | Catches failures early |
| Sequential execution | Parallel where possible | 2-3x faster |
| Assume success | Check git diff after scout | Prevents corruption |
| Follow docs blindly | Check reality first | Docs often outdated |

---

**Remember**: This v3 reflects **what actually works** as of 2025-01-20. The system is functional but needs the Agents SDK implementation to reach its potential. Always verify tool availability before using slash commands that depend on external tools.