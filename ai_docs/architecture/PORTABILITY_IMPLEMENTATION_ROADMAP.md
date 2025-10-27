# Portability Implementation Roadmap

**Goal**: Achieve 90+ portability score for scout_plan_build_mvp
**Current Score**: 72/100
**Target Score**: 90+/100
**Timeline**: 3-4 weeks

---

## Quick Reference

| Phase | Duration | Priority | Deliverables |
|-------|----------|----------|--------------|
| **1. Configuration System** | Week 1 | Critical | Config loader, path abstraction |
| **2. Installation Package** | Week 2 | High | PyPI package, CLI, auto-setup |
| **3. Abstraction Layers** | Week 3-4 | Medium | VCS/AI providers, templates |
| **4. Testing & Docs** | Week 5 | High | Multi-project tests, guides |

---

## Phase 1: Configuration System (Week 1)

### Objective
Replace hardcoded paths and settings with runtime configuration from `adw_config.yaml`

### Tasks

#### 1.1 Create Configuration Module (Day 1-2)
**File**: `adws/config.py`

```python
"""Configuration management for ADW system."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import yaml
from pydantic import BaseModel, Field


class PathsConfig(BaseModel):
    """Directory paths configuration."""
    specs: str = "specs/"
    agents: str = "agents/"
    ai_docs: str = "ai_docs/"
    app_code: str = "app/"
    tests: str = "tests/"
    scripts: str = "scripts/"
    docs: str = "docs/"

    def allowed_prefixes(self) -> List[str]:
        """Generate allowed path prefixes from configured paths."""
        return [
            self.specs,
            self.agents,
            self.ai_docs,
            self.app_code,
            self.tests,
            self.scripts,
            self.docs,
        ]


class WorkflowConfig(BaseModel):
    """Workflow settings."""
    issue_class_commands: List[str] = Field(default=["/chore", "/bug", "/feature"])
    custom_commands: List[str] = Field(default_factory=list)
    agent_planner: str = "planner"
    agent_implementor: str = "implementor"
    agent_tester: str = "tester"
    agent_reviewer: str = "reviewer"
    agent_documenter: str = "documenter"

    def all_slash_commands(self) -> List[str]:
        """Get all allowed slash commands."""
        base_commands = [
            "/classify_issue", "/classify_adw", "/generate_branch_name",
            "/commit", "/pull_request", "/implement", "/test",
            "/resolve_failed_test", "/test_e2e", "/resolve_failed_e2e_test",
            "/review", "/patch", "/document"
        ]
        return self.issue_class_commands + self.custom_commands + base_commands


class GitHubConfig(BaseModel):
    """GitHub integration settings."""
    repo_url: Optional[str] = None
    require_pat: bool = False
    auto_create_pr: bool = True
    pr_template: str = "default"


class SecurityConfig(BaseModel):
    """Security validation settings."""
    max_prompt_length: int = 100000
    max_commit_message_length: int = 5000
    max_file_path_length: int = 4096
    max_adw_id_length: int = 64
    allowed_commands: List[str] = Field(default=["git", "gh", "claude"])


class ProjectConfig(BaseModel):
    """Project metadata."""
    name: str
    type: str = "auto"  # auto, python, java, javascript, go, etc.
    root: str = "."
    monorepo_root: Optional[str] = None


class ADWConfig(BaseModel):
    """Complete ADW configuration."""
    project: ProjectConfig
    paths: PathsConfig = Field(default_factory=PathsConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "ADWConfig":
        """Load configuration from YAML file.

        Args:
            config_path: Path to adw_config.yaml (defaults to project root)

        Returns:
            Loaded configuration

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config is invalid
        """
        if config_path is None:
            # Search for config in common locations
            search_paths = [
                "adw_config.yaml",
                ".adw/config.yaml",
                "config/adw_config.yaml",
            ]
            for path in search_paths:
                if os.path.exists(path):
                    config_path = path
                    break

            if config_path is None:
                raise FileNotFoundError(
                    "No adw_config.yaml found. Run 'adws init' to create one."
                )

        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        # Validate and parse with Pydantic
        return cls(**data)

    def save(self, config_path: str = "adw_config.yaml") -> None:
        """Save configuration to YAML file."""
        with open(config_path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, indent=2)

    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative path to absolute based on project root."""
        return Path(self.project.root).resolve() / relative_path


# Global config instance (lazy loaded)
_config: Optional[ADWConfig] = None


def get_config(reload: bool = False) -> ADWConfig:
    """Get global ADW configuration.

    Args:
        reload: Force reload from file

    Returns:
        Current ADW configuration
    """
    global _config
    if _config is None or reload:
        _config = ADWConfig.load()
    return _config


def set_config(config: ADWConfig) -> None:
    """Set global ADW configuration (for testing)."""
    global _config
    _config = config
```

**File**: `templates/adw_config.yaml.template`

```yaml
# ADW Configuration Template
# Copy to adw_config.yaml and customize for your project

project:
  name: "${PROJECT_NAME}"
  type: "auto"  # auto-detect or specify: python|java|javascript|go|typescript
  root: "."

paths:
  specs: "specs/"
  agents: "agents/"
  ai_docs: "ai_docs/"
  app_code: "app/"  # Adjust to src/, lib/, etc.
  tests: "tests/"
  scripts: "scripts/"
  docs: "docs/"

workflow:
  issue_class_commands:
    - "/chore"
    - "/bug"
    - "/feature"

  custom_commands: []
    # Add your custom slash commands here
    # - "/custom-command"

  # Agent naming (optional customization)
  agent_planner: "planner"
  agent_implementor: "implementor"
  agent_tester: "tester"
  agent_reviewer: "reviewer"
  agent_documenter: "documenter"

github:
  repo_url: "${GITHUB_REPO_URL}"  # From environment
  require_pat: false
  auto_create_pr: true
  pr_template: "default"

security:
  max_prompt_length: 100000
  max_commit_message_length: 5000
  max_file_path_length: 4096
  allowed_commands:
    - "git"
    - "gh"
    - "claude"
    # Add project-specific commands as needed
```

#### 1.2 Update Validators (Day 2-3)
**File**: `adws/adw_modules/validators.py`

```python
# Replace hardcoded constants with config
from adws.config import get_config

# OLD:
# ALLOWED_PATH_PREFIXES = ["specs/", "agents/", ...]

# NEW:
def get_allowed_prefixes() -> List[str]:
    """Get allowed path prefixes from config."""
    config = get_config()
    return config.paths.allowed_prefixes()

class SafeFilePath(BaseModel):
    # ... existing code ...

    @field_validator('file_path')
    @classmethod
    def validate_path_safety(cls, v: str) -> str:
        # ... existing validation ...

        # Use dynamic prefixes from config
        allowed_prefixes = get_allowed_prefixes()
        if not Path(v).is_absolute():
            has_allowed_prefix = any(v.startswith(prefix) for prefix in allowed_prefixes)
            if not has_allowed_prefix:
                raise ValueError(
                    f"File path must start with one of: {', '.join(allowed_prefixes)}"
                )
        return v


class SafeSlashCommand(BaseModel):
    # OLD: Hardcoded ALLOWED_COMMANDS

    # NEW:
    @classmethod
    def get_allowed_commands(cls) -> List[str]:
        config = get_config()
        return config.workflow.all_slash_commands()

    @field_validator('command')
    @classmethod
    def validate_slash_command(cls, v: str) -> str:
        if not v.startswith('/'):
            raise ValueError("Slash command must start with '/'")

        allowed = cls.get_allowed_commands()
        if v not in allowed:
            raise ValueError(f"Invalid slash command: {v}. Allowed: {allowed}")

        return v
```

#### 1.3 Update Path References (Day 3-4)
**Files to Update**:
- `adws/adw_modules/state.py`
- `adws/adw_modules/agent.py`
- `adws/adw_modules/utils.py`
- `adws/adw_common.py`

**Pattern**:
```python
# OLD:
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
state_path = os.path.join(project_root, "agents", self.adw_id, self.STATE_FILENAME)

# NEW:
from adws.config import get_config

config = get_config()
state_path = config.get_absolute_path(f"{config.paths.agents}{self.adw_id}/{self.STATE_FILENAME}")
```

#### 1.4 Testing (Day 4-5)
```python
# tests/test_config.py
def test_config_loading():
    config = ADWConfig.load("tests/fixtures/test_config.yaml")
    assert config.project.name == "test-project"
    assert config.paths.specs == "custom-specs/"

def test_allowed_prefixes():
    config = ADWConfig.load("tests/fixtures/test_config.yaml")
    prefixes = config.paths.allowed_prefixes()
    assert "custom-specs/" in prefixes

def test_slash_commands():
    config = ADWConfig.load("tests/fixtures/test_config.yaml")
    commands = config.workflow.all_slash_commands()
    assert "/custom-command" in commands
```

**Deliverables**:
- [ ] `adws/config.py` module
- [ ] `templates/adw_config.yaml.template`
- [ ] Updated validators to use config
- [ ] Updated path references across codebase
- [ ] Unit tests for config loading
- [ ] Integration tests with custom configs

---

## Phase 2: Installation Package (Week 2)

### Objective
Create installable package with CLI and auto-setup

### Tasks

#### 2.1 Create CLI Interface (Day 1-2)
**File**: `src/adws/cli.py`

```python
"""Command-line interface for ADW."""

import click
import os
import shutil
from pathlib import Path
from .config import ADWConfig, ProjectConfig


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AI Developer Workflow (ADW) - Automate development tasks."""
    pass


@cli.command()
@click.option("--project-name", prompt="Project name", help="Name of your project")
@click.option("--project-type", default="auto", help="Project type (auto/python/java/javascript)")
@click.option("--app-path", default="app/", help="Path to application code")
def init(project_name: str, project_type: str, app_path: str):
    """Initialize ADW in current repository."""
    click.echo(f"🚀 Initializing ADW for {project_name}...")

    # 1. Create directory structure
    directories = ["specs", "agents", "ai_docs", "ai_docs/build_reports", "ai_docs/reviews", "scripts"]
    for dir_name in directories:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        click.echo(f"  ✅ Created {dir_name}/")

    # 2. Generate config
    config = ADWConfig(
        project=ProjectConfig(name=project_name, type=project_type),
    )
    config.paths.app_code = app_path
    config.save("adw_config.yaml")
    click.echo("  ✅ Created adw_config.yaml")

    # 3. Copy .env template
    if not Path(".env").exists():
        # In packaged version, this would copy from package resources
        click.echo("  ⚠️  Please create .env file with your API keys")
        click.echo("     Required: ANTHROPIC_API_KEY, GITHUB_REPO_URL")

    # 4. Verify tools
    tools_status = {
        "git": shutil.which("git") is not None,
        "gh": shutil.which("gh") is not None,
        "claude": shutil.which("claude") is not None,
    }

    click.echo("\n📋 Tool Status:")
    for tool, installed in tools_status.items():
        status = "✅" if installed else "❌"
        click.echo(f"  {status} {tool}")

    if not all(tools_status.values()):
        click.echo("\n⚠️  Some tools are missing. Please install them:")
        if not tools_status["git"]:
            click.echo("  - git: https://git-scm.com/downloads")
        if not tools_status["gh"]:
            click.echo("  - gh: https://cli.github.com/")
        if not tools_status["claude"]:
            click.echo("  - claude: https://claude.ai/claude-code")

    click.echo("\n✅ Initialization complete!")
    click.echo("Next steps:")
    click.echo("  1. Edit adw_config.yaml for your project structure")
    click.echo("  2. Create .env with your API keys")
    click.echo("  3. Run: adws health-check")


@cli.command()
def health_check():
    """Verify ADW installation and configuration."""
    click.echo("🏥 ADW Health Check\n")

    # 1. Check config exists
    try:
        config = ADWConfig.load()
        click.echo("✅ Configuration loaded")
        click.echo(f"   Project: {config.project.name} ({config.project.type})")
    except FileNotFoundError:
        click.echo("❌ No adw_config.yaml found. Run 'adws init' first.")
        return

    # 2. Check directories
    click.echo("\n📁 Directory Structure:")
    for path_name in ["specs", "agents", "ai_docs"]:
        path = getattr(config.paths, path_name)
        exists = Path(path).exists()
        status = "✅" if exists else "❌"
        click.echo(f"  {status} {path}")

    # 3. Check environment
    click.echo("\n🔑 Environment Variables:")
    env_vars = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GITHUB_REPO_URL": os.getenv("GITHUB_REPO_URL"),
    }
    for var, value in env_vars.items():
        status = "✅" if value else "❌"
        masked = f"{value[:10]}..." if value else "Not set"
        click.echo(f"  {status} {var}: {masked}")

    # 4. Check tools
    click.echo("\n🛠️  Required Tools:")
    tools = ["git", "gh", "claude"]
    for tool in tools:
        installed = shutil.which(tool) is not None
        status = "✅" if installed else "❌"
        click.echo(f"  {status} {tool}")

    click.echo("\n✅ Health check complete!")


@cli.command()
@click.argument("issue_number")
@click.option("--adw-id", default=None, help="ADW workflow ID (auto-generated if not provided)")
def plan(issue_number: str, adw_id: str):
    """Run planning phase for an issue."""
    click.echo(f"📋 Planning phase for issue #{issue_number}")

    # Import and run adw_plan
    from adws import adw_plan
    adw_plan.main_with_args(issue_number, adw_id)


@cli.command()
@click.argument("issue_number")
@click.argument("adw_id")
def build(issue_number: str, adw_id: str):
    """Run build phase for an issue."""
    click.echo(f"🔨 Build phase for issue #{issue_number} (ADW: {adw_id})")

    from adws import adw_build
    adw_build.main_with_args(issue_number, adw_id)


@cli.command()
@click.argument("config_key", required=False)
@click.argument("config_value", required=False)
def config(config_key: str, config_value: str):
    """View or update configuration."""
    if not config_key:
        # Show current config
        config = ADWConfig.load()
        click.echo(config.model_dump_json(indent=2))
    else:
        # Update config
        click.echo(f"Updating {config_key} = {config_value}")
        # TODO: Implement config update logic


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
```

#### 2.2 Create pyproject.toml (Day 2)
```toml
[project]
name = "scout-plan-build-mvp"
version = "0.1.0"
description = "AI-powered development workflow automation with Claude"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Alex Kamysz", email = "alex@example.com"}
]
keywords = ["ai", "development", "automation", "claude", "workflow"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Code Generators",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "pydantic>=2.0",
    "python-dotenv>=1.0",
    "pyyaml>=6.0",
    "click>=8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "black",
    "mypy",
    "ruff",
]
cloud = [
    "boto3",  # For R2 uploads
]

[project.urls]
Homepage = "https://github.com/alexkamysz/scout_plan_build_mvp"
Documentation = "https://github.com/alexkamysz/scout_plan_build_mvp/docs"
Repository = "https://github.com/alexkamysz/scout_plan_build_mvp"
Issues = "https://github.com/alexkamysz/scout_plan_build_mvp/issues"

[project.scripts]
adws = "adws.cli:main"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.black]
line-length = 100
target-version = ["py310"]

[tool.ruff]
line-length = 100
target-version = "py310"
```

#### 2.3 Restructure for Package (Day 3)
```bash
# Move from:
scout_plan_build_mvp/
├── adws/
│   ├── adw_plan.py
│   └── adw_modules/

# To:
scout_plan_build_mvp/
├── src/
│   └── adws/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── adw_plan.py
│       └── adw_modules/
├── templates/
│   ├── adw_config.yaml.template
│   └── .env.template
├── tests/
└── pyproject.toml
```

#### 2.4 Create install.sh (Day 4)
```bash
#!/bin/bash
# install.sh - Automated installation for ADW

set -e

echo "🚀 Scout Plan Build MVP Installer"
echo "=================================="

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(echo "$PYTHON_VERSION < 3.10" | bc)" -eq 1 ]; then
    echo "❌ Python 3.10+ required (found $PYTHON_VERSION)"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION"

# Install package
echo "\n📦 Installing adws package..."
pip install scout-plan-build-mvp

# Initialize in current directory
echo "\n🔧 Initializing ADW..."
adws init

echo "\n✅ Installation complete!"
echo "Next steps:"
echo "  1. Edit adw_config.yaml for your project"
echo "  2. Create .env with API keys"
echo "  3. Run: adws health-check"
```

**Deliverables**:
- [ ] `src/adws/cli.py` with click commands
- [ ] `pyproject.toml` for PyPI packaging
- [ ] Restructured source code under `src/`
- [ ] `install.sh` script
- [ ] README with installation instructions
- [ ] Test installation on clean environment

---

## Phase 3: Abstraction Layers (Week 3-4)

### Objective
Support multiple VCS providers, AI providers, and project types

### Tasks

#### 3.1 VCS Provider Abstraction (Days 1-3)
**File**: `src/adws/providers/vcs.py`

```python
"""Version control system provider abstraction."""

from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from ..adw_modules.data_types import GitHubIssue


class VCSProvider(ABC):
    """Abstract base class for version control providers."""

    @abstractmethod
    def get_repo_url(self) -> str:
        """Get repository URL."""
        pass

    @abstractmethod
    def fetch_issue(self, issue_number: str) -> GitHubIssue:
        """Fetch issue details."""
        pass

    @abstractmethod
    def create_comment(self, issue_number: str, comment: str) -> None:
        """Post comment to issue."""
        pass

    @abstractmethod
    def create_pr(self, branch: str, title: str, body: str) -> str:
        """Create pull request. Returns PR URL."""
        pass

    @abstractmethod
    def check_pr_exists(self, branch: str) -> Optional[str]:
        """Check if PR exists for branch. Returns PR URL or None."""
        pass


class GitHubProvider(VCSProvider):
    """GitHub implementation using gh CLI."""
    # Move existing github.py logic here


class GitLabProvider(VCSProvider):
    """GitLab implementation using glab CLI."""
    # TODO: Implement


class BitbucketProvider(VCSProvider):
    """Bitbucket implementation using bb CLI."""
    # TODO: Implement


def get_vcs_provider(config: Optional[ADWConfig] = None) -> VCSProvider:
    """Factory function to get appropriate VCS provider."""
    if config is None:
        from ..config import get_config
        config = get_config()

    repo_url = config.github.repo_url or os.getenv("GITHUB_REPO_URL")

    if "github.com" in repo_url:
        return GitHubProvider()
    elif "gitlab.com" in repo_url:
        return GitLabProvider()
    elif "bitbucket.org" in repo_url:
        return BitbucketProvider()
    else:
        raise ValueError(f"Unsupported VCS provider for URL: {repo_url}")
```

#### 3.2 AI Provider Abstraction (Days 4-6)
**File**: `src/adws/providers/ai.py`

```python
"""AI provider abstraction."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def run_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute prompt and return response."""
        pass


class ClaudeProvider(AIProvider):
    """Claude Code implementation."""

    def __init__(self, cli_path: str = "claude"):
        self.cli_path = cli_path

    def run_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Existing logic from agent.py
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT implementation."""
    # TODO: Implement


class GeminiProvider(AIProvider):
    """Google Gemini implementation."""
    # TODO: Implement
```

#### 3.3 Language-Specific Templates (Days 7-10)
**Directory Structure**:
```
templates/
├── python/
│   ├── adw_config.yaml
│   └── slash_commands/
├── java/
│   ├── adw_config.yaml
│   └── slash_commands/
├── javascript/
│   ├── adw_config.yaml
│   └── slash_commands/
└── go/
    ├── adw_config.yaml
    └── slash_commands/
```

**File**: `src/adws/templates.py`

```python
"""Template management for different project types."""

from pathlib import Path
from typing import Dict
from .config import ADWConfig


def get_template_path(project_type: str) -> Path:
    """Get template directory for project type."""
    # In packaged version, use importlib.resources
    return Path(__file__).parent.parent / "templates" / project_type


def load_language_config(project_type: str) -> Dict:
    """Load language-specific configuration."""
    template_path = get_template_path(project_type)
    config_path = template_path / "adw_config.yaml"

    if not config_path.exists():
        # Fallback to generic
        template_path = get_template_path("generic")
        config_path = template_path / "adw_config.yaml"

    with open(config_path) as f:
        return yaml.safe_load(f)
```

**Deliverables**:
- [ ] VCS provider abstraction
- [ ] GitHub provider implementation
- [ ] AI provider abstraction
- [ ] Claude provider implementation
- [ ] Language-specific templates
- [ ] Template loader
- [ ] Provider factory functions

---

## Phase 4: Testing & Documentation (Week 5)

### Objective
Comprehensive testing on diverse projects and clear migration guides

### Tasks

#### 4.1 Multi-Project Testing (Days 1-3)
**Test Projects**:
1. **Python Django app** (existing structure)
2. **Java Spring Boot** (Maven structure)
3. **Node.js Express** (NPM structure)
4. **Go microservice** (Go modules)
5. **Monorepo** (Nx/Turborepo)

**Test Cases**:
```python
# tests/integration/test_portability.py

def test_python_project():
    """Test installation on Python project."""
    # Set up mock Python project
    # Run adws init
    # Verify config created
    # Run adws plan 1
    # Assert success

def test_java_project():
    """Test installation on Java project."""
    # Maven structure
    # Custom paths (src/main/java)
    # Verify adaptation

def test_monorepo():
    """Test installation in monorepo."""
    # Multiple services
    # Shared configuration
    # Service-specific state
```

#### 4.2 Documentation (Days 4-5)
**Files to Create**:

1. **INSTALLATION.md** - Step-by-step installation
2. **MIGRATION_GUIDE.md** - Porting to new repos
3. **CONFIGURATION_REFERENCE.md** - All config options
4. **TROUBLESHOOTING.md** - Common issues
5. **EXAMPLES.md** - Real-world examples

**Example: MIGRATION_GUIDE.md**
```markdown
# Migration Guide

## Migrating to a Java Project

### 1. Project Structure
Your Java project:
```
my-app/
├── src/
│   ├── main/java/
│   └── test/java/
├── target/
└── pom.xml
```

### 2. Install ADW
```bash
cd my-app
pip install scout-plan-build-mvp
adws init --project-name "my-app" --project-type "java" --app-path "src/main/java/"
```

### 3. Customize Configuration
Edit `adw_config.yaml`:
```yaml
paths:
  app_code: "src/main/java/"
  tests: "src/test/java/"

security:
  allowed_commands:
    - "git"
    - "gh"
    - "claude"
    - "mvn"  # Add Maven
    - "java"
```

### 4. Test
```bash
adws health-check
adws plan 123
```
```

**Deliverables**:
- [ ] Integration tests on 5 project types
- [ ] Installation guide
- [ ] Migration guide with examples
- [ ] Configuration reference
- [ ] Troubleshooting FAQ
- [ ] Video walkthrough (optional)

---

## Success Metrics

### Portability Score Targets
- **Week 1**: 75/100 (config system)
- **Week 2**: 80/100 (installation package)
- **Week 3**: 85/100 (VCS abstraction)
- **Week 4**: 90/100 (AI abstraction)
- **Week 5**: 92+/100 (testing & docs)

### Installation Time Targets
- **Small project** (< 10k LOC): < 5 minutes
- **Medium project** (10k-50k LOC): < 15 minutes
- **Large project** (> 50k LOC): < 30 minutes

### Test Coverage Targets
- **Unit tests**: 85%+
- **Integration tests**: 70%+
- **Real-world projects**: 5 successful deployments

---

## Risk Mitigation

### High-Risk Items
1. **Breaking existing installations**
   - Mitigation: Version bump, migration script
   - Rollback: Keep v0.0.x compatible

2. **Config format changes**
   - Mitigation: Schema validation, auto-migration
   - Rollback: Support legacy format

3. **VCS provider bugs**
   - Mitigation: Fallback to GitHub-only
   - Testing: Mock providers

### Medium-Risk Items
1. Language detection failures
2. Path resolution edge cases
3. Security bypass attempts

---

## Next Steps

1. **Immediate** (This week):
   - [ ] Review and approve roadmap
   - [ ] Set up development branch
   - [ ] Create milestones in GitHub

2. **Week 1** (Start Phase 1):
   - [ ] Create `config.py` module
   - [ ] Write unit tests
   - [ ] Update validators

3. **Week 2** (Continue Phase 1):
   - [ ] Update all path references
   - [ ] Integration testing
   - [ ] Documentation

4. **Ongoing**:
   - [ ] Weekly progress reviews
   - [ ] User testing feedback
   - [ ] Community input

---

**Questions or Concerns**: File an issue or comment on this roadmap.
