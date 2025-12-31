# Core Documentation Research

**Agent**: Explore (very thorough)
**Date**: 2025-12-24
**Files Analyzed**: README.md, INSTALL.md, CLAUDE.md

---

## Value Proposition

**The Problem SPB Solves:**
- AI coding assistants are powerful but chaotic - without structure, they create sprawling conversations that lose context
- No clear separation between planning and building phases
- Files are dumped in random locations with no canonical organization
- Unable to resume work after a break due to lost context
- Dependency analysis across large codebases requires 50K+ tokens manually

**Why Use Scout-Plan-Build:**
1. **Enforced Workflow Structure**: Discover → Plan → Build follows a deterministic pattern
2. **Traceable Operations**: Every step is documented, every output has a canonical location
3. **40-50% Speed Improvement**: Parallel execution (test, review, document simultaneously)
4. **95% Token Reduction**: Smart tools like dependency-tracer minimize context consumption
5. **Session Continuity**: Handoff documents allow resuming after breaks
6. **Validated Framework**: Built using itself - every feature was spec'd, built, and refined through the workflow

**Core Benefit Statement:** "Structured AI development workflows that actually ship" - turning chaotic AI conversations into deterministic, traceable, resumable development processes.

---

## Philosophy & Principles

**Core Philosophy:**
- Evidence-based reasoning over assumptions
- Efficiency through parallelization and smart tooling
- Natural language first (describe your intent, framework routes to right tools)
- Validated through use (self-built using own workflow)

**Key Principles:**

1. **Separation of Concerns**
   - Scout phase: Discover relevant files (use native Grep/Glob, not external tools)
   - Plan phase: Create detailed specifications with requirements
   - Build phase: Implement from specifications deterministically

2. **Canonical Output Organization** (CRITICAL)
   - Specs → `specs/`
   - Build reports → `ai_docs/build_reports/`
   - Scout results → `scout_outputs/`
   - Analyses → `ai_docs/analyses/`
   - Reviews → `ai_docs/reviews/`
   - Research → `ai_docs/research/`
   - Session handoffs → `ai_docs/sessions/`

3. **Natural Language First**
   - Users describe what they want in plain English
   - Framework automatically routes to appropriate tools and commands
   - Commands available for those who need more control

4. **Token Efficiency**
   - 95% reduction on dependency analysis (3,100 tokens vs 60,000)
   - Intelligent summary modes to minimize context consumption
   - Coach mode with configurable overhead (5%, 15%, or 30%)

5. **Git-First Workflow**
   - Feature branches only (never work on main/master)
   - Incremental commits with meaningful messages
   - Git worktrees for parallel exploration of multiple approaches

---

## Installation

**Quick Install (30 seconds):**
```bash
./scripts/install_to_new_repo.sh /path/to/your/repo
cd /path/to/your/repo
cp .env.template .env
# Edit .env with your API keys
python test_installation.py
```

**Detailed Steps:**

1. **Run Installer** - `scripts/install_to_new_repo.sh`
2. **Directory Creation** - specs/, ai_docs/, .claude/commands/, adws/, agents/
3. **Files Copied** - 48 slash commands, hooks, skills, core modules
4. **Environment Variables**:
   - ANTHROPIC_API_KEY (required)
   - GITHUB_PAT (required)
   - GITHUB_REPO_URL (required)
   - CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768 (critical)
5. **Python Dependencies**: `uv sync` or `pip install -e .`
6. **Validation**: `python test_installation.py`

---

## Workflows

**Workflow Selection Decision Tree:**

```
What's your task?

├─ Simple (1-2 files, obvious fix)
│   └─ Just do it. No framework needed.
│
├─ Standard (3-5 files, clear requirements)
│   └─ /plan_w_docs_improved → /build_adw
│
├─ Complex (6+ files, new feature)
│   └─ Scout first → /plan_w_docs_improved → /build_adw
│
├─ Uncertain (multiple valid approaches)
│   └─ /init-parallel-worktrees → try each → /merge-worktree best
│
└─ Research (exploring unknown codebase)
    └─ Task(Explore) or native Grep/Glob
```

---

## Prerequisites

- Git repository (must have `.git/` directory)
- Python 3.9+ (3.10+ recommended)
- Bash shell (for installation script)
- API Keys: Anthropic, GitHub PAT, optional Gemini

---

## 🚩 Issues Found

### 1. Version Inconsistency
- README.md: "Last Updated: 2025-11-24"
- INSTALL.md: "Last Updated: 2025-12-22"
- CLAUDE.md: "Date Updated: 2025-11-22"
- All claim "Framework Version: 4.0"

### 2. Installation Script vs Generated CLAUDE.md Mismatch
- Generated version references deprecated `python adws/scout_simple.py`
- Generated version references `/plan_w_docs` but actual commands use `/plan_w_docs_improved`

### 3. Scout Phase Status Contradiction
- README says: "Scout ⚠️ 70% broken with external tools"
- CLAUDE.md says: "Scout Commands ❌ 40% broken"
- Multiple commands still exist but status unclear

### 4. Coach Mode Docs Incomplete
- References to "coach" command in multiple places
- Not clear if `/coach` is working slash command

### 5. Natural Language Guide Limitations Outdated
- States "Bitbucket: Currently GitHub-only (fixing this week)"
- Status section dated 2025-11-22

### 6. Python Dependency Discrepancies
- Installation script's auto-generated pyproject.toml lists minimal deps
- README references additional packages

### 7. Hardcoded Paths in Installation Script
- README says "Portability 🟡 85% - Some paths hardcoded"

### 8. 48 Commands Mentioned But Not Enumerated
- Categories listed but documentation scattered

### 9. Output Organization Not Enforced at Install
- No git hooks to prevent writing to wrong locations

### 10. Spec Schema Not Documented in Core Docs
- Users need to understand what `/plan_w_docs_improved` creates
