# Scout Plan Build MVP - Portability Analysis

**Analysis Date**: 2025-10-25
**Target Use Case**: Porting to other repositories (e.g., tax-prep, microservices, legacy codebases)
**Portability Score**: 72/100

---

## Executive Summary

The scout_plan_build_mvp system is **moderately portable** with clear abstraction boundaries but contains several hardcoded assumptions about directory structure and workflow patterns. Migration to a new repository requires configuration setup and potential structural adjustments.

**Key Findings**:
- **Component Independence**: 85% - Most modules are well-isolated
- **Configuration Abstraction**: 65% - Mix of configurable and hardcoded values
- **Deployment Readiness**: 60% - Requires manual setup steps
- **Breaking Scenarios**: Identified 8 critical failure points

---

## 1. Component Independence Analysis

### Standalone Components (Work Anywhere)

| Component | Independence | Dependencies | Notes |
|-----------|--------------|--------------|-------|
| `adw_modules/validators.py` | 100% | Pydantic only | Pure security validation |
| `adw_modules/exceptions.py` | 100% | None | Domain exceptions |
| `adw_modules/data_types.py` | 95% | Pydantic | GitHub API types |
| `adw_modules/utils.py` | 90% | Standard lib | Logger, JSON parsing |
| `adw_modules/github.py` | 85% | `gh` CLI | Requires GitHub repo |

### Tightly Coupled Components (Need Integration)

| Component | Coupling Issues | Fix Required |
|-----------|-----------------|--------------|
| `adw_modules/state.py` | Hardcoded `agents/` path | Make configurable |
| `adw_modules/agent.py` | Assumes `agents/{adw_id}/` structure | Path abstraction |
| `adw_common.py` | Uses `Path.cwd()` as ROOT | Inject root path |
| `.claude/commands/*.md` | Reference `specs/`, `ai_docs/` | Template variables |
| `adw_modules/validators.py` | Hardcoded ALLOWED_PATH_PREFIXES | Runtime configuration |

---

## 2. Configuration Abstraction Analysis

### Current Configuration Points

#### Environment Variables (.env.sample)
```bash
# ✅ PORTABLE - Already abstracted
ANTHROPIC_API_KEY=sk-ant-xxx
GITHUB_REPO_URL=https://github.com/owner/repo
CLAUDE_CODE_PATH=/path/to/claude
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768

# ✅ PORTABLE - Optional features
GITHUB_PAT=ghp_xxx
R2_ACCESS_KEY_ID=xxx
E2B_API_KEY=xxx
```

#### Hardcoded Assumptions (NOT Portable)

**File Paths** (`adw_modules/validators.py:30-38`):
```python
# ❌ HARDCODED
ALLOWED_PATH_PREFIXES = [
    "specs/",      # Planning documents
    "agents/",     # Agent state/logs
    "ai_docs/",    # AI-generated docs
    "docs/",       # Human documentation
    "scripts/",    # Utility scripts
    "adws/",       # Workflow code
    "app/",        # Application code (assumed structure)
]
```

**Project Root Discovery** (`adw_modules/utils.py:32`):
```python
# ⚠️ BRITTLE - Assumes specific depth
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
# Assumes: adws/adw_modules/utils.py → 3 levels up
```

**State Storage** (`adw_modules/state.py:64`):
```python
# ❌ HARDCODED
return os.path.join(project_root, "agents", self.adw_id, self.STATE_FILENAME)
```

**Slash Commands** (`.claude/commands/*.md`):
```markdown
# ❌ REFERENCES SPECIFIC PATHS
1. Run SlashCommand: /scout "[USER_PROMPT]" "4" -> "relevant_files_collection_path"
2. Run SlashCommand: /plan_w_docs ... -> "specs/issue-{N}-adw-{ID}.md"
3. Run SlashCommand: /build ... -> "ai_docs/build_reports/{slug}.md"
```

### Required Configuration System

**Proposed: `adw_config.yaml`**
```yaml
# Project metadata
project:
  name: "scout_plan_build_mvp"
  type: "python"  # python, java, typescript, etc.
  root: "."       # Auto-detected via git

# Directory structure
paths:
  specs: "specs/"           # Where plans are stored
  agents: "agents/"         # Agent state and logs
  ai_docs: "ai_docs/"       # AI-generated documentation
  app_code: "app/"          # Application source code
  tests: "tests/"           # Test files
  scripts: "scripts/"       # Utility scripts

  # Validation whitelist (derived from above)
  allowed_prefixes:
    - "${paths.specs}"
    - "${paths.agents}"
    - "${paths.ai_docs}"
    - "docs/"
    - "${paths.scripts}"
    - "${paths.app_code}"

# Workflow settings
workflow:
  issue_class_commands:
    - "/chore"
    - "/bug"
    - "/feature"

  # Custom slash commands (optional)
  custom_commands: []

  # Agent naming
  agent_planner: "planner"
  agent_implementor: "implementor"
  agent_tester: "tester"
  agent_reviewer: "reviewer"
  agent_documenter: "documenter"

# GitHub integration
github:
  repo_url: "${GITHUB_REPO_URL}"  # From env
  require_pat: false
  auto_create_pr: true
  pr_template: "default"

# Security settings
security:
  max_prompt_length: 100000
  max_commit_message_length: 5000
  max_file_path_length: 4096
  allowed_commands:
    - "git"
    - "gh"
    - "claude"
```

---

## 3. Deployment Patterns

### Current Installation (Manual - 15-20 minutes)

```bash
# 1. Clone repository
git clone https://github.com/alexkamysz/scout_plan_build_mvp.git
cd scout_plan_build_mvp

# 2. Set up environment
cp .env.sample .env
# Edit .env with your keys

# 3. Install dependencies
pip install -r requirements.txt  # OR use uv

# 4. Verify tools
gh --version        # GitHub CLI
claude --version    # Claude Code CLI

# 5. Test installation
uv run adws/adw_tests/health_check.py
```

### Proposed Installation (Automated - 5 minutes)

**Create: `install.sh`**
```bash
#!/bin/bash
set -e

echo "🚀 Scout Plan Build MVP Installer"

# 1. Detect project type
detect_project_type() {
    if [ -f "pom.xml" ]; then echo "java"
    elif [ -f "package.json" ]; then echo "javascript"
    elif [ -f "requirements.txt" ]; then echo "python"
    elif [ -f "go.mod" ]; then echo "go"
    else echo "unknown"; fi
}

PROJECT_TYPE=$(detect_project_type)
echo "Detected project type: $PROJECT_TYPE"

# 2. Create directory structure
echo "Creating directory structure..."
mkdir -p specs agents ai_docs/{analyses,build_reports,reviews} scripts

# 3. Initialize configuration
echo "Generating adw_config.yaml..."
cat > adw_config.yaml <<EOF
project:
  name: "$(basename $(pwd))"
  type: "$PROJECT_TYPE"
  root: "."

paths:
  specs: "specs/"
  agents: "agents/"
  ai_docs: "ai_docs/"
  app_code: "src/"  # Adjust based on project type
  tests: "tests/"
  scripts: "scripts/"
EOF

# 4. Set up environment
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    curl -s https://raw.githubusercontent.com/alexkamysz/scout_plan_build_mvp/main/.env.sample > .env
    echo "⚠️  Please edit .env with your API keys"
fi

# 5. Install adws package
echo "Installing adws package..."
pip install scout-plan-build-mvp  # Future PyPI package

# 6. Verify installation
echo "Verifying installation..."
adws health-check

echo "✅ Installation complete!"
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Review adw_config.yaml for project-specific settings"
echo "  3. Run: adws plan <issue-number>"
```

### Package Structure (PyPI-Ready)

```
scout-plan-build-mvp/
├── pyproject.toml              # Package metadata
├── src/
│   └── adws/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── config.py           # Configuration loader
│       ├── adw_modules/        # Core modules
│       └── templates/          # Command templates
├── templates/
│   ├── adw_config.yaml.tmpl    # Config template
│   └── .env.tmpl               # Environment template
├── tests/
└── README.md
```

**Proposed: `pyproject.toml`**
```toml
[project]
name = "scout-plan-build-mvp"
version = "0.1.0"
description = "AI-powered development workflow automation"
authors = [{name = "Your Name", email = "email@example.com"}]
requires-python = ">=3.10"
dependencies = [
    "pydantic>=2.0",
    "python-dotenv",
    "pyyaml",
    "click>=8.0",  # CLI framework
]

[project.optional-dependencies]
dev = ["pytest", "black", "mypy"]
cloud = ["e2b", "boto3"]  # For cloud sandboxes and R2

[project.scripts]
adws = "adws.cli:main"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

---

## 4. Breaking Scenarios

### Critical Failure Points

#### 1. Different Directory Structure
**Scenario**: Tax-prep repo uses `documents/` instead of `specs/`
```
tax-prep-repo/
├── documents/          # ❌ Not in ALLOWED_PATH_PREFIXES
│   └── tax-plans/
├── calculations/       # ❌ Not whitelisted
└── reports/            # ❌ Not whitelisted
```

**Impact**: `SafeFilePath` validator rejects all file operations
**Fix**: Load `ALLOWED_PATH_PREFIXES` from `adw_config.yaml`

#### 2. Monorepo Structure
**Scenario**: Microservices in subdirectories
```
monorepo/
├── services/
│   ├── auth-service/
│   ├── payment-service/
│   └── user-service/
├── libs/
└── tools/
```

**Impact**:
- Project root detection fails (assumes single repo)
- State files scattered across services
- GitHub operations ambiguous (which service?)

**Fix**:
- Add `project.subpath` to config
- Scope state to service: `agents/{service}/{adw_id}/`
- Require explicit service parameter

#### 3. Non-GitHub VCS
**Scenario**: GitLab, Bitbucket, or Azure DevOps
```python
# adw_modules/github.py:56
def get_repo_url() -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],  # ✅ Works
        ...
    )
    return result.stdout.strip()

# But downstream code assumes GitHub:
def extract_repo_path(github_url: str) -> str:
    return github_url.replace("https://github.com/", "").replace(".git", "")
    # ❌ Fails for gitlab.com, bitbucket.org
```

**Impact**: All GitHub API calls fail
**Fix**: Abstract VCS provider:
```python
class VCSProvider:
    def fetch_issue(self, issue_id: str) -> Issue: ...
    def create_pr(self, branch: str, title: str) -> str: ...

class GitHubProvider(VCSProvider): ...
class GitLabProvider(VCSProvider): ...
```

#### 4. Language/Framework Mismatch
**Scenario**: Java project (Maven structure)
```
tax-prep-java/
├── src/
│   ├── main/java/com/example/
│   └── test/java/com/example/
├── target/                # Build artifacts
└── pom.xml
```

**Impact**:
- Validators assume Python-like structure
- Scout doesn't understand Java package paths
- Build commands fail (no `uv run`)

**Fix**:
- Add language detection
- Load language-specific templates
- Adjust build commands based on project type

#### 5. Custom Slash Commands
**Scenario**: Tax-prep needs `/tax-calculation` command
```markdown
# .claude/commands/tax-calculation.md
# Purpose: Generate tax calculation logic
...
```

**Impact**:
- `SafeSlashCommand.ALLOWED_COMMANDS` rejects it
- Validator hardcoded to specific set

**Fix**: Load allowed commands from config
```python
class SafeSlashCommand(BaseModel):
    command: str

    @classmethod
    def from_config(cls, config_path: str):
        config = yaml.safe_load(open(config_path))
        cls.ALLOWED_COMMANDS = (
            config['workflow']['issue_class_commands'] +
            config['workflow']['custom_commands']
        )
```

#### 6. No Claude Code CLI
**Scenario**: Team uses different AI tools (OpenAI Codex, Gemini)
```bash
# adw_modules/utils.py:180
"CLAUDE_CODE_PATH": os.getenv("CLAUDE_CODE_PATH", "claude"),
```

**Impact**: All agent operations fail
**Fix**: Abstract AI provider
```python
class AIProvider:
    def run_prompt(self, prompt: str) -> str: ...

class ClaudeProvider(AIProvider):
    def run_prompt(self, prompt: str) -> str:
        return subprocess.run([self.cli_path, "prompt", prompt])

class OpenAIProvider(AIProvider): ...
```

#### 7. State Storage Conflicts
**Scenario**: Multiple users running ADW on same issue
```
agents/
└── ADW-12345/          # User A's state
    └── adw_state.json  # Overwritten by User B
```

**Impact**: Race conditions, lost work
**Fix**: Namespace by user
```python
state_path = f"agents/{username}/{adw_id}/adw_state.json"
```

#### 8. Path Traversal in Custom Repos
**Scenario**: Tax-prep uses symlinks to shared libraries
```
tax-prep/
├── libs -> /usr/local/shared-libs/  # Symlink
└── calculations/
```

**Impact**:
- `SafeFilePath.validate_path_safety` resolves symlinks
- May allow access outside project root

**Fix**: Validate resolved path stays within project
```python
def validate_path_safety(cls, v: str) -> str:
    normalized = str(Path(v).resolve())
    project_root = get_project_root()

    if not normalized.startswith(str(project_root)):
        raise ValueError(f"Path escapes project root: {v}")
```

---

## 5. Portability Recommendations

### Required Changes for 90%+ Portability

#### Level 1: Essential (Immediate)
1. **Configuration System**
   - Create `adws/config.py` to load `adw_config.yaml`
   - Replace all hardcoded paths with config lookups
   - Priority: Critical | Effort: 4 hours

2. **Path Abstraction**
   - Inject `project_root` instead of computing via `__file__`
   - Use config for all directory references
   - Priority: Critical | Effort: 3 hours

3. **VCS Provider Abstraction**
   - Create `VCSProvider` interface
   - Implement GitHub as default
   - Support GitLab, Bitbucket as plugins
   - Priority: High | Effort: 8 hours

#### Level 2: Important (1-2 weeks)
4. **Installation Package**
   - Create `pyproject.toml` for PyPI
   - Build `install.sh` script
   - Add `adws` CLI entry point
   - Priority: High | Effort: 12 hours

5. **Language Detection**
   - Auto-detect project type (Python, Java, JS, etc.)
   - Load language-specific templates
   - Adjust build commands
   - Priority: Medium | Effort: 6 hours

6. **Template System**
   - Convert slash commands to Jinja2 templates
   - Support variable substitution
   - Allow custom command injection
   - Priority: Medium | Effort: 8 hours

#### Level 3: Enhanced (Future)
7. **Multi-User Support**
   - Namespace state by user/session
   - Add locking mechanisms
   - Priority: Low | Effort: 4 hours

8. **AI Provider Abstraction**
   - Support Claude, GPT-4, Gemini
   - Pluggable architecture
   - Priority: Low | Effort: 16 hours

---

## 6. Installation Checklist (New Repo)

### Pre-Installation
- [ ] Verify git repository initialized
- [ ] Confirm GitHub/GitLab remote configured
- [ ] Check Python 3.10+ installed
- [ ] Verify `gh` CLI installed (if using GitHub)
- [ ] Obtain Anthropic API key

### Installation Steps
```bash
# 1. Install package (future)
pip install scout-plan-build-mvp

# 2. Initialize in your repo
cd /path/to/your/repo
adws init

# 3. Configure
# Edit generated adw_config.yaml:
#   - Set paths.app_code to your source directory
#   - Add custom slash commands if needed
#   - Adjust allowed_prefixes for your structure

# 4. Set environment
cp .env.template .env
# Add your ANTHROPIC_API_KEY, GITHUB_REPO_URL

# 5. Verify
adws health-check

# 6. Test
adws plan 123  # Where 123 is an existing issue
```

### Post-Installation
- [ ] Review generated directory structure
- [ ] Test planning phase on sample issue
- [ ] Customize slash commands for your domain
- [ ] Set up team access (if multi-user)
- [ ] Configure CI/CD integration (optional)

---

## 7. Config Template for New Repos

### Minimal Configuration (Works Everywhere)
```yaml
# adw_config.yaml
project:
  name: "my-awesome-project"
  type: "auto"  # Auto-detect or specify: python|java|javascript|go

paths:
  specs: "specs/"
  agents: "agents/"
  ai_docs: "ai_docs/"
```

### Tax-Prep Example
```yaml
# tax-prep-repo/adw_config.yaml
project:
  name: "tax-prep-system"
  type: "java"
  root: "."

paths:
  specs: "documents/tech-specs/"
  agents: ".adw/agents/"            # Hidden directory
  ai_docs: "documents/ai-generated/"
  app_code: "src/main/java/"
  tests: "src/test/java/"
  scripts: "scripts/"

  # Tax-specific paths
  allowed_prefixes:
    - "documents/"
    - ".adw/"
    - "src/"
    - "scripts/"
    - "calculations/"
    - "reports/"

workflow:
  issue_class_commands:
    - "/chore"
    - "/bug"
    - "/feature"
    - "/tax-calculation"    # Custom command
    - "/compliance-check"   # Custom command

  custom_commands:
    - "/generate-tax-form"
    - "/validate-calculations"

github:
  repo_url: "https://github.com/company/tax-prep"
  require_pat: true
  auto_create_pr: false  # Manual review required

security:
  max_prompt_length: 50000  # Smaller for compliance
  allowed_commands:
    - "git"
    - "gh"
    - "claude"
    - "mvn"         # Maven for Java builds
    - "java"        # Java execution
```

### Monorepo Example
```yaml
# monorepo/services/auth-service/adw_config.yaml
project:
  name: "auth-service"
  type: "typescript"
  root: "services/auth-service"  # Subpath in monorepo
  monorepo_root: "../.."         # Reference to monorepo root

paths:
  specs: "docs/specs/"
  agents: "../../.adw/agents/auth-service/"  # Shared agents dir
  ai_docs: "docs/ai-generated/"
  app_code: "src/"
  tests: "tests/"

  # Shared libraries (read-only)
  readonly_prefixes:
    - "../../libs/"
    - "../../shared/"

github:
  repo_url: "https://github.com/company/monorepo"
  issue_prefix: "[auth-service]"  # Tag issues for this service
```

---

## 8. Migration Effort Estimates

### Small Project (< 10k LOC)
- Setup time: 30 minutes
- Configuration: 15 minutes
- Testing: 30 minutes
- **Total**: ~1 hour

### Medium Project (10k-50k LOC)
- Setup time: 1 hour
- Configuration: 30 minutes
- Custom commands: 1 hour
- Testing: 1 hour
- **Total**: ~3.5 hours

### Large/Legacy Project (> 50k LOC)
- Setup time: 2 hours
- Configuration: 1 hour
- Path mapping: 2 hours
- Custom commands: 3 hours
- Testing: 4 hours
- Team training: 4 hours
- **Total**: ~16 hours (2 days)

### Enterprise Monorepo
- Setup per service: 1 hour × N services
- Shared configuration: 4 hours
- VCS integration: 8 hours (if non-GitHub)
- Custom AI provider: 16 hours (if not Claude)
- Security review: 8 hours
- **Total**: ~36 hours + (N × 1 hour)

---

## 9. Portability Score Breakdown

| Category | Weight | Score | Weighted |
|----------|--------|-------|----------|
| **Component Independence** | 25% | 85/100 | 21.25 |
| **Configuration Abstraction** | 30% | 65/100 | 19.50 |
| **Installation Automation** | 15% | 60/100 | 9.00 |
| **Documentation Clarity** | 10% | 80/100 | 8.00 |
| **Error Handling** | 10% | 75/100 | 7.50 |
| **Platform Support** | 10% | 70/100 | 7.00 |
| **Total** | 100% | - | **72.25** |

### Score Interpretation
- **90-100**: Drop-in portable, minimal configuration
- **70-89**: Portable with moderate setup (current state)
- **50-69**: Significant adaptation required
- **< 50**: Tightly coupled, major refactoring needed

---

## 10. Action Plan for 90+ Portability

### Phase 1: Configuration System (Week 1)
- [ ] Create `adws/config.py` with YAML loader
- [ ] Add `adw_config.yaml.template`
- [ ] Refactor path references to use config
- [ ] Update validators to load from config
- [ ] Test with 3 different directory structures

### Phase 2: Installation Package (Week 2)
- [ ] Create `pyproject.toml`
- [ ] Build CLI entry point (`adws` command)
- [ ] Write `install.sh` script
- [ ] Add auto-detection for project type
- [ ] Create migration guide

### Phase 3: Abstraction Layer (Week 3-4)
- [ ] Abstract VCS provider (GitHub, GitLab, Bitbucket)
- [ ] Abstract AI provider (Claude, GPT, Gemini)
- [ ] Create language-specific templates
- [ ] Add plugin system for custom extensions
- [ ] Document extension points

### Phase 4: Testing & Documentation (Week 5)
- [ ] Test on 5 different project types
- [ ] Write detailed migration guides
- [ ] Create video walkthrough
- [ ] Build troubleshooting FAQ
- [ ] Publish to PyPI

---

## Conclusion

The scout_plan_build_mvp system has **strong architectural foundations** but needs **configuration abstraction** to achieve high portability. The core logic (validation, state management, workflow orchestration) is well-designed and reusable.

**Key Strengths**:
- Clean module boundaries
- Comprehensive security validation
- Well-documented workflows
- Extensible agent system

**Key Weaknesses**:
- Hardcoded directory paths
- GitHub-only VCS support
- Manual installation process
- Limited project type support

**Recommended Path Forward**:
1. Implement configuration system (4-6 hours)
2. Package for PyPI distribution (8-12 hours)
3. Test on 3 different repo types (4-6 hours)
4. Document migration patterns (2-4 hours)

**Estimated Time to 90+ Portability**: 3-4 weeks of focused development

With these changes, the system would be portable to:
- Python, Java, TypeScript, Go projects
- GitHub, GitLab, Bitbucket repositories
- Monorepos and microservices
- Legacy codebases with custom structures
- Enterprise environments with security constraints
