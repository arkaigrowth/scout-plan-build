# 🚀 Portable Deployment Guide

## Quick Deploy to Tax-Prep Repo (15 minutes)

### Step 1: Clean Your Agents (Optional but Recommended)
```bash
# Remove redundant agents that overlap with built-ins
./scripts/cleanup_agents.sh
```

### Step 2: Install to Your Tax Repo
```bash
# One command installation!
./scripts/install_to_new_repo.sh /path/to/your/tax-prep-repo
```

### Step 3: Configure
```bash
cd /path/to/your/tax-prep-repo
cp .env.template .env
nano .env  # Add your API keys:
           # - ANTHROPIC_API_KEY (required)
           # - GITHUB_PAT (for GitHub operations)
           # - CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768 (important!)
```

### Step 4: Activate & Test
```bash
# Load environment
export $(grep -v '^#' .env | xargs)

# Test installation
python test_installation.py

# Validate pipeline
./scripts/validate_pipeline.sh
```

### Step 5: Use It!
```bash
# Example: Find all tax calculation files
Task(subagent_type="explore", prompt="Find all tax calculation and form processing files")

# Create a spec for new feature
/plan_w_docs "Add W-2 form parser" "" "ai_docs/scout/relevant_files.json"

# Build the feature
/build_adw "specs/issue-001-w2-parser.md"
```

---

## What Gets Installed

```
tax-prep-repo/
├── adws/                      # Core workflow modules (100% portable)
│   ├── adw_plan.py           # Planning system
│   ├── adw_build.py          # Build system
│   └── adw_modules/          # Validators, GitHub, state management
├── .claude/
│   └── commands/             # Working slash commands
│       ├── plan_w_docs.md   # Plan generator
│       ├── build_adw.md     # Code builder
│       └── scout.md         # File finder (fixed version)
├── specs/                    # Your plans/specifications
├── ai_docs/                  # All AI-generated artifacts
│   ├── scout/               # Scout outputs
│   └── build_reports/       # Build reports
├── scripts/
│   └── validate_pipeline.sh # System health check
├── .adw_config.json         # Customizable configuration
├── .env.template            # Environment template
└── CLAUDE.md                # Quick reference guide
```

---

## Customization for Tax-Prep

### Option A: Use Default Structure (No Changes Needed)
The default `specs/`, `ai_docs/scout/`, `ai_docs/` directories work fine.

### Option B: Custom Directory Names
Edit `.adw_config.json`:
```json
{
  "paths": {
    "specs": "tax-specs/",
    "scout_outputs": "tax-docs/scout/",
    "ai_docs": "tax-docs/",
    "allowed": ["tax-specs", "tax-docs", "forms", "calculations", "returns"]
  }
}
```

### Option C: Add Tax-Specific Commands
Create `.claude/commands/tax_calculate.md`:
```markdown
# Tax Calculate
Calculate tax liability for given inputs

# Workflow
- Load tax tables and rates
- Apply deductions and credits
- Generate Form 1040
```

---

## Common Scenarios

### Scenario 1: "I have a different directory structure"
**Solution**: Edit `.adw_config.json` paths (2 minutes)

### Scenario 2: "I use GitLab, not GitHub"
**Solution**: The git operations still work, just not the `gh` CLI commands

### Scenario 3: "Scout doesn't find my tax files"
**Solution**: Use Task agents with specific prompts:
```python
Task(subagent_type="explore", prompt="Find .tax, .form, .calc files")
```

### Scenario 4: "I want to keep my existing CLAUDE.md"
**Solution**: Merge the workflow section into your existing file

---

## Testing Your Installation

### Quick Smoke Test (1 minute)
```bash
python test_installation.py
```

### Full Pipeline Test (5 minutes)
```bash
# 1. Scout for files
python adws/scout_simple.py "test task"

# 2. Check output created
ls ai_docs/scout/relevant_files.json

# 3. Validate all components
./scripts/validate_pipeline.sh
```

### Real Task Test (10 minutes)
```bash
# Try a real tax-related task
/scout "Find Form 1099 processing code" "3"
/plan_w_docs "Add 1099-DIV support" "" "ai_docs/scout/relevant_files.json"
# Review the generated spec in specs/
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Command not found: Task" | You're in bash, not Claude Code. Use inside Claude. |
| "Token limit exceeded" | Ensure `CLAUDE_CODE_MAX_OUTPUT_TOKENS=32768` is set |
| "Scout fails" | The fixed version uses Task agents, not external tools |
| "Can't find specs/" | Run from repo root, not subdirectory |
| "Permission denied" | Run `chmod +x scripts/*.sh` |

---

## What's Portable vs What's Not

### ✅ 100% Portable (Works Everywhere)
- Core `adws/` modules
- Git operations
- State management
- Validation system
- Error handling

### ⚠️ Needs Configuration (Easy)
- Directory paths (via `.adw_config.json`)
- Environment variables (via `.env`)
- GitHub PAT for PR creation

### ❌ Not Portable (Optional Features)
- Memory system (requires Archon MCP)
- External AI tools (gemini, opencode)
- R2 storage (requires Cloudflare)

---

## Support & Next Steps

1. **After Installation**: Run `test_installation.py` to verify
2. **First Real Task**: Start with something simple to validate
3. **Customization**: Only customize after confirming basics work
4. **Issues**: Check `ai_docs/AGENT_CLEANUP_ANALYSIS.md` for agent tips

**Remember**: The system is 85% portable out-of-the-box. Most customization is optional!