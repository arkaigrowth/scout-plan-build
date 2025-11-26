# Local Claude Configuration

This folder contains project-specific Claude Code configuration.

## Created
2025-11-09T03:16:20.924397

## Purpose
- **Project Isolation**: Each project tracks its own context independently
- **Team Collaboration**: Share configuration via version control
- **Local Overrides**: Personal settings in settings.local.json

## Files
- `statusline_output.txt` - Current context percentage (auto-updated)
- `context_stats.json` - Context usage statistics
- `settings.local.json` - Personal configuration overrides
- `.gitignore` - Excludes tracking files from git

## Context Tracking
This project uses local context tracking to prevent interference between projects.
The auto-memory hook will trigger at 93.75% (150k tokens) to prevent context loss.

## Global Configuration
Global hooks and settings are in: ~/.claude/
