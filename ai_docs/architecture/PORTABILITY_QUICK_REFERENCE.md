# Portability Quick Reference

**One-page guide for porting scout_plan_build_mvp to new repositories**

---

## Current Portability Score: 72/100

### What Works Today
- Core validation logic (security, paths, git)
- State management and workflow orchestration
- Agent system and prompt engineering
- GitHub integration via `gh` CLI
- Environment-based configuration

### What Needs Adaptation
- Directory paths (hardcoded to `specs/`, `agents/`, `ai_docs/`)
- Slash commands (fixed list, not extensible)
- Project structure assumptions (Python-centric)
- Single VCS provider (GitHub only)
- Manual installation process

---

## 3 Levels of Portability

### Level 1: Drop-In Compatible (Current: NO, Target: YES)
**Install once, works everywhere**
```bash
pip install scout-plan-build-mvp
cd /any/repo
adws init
adws plan 123
```
**Requirements**: Configuration system, package distribution, auto-detection

### Level 2: Minimal Configuration (Current: PARTIAL, Target: YES)
**Install + 5-minute config**
```bash
pip install scout-plan-build-mvp
cd /my/repo
adws init
# Edit adw_config.yaml (set app_code path)
adws plan 123
```
**Requirements**: Config template, sensible defaults, validation

### Level 3: Deep Integration (Current: NO, Target: OPTIONAL)
**Custom workflows, integrations, extensions**
```yaml
# adw_config.yaml
workflow:
  custom_commands: ["/tax-calculation", "/compliance"]
security:
  allowed_commands: ["mvn", "gradle", "npm"]
```
**Requirements**: Plugin system, custom templates, hooks

---

## Critical Dependencies

### Must Have
1. **Git repository** with remote configured
2. **Python 3.10+** installed
3. **Anthropic API key** for Claude
4. **GitHub CLI (`gh`)** for GitHub integration

### Nice to Have
- Claude Code CLI for enhanced prompting
- R2/S3 credentials for screenshot uploads
- E2B API key for cloud sandboxes

### Repository Requirements
- Git-based version control
- Issue tracker (GitHub Issues, GitLab, Jira)
- Pull request workflow
- Branch permissions (optional)

---

## 5-Minute Migration Checklist

### Pre-Migration
- [ ] Repository has `.git` directory
- [ ] Remote URL configured (`git remote -v`)
- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] API keys available (Anthropic, GitHub)

### Installation
```bash
# 1. Install package (future - when published to PyPI)
pip install scout-plan-build-mvp

# 2. OR clone repository (current)
git clone https://github.com/alexkamysz/scout_plan_build_mvp.git
cd scout_plan_build_mvp
pip install -e .

# 3. Initialize in target repo
cd /path/to/target/repo
adws init
```

### Configuration
```bash
# 4. Edit adw_config.yaml
# Set: project.name, paths.app_code, workflow.custom_commands

# 5. Set environment
cp .env.template .env
# Add: ANTHROPIC_API_KEY, GITHUB_REPO_URL

# 6. Verify
adws health-check
```

### Testing
```bash
# 7. Test on sample issue
adws plan 123  # Use real issue number

# 8. Review generated plan
cat specs/issue-123-adw-*.md

# 9. Test build (optional)
adws build 123 <adw-id>
```

---

## Common Adaptations by Project Type

### Python → Python
**Effort**: 5 minutes
```yaml
# adw_config.yaml (minimal changes)
paths:
  app_code: "src/"  # or lib/, package/, etc.
```

### Python → Java (Maven)
**Effort**: 15 minutes
```yaml
project:
  type: "java"

paths:
  app_code: "src/main/java/"
  tests: "src/test/java/"

security:
  allowed_commands: ["git", "gh", "claude", "mvn", "java"]
```

### Python → JavaScript (Node)
**Effort**: 15 minutes
```yaml
project:
  type: "javascript"

paths:
  app_code: "src/"
  tests: "tests/"

security:
  allowed_commands: ["git", "gh", "claude", "npm", "node"]
```

### Python → Go
**Effort**: 20 minutes
```yaml
project:
  type: "go"

paths:
  app_code: "."  # Go files at root
  tests: "."     # Test files alongside

security:
  allowed_commands: ["git", "gh", "claude", "go"]
```

### Single Repo → Monorepo
**Effort**: 30 minutes
```yaml
# In each service: services/auth/adw_config.yaml
project:
  name: "auth-service"
  root: "services/auth"
  monorepo_root: "../.."

paths:
  agents: "../../.adw/agents/auth/"  # Shared state
```

---

## Breaking Scenarios (Avoid These)

### 1. Custom Directory Names
**Problem**: Tax-prep uses `documents/` instead of `specs/`
**Solution**: Add to `allowed_prefixes` in config
```yaml
paths:
  specs: "documents/tech-specs/"
  allowed_prefixes:
    - "documents/"
```

### 2. Non-GitHub VCS
**Problem**: GitLab or Bitbucket repository
**Solution**: (Future) VCS provider abstraction
**Workaround**: Manual PR creation

### 3. Different AI Provider
**Problem**: Team uses GPT-4 instead of Claude
**Solution**: (Future) AI provider abstraction
**Workaround**: Not supported yet

### 4. No Issue Tracker
**Problem**: Using Jira or Linear instead of GitHub Issues
**Solution**: Manual issue specification
**Workaround**: Create local markdown files as "issues"

### 5. Custom Build System
**Problem**: Bazel, Gradle, custom scripts
**Solution**: Add to `allowed_commands` in config
```yaml
security:
  allowed_commands: ["git", "gh", "claude", "bazel", "gradle"]
```

---

## Troubleshooting Quick Fixes

### "No adw_config.yaml found"
```bash
adws init  # Generate config
```

### "File path not allowed"
```yaml
# adw_config.yaml - add custom path
paths:
  allowed_prefixes:
    - "custom-dir/"
```

### "GitHub API failed"
```bash
gh auth login  # Authenticate GitHub CLI
# OR set GITHUB_PAT in .env
```

### "Claude Code not found"
```bash
# Install Claude Code CLI
# OR set CLAUDE_CODE_PATH in .env
```

### "Permission denied"
```bash
# Check file permissions
chmod +x scripts/*.sh
# Check git permissions
git config --get user.name
```

---

## Portability Roadmap (At a Glance)

| Phase | Timeline | Deliverable | Impact |
|-------|----------|-------------|--------|
| **1. Config** | Week 1 | `adw_config.yaml` system | +8 points |
| **2. Package** | Week 2 | PyPI package + CLI | +5 points |
| **3. Abstract** | Week 3-4 | VCS/AI providers | +7 points |
| **4. Test** | Week 5 | Multi-project tests | +3 points |
| **Total** | 5 weeks | From 72 → 90+ score | +18 points |

---

## Decision Tree: Can I Port This?

```
Do you have a git repository?
├─ NO → ❌ Cannot use ADW (git required)
└─ YES → Continue

Is it on GitHub, GitLab, or Bitbucket?
├─ NO → ⚠️ Limited support (manual PRs)
└─ YES → Continue

Python 3.10+ installed?
├─ NO → 📦 Install Python first
└─ YES → Continue

Can you get Anthropic API key?
├─ NO → ❌ Cannot use ADW (Claude required)
└─ YES → Continue

Is directory structure customizable?
├─ NO → ⚠️ May need wrapper scripts
└─ YES → ✅ Ready to install!

Portability Assessment:
├─ All YES → 95% portable (drop-in)
├─ 1-2 ⚠️ → 80% portable (15-min setup)
├─ 3+ ⚠️ → 60% portable (30-min setup)
└─ Any ❌ → Blocker (fix first)
```

---

## Architecture Layers (Portability View)

```
┌─────────────────────────────────────────┐
│  User Interface                         │ ← CLI, slash commands
│  (Portable: Add custom commands)        │
├─────────────────────────────────────────┤
│  Workflow Orchestration                 │ ← Plan → Build → Test
│  (Portable: Config-driven)              │
├─────────────────────────────────────────┤
│  Configuration Layer                    │ ← adw_config.yaml
│  (Portable: Runtime settings)           │   ← NEW IN WEEK 1
├─────────────────────────────────────────┤
│  Provider Abstraction                   │ ← VCS, AI providers
│  (Portable: Pluggable)                  │   ← NEW IN WEEK 3-4
├─────────────────────────────────────────┤
│  Core Logic                             │ ← Validation, state, agents
│  (Portable: Framework-agnostic)         │   ← ALREADY PORTABLE
├─────────────────────────────────────────┤
│  Infrastructure                         │ ← Git, gh CLI, file system
│  (Portable: Standard tools)             │   ← ALREADY PORTABLE
└─────────────────────────────────────────┘
```

**Green = Already portable** (bottom 2 layers)
**Yellow = Needs config** (middle 2 layers)
**Red = Hardcoded** (top 2 layers → being fixed)

---

## Quick Commands Reference

### Installation
```bash
pip install scout-plan-build-mvp  # Future
cd /your/repo && adws init
```

### Configuration
```bash
adws config                    # View current config
adws config project.name "my-app"  # Set value
adws health-check              # Verify setup
```

### Workflows
```bash
adws plan 123                  # Plan only
adws build 123 <adw-id>        # Build only
adws plan-build 123            # Plan + Build (future)
```

### Troubleshooting
```bash
adws doctor                    # Diagnose issues (future)
adws validate-config           # Check config (future)
adws reset <adw-id>            # Clean state (future)
```

---

## Resources

- **Full Analysis**: `PORTABILITY_ANALYSIS.md`
- **Implementation Plan**: `PORTABILITY_IMPLEMENTATION_ROADMAP.md`
- **Configuration Reference**: `docs/CONFIGURATION_REFERENCE.md` (coming soon)
- **Migration Examples**: `docs/MIGRATION_GUIDE.md` (coming soon)

---

**Last Updated**: 2025-10-25
**Version**: Based on current codebase (pre-portability work)
**Next Review**: After Week 1 implementation
