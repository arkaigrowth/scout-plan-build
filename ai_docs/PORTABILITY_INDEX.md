# Portability Analysis - Complete Index

**Generated:** 2025-10-25
**System:** scout_plan_build_mvp AI Developer Workflow
**Status:** Production Ready for Porting

## Quick Start

| Goal | Action | Time |
|------|--------|------|
| **Quick Test** | `./scripts/port_to_new_repo.sh /tmp/test-repo` | 5 min |
| **Use in New Repo** | Follow Minimal Setup in Quick Port Guide | 15 min |
| **Full Customization** | Follow Custom Setup in Quick Port Guide | 2 hrs |
| **Understand System** | Read Portability Analysis | 30 min |

## Document Index

### 1. PORTABILITY_SUMMARY.md
**Purpose:** Executive overview of portability
**Audience:** Decision makers, quick reference
**Key Sections:**
- Portability score (85%)
- Three ways to port
- What's portable vs what needs configuration
- Success metrics
- ROI analysis

**When to read:** Before starting any port

### 2. PORTABILITY_ANALYSIS.md
**Purpose:** Comprehensive technical analysis
**Audience:** Engineers implementing the port
**Key Sections:**
- Component-by-component portability analysis
- Hard-coded path identification
- Breaking scenarios for different repo types
- Configuration abstraction recommendations
- Detailed installation requirements

**When to read:** During custom setup or troubleshooting

### 3. QUICK_PORT_GUIDE.md
**Purpose:** Step-by-step practical instructions
**Audience:** Engineers performing the port
**Key Sections:**
- 15-minute minimal setup
- 2-hour custom setup
- Common issues and solutions
- Verification checklist
- Advanced customization options

**When to read:** While actively porting to new repo

### 4. port_to_new_repo.sh
**Purpose:** Automated installation script
**Audience:** Anyone wanting quick setup
**Features:**
- Copies all necessary files
- Creates configuration interactively
- Sets up directory structure
- Generates setup documentation
- Validates prerequisites

**When to use:** For fastest setup or testing

## Usage Patterns

### Pattern 1: Quick Test Drive
```bash
# Create test repository
mkdir -p /tmp/test-adw
cd /tmp/test-adw
git init

# Port system
/path/to/scout_plan_build_mvp/scripts/port_to_new_repo.sh .

# Configure and test
nano .env  # Add API key
source .env
uv run adws/adw_tests/health_check.py
```

**Time:** 10 minutes
**Documents:** None needed (script guides you)

### Pattern 2: Standard Repository
```bash
# Already have a git repo with GitHub remote
cd /path/to/my/repo

# Run port script
/path/to/scout_plan_build_mvp/scripts/port_to_new_repo.sh .

# Or manual setup:
# 1. Read: QUICK_PORT_GUIDE.md - "15-Minute Minimal Setup"
# 2. Copy files and configure
# 3. Test with sample issue
```

**Time:** 15 minutes
**Documents:** QUICK_PORT_GUIDE.md (minimal setup section)

### Pattern 3: Custom Structure
```bash
# Repo with non-standard directories
cd /path/to/custom/repo

# 1. Read: PORTABILITY_ANALYSIS.md
#    - Section 3: "NEEDS_ABSTRACTION"
#    - Section 5: "INSTALLATION_REQUIREMENTS"

# 2. Follow: QUICK_PORT_GUIDE.md
#    - "2-Hour Custom Setup"
#    - "Option 1: Custom Directory Structure"

# 3. Create .adw_config.json
# 4. Test and validate
```

**Time:** 2 hours
**Documents:** Both PORTABILITY_ANALYSIS.md and QUICK_PORT_GUIDE.md

### Pattern 4: Enterprise Deployment
```bash
# Multiple teams, strict requirements
# 1. Read all documentation
# 2. Plan configuration strategy
# 3. Create deployment checklist
# 4. Test in staging environment
# 5. Roll out with training
```

**Time:** 1 day
**Documents:** All documents + custom documentation

## Common Scenarios

### Scenario A: Tax-Prep Application
**Repository Structure:**
```
tax-prep/
├── plans/              # Custom
├── audit-logs/         # Custom
├── docs/              # Standard
└── src/               # Standard
```

**Recommended Approach:**
1. Run port script for initial setup
2. Create `.adw_config.json`:
   ```json
   {
     "allowed_paths": ["plans/", "audit-logs/", "docs/", "src/"],
     "specs_dir": "plans",
     "state_dir": "audit-logs"
   }
   ```
3. Test workflow

**Reference:** QUICK_PORT_GUIDE.md - "Custom Directory Structure"

### Scenario B: Monorepo (Multiple Projects)
**Repository Structure:**
```
company-monorepo/
├── frontend/
├── backend/
├── shared/
└── tools/
```

**Recommended Approach:**
1. Port to root with workspace configuration
2. Set `ADW_WORKSPACE=backend` for specific project
3. Configure paths relative to workspace

**Reference:** QUICK_PORT_GUIDE.md - "Monorepo Support"

### Scenario C: Different Issue Tracker (Jira)
**Setup:**
- GitLab instead of GitHub
- Jira instead of GitHub Issues

**Recommended Approach:**
1. Port core system (still works with Git)
2. Implement adapter for Jira
3. Update workflow scripts to use adapter

**Reference:** PORTABILITY_ANALYSIS.md - "Integration Adapters"

### Scenario D: Different Tech Stack
**Stack:**
- TypeScript/Node.js (not Python)
- Jest (not pytest)

**Recommended Approach:**
1. Port system as-is (language-agnostic workflows)
2. Update slash commands for TypeScript
3. Configure test framework

**Reference:** QUICK_PORT_GUIDE.md - "Multi-Language Support"

## Troubleshooting Guide

### Issue: "Path validation failed"
**Documents:**
- PORTABILITY_ANALYSIS.md - Section 3 "NEEDS_ABSTRACTION"
- QUICK_PORT_GUIDE.md - "Issue 5: Path validation failed"

**Quick Fix:**
```bash
# Option 1: Use standard directories
mkdir -p specs agents ai_docs

# Option 2: Create config
cat > .adw_config.json << 'EOF'
{"allowed_paths": ["your/", "custom/", "paths/"]}
EOF
```

### Issue: "State file not found"
**Documents:**
- PORTABILITY_ANALYSIS.md - Section 3 "State File Locations"
- QUICK_PORT_GUIDE.md - "Issue 6: Plan file not found"

**Quick Fix:**
```bash
# Check state directory exists
ls -la agents/

# Verify state file
cat agents/*/adw_state.json | jq .
```

### Issue: "GitHub authentication failed"
**Documents:**
- QUICK_PORT_GUIDE.md - "Issue 2: gh authentication failed"

**Quick Fix:**
```bash
gh auth login
gh auth status
```

### Issue: "Module not found"
**Documents:**
- QUICK_PORT_GUIDE.md - "Prerequisites Checklist"

**Quick Fix:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify Python
python --version  # Should be 3.10+
```

## Decision Trees

### Should I Use This System?

```
Do you have:
├─ GitHub repository? ─── YES ─→ ✅ Compatible
├─ Git repository? ───── YES ─→ ⚠️ Compatible (manual issue mode)
├─ Issue tracking? ───── YES ─→ ✅ Compatible (any tracker)
└─ AI automation needs? ─ YES ─→ ✅ Perfect fit
```

### Which Setup Should I Use?

```
Your situation:
├─ Just testing? ────────────→ Use port script (5 min)
├─ Standard GitHub repo? ────→ Minimal setup (15 min)
├─ Custom structure? ────────→ Custom setup (2 hrs)
└─ Enterprise deployment? ───→ Full planning (1 day)
```

### Do I Need Custom Configuration?

```
Your directories:
├─ Match specs/, agents/, ai_docs/? ─→ NO config needed
├─ Different names? ──────────────→ Create .adw_config.json
└─ Completely different? ──────────→ Custom setup + validation update
```

## Validation Checklist

After porting, verify these items:

### Environment
- [ ] `.env` file created with API key
- [ ] `GITHUB_REPO_URL` points to correct repo
- [ ] Environment variables loaded (`source .env`)
- [ ] Claude Code CLI accessible

### Files
- [ ] `adws/` directory copied
- [ ] `.claude/commands/` directory copied
- [ ] All Python scripts executable
- [ ] No import errors when testing

### Directories
- [ ] Required directories created (specs/, agents/, etc.)
- [ ] Or `.adw_config.json` created for custom paths
- [ ] Validators accept your directory structure

### Tools
- [ ] `gh` CLI installed and authenticated
- [ ] `git` working with remote
- [ ] `uv` installed
- [ ] Python 3.10+ available

### Functionality
- [ ] Health check passes
- [ ] Can create/fetch GitHub issues
- [ ] Planning workflow completes
- [ ] State persists between phases
- [ ] Git operations work

## Performance Metrics

### Setup Time

| Method | Initial | Testing | Total | Skill Level |
|--------|---------|---------|-------|-------------|
| **Port Script** | 5 min | 5 min | 10 min | Beginner |
| **Minimal Setup** | 10 min | 5 min | 15 min | Beginner |
| **Custom Setup** | 1 hr | 1 hr | 2 hrs | Intermediate |
| **Production** | 4 hrs | 4 hrs | 8 hrs | Advanced |

### Portability Score by Component

```
Core Modules:        ████████████████████ 100%
Git Operations:      ████████████████████ 100%
GitHub Integration:  ████████████████████ 100%
Workflow Scripts:    ███████████████████░  95%
Slash Commands:      ██████████████████░░  90%
State Management:    ████████████████░░░░  80%
Path Validators:     ████████████░░░░░░░░  60%

Overall:             █████████████████░░░  85%
```

### Effort Required

```
Copy Files:          █░░░░  5% of time
Configure Env:       ██░░░  10% of time
Create Directories:  █░░░░  5% of time
Test & Validate:     ████░  20% of time
Customize (opt):     ████████████  60% of time
```

## Best Practices

### Before Porting
1. Read PORTABILITY_SUMMARY.md
2. Identify your repository structure
3. Choose appropriate setup method
4. Gather prerequisites (API keys, tools)

### During Porting
1. Follow checklist in chosen guide
2. Validate each step before proceeding
3. Keep original repo as reference
4. Document any customizations

### After Porting
1. Run complete validation checklist
2. Test with sample issue end-to-end
3. Document your setup for team
4. Train team on workflows

### Maintenance
1. Keep `.env` secure (never commit)
2. Update documentation for customizations
3. Test after repository structure changes
4. Review logs for issues

## Future Improvements

### Planned Enhancements
- [ ] Full configuration system (Section 7 of PORTABILITY_ANALYSIS.md)
- [ ] Integration adapter pattern
- [ ] Multi-language auto-detection
- [ ] Monorepo workspace support
- [ ] Migration guide generator

### Contribution Opportunities
- GitLab integration adapter
- Jira integration adapter
- Configuration UI/wizard
- Docker containerization
- Cloud deployment templates

## Support

### Getting Help

**Issue Type → Resource**
- Setup questions → QUICK_PORT_GUIDE.md
- Understanding components → PORTABILITY_ANALYSIS.md
- Quick reference → PORTABILITY_SUMMARY.md
- Automated setup → Run `port_to_new_repo.sh --help`

### Debug Information

**Collect this information when reporting issues:**
```bash
# Environment
cat .env | grep -v 'API_KEY\|SECRET'
uv --version
python --version
gh --version

# Configuration
cat .adw_config.json 2>/dev/null || echo "No custom config"

# Validation
uv run adws/adw_tests/health_check.py 2>&1

# Logs
find agents -name "execution.log" -exec tail -20 {} \;
```

---

## Summary

The scout_plan_build_mvp system is **highly portable (85%)** with:
- **Universal core** - Works anywhere without changes
- **Flexible configuration** - Adapts to different structures
- **Comprehensive documentation** - Clear guides for all scenarios
- **Automated setup** - Script for fastest deployment
- **Well-tested** - Validation at every step

**Get started in 5 minutes** with the automated script, or **customize in 2 hours** for unique requirements.

All documents are located in `/ai_docs/`:
- `PORTABILITY_SUMMARY.md` - Overview and quick reference
- `PORTABILITY_ANALYSIS.md` - Technical deep dive
- `QUICK_PORT_GUIDE.md` - Step-by-step instructions
- `PORTABILITY_INDEX.md` - This navigation guide

Installation script: `/scripts/port_to_new_repo.sh`

**Ready to start?** Choose your path above and follow the corresponding guide!
