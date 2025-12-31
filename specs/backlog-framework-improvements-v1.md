# Backlog: Scout-Plan-Build Framework Improvements

**Created**: 2025-12-24
**Source**: ARCHITECT_GUIDE research (4 parallel agents, very thorough)
**Research Location**: `ai_docs/architecture/_research/`
**Total Issues**: 21
**Parallelizable**: 17 (81%)

---

## Table of Contents

1. [Overview & Execution Strategy](#overview--execution-strategy)
2. [Issue Categories](#issue-categories)
3. [Parallel Execution Groups](#parallel-execution-groups)
4. [Detailed Issue Specifications](#detailed-issue-specifications)
5. [Deep-Dive References](#deep-dive-references)
6. [Acceptance Criteria Template](#acceptance-criteria-template)

---

## Overview & Execution Strategy

### Why This Backlog Exists

During creation of `ARCHITECT_GUIDE.md`, 4 parallel research agents uncovered 20+ issues blocking framework adoption and SOTA compliance. This spec enables systematic resolution via parallel subagent execution.

### Execution Philosophy

```
┌─────────────────────────────────────────────────────────┐
│ PARALLEL-FIRST APPROACH                                 │
├─────────────────────────────────────────────────────────┤
│ 1. Group issues by dependency (can run in parallel?)    │
│ 2. Spawn subagents per group (4-6 concurrent)          │
│ 3. Each agent: deep-dive → implement → test → PR       │
│ 4. Sequential only for: security (audit first)         │
└─────────────────────────────────────────────────────────┘
```

### Resource Estimates

| Metric | Value |
|--------|-------|
| Total issues | 21 |
| Critical (must fix) | 4 |
| High (should fix) | 6 |
| Medium (nice to have) | 10 |
| Low (cosmetic) | 1 |
| Parallelizable | 16 (80%) |
| Sequential required | 4 (security + dependencies) |
| Est. total effort | 40-60 agent-hours |
| With parallelization | 10-15 wall-clock hours |

---

## Issue Categories

### By Priority

| Priority | Count | Issues |
|----------|-------|--------|
| 🔴 CRITICAL | 4 | #1, #2, #3, #4 |
| 🟡 HIGH | 6 | #5, #6, #7, #8, #9, #10 |
| 🟢 MEDIUM | 10 | #11-#20 |

### By Type

| Type | Count | Issues |
|------|-------|--------|
| Security | 1 | #3 |
| Portability | 3 | #2, #4, #12 |
| Documentation | 5 | #5, #6, #7, #8, #17 |
| Architecture | 4 | #1, #9, #11, #13 |
| DX/Usability | 4 | #10, #15, #16, #18 |
| Quality | 3 | #14, #19, #20 |

### By Parallelizability

| Group | Can Parallelize? | Issues |
|-------|------------------|--------|
| Independent | ✅ Yes | #5, #6, #7, #8, #10, #13, #14, #15, #16, #17, #18 |
| Depends on #1 | After Scout fix | #11 (memory needs working scout) |
| Depends on #3 | After Security | #2, #4, #12 (portability after security audit) |
| Sequential | ❌ Must be ordered | #3 (security first), #9 (config enables others) |

---

## Parallel Execution Groups

### Group A: Documentation Fixes (5 issues, fully parallel)
**Can spawn 5 agents simultaneously**

| Issue | Summary | Complexity | Est. Time |
|-------|---------|------------|-----------|
| #5 | Version date inconsistency | Low | 30 min |
| #6 | Scout status contradictions | Low | 45 min |
| #7 | Generated CLAUDE.md outdated | Medium | 1 hr |
| #8 | Stale path references | Low | 45 min |
| #17 | SPB vs ADW terminology | Low | 30 min |

**Execution command**:
```bash
# Spawn 5 parallel agents
/init-parallel-worktrees docs-fixes 5
# Each worktree tackles one issue
```

---

### Group B: Command/Workflow Cleanup (4 issues, fully parallel)
**Can spawn 4 agents simultaneously**

| Issue | Summary | Complexity | Est. Time |
|-------|---------|------------|-----------|
| #10 | Plan commands overlap | Medium | 1.5 hr |
| #13 | Scout command sprawl | Medium | 2 hr |
| #15 | Worktree commands scattered | Medium | 1.5 hr |
| #16 | Coach mode underdocumented | Low | 45 min |

---

### Group C: Quality & Cleanup (4 issues, fully parallel)
**Can spawn 4 agents simultaneously**

| Issue | Summary | Complexity | Est. Time |
|-------|---------|------------|-----------|
| #14 | Missing test coverage | High | 3 hr |
| #18 | Orphaned scripts | Medium | 1 hr |
| #19 | State race conditions | Medium | 1.5 hr |
| #20 | Output paths not enforced | Medium | 1 hr |

---

### Group D: Architecture (Sequential - Dependencies)
**Must execute in order**

| Order | Issue | Summary | Depends On |
|-------|-------|---------|------------|
| 1 | #3 | Security vulnerabilities | None (FIRST) |
| 2 | #9 | No configuration system | #3 done |
| 3 | #1 | Scout phase broken | #9 done |
| 4 | #4 | Hardcoded directory paths | #9 done |
| 5 | #2 | GitHub-only coupling | #3, #9 done |
| 6 | #12 | No provider abstraction | #9 done |
| 7 | #11 | Stateless subprocess pattern | #1 done |

---

## Detailed Issue Specifications

---

### Issue #1: Scout Phase 70% Broken

**Priority**: 🔴 CRITICAL
**Type**: Architecture
**Parallelizable**: No (others depend on this)
**Complexity**: High
**Est. Time**: 4-6 hours

#### Problem Statement

Scout phase assumes external CLI tools exist (`gemini`, `opencode`, `codex`) but they are not installed in typical environments. 70% of scout failures trace to missing tools, not logic errors.

#### Current State

```python
# adws/scout_simple.py - BROKEN PATTERN
def scout(keyword):
    # Assumes 'gemini' CLI exists - IT DOESN'T
    result = subprocess.run(["gemini", "search", keyword], ...)
```

#### Affected Files

| File | Issue | Line Range |
|------|-------|------------|
| `adws/scout_simple.py` | External tool assumptions | Throughout |
| `adws/adw_scout_parallel.py` | Same pattern | Throughout |
| `.claude/commands/workflow/scout.md` | References broken impl | All |
| `.claude/commands/workflow/scout_parallel.md` | References broken impl | All |
| `adws/adw_modules/gemini_search.py` | Assumes Gemini CLI | All |

#### Deep-Dive Steps

1. **Read current implementations**:
   ```
   Read adws/scout_simple.py
   Read adws/adw_scout_parallel.py
   Read adws/adw_modules/gemini_search.py
   ```

2. **Understand working pattern**:
   ```
   Read .claude/commands/workflow/scout_improved.md
   Read .claude/commands/workflow/scout_fixed.md
   ```

3. **Check what native tools are available**:
   - `Grep` tool (always available)
   - `Glob` tool (always available)
   - `Task(Explore)` agent (always available)

4. **Research existing patterns**:
   ```
   Read ai_docs/architecture/_research/03-learnings.md
   # Section: "Scout Phase Broken by Assumptions"
   ```

#### Solution Approach

```python
# FIXED PATTERN - Use native tools only
def scout(keyword: str, file_patterns: list[str]) -> dict:
    """Scout using native Grep/Glob only."""
    results = {
        "files": [],
        "matches": []
    }

    # Use Glob for file discovery
    for pattern in file_patterns:
        files = glob(pattern)  # Native tool
        results["files"].extend(files)

    # Use Grep for content search
    matches = grep(keyword, type="py")  # Native tool
    results["matches"] = matches

    return results
```

#### Acceptance Criteria

- [ ] `scout_simple.py` works without external tools
- [ ] All 4 scout commands use same native implementation
- [ ] Deprecated commands removed or redirect to working version
- [ ] `scout_outputs/relevant_files.json` format unchanged
- [ ] Tests pass: `python -m pytest adws/adw_tests/test_scout.py`
- [ ] Documentation updated in CLAUDE.md

#### Test Commands

```bash
# After fix, this should work without gemini/opencode/codex installed
python adws/scout_simple.py "authentication" "**/*.py"

# Should produce valid JSON
cat scout_outputs/relevant_files.json | python -m json.tool
```

---

### Issue #2: GitHub-Only Coupling

**Priority**: 🔴 CRITICAL
**Type**: Portability
**Parallelizable**: After #3 (security) and #9 (config)
**Complexity**: High
**Est. Time**: 6-8 hours

#### Problem Statement

Framework requires GitHub Issues and `gh` CLI everywhere. No local/offline mode, no bypass. Blocks adoption in Bitbucket, GitLab, self-hosted Git, and testing scenarios.

#### Current State

```python
# adws/adw_modules/github.py - HARDCODED
def get_issue(issue_number: int):
    result = subprocess.run(["gh", "issue", "view", str(issue_number), "--json", ...])
    # No abstraction, no fallback, no alternative providers
```

#### Affected Files

| File | Issue | Line Range |
|------|-------|------------|
| `adws/adw_modules/github.py` | Hardcoded `gh` CLI | Throughout |
| `adws/adw_modules/git_ops.py` | GitHub-specific ops | Throughout |
| `adws/adw_triggers/trigger_webhook.py` | GitHub webhook only | Throughout |
| `adws/adw_plan.py` | Assumes GitHub issue | Lines 50-100 |
| `adws/adw_build.py` | GitHub PR operations | Lines 80-120 |

#### Deep-Dive Steps

1. **Map all GitHub touchpoints**:
   ```bash
   Grep "gh " --type py path=adws/
   Grep "github" --type py path=adws/
   Grep "GitHubError" --type py path=adws/
   ```

2. **Read portability analysis**:
   ```
   Read ai_docs/architecture/PORTABILITY_ANALYSIS.md
   Read ai_docs/architecture/PORTABILITY_IMPLEMENTATION_ROADMAP.md
   ```

3. **Understand VCS detection**:
   ```
   Read adws/adw_modules/vcs_detection.py
   Read adws/adw_modules/bitbucket_ops.py  # Exists but incomplete
   ```

#### Solution Approach

```python
# vcs_provider.py - NEW ABSTRACTION
from abc import ABC, abstractmethod

class VCSProvider(ABC):
    @abstractmethod
    def get_issue(self, issue_id: str) -> dict: ...

    @abstractmethod
    def create_pr(self, title: str, body: str, branch: str) -> str: ...

    @abstractmethod
    def add_comment(self, issue_id: str, comment: str) -> None: ...

class GitHubProvider(VCSProvider):
    def get_issue(self, issue_id: str) -> dict:
        # Existing gh CLI implementation
        ...

class GitLabProvider(VCSProvider):
    def get_issue(self, issue_id: str) -> dict:
        # GitLab API implementation
        ...

class LocalProvider(VCSProvider):
    """For offline/testing - reads from local markdown files."""
    def get_issue(self, issue_id: str) -> dict:
        # Read from specs/issues/{issue_id}.md
        ...
```

#### Acceptance Criteria

- [ ] `VCSProvider` abstract base class created
- [ ] `GitHubProvider` works (existing functionality preserved)
- [ ] `LocalProvider` works for offline testing
- [ ] Config selects provider: `VCS_PROVIDER=github|gitlab|local`
- [ ] All `adw_*.py` scripts use provider abstraction
- [ ] Webhook handler supports multiple providers
- [ ] Tests pass with `VCS_PROVIDER=local`

---

### Issue #3: Security Vulnerabilities

**Priority**: 🔴 CRITICAL
**Type**: Security
**Parallelizable**: NO - Must be FIRST
**Complexity**: High
**Est. Time**: 4-5 hours

#### Problem Statement

5 security vulnerabilities identified in pre-release audit. Must be fixed before any public release or broader adoption.

#### Vulnerabilities

| # | Type | Location | Severity |
|---|------|----------|----------|
| 3.1 | Command Injection | `scout_simple.py` | HIGH |
| 3.2 | Missing Webhook Signature | `trigger_webhook.py` | HIGH |
| 3.3 | Unvalidated JSON Payload | `trigger_webhook.py` | MEDIUM |
| 3.4 | Path Traversal | `validators.py` | MEDIUM |
| 3.5 | Secret Logging | Multiple files | LOW |

#### Deep-Dive Steps

1. **Read security assessment**:
   ```
   Read ai_docs/architecture/_research/03-learnings.md
   # Section: "Functionality Issues" → Security vulnerabilities
   ```

2. **Audit affected files**:
   ```
   Read adws/scout_simple.py
   Read adws/adw_triggers/trigger_webhook.py
   Read adws/adw_modules/validators.py
   ```

3. **Check for secret patterns**:
   ```bash
   Grep "api_key" --type py
   Grep "password" --type py
   Grep "secret" --type py
   Grep "token" --type py
   ```

#### Solution Approach

**3.1 Command Injection Fix**:
```python
# BEFORE (vulnerable)
subprocess.run(f"grep {keyword} *.py", shell=True)

# AFTER (safe)
import shlex
subprocess.run(["grep", shlex.quote(keyword), "*.py"], shell=False)
```

**3.2 Webhook Signature Verification**:
```python
import hmac
import hashlib

def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

**3.3 JSON Payload Validation**:
```python
from pydantic import BaseModel, validator

class WebhookPayload(BaseModel):
    action: str
    issue: dict

    @validator('action')
    def validate_action(cls, v):
        allowed = ['opened', 'edited', 'closed', 'labeled']
        if v not in allowed:
            raise ValueError(f"Invalid action: {v}")
        return v
```

**3.4 Path Traversal Prevention**:
```python
import os

def safe_path(base_dir: str, user_path: str) -> str:
    """Prevent path traversal attacks."""
    # Resolve to absolute, check it's under base_dir
    full_path = os.path.realpath(os.path.join(base_dir, user_path))
    if not full_path.startswith(os.path.realpath(base_dir)):
        raise ValueError(f"Path traversal attempt: {user_path}")
    return full_path
```

**3.5 Secret Sanitization**:
```python
import re

def sanitize_for_logging(text: str) -> str:
    """Remove secrets from log output."""
    patterns = [
        r'sk-ant-[a-zA-Z0-9-_]+',  # Anthropic keys
        r'ghp_[a-zA-Z0-9]+',        # GitHub PAT
        r'ghu_[a-zA-Z0-9]+',        # GitHub user token
        r'password["\s:=]+\S+',     # Passwords
    ]
    for pattern in patterns:
        text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)
    return text
```

#### Acceptance Criteria

- [ ] Command injection fixed in `scout_simple.py`
- [ ] Webhook signature verification added
- [ ] Pydantic validation for webhook payloads
- [ ] Path traversal protection in validators
- [ ] Secret sanitization in logging
- [ ] Security tests added: `adws/adw_tests/test_security.py`
- [ ] No secrets in git history (verify with `git log -p | grep -i "sk-ant"`)

---

### Issue #4: Hardcoded Directory Paths

**Priority**: 🔴 CRITICAL
**Type**: Portability
**Parallelizable**: After #9 (config system)
**Complexity**: Medium
**Est. Time**: 3-4 hours

#### Problem Statement

`specs/`, `agents/`, `ai_docs/`, `scout_outputs/` are hardcoded throughout validators and adw_modules. Cannot run on different directory structure or in monorepo.

#### Affected Files

| File | Hardcoded Paths |
|------|-----------------|
| `adws/adw_modules/validators.py` | `specs/`, `agents/` |
| `adws/adw_modules/state.py` | `agents/{adw_id}/` |
| `adws/adw_modules/file_organization.py` | All output dirs |
| `adws/adw_modules/workflow_ops.py` | `specs/`, `scout_outputs/` |
| `.claude/commands/workflow/*.md` | Various paths |

#### Deep-Dive Steps

```bash
Grep "specs/" --type py path=adws/
Grep "agents/" --type py path=adws/
Grep "ai_docs/" --type py path=adws/
Grep "scout_outputs/" --type py path=adws/
```

#### Solution Approach

```python
# adw_modules/config.py - NEW
from pathlib import Path
import os

class ADWConfig:
    """Centralized path configuration."""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()

    @property
    def specs_dir(self) -> Path:
        return Path(os.environ.get("ADW_SPECS_DIR", self.base_dir / "specs"))

    @property
    def agents_dir(self) -> Path:
        return Path(os.environ.get("ADW_AGENTS_DIR", self.base_dir / "agents"))

    @property
    def ai_docs_dir(self) -> Path:
        return Path(os.environ.get("ADW_AI_DOCS_DIR", self.base_dir / "ai_docs"))

    @property
    def scout_outputs_dir(self) -> Path:
        return Path(os.environ.get("ADW_SCOUT_DIR", self.base_dir / "scout_outputs"))

# Usage in other modules
config = ADWConfig()
spec_path = config.specs_dir / f"{adw_id}_plan_spec.md"
```

#### Acceptance Criteria

- [ ] `ADWConfig` class created with all paths
- [ ] Environment variable overrides work
- [ ] All hardcoded paths replaced with config references
- [ ] Default behavior unchanged (backward compatible)
- [ ] Works in monorepo structure
- [ ] Tests pass with custom paths

---

### Issue #5: Version Date Inconsistency

**Priority**: 🟡 HIGH
**Type**: Documentation
**Parallelizable**: ✅ Yes
**Complexity**: Low
**Est. Time**: 30 minutes

#### Problem Statement

README.md (11-24), INSTALL.md (12-22), CLAUDE.md (11-22) all claim version 4.0 but have different dates.

#### Affected Files

- `README.md` - Line ~3
- `INSTALL.md` - Line ~3
- `CLAUDE.md` - Line ~3
- `ai_docs/architecture/DIRECTORY_STRUCTURE.md` - Line ~3

#### Solution

1. Set all dates to current date
2. Add version changelog or remove dates entirely
3. Consider: Single source of truth for version (package.json or pyproject.toml)

#### Acceptance Criteria

- [ ] All version headers consistent
- [ ] Dates match or removed
- [ ] Single source of version truth identified

---

### Issue #6: Scout Status Contradictions

**Priority**: 🟡 HIGH
**Type**: Documentation
**Parallelizable**: ✅ Yes (but coordinate with #1)
**Complexity**: Low
**Est. Time**: 45 minutes

#### Problem Statement

- README says: "Scout ⚠️ 70% broken with external tools"
- CLAUDE.md says: "Scout Commands ❌ 40% broken"
- Natural Language Guide says: "Scout phase: 70% broken"
- Multiple scout commands still exist

#### Solution

1. Audit actual scout status (after #1 is fixed)
2. Update all docs to consistent status
3. Add deprecation notices to broken commands

#### Acceptance Criteria

- [ ] All docs show same scout status
- [ ] Broken commands marked deprecated
- [ ] Working command clearly identified

---

### Issue #7: Generated CLAUDE.md Outdated

**Priority**: 🟡 HIGH
**Type**: Documentation
**Parallelizable**: ✅ Yes
**Complexity**: Medium
**Est. Time**: 1 hour

#### Problem Statement

`install_to_new_repo.sh` generates a CLAUDE.md that references deprecated commands like `python adws/scout_simple.py` and `/plan_w_docs` instead of `/plan_w_docs_improved`.

#### Affected Files

- `scripts/install_to_new_repo.sh` - CLAUDE.md template section

#### Deep-Dive Steps

```
Read scripts/install_to_new_repo.sh
# Find the heredoc that generates CLAUDE.md
# Compare to actual CLAUDE.md in repo root
```

#### Acceptance Criteria

- [ ] Generated CLAUDE.md matches repo CLAUDE.md patterns
- [ ] References only working commands
- [ ] Includes current workflow decision tree

---

### Issue #8: Stale Path References

**Priority**: 🟡 HIGH
**Type**: Documentation
**Parallelizable**: ✅ Yes
**Complexity**: Low
**Est. Time**: 45 minutes

#### Problem Statement

`ai_docs/scout/` was removed but still referenced in 8 root-level .md files.

#### Deep-Dive Steps

```bash
Grep "ai_docs/scout" path=.
Grep "scout/" --type md path=.
```

#### Acceptance Criteria

- [ ] No references to removed directories
- [ ] All path references point to existing locations
- [ ] Verified with grep after fix

---

### Issue #9: No Configuration System

**Priority**: 🟡 HIGH
**Type**: Architecture
**Parallelizable**: No (enables #4, #2, #12)
**Complexity**: Medium
**Est. Time**: 2-3 hours

#### Problem Statement

All config via environment variables. No YAML/settings module. Makes customization difficult and error-prone.

#### Solution Approach

```yaml
# .adw_config.yaml
version: "1.0"

paths:
  specs: specs/
  agents: agents/
  ai_docs: ai_docs/
  scout_outputs: scout_outputs/

providers:
  vcs: github  # github | gitlab | local
  ai: claude   # claude | openai | gemini

options:
  parallel_agents: 4
  timeout_seconds: 180
  auto_commit: false
```

```python
# adw_modules/config.py
import yaml
from pathlib import Path
from pydantic import BaseModel

class ADWConfig(BaseModel):
    paths: PathsConfig
    providers: ProvidersConfig
    options: OptionsConfig

    @classmethod
    def load(cls, path: Path = None) -> "ADWConfig":
        path = path or Path(".adw_config.yaml")
        if path.exists():
            with open(path) as f:
                return cls(**yaml.safe_load(f))
        return cls()  # Defaults
```

#### Acceptance Criteria

- [ ] `.adw_config.yaml` schema defined
- [ ] `ADWConfig` Pydantic model created
- [ ] Env vars override config file
- [ ] Defaults match current behavior
- [ ] All modules use config

---

### Issue #10: Plan Commands Overlap

**Priority**: 🟡 HIGH
**Type**: DX/Usability
**Parallelizable**: ✅ Yes
**Complexity**: Medium
**Est. Time**: 1.5 hours

#### Problem Statement

`/plan_w_docs` vs `/plan_w_docs_improved` are similar. Plus `/feature`, `/bug`, `/chore`, `/patch` exist as issue-specific variants. Unclear when to use which.

#### Deep-Dive Steps

```
Read .claude/commands/planning/plan_w_docs.md
Read .claude/commands/planning/plan_w_docs_improved.md
Read .claude/commands/planning/feature.md
Read .claude/commands/planning/bug.md
```

#### Solution

1. Deprecate `/plan_w_docs` → redirect to `_improved`
2. Document clear decision tree:
   - GitHub issue exists → `/feature|bug|chore|patch`
   - No issue, general planning → `/plan_w_docs_improved`

#### Acceptance Criteria

- [ ] Clear decision tree in CLAUDE.md
- [ ] Deprecated command shows warning + redirect
- [ ] Each command has distinct, documented purpose

---

### Issue #11: Stateless Subprocess Pattern

**Priority**: 🟢 MEDIUM
**Type**: Architecture
**Parallelizable**: After #1 (Scout fix)
**Complexity**: High
**Est. Time**: 4-6 hours

#### Problem Statement

Each `subprocess.run(["claude"])` starts fresh with no memory. Agents repeat expensive analysis, rediscover patterns every time.

#### Deep-Dive Steps

```
Read ai_docs/architecture/_research/03-learnings.md
# Section: "Stateless Subprocess Anti-Pattern"

Read ai_docs/architecture/MEM0_INTEGRATION_ARCHITECTURE.md
Read ai_docs/architecture/MEM0_INTEGRATION_SUMMARY.md
```

#### Solution Approach

Integrate mem0 or Serena MCP for cross-session learning:

```python
# adw_modules/memory.py
from mem0 import Memory

memory = Memory()

def remember(key: str, value: str, metadata: dict = None):
    """Store learning for future sessions."""
    memory.add(value, user_id=key, metadata=metadata)

def recall(key: str, query: str, limit: int = 5) -> list:
    """Retrieve relevant memories."""
    return memory.search(query, user_id=key, limit=limit)

# Usage in scout
previous_scouts = recall("scout", f"files for {keyword}")
if previous_scouts:
    # Skip re-scouting, use cached results
    return previous_scouts[0]
```

#### Acceptance Criteria

- [ ] Memory integration optional (config toggle)
- [ ] Scout results cached for reuse
- [ ] Pattern recognition improves over time
- [ ] 2-3x speedup on repeated tasks

---

### Issues #12-#20: Medium Priority

For brevity, summarized specifications:

| Issue | Summary | Complexity | Key Files |
|-------|---------|------------|-----------|
| #12 | Provider abstraction | High | `agent.py` |
| #13 | Scout consolidation | Medium | `.claude/commands/workflow/scout*.md` |
| #14 | Missing test coverage | High | `adws/adw_tests/` |
| #15 | Worktree docs scattered | Medium | `.claude/commands/git/` |
| #16 | Coach mode undocumented | Low | `CLAUDE.md`, `COACH_MODE.md` |
| #17 | SPB vs ADW terminology | Low | All docs |
| #18 | Orphaned scripts | Medium | `scripts/` |
| #19 | State race conditions | Medium | `state.py` |
| #20 | Output paths unenforced | Medium | Add pre-commit hook |

---

## Deep-Dive References

### Research Documents

| File | Contains |
|------|----------|
| `ai_docs/architecture/_research/01-core-docs.md` | Installation, workflows, philosophy |
| `ai_docs/architecture/_research/02-architecture.md` | Component map, data flow, structure |
| `ai_docs/architecture/_research/03-learnings.md` | Best practices, anti-patterns, perf |
| `ai_docs/architecture/_research/04-commands.md` | 50 commands, risk levels, examples |

### Architecture Documents

| File | Relevant For |
|------|--------------|
| `ai_docs/architecture/PORTABILITY_ANALYSIS.md` | Issues #2, #4, #12 |
| `ai_docs/architecture/PORTABILITY_IMPLEMENTATION_ROADMAP.md` | Issues #2, #4, #12 |
| `ai_docs/architecture/MEM0_INTEGRATION_ARCHITECTURE.md` | Issue #11 |
| `ai_docs/architecture/ARCHITECTURE_INDEX.md` | Overall system |

### Key Source Files

| File | Relevant For |
|------|--------------|
| `adws/adw_modules/validators.py` | Issues #3, #4 |
| `adws/adw_modules/github.py` | Issue #2 |
| `adws/scout_simple.py` | Issues #1, #3 |
| `adws/adw_triggers/trigger_webhook.py` | Issue #3 |
| `scripts/install_to_new_repo.sh` | Issue #7 |

---

## Acceptance Criteria Template

For agents tackling individual issues, use this template:

```markdown
## Issue #N: [Title]

### Pre-Implementation
- [ ] Read all affected files
- [ ] Read relevant research docs
- [ ] Understand current behavior
- [ ] Create feature branch: `fix/issue-N-short-name`

### Implementation
- [ ] Code changes complete
- [ ] No new lint errors
- [ ] No regressions in existing tests
- [ ] New tests added if applicable

### Documentation
- [ ] CLAUDE.md updated if commands changed
- [ ] Inline comments for complex logic
- [ ] Research findings noted if any

### Validation
- [ ] `python -m pytest adws/adw_tests/` passes
- [ ] Manual testing of affected workflows
- [ ] Verified fix with grep/search

### Completion
- [ ] Commit with descriptive message
- [ ] PR created with summary
- [ ] Linked to this backlog issue
```

---

## Execution Commands

### Start Parallel Documentation Fixes (Group A)

```bash
# Create 5 worktrees for doc fixes
/init-parallel-worktrees docs-fixes 5

# Assign issues to worktrees
# worktree 1: Issue #5 (versions)
# worktree 2: Issue #6 (scout status)
# worktree 3: Issue #7 (generated CLAUDE.md)
# worktree 4: Issue #8 (stale paths)
# worktree 5: Issue #17 (terminology)
```

### Start Sequential Security Fix (Group D - First)

```bash
# Security must be first, solo
git checkout -b fix/issue-3-security-vulnerabilities

# Deep dive
Read adws/scout_simple.py
Read adws/adw_triggers/trigger_webhook.py
Read adws/adw_modules/validators.py

# Implement fixes...
```

---

## Issue #21: Directory Structure Reorganization

**Priority**: 🔵 LOW (cosmetic, not functional)
**Type**: Organization/DX
**Parallelizable**: ✅ Yes (after #9)
**Depends On**: Issue #9 (Config System)
**Complexity**: High
**Est. Time**: 8-12 hours

### Problem Statement

Current directory structure is disorganized (6/10):
- `scout_outputs/` at root (transient data mixed with project structure)
- `agents/` vs `agent_outputs/` vs `agent_runs/` (3 dirs for similar purpose)
- `ai_docs/` sprawling (15+ subdirs, some empty)
- No clear organizing principle (by producer? consumer? lifecycle?)

### Scope of Change

| Metric | Count |
|--------|-------|
| Total path occurrences | 1,274 |
| Total files affected | 237 |
| Python files (core) | 15 |
| Python files (backups) | 20 |
| Command files | 10 |
| Documentation | ~190 |

### Proposed New Structure

```
project/
├── _ai/                    # Transient AI working data (visible, sorts first)
│   ├── scout/              # Scout discovery outputs
│   ├── agents/             # Workflow execution state (ADW - per task)
│   ├── memory/             # 🆕 Cross-session memory (mem0, Serena - cumulative)
│   │   └── state.json      # Machine-readable session state
│   ├── traces/             # Execution traces
│   └── cache/              # Cached analyses
│
├── ai_docs/                # Docs FOR AI to read (not "by AI" - everything is!)
│   ├── architecture/       # System design docs
│   ├── analyses/           # Completed analyses
│   ├── decisions/          # 🆕 Architecture Decision Records (ADRs)
│   ├── research/           # Research materials
│   └── sessions/           # Session handoffs (existing)
│
├── specs/                  # Implementation specs (unchanged)
├── docs/                   # Human documentation (unchanged)
└── scripts/                # Utilities (unchanged)
```

### Naming Clarification

**`ai_docs/` = Docs FOR AI consumption, not "written by AI"**

| Folder | Purpose | Consumer |
|--------|---------|----------|
| `ai_docs/` | Structured reference for context loading | AI agents |
| `docs/` | Narrative documentation for understanding | Humans |

Everything is written by AI now. The distinction is WHO READS IT:
- `ai_docs/`: Optimized for AI context loading, structured, machine-parseable
- `docs/`: Optimized for human reading, narrative, explanatory

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `_ai/` not `.ai/` | Visible in file pickers, `@` symbol works |
| `_ai/` not `ai_docs/scout/` | Different lifecycle (transient vs persistent) |
| Consolidate 3 agent dirs | `agents/`, `agent_outputs/`, `agent_runs/` → `_ai/agents/` |
| Keep `ai_docs/` | Curated reference docs, different purpose |
| Add `_ai/memory/` | Separate cross-session memory (mem0) from per-task workflow state |
| Add `ai_docs/decisions/` | ADRs are a proven pattern for documenting "why X over Y" |
| Keep `analyses/` name | "Assessments" is lateral, not better. 29 existing files. |
| Gitignore `_ai/` | Transient data shouldn't be committed (regenerable) |

### Greenfield Projects (New Repos Without Existing ADW)

**Greenfield** = A brand new project with no existing codebase or tooling to maintain compatibility with. (Like building on an empty "green field" vs renovating an existing building.)

For greenfield projects, use this **enhanced structure with spec lifecycle directories**:

```
project/
├── _ai/                         # Transient (gitignored)
│   ├── scout/
│   ├── agents/
│   ├── memory/
│   ├── traces/
│   └── cache/
│
├── ai_docs/                     # Persistent (committed)
│   ├── architecture/
│   ├── analyses/
│   ├── decisions/               # ADRs
│   ├── research/
│   └── sessions/
│
├── specs/                       # 🆕 With lifecycle subdirectories
│   ├── active/                  # Currently being implemented
│   ├── completed/               # Done, archived for reference
│   └── backlog/                 # Future work, not started
│
├── docs/                        # Human documentation
└── scripts/                     # Utilities
```

**Why lifecycle subdirectories for greenfield?**
- Visual clarity: instantly see what's active vs done
- No legacy tooling to break (no existing `adw_state.json` paths)
- Matches Kanban-style workflow (backlog → active → completed)
- Easy cleanup: archive completed specs without deleting

**NOT recommended for existing SPB repos** because:
- `adw_state.json` stores `plan_file: "specs/xxx.md"` paths
- Moving files would break these references
- Would require tooling updates to handle path changes

### Gitignore Configuration

Add to `.gitignore` for new projects:

```gitignore
# AI operational data (transient, regenerable)
_ai/

# But DO commit curated AI docs
!ai_docs/
```

### Deep-Dive Steps

1. **Check central path definitions**:
   ```
   Read adws/adw_modules/constants.py  # 12 refs - central definition
   Read adws/adw_modules/file_organization.py
   ```

2. **Understand current flow**:
   ```
   Grep "scout_outputs" --type py path=adws/
   Grep "agents/" --type py path=adws/
   ```

3. **Review install script**:
   ```
   Read scripts/install_to_new_repo.sh  # Creates directories
   ```

### Implementation Strategy

**DO NOT do this as a breaking change.** Instead:

1. **Complete Issue #9 (Config System) first**
2. **Add path configurability to config**:
   ```python
   # adw_modules/config.py
   class ADWConfig:
       # Backward compatible defaults
       scout_dir: str = "scout_outputs/"
       agents_dir: str = "agents/"

       # New installs can override
       # scout_dir: str = "_ai/scout/"
       # agents_dir: str = "_ai/agents/"
   ```
3. **Update install script** to use new defaults for fresh installs
4. **Existing installs keep working** with old paths
5. **Migration script** for users who want to upgrade

### Acceptance Criteria

- [ ] Issue #9 (Config System) completed first
- [ ] All paths read from config, not hardcoded
- [ ] New installs get cleaner `_ai/` structure
- [ ] Existing installs continue working unchanged
- [ ] Migration script available for opt-in upgrade
- [ ] ARCHITECT_GUIDE.md updated with new structure
- [ ] Install script uses new defaults

### Why Not Now?

| Factor | Assessment |
|--------|------------|
| Functional value | Zero - current paths work |
| Effort | High - 237 files, 1274 changes |
| Risk | Medium - could break existing installs |
| Dependencies | Needs config system first |
| Priority | Cosmetic improvement, not functional |

**Verdict**: Add to backlog, do AFTER critical issues (#1-4) and config system (#9).

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Scout success rate | 30% | 95% |
| Portability score | 72/100 | 90/100 |
| Security vulnerabilities | 5 | 0 |
| Documentation consistency | 60% | 95% |
| Test coverage | ~40% | 80% |
| Command clarity | Confusing | Clear decision tree |

---

**Document Version**: 1.0
**Created**: 2025-12-24
**Location**: `specs/backlog-framework-improvements-v1.md`
