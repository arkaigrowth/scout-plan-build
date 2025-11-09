# Agents Naming Migration Record

## Migration Date
$(date +%Y-%m-%d)

## What Changed

### Folder Rename
- **Old**: `/agents/` - Confusingly named, contained scout outputs not agent definitions
- **New**: `/scout_outputs/` - Clearly indicates these are output artifacts

### Path Updates
All references updated from `agents/scout_files/` to `scout_outputs/`

### Security Fix
- **Old**: `ALLOWED_PATH_PREFIXES = ["agents/"]` - Too broad, security risk
- **New**: `ALLOWED_PATH_PREFIXES = ["scout_outputs/"]` - Specific and secure

### Files Updated
- adws/adw_scout_parallel.py
- adws/adw_modules/validators.py
- .claude/commands/scout_parallel.md
- .claude/skills/adw-scout.md
- scripts/workflow.sh
- CLAUDE.md

## Why This Change

1. **Clarity**: "agents" implied agent definitions, but folder contained scout outputs
2. **Security**: Previous path validation was too permissive
3. **Standards**: Aligns with Claude Code conventions where outputs != definitions

## Rollback Instructions

If needed, run:
```bash
git checkout -- .
mv scout_outputs agents
```
