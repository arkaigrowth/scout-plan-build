# Deprecated Installation Documentation

**Archived**: 2025-12-22
**Replaced By**: `/INSTALL.md` (consolidated installation guide)

## What's Here

These files were part of scattered installation documentation that has been consolidated:

| Old File | What It Was | Status |
|----------|-------------|--------|
| `IMPLEMENTATION_GUIDE.md` | Code location reference for portability issues | Archived - implementation details now in INSTALL.md troubleshooting |
| `NAVIGATION_GUIDE.md` | Guide to finding things in the codebase | Archived - covered in INSTALL.md "What Gets Installed" |
| `interactive-installer-menu.md` | Design spec for interactive installer menu | Archived - not implemented, current installer is simpler |
| `installer-implementation-spec.md` | Technical spec for component-based installer | Archived - not implemented, current installer is simpler |

## Why Archived

The original documentation was:
- Scattered across multiple directories
- Some specs were never implemented
- Difficult for agents to find and follow

The new `/INSTALL.md` provides:
- Single source of truth
- Agent-friendly instructions
- Tested, working installation flow
- Clear troubleshooting section

## If You Need These

These files are kept for historical reference. If you need to:
- Understand past design decisions → read these
- Implement the interactive installer → use `interactive-installer-menu.md` as starting point
- Find specific code locations → `IMPLEMENTATION_GUIDE.md` has line numbers (may be stale)

## Current Installation

See `/INSTALL.md` at the repository root for the current installation process.
