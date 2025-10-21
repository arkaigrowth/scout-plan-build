# Scout Plan Build MVP - Agent Instructions v2

**Your role:** Execute Scout→Plan→Build workflows using established patterns and conventions.

## 🚀 Quick Start

### Environment Setup (REQUIRED)
```bash
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768  # Prevents token limit errors
export ANTHROPIC_API_KEY="your-key-here"
export GITHUB_REPO_URL="https://github.com/owner/repo"
```

### Core Workflow
```bash
# 1. Scout - Find relevant files
/scout "[TASK]" "4"  # Returns: agents/scout_files/relevant_files.json

# 2. Plan - Generate implementation plan
/plan_w_docs "[TASK]" "[DOCS_URL]" "agents/scout_files/relevant_files.json"
# Returns: specs/issue-{N}-adw-{ID}-{slug}.md

# 3. Build - Implement the plan
/build_adw "specs/[plan-file].md"
# Returns: ai_docs/build_reports/{slug}-build-report.md
```

## 📁 File Organization (STRICT)

**ALWAYS** place files in these locations:

| Content Type | Location | Example |
|-------------|----------|---------|
| Scout results | `agents/scout_files/` | `relevant_files.json` |
| Plans/Specs | `specs/` | `issue-001-adw-ext001-feature.md` |
| Build reports | `ai_docs/build_reports/` | `feature-build-report.md` |
| Reviews | `ai_docs/reviews/` | `feature-review.md` |
| AI analyses | `ai_docs/analyses/` | `ENGINEERING_ASSESSMENT.md` |
| Reference docs | `ai_docs/reference/` | `REPOSITORY_REFERENCE.md` |
| Architecture | `ai_docs/architecture/` | `ARCHITECTURE_INSIGHTS.md` |
| Human docs | `docs/` | Manual documentation only |

## 🔧 Common Tasks

### Fix Token Limit Errors
```bash
# Add to utils.py line 181:
"CLAUDE_CODE_MAX_OUTPUT_TOKENS": os.getenv("CLAUDE_CODE_MAX_OUTPUT_TOKENS", "32768"),
```

### Run Analysis
```bash
/sc:analyze  # Comprehensive code analysis
```

### Create Feature Plan
```bash
/feature "[description]"  # Generates plan in specs/
```

### Check Repository State
```bash
git status && git branch  # Always start here
ls -la ai_docs/          # Check existing analyses
cat TODO.md              # Review pending tasks
```

## ⚠️ Safety Rules

1. **No git operations on main/master** - Always use feature branches
2. **Check before modifying** - Read files before editing
3. **Git safety after scout** - Run `git diff --stat` then `git reset --hard` if needed
4. **Use subprocess safely** - Never use `shell=True`
5. **Validate paths** - Check for path traversal attempts

## 📊 Current System State

- **Architecture**: Modular ADW system (28 Python files, ~5,873 LOC)
- **Type Coverage**: ~60% (Pydantic in data_types.py)
- **Test Coverage**: ~30% (needs improvement)
- **Key Gaps**: Rate limiting, retry logic, parallelization
- **Production Ready**: 70% - needs 1 week hardening

## 🎯 Priority Tasks

1. **Input Validation** - Add Pydantic to workflow_ops.py
2. **Error Handling** - Structured exceptions, not generic
3. **Token Limits** - Already fixed via environment variable
4. **File Organization** - Use conventions above strictly
5. **Documentation** - Update ai_docs/ANALYSIS_INDEX.md when adding docs

## 📚 Key References

- `ai_docs/ANALYSIS_INDEX.md` - Index of all analyses
- `ai_docs/reference/REPOSITORY_REFERENCE.md` - Complete codebase reference
- `ai_docs/analyses/ENGINEERING_ASSESSMENT.md` - Engineering recommendations
- `specs/issue-001-adw-ext001-*` - External tools feature plan
- `TODO.md` - Development task tracking

## 🔄 Handoff Notes

**What's been done:**
- Comprehensive repository analysis complete
- Token limit issue fixed in code and environment
- File organization cleaned up and documented
- External tools feature planned
- Engineering assessment with ship-ready recommendations

**Next agent should:**
1. Implement input validation fixes (Priority 1)
2. Add structured error handling
3. Follow file organization strictly
4. Update ANALYSIS_INDEX.md with new docs
5. Check TODO.md for pending tasks

---
*Context: 7% remaining. Use `/sc:analyze` for deep dives. Check ai_docs/ for existing analyses.*