# AI Documentation Organization Structure

> **Updated**: 2024-11-22 - Added `research/` folder, clarified canonical paths

## ✅ The Current Structure (Implemented)

```
ai_docs/                      # AI-generated and AI-consumed artifacts
├── architecture/             # Architecture documentation & diagrams
│   └── diagrams/            # Visual architecture representations
├── analyses/                # System and code analyses
├── assessments/             # Security audits, readiness assessments
├── build_reports/           # Build phase execution reports
├── reference/               # Internal quick reference guides
├── research/                # External learning resources (NEW)
│   ├── videos/             # Video transcript analyses
│   ├── articles/           # Article summaries
│   ├── implementations/    # Reference codebase notes
│   └── papers/             # Academic papers
├── reviews/                # Code review reports
├── sessions/               # Session persistence & handoffs
│   └── handoffs/          # Cross-session handoff documents
└── scout/                  # DEPRECATED - see scout_outputs/

scout_outputs/              # Scout phase outputs (CANONICAL location)
├── relevant_files.json    # Primary scout output
└── workflows/             # Workflow execution state

specs/                      # Implementation specs (separate for visibility)
```

## 🎯 Why This Structure

### Semantic Boundaries

| Folder | Semantic | Direction |
|--------|----------|-----------|
| `ai_docs/reference/` | Internal knowledge about THIS project | Generated → Out |
| `ai_docs/research/` | External knowledge from OTHER sources | Sourced → In |
| `ai_docs/architecture/` | How things ARE built | Documentation |
| `ai_docs/analyses/` | What we LEARNED from analysis | Generated |
| `scout_outputs/` | Scout phase results | Workflow artifact |

### Content Types

**AI-Generated (OUTPUT)**
- `build_reports/` - Build execution logs
- `reviews/` - Code review findings
- `analyses/` - Deep-dive analyses
- `reference/` - Internal quick refs

**AI-Consumed (INPUT)**
- `research/` - External learning resources
- `sessions/` - Cross-session context

## 📋 Organizational Principles

1. **SSOT**: Each content type has ONE canonical location
2. **Clear Naming**: Folder names match their purpose
3. **Workflow Clarity**: Each phase has its place:
   - Scout → `scout_outputs/` (canonical)
   - Plan → `specs/`
   - Build → `ai_docs/build_reports/`
   - Review → `ai_docs/reviews/`
4. **Semantic Accuracy**: `reference/` (internal) vs `research/` (external)

## 🔄 Migration History

| Date | Change | Reason |
|------|--------|--------|
| 2024-11-20 | `ai_docs/scout/` → `scout_outputs/` | SSOT consolidation |
| 2024-11-22 | Added `ai_docs/research/` | External learning resources |

### Deprecated Paths

| Old Path | New Path | Status |
|----------|----------|--------|
| `ai_docs/scout/` | `scout_outputs/` | Deprecated, fallback only |
| `agents/scout_files/` | `scout_outputs/` | Removed |

## 📝 Code References

All code uses canonical paths:
- ✅ `adws/scout_simple.py` - saves to `scout_outputs/`
- ✅ `adws/adw_modules/constants.py` - defines canonical paths
- ✅ Validation in `validators.py` - enforces paths

## 💡 Best Practice

**Rule**:
- AI **generated** it → `ai_docs/` (except specs)
- AI **consumes** it → `ai_docs/research/` or `ai_docs/sessions/`
- Scout **output** → `scout_outputs/` (workflow artifact)
- Implementation **plan** → `specs/` (for workflow visibility)

This makes it crystal clear:
- Human code: `src/`, `app/`, etc.
- AI artifacts: `ai_docs/`
- AI learning: `ai_docs/research/`
- AI specs: `specs/`
- Scout results: `scout_outputs/`
