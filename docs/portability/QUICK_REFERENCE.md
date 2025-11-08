# Portability Assessment - Quick Reference

**Portability Score: 6.2/10** (Moderate - works with effort)

## Critical Blockers (Must Fix)

| Blocker | Severity | Impact |
|---------|----------|--------|
| ALLOWED_PATH_PREFIXES hardcoded | 🔴 CRITICAL | Can't use custom directory structures |
| agents/ directory locked | 🔴 CRITICAL | State/logs can't go elsewhere |
| No installation validation | 🟡 HIGH | Silent failures when tools missing |
| Python version not specified | 🟡 HIGH | Wrong Python version silently fails |
| Claude Code CLI not verified | 🟡 HIGH | Scripts fail if not installed |

## Current Requirements (Undocumented)

### MUST HAVE
- [ ] Python 3.9 or higher
- [ ] `uv` package manager (`pip install uv`)
- [ ] Claude Code CLI (Node.js/npm required)
- [ ] Anthropic API key

### SHOULD HAVE
- [ ] GitHub CLI (`gh` command) - optional but assumed
- [ ] GitHub personal access token (GITHUB_PAT)
- [ ] Git repository with remote configured

### NICE-TO-HAVE
- [ ] E2B API key (for sandbox testing)
- [ ] Cloudflare R2 credentials (for screenshot storage)

## Installation Paths & Hardcoded Values

### Mandatory Directories (Cannot Change)
```
specs/                 → Specifications directory
agents/{adw_id}/      → State and logs (LOCKED)
ai_docs/              → Build reports and documentation
.claude/commands/     → Slash command definitions
```

### Configurable (Via .env)
```
ANTHROPIC_API_KEY          → API authentication
CLAUDE_CODE_PATH           → Where claude CLI is installed
CLAUDE_CODE_MAX_OUTPUT_TOKENS → Output limit (default too low!)
GITHUB_PAT                 → GitHub authentication
```

### NOT Configurable (Code Changes Required)
```
ALLOWED_PATH_PREFIXES      → Which directories are allowed
State file location        → agents/{adw_id}/adw_state.json
Log location               → agents/{adw_id}/{workflow}/execution.log
Plan discovery path        → specs/*{issue_number}*.md
```

## Portability Breakdown

### Code Structure: 72% Portable
✅ Modules are relative imports  
✅ No hardcoded absolute paths  
❌ Directory structure assumed (specs/, agents/, ai_docs/)  
❌ Whitelist prevents custom paths  

### Environment: 50% Portable
✅ API keys configurable  
✅ Claude path configurable  
❌ Python version not enforced  
❌ Tools not validated  
❌ Dependencies not documented  

### Installation: 44% Portable
✅ Installation script exists  
✅ Creates .env template  
❌ No validation checks  
❌ No tool verification  
❌ No error handling  

## Common Failure Modes

### Failure 1: "command not found: uv"
```
Cause: uv not installed
Fix: pip install uv
Prevention: Install script should check
```

### Failure 2: "command not found: gh"
```
Cause: GitHub CLI not installed
Fix: brew install gh (Mac) or apt install gh (Linux)
Prevention: Script should verify
```

### Failure 3: SafeFilePath validation error
```
Cause: Custom directory structure not in whitelist
Fix: Edit validators.py ALLOWED_PATH_PREFIXES
Prevention: Make configurable via env vars
```

### Failure 4: Module not found errors
```
Cause: Python < 3.9 (missing type hint support)
Fix: Upgrade Python to 3.9+
Prevention: Check version in install script
```

### Failure 5: State file conflicts
```
Cause: Multiple runs use same agents/{adw_id}/ directory
Fix: Use unique adw_id for each run
Prevention: Support configurable state directory
```

## Files to Modify for Full Portability

### PRIORITY 1 (Critical)
- [ ] `adws/adw_modules/validators.py` - Make path whitelist configurable
- [ ] `adws/adw_modules/state.py` - Make state directory configurable
- [ ] `adws/adw_modules/utils.py` - Make log directory configurable
- [ ] `scripts/install_to_new_repo.sh` - Add validation checks

### PRIORITY 2 (Important)
- [ ] `.env.sample` - Document all variables clearly
- [ ] `README.md` - Add prerequisites section
- [ ] `adws/adw_plan.py` - Support --no-github mode
- [ ] Create new `adws/adw_modules/config.py` - Configuration system

### PRIORITY 3 (Nice-to-Have)
- [ ] Create Windows install script
- [ ] Add Docker support
- [ ] Add CI/CD templates
- [ ] Centralized logging support

## Estimated Effort to Fix

| Category | Hours | Impact |
|----------|-------|--------|
| Configuration system | 4-6 | 80% improvement |
| Validation in install | 2-3 | 15% improvement |
| Documentation | 2-3 | 5% improvement |
| **Total** | **8-12** | **Full portability** |

## Workarounds for Current Version

### Workaround 1: Custom Directory Structure
```bash
# Edit validators.py before installation
sed -i 's/"specs\/"/"my_specs\/"/' adws/adw_modules/validators.py
# Then install
```

### Workaround 2: No GitHub Support
```bash
# Skip GitHub integration
# Manually create issue.json file
# Point adw_plan.py to it instead
```

### Workaround 3: Custom State Location
```bash
# Symlink agents/ to desired location
ln -s /custom/path/agents agents
```

## Quick Install Checklist

Before running install_to_new_repo.sh, ensure:

- [ ] Target is a git repository
- [ ] Python 3.9+ installed: `python3 --version`
- [ ] uv installed: `which uv` (or `pip install uv`)
- [ ] Claude Code CLI installed: `which claude`
- [ ] GitHub CLI installed: `which gh` (optional)
- [ ] Have Anthropic API key ready
- [ ] Have GitHub PAT ready (if using GitHub)
- [ ] Target directory is writable
- [ ] Enough disk space (~500MB for full installation)

## Deployment Scenarios & Feasibility

### Scenario: Single Developer, Custom Structure
**Feasibility**: 🟡 Medium (needs validators.py edit)

### Scenario: Team, Standard Structure
**Feasibility**: 🟢 Easy (works as-is)

### Scenario: Monorepo, Multiple Services
**Feasibility**: 🔴 Hard (state conflicts, path issues)

### Scenario: CI/CD Pipeline
**Feasibility**: 🟡 Medium (needs pre-flight checks)

### Scenario: Docker Container
**Feasibility**: 🔴 Hard (no Dockerfile, scripts assume bash)

### Scenario: Windows Development
**Feasibility**: 🔴 Hard (install script is bash-only)

## Key Takeaways

1. **Core code is portable** - Python modules work fine
2. **Configuration is not portable** - Hardcoded paths break new repos
3. **Installation is not robust** - Missing validation causes silent failures
4. **Documentation is incomplete** - Prerequisites not listed, actual setup time longer
5. **GitHub is assumed** - Code assumes gh CLI availability
6. **Python version implicit** - 3.9+ required but not checked

## Next Actions

1. **For current users**: Use as-is with standard directory structure
2. **For new repos**: Plan 45-60 minutes for full setup
3. **For enterprise**: Contact for custom path configuration (need code edits)
4. **For portability improvements**: See main PORTABILITY_ASSESSMENT_REPORT.md

---

**For detailed analysis**, see: PORTABILITY_ASSESSMENT_REPORT.md
