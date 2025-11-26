# Framework Upgrades

This directory contains backup snapshots and reports from framework upgrades.

---

## Active Upgrades

### Refinery Data Refiner (2025-11-25 23:10:38)

**Target Repo**: `/Users/alexkamysz/AI/refinery-data-refiner`
**Framework**: v2024.11.8 → v4.0
**Status**: ✅ COMPLETE

**Files**:
- [Detailed Report](./refinery_upgrade_report.md) - Full upgrade documentation
- [Migration Guide](./refinery_migration_guide.md) - Quick reference for users
- [Backup Directory](./refinery_backup_20251125_231038/) - Complete snapshot (1.2M)

**Summary**:
- Commands: 4 files → 9 directories
- Skills: 0 → 3 files
- Hooks: 0 → 9 files
- User files: 100% preserved (settings, 7 custom agents)
- Validation: All checks passed
- Rollback: Available

---

## Backup Structure

Each upgrade creates:
```
{repo}_backup_{timestamp}/
├── .adw_config.json       - Project config
├── .claude/               - Complete .claude snapshot
│   ├── commands/          - Old commands
│   ├── hooks/             - Old hooks
│   ├── skills/            - Old skills
│   ├── agents/            - User's agents
│   └── settings.local.json - User settings
├── adws/                  - Old framework modules
├── CLAUDE.md              - Old documentation
├── specs/                 - User work (if exists)
├── settings.local.json.PRESERVE - User settings backup
└── agents.PRESERVE/       - User agents backup
```

---

## Rollback Template

```bash
BACKUP="path/to/backup"
TARGET="path/to/target/repo"

# Remove new files
rm -rf "$TARGET/.claude" "$TARGET/adws" "$TARGET/CLAUDE.md"

# Restore from backup
cp -r "$BACKUP/.claude" "$TARGET/"
cp -r "$BACKUP/adws" "$TARGET/"
cp "$BACKUP/CLAUDE.md" "$TARGET/"
cp "$BACKUP/.adw_config.json" "$TARGET/"
```

---

## Upgrade Checklist

Pre-upgrade:
- [ ] Audit current state (commands, modules, user files)
- [ ] Create timestamped backup
- [ ] Preserve critical files separately

During upgrade:
- [ ] Remove old framework files (ONLY framework, preserve user files)
- [ ] Install new framework
- [ ] Create directory structure
- [ ] Restore user files

Post-upgrade:
- [ ] Validate Python imports
- [ ] Verify command structure
- [ ] Confirm user files preserved
- [ ] Test basic workflows
- [ ] Generate reports

---

## Version History

| Repo | Date | From | To | Status |
|------|------|------|-----|--------|
| refinery-data-refiner | 2025-11-25 | v2024.11.8 | v4.0 | ✅ Complete |

---

## Notes

- Always preserve `.claude/settings.local.json`
- Always preserve `.claude/agents/` if exists
- Always preserve `.env` if exists
- Always preserve `specs/` directory
- Never delete user work
- Create separate backups of critical files (*.PRESERVE)
- Validate Python imports after upgrade
- Test workflows before declaring success

---

Last Updated: 2025-11-25
