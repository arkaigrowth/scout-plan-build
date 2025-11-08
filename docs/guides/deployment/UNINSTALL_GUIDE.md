# Uninstall Guide

## Three Scenarios

### Scenario 1: Test Installation in /tmp (Your Case)

Since `/tmp/test-tax-repo` was just a test with the old structure:

```bash
# Option A: Just delete it
rm -rf /tmp/test-tax-repo

# Option B: Delete and reinstall fresh with correct structure
rm -rf /tmp/test-tax-repo
./scripts/install_to_new_repo.sh /tmp/test-tax-repo
```

**Why this is safe:**
- It's in `/tmp/` - meant to be temporary
- No real code/data to preserve
- Fresh install ensures latest structure

---

### Scenario 2: Real Repo with Old Installation

If you installed to a real repo before we fixed the structure:

```bash
# Uninstall old version
./scripts/uninstall_from_repo.sh /path/to/your/repo

# Reinstall with correct structure
./scripts/install_to_new_repo.sh /path/to/your/repo
```

**What the uninstaller does:**
- Removes `adws/` module
- Removes slash commands
- Removes config files (asks first)
- Preserves directories with content
- Safe - won't delete your code

---

### Scenario 3: Manual Cleanup

If you prefer to manually remove old components:

```bash
cd /path/to/your/repo

# Remove core module
rm -rf adws/

# Remove old scout outputs location
rm -rf scout_outputs/  # Only if using old structure

# Remove slash commands
rm -f .claude/commands/scout*.md
rm -f .claude/commands/plan_w_docs*.md
rm -f .claude/commands/build*.md

# Remove config files
rm -f .env.template
rm -f .adw_config.json
rm -f test_installation.py
rm -f scripts/validate_pipeline.sh

# Keep these if they have your content:
# - specs/ (your generated specs)
# - ai_docs/scout/ (your scout outputs)
# - ai_docs/build_reports/ (your build reports)
```

---

## What to Keep vs Remove

### ❌ Safe to Remove (Installed by System)
- `adws/` - core modules (can reinstall)
- `.claude/commands/scout*.md` - commands
- `.env.template` - just a template
- `test_installation.py` - test script
- Empty `scout_outputs/` or `ai_docs/scout/`

### ⚠️ Ask Before Removing
- `.adw_config.json` - if you customized it
- `CLAUDE.md` - if you added your own content
- `specs/` - if you created specs

### ✅ Always Keep
- Your application code
- Any specs you created
- Scout outputs with real data
- Build reports you want to reference
- Any customizations you made

---

## Verification After Uninstall

Check these are gone:
```bash
ls adws/                              # Should not exist
ls .claude/commands/scout*.md         # Should not exist
ls scripts/validate_pipeline.sh      # Should not exist
```

Your repo should be clean of Scout-Plan-Build components.

---

## Reinstalling Fresh

After uninstalling, reinstall with the latest structure:

```bash
./scripts/install_to_new_repo.sh /path/to/your/repo
```

This will:
- Install to `ai_docs/scout/` (not `scout_outputs/`)
- Use all updated paths
- Create proper directory structure
- Give you the latest fixes