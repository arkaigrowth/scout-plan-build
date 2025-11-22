# AI Documentation Structure

AI-generated and AI-consumed artifacts organized for clarity and consistency.

## Directory Structure

```
ai_docs/
├── architecture/       # Architecture documentation & diagrams
│   └── diagrams/       # Visual architecture representations
├── analyses/           # System and code analyses
├── assessments/        # Security audits, readiness assessments
├── build_reports/      # Build phase execution reports
├── reference/          # Internal quick reference guides
├── research/           # External learning resources (NEW)
│   ├── videos/         # Video transcript analyses
│   ├── articles/       # Article summaries
│   ├── implementations/# Reference codebase notes
│   └── papers/         # Academic papers
├── reviews/            # Code review reports
├── sessions/           # Session persistence & handoffs
│   └── handoffs/       # Cross-session handoff documents
└── [root .md files]    # Various indices and summaries
```

## Content Types

### AI-Generated (OUTPUT)
| Type | Location | Purpose |
|------|----------|---------|
| Build reports | `build_reports/` | Execution logs from build phase |
| Reviews | `reviews/` | Code review findings |
| Analyses | `analyses/` | Deep-dive system analyses |
| Architecture | `architecture/` | Architecture documentation |
| Reference | `reference/` | Internal quick reference guides |
| Assessments | `assessments/` | Security audits, readiness checks |

### AI-Consumed (INPUT)
| Type | Location | Purpose |
|------|----------|---------|
| Research | `research/` | External learning resources |
| Sessions | `sessions/` | Cross-session context |

## Workflow Integration

```
Scout Phase  → scout_outputs/relevant_files.json (canonical location)
Plan Phase   → specs/issue-XXX-*.md
Build Phase  → ai_docs/build_reports/*-report.md
Review Phase → ai_docs/reviews/*-review.md
```

> **Note**: Scout outputs go to `scout_outputs/` (top-level), NOT `ai_docs/scout/`.
> The `ai_docs/scout/` path is deprecated as of v2024.11.20.

## Semantic Boundaries

| Folder | Semantic | Direction |
|--------|----------|-----------|
| `reference/` | Internal knowledge about THIS project | Generated → Out |
| `research/` | External knowledge from OTHER sources | Sourced → In |
| `architecture/` | How things ARE built | Documentation |
| `analyses/` | What we LEARNED from analysis | Generated |

## Why This Organization?

- **SSOT**: Each content type has ONE canonical location
- **Clarity**: Clear separation of generated vs sourced content
- **Discoverability**: Easy to find all AI artifacts
- **Semantic accuracy**: Folder names match their purpose
