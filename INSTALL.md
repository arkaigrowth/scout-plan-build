# Scout-Plan-Build Framework Installation Guide

**Single source of truth for installation.** This document replaces all previous scattered installation docs.

---

## Quick Install (30 seconds)

```bash
# From the scout_plan_build_mvp directory:
./scripts/install_to_new_repo.sh /path/to/your/repo

# Then in your target repo:
cd /path/to/your/repo
cp .env.template .env
# Edit .env with your API keys
python test_installation.py
```

That's it. Your repo now has Scout-Plan-Build.

---

## What Gets Installed

```
your-repo/
├── adws/                    # Core workflow modules (Python)
│   ├── adw_plan.py          # Planning phase
│   ├── adw_build.py         # Build phase
│   └── adw_modules/         # Shared utilities
├── .claude/
│   ├── commands/            # 48 slash commands
│   │   ├── planning/        # /plan_w_docs_improved, etc.
│   │   ├── workflow/        # /build_adw, etc.
│   │   ├── git/             # /git:commit, etc.
│   │   ├── testing/         # /sc:test, etc.
│   │   └── ...
│   ├── hooks/               # Session tracking, logging
│   ├── skills/              # Workflow building blocks
│   └── output-styles/       # Coach mode styles (if copied)
├── specs/                   # Generated specifications go here
├── scout_outputs/           # Scout phase outputs
├── ai_docs/
│   ├── build_reports/       # Build execution reports
│   ├── research/            # Research documents
│   │   ├── sources/         # Raw inputs (articles, videos, etc.)
│   │   └── implementations/ # Synthesized outputs
│   └── sessions/            # Session handoffs
├── scripts/
│   ├── research-add.py      # URL extraction + synthesis (Gemini)
│   ├── spb_search.py        # Codebase search
│   └── validate_pipeline.sh # Validation script
├── agents/                  # Agent state tracking
├── agent_runs/              # Agent run artifacts
├── .env.template            # Environment variable template
├── .adw_config.json         # Project configuration
├── pyproject.toml           # Python dependencies
├── test_installation.py     # Post-install validation
└── CLAUDE.md                # Command router (read this!)
```

---

## Required Environment Variables

Create `.env` from template and set:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...          # Your Claude API key
GITHUB_PAT=ghp_...                    # GitHub Personal Access Token
GITHUB_REPO_URL=https://github.com/owner/repo

# Prevents token limit errors (IMPORTANT)
CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768

# Optional - for research-add.py URL extraction
GEMINI_API_KEY=...                    # Google Gemini API key
```

Load them:
```bash
export $(grep -v '^#' .env | xargs)
```

---

## Post-Install Validation

```bash
# Run the test script
python test_installation.py

# Expected output:
# ✅ Directory exists: specs
# ✅ Directory exists: agents
# ✅ Directory exists: ai_docs
# ✅ Directory exists: .claude/commands
# ✅ Directory exists: adws
# ✅ Core modules installed
# ✅ Slash commands installed
# ✨ Installation successful!
```

---

## Python Dependencies

The installer creates `pyproject.toml`. Install with:

```bash
# If using uv (recommended)
uv sync

# If using pip
pip install -e .
```

Dependencies include:
- pydantic, python-dotenv, gitpython
- anthropic, boto3
- google-genai (for research-add.py)
- httpx, pyyaml

---

## First Steps After Install

1. **Read CLAUDE.md** - The command router explains how to use the framework
2. **Try a simple task**:
   ```
   You: "Find all Python files related to authentication"
   → Framework uses Grep/Glob to find files
   ```
3. **Create your first spec**:
   ```bash
   /plan_w_docs_improved "Add feature X" "" "scout_outputs/files.json"
   ```
4. **Build from spec**:
   ```bash
   /build_adw "specs/your-spec.md"
   ```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `Slash commands missing` | Wrong path check | Commands are in subdirectories, not root |
| `ANTHROPIC_API_KEY not set` | Env not loaded | Run `export $(grep -v '^#' .env | xargs)` |
| `Token limit errors` | Missing env var | Set `CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768` |
| `google-genai not found` | Wrong Python | Install to active Python: `pip install google-genai` |
| `Permission denied` | Script not executable | `chmod +x scripts/*.sh scripts/*.py` |

---

## Uninstall

```bash
# From scout_plan_build_mvp:
./scripts/uninstall_from_repo.sh /path/to/your/repo
```

---

## For AI Agents

If you're an AI agent installing this framework:

1. **Run the installer**:
   ```bash
   ./scripts/install_to_new_repo.sh /absolute/path/to/target
   ```

2. **Copy coach output styles** (optional but recommended):
   ```bash
   mkdir -p /target/.claude/output-styles
   cp ~/.claude/output-styles/coach*.md /target/.claude/output-styles/
   ```

3. **Validate**:
   ```bash
   cd /target && python test_installation.py
   ```

4. **Read CLAUDE.md** in the target repo for usage instructions.

Key files to understand:
- `CLAUDE.md` - Command router, workflow patterns
- `adws/adw_plan.py` - Planning phase implementation
- `adws/adw_build.py` - Build phase implementation
- `.claude/commands/` - All slash commands

---

## Version Info

- **Framework Version**: 4.0
- **Last Updated**: 2025-12-22
- **Replaces**: docs/portability/*, specs/interactive-installer-menu.md, ai_docs/analyses/installer-implementation-spec.md
