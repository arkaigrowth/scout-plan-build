# Scout-Plan-Build Framework - Installation Guide

**How to Install the Framework in Any Repository**

This guide shows you how to install the Scout-Plan-Build framework in any new or existing repository using our declarative installer.

---

## 🎯 What You'll Get

After installation, your target repo will have:
- ✅ Complete Scout→Plan→Build workflow
- ✅ Parallel execution (40% faster)
- ✅ Security-validated file operations
- ✅ All scripts and commands ready to use
- ✅ Proper directory structure
- ✅ Documentation and examples

---

## 📋 Prerequisites

Before installing, ensure you have:

1. **Python 3.10+**
   ```bash
   python --version  # Should be 3.10 or higher
   ```

2. **Git repository** (existing or new)
   ```bash
   cd /path/to/your/repo
   git status  # Should show a git repo
   ```

3. **Environment variables** (optional but recommended)
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768
   ```

---

## 🚀 Installation Methods

### Method 1: Declarative Installer (Recommended)

This is the **easiest and safest** method. The installer:
- ✅ Validates your environment
- ✅ Creates correct directory structure
- ✅ Copies all necessary files
- ✅ Sets up configuration
- ✅ Runs validation tests
- ✅ Generates documentation

**Step-by-step**:

```bash
# 1. Go to the framework source directory
cd /Users/alexkamysz/AI/scout_plan_build_mvp

# 2. Run the installer with your target repo path
python scripts/install_declarative.py "/path/to/your/target/repo"

# Example for meow_loader_v2:
python scripts/install_declarative.py "/Users/alexkamysz/Documents/CATSY Documents/Catsy AI Projects/meow_loader_v2"
```

**What happens**:
```
🔍 Checking requirements...
  ✅ git found
  ✅ python found
  ⚠️  gh not found (optional)

📦 Installing components...
  ✅ Copied adws/ → adws/
  ✅ Copied .claude/commands/ → .claude/commands/
  ✅ Copied scripts/ → scripts/

📁 Creating directory structure...
  ✅ specs/ - Implementation plans
  ✅ scout_outputs/ - Scout results
  ✅ ai_docs/ - AI-generated docs

⚙️  Generating configuration files...
  ✅ .adw_config.json (generated)
  ✅ CLAUDE.md (copied)
  ✅ .env (created)

✅ Running validation checks...
  ✅ Core modules directory exists
  ✅ Scout module executable
  ✅ Config file exists

🚀 Running post-installation tasks...
  ✅ Marked scripts as executable
  ✅ Test installation passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ INSTALLATION SUCCESSFUL!

📦 Installed 45 files
```

### Method 2: Dry Run First (Safest)

If you want to see what will be installed without making changes:

```bash
python scripts/install_declarative.py "/path/to/target" --dry-run
```

This shows you exactly what will happen without touching any files.

---

## 🔧 Post-Installation Steps

After the installer completes:

### 1. Navigate to Your Repo
```bash
cd "/Users/alexkamysz/Documents/CATSY Documents/Catsy AI Projects/meow_loader_v2"
```

### 2. Review Generated Files
```bash
# Check what was installed
ls -la

# Review configuration
cat .adw_config.json

# Read the quick start guide
cat QUICK_START.md
```

### 3. Set Up Environment Variables
```bash
# Edit .env with your API keys
nano .env

# Required variables:
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768

# Optional (for GitHub integration):
GITHUB_PAT=ghp_...
GITHUB_REPO_URL=https://github.com/your/repo
```

### 4. Activate Environment
```bash
# Load environment variables
export $(grep -v '^#' .env | xargs)

# Or add to your shell profile:
echo 'export $(grep -v "^#" /path/to/repo/.env | xargs)' >> ~/.zshrc
```

### 5. Validate Installation
```bash
# Run validation script
./scripts/validate_pipeline.sh

# Expected output:
🧪 PIPELINE VALIDATION TEST
==========================
1. Testing Scout... ✅ Works
2. Scout creates output... ✅ Yes
3. Plan command exists... ✅ Yes
4. Build command exists... ✅ Yes
```

### 6. Test Scout
```bash
# Try a simple scout operation
python adws/scout_simple.py "test query"

# Should output:
🔍 Scouting for: test query
✅ Found X files
📁 Saved to: ai_docs/scout/relevant_files.json
```

---

## 📂 What Gets Installed

The installer creates this structure:

```
your-repo/
├── adws/                          # Core workflow orchestrators
│   ├── scout_simple.py           # File discovery
│   ├── adw_plan.py               # Plan generation
│   ├── adw_build.py              # Implementation
│   ├── adw_sdlc.py               # Complete SDLC (with --parallel)
│   └── adw_modules/              # Shared utilities
│       ├── validators.py         # Security validation ✅
│       ├── agent.py              # Agent coordination
│       └── ...
│
├── .claude/
│   ├── commands/                 # Slash commands
│   │   ├── scout.md
│   │   ├── plan_w_docs.md
│   │   └── build_adw.md
│   ├── hooks/                    # Event listeners (optional)
│   └── skills/                   # Advanced workflows (optional)
│
├── scripts/
│   ├── validate_pipeline.sh      # Test everything works
│   ├── workflow.sh               # Helper commands
│   ├── worktree_manager.sh       # Git worktree system
│   └── fix_agents_naming.sh      # Migration helper
│
├── scout_outputs/                # Scout results go here
├── specs/                        # Implementation plans
├── ai_docs/                      # AI-generated documentation
│   ├── scout/
│   ├── build_reports/
│   └── reviews/
│
├── .adw_config.json              # Framework configuration
├── .env                          # Environment variables
├── CLAUDE.md                     # Framework instructions
├── QUICK_START.md                # Getting started guide
└── test_installation.py          # Installation validator
```

---

## ⚙️ Configuration

The installer generates `.adw_config.json` with smart defaults:

```json
{
  "project": {
    "name": "meow_loader_v2",
    "type": "auto-detect"
  },
  "paths": {
    "specs": "specs/",
    "scout_outputs": "scout_outputs/",
    "ai_docs": "ai_docs/",
    "app_code": ".",
    "allowed": ["specs", "scout_outputs", "ai_docs", "app", "src", "lib"]
  },
  "workflow": {
    "use_github": true,
    "auto_branch": true,
    "branch_prefix": "feature/"
  }
}
```

**You can customize**:
- `project.type`: Your language (python, javascript, etc.)
- `paths.app_code`: Where your main code lives
- `paths.allowed`: Which directories framework can access
- `workflow.branch_prefix`: Git branch naming

---

## 🔒 Security Features (Included)

The framework includes security by default:

### Path Validation
```python
# Only allows access to specific directories
ALLOWED_PATH_PREFIXES = [
    "specs/",
    "scout_outputs/",
    "ai_docs/",
    "docs/",
    "scripts/",
    "adws/",
    "app/",      # Your app code
]
```

### Input Sanitization
- No shell metacharacters
- No path traversal (../)
- No system directory access
- Pydantic validation on all inputs

---

## 🎯 First Workflow After Installation

Try this complete workflow to verify everything works:

```bash
# 1. Scout for relevant files
python adws/scout_simple.py "configuration files"

# 2. Check the output
cat ai_docs/scout/relevant_files.json

# 3. Create a feature branch
git checkout -b feature/test-framework

# 4. Generate a plan (example)
# Note: You'd normally use a real task here
python adws/adw_plan.py \
  "Test framework installation" \
  "https://docs.python.org" \
  "ai_docs/scout/relevant_files.json"

# 5. Check the plan was created
ls -la specs/

# Success! The framework is working!
```

---

## 🐛 Troubleshooting

### Issue: "Python not found"
```bash
# Install Python 3.10+
brew install python@3.11  # macOS
apt install python3.11    # Linux

# Or use pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

### Issue: "Not a git repository"
```bash
cd /path/to/your/repo
git init
git add .
git commit -m "Initial commit"
```

### Issue: "Permission denied" on scripts
```bash
chmod +x scripts/*.sh
chmod +x adws/*.py
```

### Issue: "Module not found" errors
```bash
# Install dependencies
pip install pydantic python-dotenv gitpython anthropic

# Or use uv (faster)
uv sync
```

### Issue: Scout fails to run
```bash
# Check environment
echo $CLAUDE_CODE_MAX_OUTPUT_TOKENS  # Should be 32768

# Set if not set
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768

# Try again
python adws/scout_simple.py "test"
```

### Issue: "Token limit exceeded"
```bash
# This is fixed in the installed version, but verify:
grep "MAX_OUTPUT_TOKENS" adws/adw_modules/utils.py

# Should see:
# os.environ.setdefault("CLAUDE_CODE_MAX_OUTPUT_TOKENS", "32768")
```

---

## 📚 Next Steps After Installation

1. **Read QUICK_START.md** in your repo
   ```bash
   cat QUICK_START.md
   ```

2. **Try the walkthrough**
   ```bash
   cat QUICK_WALKTHROUGH.md  # If installed
   ```

3. **Customize for your project**
   - Edit `.adw_config.json` with your paths
   - Update `.env` with your API keys
   - Add project-specific slash commands

4. **Test on a real task**
   - Pick a small feature
   - Run Scout → Plan → Build
   - Review the results

5. **Set up GitHub integration** (optional)
   ```bash
   export GITHUB_PAT=ghp_...
   export GITHUB_REPO_URL=https://github.com/your/meow_loader_v2
   ```

---

## 🔄 Updating an Existing Installation

If you installed the framework before November 8, 2025, update it:

```bash
# 1. Navigate to your repo
cd /path/to/repo

# 2. Copy migration script
cp /Users/alexkamysz/AI/scout_plan_build_mvp/scripts/fix_agents_naming.sh scripts/

# 3. Run migration
./scripts/fix_agents_naming.sh

# This updates:
# - Security fix in validators.py
# - Renames agents/ → scout_outputs/
# - Updates all path references
```

---

## 💡 Pro Tips

1. **Use --dry-run first** to see what will be installed
2. **Check .scout_installation.json** after install for a record
3. **Commit the framework** to your repo for team use
4. **Customize .adw_config.json** for your project structure
5. **Read CLAUDE.md** for usage instructions
6. **Test scout first** before trying complex workflows

---

## 🆘 Getting Help

| Issue | Solution |
|-------|----------|
| Installation fails | Run with `--dry-run` to see what's wrong |
| Missing dependencies | Check `requirements.txt` or use `uv sync` |
| Scout doesn't work | Verify environment variables are set |
| Permission errors | Run `chmod +x scripts/*.sh adws/*.py` |
| Can't find output | Check `scout_outputs/` and `ai_docs/scout/` |

---

## 📖 Related Documentation

- **QUICK_START.md** - Getting started (created in your repo)
- **QUICK_WALKTHROUGH.md** - Feature walkthrough
- **CLAUDE.md** - Framework usage instructions
- **.scout_framework.yaml** - Installation manifest (source repo)
- **docs/NOVEMBER_8_UPDATES_SUMMARY.md** - Recent changes

---

## ✅ Installation Checklist

Use this to verify your installation:

- [ ] Installer ran successfully
- [ ] `.adw_config.json` exists
- [ ] `.env` exists and has API keys
- [ ] `adws/` directory present
- [ ] `.claude/commands/` directory present
- [ ] `scripts/` directory present
- [ ] `scout_outputs/` directory exists
- [ ] `specs/` directory exists
- [ ] `ai_docs/` directory exists
- [ ] `./scripts/validate_pipeline.sh` passes
- [ ] `python adws/scout_simple.py "test"` works
- [ ] Environment variables loaded
- [ ] Reviewed QUICK_START.md

---

*Framework Version: 2024.11.8*
*Last Updated: November 8, 2025*
*Installation Method: Declarative Installer*
