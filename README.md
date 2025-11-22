# Scout-Plan-Build Development System

**Portable AI-assisted development workflow for any repository. Scout for files, plan features, build implementations - all with AI assistance.**

## 🚀 Quick Install to Your Repo

```bash
# Install to any repository (e.g., your tax-prep project)
./scripts/install_to_new_repo.sh /path/to/your/repo

# Follow the prompts, then:
cd /path/to/your/repo
cp .env.template .env
# Add your ANTHROPIC_API_KEY to .env

# You're ready!
```

**That's it!** The system is now installed in your repo.

---

## 📖 Documentation

| Document | When to Use |
|----------|-------------|
| **[PORTABLE_DEPLOYMENT_GUIDE.md](PORTABLE_DEPLOYMENT_GUIDE.md)** | Installing to new repos (detailed walkthrough) |
| **[CLAUDE.md](CLAUDE.md)** | Quick reference for using the system |
| **[TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)** | Architecture, troubleshooting, advanced usage |
| **[UNINSTALL_GUIDE.md](UNINSTALL_GUIDE.md)** | Removing from a repo |
| **[AI_DOCS_ORGANIZATION.md](AI_DOCS_ORGANIZATION.md)** | Understanding the folder structure |

---

## 🎯 Quick Workflow (After Installation)

```bash
# 1. Find relevant files for your task
Task(subagent_type="explore", prompt="Find all authentication code")

# 2. Create a specification
/plan_w_docs "Add OAuth2 support" "" "scout_outputs/relevant_files.json"

# 3. Build from the spec
/build_adw "specs/issue-001-oauth2.md"
```

### 🚄 Parallel Execution (40-50% Faster!)

```bash
# Run complete SDLC workflow with parallel execution
uv run adws/adw_sdlc.py <issue-number> <adw-id> --parallel

# What happens:
# 1. Plan phase runs (sequential)
# 2. Build phase runs (sequential)
# 3. Test + Review + Document run IN PARALLEL (40-50% speedup!)
# 4. Single aggregated commit at the end

# Example timing:
# Sequential: 12-17 minutes total
# Parallel:   8-11 minutes total (40-50% faster!)
```

---

## 🏗️ What Gets Installed

```
your-repo/
├── adws/                # Core workflow modules
├── scout_outputs/       # Scout phase outputs (canonical)
├── ai_docs/
│   ├── build_reports/   # Build execution reports
│   ├── reviews/         # Code reviews
│   └── research/        # External learning resources
├── specs/               # Generated specifications
├── .claude/commands/    # Workflow commands
└── scripts/             # Validation tools
```

**Your existing code is untouched** - this system works alongside it.

---

## ✨ Features

- **Portable**: Install to any repo in 15 minutes
- **Safe**: Input validation, path security, git safety
- **Organized**: AI-generated content in `ai_docs/`, specs in `specs/`
- **Working**: No broken external tools - uses Task agents that actually exist

---

## 🧹 Maintenance Scripts

```bash
# Validate everything works
./scripts/validate_pipeline.sh

# Clean up redundant agents (optional)
./scripts/cleanup_agents.sh

# Uninstall from a repo
./scripts/uninstall_from_repo.sh /path/to/repo
```

---

## 📊 System Status

| Component | Status | Documentation |
|-----------|--------|---------------|
| Scout | ✅ Working | Uses Task agents (no external tools) |
| Plan | ✅ Working | Spec schema v1.1.0 with validation |
| Build | ✅ Working | Pydantic validation, error handling |
| **Parallel Execution** | ✅ Working | Test+Review+Document run in parallel (40-50% speedup) |
| GitHub Integration | ✅ Working | Requires `gh` CLI |
| Portability | ✅ 85% | See PORTABLE_DEPLOYMENT_GUIDE.md |

---

## 🆘 Support

- **Installation issues**: See [PORTABLE_DEPLOYMENT_GUIDE.md](PORTABLE_DEPLOYMENT_GUIDE.md)
- **Uninstalling**: See [UNINSTALL_GUIDE.md](UNINSTALL_GUIDE.md)
- **Agent confusion**: See [ai_docs/AGENT_CLEANUP_ANALYSIS.md](ai_docs/AGENT_CLEANUP_ANALYSIS.md)
- **Technical details**: See [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)

---

## 🎓 Learning Resources

**New to the system?** Read in this order:
1. This README (you are here!)
2. [PORTABLE_DEPLOYMENT_GUIDE.md](PORTABLE_DEPLOYMENT_GUIDE.md) - Install it
3. [CLAUDE.md](CLAUDE.md) - Use it
4. [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) - Understand it

**Installing to a specific repo type?**
- Tax preparation: Examples in PORTABLE_DEPLOYMENT_GUIDE.md
- Different languages: System is language-agnostic
- Monorepos: Configure with `.adw_config.json`

---

## 🔧 Configuration

After installation, customize via `.adw_config.json`:

```json
{
  "paths": {
    "specs": "specs/",
    "ai_docs": "ai_docs/",
    "allowed": ["specs", "ai_docs", "src", "lib"]
  }
}
```

See [PORTABLE_DEPLOYMENT_GUIDE.md](PORTABLE_DEPLOYMENT_GUIDE.md) for examples.

---

**Version**: MVP (Portable Edition)
**Last Updated**: October 2024
**License**: Internal/Private Use
