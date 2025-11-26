# Scout-Plan-Build Quick Reference

> One-page guide for installation, configuration, and troubleshooting

**Version**: 1.0.0 | **Updated**: 2025-11-25 | **Framework**: v2024.11.8

---

## 🚀 Quick Install

```bash
# One-liner installation (coming soon)
curl -sL https://raw.githubusercontent.com/arkaigrowth/scout-plan-build/main/install.sh | bash -s /path/to/target

# Manual installation
git clone https://github.com/arkaigrowth/scout-plan-build.git
cd scout-plan-build
python scripts/install_framework.py /path/to/target --full
```

**Options**:
- `--minimal` - Commands only, no hooks/skills
- `--full` - Everything (default)
- `--dry-run` - Preview without installation

---

## 🔑 Environment Variables

| Variable | Required | Purpose | Example |
|----------|----------|---------|---------|
| `ANTHROPIC_API_KEY` | ✅ | Claude API access | `sk-ant-api03-...` |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | ✅ | Prevents token limits | `32768` |
| `GITHUB_REPO_URL` | 🟡 | GitHub integration | `https://github.com/owner/repo` |
| `GITHUB_PAT` | 🟡 | GitHub operations | `ghp_...` |

**Setup**:
```bash
cp .env.sample .env
# Edit .env with your values
export $(cat .env | xargs)
```

---

## 📁 Directory Structure

```
your-project/
├── .claude/
│   ├── commands/           # Slash commands
│   │   ├── plan_w_docs_improved.md
│   │   ├── build_adw.md
│   │   └── scout_improved.md
│   ├── hooks/             # Event hooks (optional)
│   └── skills/            # Advanced workflows (optional)
├── adws/                  # Python modules
│   ├── adw_modules/       # Core modules
│   ├── scout_simple.py    # Scout orchestrator
│   └── adw_sdlc.py        # Build orchestrator
├── specs/                 # Implementation plans
├── scout_outputs/         # Scout results (canonical)
│   ├── relevant_files.json
│   └── traces/
├── ai_docs/               # AI-generated docs
│   ├── build_reports/
│   ├── reviews/
│   └── research/
├── scripts/               # Utility scripts
│   ├── validate_pipeline.sh
│   └── test_installation.py
└── CLAUDE.md              # Project instructions
```

---

## 🎯 Key Commands

### Safe Commands (Read-Only)
| Command | Purpose | Example |
|---------|---------|---------|
| `Grep` | Search content | `Grep "auth" --type py` |
| `Glob` | Find files | `Glob "**/*.py"` |
| `/sc:analyze` | Code review | `/sc:analyze` |
| `/sc:explain` | Explain code | `/sc:explain` |

### Local Changes (Require Approval)
| Command | Purpose | Example |
|---------|---------|---------|
| `/plan_w_docs_improved` | Create spec | `/plan_w_docs_improved "Add auth" "" "files.json"` |
| `/build_adw` | Build from spec | `/build_adw "specs/issue-001-adw-AUTH.md"` |
| `/sc:test` | Run tests | `/sc:test` |
| `/init-parallel-worktrees` | Create branches | `/init-parallel-worktrees feature 3` |

### External Changes (Never Auto-invoke)
| Command | Purpose | Risk |
|---------|---------|------|
| `/sc:git` | Git operations | Can push to remote |
| `/merge-worktree` | Merge branches | Affects main branch |

---

## 🔄 Common Workflows

### Pattern 1: Simple Feature (1-3 files)
```bash
# Just implement directly
Edit files → Test → Commit
```

### Pattern 2: Standard Feature (4-10 files)
```bash
# 1. Find relevant files
Grep "pattern" --type py
Glob "**/*.py"

# 2. Create plan
/plan_w_docs_improved "Feature description" "" "scout_outputs/relevant_files.json"

# 3. Build
/build_adw "specs/issue-001-adw-XXX-feature.md"

# 4. Test
/sc:test
```

### Pattern 3: Complex/Uncertain Feature
```bash
# 1. Parallel exploration
/init-parallel-worktrees explore-feature 3

# 2. Each agent tries different approach
/run-parallel-agents "specs/feature.md" explore-feature

# 3. Compare and merge best
/compare-worktrees explore-feature
/merge-worktree trees/explore-feature-2  # Best one
```

---

## 🔧 Troubleshooting One-Liners

### Check Installation
```bash
# Python version
python --version  # Should be >=3.10

# Test imports
python -c "import sys; sys.path.insert(0, 'adws'); from adw_modules import utils"

# Validate installation
python scripts/test_installation.py

# Check git
git --version  # Should be >=2.0
```

### Environment Issues
```bash
# Check environment variables
echo $ANTHROPIC_API_KEY
echo $CLAUDE_CODE_MAX_OUTPUT_TOKENS

# Load .env file
export $(cat .env | xargs)

# Verify Claude API key
curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages
```

### File Permissions
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Verify permissions
ls -la scripts/
```

---

## ⚠️ Common Errors & Quick Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Token limit exceeded` | Default 8192 limit | `export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768` |
| `ModuleNotFoundError: adw_modules` | Import path issue | `export PYTHONPATH=$PWD/adws:$PYTHONPATH` |
| `Permission denied: script.sh` | Not executable | `chmod +x scripts/*.sh` |
| `API key not found` | Missing env var | `export ANTHROPIC_API_KEY=sk-ant-...` |
| `Scout commands fail` | Missing Task tool | Use native Grep/Glob instead |
| `Files in repo root` | No path enforcement | Use canonical paths (see Directory Structure) |
| `Git on main branch` | No branch check | `git checkout -b feature/issue-XXX-adw-YYY` |
| `Python version too old` | Python <3.10 | Install Python 3.10+ |

---

## 🛡️ Safety Rules

### Git Safety
```bash
# ALWAYS create feature branch before changes
git checkout -b feature/issue-XXX-adw-YYY
```

### Output Safety
```python
# ❌ BAD - Never write to repo root
Write("REPORT.md", content)

# ✅ GOOD - Use canonical paths
Write("ai_docs/reports/report.md", content)
```

### Approval Gates
Get user confirmation for:
- 🟡 Any file modifications
- 🔴 Any git push operations
- 🔴 Any agent spawning

---

## 📊 Quick Decision Helper

**Not sure which command?**

1. **How many files?**
   - 1-3 → Just do it
   - 4-10 → `/plan_w_docs_improved` → `/build_adw`
   - 11+ → Use parallel worktrees

2. **How clear are requirements?**
   - Crystal clear → Standard workflow
   - Need exploration → `/sc:analyze` → `/sc:design`
   - Multiple approaches → Parallel worktrees

3. **Risk level?**
   - Reading only → Use any 🟢 command freely
   - Changing files → Get approval for 🟡 commands
   - External changes → Manual only for 🔴 commands

---

## 🔗 Links to Other Docs

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](../CLAUDE.md) | Full project instructions |
| [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md) | Detailed setup |
| [TROUBLESHOOTING_AND_INTERNALS.md](./TROUBLESHOOTING_AND_INTERNALS.md) | Deep troubleshooting |
| [SLASH_COMMANDS_REFERENCE.md](./SLASH_COMMANDS_REFERENCE.md) | All commands |
| [portability/](./portability/) | Deployment guides |
| [WORKFLOW_ARCHITECTURE.md](./WORKFLOW_ARCHITECTURE.md) | System design |

---

## 💡 Pro Tips

- **Always start with native tools**: Use Grep/Glob before slash commands
- **Read before you write**: Check existing patterns before creating files
- **Use canonical paths**: Never write to repo root
- **Create feature branches**: Never work directly on main
- **Set token limit high**: `32768` or higher for large operations
- **Validate early**: Run `/sc:test` before committing

---

**Remember**: Commands are deterministic. The LLM suggests, the user decides, the command executes predictably.
