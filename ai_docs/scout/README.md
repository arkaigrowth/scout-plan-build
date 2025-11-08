# Scout Outputs Directory

This directory contains the output files from scout operations.

## Migration Notice (Oct 2024)

This directory was renamed from `agents/` to `scout_outputs/` to eliminate confusion.

**Why the change?**
- "agents" was ambiguous - could mean agent definitions, outputs, or configs
- This folder specifically contains scout OUTPUT files
- Agent DEFINITIONS live in ~/.claude/agents/ (user home)

## Structure

```
scout_outputs/
└── relevant_files.json   # Main output from scout operations
```

## Usage

When scout runs, it saves found files here:
```bash
scout_outputs/relevant_files.json
```

This file is then used by the plan phase:
```bash
/plan_w_docs "task" "" "scout_outputs/relevant_files.json"
```

## Security Note

Previous versions had a vulnerability where task names/URLs could create arbitrary folders.
This has been fixed - all outputs now go directly to relevant_files.json.
