# scout_outputs/

Workflow artifacts and scout phase outputs - the operational bridge between workflow phases.

## Purpose

This directory stores **operational state** used by the Scout-Plan-Build workflow:
- **AI consumers**: Plan/build phases read these as inputs
- **Human consumers**: Developers review for context and debugging

## Structure

```
scout_outputs/
├── README.md                    # This file
├── relevant_files.json          # PRIMARY: Scout discovery output
├── .gitignore                   # Selective tracking rules
│
├── reports/                     # Analysis & execution reports
│   ├── architecture_report.json
│   ├── configuration_report.json
│   ├── implementation_report.json
│   ├── tests_report.json
│   └── phase1-state-management.json
│
├── workflows/                   # Per-workflow execution state
│   └── ADW-{ID}/               # e.g., ADW-PARALLEL001/
│       ├── adw_state.json      # Workflow status
│       └── [phase outputs]
│
├── archive/                     # Historical backups
│   └── [old versions]
│
└── temp/                        # Temporary working files (gitignored)
```

## Key Files

| File | Purpose | Consumer |
|------|---------|----------|
| `relevant_files.json` | Scout phase output - list of files relevant to task | Plan phase |
| `reports/*.json` | Analysis reports from various phases | Build/review phases |
| `workflows/ADW-*/adw_state.json` | Per-workflow execution state | ADW orchestration |

## Relationship to Other Directories

| Directory | Purpose | Lifecycle |
|-----------|---------|-----------|
| `scout_outputs/` | Operational workflow artifacts | Transient (per workflow) |
| `ai_docs/` | Human-readable documentation | Permanent (project docs) |
| `agent_runs/` | Execution history & traceability | Permanent (audit trail) |

## Gitignore Rules

The `.gitignore` selectively tracks:
- `relevant_files.json` - Always tracked (critical workflow input)
- `reports/*.json` - Tracked (valuable analysis)
- `workflows/` - Gitignored (transient state)
- `temp/` - Gitignored (temporary files)

---
*Updated: 2024-11-23*
