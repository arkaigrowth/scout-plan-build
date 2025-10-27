# Architecture Documentation

**System architecture, design decisions, and portability analysis for scout_plan_build_mvp**

---

## Overview

This directory contains architectural documentation for the scout_plan_build_mvp system, focusing on system design, scalability, portability, and long-term evolution.

## 🎯 NEW: Visual Architecture Documentation

### [ARCHITECTURE_INDEX.md](ARCHITECTURE_INDEX.md) ← Start Here!
**Created using parallel execution**: 4 docs-architect subagents created these diagrams simultaneously, demonstrating the framework's 40-50% speedup!

### [diagrams/](diagrams/) - Architecture Diagrams (NEW!)
1. **[System Architecture Overview](diagrams/system-architecture-overview.md)**
   - Three-layer architecture design
   - Parallel vs sequential execution paths
   - Performance metrics and dogfooding success

2. **[Parallel Execution Sequence](diagrams/parallel-execution-sequence.md)**
   - The 30-line subprocess.Popen() solution
   - Git conflict resolution via --no-commit flags
   - Simple vs overengineered comparison

3. **[Component Interaction UML](diagrams/component-interaction-uml.md)**
   - ADW module relationships
   - Pydantic validation security
   - State management patterns

4. **[Scout→Plan→Build Pipeline](diagrams/scout-plan-build-pipeline.md)**
   - Complete workflow visualization
   - Reality vs documentation
   - Working patterns and fallbacks

**Dogfooding Success**: These diagrams were created using the framework's own parallel execution feature - ultimate validation!

---

## Document Index

### Portability Analysis Series

1. **[PORTABILITY_ANALYSIS.md](./PORTABILITY_ANALYSIS.md)** (Main Document)
   - **Score**: 72/100 portability
   - **Audience**: System architects, team leads, decision makers
   - **Length**: ~6000 words, 30-minute read
   - **Purpose**: Comprehensive analysis of portability to other repositories

   **What's Inside**:
   - Component independence breakdown (85% standalone)
   - Configuration abstraction analysis (65% configurable)
   - 8 critical breaking scenarios identified
   - Deployment patterns and installation strategies
   - Required vs optional components
   - Config templates for new repos

   **Read This If**:
   - You're evaluating whether this system will work for your project
   - You need to understand architectural trade-offs
   - You're planning a migration to a different repository
   - You want to know what breaks in different scenarios

2. **[PORTABILITY_IMPLEMENTATION_ROADMAP.md](./PORTABILITY_IMPLEMENTATION_ROADMAP.md)** (Implementation Plan)
   - **Timeline**: 5 weeks to 90+ portability score
   - **Audience**: Developers, contributors, implementers
   - **Length**: ~4000 words, code-heavy
   - **Purpose**: Step-by-step implementation plan to achieve portability

   **What's Inside**:
   - Week-by-week task breakdown
   - Code examples for each component
   - Configuration system design
   - Package structure for PyPI
   - VCS and AI provider abstractions
   - Testing strategy across project types

   **Read This If**:
   - You're implementing the portability improvements
   - You need concrete code examples
   - You want to contribute to the project
   - You're tracking progress week-by-week

3. **[PORTABILITY_QUICK_REFERENCE.md](./PORTABILITY_QUICK_REFERENCE.md)** (Quick Start)
   - **Format**: One-page reference guide
   - **Audience**: Users, DevOps, quick adopters
   - **Length**: ~1500 words, 10-minute read
   - **Purpose**: Fast reference for common portability questions

   **What's Inside**:
   - 5-minute migration checklist
   - Common adaptations by project type
   - Troubleshooting quick fixes
   - Decision tree: "Can I port this?"
   - Quick commands reference

   **Read This If**:
   - You need to migrate RIGHT NOW
   - You hit a specific error and need a quick fix
   - You want to know if your project is compatible
   - You prefer concise, actionable guidance

---

## Reading Paths

### For Decision Makers
**Goal**: Evaluate if this system works for your organization

1. Start: [PORTABILITY_QUICK_REFERENCE.md](./PORTABILITY_QUICK_REFERENCE.md) - Decision tree section
2. Deep dive: [PORTABILITY_ANALYSIS.md](./PORTABILITY_ANALYSIS.md) - Section 4 (Breaking Scenarios)
3. Cost assessment: [PORTABILITY_ANALYSIS.md](./PORTABILITY_ANALYSIS.md) - Section 8 (Migration Effort)

**Time Investment**: 20 minutes
**Output**: Go/No-Go decision with cost estimates

### For Implementers
**Goal**: Port the system to a new repository

1. Start: [PORTABILITY_QUICK_REFERENCE.md](./PORTABILITY_QUICK_REFERENCE.md) - 5-minute checklist
2. Configure: [PORTABILITY_ANALYSIS.md](./PORTABILITY_ANALYSIS.md) - Section 7 (Config Templates)
3. Troubleshoot: [PORTABILITY_QUICK_REFERENCE.md](./PORTABILITY_QUICK_REFERENCE.md) - Quick fixes

**Time Investment**: 30-60 minutes (setup + testing)
**Output**: Working installation in your repo

### For Developers
**Goal**: Contribute to portability improvements

1. Start: [PORTABILITY_ANALYSIS.md](./PORTABILITY_ANALYSIS.md) - Full read
2. Plan: [PORTABILITY_IMPLEMENTATION_ROADMAP.md](./PORTABILITY_IMPLEMENTATION_ROADMAP.md) - Your phase
3. Reference: [PORTABILITY_QUICK_REFERENCE.md](./PORTABILITY_QUICK_REFERENCE.md) - Architecture layers

**Time Investment**: 2-3 hours (initial read + planning)
**Output**: Clear understanding of what to build

### For System Architects
**Goal**: Understand design decisions and trade-offs

1. Start: [PORTABILITY_ANALYSIS.md](./PORTABILITY_ANALYSIS.md) - Sections 1-2 (Components & Config)
2. Patterns: [PORTABILITY_IMPLEMENTATION_ROADMAP.md](./PORTABILITY_IMPLEMENTATION_ROADMAP.md) - Phase 3 (Abstractions)
3. Future: [PORTABILITY_ANALYSIS.md](./PORTABILITY_ANALYSIS.md) - Section 10 (Action Plan)

**Time Investment**: 1-2 hours
**Output**: Architecture understanding and design patterns

---

## Key Insights from Analysis

### What Makes This System Portable

**Strong Foundation (85% Component Independence)**:
- Clean module boundaries (adw_modules/)
- Pydantic validation (security-first)
- State management abstraction
- Workflow orchestration decoupled from implementation
- GitHub API wrapped in module layer

**Weak Points (65% Configuration Abstraction)**:
- Hardcoded directory paths (`specs/`, `agents/`, `ai_docs/`)
- Fixed slash command list (not extensible)
- Single VCS provider (GitHub-only via `gh` CLI)
- Python-centric assumptions (uv, project structure)
- Manual installation (no package distribution)

### Critical Dependencies

**Required (Cannot Work Without)**:
1. Git repository with remote
2. Python 3.10+
3. Anthropic API key (Claude)
4. GitHub CLI (`gh`) for issue/PR operations

**Optional (Degrades Gracefully)**:
1. Claude Code CLI (can use API directly)
2. R2/S3 credentials (screenshots upload)
3. E2B sandbox (cloud execution)

### Breaking Scenarios (Where It Fails)

1. **Different directory structure** → Path validation rejects operations
2. **Monorepo** → State management conflicts, unclear boundaries
3. **Non-GitHub VCS** → All issue/PR operations fail
4. **Java/Go/JS project** → Build commands fail, structure mismatches
5. **Custom slash commands** → Validator rejects them
6. **No Claude Code CLI** → Agent operations fail
7. **Multi-user on same issue** → Race conditions in state
8. **Symlinked paths** → Path traversal edge cases

**Fix**: Configuration system + provider abstractions (5 weeks)

---

## Current State vs Target State

### Current State (Score: 72/100)
```yaml
Installation:
  method: "Clone repo + manual setup"
  time: "15-20 minutes"

Configuration:
  type: "Environment variables only"
  paths: "Hardcoded in validators.py"
  extensibility: "None"

Portability:
  repositories: "Python projects on GitHub"
  vcs: "GitHub only"
  ai: "Claude only"

Directory_Structure:
  required:
    - specs/
    - agents/
    - ai_docs/
  optional: []
  configurable: false
```

### Target State (Score: 90+/100)
```yaml
Installation:
  method: "pip install scout-plan-build-mvp"
  time: "5 minutes"
  cli: "adws init"

Configuration:
  type: "adw_config.yaml + environment"
  paths: "Fully configurable"
  extensibility: "Custom slash commands"

Portability:
  repositories: "Python, Java, JS, Go, Rust"
  vcs: "GitHub, GitLab, Bitbucket (pluggable)"
  ai: "Claude, GPT-4, Gemini (pluggable)"

Directory_Structure:
  required: []  # All configurable
  optional:
    - specs/
    - agents/
    - ai_docs/
  configurable: true
```

---

## Implementation Status

### Phase 1: Configuration System (Week 1)
- [ ] Create `adws/config.py` module
- [ ] Design `adw_config.yaml` schema
- [ ] Update validators to use config
- [ ] Refactor path references
- [ ] Unit tests

**Impact**: +8 portability points (72 → 80)

### Phase 2: Installation Package (Week 2)
- [ ] Build `pyproject.toml`
- [ ] Create CLI interface (`adws` command)
- [ ] Restructure for PyPI
- [ ] Write `install.sh` script
- [ ] Package documentation

**Impact**: +5 portability points (80 → 85)

### Phase 3: Abstraction Layers (Week 3-4)
- [ ] VCS provider abstraction
- [ ] AI provider abstraction
- [ ] Language-specific templates
- [ ] Plugin system
- [ ] Provider factories

**Impact**: +7 portability points (85 → 92)

### Phase 4: Testing & Docs (Week 5)
- [ ] Test on 5 project types
- [ ] Migration guide
- [ ] Configuration reference
- [ ] Troubleshooting FAQ
- [ ] Video walkthrough

**Impact**: +3 portability points (92 → 95+)

---

## Migration Effort Estimates

| Project Size | Setup | Config | Custom | Testing | Training | Total |
|--------------|-------|--------|--------|---------|----------|-------|
| **Small** (< 10k LOC) | 30m | 15m | 0m | 30m | 0m | **~1 hour** |
| **Medium** (10k-50k) | 1h | 30m | 1h | 1h | 0m | **~3.5 hours** |
| **Large** (> 50k) | 2h | 1h | 2h | 4h | 4h | **~2 days** |
| **Enterprise Monorepo** | 4h | 4h | 8h | 16h | 8h | **~5 days** |

**Note**: Times based on post-portability improvements (target state)

---

## Architecture Principles

### 1. Separation of Concerns
- **Core Logic**: Validation, state, workflow (portable)
- **Infrastructure**: Git, GitHub, file system (adaptable)
- **Configuration**: Runtime settings (customizable)
- **Providers**: VCS, AI, language-specific (pluggable)

### 2. Dependency Inversion
- High-level modules don't depend on low-level details
- Both depend on abstractions (VCSProvider, AIProvider)
- Inject dependencies rather than hardcode

### 3. Open/Closed Principle
- Open for extension (custom slash commands, providers)
- Closed for modification (core workflow logic stable)
- Plugin architecture for new features

### 4. Fail-Safe Defaults
- Default paths work for 80% of Python projects
- Graceful degradation (R2 optional, E2B optional)
- Clear error messages guide configuration

### 5. Progressive Enhancement
- Basic: Manual setup, GitHub-only, Claude-only
- Enhanced: Auto-setup, multi-VCS, multi-AI
- Advanced: Custom workflows, integrations, plugins

---

## Design Patterns Used

1. **State Pattern** (`adw_modules/state.py`)
   - Persistent state across workflow phases
   - File-based storage for simplicity
   - JSON serialization via Pydantic

2. **Strategy Pattern** (Future: Providers)
   - VCS provider strategy (GitHub, GitLab, Bitbucket)
   - AI provider strategy (Claude, GPT, Gemini)
   - Language template strategy (Python, Java, JS)

3. **Template Method** (Workflow scripts)
   - Plan → Build → Test → Review → Document
   - Each step follows same pattern
   - Customizable steps via config

4. **Factory Pattern** (Future: Provider factories)
   - `get_vcs_provider()` based on repo URL
   - `get_ai_provider()` based on config
   - Auto-detection with fallbacks

5. **Facade Pattern** (`adw_common.py`)
   - Simplified interface to complex subsystems
   - Git operations abstracted
   - Path utilities centralized

---

## Technology Stack

### Core Dependencies
- **Python 3.10+**: Type hints, dataclasses, modern syntax
- **Pydantic 2.x**: Data validation, settings management
- **PyYAML**: Configuration file parsing
- **Click**: CLI framework (future)
- **python-dotenv**: Environment variables

### External Tools
- **git**: Version control operations
- **gh**: GitHub CLI for issues/PRs
- **claude**: Claude Code CLI (optional)

### Optional Dependencies
- **boto3**: R2/S3 uploads (screenshots)
- **e2b**: Cloud sandbox execution
- **pytest**: Testing framework
- **black/ruff**: Code formatting/linting

---

## Related Documentation

### In This Repository
- `/docs/WORKFLOW_ARCHITECTURE.md` - Workflow design
- `/docs/SPEC_SCHEMA.md` - Plan document format
- `/docs/SETUP.md` - Installation guide
- `/CLAUDE.md` - Agent instructions

### External Resources
- [Pydantic Docs](https://docs.pydantic.dev/) - Validation library
- [Click Docs](https://click.palletsprojects.com/) - CLI framework
- [GitHub CLI Manual](https://cli.github.com/manual/) - `gh` command
- [Python Packaging](https://packaging.python.org/) - PyPI distribution

---

## Contributing to Portability

### How to Help

1. **Test on Your Project**
   - Try installing on different project types
   - Report compatibility issues
   - Share configuration examples

2. **Contribute Code**
   - Pick a task from [PORTABILITY_IMPLEMENTATION_ROADMAP.md](./PORTABILITY_IMPLEMENTATION_ROADMAP.md)
   - Follow Python best practices
   - Add tests for new features

3. **Improve Documentation**
   - Add migration examples
   - Create troubleshooting guides
   - Record video walkthroughs

4. **Build Providers**
   - Implement GitLab/Bitbucket support
   - Create GPT-4/Gemini providers
   - Add language templates

### Contribution Workflow

```bash
# 1. Fork repository
git clone https://github.com/alexkamysz/scout_plan_build_mvp.git
cd scout_plan_build_mvp

# 2. Create feature branch
git checkout -b portability/config-system

# 3. Implement (follow roadmap)
# Edit code, add tests

# 4. Test
pytest tests/
adws health-check

# 5. Submit PR
git push origin portability/config-system
# Create PR on GitHub
```

---

## Questions & Support

- **General Questions**: File an issue with `[portability]` tag
- **Implementation Help**: Comment on roadmap document
- **Bug Reports**: Use `[bug][portability]` tags
- **Feature Requests**: Use `[enhancement][portability]` tags

---

**Maintained By**: System Architecture Team
**Last Updated**: 2025-10-25
**Next Review**: After Phase 1 completion (Week 1)
**Version**: 1.0 (Initial portability analysis)
